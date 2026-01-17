"""
Temporal Orchestrator Library

Orchestrates all temporal updates when state transitions occur:
- Phase-based reweighting
- Crisis overrides
- Session compression
- Decay calculations
- Staleness updates

Integrates with state manager to trigger updates on state transitions.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
import logging

from app.models import LegislativeState

from .edge_decay import calculate_decayed_weight, classify_edge_decay_type
from .staleness_detector import update_edge_staleness
from .power_reweighting import apply_phase_reweighting
from .crisis_handler import get_active_crisis_events, apply_crisis_override
from .session_compression import apply_session_compression_to_weights, get_session_compression_for_date

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent

EDGE_UPDATES_LOG = BASE_DIR / "data" / "temporal" / "edge_updates.jsonl"


def load_all_influence_edges() -> List[Dict[str, Any]]:
    """
    Load all influence edges from storage.
    
    TODO: This should read from the actual edge storage system.
    For now, returns empty list if file doesn't exist.
    
    Returns:
        List of edge dictionaries
    """
    edges_file = BASE_DIR / "data" / "edges" / "influence_edges__derived.json"
    
    if not edges_file.exists():
        logger.warning(f"Edges file not found at {edges_file}")
        return []
    
    try:
        edges_data = json.loads(edges_file.read_text())
        return edges_data.get("edges", [])
    except Exception as e:
        logger.error(f"Failed to load edges: {e}")
        return []


def save_edge_updates(updates: List[Dict[str, Any]]) -> bool:
    """
    Save edge updates to audit log.
    
    Args:
        updates: List of update records
    
    Returns:
        True if saved successfully
    """
    try:
        # Ensure directory exists
        EDGE_UPDATES_LOG.parent.mkdir(parents=True, exist_ok=True)
        
        # Append to JSONL file
        with open(EDGE_UPDATES_LOG, 'a', encoding='utf-8') as f:
            for update in updates:
                f.write(json.dumps(update) + '\n')
        
        return True
    except Exception as e:
        logger.error(f"Failed to save edge updates: {e}")
        return False


def update_edges_for_state_transition(
    current_phase: LegislativeState,
    previous_phase: LegislativeState,
    transition_time: datetime,
    edges: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Orchestrate all temporal updates when state transitions.
    
    Steps:
    1. Apply phase-based reweighting
    2. Check for active crisis overrides
    3. Calculate session compression
    4. Apply decay (if needed)
    5. Update edge weight_evolution array
    6. Update last_confirmed_at (if externally validated)
    7. Update staleness status
    
    Args:
        current_phase: New legislative state
        previous_phase: Previous legislative state
        transition_time: When transition occurred
        edges: Optional list of edges (loads all if None)
    
    Returns:
        Dictionary with updated_edges, update_count, summary
    """
    if edges is None:
        edges = load_all_influence_edges()
    
    if not edges:
        logger.warning("No edges to update")
        return {
            "updated_edges": [],
            "update_count": 0,
            "summary": {
                "total_edges": 0,
                "updated": 0,
                "skipped": 0
            }
        }
    
    updates = []
    updated_edges = []
    summary = {
        "total_edges": len(edges),
        "updated": 0,
        "skipped": 0,
        "by_decay_type": {
            "PERSON_DEPENDENT": 0,
            "INSTITUTION_DEPENDENT": 0,
            "HYBRID": 0
        }
    }
    
    # Get active crisis events
    active_crises = get_active_crisis_events(transition_time)
    
    # Get session compression factor
    compression_factor = get_session_compression_for_date(transition_time)
    
    for edge in edges:
        try:
            # Store original weights for audit
            original_weights = edge.get("weights", {}).copy()
            if not original_weights:
                summary["skipped"] += 1
                continue
            
            # Track if each factor actually changed weights (for advisory metadata)
            phase_changed = False
            compression_changed = False
            decay_changed = False
            
            # 1. Phase-based reweighting
            reweighted = apply_phase_reweighting(original_weights, current_phase)
            phase_changed = reweighted != original_weights
            
            # 2. Crisis overrides (check if edge is affected)
            crisis_override_applied = False
            revolving_door_active = False
            applied_crisis = None
            for crisis in active_crises:
                # Pass current_phase for phase-sensitive adjustments (revolving-door)
                current_phase_str = current_phase.value if hasattr(current_phase, 'value') else str(current_phase)
                override = apply_crisis_override(
                    edge, crisis, transition_time,
                    current_phase=current_phase_str
                )
                if override:
                    reweighted = override
                    crisis_override_applied = True
                    applied_crisis = crisis
                    if crisis.get("event_type") == "REVOLVING_DOOR":
                        revolving_door_active = True
                    break
            
            # 3. Session compression
            compressed = apply_session_compression_to_weights(
                reweighted,
                transition_time,
                affected_axes=["temporal_leverage", "procedural_power"]
            )
            compression_changed = compressed != reweighted
            
            # 4. Decay (applies minimum decay to prevent weights from going below decayed floor)
            decayed = calculate_decayed_weight(edge, transition_time)
            decay_changed = any(
                decayed.get(axis, 1.0) < compressed.get(axis, 1.0)
                for axis in compressed
                if axis in decayed
            )
            
            # Combine: take minimum of compressed and decayed (decay is floor)
            final_weights = {}
            for axis in compressed:
                if axis in decayed:
                    final_weights[axis] = min(compressed[axis], decayed[axis])
                else:
                    final_weights[axis] = compressed[axis]
            
            # Only update if weights actually changed
            weights_changed = final_weights != original_weights
            
            if weights_changed:
                # 5. Update weight_evolution
                if "weight_evolution" not in edge:
                    edge["weight_evolution"] = []
                
                # Build advisory metadata
                influence_reasons = []
                confidence = "HIGH"
                
                if crisis_override_applied and applied_crisis:
                    # Check if crisis is revolving-door
                    if applied_crisis.get("event_type") == "REVOLVING_DOOR":
                        influence_reasons.append("REVOLVING_DOOR_RECENCY")
                        # Revolving-door influence has lower confidence
                        confidence = "MEDIUM"
                    else:
                        influence_reasons.append("CRISIS_OVERRIDE")
                
                # Track other influence factors
                if phase_changed:
                    influence_reasons.append("PHASE_REWEIGHT")
                if compression_factor != 1.0:
                    influence_reasons.append(f"SESSION_COMPRESSION_{compression_factor:.2f}x")
                if decay_changed:
                    influence_reasons.append("DECAY_FLOOR")
                
                evolution_entry = {
                    "at": transition_time.isoformat() + "Z",
                    "weights": final_weights.copy(),
                    "trigger": f"state_transition_{previous_phase.value if hasattr(previous_phase, 'value') else previous_phase}_to_{current_phase.value if hasattr(current_phase, 'value') else current_phase}",
                    "update_reason": " + ".join(influence_reasons) if influence_reasons else "no_change",
                    "influence_reason": influence_reasons[0] if influence_reasons else None,  # Primary reason
                    "confidence": confidence,  # Confidence level
                    "compression_factor": compression_factor,
                    "crisis_override": crisis_override_applied,
                    "revolving_door_active": revolving_door_active  # Flag for revolving-door
                }
                edge["weight_evolution"].append(evolution_entry)
                
                # Update current weights
                edge["weights"] = final_weights
                edge["_meta"]["last_updated"] = transition_time.isoformat() + "Z"
                
                # 6. Update staleness (if not externally confirmed, keep existing)
                # Staleness is updated separately by staleness detector
                
                # Create update record for audit log
                # Compute weight deltas for audit clarity
                weight_deltas = {}
                changed_axes = []
                for axis in final_weights:
                    old = original_weights.get(axis, 0.0)
                    new = final_weights[axis]
                    delta = new - old
                    if abs(delta) > 0.001:  # Threshold to ignore floating-point noise
                        weight_deltas[axis] = round(delta, 4)
                        changed_axes.append(axis)
                
                previous_phase_str = previous_phase.value if hasattr(previous_phase, 'value') else str(previous_phase)
                current_phase_str = current_phase.value if hasattr(current_phase, 'value') else str(current_phase)
                
                update_record = {
                    "timestamp": transition_time.isoformat() + "Z",
                    "edge_id": edge.get("edge_id"),
                    "update_type": "state_transition",
                    "previous_phase": previous_phase_str,
                    "current_phase": current_phase_str,
                    "previous_weights": original_weights,
                    "new_weights": final_weights,
                    "weight_deltas": weight_deltas,  # NEW: Per-axis changes
                    "changed_axes": changed_axes,  # NEW: Which axes changed
                    "change_summary": f"{len(changed_axes)} axes changed" if changed_axes else "no_change",  # NEW
                    "trigger": evolution_entry["trigger"],
                    "influence_reason": evolution_entry.get("influence_reason"),  # NEW: Primary influence reason
                    "confidence": evolution_entry.get("confidence"),  # NEW: Confidence level
                    "compression_factor": compression_factor,
                    "crisis_override": crisis_override_applied,
                    "revolving_door_active": revolving_door_active  # NEW: Revolving-door flag
                }
                updates.append(update_record)
                
                # Track decay type
                decay_type = classify_edge_decay_type(edge)
                summary["by_decay_type"][decay_type] = summary["by_decay_type"].get(decay_type, 0) + 1
                
                updated_edges.append(edge)
                summary["updated"] += 1
            else:
                summary["skipped"] += 1
        
        except Exception as e:
            logger.error(f"Error updating edge {edge.get('edge_id')}: {e}")
            summary["skipped"] += 1
            continue
    
    # Save updates to audit log
    if updates:
        save_edge_updates(updates)
    
    return {
        "updated_edges": updated_edges,
        "update_count": summary["updated"],
        "summary": summary
    }


def update_edges_for_staleness_check(
    edges: Optional[List[Dict[str, Any]]] = None,
    current_time: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Update edges with current staleness status.
    
    This is separate from state transition updates and can be run periodically.
    
    Args:
        edges: Optional list of edges (loads all if None)
        current_time: Current timestamp (defaults to now)
    
    Returns:
        Dictionary with summary of staleness updates
    """
    if current_time is None:
        current_time = datetime.utcnow()
    
    if edges is None:
        edges = load_all_influence_edges()
    
    if not edges:
        return {
            "checked": 0,
            "fresh": 0,
            "stale": 0,
            "very_stale": 0
        }
    
    summary = {
        "checked": len(edges),
        "fresh": 0,
        "stale": 0,
        "very_stale": 0
    }
    
    for edge in edges:
        try:
            updated_edge = update_edge_staleness(edge, current_time)
            status = updated_edge.get("staleness_status", "FRESH")
            summary[status.lower()] = summary.get(status.lower(), 0) + 1
        except Exception as e:
            logger.error(f"Error checking staleness for edge {edge.get('edge_id')}: {e}")
    
    return summary


if __name__ == "__main__":
    # Test temporal orchestrator
    from app.models import LegislativeState
    
    previous_phase = LegislativeState.PRE_EVT
    current_phase = LegislativeState.COMM_EVT
    transition_time = datetime.utcnow()
    
    result = update_edges_for_state_transition(
        current_phase,
        previous_phase,
        transition_time
    )
    
    print(f"Update result: {json.dumps(result, indent=2, default=str)}")
