"""
Script: advance_to_comm_evt.py
Intent: snapshot (modifies state)
Purpose: Advance legislative state from INTRO_EVT to COMM_EVT

Reads:
- state/legislative-state.json
- review/HR_PRE_queue.json

Writes:
- state/legislative-state.json (updates state to COMM_EVT)
"""

import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
STATE_PATH = BASE_DIR / "state" / "legislative-state.json"
REVIEW_QUEUE_PATH = BASE_DIR / "review" / "HR_PRE_queue.json"

def check_requirements():
    """Check if requirements for COMM_EVT are met"""
    issues = []
    
    # Check current state
    if not STATE_PATH.exists():
        return False, ["State file not found"]
    
    state_data = json.loads(STATE_PATH.read_text())
    current_state = state_data.get("current_state", "")
    
    if current_state != "INTRO_EVT":
        return False, [f"Current state is {current_state}, expected INTRO_EVT"]
    
    # Check review queue for approved artifacts
    if not REVIEW_QUEUE_PATH.exists():
        return False, ["Review queue not found"]
    
    queue = json.loads(REVIEW_QUEUE_PATH.read_text())
    history = queue.get("review_history", [])
    
    # Check for approved INTRO_FRAME
    intro_frame_approved = False
    intro_whitepaper_approved = False
    
    for review in history:
        artifact_type = review.get("artifact_type", "")
        decision = review.get("decision", "")
        
        if artifact_type == "INTRO_FRAME" and decision == "APPROVED":
            intro_frame_approved = True
        if artifact_type == "INTRO_WHITEPAPER" and decision == "APPROVED":
            intro_whitepaper_approved = True
    
    if not intro_frame_approved:
        issues.append("INTRO_FRAME not approved")
    if not intro_whitepaper_approved:
        issues.append("INTRO_WHITEPAPER not approved")
    
    return len(issues) == 0, issues

def advance_state():
    """Advance state from INTRO_EVT to COMM_EVT"""
    print("=" * 60)
    print("Advancing State: INTRO_EVT -> COMM_EVT")
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
    state_data = json.loads(STATE_PATH.read_text())
    
    # Update state
    old_state = state_data.get("current_state", "")
    state_data["current_state"] = "COMM_EVT"
    state_data["state_definition"] = "Committee Referral"
    state_data["next_allowed_states"] = ["FLOOR_EVT"]
    state_data["state_advancement_rule"] = "Requires HR_LANG approval + Requires external confirmation: floor_scheduling"
    
    # Add to history
    state_history = state_data.get("state_history", [])
    state_history.append({
        "state": "COMM_EVT",
        "entered_at": datetime.utcnow().isoformat() + "Z",
        "entered_by": "system",
        "reason": "State advanced - INTRO_EVT artifacts approved, committee referral confirmed"
    })
    state_data["state_history"] = state_history
    
    # Update metadata
    state_data["_meta"]["last_updated"] = datetime.utcnow().isoformat() + "Z"
    
    # Save
    STATE_PATH.write_text(json.dumps(state_data, indent=2))
    
    print(f"\n[OK] State advanced: {old_state} -> COMM_EVT")
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
