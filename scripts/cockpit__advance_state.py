"""
Script: cockpit__advance_state.py
Intent:
- snapshot

Reads:
- state/legislative-state.json

Writes:
- Updates state/legislative-state.json (advances to next state)
- audit/audit-log.jsonl (logs state advancement)

Schema:
Command-line script that advances legislative state with external confirmation.
Input: next_state, external_confirmation (required), confirmed_by
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
STATE_PATH = BASE_DIR / "state" / "legislative-state.json"
AUDIT_LOG_PATH = BASE_DIR / "audit" / "audit-log.jsonl"

# State definitions
STATE_DEFINITIONS = {
    "PRE_EVT": "Policy Opportunity Detected",
    "INTRO_EVT": "Bill Vehicle Identified",
    "COMM_EVT": "Committee Referral",
    "FLOOR_EVT": "Floor Scheduled",
    "FINAL_EVT": "Vote Imminent",
    "IMPL_EVT": "Law Enacted",
}

# Valid state transitions
VALID_TRANSITIONS = {
    "PRE_EVT": ["INTRO_EVT"],
    "INTRO_EVT": ["COMM_EVT"],
    "COMM_EVT": ["FLOOR_EVT"],
    "FLOOR_EVT": ["FINAL_EVT"],
    "FINAL_EVT": ["IMPL_EVT"],
    "IMPL_EVT": [],  # Terminal state
}


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


def validate_state_transition(current_state: str, next_state: str) -> tuple[bool, Optional[str]]:
    """Validate that state transition is allowed."""
    if current_state not in VALID_TRANSITIONS:
        return False, f"Unknown current state: {current_state}"
    
    allowed_next = VALID_TRANSITIONS[current_state]
    if not allowed_next:
        return False, f"Current state {current_state} is terminal (no next states allowed)"
    
    if next_state not in allowed_next:
        return False, f"Invalid transition: {current_state} -> {next_state}. Allowed: {', '.join(allowed_next)}"
    
    return True, None


def check_state_requirements(state_data: Dict[str, Any], review_gates: Dict[str, Dict[str, Any]]) -> tuple[bool, list[str]]:
    """Check if state advancement requirements are met."""
    current_state = state_data.get("current_state", "UNKNOWN")
    advancement_rule = state_data.get("state_advancement_rule", "")
    
    blocking_reasons = []
    
    # Check for required approvals based on current state
    if current_state == "INTRO_EVT":
        # Need HR_PRE approval for INTRO artifacts
        from pathlib import Path
        REVIEW_DIR = BASE_DIR / "review"
        hr_pre_file = REVIEW_DIR / "HR_PRE_queue.json"
        if hr_pre_file.exists():
            hr_pre_data = load_json(hr_pre_file)
            pending = hr_pre_data.get("pending_reviews", [])
            if pending:
                blocking_reasons.append(f"HR_PRE approval pending ({len(pending)} items)")
            else:
                # Check if there's at least one approved review
                history = hr_pre_data.get("review_history", [])
                has_approved = any(r.get("decision") == "APPROVED" for r in history)
                if not has_approved:
                    blocking_reasons.append("HR_PRE approval required (no approved reviews)")
    
    # Check for external confirmation requirement
    if "external confirmation" in advancement_rule.lower():
        # External confirmation must be provided via command line
        pass  # Will be checked in main()
    
    return len(blocking_reasons) == 0, blocking_reasons


def advance_state(
    next_state: str,
    external_confirmation: str,
    confirmed_by: str = "operator",
    source_reference: Optional[str] = None
) -> bool:
    """
    Advance legislative state.
    
    Args:
        next_state: Target state to advance to
        external_confirmation: Description of external event that occurred
        confirmed_by: User identifier
        source_reference: Optional reference to external source
        
    Returns:
        True if successful
    """
    # Load current state
    if not STATE_PATH.exists():
        print(f"[ERROR] State file not found: {STATE_PATH}")
        return False
    
    state_data = load_json(STATE_PATH)
    current_state = state_data.get("current_state", "UNKNOWN")
    
    # Validate transition
    is_valid, error_msg = validate_state_transition(current_state, next_state)
    if not is_valid:
        print(f"[ERROR] {error_msg}")
        return False
    
    # Check requirements (basic check - full validation should be done via API)
    # Load review gates for requirement checking
    review_gates = {}
    REVIEW_DIR = BASE_DIR / "review"
    if REVIEW_DIR.exists():
        for queue_file in REVIEW_DIR.glob("HR_*_queue.json"):
            gate_data = load_json(queue_file)
            gate_id = gate_data.get("_meta", {}).get("review_gate", "UNKNOWN")
            review_gates[gate_id] = gate_data
    
    requirements_met, blocking_reasons = check_state_requirements(state_data, review_gates)
    if not requirements_met:
        print(f"[WARNING] Requirements not fully met:")
        for reason in blocking_reasons:
            print(f"  - {reason}")
        print(f"[WARNING] Proceeding anyway (override mode)")
        confirm = input("Type 'ADVANCE' to confirm override: ")
        if confirm != "ADVANCE":
            print("[CANCELLED] State advancement cancelled")
            return False
    
    # Require external confirmation
    if not external_confirmation:
        print("[ERROR] External confirmation is required for state advancement")
        print("Please provide a description of the external event that occurred.")
        return False
    
    # Confirm irreversible action
    print(f"[WARNING] State advancement is IRREVERSIBLE")
    print(f"  Current: {current_state} ({STATE_DEFINITIONS.get(current_state, current_state)})")
    print(f"  Next:    {next_state} ({STATE_DEFINITIONS.get(next_state, next_state)})")
    print(f"  External confirmation: {external_confirmation}")
    confirm = input("Type 'CONFIRM' to proceed: ")
    if confirm != "CONFIRM":
        print("[CANCELLED] State advancement cancelled")
        return False
    
    # Update state
    state_history = state_data.get("state_history", [])
    state_history.append({
        "state": next_state,
        "entered_at": datetime.now(timezone.utc).isoformat() + "Z",
        "entered_by": confirmed_by,
        "reason": f"State advanced with external confirmation: {external_confirmation}",
        "external_confirmation": external_confirmation,
        "source_reference": source_reference
    })
    
    state_data["current_state"] = next_state
    state_data["state_definition"] = STATE_DEFINITIONS.get(next_state, next_state)
    state_data["state_history"] = state_history
    state_data["_meta"]["last_updated"] = datetime.now(timezone.utc).isoformat() + "Z"
    
    # Update next allowed states
    state_data["next_allowed_states"] = VALID_TRANSITIONS.get(next_state, [])
    
    # Update advancement rule (would need to be determined from invariants)
    # For now, keep existing rule or set placeholder
    if "state_advancement_rule" not in state_data:
        state_data["state_advancement_rule"] = "Check requirements"
    
    # Save updated state
    save_json(STATE_PATH, state_data)
    
    # Log to audit trail
    log_audit_event(
        "state_advanced",
        f"Legislative state advanced from {current_state} to {next_state}",
        previous_state=current_state,
        new_state=next_state,
        advanced_by=confirmed_by,
        external_confirmation=external_confirmation,
        source_reference=source_reference
    )
    
    print(f"[OK] State advanced successfully")
    print(f"   Previous: {current_state} ({STATE_DEFINITIONS.get(current_state, current_state)})")
    print(f"   New:      {next_state} ({STATE_DEFINITIONS.get(next_state, next_state)})")
    print(f"   External confirmation: {external_confirmation}")
    
    return True


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description="Advance legislative state (IRREVERSIBLE)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Advance from INTRO_EVT to COMM_EVT with external confirmation
  python cockpit__advance_state.py COMM_EVT "Committee referral confirmed via congress.gov" --source "congress.gov/bill/123"
  
  # Advance with reference
  python cockpit__advance_state.py COMM_EVT "Bill HR-1234 referred to Energy & Commerce" --source "HR-1234" --confirmed-by "operator"
        """
    )
    
    parser.add_argument("next_state", choices=list(STATE_DEFINITIONS.keys()), help="Target state to advance to")
    parser.add_argument("external_confirmation", help="Description of external event that occurred (REQUIRED)")
    parser.add_argument("--source", "-s", help="Optional source reference (e.g., congress.gov URL)")
    parser.add_argument("--confirmed-by", "-u", default="operator", help="User identifier (default: operator)")
    
    args = parser.parse_args()
    
    print(f"[cockpit__advance_state] Advancing state to {args.next_state}...")
    
    success = advance_state(
        next_state=args.next_state,
        external_confirmation=args.external_confirmation,
        confirmed_by=args.confirmed_by,
        source_reference=args.source
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
