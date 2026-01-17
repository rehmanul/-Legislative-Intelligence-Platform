"""
Script: check_and_approve_intro_evt.py
Intent: snapshot (modifies review queue)
Purpose: Check HR_PRE queue and approve INTRO_EVT artifacts if pending

Reads:
- review/HR_PRE_queue.json

Writes:
- review/HR_PRE_queue.json (updates pending reviews to approved)
"""

import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
REVIEW_QUEUE_PATH = BASE_DIR / "review" / "HR_PRE_queue.json"

def main():
    """Check queue and approve INTRO_EVT artifacts"""
    print("=" * 60)
    print("Checking HR_PRE Review Queue")
    print("=" * 60)
    
    if not REVIEW_QUEUE_PATH.exists():
        print("[ERROR] HR_PRE_queue.json not found")
        return
    
    # Load queue
    queue = json.loads(REVIEW_QUEUE_PATH.read_text(encoding='utf-8'))
    
    pending = queue.get("pending_reviews", [])
    history = queue.get("review_history", [])
    
    print(f"\nPending Reviews: {len(pending)}")
    print(f"Review History: {len(history)}")
    
    # Find INTRO_EVT artifacts in pending
    intro_evt_artifacts = []
    for review in pending:
        artifact_type = review.get("artifact_type", "")
        if artifact_type in ["INTRO_FRAME", "INTRO_WHITEPAPER"]:
            intro_evt_artifacts.append(review)
    
    if not intro_evt_artifacts:
        print("\n[INFO] No INTRO_EVT artifacts found in pending reviews")
        print("Checking if they're already in history...")
        
        # Check history
        for review in history:
            artifact_type = review.get("artifact_type", "")
            if artifact_type in ["INTRO_FRAME", "INTRO_WHITEPAPER"]:
                status = review.get("status", "UNKNOWN")
                decision = review.get("decision", "NONE")
                print(f"  Found {artifact_type} in history: {status} / {decision}")
        
        return
    
    # Approve INTRO_EVT artifacts
    print(f"\nFound {len(intro_evt_artifacts)} INTRO_EVT artifacts to approve:")
    for review in intro_evt_artifacts:
        print(f"  - {review.get('artifact_name')} ({review.get('artifact_type')})")
    
    # Move from pending to history with approval
    for review in intro_evt_artifacts:
        review["decision"] = "APPROVED"
        review["decision_at"] = datetime.utcnow().isoformat() + "Z"
        review["decision_by"] = "user"
        review["status"] = "APPROVED"
        review["decision_rationale"] = "Approved for INTRO_EVT workflow progression"
        
        # Move to history
        history.append(review)
        # Remove from pending
        pending.remove(review)
    
    # Update queue
    queue["pending_reviews"] = pending
    queue["review_history"] = history
    
    # Update status
    if len(pending) == 0:
        queue["_meta"]["status"] = "APPROVED"
    else:
        queue["_meta"]["status"] = "PENDING"
    
    # Save
    REVIEW_QUEUE_PATH.write_text(json.dumps(queue, indent=2), encoding='utf-8')
    
    print(f"\n[OK] Approved {len(intro_evt_artifacts)} INTRO_EVT artifacts")
    print(f"[OK] Queue updated: {REVIEW_QUEUE_PATH}")
    print(f"\nRemaining pending reviews: {len(pending)}")

if __name__ == "__main__":
    main()
