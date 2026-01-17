"""
Script: cockpit__authorize_execution.py
Intent:
- snapshot

Reads:
- registry/agent-registry.json

Writes:
- Updates registry/agent-registry.json (changes agent status from BLOCKED)
- audit/audit-log.jsonl (logs execution authorization)

Schema:
Command-line script that authorizes execution agents to proceed.
Input: agent_id, action_type (optional), authorized_by
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional

# Path setup
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

# Constants
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
AUDIT_LOG_PATH = BASE_DIR / "audit" / "audit-log.jsonl"
GUIDANCE_PATH = BASE_DIR / "guidance" / "PROFESSIONAL_GUIDANCE.json"


def load_json(path: Path) -> Dict[str, Any]:
    """Load JSON file, return {} if not found or invalid."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_json(path: Path, data: Dict[str, Any]) -> None:
    """Save JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def log_audit_event(event_type: str, message: str, **kwargs) -> None:
    """Log event to audit log."""
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "event_type": event_type,
        "message": message,
        **kwargs
    }
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


def check_guidance_signed() -> bool:
    """Check if GUIDANCE artifact is signed."""
    if not GUIDANCE_PATH.exists():
        return False
    
    try:
        guidance = load_json(GUIDANCE_PATH)
        signatures = guidance.get("_meta", {}).get("signatures", {})
        
        for role, sig_data in signatures.items():
            if sig_data.get("signed", False):
                return True
        
        return False
    except Exception:
        return False


def authorize_execution(
    agent_id: str,
    action_type: Optional[str] = None,
    authorized_by: str = "operator"
) -> bool:
    """
    Authorize execution agent to proceed.
    
    Args:
        agent_id: Agent identifier
        action_type: Optional action type description
        authorized_by: User identifier
        
    Returns:
        True if successful
    """
    # Load registry
    if not REGISTRY_PATH.exists():
        print(f"[ERROR] Registry file not found: {REGISTRY_PATH}")
        return False
    
    registry_data = load_json(REGISTRY_PATH)
    agents = registry_data.get("agents", [])
    
    # Find the agent
    agent = None
    agent_index = None
    for idx, a in enumerate(agents):
        if a.get("agent_id") == agent_id:
            agent = a
            agent_index = idx
            break
    
    if not agent:
        print(f"[ERROR] Agent not found: {agent_id}")
        print(f"Available agents:")
        for a in agents:
            if a.get("agent_type") == "Execution":
                print(f"  - {a.get('agent_id')} (status: {a.get('status')})")
        return False
    
    # Validate agent type
    agent_type = agent.get("agent_type", "")
    if agent_type != "Execution":
        print(f"[ERROR] Agent {agent_id} is not an Execution agent (type: {agent_type})")
        return False
    
    # Validate agent status
    agent_status = agent.get("status", "")
    if agent_status != "BLOCKED":
        print(f"[ERROR] Agent {agent_id} is not BLOCKED (current status: {agent_status})")
        print(f"Only BLOCKED execution agents can be authorized.")
        return False
    
    # Check guidance
    guidance_signed = check_guidance_signed()
    if not guidance_signed:
        print(f"[WARNING] GUIDANCE artifact not signed")
        print(f"Execution authorization requires signed GUIDANCE.")
        confirm = input("Type 'AUTHORIZE_ANYWAY' to proceed without guidance: ")
        if confirm != "AUTHORIZE_ANYWAY":
            print("[CANCELLED] Authorization cancelled (guidance required)")
            return False
    
    # Check risk level
    risk_level = agent.get("risk_level", "").upper()
    if "HIGH" in risk_level:
        print(f"[WARNING] HIGH risk execution agent")
        print(f"  Agent: {agent_id}")
        print(f"  Task: {agent.get('current_task', 'Unknown')}")
        print(f"  Risk: {risk_level}")
        confirm = input("Type 'AUTHORIZE_HIGH_RISK' to confirm: ")
        if confirm != "AUTHORIZE_HIGH_RISK":
            print("[CANCELLED] Authorization cancelled by user")
            return False
    
    # Update agent status
    agents[agent_index]["status"] = "RUNNING"
    agents[agent_index]["authorized_at"] = datetime.now(timezone.utc).isoformat() + "Z"
    agents[agent_index]["authorized_by"] = authorized_by
    if action_type:
        agents[agent_index]["authorized_action_type"] = action_type
    
    # Update registry metadata
    registry_data["_meta"]["last_updated"] = datetime.now(timezone.utc).isoformat() + "Z"
    
    # Recalculate blocked count
    blocked_count = sum(1 for a in agents if a.get("status") == "BLOCKED")
    registry_data["_meta"]["blocked_agents"] = blocked_count
    
    # Save updated registry
    save_json(REGISTRY_PATH, registry_data)
    
    # Log to audit trail
    log_audit_event(
        "execution_authorized",
        f"Execution agent {agent_id} authorized",
        agent_id=agent_id,
        agent_type=agent_type,
        action_type=action_type,
        authorized_by=authorized_by,
        risk_level=risk_level,
        guidance_signed=guidance_signed
    )
    
    print(f"[OK] Execution agent authorized successfully")
    print(f"   Agent: {agent_id}")
    print(f"   Status: BLOCKED -> RUNNING")
    print(f"   Risk: {risk_level}")
    if action_type:
        print(f"   Action: {action_type}")
    print(f"[NOTE] Authorization is partially reversible (can pause, cannot undo sent communications)")
    
    return True


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description="Authorize execution agents to proceed",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Authorize an execution agent
  python cockpit__authorize_execution.py execution_outreach_comm_evt
  
  # Authorize with action type
  python cockpit__authorize_execution.py execution_outreach_comm_evt --action "Outreach to Energy & Commerce"
  
  # Authorize with user identifier
  python cockpit__authorize_execution.py execution_outreach_comm_evt --authorized-by "operator:john.doe"
        """
    )
    
    parser.add_argument("agent_id", help="Execution agent identifier")
    parser.add_argument("--action", "-a", help="Optional action type description")
    parser.add_argument("--authorized-by", "-u", default="operator", help="User identifier (default: operator)")
    
    args = parser.parse_args()
    
    print(f"[cockpit__authorize_execution] Authorizing execution agent {args.agent_id}...")
    
    success = authorize_execution(
        agent_id=args.agent_id,
        action_type=args.action,
        authorized_by=args.authorized_by
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
