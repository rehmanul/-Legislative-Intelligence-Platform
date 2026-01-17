"""
Script: check_comm_evt_readiness.py
Intent: aggregate (read-only validation)
Purpose: Check if system is ready to advance from INTRO_EVT to COMM_EVT

Reads:
- state/legislative-state.json
- review/HR_PRE_queue.json
- artifacts/intro_evt/INTRO_EVT_READINESS.json

Writes:
- None (read-only validation, outputs to stdout)

Schema: N/A (validation script)
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Tuple

BASE_DIR = Path(__file__).parent.parent

def load_state() -> Dict[str, Any]:
    """Load legislative state"""
    state_path = BASE_DIR / "state" / "legislative-state.json"
    if not state_path.exists():
        return {}
    return json.loads(state_path.read_text())

def load_hr_pre_queue() -> Dict[str, Any]:
    """Load HR_PRE review queue"""
    queue_path = BASE_DIR / "review" / "HR_PRE_queue.json"
    if not queue_path.exists():
        return {}
    return json.loads(queue_path.read_text())

def check_artifact_approvals(hr_pre_queue: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
    """Check if required artifacts are approved"""
    required_artifacts = ["INTRO_FRAME", "INTRO_WHITEPAPER"]
    approved = []
    missing = []
    
    review_history = hr_pre_queue.get("review_history", [])
    
    for artifact_type in required_artifacts:
        found_approved = False
        for review in review_history:
            if review.get("artifact_type") == artifact_type and review.get("decision") == "APPROVED":
                approved.append(f"{artifact_type} (approved by {review.get('decision_by', 'unknown')} at {review.get('decision_at', 'unknown')})")
                found_approved = True
                break
        
        if not found_approved:
            missing.append(f"{artifact_type} (not approved)")
    
    all_approved = len(missing) == 0
    return all_approved, approved, missing

def check_external_event(state_data: Dict[str, Any]) -> Tuple[bool, str]:
    """Check if external event is confirmed"""
    advancement_rule = state_data.get("state_advancement_rule", "")
    
    if "committee_referral" in advancement_rule.lower():
        # Check if there's any external event confirmation in state history
        state_history = state_data.get("state_history", [])
        for entry in state_history:
            if entry.get("reason", "").lower().startswith("external"):
                return True, "External event confirmed in state history"
        
        return False, "External confirmation required: committee_referral"
    
    return True, "No external event required"

def check_readiness() -> Dict[str, Any]:
    """Check overall readiness for COMM_EVT"""
    state_data = load_state()
    hr_pre_queue = load_hr_pre_queue()
    
    current_state = state_data.get("current_state", "UNKNOWN")
    next_states = state_data.get("next_allowed_states", [])
    
    result = {
        "_meta": {
            "check_timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "current_state": current_state,
            "target_state": "COMM_EVT"
        },
        "state_check": {
            "current_state": current_state,
            "can_advance": current_state == "INTRO_EVT" and "COMM_EVT" in next_states,
            "next_allowed_states": next_states
        },
        "artifact_approvals": {},
        "external_event": {},
        "readiness_summary": {
            "ready": False,
            "blocking_issues": [],
            "satisfied_requirements": []
        }
    }
    
    # Check artifact approvals
    artifacts_approved, approved_list, missing_list = check_artifact_approvals(hr_pre_queue)
    result["artifact_approvals"] = {
        "all_approved": artifacts_approved,
        "approved": approved_list,
        "missing": missing_list
    }
    
    # Check external event
    event_confirmed, event_status = check_external_event(state_data)
    result["external_event"] = {
        "confirmed": event_confirmed,
        "status": event_status
    }
    
    # Overall readiness
    blocking_issues = []
    satisfied_requirements = []
    
    if not result["state_check"]["can_advance"]:
        blocking_issues.append(f"Current state is {current_state}, not INTRO_EVT")
    
    if not artifacts_approved:
        blocking_issues.extend(missing_list)
    else:
        satisfied_requirements.extend(approved_list)
    
    if not event_confirmed:
        blocking_issues.append(event_status)
    else:
        satisfied_requirements.append("External event confirmed")
    
    result["readiness_summary"] = {
        "ready": result["state_check"]["can_advance"] and artifacts_approved and event_confirmed,
        "blocking_issues": blocking_issues,
        "satisfied_requirements": satisfied_requirements
    }
    
    return result

def print_summary(result: Dict[str, Any]):
    """Print human-readable summary"""
    print("=" * 70)
    print("COMM_EVT READINESS CHECK")
    print("=" * 70)
    print(f"Current State: {result['state_check']['current_state']}")
    print(f"Target State: COMM_EVT")
    print()
    
    # Artifact approvals
    print("Artifact Approvals:")
    if result["artifact_approvals"]["all_approved"]:
        print("  [OK] All required artifacts approved")
        for approved in result["artifact_approvals"]["approved"]:
            print(f"    - {approved}")
    else:
        print("  [MISSING] Missing approvals:")
        for missing in result["artifact_approvals"]["missing"]:
            print(f"    - {missing}")
    print()
    
    # External event
    print("External Event:")
    if result["external_event"]["confirmed"]:
        print(f"  [OK] {result['external_event']['status']}")
    else:
        print(f"  [PENDING] {result['external_event']['status']}")
    print()
    
    # Overall readiness
    print("=" * 70)
    if result["readiness_summary"]["ready"]:
        print("[READY] READY TO ADVANCE TO COMM_EVT")
    else:
        print("[BLOCKED] NOT READY - Blocking Issues:")
        for issue in result["readiness_summary"]["blocking_issues"]:
            print(f"  - {issue}")
    
    if result["readiness_summary"]["satisfied_requirements"]:
        print()
        print("Satisfied Requirements:")
        for req in result["readiness_summary"]["satisfied_requirements"]:
            print(f"  [OK] {req}")
    
    print("=" * 70)

if __name__ == "__main__":
    result = check_readiness()
    print_summary(result)
    
    # Also output JSON for programmatic use
    print()
    print("JSON Output:")
    print(json.dumps(result, indent=2))
