"""
Script: derive__edge_evolution.py
Intent:
- aggregate

Reads:
- data/edges/influence_edges__derived.json
- data/temporal/power_transfers.jsonl
- Event data

Writes:
- Updates data/edges/influence_edges__derived.json with lifecycle status

Schema:
- See schemas/edges/influence_edge.schema.json (adds lifecycle fields)
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
EDGES_DIR = DATA_DIR / "edges"
TEMPORAL_DIR = DATA_DIR / "temporal"


def load_edges() -> List[Dict[str, Any]]:
    """Load current edges."""
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


def load_power_transfers() -> List[Dict[str, Any]]:
    """Load power transfer events."""
    transfers_log = TEMPORAL_DIR / "power_transfers.jsonl"
    if not transfers_log.exists():
        return []
    
    transfers = []
    try:
        with open(transfers_log, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    transfers.append(json.loads(line))
    except Exception as e:
        print(f"Warning: Failed to load power transfers: {e}")
    
    return transfers


def update_edge_lifecycle(
    edges: List[Dict[str, Any]],
    power_transfers: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Update edge lifecycle status based on events.
    
    Activation: New committee assignment → activate has_formal_authority_over edge
    Strengthening: Repeated successful influence → increase weights
    Decay: Staff departure → reduce institutional_memory weight
    Deactivation: Committee membership removal → set status to ARCHIVED
    """
    print("[derive__edge_evolution] Updating edge lifecycle...")
    
    updated_edges = []
    now = datetime.now(timezone.utc).isoformat()
    
    for edge in edges:
        updated_edge = edge.copy()
        
        # Check for activation events
        # (In production, would check events like committee assignments, staff movements)
        
        # Check for decay triggers
        # (In production, would check for staff departures, membership removals)
        
        # For now, maintain current status
        if "edge_status" not in updated_edge:
            updated_edge["edge_status"] = "ACTIVE"
        
        if "activation_events" not in updated_edge:
            updated_edge["activation_events"] = []
        
        if "decay_triggers" not in updated_edge:
            updated_edge["decay_triggers"] = []
        
        updated_edges.append(updated_edge)
    
    return updated_edges


def derive_edge_evolution() -> Dict[str, Any]:
    """Main derivation function."""
    print("[derive__edge_evolution] Starting edge evolution derivation...")
    
    # Load source data
    edges = load_edges()
    power_transfers = load_power_transfers()
    
    # Update edge lifecycle
    updated_edges = update_edge_lifecycle(edges, power_transfers)
    
    # Count by status
    status_count = {}
    for edge in updated_edges:
        status = edge.get("edge_status", "ACTIVE")
        status_count[status] = status_count.get(status, 0) + 1
    
    # Create output structure
    output_data = {
        "_meta": {
            "source_files": [
                str(EDGES_DIR / "influence_edges__derived.json"),
                str(TEMPORAL_DIR / "power_transfers.jsonl") if power_transfers else None
            ],
            "derived_at": datetime.now(timezone.utc).isoformat(),
            "script": "derive__edge_evolution.py",
            "schema_version": "1.0.0",
            "doctrine_version": "Congressional Network Mapping v1.0",
            "count": {
                "total_edges": len(updated_edges),
                "by_status": status_count
            }
        },
        "edges": updated_edges
    }
    
    return output_data


def main():
    """Main derivation function."""
    try:
        output_data = derive_edge_evolution()
        
        # Write output (overwrites existing file with updated lifecycle)
        output_file = EDGES_DIR / "influence_edges__derived.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"[derive__edge_evolution] Evolution derivation complete: {output_file}")
        print(f"[derive__edge_evolution] Updated {output_data['_meta']['count']['total_edges']} edges")
        print(f"[derive__edge_evolution] Status breakdown: {output_data['_meta']['count']['by_status']}")
        return output_file
        
    except Exception as e:
        print(f"[derive__edge_evolution] ERROR: Derivation failed: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)
