"""
Script: temporal__test__agent_status_html.py
Intent:
- temporal (test script, no persistent outputs)

Reads:
- registry/agent-registry.json
- state/legislative-state.json

Writes:
- None (temporal test only)
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).parent.parent
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
STATE_PATH = BASE_DIR / "state" / "legislative-state.json"

def load_json(path: Path) -> dict:
    """Load JSON file."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return {}

def format_for_cockpit_html(registry_data: dict, state_data: dict) -> dict:
    """Format data for cockpit_template.html consumption."""
    agents_list = registry_data.get("agents", [])
    agents_meta = registry_data.get("_meta", {})
    
    # Count agents by status
    status_counts = {
        "RUNNING": 0,
        "IDLE": 0,
        "WAITING_REVIEW": 0,
        "BLOCKED": 0,
        "RETIRED": 0,
        "FAILED": 0
    }
    
    for agent in agents_list:
        status = agent.get("status", "UNKNOWN")
        if status in status_counts:
            status_counts[status] += 1
    
    # Format for HTML
    cockpit_state = {
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "legislative": state_data,
        "agents": {
            "_meta": agents_meta,
            "agents": agents_list
        },
        "system": {
            "current_state": state_data.get("current_state", "UNKNOWN"),
            "state_definition": state_data.get("state_definition", ""),
            "state_lock": state_data.get("state_lock", False),
            "next_allowed_states": state_data.get("next_allowed_states", []),
            "agents": {
                "total": agents_meta.get("total_agents", len(agents_list)),
                "running": status_counts["RUNNING"],
                "idle": status_counts["IDLE"],
                "waiting_review": status_counts["WAITING_REVIEW"],
                "blocked": status_counts["BLOCKED"],
                "retired": status_counts["RETIRED"]
            }
        },
        "review_gates": [],
        "alerts": []
    }
    
    return cockpit_state

def main():
    """Test agent status display in HTML."""
    print("=" * 80)
    print("Testing Agent Status HTML Display")
    print("=" * 80)
    
    # Load data
    registry_data = load_json(REGISTRY_PATH)
    state_data = load_json(STATE_PATH)
    
    if not registry_data:
        print(f"❌ ERROR: Could not load {REGISTRY_PATH}")
        return
    
    if not state_data:
        print(f"⚠️  WARNING: Could not load {STATE_PATH}")
        state_data = {}
    
    # Format for HTML
    cockpit_state = format_for_cockpit_html(registry_data, state_data)
    
    # Count agents by status
    agents_list = registry_data.get("agents", [])
    status_counts = {}
    for agent in agents_list:
        status = agent.get("status", "UNKNOWN")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Display summary
    print("\nAgent Status Summary:")
    print("-" * 80)
    for status, count in sorted(status_counts.items()):
        indicator = "[ON]" if status == "RUNNING" else "[IDLE]" if status == "IDLE" else "[OFF]" if status in ["RETIRED", "BLOCKED"] else "[WAIT]"
        print(f"  {indicator} {status:20s}: {count:3d} agent(s)")
    
    # Show which agents are "ON" (RUNNING or IDLE)
    running_agents = [a for a in agents_list if a.get("status") == "RUNNING"]
    idle_agents = [a for a in agents_list if a.get("status") == "IDLE"]
    
    print(f"\n[ON] Agents RUNNING: {len(running_agents)}")
    for agent in running_agents:
        print(f"   - {agent.get('agent_id')}")
    
    print(f"\n[IDLE] Agents IDLE: {len(idle_agents)}")
    for agent in idle_agents:
        print(f"   - {agent.get('agent_id')}")
    
    # Show which agents are "OFF" (RETIRED, BLOCKED, WAITING_REVIEW)
    off_agents = [a for a in agents_list if a.get("status") in ["RETIRED", "BLOCKED", "WAITING_REVIEW"]]
    
    print(f"\n[OFF] Agents OFF: {len(off_agents)}")
    for agent in off_agents[:10]:  # Show first 10
        print(f"   - {agent.get('agent_id')}: {agent.get('status')}")
    if len(off_agents) > 10:
        print(f"   ... and {len(off_agents) - 10} more")
    
    # Write formatted JSON for HTML
    output_file = BASE_DIR / "dashboards" / "test_agent_status.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cockpit_state, f, indent=2)
    
    print(f"\n[OK] Formatted JSON written to: {output_file}")
    print(f"\nTo test HTML:")
    print(f"   1. Open: {BASE_DIR / 'dashboards' / 'cockpit_template.html'}")
    print(f"   2. Click 'Load State File'")
    print(f"   3. Select: {output_file}")
    print(f"   4. Verify agent status display matches above summary")
    
    return output_file

if __name__ == "__main__":
    main()
