"""
Script: cockpit__approve_artifact.py
Intent:
- snapshot

Reads:
- review/HR_*_queue.json (4 files)
- artifacts/{agent_id}/*.json (artifact content)

Writes:
- Updates review/HR_*_queue.json (moves from pending to history)
- audit/audit-log.jsonl (logs approval decision)

Schema:
Command-line script that approves or rejects artifacts in review queues.
Input: gate_id, artifact_id (or review_id), decision (APPROVE/REJECT), rationale (optional)
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
REVIEW_DIR = BASE_DIR / "review"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
AUDIT_LOG_PATH = BASE_DIR / "audit" / "audit-log.jsonl"
APPROVALS_DIR = BASE_DIR / "approvals"

# Review gate definitions
REVIEW_GATES = {
    "HR_PRE": "Concept Direction Review",
    "HR_LANG": "Legislative Language Review",
    "HR_MSG": "Messaging & Narrative Review",
    "HR_RELEASE": "Public Release Authorization",
}


def parse_timestamp(ts_str: str) -> Optional[datetime]:
    """Parse ISO timestamp to datetime object."""
    if not ts_str:
        return None
    try:
        ts_str = ts_str.replace("Z", "+00:00")
        return datetime.fromisoformat(ts_str)
    except Exception:
        return None


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


def approve_artifact(
    gate_id: str,
    artifact_id: str,
    decision: str,
    rationale: Optional[str] = None,
    approved_by: str = "operator"
) -> bool:
    """
    Approve or reject an artifact.
    
    Args:
        gate_id: Review gate ID (HR_PRE, HR_LANG, etc.)
        artifact_id: Artifact identifier (review_id or artifact_name)
        decision: "APPROVE" or "REJECT"
        rationale: Optional rationale for decision
        approved_by: User identifier
        
    Returns:
        True if successful
    """
    if gate_id not in REVIEW_GATES:
        print(f"[ERROR] Invalid gate_id: {gate_id}. Must be one of: {', '.join(REVIEW_GATES.keys())}")
        return False
    
    if decision not in ["APPROVE", "REJECT"]:
        print(f"[ERROR] Invalid decision: {decision}. Must be APPROVE or REJECT")
        return False
    
    # Load review queue
    queue_file = REVIEW_DIR / f"{gate_id}_queue.json"
    if not queue_file.exists():
        print(f"[ERROR] Review queue file not found: {queue_file}")
        return False
    
    queue_data = load_json(queue_file)
    pending_reviews = queue_data.get("pending_reviews", [])
    
    # Find the artifact in pending reviews
    review_entry = None
    review_index = None
    for idx, review in enumerate(pending_reviews):
        review_id = review.get("review_id", "")
        artifact_name = review.get("artifact_name", "")
        artifact_path = review.get("artifact_path", "")
        
        # Match by review_id, artifact_name, or artifact_path
        if (artifact_id == review_id or 
            artifact_id == artifact_name or 
            artifact_id in artifact_path):
            review_entry = review
            review_index = idx
            break
    
    if not review_entry:
        print(f"[ERROR] Artifact not found in pending reviews: {artifact_id}")
        print(f"Available pending reviews:")
        for idx, review in enumerate(pending_reviews, 1):
            print(f"  [{idx}] {review.get('artifact_name', 'Unknown')} (review_id: {review.get('review_id', 'N/A')})")
        return False
    
    # Check risk level for confirmation
    risk_level = review_entry.get("risk_level", "").upper()
    if decision == "APPROVE" and "HIGH" in risk_level:
        print(f"[WARNING] HIGH risk artifact. Approval requires confirmation.")
        confirm = input("Type 'APPROVE' to confirm: ")
        if confirm != "APPROVE":
            print("[CANCELLED] Approval cancelled by user")
            return False
    
    # Move from pending to history
    pending_reviews.pop(review_index)
    
    # Update review entry with decision
    review_entry["decision"] = decision
    review_entry["decision_at"] = datetime.now(timezone.utc).isoformat() + "Z"
    review_entry["decision_by"] = approved_by
    review_entry["decision_rationale"] = rationale
    review_entry["status"] = decision
    
    # Add to history
    review_history = queue_data.get("review_history", [])
    review_history.append(review_entry)
    queue_data["review_history"] = review_history
    
    # Update queue status
    if pending_reviews:
        queue_data["_meta"]["status"] = "PENDING"
    else:
        queue_data["_meta"]["status"] = "APPROVED" if decision == "APPROVE" else "REJECTED"
    
    queue_data["_meta"]["last_updated"] = datetime.now(timezone.utc).isoformat() + "Z"
    
    # Save updated queue
    save_json(queue_file, queue_data)
    
    # Log to audit trail
    log_audit_event(
        "artifact_reviewed",
        f"Artifact {artifact_id} {decision.lower()}ed via {gate_id}",
        gate_id=gate_id,
        artifact_id=artifact_id,
        artifact_name=review_entry.get("artifact_name", ""),
        decision=decision,
        decision_by=approved_by,
        rationale=rationale,
        risk_level=risk_level
    )
    
    # Update artifact file if it exists
    artifact_path_str = review_entry.get("artifact_path", "")
    if artifact_path_str:
        artifact_file = BASE_DIR / artifact_path_str
        if artifact_file.exists():
            artifact_data = load_json(artifact_file)
            if "_meta" in artifact_data:
                # Update artifact status (lifecycle status)
                artifact_data["_meta"]["status"] = "ACTIONABLE" if decision == "APPROVE" else "SPECULATIVE"
                artifact_data["_meta"]["confidence"] = "HIGH" if decision == "APPROVE" else "LOW"
                artifact_data["_meta"]["human_review_required"] = False  # DEPRECATED - derive from review_gate_status
                
                # Update review gate status (approval status)
                if decision == "APPROVE":
                    artifact_data["_meta"]["review_gate_status"] = "APPROVED"
                    artifact_data["_meta"]["approved_at"] = datetime.now(timezone.utc).isoformat() + "Z"
                    artifact_data["_meta"]["approved_by"] = approved_by
                elif decision == "REJECT":
                    artifact_data["_meta"]["review_gate_status"] = "REJECTED"
                    artifact_data["_meta"]["rejected_at"] = datetime.now(timezone.utc).isoformat() + "Z"
                # Note: requires_review field persists for audit trail
                
                save_json(artifact_file, artifact_data)
                
                # NEW: If strategy artifact approved, spawn tactical agents
                if decision == "APPROVE":
                    artifact_type = artifact_data.get("_meta", {}).get("artifact_type", "")
                    STRATEGY_ARTIFACT_TYPES = ["RISK_ASSESSMENT", "PRE_CONCEPT", "INTRO_FRAMING", "COMM_LANGUAGE"]
                    
                    if artifact_type in STRATEGY_ARTIFACT_TYPES:
                        print(f"\n[INFO] Strategy artifact approved. Triggering tactical agent spawning...")
                        try:
                            from scripts.tactical__spawn_on_strategy_approval import (
                                spawn_tactical_agents_for_strategy,
                                is_strategy_artifact
                            )
                            
                            if is_strategy_artifact(artifact_data):
                                spawn_results = spawn_tactical_agents_for_strategy(
                                    strategy_artifact_type=artifact_type,
                                    strategy_artifact_data=artifact_data
                                )
                                
                                successful = sum(1 for r in spawn_results if r.get("success"))
                                print(f"[OK] Spawned {successful}/{len(spawn_results)} tactical agents")
                                
                                if successful < len(spawn_results):
                                    print(f"[WARNING] {len(spawn_results) - successful} tactical agents failed to spawn")
                                    for result in spawn_results:
                                        if not result.get("success"):
                                            print(f"  - {result.get('agent_id')}: {result.get('error', 'Unknown error')}")
                        except Exception as e:
                            print(f"[WARNING] Failed to spawn tactical agents: {e}")
                            print("   Strategy approval succeeded, but tactical spawning failed.")
                            print("   You can manually spawn tactical agents if needed.")
    
    print(f"[OK] Artifact {artifact_id} {decision.lower()}ed successfully")
    print(f"   Gate: {gate_id} ({REVIEW_GATES[gate_id]})")
    print(f"   Decision: {decision}")
    if rationale:
        print(f"   Rationale: {rationale}")
    
    return True


def process_manifest_file(manifest_file: Path) -> int:
    """
    Process approval decisions from a manifest file.
    
    Args:
        manifest_file: Path to manifest JSON file
        
    Returns:
        Number of successful decisions processed
    """
    if not manifest_file.exists():
        print(f"[ERROR] Manifest file not found: {manifest_file}")
        return 0
    
    manifest_data = load_json(manifest_file)
    decisions = manifest_data.get("decisions", [])
    
    if not decisions:
        print("[WARNING] Manifest contains no decisions")
        return 0
    
    print(f"[INFO] Processing {len(decisions)} approval decisions from manifest...")
    
    success_count = 0
    for decision in decisions:
        review_id = decision.get("review_id", "")
        gate_id = decision.get("gate_id", "")
        decision_value = decision.get("decision", "")
        rationale = decision.get("rationale")
        decision_by = decision.get("decision_by", "operator")
        artifact_id = review_id  # Use review_id as artifact_id for lookup
        
        if not gate_id or gate_id not in REVIEW_GATES:
            print(f"[ERROR] Invalid or missing gate_id in decision: {decision}")
            continue
        
        if decision_value not in ["APPROVE", "REJECT"]:
            print(f"[ERROR] Invalid decision in manifest: {decision_value}")
            continue
        
        print(f"[INFO] Processing decision for {artifact_id} via {gate_id}...")
        
        if approve_artifact(
            gate_id=gate_id,
            artifact_id=artifact_id,
            decision=decision_value,
            rationale=rationale,
            approved_by=decision_by
        ):
            success_count += 1
    
    return success_count


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description="Approve or reject artifacts in review queues",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Approve an artifact by review_id
  python cockpit__approve_artifact.py HR_PRE review_001 APPROVE "Approved for policy alignment"
  
  # Reject an artifact by artifact_name
  python cockpit__approve_artifact.py HR_LANG "Concept Memo" REJECT "Needs revision"
  
  # Approve with rationale
  python cockpit__approve_artifact.py HR_PRE concept_memo APPROVE --rationale "Policy goals aligned"
  
  # Process decisions from manifest file
  python cockpit__approve_artifact.py --manifest approvals/manifest.json
        """
    )
    
    parser.add_argument("gate_id", nargs="?", choices=list(REVIEW_GATES.keys()), help="Review gate ID (optional if using --manifest)")
    parser.add_argument("artifact_id", nargs="?", help="Artifact identifier (optional if using --manifest)")
    parser.add_argument("decision", nargs="?", choices=["APPROVE", "REJECT"], help="Decision (optional if using --manifest)")
    parser.add_argument("--rationale", "-r", help="Optional rationale for decision")
    parser.add_argument("--approved-by", "-u", default="operator", help="User identifier (default: operator)")
    parser.add_argument("--manifest", "-m", type=Path, help="Process approval decisions from manifest JSON file")
    
    args = parser.parse_args()
    
    # Manifest mode
    if args.manifest:
        success_count = process_manifest_file(args.manifest)
        if success_count > 0:
            print(f"[SUCCESS] Processed {success_count} decisions from manifest")
            sys.exit(0)
        else:
            print("[ERROR] No decisions were successfully processed")
            sys.exit(1)
    
    # Single decision mode (original behavior)
    if not args.gate_id or not args.artifact_id or not args.decision:
        parser.error("gate_id, artifact_id, and decision are required unless using --manifest")
    
    print(f"[cockpit__approve_artifact] Processing {args.decision} for {args.artifact_id} via {args.gate_id}...")
    
    success = approve_artifact(
        gate_id=args.gate_id,
        artifact_id=args.artifact_id,
        decision=args.decision,
        rationale=args.rationale,
        approved_by=args.approved_by
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
