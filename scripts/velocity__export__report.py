"""
Script: velocity__export__report.py
Intent:
- snapshot

Reads:
- state/legislative-state.json
- review/HR_*_queue.json (4 files)
- registry/agent-registry.json
- audit/audit-log.jsonl

Writes:
- dashboards/velocity_report.json (operational, disposable)

Schema:
Structured JSON export of velocity metrics for external analysis.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any

# Path setup
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

# Import from velocity calculation script
from velocity__calculate__metrics import (
    load_json,
    calculate_time_in_state,
    calculate_review_times,
    calculate_agent_execution_times,
    get_queue_depths,
    identify_bottlenecks,
)

# Constants
STATE_PATH = BASE_DIR / "state" / "legislative-state.json"
REVIEW_DIR = BASE_DIR / "review"
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
DASHBOARDS_DIR = BASE_DIR / "dashboards"
DASHBOARDS_DIR.mkdir(parents=True, exist_ok=True)


def generate_velocity_report() -> Dict[str, Any]:
    """Generate velocity metrics as structured JSON."""
    # Load canonical data
    state_data = load_json(STATE_PATH)
    registry_data = load_json(REGISTRY_PATH)
    
    # Load review gates
    review_gates = {}
    if REVIEW_DIR.exists():
        for queue_file in REVIEW_DIR.glob("HR_*_queue.json"):
            gate_data = load_json(queue_file)
            gate_id = gate_data.get("_meta", {}).get("review_gate", "UNKNOWN")
            review_gates[gate_id] = gate_data
    
    # Calculate metrics
    time_in_state_seconds = calculate_time_in_state(state_data)
    review_times = calculate_review_times(review_gates)
    agent_times = calculate_agent_execution_times(registry_data)
    queue_depths = get_queue_depths(review_gates, registry_data)
    bottlenecks = identify_bottlenecks(review_times, agent_times, queue_depths, review_gates, registry_data)
    
    # Build structured report
    report = {
        "_meta": {
            "generated_at": datetime.now(timezone.utc).isoformat() + "Z",
            "script": "velocity__export__report.py",
            "schema_version": "1.0.0",
        },
        "time_in_state": {
            "current_state": state_data.get("current_state", "UNKNOWN"),
            "time_seconds": time_in_state_seconds,
            "expected_days": None,  # Would need to calculate from STATE_ADVANCEMENT_EXPECTED
        },
        "review_cycle_times": review_times,
        "agent_execution_times": agent_times,
        "queue_depths": queue_depths,
        "bottlenecks": [
            {"priority": priority, "description": desc}
            for priority, desc in bottlenecks
        ],
    }
    
    return report


def main():
    """Main execution."""
    print("[velocity__export__report] Generating velocity report JSON...")
    
    try:
        report_data = generate_velocity_report()
        
        # Write to file
        output_file = DASHBOARDS_DIR / "velocity_report.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Velocity report JSON written to: {output_file}")
        print(f"   Bottlenecks identified: {len(report_data['bottlenecks'])}")
        
        return output_file
        
    except Exception as e:
        print(f"[ERROR] Error generating velocity report: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)
