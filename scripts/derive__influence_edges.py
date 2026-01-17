"""
Script: derive__influence_edges.py
Intent:
- aggregate

Reads:
- data/entities/staff__snapshot.json
- data/committees/committees__snapshot.json

Writes:
- data/edges/influence_edges__derived.json

Schema:
- See schemas/edges/influence_edge.schema.json
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
COMMITTEES_DIR = DATA_DIR / "committees"
EDGES_DIR = DATA_DIR / "edges"
EDGES_DIR.mkdir(parents=True, exist_ok=True)


def load_staff_data() -> Optional[Dict[str, Any]]:
    """Load staff snapshot data."""
    staff_file = ENTITIES_DIR / "staff__snapshot.json"
    if not staff_file.exists():
        return None
    
    try:
        with open(staff_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load staff data: {e}")
        return None


def load_committees_data() -> Optional[Dict[str, Any]]:
    """Load committees snapshot data."""
    committees_file = COMMITTEES_DIR / "committees__snapshot.json"
    if not committees_file.exists():
        return None
    
    try:
        with open(committees_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load committees data: {e}")
        return None


def derive_edges_from_staff(staff_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Derive influence edges from staff data."""
    edges = []
    now = datetime.now(timezone.utc).isoformat()
    
    staff_list = staff_data.get("staff", [])
    for staff in staff_list:
        staff_id = staff.get("staff_id")
        if not staff_id:
            continue
        
        # Default conservative weights (0.5 - requires evidence for higher)
        default_weights = {
            "procedural_power": 0.5,
            "temporal_leverage": 0.5,
            "informational_advantage": 0.5,
            "institutional_memory": 0.5,
            "retaliation_capacity": 0.5
        }
        
        # Staff -> Committee edges (influences_drafting)
        for committee_id in staff.get("linked_to_committee_ids", []):
            edge = {
                "edge_id": str(uuid.uuid4()),
                "from_entity_id": staff_id,
                "to_entity_id": committee_id,
                "edge_type": "influences_drafting",
                "effective_from": now,
                "effective_until": None,
                "legislative_state": None,  # State-independent
                "weights": default_weights.copy(),
                "weight_evolution": [],
                "edge_status": "ACTIVE",
                "activation_events": [
                    {
                        "event_type": "committee_assignment",
                        "event_at": now,
                        "impact": "activated"
                    }
                ],
                "decay_triggers": []
            }
            edges.append(edge)
        
        # Staff -> Member edges (signals_pre_clearance, influences_drafting)
        member_id = staff.get("linked_to_member_id")
        if member_id:
            edge = {
                "edge_id": str(uuid.uuid4()),
                "from_entity_id": staff_id,
                "to_entity_id": member_id,
                "edge_type": "signals_pre_clearance",
                "effective_from": now,
                "effective_until": None,
                "legislative_state": None,
                "weights": default_weights.copy(),
                "weight_evolution": [],
                "edge_status": "ACTIVE",
                "activation_events": [
                    {
                        "event_type": "member_assignment",
                        "event_at": now,
                        "impact": "activated"
                    }
                ],
                "decay_triggers": []
            }
            edges.append(edge)
    
    return edges


def derive_edges_from_committees(committees_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Derive influence edges from committee structure."""
    edges = []
    now = datetime.now(timezone.utc).isoformat()
    
    # Default conservative weights
    default_weights = {
        "procedural_power": 0.5,
        "temporal_leverage": 0.5,
        "informational_advantage": 0.5,
        "institutional_memory": 0.5,
        "retaliation_capacity": 0.5
    }
    
    # Committee -> Subcommittee edges (has_formal_authority_over)
    subcommittees = committees_data.get("subcommittees", [])
    for subcommittee in subcommittees:
        committee_id = subcommittee.get("committee_id")
        subcommittee_id = subcommittee.get("subcommittee_id")
        if committee_id and subcommittee_id and committee_id != "UNKNOWN":
            edge = {
                "edge_id": str(uuid.uuid4()),
                "from_entity_id": committee_id,
                "to_entity_id": subcommittee_id,
                "edge_type": "has_formal_authority_over",
                "effective_from": now,
                "effective_until": None,
                "legislative_state": None,
                "weights": default_weights.copy(),
                "weight_evolution": [],
                "edge_status": "ACTIVE",
                "activation_events": [
                    {
                        "event_type": "subcommittee_creation",
                        "event_at": now,
                        "impact": "activated"
                    }
                ],
                "decay_triggers": []
            }
            edges.append(edge)
    
    # Membership edges will be derived from memberships data when available
    memberships = committees_data.get("memberships", [])
    for membership in memberships:
        member_id = membership.get("member_id")
        committee_id = membership.get("committee_id")
        role = membership.get("role", "")
        
        if member_id and committee_id:
            # Member -> Committee edges based on role
            if role == "chair":
                edge_type = "controls_agenda_of"
                # Chairs have higher procedural power
                weights = default_weights.copy()
                weights["procedural_power"] = 0.8
            elif role == "ranking_member":
                edge_type = "can_delay"
                weights = default_weights.copy()
                weights["temporal_leverage"] = 0.7
            else:
                edge_type = "influences_drafting"
                weights = default_weights.copy()
            
            edge = {
                "edge_id": str(uuid.uuid4()),
                "from_entity_id": member_id,
                "to_entity_id": committee_id,
                "edge_type": edge_type,
                "effective_from": membership.get("appointed_at", now),
                "effective_until": membership.get("removed_at"),
                "legislative_state": "COMM_EVT",  # Committee power most relevant in COMM_EVT
                "weights": weights,
                "weight_evolution": [],
                "edge_status": "ACTIVE" if not membership.get("removed_at") else "ARCHIVED",
                "activation_events": [
                    {
                        "event_type": "committee_membership",
                        "event_at": membership.get("appointed_at", now),
                        "impact": "activated"
                    }
                ],
                "decay_triggers": [
                    {
                        "event_type": "membership_removed",
                        "event_at": membership.get("removed_at", now),
                        "impact": "archived"
                    }
                ] if membership.get("removed_at") else []
            }
            edges.append(edge)
    
    return edges


def derive_influence_edges() -> Dict[str, Any]:
    """Derive influence edges from entity data."""
    print("[derive__influence_edges] Starting edge derivation...")
    
    # Load source data
    staff_data = load_staff_data()
    committees_data = load_committees_data()
    
    all_edges = []
    
    # Derive edges from staff
    if staff_data:
        staff_edges = derive_edges_from_staff(staff_data)
        all_edges.extend(staff_edges)
        print(f"[derive__influence_edges] Derived {len(staff_edges)} edges from staff data")
    
    # Derive edges from committees
    if committees_data:
        committee_edges = derive_edges_from_committees(committees_data)
        all_edges.extend(committee_edges)
        print(f"[derive__influence_edges] Derived {len(committee_edges)} edges from committee data")
    
    # Create output structure
    output_data = {
        "_meta": {
            "source_files": [
                str(ENTITIES_DIR / "staff__snapshot.json") if staff_data else None,
                str(COMMITTEES_DIR / "committees__snapshot.json") if committees_data else None
            ],
            "derived_at": datetime.now(timezone.utc).isoformat(),
            "script": "derive__influence_edges.py",
            "schema_version": "1.0.0",
            "doctrine_version": "Congressional Network Mapping v1.0",
            "count": {
                "total_edges": len(all_edges),
                "by_type": {}
            }
        },
        "edges": all_edges
    }
    
    # Count by edge type
    for edge in all_edges:
        edge_type = edge.get("edge_type")
        output_data["_meta"]["count"]["by_type"][edge_type] = output_data["_meta"]["count"]["by_type"].get(edge_type, 0) + 1
    
    return output_data


def main():
    """Main derivation function."""
    try:
        output_data = derive_influence_edges()
        
        # Write output
        output_file = EDGES_DIR / "influence_edges__derived.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"[derive__influence_edges] Derivation complete: {output_file}")
        print(f"[derive__influence_edges] Derived {output_data['_meta']['count']['total_edges']} influence edges")
        return output_file
        
    except Exception as e:
        print(f"[derive__influence_edges] ERROR: Derivation failed: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)
