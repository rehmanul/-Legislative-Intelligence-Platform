"""
Script: dev__monitor_resource_usage.py
Intent:
- temporal

Reads:
- agent-orchestrator/registry/agent-registry.json
- agent-orchestrator/state/legislative-state.json

Writes:
- None (read-only monitoring)

Schema:
- N/A (monitoring script)
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List

# Path setup
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Constants
BASE_DIR = PROJECT_ROOT
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
STATE_PATH = BASE_DIR / "state" / "legislative-state.json"


def load_registry() -> Dict[str, Any]:
    """Load agent registry."""
    if not REGISTRY_PATH.exists():
        return {"agents": [], "_meta": {}}
    
    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_state() -> Dict[str, Any]:
    """Load legislative state."""
    if not STATE_PATH.exists():
        return {}
    
    with open(STATE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_resource_usage(registry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze current agent resource usage.
    
    Args:
        registry: Agent registry data
        
    Returns:
        Resource usage analysis
    """
    agents = registry.get("agents", [])
    meta = registry.get("_meta", {})
    
    # Count by status
    status_counts = {}
    type_counts = {}
    development_agents = []
    production_agents = []
    
    for agent in agents:
        status = agent.get("status", "UNKNOWN")
        agent_type = agent.get("agent_type", "UNKNOWN")
        agent_id = agent.get("agent_id", "unknown")
        metadata = agent.get("metadata", {})
        
        # Count by status
        status_counts[status] = status_counts.get(status, 0) + 1
        
        # Count by type
        type_counts[agent_type] = type_counts.get(agent_type, 0) + 1
        
        # Categorize by development vs production
        if metadata.get("development_mode") or metadata.get("development"):
            development_agents.append(agent_id)
        else:
            production_agents.append(agent_id)
    
    # Calculate resource utilization
    active_count = status_counts.get("RUNNING", 0) + status_counts.get("IDLE", 0)
    total_count = len(agents)
    utilization = (active_count / total_count * 100) if total_count > 0 else 0
    
    return {
        "total_agents": total_count,
        "status_breakdown": status_counts,
        "type_breakdown": type_counts,
        "active_agents": active_count,
        "utilization_percent": round(utilization, 2),
        "development_agents": development_agents,
        "production_agents": production_agents,
        "registry_metadata": meta
    }


def display_resource_report(analysis: Dict[str, Any], state: Dict[str, Any]) -> None:
    """Display resource usage report."""
    print("=" * 70)
    print("AGENT RESOURCE USAGE REPORT")
    print("=" * 70)
    print()
    
    # System state
    current_state = state.get("current_state", "UNKNOWN")
    print(f"Current Legislative State: {current_state}")
    print()
    
    # Resource summary
    print("Resource Summary:")
    print("-" * 70)
    print(f"Total Agents: {analysis['total_agents']}")
    print(f"Active Agents: {analysis['active_agents']}")
    print(f"Resource Utilization: {analysis['utilization_percent']}%")
    print()
    
    # Status breakdown
    print("Status Breakdown:")
    print("-" * 70)
    for status, count in sorted(analysis['status_breakdown'].items()):
        bar = "#" * min(count, 20)
        print(f"  {status:20s} {count:3d} {bar}")
    print()
    
    # Type breakdown
    print("Agent Type Breakdown:")
    print("-" * 70)
    for agent_type, count in sorted(analysis['type_breakdown'].items()):
        bar = "#" * min(count, 20)
        print(f"  {agent_type:20s} {count:3d} {bar}")
    print()
    
    # Development vs Production
    print("Development vs Production:")
    print("-" * 70)
    print(f"  Development Agents: {len(analysis['development_agents'])}")
    if analysis['development_agents']:
        for agent_id in analysis['development_agents']:
            print(f"    - {agent_id}")
    print()
    print(f"  Production Agents: {len(analysis['production_agents'])}")
    if len(analysis['production_agents']) > 5:
        print(f"    (Showing first 5 of {len(analysis['production_agents'])})")
        for agent_id in analysis['production_agents'][:5]:
            print(f"    - {agent_id}")
    else:
        for agent_id in analysis['production_agents']:
            print(f"    - {agent_id}")
    print()
    
    # Recommendations
    print("Resource Allocation Recommendations:")
    print("-" * 70)
    
    if analysis['active_agents'] == 0:
        print("  [OK] No active agents - resources available for development")
    elif analysis['active_agents'] < 3:
        print("  [OK] Low resource usage - can spawn development agents")
    elif analysis['active_agents'] < 6:
        print("  [WARN] Moderate resource usage - consider limiting concurrent agents")
    else:
        print("  [HIGH] High resource usage - wait for agents to complete or increase limits")
    
    if len(analysis['development_agents']) == 0:
        print("  [TIP] No development agents active - use dev__spawn_intelligence_agents.py")
    
    print()
    print("=" * 70)


def main():
    """Main execution."""
    try:
        # Load data
        registry = load_registry()
        state = load_state()
        
        # Analyze
        analysis = analyze_resource_usage(registry)
        
        # Display report
        display_resource_report(analysis, state)
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
