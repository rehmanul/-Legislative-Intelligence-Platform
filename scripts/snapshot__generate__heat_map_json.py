"""
Script: snapshot__generate__heat_map_json.py
Intent:
- snapshot

Reads:
- registry/agent-registry.json
- state/legislative-state.json
- review/HR_*_queue.json (4 files)
- audit/audit-log.jsonl (optional, for recent errors)

Writes:
- dashboards/heat_map_snapshot.json (operational, disposable)

Schema:
{
  "_meta": {
    "generated_at": "ISO-8601 UTC timestamp",
    "script": "snapshot__generate__heat_map_json.py",
    "schema_version": "1.0.0"
  },
  "state": {
    "current_state": "INTRO_EVT",
    "state_definition": "Bill Vehicle Identified",
    "time_in_state_seconds": 123456,
    "next_allowed_states": ["COMM_EVT"],
    "advancement_ready": false,
    "blocking_reasons": ["HR_PRE approval pending"]
  },
  "agents": {
    "RUNNING": 2,
    "WAITING_REVIEW": 1,
    "BLOCKED": 1,
    "IDLE": 0,
    "RETIRED": 8,
    "FAILED": 0
  },
  "review_gates": {
    "HR_PRE": {
      "pending_count": 0,
      "last_review": {
        "decision": "APPROVED",
        "decision_at": "ISO-8601 UTC",
        "age_seconds": 123456
      }
    },
    ...
  },
  "blocking_conditions": [
    "agent_id: WAITING_REVIEW (HR_PRE)"
  ],
  "overall_status": {
    "color": "GREEN" | "YELLOW" | "RED",
    "reason": "All systems operational"
  }
}
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

# Path setup
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

# Import shared functions from main heat map script
from snapshot__generate__heat_map import (
    parse_timestamp,
    format_duration,
    load_json,
    count_agents_by_status,
    load_review_gates,
    analyze_state_advancement,
    get_blocking_conditions,
    check_recent_errors,
    determine_overall_status,
    calculate_time_in_state,
    STATE_DEFINITIONS,
    REVIEW_GATES,
)

# Constants
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
STATE_PATH = BASE_DIR / "state" / "legislative-state.json"
REVIEW_DIR = BASE_DIR / "review"
AUDIT_LOG_PATH = BASE_DIR / "audit" / "audit-log.jsonl"
DASHBOARDS_DIR = BASE_DIR / "dashboards"
DASHBOARDS_DIR.mkdir(parents=True, exist_ok=True)


def get_review_gate_data(gate_data: Dict[str, Any]) -> Dict[str, Any]:
    """Get structured data for a review gate."""
    pending_count = len(gate_data.get("pending_reviews", []))
    
    # Get last review from history
    review_history = gate_data.get("review_history", [])
    last_review_data = None
    if review_history:
        last_review = review_history[-1]
        decision_at = last_review.get("decision_at", "")
        if decision_at:
            dt = parse_timestamp(decision_at)
            if dt:
                now = datetime.now(timezone.utc)
                age_seconds = (now - dt).total_seconds()
                last_review_data = {
                    "decision": last_review.get("decision", ""),
                    "decision_at": decision_at,
                    "age_seconds": age_seconds,
                }
    
    return {
        "pending_count": pending_count,
        "last_review": last_review_data,
    }


def calculate_time_in_state_seconds(state_data: Dict[str, Any]) -> Optional[float]:
    """Calculate time spent in current state in seconds."""
    state_history = state_data.get("state_history", [])
    if not state_history:
        return None
    
    current_state = state_data.get("current_state", "UNKNOWN")
    # Find when we entered current state
    for entry in reversed(state_history):
        if entry.get("state") == current_state:
            entered_at = entry.get("entered_at", "")
            if entered_at:
                dt = parse_timestamp(entered_at)
                if dt:
                    now = datetime.now(timezone.utc)
                    return (now - dt).total_seconds()
    
    return None


def generate_heat_map_json() -> Dict[str, Any]:
    """Generate heat map snapshot as JSON."""
    # Load canonical data
    registry_data = load_json(REGISTRY_PATH)
    state_data = load_json(STATE_PATH)
    review_gates = load_review_gates()
    
    agents = registry_data.get("agents", [])
    agent_counts = count_agents_by_status(agents)
    
    # Analyze state advancement
    state_ready, blocking_reasons = analyze_state_advancement(state_data, review_gates)
    
    # Check for errors
    has_errors = check_recent_errors()
    
    # Determine overall status
    status_color, status_reason = determine_overall_status(
        agent_counts, review_gates, state_ready, has_errors
    )
    
    # Calculate time in state
    time_in_state_seconds = calculate_time_in_state_seconds(state_data)
    
    # Build JSON structure
    current_state = state_data.get("current_state", "UNKNOWN")
    state_def = STATE_DEFINITIONS.get(current_state, current_state)
    
    result = {
        "_meta": {
            "generated_at": datetime.now(timezone.utc).isoformat() + "Z",
            "script": "snapshot__generate__heat_map_json.py",
            "schema_version": "1.0.0",
        },
        "state": {
            "current_state": current_state,
            "state_definition": state_def,
            "time_in_state_seconds": time_in_state_seconds,
            "next_allowed_states": state_data.get("next_allowed_states", []),
            "advancement_ready": state_ready,
            "blocking_reasons": blocking_reasons,
        },
        "agents": agent_counts,
        "review_gates": {},
        "blocking_conditions": get_blocking_conditions(agents, review_gates),
        "overall_status": {
            "color": status_color,
            "reason": status_reason,
        },
    }
    
    # Add review gate data
    for gate_id in ["HR_PRE", "HR_LANG", "HR_MSG", "HR_RELEASE"]:
        gate_data = review_gates.get(gate_id, {})
        result["review_gates"][gate_id] = get_review_gate_data(gate_data)
    
    return result


def main():
    """Main execution."""
    print("[snapshot__generate__heat_map_json] Generating heat map snapshot JSON...")
    
    try:
        heat_map_data = generate_heat_map_json()
        
        # Write to file
        output_file = DASHBOARDS_DIR / "heat_map_snapshot.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(heat_map_data, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Heat map snapshot JSON written to: {output_file}")
        print(f"   Status: {heat_map_data['overall_status']['color']} - {heat_map_data['overall_status']['reason']}")
        
        return output_file
        
    except Exception as e:
        print(f"[ERROR] Error generating heat map JSON: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)
