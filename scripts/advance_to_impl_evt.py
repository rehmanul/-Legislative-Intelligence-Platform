"""
Script: advance_to_impl_evt.py
Intent: snapshot (modifies state)
Purpose: Advance legislative state from FINAL_EVT to IMPL_EVT (final state)

Reads:
- state/legislative-state.json
- review/HR_RELEASE_queue.json

Writes:
- state/legislative-state.json (updates state to IMPL_EVT)
"""

import json
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
STATE_PATH = BASE_DIR / "state" / "legislative-state.json"
HR_RELEASE_QUEUE_PATH = BASE_DIR / "review" / "HR_RELEASE_queue.json"

def check_requirements():
    """Check if requirements for IMPL_EVT are met"""
    issues = []
    
    # Check current state
    if not STATE_PATH.exists():
        return False, ["State file not found"]
    
    state_data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    current_state = state_data.get("current_state", "")
    
    if current_state != "FINAL_EVT":
        return False, [f"Current state is {current_state}, expected FINAL_EVT"]
    
    # Check HR_RELEASE queue for approved artifacts
    if not HR_RELEASE_QUEUE_PATH.exists():
        return False, ["HR_RELEASE queue not found"]
    
    queue = json.loads(HR_RELEASE_QUEUE_PATH.read_text(encoding="utf-8"))
    history = queue.get("review_history", [])
    
    # Check for approved FINAL_EVT artifacts
    required_types = ["FINAL_CONSTITUENT_NARRATIVE"]
    approved_types = set()
    
    for review in history:
        artifact_type = review.get("artifact_type", "")
        decision = review.get("decision", "")
        if decision == "APPROVED":
            approved_types.add(artifact_type)
    
    for req_type in required_types:
        if req_type not in approved_types:
            issues.append(f"{req_type} not approved via HR_RELEASE")
    
    return len(issues) == 0, issues

def advance_state():
    """Advance state from FINAL_EVT to IMPL_EVT"""
    print("=" * 60)
    print("Advancing State: FINAL_EVT -> IMPL_EVT")
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
    state_data["current_state"] = "IMPL_EVT"
    state_data["state_definition"] = "Implementation & Monitoring"
    state_data["next_allowed_states"] = []  # Terminal state
    state_data["state_advancement_rule"] = "Terminal state - workflow complete"
    
    # Add to history
    state_history = state_data.get("state_history", [])
    state_history.append({
        "state": "IMPL_EVT",
        "entered_at": datetime.now(timezone.utc).isoformat(),
        "entered_by": "system",
        "reason": "State advanced - FINAL_EVT artifacts approved via HR_RELEASE, enactment confirmed"
    })
    state_data["state_history"] = state_history
    
    # Update metadata
    state_data["_meta"]["last_updated"] = datetime.now(timezone.utc).isoformat()
    
    # Save
    STATE_PATH.write_text(json.dumps(state_data, indent=2), encoding="utf-8")
    
    print(f"\n[OK] State advanced: {old_state} -> IMPL_EVT")
    print(f"[OK] State file updated: {STATE_PATH}")
    print(f"\nNext allowed states: {state_data['next_allowed_states']}")
    print(f"Status: {state_data['state_advancement_rule']}")
    
    return True

if __name__ == "__main__":
    success = advance_state()
    if success:
        print("\n" + "=" * 60)
        print("WORKFLOW COMPLETE")
        print("=" * 60)
        print("\nThe legislative workflow has reached its terminal state (IMPL_EVT).")
        print("All phases have been completed:")
        print("  1. PRE_EVT - Pre-Event Planning")
        print("  2. INTRO_EVT - Bill Introduction")
        print("  3. COMM_EVT - Committee Consideration")
        print("  4. FLOOR_EVT - Floor Consideration")
        print("  5. FINAL_EVT - Final Passage")
        print("  6. IMPL_EVT - Implementation & Monitoring (CURRENT)")
        print("\n[SUCCESS] Full legislative workflow executed successfully!")
    else:
        print("\n[FAILED] State advancement blocked")
        exit(1)
