"""
Script: submit_intro_evt_artifacts_to_review.py
Intent: snapshot (modifies review queue)
Purpose: Submit existing INTRO_EVT artifacts to HR_PRE review queue

Reads:
- artifacts/draft_framing_intro_evt/INTRO_FRAME.json
- artifacts/draft_whitepaper_intro_evt/INTRO_WHITEPAPER.json
- review/HR_PRE_queue.json

Writes:
- review/HR_PRE_queue.json (adds pending reviews)

Schema: Review queue schema
"""

import json
import uuid
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
REVIEW_QUEUE_PATH = BASE_DIR / "review" / "HR_PRE_queue.json"
INTRO_FRAME_PATH = BASE_DIR / "artifacts" / "draft_framing_intro_evt" / "INTRO_FRAME.json"
INTRO_WHITEPAPER_PATH = BASE_DIR / "artifacts" / "draft_whitepaper_intro_evt" / "INTRO_WHITEPAPER.json"

def load_review_queue():
    """Load existing review queue"""
    if REVIEW_QUEUE_PATH.exists():
        return json.loads(REVIEW_QUEUE_PATH.read_text())
    else:
        return {
            "_meta": {
                "review_gate": "HR_PRE",
                "review_gate_name": "Approve Concept Direction",
                "display_name": "Concept Direction Review",
                "description": "Human approval of concept memo and policy direction before bill introduction",
                "created_at": datetime.utcnow().isoformat() + "Z",
                "status": "PENDING",
                "note": "SYNCED FROM API - This file is maintained by API"
            },
            "pending_reviews": [],
            "review_history": []
        }

def artifact_already_in_queue(queue, artifact_path):
    """Check if artifact is already in queue (pending or history)"""
    artifact_rel_path = str(artifact_path.relative_to(BASE_DIR))
    
    # Check pending reviews
    for review in queue.get("pending_reviews", []):
        if review.get("artifact_path") == artifact_rel_path:
            return True
    
    # Check review history
    for review in queue.get("review_history", []):
        if review.get("artifact_path") == artifact_rel_path:
            return True
    
    return False

def submit_artifact_to_queue(artifact_path: Path, artifact_type: str, artifact_name: str, review_effort: str, risk_level: str, review_requirements: list):
    """Submit artifact to HR_PRE review queue"""
    queue = load_review_queue()
    
    # Check if already submitted
    if artifact_already_in_queue(queue, artifact_path):
        print(f"  [SKIP] {artifact_name} already in review queue - skipping")
        return None
    
    # Load artifact to get metadata
    try:
        artifact_data = json.loads(artifact_path.read_text())
        artifact_meta = artifact_data.get("_meta", {})
    except Exception as e:
        print(f"  [WARN] Could not load artifact metadata: {e}")
        artifact_meta = {}
    
    # Create review entry
    review_entry = {
        "review_id": f"{uuid.uuid4()}_{artifact_name.replace(' ', '_')}",
        "artifact_path": str(artifact_path.relative_to(BASE_DIR)),
        "artifact_type": artifact_type,
        "artifact_name": artifact_name,
        "submitted_by": artifact_meta.get("agent_id", "system"),
        "submitted_at": datetime.utcnow().isoformat() + "Z",
        "review_effort_estimate": review_effort,
        "risk_level": risk_level,
        "review_requirements": review_requirements,
        "decision": None,
        "decision_at": None,
        "decision_by": None,
        "decision_rationale": None,
        "status": "ACTIVE"
    }
    
    # Add to pending reviews
    queue["pending_reviews"].append(review_entry)
    queue["_meta"]["status"] = "PENDING"
    
    # Save queue
    REVIEW_QUEUE_PATH.write_text(json.dumps(queue, indent=2))
    
    print(f"  [OK] {artifact_name} submitted to HR_PRE queue (ID: {review_entry['review_id']})")
    return review_entry["review_id"]

def main():
    """Submit INTRO_EVT artifacts to HR_PRE review"""
    print("=" * 60)
    print("Submitting INTRO_EVT Artifacts to HR_PRE Review")
    print("=" * 60)
    
    submitted = []
    
    # Submit INTRO_FRAME
    if INTRO_FRAME_PATH.exists():
        print(f"\nProcessing: {INTRO_FRAME_PATH.name}")
        review_id = submit_artifact_to_queue(
            artifact_path=INTRO_FRAME_PATH,
            artifact_type="INTRO_FRAME",
            artifact_name="Legitimacy & Policy Framing",
            review_effort="10-15 minutes",
            risk_level="Low-Medium",
            review_requirements=[
                "Review framing document content",
                "Assess legitimacy arguments",
                "Evaluate framing narrative options",
                "Approve or reject concept direction"
            ]
        )
        if review_id:
            submitted.append(("INTRO_FRAME", review_id))
    else:
        print(f"\n[ERROR] {INTRO_FRAME_PATH.name} not found")
    
    # Submit INTRO_WHITEPAPER
    if INTRO_WHITEPAPER_PATH.exists():
        print(f"\nProcessing: {INTRO_WHITEPAPER_PATH.name}")
        review_id = submit_artifact_to_queue(
            artifact_path=INTRO_WHITEPAPER_PATH,
            artifact_type="INTRO_WHITEPAPER",
            artifact_name="Policy Whitepaper",
            review_effort="10-15 minutes",
            risk_level="Low-Medium",
            review_requirements=[
                "Review whitepaper content",
                "Assess research citations and evidence",
                "Evaluate policy rationale and impact analysis",
                "Approve or reject concept direction"
            ]
        )
        if review_id:
            submitted.append(("INTRO_WHITEPAPER", review_id))
    else:
        print(f"\n[ERROR] {INTRO_WHITEPAPER_PATH.name} not found")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Artifacts submitted: {len(submitted)}")
    for artifact_type, review_id in submitted:
        print(f"  [OK] {artifact_type}: {review_id}")
    
    if submitted:
        print(f"\nReview queue updated: {REVIEW_QUEUE_PATH}")
        print(f"Pending reviews: Check HR_PRE_queue.json for review status")
        print(f"\nNote: Artifacts require human approval before state advancement")
    else:
        print("\n[WARN] No artifacts were submitted (may already be in queue)")

if __name__ == "__main__":
    main()
