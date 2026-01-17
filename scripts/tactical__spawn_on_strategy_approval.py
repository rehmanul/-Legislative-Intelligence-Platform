"""
Script: tactical__spawn_on_strategy_approval.py
Intent:
- aggregate

Reads:
- Strategy artifact JSON (e.g., RISK_ASSESSMENT.json)
- Agent registry (registry/agent-registry.json)

Writes:
- Spawns tactical agents
- Updates agent registry with spawned agents
- Logs to audit trail

Schema:
Spawns tactical agents after strategy artifact approval.
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

# Path setup
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.agent_spawner import AgentSpawner

# Constants
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
AUDIT_LOG_PATH = BASE_DIR / "audit" / "audit-log.jsonl"

# Strategy artifact types that trigger tactical spawning
STRATEGY_ARTIFACT_TYPES = {
    "RISK_ASSESSMENT": "Strategy - Risk Assessment",
    "PRE_CONCEPT": "Strategy - Concept Memo",
    "INTRO_FRAMING": "Strategy - Policy Framing",
    "COMM_LANGUAGE": "Strategy - Legislative Language"
}

# Tactical agent mapping: strategy type → list of tactical agent IDs
TACTICAL_AGENT_MAP = {
    "RISK_ASSESSMENT": [
        {
            "agent_id": "draft_talking_points_comm_evt",
            "agent_type": "Drafting",
            "priority": 1,
            "description": "Generate talking points from risk assessment"
        },
        {
            "agent_id": "draft_messaging_framework_comm_evt",
            "agent_type": "Drafting",
            "priority": 1,
            "description": "Create unified messaging framework"
        },
        {
            "agent_id": "draft_outreach_plan_comm_evt",
            "agent_type": "Drafting",
            "priority": 1,
            "description": "Generate structured outreach plan"
        },
        {
            "agent_id": "draft_counter_strategy_comm_evt",
            "agent_type": "Drafting",
            "priority": 2,
            "description": "Develop counter-strategy for opposition"
        },
        {
            "agent_id": "execution_coalition_activation_comm_evt",
            "agent_type": "Execution",
            "priority": 2,
            "description": "Create coalition activation plan"
        },
        {
            "agent_id": "draft_staff_briefing_comm_evt",
            "agent_type": "Drafting",
            "priority": 2,
            "description": "Generate committee staff briefing materials"
        }
    ],
    "PRE_CONCEPT": [
        {
            "agent_id": "draft_framing_intro_evt",
            "agent_type": "Drafting",
            "priority": 1,
            "description": "Develop policy framing"
        },
        {
            "agent_id": "draft_stakeholder_engagement_plan_intro_evt",
            "agent_type": "Drafting",
            "priority": 1,
            "description": "Create stakeholder engagement plan"
        }
    ],
    # Add more mappings as needed
}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


def log_audit_event(event_type: str, message: str, **kwargs):
    """Log event to audit trail."""
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "event_type": event_type,
        "message": message,
        **kwargs
    }
    with open(AUDIT_LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(event) + '\n')


def is_strategy_artifact(artifact_data: Dict[str, Any]) -> bool:
    """Check if artifact is a strategy artifact that should trigger tactical spawning."""
    artifact_type = artifact_data.get("_meta", {}).get("artifact_type", "")
    return artifact_type in STRATEGY_ARTIFACT_TYPES


def get_tactical_agents_for_strategy(strategy_artifact_type: str) -> List[Dict[str, Any]]:
    """Get list of tactical agents to spawn for a strategy artifact type."""
    return TACTICAL_AGENT_MAP.get(strategy_artifact_type, [])


def spawn_tactical_agents_for_strategy(
    strategy_artifact_type: str,
    strategy_artifact_data: Dict[str, Any],
    workflow_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Spawn tactical agents after strategy approval.
    
    Args:
        strategy_artifact_type: Type of strategy artifact (e.g., "RISK_ASSESSMENT")
        strategy_artifact_data: Full strategy artifact data
        workflow_id: Optional workflow ID
        
    Returns:
        List of spawn results
    """
    tactical_agents = get_tactical_agents_for_strategy(strategy_artifact_type)
    
    if not tactical_agents:
        logger.warning(f"No tactical agents mapped for strategy type: {strategy_artifact_type}")
        return []
    
    # Get workflow ID from artifact or use default
    if not workflow_id:
        workflow_id = strategy_artifact_data.get("_meta", {}).get("workflow_id", "default")
    
    # Get artifact path
    artifact_path = strategy_artifact_data.get("_meta", {}).get("artifact_path", "")
    if not artifact_path:
        # Try to infer from artifact type
        agent_id = strategy_artifact_data.get("_meta", {}).get("agent_id", "")
        artifact_type = strategy_artifact_data.get("_meta", {}).get("artifact_type", "")
        if agent_id and artifact_type:
            artifact_path = f"artifacts/{agent_id}/{artifact_type}.json"
    
    logger.info(
        f"Spawning {len(tactical_agents)} tactical agents for strategy: {strategy_artifact_type}"
    )
    
    spawner = AgentSpawner(workflow_id=workflow_id)
    results = []
    
    # Spawn agents by priority (Tier 1 first, then Tier 2)
    tier1_agents = [a for a in tactical_agents if a.get("priority") == 1]
    tier2_agents = [a for a in tactical_agents if a.get("priority") == 2]
    
    for agent_config in tier1_agents + tier2_agents:
        agent_id = agent_config.get("agent_id")
        agent_type = agent_config.get("agent_type", "Drafting")
        description = agent_config.get("description", "")
        
        try:
            logger.info(f"Spawning tactical agent: {agent_id}")
            
            result = spawner.spawn_agent(
                agent_id=agent_id,
                agent_type=agent_type,
                scope=f"{description} (supporting {strategy_artifact_type})",
                risk_level="MEDIUM",
                metadata={
                    "triggered_by": "strategy_approval",
                    "strategy_artifact_type": strategy_artifact_type,
                    "strategy_artifact_path": artifact_path,
                    "strategy_approved_at": strategy_artifact_data.get("_meta", {}).get("approved_at", ""),
                    "tactical_category": infer_tactical_category(agent_id)
                }
            )
            
            results.append({
                "agent_id": agent_id,
                "success": result.get("success", False),
                "result": result,
                "description": description
            })
            
            log_audit_event(
                "tactical_agent_spawned",
                f"Spawned tactical agent {agent_id} for strategy {strategy_artifact_type}",
                agent_id=agent_id,
                strategy_artifact_type=strategy_artifact_type,
                strategy_artifact_path=artifact_path,
                success=result.get("success", False)
            )
            
        except Exception as e:
            logger.error(f"Failed to spawn tactical agent {agent_id}: {e}", exc_info=True)
            results.append({
                "agent_id": agent_id,
                "success": False,
                "error": str(e),
                "description": description
            })
            
            log_audit_event(
                "tactical_agent_spawn_failed",
                f"Failed to spawn tactical agent {agent_id}: {e}",
                agent_id=agent_id,
                strategy_artifact_type=strategy_artifact_type,
                error=str(e)
            )
    
    successful = sum(1 for r in results if r.get("success"))
    logger.info(
        f"Spawned {successful}/{len(results)} tactical agents successfully for {strategy_artifact_type}"
    )
    
    return results


def infer_tactical_category(agent_id: str) -> str:
    """Infer tactical category from agent ID."""
    if "talking_points" in agent_id or "messaging" in agent_id:
        return "messaging"
    elif "outreach" in agent_id:
        return "outreach"
    elif "counter" in agent_id or "prebuttal" in agent_id:
        return "counter-strategy"
    elif "coalition" in agent_id:
        return "coalition"
    elif "briefing" in agent_id or "staff" in agent_id:
        return "briefing"
    else:
        return "tactical"


def main():
    """Main function for testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Spawn tactical agents for approved strategy")
    parser.add_argument("strategy_artifact_path", help="Path to strategy artifact JSON")
    parser.add_argument("--workflow-id", help="Workflow ID (optional)")
    
    args = parser.parse_args()
    
    # Load strategy artifact
    artifact_path = Path(args.strategy_artifact_path)
    if not artifact_path.exists():
        print(f"[ERROR] Strategy artifact not found: {artifact_path}")
        sys.exit(1)
    
    with open(artifact_path, 'r', encoding='utf-8') as f:
        strategy_data = json.load(f)
    
    # Check if it's a strategy artifact
    if not is_strategy_artifact(strategy_data):
        print(f"[ERROR] Not a strategy artifact: {artifact_path}")
        sys.exit(1)
    
    # Check if approved
    meta = strategy_data.get("_meta", {})
    status = meta.get("status", "SPECULATIVE")
    review_gate_status = meta.get("review_gate_status", "")
    
    if status != "ACTIONABLE" or review_gate_status != "APPROVED":
        print(f"[WARNING] Strategy artifact not approved (status: {status}, review_gate_status: {review_gate_status})")
        print("Tactical agents will still spawn, but strategy may not be actionable.")
        confirm = input("Continue? (y/n): ")
        if confirm.lower() != 'y':
            sys.exit(0)
    
    # Get strategy type
    strategy_type = meta.get("artifact_type", "")
    
    # Spawn tactical agents
    results = spawn_tactical_agents_for_strategy(
        strategy_artifact_type=strategy_type,
        strategy_artifact_data=strategy_data,
        workflow_id=args.workflow_id
    )
    
    # Print results
    print(f"\n[RESULTS] Spawned {len(results)} tactical agents:")
    for result in results:
        status_icon = "✅" if result.get("success") else "❌"
        print(f"  {status_icon} {result.get('agent_id')}: {result.get('description', '')}")
        if not result.get("success"):
            print(f"     Error: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()
