"""
Script: advance_to_final_evt.py
Intent: snapshot (modifies state)
Purpose: Advance legislative state from FLOOR_EVT to FINAL_EVT

Reads:
- state/legislative-state.json
- review/HR_MSG_queue.json

Writes:
- state/legislative-state.json (updates state to FINAL_EVT)
"""

import json
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
STATE_PATH = BASE_DIR / "state" / "legislative-state.json"
HR_MSG_QUEUE_PATH = BASE_DIR / "review" / "HR_MSG_queue.json"

def check_requirements():
    """Check if requirements for FINAL_EVT are met"""
    issues = []
    
    # Check current state
    if not STATE_PATH.exists():
        return False, ["State file not found"]
    
    state_data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    current_state = state_data.get("current_state", "")
    
    if current_state != "FLOOR_EVT":
        return False, [f"Current state is {current_state}, expected FLOOR_EVT"]
    
    # Check HR_MSG queue for approved artifacts
    if not HR_MSG_QUEUE_PATH.exists():
        return False, ["HR_MSG queue not found"]
    
    queue = json.loads(HR_MSG_QUEUE_PATH.read_text(encoding="utf-8"))
    history = queue.get("review_history", [])
    
    # Check for approved FLOOR_EVT artifacts
    required_types = ["FLOOR_MESSAGING", "FLOOR_MEDIA_NARRATIVE"]
    approved_types = set()
    
    for review in history:
        artifact_type = review.get("artifact_type", "")
        decision = review.get("decision", "")
        if decision == "APPROVED":
            approved_types.add(artifact_type)
    
    for req_type in required_types:
        if req_type not in approved_types:
            issues.append(f"{req_type} not approved via HR_MSG")
    
    return len(issues) == 0, issues

def advance_state():
    """Advance state from FLOOR_EVT to FINAL_EVT"""
    print("=" * 60)
    print("Advancing State: FLOOR_EVT -> FINAL_EVT")
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
    state_data["current_state"] = "FINAL_EVT"
    state_data["state_definition"] = "Final Passage & Enactment"
    state_data["next_allowed_states"] = ["IMPL_EVT"]
    state_data["state_advancement_rule"] = "Requires HR_RELEASE approval + Requires external confirmation: enactment"
    
    # Add to history
    state_history = state_data.get("state_history", [])
    state_history.append({
        "state": "FINAL_EVT",
        "entered_at": datetime.now(timezone.utc).isoformat(),
        "entered_by": "system",
        "reason": "State advanced - FLOOR_EVT artifacts approved via HR_MSG, vote result confirmed"
    })
    state_data["state_history"] = state_history
    
    # Update metadata
    state_data["_meta"]["last_updated"] = datetime.now(timezone.utc).isoformat()
    
    # Save
    STATE_PATH.write_text(json.dumps(state_data, indent=2), encoding="utf-8")
    
    print(f"\n[OK] State advanced: {old_state} -> FINAL_EVT")
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
