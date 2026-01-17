"""
Script: review_schema.py
Intent: snapshot

Reads:
- None (defines schema only)

Writes:
- None (utility module)

Schema:
- Defines review log entry schema and validation
- Used by review server and brief generator
"""

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Literal
from dataclasses import dataclass, asdict, field
import uuid


# Schema version for future migrations
SCHEMA_VERSION = "1.0.0"

# Valid decision values
DecisionType = Literal["APPROVE", "REJECT", "REVISE"]


@dataclass
class ReviewEntry:
    """Single review decision for an artifact."""
    review_id: str
    artifact_path: str
    decision: DecisionType
    reason: str
    reviewed_at: str
    reviewer: str
    artifact_modified_at: str
    artifact_sha256: str
    selected_for_llm: bool
    intended_recipient: str  # e.g., "ChatGPT", "Codex", "Claude", "Internal"
    why_sending: str
    schema_version: str = SCHEMA_VERSION
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReviewEntry":
        return cls(**data)


@dataclass
class ReviewLog:
    """Collection of review entries with metadata."""
    _meta: Dict[str, Any]
    reviews: List[ReviewEntry]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "_meta": self._meta,
            "reviews": [r.to_dict() for r in self.reviews]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReviewLog":
        meta = data.get("_meta", {})
        reviews = [ReviewEntry.from_dict(r) for r in data.get("reviews", [])]
        return cls(_meta=meta, reviews=reviews)


def generate_review_id() -> str:
    """Generate unique review ID."""
    return f"review_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA256 hash of file contents."""
    try:
        content = file_path.read_bytes()
        return hashlib.sha256(content).hexdigest()
    except Exception:
        return "HASH_ERROR"


def get_file_modified_time(file_path: Path) -> str:
    """Get file modification time as ISO string."""
    try:
        mtime = file_path.stat().st_mtime
        return datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()
    except Exception:
        return "UNKNOWN"


def validate_review_entry(entry: Dict[str, Any]) -> tuple[bool, List[str]]:
    """Validate a review entry against schema."""
    errors = []
    
    required_fields = [
        "review_id", "artifact_path", "decision", "reason",
        "reviewed_at", "reviewer", "artifact_modified_at", "artifact_sha256",
        "selected_for_llm", "intended_recipient", "why_sending"
    ]
    
    for field in required_fields:
        if field not in entry:
            errors.append(f"Missing required field: {field}")
    
    if "decision" in entry:
        if entry["decision"] not in ["APPROVE", "REJECT", "REVISE"]:
            errors.append(f"Invalid decision: {entry['decision']}. Must be APPROVE, REJECT, or REVISE")
    
    if "selected_for_llm" in entry:
        if not isinstance(entry["selected_for_llm"], bool):
            errors.append(f"selected_for_llm must be boolean, got {type(entry['selected_for_llm'])}")
    
    return len(errors) == 0, errors


def create_review_entry(
    artifact_path: str,
    decision: DecisionType,
    reason: str,
    reviewer: str = "local_user",
    selected_for_llm: bool = False,
    intended_recipient: str = "",
    why_sending: str = "",
    base_dir: Optional[Path] = None
) -> ReviewEntry:
    """Create a new review entry with computed fields."""
    
    # Resolve artifact path
    if base_dir:
        full_path = base_dir / artifact_path
    else:
        full_path = Path(artifact_path)
    
    return ReviewEntry(
        review_id=generate_review_id(),
        artifact_path=artifact_path,
        decision=decision,
        reason=reason,
        reviewed_at=datetime.now(timezone.utc).isoformat(),
        reviewer=reviewer,
        artifact_modified_at=get_file_modified_time(full_path),
        artifact_sha256=compute_file_hash(full_path),
        selected_for_llm=selected_for_llm,
        intended_recipient=intended_recipient,
        why_sending=why_sending,
        schema_version=SCHEMA_VERSION
    )


def load_review_log(log_path: Path) -> ReviewLog:
    """Load review log from file."""
    if not log_path.exists():
        return ReviewLog(
            _meta={
                "schema_version": SCHEMA_VERSION,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "total_reviews": 0
            },
            reviews=[]
        )
    
    try:
        data = json.loads(log_path.read_text(encoding="utf-8"))
        return ReviewLog.from_dict(data)
    except Exception as e:
        print(f"[ERROR] Failed to load review log: {e}")
        return ReviewLog(
            _meta={
                "schema_version": SCHEMA_VERSION,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "total_reviews": 0,
                "load_error": str(e)
            },
            reviews=[]
        )


def save_review_log(log: ReviewLog, log_path: Path) -> bool:
    """Save review log to file."""
    try:
        log._meta["last_updated"] = datetime.now(timezone.utc).isoformat()
        log._meta["total_reviews"] = len(log.reviews)
        log._meta["schema_version"] = SCHEMA_VERSION
        
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(json.dumps(log.to_dict(), indent=2), encoding="utf-8")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save review log: {e}")
        return False


def append_review(log_path: Path, entry: ReviewEntry) -> bool:
    """Append a review entry to the log."""
    log = load_review_log(log_path)
    log.reviews.append(entry)
    return save_review_log(log, log_path)


def get_latest_status(log: ReviewLog, artifact_path: str) -> Optional[Dict[str, Any]]:
    """Get the latest review status for an artifact."""
    matching = [r for r in log.reviews if r.artifact_path == artifact_path]
    if not matching:
        return None
    
    # Sort by reviewed_at descending
    matching.sort(key=lambda r: r.reviewed_at, reverse=True)
    latest = matching[0]
    
    return {
        "decision": latest.decision,
        "reason": latest.reason,
        "reviewed_at": latest.reviewed_at,
        "reviewer": latest.reviewer,
        "selected_for_llm": latest.selected_for_llm,
        "review_count": len(matching)
    }


def get_artifacts_by_status(log: ReviewLog) -> Dict[str, List[str]]:
    """Group artifacts by their latest status."""
    result = {
        "APPROVE": [],
        "REJECT": [],
        "REVISE": [],
        "UNREVIEWED": []
    }
    
    # Get unique artifact paths
    all_paths = set(r.artifact_path for r in log.reviews)
    
    for path in all_paths:
        status = get_latest_status(log, path)
        if status:
            result[status["decision"]].append(path)
    
    return result


def get_llm_ready_artifacts(log: ReviewLog) -> List[ReviewEntry]:
    """Get artifacts that are approved and selected for LLM."""
    # Get latest review for each artifact
    latest_by_path = {}
    for review in log.reviews:
        if review.artifact_path not in latest_by_path:
            latest_by_path[review.artifact_path] = review
        elif review.reviewed_at > latest_by_path[review.artifact_path].reviewed_at:
            latest_by_path[review.artifact_path] = review
    
    # Filter to approved + selected for LLM
    return [
        r for r in latest_by_path.values()
        if r.decision == "APPROVE" and r.selected_for_llm
    ]


if __name__ == "__main__":
    # Test the schema
    print("[INFO] Testing review schema...")
    
    entry = create_review_entry(
        artifact_path="test/artifact.json",
        decision="APPROVE",
        reason="Looks good",
        selected_for_llm=True,
        intended_recipient="ChatGPT",
        why_sending="Need analysis"
    )
    
    print(f"[OK] Created entry: {entry.review_id}")
    
    is_valid, errors = validate_review_entry(entry.to_dict())
    if is_valid:
        print("[OK] Entry validates successfully")
    else:
        print(f"[ERROR] Validation errors: {errors}")
