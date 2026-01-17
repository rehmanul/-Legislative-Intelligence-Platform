"""
Crisis Override Handler Library

Handles temporary weight adjustments during crises (elections, scandals, emergencies).
Crisis overrides can boost, suppress, or revert edge weights for specific entities or scopes.

Includes revolving-door influence handling: temporary, decaying, phase-sensitive boosts
for entity transitions (Hill → K Street → Agency).
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
import logging
import uuid
import os

from .edge_decay import parse_timestamp

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent

CRISIS_EVENTS_FILE = BASE_DIR / "data" / "temporal" / "crisis_events.jsonl"


def load_active_crisis_events(current_time: datetime) -> List[Dict[str, Any]]:
    """
    Load active crisis events from JSONL log.
    
    Args:
        current_time: Current timestamp to check expiration
    
    Returns:
        List of active crisis events
    """
    active_events = []
    
    if not CRISIS_EVENTS_FILE.exists():
        return active_events
    
    try:
        with open(CRISIS_EVENTS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    event = json.loads(line)
                    
                    # Check if event is still active
                    expires_at = event.get("expires_at")
                    if expires_at:
                        expires_time = parse_timestamp(expires_at)
                        if current_time > expires_time:
                            continue  # Event expired
                    
                    duration = event.get("duration", "TEMPORARY")
                    
                    # Check for revolving-door events (faster decay and hard cap)
                    if event.get("event_type") == "REVOLVING_DOOR":
                        # Revolving-door events: hard cap at 180 days
                        event_at_time = parse_timestamp(event.get("event_at"))
                        days_since = (current_time - event_at_time).days
                        
                        if days_since > 180:
                            continue  # Expired (hard cap enforced)
                        
                        # Apply faster decay after 90 days: boost reduces by 50% over next 90 days
                        if days_since > 90:
                            decay_factor = 0.5 ** ((days_since - 90) / 90)  # Exponential decay after 90 days
                            if "weight_overrides" in event:
                                # Create copy to avoid mutating original
                                event = event.copy()
                                event["weight_overrides"] = {
                                    axis: value * decay_factor
                                    for axis, value in event["weight_overrides"].items()
                                }
                                # Add decay metadata
                                event["_revolving_door_decay_factor"] = decay_factor
                                event["_revolving_door_days_since"] = days_since
                    
                    # Check global disable flag
                    if os.getenv("DISABLE_REVOLVING_DOOR", "false").lower() == "true":
                        if event.get("event_type") == "REVOLVING_DOOR":
                            continue  # Skip revolving-door events if disabled
                    
                    if duration == "PERMANENT":
                        # Permanent events are active until manually cleared
                        active_events.append(event)
                    elif duration == "TEMPORARY":
                        # Temporary events auto-expire
                        if not expires_at:
                            # If no expiration set but marked temporary, check if it's been too long
                            event_at = parse_timestamp(event.get("event_at"))
                            days_since = (current_time - event_at).days
                            if days_since > 365:  # Auto-expire after 1 year
                                continue
                        active_events.append(event)
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse crisis event line: {e}")
                    continue
    
    except Exception as e:
        logger.error(f"Failed to load crisis events: {e}")
    
    return active_events


def save_crisis_event(event: Dict[str, Any]) -> bool:
    """
    Save crisis event to JSONL log.
    
    Args:
        event: Crisis event dictionary
    
    Returns:
        True if saved successfully
    """
    try:
        # Ensure directory exists
        CRISIS_EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # Append to JSONL file
        with open(CRISIS_EVENTS_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event) + '\n')
        
        return True
    except Exception as e:
        logger.error(f"Failed to save crisis event: {e}")
        return False


def create_crisis_event(
    event_type: str,
    scope: str,
    impact: str,
    event_at: datetime,
    duration: str = "TEMPORARY",
    affected_entities: Optional[List[str]] = None,
    weight_overrides: Optional[Dict[str, float]] = None,
    description: Optional[str] = None,
    expires_at: Optional[datetime] = None,
    created_by: Optional[str] = None,
    approved_by: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new crisis event.
    
    Args:
        event_type: Type of crisis (ELECTION, SCANDAL, etc.)
        scope: Scope of impact (ENTITY_SPECIFIC, COMMITTEE_WIDE, etc.)
        impact: Type of adjustment (BOOST, SUPPRESS, REVERT_TO_BASE)
        event_at: When the crisis occurred
        duration: TEMPORARY or PERMANENT
        affected_entities: List of entity IDs (required for ENTITY_SPECIFIC scope)
        weight_overrides: Weight adjustments per axis
        description: Human-readable description
        expires_at: When override expires (for TEMPORARY events)
        created_by: Who created this event
        approved_by: Who approved this override (for PERMANENT events)
    
    Returns:
        Crisis event dictionary
    """
    event = {
        "_meta": {
            "schema_version": "1.0.0",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "created_by": created_by or "system"
        },
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "scope": scope,
        "impact": impact,
        "event_at": event_at.isoformat() + "Z",
        "duration": duration,
        "affected_entities": affected_entities or [],
        "weight_overrides": weight_overrides or {},
        "description": description or f"{event_type} crisis event",
        "approved_by": approved_by
    }
    
    # Revolving-door events: enforce 180-day maximum
    if event_type == "REVOLVING_DOOR":
        duration = "TEMPORARY"  # Always temporary for revolving-door
        max_duration_days = 180
        if expires_at:
            # Cap expiration at max_duration_days from event_at
            max_expires = event_at + timedelta(days=max_duration_days)
            if expires_at > max_expires:
                expires_at = max_expires
                logger.info(f"Revolving-door event expiration capped at {max_duration_days} days")
        else:
            # Set to max_duration_days
            expires_at = event_at + timedelta(days=max_duration_days)
    
    if expires_at:
        event["expires_at"] = expires_at.isoformat() + "Z"
    elif duration == "TEMPORARY":
        # Default expiration: 90 days for temporary events
        default_expires = datetime.fromtimestamp(event_at.timestamp() + (90 * 24 * 60 * 60))
        event["expires_at"] = default_expires.isoformat() + "Z"
    
    return event


def apply_crisis_override(
    edge: Dict[str, Any],
    crisis_event: Dict[str, Any],
    current_time: datetime,
    current_phase: Optional[str] = None
) -> Optional[Dict[str, float]]:
    """
    Apply crisis-based weight overrides to an edge.
    
    Example: Leadership change → boost procedural_power for new chair,
    suppress for old chair.
    
    For revolving-door events, applies phase-sensitive adjustments:
    - Stronger in early phases (PRE_EVT, INTRO_EVT, COMM_EVT)
    - Weaker in late phases (FLOOR_EVT, FINAL_EVT)
    - No boost in IMPL_EVT
    
    Args:
        edge: Edge dictionary with weights
        crisis_event: Crisis event dictionary
        current_time: Current timestamp
        current_phase: Optional current legislative phase for phase sensitivity
    
    Returns:
        Dictionary of adjusted weights (same structure as edge["weights"]),
        or None if this edge is not affected by the crisis
    """
    # Check if edge is affected by this crisis
    scope = crisis_event.get("scope")
    if scope == "ENTITY_SPECIFIC":
        affected_entities = crisis_event.get("affected_entities", [])
        from_id = edge.get("from_entity_id")
        to_id = edge.get("to_entity_id")
        
        if from_id not in affected_entities and to_id not in affected_entities:
            return None  # Edge not affected
    
    # Get current weights
    current_weights = edge.get("weights", {})
    if not current_weights:
        return None
    
    # Apply impact
    impact = crisis_event.get("impact")
    weight_overrides = crisis_event.get("weight_overrides", {}).copy()  # Copy to avoid mutation
    
    # Phase sensitivity for revolving-door events
    phase_sensitivity = 1.0
    if crisis_event.get("event_type") == "REVOLVING_DOOR":
        # Get current phase from edge or parameter
        phase = current_phase or edge.get("legislative_state") or "PRE_EVT"
        
        # Phase sensitivity: stronger early, weaker late, none in IMPL_EVT
        phase_sensitivity_map = {
            "PRE_EVT": 1.0,      # Full boost
            "INTRO_EVT": 0.9,    # 90% of boost
            "COMM_EVT": 0.7,     # 70% of boost
            "FLOOR_EVT": 0.4,    # 40% of boost
            "FINAL_EVT": 0.2,    # 20% of boost
            "IMPL_EVT": 0.0      # No boost (implementation is agency-driven)
        }
        phase_sensitivity = phase_sensitivity_map.get(phase, 1.0)
        
        # Apply phase sensitivity to boost magnitudes
        for axis in weight_overrides:
            weight_overrides[axis] *= phase_sensitivity
    
    adjusted = {}
    
    if impact == "BOOST":
        # Increase affected weights
        for axis, override_value in weight_overrides.items():
            if axis in current_weights:
                current = current_weights[axis]
                adjusted[axis] = min(1.0, current + override_value)
            else:
                adjusted[axis] = min(1.0, override_value)
        
        # Copy non-overridden weights
        for axis, weight in current_weights.items():
            if axis not in adjusted:
                adjusted[axis] = weight
    
    elif impact == "SUPPRESS":
        # Decrease affected weights
        for axis, override_value in weight_overrides.items():
            if axis in current_weights:
                current = current_weights[axis]
                adjusted[axis] = max(0.0, current - override_value)
            else:
                adjusted[axis] = 0.0
        
        # Copy non-overridden weights
        for axis, weight in current_weights.items():
            if axis not in adjusted:
                adjusted[axis] = weight
    
    elif impact == "REVERT_TO_BASE":
        # Restore base weights from weight_evolution[0]
        weight_evolution = edge.get("weight_evolution", [])
        if weight_evolution:
            base_weights = weight_evolution[0].get("weights", {})
            adjusted = base_weights.copy()
        else:
            # No evolution history, keep current weights
            adjusted = current_weights.copy()
    
    else:
        # Unknown impact type, return None
        logger.warning(f"Unknown impact type: {impact}")
        return None
    
    return adjusted


def get_active_crisis_events(current_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
    """
    Get all active crisis events.
    
    Args:
        current_time: Current timestamp (defaults to now)
    
    Returns:
        List of active crisis events
    """
    if current_time is None:
        current_time = datetime.utcnow()
    
    return load_active_crisis_events(current_time)


def create_revolving_door_event(
    from_role: str,
    to_role: str,
    entity_id: str,
    event_at: datetime,
    boost_axes: Optional[List[str]] = None,
    max_duration_days: int = 180,
    created_by: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create revolving-door transition event with appropriate defaults.
    
    Enforces: Max 180 days, phase-sensitive boosts, mandatory expiration.
    Models temporary influence advantage from Hill → K Street → Agency transitions.
    
    Args:
        from_role: Previous role (e.g., "Chief of Staff", "Committee Counsel")
        to_role: New role (e.g., "K Street Partner", "Trade Association")
        entity_id: Entity ID that transitioned
        event_at: When transition occurred
        boost_axes: Optional list of axes to boost (default: informational_advantage, temporal_leverage, procedural_power)
        max_duration_days: Maximum duration (enforced cap at 180 days)
        created_by: Who created this event
    
    Returns:
        Crisis event dictionary with REVOLVING_DOOR event_type
    
    Example:
        crisis = create_revolving_door_event(
            from_role="Chief of Staff",
            to_role="K Street Partner",
            entity_id="staff-123",
            event_at=datetime(2026, 1, 15)
        )
        save_crisis_event(crisis)
    """
    # Default axes: informational_advantage, temporal_leverage, procedural_power
    if boost_axes is None:
        boost_axes = ["informational_advantage", "temporal_leverage", "procedural_power"]
    
    # Calculate boost magnitudes (conservative: +0.1 to +0.15 per axis)
    weight_overrides = {}
    for axis in boost_axes:
        if axis == "informational_advantage":
            weight_overrides[axis] = 0.15  # Highest for insider knowledge
        elif axis == "temporal_leverage":
            weight_overrides[axis] = 0.12  # High for timing knowledge
        elif axis == "procedural_power":
            weight_overrides[axis] = 0.10  # Moderate for procedural knowledge
        else:
            weight_overrides[axis] = 0.08  # Lower for other axes
    
    # Enforce max duration (180 days hard cap)
    max_duration_days = min(max_duration_days, 180)
    expires_at = event_at + timedelta(days=max_duration_days)
    
    # Create crisis event with revolving-door type
    return create_crisis_event(
        event_type="REVOLVING_DOOR",
        scope="ENTITY_SPECIFIC",
        impact="BOOST",
        event_at=event_at,
        duration="TEMPORARY",  # Always temporary for revolving-door
        affected_entities=[entity_id],
        weight_overrides=weight_overrides,
        expires_at=expires_at,
        description=f"Revolving door: {from_role} → {to_role}",
        created_by=created_by,
        approved_by=None  # Advisory, no approval needed for TEMPORARY
    )


if __name__ == "__main__":
    # Test crisis handler
    test_edge = {
        "edge_id": "test-123",
        "from_entity_id": "member-1",
        "to_entity_id": "committee-1",
        "weights": {
            "procedural_power": 0.8,
            "temporal_leverage": 0.6,
            "informational_advantage": 0.7,
            "institutional_memory": 0.5,
            "retaliation_capacity": 0.4
        }
    }
    
    # Create a leadership change crisis
    crisis = create_crisis_event(
        event_type="LEADERSHIP_CHANGE",
        scope="ENTITY_SPECIFIC",
        impact="BOOST",
        event_at=datetime.utcnow(),
        affected_entities=["member-1"],
        weight_overrides={"procedural_power": 0.2},
        description="New committee chair"
    )
    
    current_time = datetime.utcnow()
    adjusted = apply_crisis_override(test_edge, crisis, current_time)
    print(f"Adjusted weights: {adjusted}")
