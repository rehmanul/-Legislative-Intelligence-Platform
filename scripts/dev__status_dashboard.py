"""
Script: dev__status_dashboard.py
Intent:
- temporal

Reads:
- agent-orchestrator/state/legislative-state.json
- agent-orchestrator/registry/agent-registry.json
- agent-orchestrator/config/development_config.json (optional)

Writes:
- None (read-only dashboard)

Schema:
- N/A (dashboard script)
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

# Path setup
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Constants
BASE_DIR = PROJECT_ROOT
STATE_PATH = BASE_DIR / "state" / "legislative-state.json"
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
DEV_CONFIG_PATH = BASE_DIR / "config" / "development_config.json"


def load_state() -> Dict[str, Any]:
    """Load legislative state."""
    if not STATE_PATH.exists():
        return {}
    with open(STATE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_registry() -> Dict[str, Any]:
    """Load agent registry."""
    if not REGISTRY_PATH.exists():
        return {"agents": [], "_meta": {}}
    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_dev_config() -> Optional[Dict[str, Any]]:
    """Load development configuration."""
    if not DEV_CONFIG_PATH.exists():
        return None
    with open(DEV_CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def format_timestamp(timestamp_str: str) -> str:
    """Format ISO timestamp to readable string."""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        delta = now - dt
        
        if delta < timedelta(minutes=1):
            return f"{delta.seconds}s ago"
        elif delta < timedelta(hours=1):
            return f"{delta.seconds // 60}m ago"
        elif delta < timedelta(days=1):
            return f"{delta.seconds // 3600}h ago"
        else:
            return f"{delta.days}d ago"
    except:
        return timestamp_str


def display_dashboard(state: Dict[str, Any], registry: Dict[str, Any], config: Optional[Dict[str, Any]]) -> None:
    """Display development status dashboard."""
    print("=" * 80)
    print("DEVELOPMENT STATUS DASHBOARD".center(80))
    print("=" * 80)
    print()
    
    # System State
    print("SYSTEM STATE")
    print("-" * 80)
    current_state = state.get("current_state", "UNKNOWN")
    workflow_id = state.get("_meta", {}).get("workflow_id", "unknown")
    print(f"  Legislative State: {current_state}")
    print(f"  Workflow ID: {workflow_id}")
    print()
    
    # Resource Configuration
    print("RESOURCE CONFIGURATION")
    print("-" * 80)
    if config:
        limits = config.get("execution_limits", {})
        print(f"  Max Concurrent Agents: {limits.get('max_concurrent_agents', 'N/A')}")
        print(f"  Development Workers: {limits.get('development_workers', 'N/A')}")
        print(f"  Production Workers: {limits.get('production_workers', 'N/A')}")
    else:
        print("  [INFO] No development config found - using defaults")
    print()
    
    # Agent Statistics
    agents = registry.get("agents", [])
    meta = registry.get("_meta", {})
    
    status_counts = {}
    type_counts = {}
    development_agents = []
    production_agents = []
    active_agents = []
    
    for agent in agents:
        status = agent.get("status", "UNKNOWN")
        agent_type = agent.get("agent_type", "UNKNOWN")
        agent_id = agent.get("agent_id", "unknown")
        metadata = agent.get("metadata", {})
        last_heartbeat = agent.get("last_heartbeat", "")
        
        status_counts[status] = status_counts.get(status, 0) + 1
        type_counts[agent_type] = type_counts.get(agent_type, 0) + 1
        
        if metadata.get("development_mode") or metadata.get("development"):
            development_agents.append({
                "id": agent_id,
                "status": status,
                "type": agent_type,
                "heartbeat": last_heartbeat
            })
        else:
            production_agents.append({
                "id": agent_id,
                "status": status,
                "type": agent_type,
                "heartbeat": last_heartbeat
            })
        
        if status in ["RUNNING", "IDLE"]:
            active_agents.append({
                "id": agent_id,
                "status": status,
                "type": agent_type,
                "heartbeat": last_heartbeat
            })
    
    total = len(agents)
    active_count = len(active_agents)
    utilization = (active_count / total * 100) if total > 0 else 0
    
    print("AGENT STATISTICS")
    print("-" * 80)
    print(f"  Total Agents: {total}")
    print(f"  Active Agents: {active_count} ({utilization:.1f}% utilization)")
    print(f"  Development Agents: {len(development_agents)}")
    print(f"  Production Agents: {len(production_agents)}")
    print()
    
    # Status Breakdown
    print("STATUS BREAKDOWN")
    print("-" * 80)
    for status, count in sorted(status_counts.items()):
        bar = "#" * min(count, 30)
        print(f"  {status:20s} {count:3d} {bar}")
    print()
    
    # Type Breakdown
    print("TYPE BREAKDOWN")
    print("-" * 80)
    for agent_type, count in sorted(type_counts.items()):
        bar = "#" * min(count, 30)
        print(f"  {agent_type:20s} {count:3d} {bar}")
    print()
    
    # Active Agents
    if active_agents:
        print("ACTIVE AGENTS")
        print("-" * 80)
        for agent in active_agents[:10]:  # Show first 10
            heartbeat_str = format_timestamp(agent["heartbeat"]) if agent["heartbeat"] else "N/A"
            print(f"  [{agent['status']:12s}] {agent['id']:40s} ({heartbeat_str})")
        if len(active_agents) > 10:
            print(f"  ... and {len(active_agents) - 10} more")
        print()
    
    # Development Agents
    if development_agents:
        print("DEVELOPMENT AGENTS")
        print("-" * 80)
        for agent in development_agents:
            heartbeat_str = format_timestamp(agent["heartbeat"]) if agent["heartbeat"] else "N/A"
            print(f"  [{agent['status']:12s}] {agent['id']:40s} ({heartbeat_str})")
        print()
    
    # Recommendations
    print("RECOMMENDATIONS")
    print("-" * 80)
    if active_count == 0:
        print("  [OK] No active agents - resources fully available for development")
    elif active_count < 3:
        print("  [OK] Low resource usage - can spawn development agents")
    elif active_count < 6:
        print("  [WARN] Moderate resource usage - consider limiting concurrent agents")
    else:
        print("  [HIGH] High resource usage - wait for agents to complete or increase limits")
    
    if len(development_agents) == 0:
        print("  [TIP] No development agents active - use dev__spawn_intelligence_agents.py")
    
    print()
    print("=" * 80)
    print(f"Dashboard generated at: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 80)


def main():
    """Main dashboard."""
    try:
        state = load_state()
        registry = load_registry()
        config = load_dev_config()
        
        display_dashboard(state, registry, config)
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
