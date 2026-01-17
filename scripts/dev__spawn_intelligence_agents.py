"""
Script: dev__spawn_intelligence_agents.py
Intent:
- temporal

Reads:
- agent-orchestrator/state/legislative-state.json
- agent-orchestrator/registry/agent-registry.json

Writes:
- None (spawns agents via API, no file writes)

Schema:
- N/A (execution script)
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

# Path setup
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from app.agent_spawner import AgentSpawner
    from app.models import LegislativeState
    from app.agent_client import AgentClient
except ImportError as e:
    print(f"ERROR: Failed to import required modules: {e}")
    print("Make sure you're running from the agent-orchestrator directory")
    sys.exit(1)

# Constants
BASE_DIR = PROJECT_ROOT
STATE_PATH = BASE_DIR / "state" / "legislative-state.json"
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"


def load_workflow_state() -> Dict[str, Any]:
    """Load current workflow state."""
    if not STATE_PATH.exists():
        raise FileNotFoundError(f"State file not found: {STATE_PATH}")
    
    with open(STATE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_workflow_id() -> str:
    """Get workflow ID from state file."""
    state = load_workflow_state()
    return state.get("_meta", {}).get("workflow_id", "default-workflow")


def get_current_state() -> str:
    """Get current legislative state."""
    state = load_workflow_state()
    return state.get("current_state", "PRE_EVT")


def spawn_intelligence_agents_for_development(
    workflow_id: str,
    legislative_state: str,
    max_agents: int = 2,
    priority: int = 10
) -> List[Dict[str, Any]]:
    """
    Spawn Intelligence agents for development work.
    
    Args:
        workflow_id: Workflow identifier
        legislative_state: Current legislative state
        max_agents: Maximum number of agents to spawn
        priority: Priority level (higher = executed first)
        
    Returns:
        List of spawn results
    """
    print(f"[DEV] Spawning Intelligence agents for development...")
    print(f"[DEV] Workflow: {workflow_id}")
    print(f"[DEV] State: {legislative_state}")
    print(f"[DEV] Max agents: {max_agents}")
    print(f"[DEV] Priority: {priority}")
    print()
    
    # Create spawner
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
    
    # Spawn only Intelligence agents (read-only, safe for development)
    results = spawner.spawn_agents_for_state(
        legislative_state=state_enum,
        agent_types=["Intelligence"],  # Only Intelligence agents
        max_agents=max_agents
    )
    
    successful = sum(1 for r in results if r.get("success", False))
    print(f"[DEV] Spawned {successful}/{len(results)} Intelligence agents successfully")
    
    for result in results:
        agent_id = result.get("agent_id", "unknown")
        success = result.get("success", False)
        status = "[OK]" if success else "[FAIL]"
        print(f"[DEV] {status} {agent_id}")
    
    return results


def spawn_specific_development_agent(
    workflow_id: str,
    agent_id: str,
    priority: int = 10
) -> Optional[Dict[str, Any]]:
    """
    Spawn a specific agent for development.
    
    Args:
        workflow_id: Workflow identifier
        agent_id: Specific agent ID to spawn
        priority: Priority level
        
    Returns:
        Spawn result or None
    """
    print(f"[DEV] Spawning specific agent: {agent_id}")
    print(f"[DEV] Priority: {priority}")
    print()
    
    spawner = AgentSpawner(workflow_id=workflow_id)
    
    # Determine agent type from agent_id
    if agent_id.startswith("intel_"):
        agent_type = "Intelligence"
        risk_level = "LOW"
    elif agent_id.startswith("draft_"):
        agent_type = "Drafting"
        risk_level = "MEDIUM"
    elif agent_id.startswith("execution_"):
        agent_type = "Execution"
        risk_level = "HIGH"
    else:
        agent_type = "Intelligence"
        risk_level = "LOW"
    
    result = spawner.spawn_agent(
        agent_id=agent_id,
        agent_type=agent_type,
        scope=f"Development - {agent_id}",
        risk_level=risk_level,
        metadata={
            "development_mode": True,
            "spawned_by": "dev__spawn_intelligence_agents.py",
            "priority": priority,
            "spawned_at": datetime.now(timezone.utc).isoformat()
        }
    )
    
    if result.get("success"):
        print(f"[DEV] [OK] Successfully spawned {agent_id}")
    else:
        print(f"[DEV] [FAIL] Failed to spawn {agent_id}: {result.get('error', 'Unknown error')}")
    
    return result


def main():
    """Main execution."""
    print("=" * 60)
    print("Development Agent Spawner - Intelligence Agents Only")
    print("=" * 60)
    print()
    
    try:
        # Load workflow state
        workflow_id = get_workflow_id()
        current_state = get_current_state()
        
        print(f"Current State: {current_state}")
        print(f"Workflow ID: {workflow_id}")
        print()
        
        # Spawn Intelligence agents for current state
        results = spawn_intelligence_agents_for_development(
            workflow_id=workflow_id,
            legislative_state=current_state,
            max_agents=2,  # Limit to 2 agents for development
            priority=10   # High priority for development
        )
        
        print()
        print("=" * 60)
        print("Development agent spawning complete")
        print("=" * 60)
        print()
        print("Note: These agents are spawned for development work only.")
        print("They are read-only Intelligence agents and will not modify")
        print("system state or trigger execution.")
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
