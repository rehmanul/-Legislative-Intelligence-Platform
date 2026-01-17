"""
Script: cockpit__write_approval.py
Intent: snapshot

Reads:
- approval manifest JSON (from HTML interface or command line)
- review/HR_*_queue.json files
- artifacts/{agent_id}/*.json files

Writes:
- approvals/{review_id}.json (individual approval decisions)
- approvals/manifest.json (aggregated manifest)
- Updates review/HR_*_queue.json (moves from pending to history)
- Updates artifact files (_meta.status: ACTIONABLE)
- audit/audit-log.jsonl (logs approval decisions)

Schema:
Bridge script that writes approval decisions from HTML interface to filesystem.
Can read manifest JSON from stdin, file, or command-line arguments.
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

# Path setup
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

# Constants
REVIEW_DIR = BASE_DIR / "review"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
AUDIT_LOG_PATH = BASE_DIR / "audit" / "audit-log.jsonl"
APPROVALS_DIR = BASE_DIR / "approvals"

# Ensure approvals directory exists
APPROVALS_DIR.mkdir(parents=True, exist_ok=True)

# Review gate definitions
REVIEW_GATES = {
    "HR_PRE": "Concept Direction Review",
    "HR_LANG": "Legislative Language Review",
    "HR_MSG": "Messaging & Narrative Review",
    "HR_RELEASE": "Public Release Authorization",
}


def load_json(path: Path) -> Dict[str, Any]:
    """Load JSON file, return {} if not found or invalid."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
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


def write_approval_decision(decision: Dict[str, Any]) -> bool:
    """
    Write a single approval decision to filesystem.
    
    Args:
        decision: Decision object with review_id, gate_id, decision, etc.
        
    Returns:
        True if successful
    """
    review_id = decision.get("review_id")
    gate_id = decision.get("gate_id")
    artifact_path = decision.get("artifact_path", "")
    decision_value = decision.get("decision")
    rationale = decision.get("rationale")
    decision_by = decision.get("decision_by", "human:reviewer")
    risk_level = decision.get("risk_level", "")
    
    if not review_id:
        print(f"[ERROR] Missing review_id in decision: {decision}")
        return False
    
    if not gate_id or gate_id not in REVIEW_GATES:
        print(f"[ERROR] Invalid or missing gate_id: {gate_id}")
        return False
    
    if decision_value not in ["APPROVE", "REJECT"]:
        print(f"[ERROR] Invalid decision: {decision_value}. Must be APPROVE or REJECT")
        return False
    
    # Write individual approval file
    approval_file = APPROVALS_DIR / f"{review_id}.json"
    approval_data = {
        "_meta": {
            "review_id": review_id,
            "gate_id": gate_id,
            "written_at": datetime.now(timezone.utc).isoformat() + "Z",
            "written_by": "cockpit__write_approval.py"
        },
        "decision": decision
    }
    save_json(approval_file, approval_data)
    print(f"[OK] Written approval decision: {approval_file}")
    
    # Load review queue
    queue_file = REVIEW_DIR / f"{gate_id}_queue.json"
    if not queue_file.exists():
        print(f"[WARNING] Review queue file not found: {queue_file}")
        print(f"[INFO] Approval decision saved, but queue file update skipped")
        log_audit_event(
            "approval_written",
            f"Approval decision written for {review_id} (queue file not found)",
            review_id=review_id,
            gate_id=gate_id,
            decision=decision_value,
            decision_by=decision_by
        )
        return True
    
    queue_data = load_json(queue_file)
    pending_reviews = queue_data.get("pending_reviews", [])
    
    # Find and update the review entry
    review_entry = None
    review_index = None
    for idx, review in enumerate(pending_reviews):
        if review.get("review_id") == review_id:
            review_entry = review
            review_index = idx
            break
    
    if review_entry:
        # Move from pending to history
        pending_reviews.pop(review_index)
        
        # Update review entry with decision
        review_entry["decision"] = decision_value
        review_entry["decision_at"] = decision.get("decision_at") or datetime.now(timezone.utc).isoformat() + "Z"
        review_entry["decision_by"] = decision_by
        review_entry["decision_rationale"] = rationale
        review_entry["status"] = decision_value
        
        # Add to history
        review_history = queue_data.get("review_history", [])
        review_history.append(review_entry)
        queue_data["review_history"] = review_history
        queue_data["pending_reviews"] = pending_reviews
        
        # Update queue status
        if pending_reviews:
            queue_data["_meta"]["status"] = "PENDING"
        else:
            queue_data["_meta"]["status"] = "APPROVED" if decision_value == "APPROVE" else "REJECTED"
        
        queue_data["_meta"]["last_updated"] = datetime.now(timezone.utc).isoformat() + "Z"
        
        # Save updated queue
        save_json(queue_file, queue_data)
        print(f"[OK] Updated review queue: {queue_file}")
    else:
        print(f"[WARNING] Review entry {review_id} not found in pending reviews for {gate_id}")
    
    # Update artifact file if it exists and decision is APPROVE
    if decision_value == "APPROVE" and artifact_path:
        artifact_file = BASE_DIR / artifact_path.replace("\\", "/")
        if artifact_file.exists():
            artifact_data = load_json(artifact_file)
            if "_meta" in artifact_data:
                artifact_data["_meta"]["status"] = "ACTIONABLE"
                artifact_data["_meta"]["confidence"] = "HIGH"
                artifact_data["_meta"]["human_review_required"] = False
                artifact_data["_meta"]["approved_at"] = decision.get("decision_at") or datetime.now(timezone.utc).isoformat() + "Z"
                artifact_data["_meta"]["approved_by"] = decision_by
                if rationale:
                    artifact_data["_meta"]["approval_rationale"] = rationale
                save_json(artifact_file, artifact_data)
                print(f"[OK] Updated artifact file: {artifact_file}")
            else:
                print(f"[WARNING] Artifact file {artifact_file} missing _meta block")
        else:
            print(f"[WARNING] Artifact file not found: {artifact_file}")
    
    # Log to audit trail
    log_audit_event(
        "artifact_reviewed",
        f"Artifact {review_id} {decision_value.lower()}ed via {gate_id}",
        gate_id=gate_id,
        review_id=review_id,
        artifact_path=artifact_path,
        decision=decision_value,
        decision_by=decision_by,
        rationale=rationale,
        risk_level=risk_level
    )
    
    return True


def process_manifest(manifest: Dict[str, Any]) -> int:
    """
    Process an approval manifest with multiple decisions.
    
    Args:
        manifest: Manifest object with _meta and decisions array
        
    Returns:
        Number of successful decisions processed
    """
    decisions = manifest.get("decisions", [])
    if not decisions:
        print("[WARNING] Manifest contains no decisions")
        return 0
    
    print(f"[INFO] Processing {len(decisions)} approval decisions...")
    
    success_count = 0
    for decision in decisions:
        if write_approval_decision(decision):
            success_count += 1
        else:
            print(f"[ERROR] Failed to process decision for {decision.get('review_id', 'UNKNOWN')}")
    
    # Write aggregated manifest to approvals directory
    manifest_file = APPROVALS_DIR / "manifest.json"
    save_json(manifest_file, manifest)
    print(f"[OK] Saved manifest: {manifest_file}")
    
    return success_count


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description="Write approval decisions from HTML interface to filesystem",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Read manifest from file
  python cockpit__write_approval.py --manifest-file approvals/manifest.json
  
  # Read manifest from stdin
  cat manifest.json | python cockpit__write_approval.py
  
  # Single decision from command line
  python cockpit__write_approval.py --review-id hr_pre_001 --gate-id HR_PRE --decision APPROVE --artifact-path artifacts/concept.json
  
  # Read from default manifest location
  python cockpit__write_approval.py
        """
    )
    
    parser.add_argument("--manifest-file", "-f", type=Path, help="Path to approval manifest JSON file")
    parser.add_argument("--review-id", help="Review ID (for single decision)")
    parser.add_argument("--gate-id", choices=list(REVIEW_GATES.keys()), help="Review gate ID (for single decision)")
    parser.add_argument("--decision", choices=["APPROVE", "REJECT"], help="Decision (for single decision)")
    parser.add_argument("--artifact-path", help="Artifact path (for single decision)")
    parser.add_argument("--artifact-name", help="Artifact name (for single decision)")
    parser.add_argument("--rationale", "-r", help="Rationale for decision")
    parser.add_argument("--decision-by", "-u", default="human:reviewer", help="User identifier")
    
    args = parser.parse_args()
    
    # Single decision mode
    if args.review_id:
        if not args.gate_id or not args.decision:
            print("[ERROR] --gate-id and --decision required when using --review-id")
            sys.exit(1)
        
        decision = {
            "review_id": args.review_id,
            "gate_id": args.gate_id,
            "artifact_path": args.artifact_path or "",
            "artifact_name": args.artifact_name or "",
            "decision": args.decision,
            "rationale": args.rationale,
            "decision_at": datetime.now(timezone.utc).isoformat() + "Z",
            "decision_by": args.decision_by
        }
        
        success = write_approval_decision(decision)
        sys.exit(0 if success else 1)
    
    # Manifest mode
    manifest_data = None
    
    # Try to read from file
    if args.manifest_file:
        if not args.manifest_file.exists():
            print(f"[ERROR] Manifest file not found: {args.manifest_file}")
            sys.exit(1)
        manifest_data = load_json(args.manifest_file)
    else:
        # Try default location
        default_manifest = APPROVALS_DIR / "manifest.json"
        if default_manifest.exists():
            print(f"[INFO] Reading manifest from default location: {default_manifest}")
            manifest_data = load_json(default_manifest)
        else:
            # Try reading from stdin
            if not sys.stdin.isatty():
                try:
                    manifest_data = json.load(sys.stdin)
                    print("[INFO] Reading manifest from stdin")
                except json.JSONDecodeError as e:
                    print(f"[ERROR] Failed to parse JSON from stdin: {e}")
                    sys.exit(1)
    
    if not manifest_data:
        print("[ERROR] No manifest data provided. Use --manifest-file, --review-id, or pipe JSON to stdin")
        sys.exit(1)
    
    success_count = process_manifest(manifest_data)
    total_count = len(manifest_data.get("decisions", []))
    
    if success_count == total_count:
        print(f"[SUCCESS] Processed all {success_count} decisions")
        sys.exit(0)
    else:
        print(f"[WARNING] Processed {success_count} of {total_count} decisions")
        sys.exit(1 if success_count == 0 else 0)


if __name__ == "__main__":
    main()
