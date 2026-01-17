"""
Script: temporal__track__power_changes.py
Intent:
- temporal

Reads:
- data/edges/influence_edges__derived.json
- state/legislative-state.json
- Events from various sources

Writes:
- data/temporal/power_transfers.jsonl (append-only log)
- data/temporal/snapshots/network__{state}__{timestamp}.json (on state transitions)
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
TEMPORAL_DIR.mkdir(parents=True, exist_ok=True)
SNAPSHOTS_DIR = TEMPORAL_DIR / "snapshots"
SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)

STATE_DIR = BASE_DIR / "state"
POWER_TRANSFERS_LOG = TEMPORAL_DIR / "power_transfers.jsonl"


def load_current_state() -> Optional[str]:
    """Load current legislative state."""
    state_file = STATE_DIR / "legislative-state.json"
    if not state_file.exists():
        return None
    
    try:
        with open(state_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("current_state")
    except Exception as e:
        print(f"Warning: Failed to load state: {e}")
        return None


def load_previous_snapshot_state() -> Optional[str]:
    """Load legislative state from most recent snapshot."""
    snapshots = list(SNAPSHOTS_DIR.glob("network__*.json"))
    if not snapshots:
        return None
    
    # Get most recent snapshot
    snapshots.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    most_recent = snapshots[0]
    
    try:
        with open(most_recent, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("legislative_state")
    except Exception as e:
        print(f"Warning: Failed to load snapshot state: {e}")
        return None


def create_network_snapshot(current_state: Optional[str]) -> Optional[Dict[str, Any]]:
    """Create network snapshot at current point in time."""
    print(f"[temporal__track__power_changes] Creating network snapshot for state: {current_state}")
    
    # Load current edges
    edges_file = EDGES_DIR / "influence_edges__derived.json"
    edges_data = []
    if edges_file.exists():
        try:
            with open(edges_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                edges_data = data.get("edges", [])
        except Exception as e:
            print(f"Warning: Failed to load edges: {e}")
    
    # Load current classifications
    classifications_file = EDGES_DIR / "control_classifications__derived.json"
    classifications_data = []
    if classifications_file.exists():
        try:
            with open(classifications_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                classifications_data = data.get("classifications", [])
        except Exception as e:
            print(f"Warning: Failed to load classifications: {e}")
    
    # Load entities
    entities_data = []
    staff_file = DATA_DIR / "entities" / "staff__snapshot.json"
    if staff_file.exists():
        try:
            with open(staff_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                entities_data.extend(data.get("staff", []))
        except Exception as e:
            print(f"Warning: Failed to load staff: {e}")
    
    now = datetime.now(timezone.utc).isoformat()
    
    snapshot = {
        "_meta": {
            "schema_version": "1.0.0",
            "doctrine_version": "Congressional Network Mapping v1.0",
            "last_updated": now
        },
        "snapshot_id": str(uuid.uuid4()),
        "snapshot_at": now,
        "legislative_state": current_state,
        "entities": entities_data,
        "edges": edges_data,
        "control_classifications": classifications_data
    }
    
    return snapshot


def log_power_transfer(
    from_entity_id: str,
    to_entity_id: str,
    transfer_mechanism: str,
    power_metrics: Dict[str, float],
    description: Optional[str] = None
):
    """Log power transfer event to append-only log."""
    transfer_event = {
        "_meta": {
            "schema_version": "1.0.0",
            "doctrine_version": "Congressional Network Mapping v1.0",
            "last_updated": datetime.now(timezone.utc).isoformat()
        },
        "transfer_id": str(uuid.uuid4()),
        "from_entity_id": from_entity_id,
        "to_entity_id": to_entity_id,
        "transfer_mechanism": transfer_mechanism,
        "transfer_at": datetime.now(timezone.utc).isoformat(),
        "power_metric_transferred": power_metrics,
        "context": {
            "bill_id": None,
            "committee_id": None,
            "legislative_state": load_current_state()
        },
        "description": description or f"Power transfer via {transfer_mechanism}"
    }
    
    # Append to log file
    with open(POWER_TRANSFERS_LOG, 'a', encoding='utf-8') as f:
        f.write(json.dumps(transfer_event) + '\n')
    
    print(f"[temporal__track__power_changes] Logged power transfer: {from_entity_id} -> {to_entity_id} via {transfer_mechanism}")


def track_power_changes():
    """Main tracking function - monitors state changes and creates snapshots."""
    print("[temporal__track__power_changes] Starting power change tracking...")
    
    current_state = load_current_state()
    previous_snapshot_state = load_previous_snapshot_state()
    
    # Check if state has changed
    if current_state and current_state != previous_snapshot_state:
        print(f"[temporal__track__power_changes] State changed: {previous_snapshot_state} -> {current_state}")
        
        # Create snapshot at state transition
        snapshot = create_network_snapshot(current_state)
        if snapshot:
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
            snapshot_file = SNAPSHOTS_DIR / f"network__{current_state}__{timestamp}.json"
            
            with open(snapshot_file, 'w', encoding='utf-8') as f:
                json.dump(snapshot, f, indent=2, ensure_ascii=False)
            
            print(f"[temporal__track__power_changes] Snapshot created: {snapshot_file}")
    
    # Check for power transfer events (placeholder - would monitor events in production)
    # This is a placeholder for event monitoring logic
    print("[temporal__track__power_changes] Power change tracking complete")


def main():
    """Main function."""
    try:
        track_power_changes()
        return True
    except Exception as e:
        print(f"[temporal__track__power_changes] ERROR: Tracking failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)
