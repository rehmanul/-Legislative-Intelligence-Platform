"""
Script: dev__batch_execute.py
Intent:
- temporal

Reads:
- agent-orchestrator/state/legislative-state.json
- agent-orchestrator/registry/agent-registry.json

Writes:
- None (executes agents in batch, no file writes)

Schema:
- N/A (batch execution script)
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

# Path setup
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from app.agent_spawner import AgentSpawner
    from app.agent_executor import AgentExecutor
    from app.models import LegislativeState
except ImportError as e:
    print(f"[ERROR] Failed to import required modules: {e}")
    sys.exit(1)

# Constants
BASE_DIR = PROJECT_ROOT
STATE_PATH = BASE_DIR / "state" / "legislative-state.json"
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"


def load_workflow_state() -> Dict[str, Any]:
    """Load workflow state."""
    if not STATE_PATH.exists():
        raise FileNotFoundError(f"State file not found: {STATE_PATH}")
    with open(STATE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_intelligence_agents_for_state(legislative_state: str) -> List[str]:
    """
    Get list of Intelligence agent IDs for a given state.
    
    Args:
        legislative_state: Current legislative state
        
    Returns:
        List of Intelligence agent IDs
    """
    # Map of state to Intelligence agents
    agent_map = {
        "PRE_EVT": [
            "intel_signal_scan_pre_evt",
            "intel_stakeholder_map_pre_evt",
            "intel_opposition_detect_pre_evt",
            "intel_policy_context_analyzer_pre_evt"
        ],
        "INTRO_EVT": [
            "intel_signal_scan_intro_evt",
            "intel_stakeholder_map_intro_evt"
        ],
        "COMM_EVT": [
            "intel_signal_scan_comm_evt",
            "intel_stakeholder_map_comm_evt"
        ],
        "FLOOR_EVT": [
            "intel_signal_scan_floor_evt"
        ],
        "FINAL_EVT": [
            "intel_signal_scan_final_evt"
        ],
        "IMPL_EVT": [
            "intel_signal_scan_impl_evt"
        ]
    }
    
    return agent_map.get(legislative_state, [])


def batch_execute_development_agents(
    workflow_id: str,
    agent_ids: List[str],
    max_concurrent: int = 2,
    priority: int = 10
) -> Dict[str, Any]:
    """
    Execute multiple development agents in batch.
    
    Args:
        workflow_id: Workflow identifier
        agent_ids: List of agent IDs to execute
        max_concurrent: Maximum concurrent executions
        priority: Priority level for all agents
        
    Returns:
        Execution results
    """
    print(f"Batch executing {len(agent_ids)} development agents...")
    print("-" * 70)
    
    # Create executor
    executor = AgentExecutor(
        workflow_id=workflow_id,
        max_workers=max_concurrent
    )
    
    if not executor.is_running():
        executor.start()
    
    results = {
        "total": len(agent_ids),
        "queued": 0,
        "failed": 0,
        "agent_ids": []
    }
    
    for agent_id in agent_ids:
        try:
            # Determine agent type from ID
            if agent_id.startswith("intel_"):
                agent_type = "Intelligence"
                risk_level = "LOW"
            else:
                agent_type = "Intelligence"
                risk_level = "LOW"
            
            # Execute agent with high priority
            executor.execute_agent(
                agent_id=agent_id,
                workflow_id=workflow_id,
                agent_type=agent_type,
                scope=f"Development batch - {agent_id}",
                risk_level=risk_level,
                metadata={
                    "development_mode": True,
                    "batch_execution": True,
                    "priority": priority,
                    "spawned_at": datetime.now(timezone.utc).isoformat()
                }
            )
            
            results["queued"] += 1
            results["agent_ids"].append(agent_id)
            print(f"  [OK] Queued {agent_id}")
            
        except Exception as e:
            results["failed"] += 1
            print(f"  [FAIL] Failed to queue {agent_id}: {e}")
    
    print()
    print(f"Batch execution summary:")
    print(f"  Total: {results['total']}")
    print(f"  Queued: {results['queued']}")
    print(f"  Failed: {results['failed']}")
    print()
    
    return results


def main():
    """Main batch execution."""
    print("=" * 70)
    print("DEVELOPMENT BATCH EXECUTION")
    print("=" * 70)
    print()
    
    try:
        # Load state
        state = load_workflow_state()
        workflow_id = state.get("_meta", {}).get("workflow_id", "default-workflow")
        current_state = state.get("current_state", "PRE_EVT")
        
        print(f"Workflow ID: {workflow_id}")
        print(f"Current State: {current_state}")
        print()
        
        # Get Intelligence agents for current state
        agent_ids = get_intelligence_agents_for_state(current_state)
        
        if not agent_ids:
            print(f"[WARN] No Intelligence agents found for state: {current_state}")
            print("[INFO] Available states: PRE_EVT, INTRO_EVT, COMM_EVT, FLOOR_EVT, FINAL_EVT, IMPL_EVT")
            return 0
        
        print(f"Found {len(agent_ids)} Intelligence agents for {current_state}:")
        for agent_id in agent_ids:
            print(f"  - {agent_id}")
        print()
        
        # Batch execute
        results = batch_execute_development_agents(
            workflow_id=workflow_id,
            agent_ids=agent_ids,
            max_concurrent=2,  # Limit concurrent execution
            priority=10  # High priority for development
        )
        
        print("=" * 70)
        print("BATCH EXECUTION COMPLETE")
        print("=" * 70)
        print()
        print("Next steps:")
        print("  1. Monitor execution: python scripts\\dev__monitor_resource_usage.py")
        print("  2. Check agent status: registry\\agent-registry.json")
        print("  3. Review outputs: artifacts\\<agent_id>\\")
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
