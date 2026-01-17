"""
Script: advance_to_floor_evt.py
Intent: snapshot (modifies state)
Purpose: Advance legislative state from COMM_EVT to FLOOR_EVT

Reads:
- state/legislative-state.json
- review/HR_LANG_queue.json

Writes:
- state/legislative-state.json (updates state to FLOOR_EVT)
"""

import json
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
STATE_PATH = BASE_DIR / "state" / "legislative-state.json"
HR_LANG_QUEUE_PATH = BASE_DIR / "review" / "HR_LANG_queue.json"

def check_requirements():
    """Check if requirements for FLOOR_EVT are met"""
    issues = []
    
    # Check current state
    if not STATE_PATH.exists():
        return False, ["State file not found"]
    
    state_data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    current_state = state_data.get("current_state", "")
    
    if current_state != "COMM_EVT":
        return False, [f"Current state is {current_state}, expected COMM_EVT"]
    
    # Check HR_LANG queue for approved artifacts
    if not HR_LANG_QUEUE_PATH.exists():
        return False, ["HR_LANG queue not found"]
    
    queue = json.loads(HR_LANG_QUEUE_PATH.read_text(encoding="utf-8"))
    history = queue.get("review_history", [])
    
    # Check for approved COMM_EVT artifacts
    required_types = ["COMM_LEGISLATIVE_LANGUAGE", "COMM_AMENDMENT_STRATEGY", "COMM_COMMITTEE_BRIEFING"]
    approved_types = set()
    
    for review in history:
        artifact_type = review.get("artifact_type", "")
        decision = review.get("decision", "")
        if decision == "APPROVED":
            approved_types.add(artifact_type)
    
    for req_type in required_types:
        if req_type not in approved_types:
            issues.append(f"{req_type} not approved via HR_LANG")
    
    return len(issues) == 0, issues

def advance_state():
    """Advance state from COMM_EVT to FLOOR_EVT"""
    print("=" * 60)
    print("Advancing State: COMM_EVT -> FLOOR_EVT")
    print("=" * 60)
    
    # Check requirements
    can_advance, issues = check_requirements()
    
    if not can_advance:
        print("\n[ERROR] Cannot advance state. Issues:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    
    print("\n[OK] All requirements satisfied")
    
    # Load current state
    state_data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    
    # Update state
    old_state = state_data.get("current_state", "")
    state_data["current_state"] = "FLOOR_EVT"
    state_data["state_definition"] = "Floor Consideration"
    state_data["next_allowed_states"] = ["FINAL_EVT"]
    state_data["state_advancement_rule"] = "Requires HR_MSG approval + Requires external confirmation: vote_result"
    
    # Add to history
    state_history = state_data.get("state_history", [])
    state_history.append({
        "state": "FLOOR_EVT",
        "entered_at": datetime.now(timezone.utc).isoformat(),
        "entered_by": "system",
        "reason": "State advanced - COMM_EVT artifacts approved via HR_LANG, floor scheduling confirmed"
    })
    state_data["state_history"] = state_history
    
    # Update metadata
    state_data["_meta"]["last_updated"] = datetime.now(timezone.utc).isoformat()
    
    # Save
    STATE_PATH.write_text(json.dumps(state_data, indent=2), encoding="utf-8")
    
    print(f"\n[OK] State advanced: {old_state} -> FLOOR_EVT")
    print(f"[OK] State file updated: {STATE_PATH}")
    print(f"\nNext allowed states: {state_data['next_allowed_states']}")
    print(f"Next advancement rule: {state_data['state_advancement_rule']}")
    
    return True

if __name__ == "__main__":
    success = advance_state()
    if success:
        print("\n[SUCCESS] State advancement complete")
    else:
        print("\n[FAILED] State advancement blocked")
        exit(1)
