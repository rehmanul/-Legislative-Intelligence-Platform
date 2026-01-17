"""
Script: dev__workflow.py
Intent:
- temporal

Reads:
- agent-orchestrator/state/legislative-state.json
- agent-orchestrator/registry/agent-registry.json
- agent-orchestrator/config/development_config.json (optional)

Writes:
- None (executes development workflow, no file writes)

Schema:
- N/A (workflow execution script)
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

# Path setup
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from app.agent_spawner import AgentSpawner
    from app.models import LegislativeState
except ImportError as e:
    print(f"[ERROR] Failed to import required modules: {e}")
    sys.exit(1)

# Constants
BASE_DIR = PROJECT_ROOT
STATE_PATH = BASE_DIR / "state" / "legislative-state.json"
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
DEV_CONFIG_PATH = BASE_DIR / "config" / "development_config.json"


def load_state() -> Dict[str, Any]:
    """Load legislative state."""
    if not STATE_PATH.exists():
        raise FileNotFoundError(f"State file not found: {STATE_PATH}")
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


def analyze_resources(registry: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze current resource usage."""
    agents = registry.get("agents", [])
    
    status_counts = {}
    type_counts = {}
    active_count = 0
    development_count = 0
    
    for agent in agents:
        status = agent.get("status", "UNKNOWN")
        agent_type = agent.get("agent_type", "UNKNOWN")
        metadata = agent.get("metadata", {})
        
        status_counts[status] = status_counts.get(status, 0) + 1
        type_counts[agent_type] = type_counts.get(agent_type, 0) + 1
        
        if status in ["RUNNING", "IDLE"]:
            active_count += 1
        
        if metadata.get("development_mode") or metadata.get("development"):
            development_count += 1
    
    total = len(agents)
    utilization = (active_count / total * 100) if total > 0 else 0
    
    return {
        "total_agents": total,
        "active_agents": active_count,
        "development_agents": development_count,
        "utilization_percent": round(utilization, 2),
        "status_breakdown": status_counts,
        "type_breakdown": type_counts,
        "can_spawn": active_count < 6  # Can spawn if less than 6 active
    }


def display_status(state: Dict[str, Any], analysis: Dict[str, Any]) -> None:
    """Display current system status."""
    print("=" * 70)
    print("DEVELOPMENT WORKFLOW - SYSTEM STATUS")
    print("=" * 70)
    print()
    
    current_state = state.get("current_state", "UNKNOWN")
    print(f"Legislative State: {current_state}")
    print(f"Total Agents: {analysis['total_agents']}")
    print(f"Active Agents: {analysis['active_agents']} ({analysis['utilization_percent']}% utilization)")
    print(f"Development Agents: {analysis['development_agents']}")
    print()
    
    if analysis['can_spawn']:
        print("[OK] Resources available - can spawn development agents")
    else:
        print("[WARN] High resource usage - consider waiting or increasing limits")
    print()


def configure_environment(config: Optional[Dict[str, Any]]) -> None:
    """Configure environment variables from development config."""
    if not config:
        print("[INFO] No development config found - using defaults")
        return
    
    env_vars = config.get("environment_variables", {})
    if not env_vars:
        return
    
    print("Configuring environment variables:")
    print("-" * 70)
    
    for key, value in env_vars.items():
        if key != "note":
            os.environ[key] = str(value)
            print(f"  {key} = {value}")
    
    print()


def spawn_development_agents(
    workflow_id: str,
    legislative_state: str,
    max_agents: int = 2
) -> List[Dict[str, Any]]:
    """Spawn Intelligence agents for development."""
    print("Spawning development agents...")
    print("-" * 70)
    
    spawner = AgentSpawner(workflow_id=workflow_id)
    
    # Map state string to enum
    state_map = {
        "PRE_EVT": LegislativeState.PRE_EVT,
        "INTRO_EVT": LegislativeState.INTRO_EVT,
        "COMM_EVT": LegislativeState.COMM_EVT,
        "FLOOR_EVT": LegislativeState.FLOOR_EVT,
        "FINAL_EVT": LegislativeState.FINAL_EVT,
        "IMPL_EVT": LegislativeState.IMPL_EVT
    }
    
    state_enum = state_map.get(legislative_state, LegislativeState.PRE_EVT)
    
    # Spawn only Intelligence agents
    results = spawner.spawn_agents_for_state(
        legislative_state=state_enum,
        agent_types=["Intelligence"],
        max_agents=max_agents
    )
    
    successful = sum(1 for r in results if r.get("success", False))
    print(f"Spawned {successful}/{len(results)} development agents")
    
    for result in results:
        agent_id = result.get("agent_id", "unknown")
        success = result.get("success", False)
        status = "[OK]" if success else "[FAIL]"
        print(f"  {status} {agent_id}")
    
    print()
    return results


def main():
    """Main development workflow."""
    print("=" * 70)
    print("DEVELOPMENT WORKFLOW - INTEGRATED RESOURCE ALLOCATION")
    print("=" * 70)
    print()
    
    try:
        # Step 1: Load system state
        print("Step 1: Loading system state...")
        state = load_state()
        registry = load_registry()
        dev_config = load_dev_config()
        
        workflow_id = state.get("_meta", {}).get("workflow_id", "default-workflow")
        current_state = state.get("current_state", "PRE_EVT")
        
        print(f"[OK] Loaded state: {current_state}")
        print(f"[OK] Workflow ID: {workflow_id}")
        print()
        
        # Step 2: Analyze resources
        print("Step 2: Analyzing resource usage...")
        analysis = analyze_resources(registry)
        display_status(state, analysis)
        
        # Step 3: Configure environment
        print("Step 3: Configuring development environment...")
        configure_environment(dev_config)
        
        # Step 4: Spawn development agents (if resources available)
        if analysis['can_spawn']:
            print("Step 4: Spawning development agents...")
            results = spawn_development_agents(
                workflow_id=workflow_id,
                legislative_state=current_state,
                max_agents=2
            )
            
            if any(r.get("success") for r in results):
                print("[OK] Development agents spawned successfully")
            else:
                print("[WARN] No agents spawned - check logs for errors")
        else:
            print("Step 4: Skipping agent spawn (high resource usage)")
            print("[INFO] Wait for current agents to complete or increase limits")
        
        print()
        print("=" * 70)
        print("DEVELOPMENT WORKFLOW COMPLETE")
        print("=" * 70)
        print()
        print("Next steps:")
        print("  1. Monitor progress: python scripts\\dev__monitor_resource_usage.py")
        print("  2. Check agent registry: registry\\agent-registry.json")
        print("  3. Review agent outputs: artifacts\\<agent_id>\\")
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
