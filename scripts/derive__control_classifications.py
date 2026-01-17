"""
Script: derive__control_classifications.py
Intent:
- aggregate

Reads:
- data/edges/influence_edges__derived.json
- data/entities/staff__snapshot.json
- Current legislative state (from state/legislative-state.json)

Writes:
- data/edges/control_classifications__derived.json

Schema:
- See schemas/edges/control_classification.schema.json
"""

import sys
import json
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

# Path setup
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

# Data directories
DATA_DIR = BASE_DIR / "data"
ENTITIES_DIR = DATA_DIR / "entities"
EDGES_DIR = DATA_DIR / "edges"
STATE_DIR = BASE_DIR / "state"


def load_edges() -> List[Dict[str, Any]]:
    """Load influence edges."""
    edges_file = EDGES_DIR / "influence_edges__derived.json"
    if not edges_file.exists():
        return []
    
    try:
        with open(edges_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("edges", [])
    except Exception as e:
        print(f"Warning: Failed to load edges: {e}")
        return []


def get_current_legislative_state() -> Optional[str]:
    """Get current legislative state."""
    state_file = STATE_DIR / "legislative-state.json"
    if not state_file.exists():
        return None
    
    try:
        with open(state_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("current_state")
    except Exception as e:
        print(f"Warning: Failed to load legislative state: {e}")
        return None


def classify_entity_power(
    entity_id: str,
    edges: List[Dict[str, Any]],
    legislative_state: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Classify entity power based on edges.
    
    Classification logic:
    - PRIMARY: Entity can unilaterally prevent advancement (e.g., Committee Chair can block markup)
    - SECONDARY: Entity can delay or force negotiation (e.g., Ranking Member can delay)
    - SHADOW: Entity influences without formal authority (e.g., Appropriations staff influences authorizers)
    """
    # Get edges from this entity
    entity_edges = [
        e for e in edges
        if e.get("from_entity_id") == entity_id
        and e.get("edge_status") == "ACTIVE"
        and (legislative_state is None or e.get("legislative_state") == legislative_state or e.get("legislative_state") is None)
    ]
    
    if not entity_edges:
        return None
    
    # Determine control type based on edge types and weights
    has_block = any(e.get("edge_type") == "can_block" for e in entity_edges)
    has_authority = any(e.get("edge_type") == "has_formal_authority_over" for e in entity_edges)
    has_controls_agenda = any(e.get("edge_type") == "controls_agenda_of" for e in entity_edges)
    has_delay = any(e.get("edge_type") == "can_delay" for e in entity_edges)
    has_routes_around = any(e.get("edge_type") == "routes_around" for e in entity_edges)
    
    # Calculate aggregate procedural power
    max_procedural_power = max(
        (e.get("weights", {}).get("procedural_power", 0.0) for e in entity_edges),
        default=0.0
    )
    
    # Classification logic
    control_type = "SHADOW"
    rationale = ""
    evidence = []
    
    if has_block or (has_authority and max_procedural_power > 0.7):
        control_type = "PRIMARY"
        rationale = "Entity has unilateral blocking power or high formal authority"
        if has_block:
            evidence.append("Has 'can_block' edge type")
        if has_authority:
            evidence.append(f"Has 'has_formal_authority_over' edge with procedural_power={max_procedural_power:.2f}")
    elif has_controls_agenda or has_delay or (max_procedural_power > 0.5 and max_procedural_power <= 0.7):
        control_type = "SECONDARY"
        rationale = "Entity can delay or force negotiation but cannot unilaterally block"
        if has_controls_agenda:
            evidence.append("Has 'controls_agenda_of' edge type")
        if has_delay:
            evidence.append("Has 'can_delay' edge type")
        evidence.append(f"Procedural power score: {max_procedural_power:.2f}")
    else:
        control_type = "SHADOW"
        rationale = "Entity influences without formal authority"
        if has_routes_around:
            evidence.append("Has 'routes_around' edge type (informal influence)")
        else:
            evidence.append("Has influence edges but no formal authority")
        evidence.append(f"Max procedural power score: {max_procedural_power:.2f}")
    
    now = datetime.now(timezone.utc).isoformat()
    
    return {
        "classification_id": str(uuid.uuid4()),
        "entity_id": entity_id,
        "control_type": control_type,
        "context": {
            "bill_id": None,
            "policy_area": None,
            "legislative_state": legislative_state,
            "committee_id": None
        },
        "evidence": evidence,
        "rationale": rationale,
        "overrides_classification_id": None,
        "temporal_validity": {
            "effective_from": now,
            "effective_until": None
        }
    }


def derive_control_classifications() -> Dict[str, Any]:
    """Derive control classifications from edges."""
    print("[derive__control_classifications] Starting classification derivation...")
    
    # Load source data
    edges = load_edges()
    legislative_state = get_current_legislative_state()
    
    # Get unique entity IDs from edges
    entity_ids = set()
    for edge in edges:
        if edge.get("edge_status") == "ACTIVE":
            entity_ids.add(edge.get("from_entity_id"))
            entity_ids.add(edge.get("to_entity_id"))
    
    # Classify each entity
    classifications = []
    for entity_id in entity_ids:
        classification = classify_entity_power(entity_id, edges, legislative_state)
        if classification:
            classifications.append(classification)
    
    # Count by type
    count_by_type = {"PRIMARY": 0, "SECONDARY": 0, "SHADOW": 0}
    for classification in classifications:
        control_type = classification.get("control_type")
        count_by_type[control_type] = count_by_type.get(control_type, 0) + 1
    
    # Create output structure
    output_data = {
        "_meta": {
            "source_files": [
                str(EDGES_DIR / "influence_edges__derived.json"),
                str(STATE_DIR / "legislative-state.json") if legislative_state else None
            ],
            "derived_at": datetime.now(timezone.utc).isoformat(),
            "script": "derive__control_classifications.py",
            "current_legislative_state": legislative_state,
            "schema_version": "1.0.0",
            "doctrine_version": "Congressional Network Mapping v1.0",
            "count": {
                "total_classifications": len(classifications),
                "by_type": count_by_type
            }
        },
        "classifications": classifications
    }
    
    return output_data


def main():
    """Main derivation function."""
    try:
        output_data = derive_control_classifications()
        
        # Write output
        output_file = EDGES_DIR / "control_classifications__derived.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"[derive__control_classifications] Derivation complete: {output_file}")
        print(f"[derive__control_classifications] Derived {output_data['_meta']['count']['total_classifications']} classifications")
        print(f"[derive__control_classifications] PRIMARY: {output_data['_meta']['count']['by_type'].get('PRIMARY', 0)}, SECONDARY: {output_data['_meta']['count']['by_type'].get('SECONDARY', 0)}, SHADOW: {output_data['_meta']['count']['by_type'].get('SHADOW', 0)}")
        return output_file
        
    except Exception as e:
        print(f"[derive__control_classifications] ERROR: Derivation failed: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)
