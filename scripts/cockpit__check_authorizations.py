"""
Script: cockpit__check_authorizations.py
Intent: snapshot

Reads:
- registry/agent-registry.json
- config/authorization_policy.json

Writes:
- Updates registry/agent-registry.json (auto-approves eligible agents)
- audit/audit-log.jsonl (logs auto-approval decisions)

Schema:
Background script that checks blocked agents and applies auto-approval rules.
Can be run periodically (e.g., every 5 minutes) to auto-approve eligible agents.
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

# Path setup
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

# Import authorization engine
try:
    from execution.authorization_engine import (
        get_authorization_engine,
        AuthorizationDecision
    )
except ImportError:
    print("[ERROR] Failed to import authorization_engine. Is execution/authorization_engine.py present?")
    sys.exit(1)

# Constants
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
AUDIT_LOG_PATH = BASE_DIR / "audit" / "audit-log.jsonl"


def load_json(path: Path) -> Dict[str, Any]:
    """Load JSON file, return {} if not found."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_json(path: Path, data: Dict[str, Any]) -> None:
    """Save JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
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


def parse_blocked_at(agent: Dict[str, Any]) -> Optional[datetime]:
    """Parse blocked_at timestamp from agent metadata."""
    auth_meta = agent.get("authorization_metadata", {})
    blocked_at_str = auth_meta.get("blocked_at") or agent.get("blocked_at")
    
    if not blocked_at_str:
        return None
    
    try:
        # Parse ISO-8601 timestamp
        if blocked_at_str.endswith("Z"):
            blocked_at_str = blocked_at_str[:-1] + "+00:00"
        return datetime.fromisoformat(blocked_at_str)
    except Exception:
        return None


def check_blocked_agents(
    dry_run: bool = False,
    auto_approve: bool = True
) -> Dict[str, Any]:
    """
    Check all blocked agents and apply authorization rules.
    
    Args:
        dry_run: If True, don't modify registry, only report
        auto_approve: If True, auto-approve eligible agents
        
    Returns:
        Summary of actions taken
    """
    # Load registry
    if not REGISTRY_PATH.exists():
        print(f"[ERROR] Registry file not found: {REGISTRY_PATH}")
        return {"error": "registry_not_found"}
    
    registry_data = load_json(REGISTRY_PATH)
    agents = registry_data.get("agents", [])
    
    # Find blocked execution agents
    blocked_agents = [
        agent for agent in agents
        if agent.get("status") == "BLOCKED" and agent.get("agent_type") == "Execution"
    ]
    
    if not blocked_agents:
        print("[INFO] No blocked execution agents found")
        return {
            "checked": 0,
            "auto_approved": 0,
            "escalated": 0,
            "requires_manual": 0
        }
    
    print(f"[INFO] Found {len(blocked_agents)} blocked execution agent(s)")
    
    # Initialize authorization engine
    engine = get_authorization_engine()
    
    summary = {
        "checked": len(blocked_agents),
        "auto_approved": 0,
        "escalated": 0,
        "requires_manual": 0,
        "decisions": []
    }
    
    # Process each blocked agent
    for agent in blocked_agents:
        agent_id = agent.get("agent_id")
        print(f"\n[CHECK] Processing agent: {agent_id}")
        
        # Get agent metadata
        auth_meta = agent.get("authorization_metadata", {})
        blocked_at = parse_blocked_at(agent)
        
        if not blocked_at:
            # Set blocked_at to now if missing (conservative)
            blocked_at = datetime.now(timezone.utc)
            print(f"  [WARN] Missing blocked_at timestamp, using current time")
        
        # Classify authorization
        decision = engine.classify_authorization(
            agent_id=agent_id,
            agent_metadata=agent,
            blocked_at=blocked_at
        )
        
        decision_type = decision.get("decision")
        action = decision.get("action")
        
        print(f"  [DECISION] {decision_type.value}: {decision.get('reason')}")
        print(f"  [ACTION] {action}")
        
        summary["decisions"].append({
            "agent_id": agent_id,
            "decision": decision_type.value,
            "action": action,
            "reason": decision.get("reason")
        })
        
        # Apply decision
        if action == "APPROVE_IMMEDIATELY" or (action == "AUTO_APPROVE" and auto_approve):
            if not dry_run:
                # Auto-approve agent
                agent["status"] = "RUNNING"
                agent["authorized_at"] = datetime.now(timezone.utc).isoformat() + "Z"
                agent["authorized_by"] = f"system:auto_approval_{decision.get('reason')}"
                agent["authorization_metadata"]["auto_approved"] = True
                agent["authorization_metadata"]["auto_approval_reason"] = decision.get("reason")
                
                # Log decision
                engine.log_authorization_decision(
                    agent_id=agent_id,
                    decision=decision_type,
                    reason=decision.get("reason"),
                    metadata=decision.get("metadata", {}),
                    authorized_by=agent["authorized_by"]
                )
                
                print(f"  [AUTO-APPROVED] Agent {agent_id} authorized automatically")
                summary["auto_approved"] += 1
            else:
                print(f"  [DRY-RUN] Would auto-approve agent {agent_id}")
                summary["auto_approved"] += 1
        
        elif action == "ALERT_OPERATOR" or action == "WARN":
            print(f"  [ESCALATION] Agent {agent_id} requires operator attention")
            summary["escalated"] += 1
            
            # Log escalation
            log_audit_event(
                "authorization_escalation",
                f"Agent {agent_id} escalated for operator review",
                agent_id=agent_id,
                priority=decision.get("priority"),
                minutes_blocked=decision.get("minutes_blocked"),
                reason=decision.get("reason")
            )
        
        elif action == "REQUIRE_MANUAL_REVIEW":
            print(f"  [MANUAL] Agent {agent_id} requires manual review")
            summary["requires_manual"] += 1
    
    # Save updated registry
    if not dry_run and summary["auto_approved"] > 0:
        # Recalculate blocked count
        blocked_count = sum(1 for a in agents if a.get("status") == "BLOCKED")
        registry_data["_meta"]["blocked_agents"] = blocked_count
        registry_data["_meta"]["last_updated"] = datetime.now(timezone.utc).isoformat() + "Z"
        
        save_json(REGISTRY_PATH, registry_data)
        print(f"\n[SUCCESS] Updated registry: {summary['auto_approved']} agent(s) auto-approved")
    
    return summary


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description="Check blocked agents and apply auto-approval rules",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check and auto-approve eligible agents
  python cockpit__check_authorizations.py
  
  # Dry-run (report only, no changes)
  python cockpit__check_authorizations.py --dry-run
  
  # Check only, don't auto-approve
  python cockpit__check_authorizations.py --no-auto-approve
        """
    )
    
    parser.add_argument("--dry-run", action="store_true", help="Dry-run mode (report only, no changes)")
    parser.add_argument("--no-auto-approve", action="store_true", help="Check only, don't auto-approve")
    
    args = parser.parse_args()
    
    print(f"[cockpit__check_authorizations] Checking blocked agents...")
    if args.dry_run:
        print("[DRY-RUN] Mode: reporting only, no changes will be made")
    
    summary = check_blocked_agents(
        dry_run=args.dry_run,
        auto_approve=not args.no_auto_approve
    )
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Checked: {summary.get('checked', 0)} agent(s)")
    print(f"Auto-approved: {summary.get('auto_approved', 0)} agent(s)")
    print(f"Escalated: {summary.get('escalated', 0)} agent(s)")
    print(f"Requires manual: {summary.get('requires_manual', 0)} agent(s)")
    print("="*60)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
