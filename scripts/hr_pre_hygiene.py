"""
HR_PRE queue hygiene utility.

INTERNAL / NON-AUTHORITATIVE:
- Marks newest submission per artifact_type as ACTIVE
- Marks older submissions as SUPERSEDED
- Does not delete or approve anything
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent
QUEUE_PATH = BASE_DIR / "review" / "HR_PRE_queue.json"


def _parse_ts(ts: str) -> datetime:
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return datetime.min


def _mark_status(entries: List[Dict]) -> List[Dict]:
    by_type: Dict[str, List[Tuple[datetime, int]]] = {}
    for idx, entry in enumerate(entries):
        art_type = entry.get("artifact_type", "UNKNOWN")
        ts = _parse_ts(entry.get("submitted_at", ""))
        by_type.setdefault(art_type, []).append((ts, idx))

    for art_type, items in by_type.items():
        # newest first
        items.sort(key=lambda t: t[0], reverse=True)
        for pos, (_, idx) in enumerate(items):
            entries[idx]["status"] = "ACTIVE" if pos == 0 else "SUPERSEDED"
    return entries


def run():
    if not QUEUE_PATH.exists():
        raise FileNotFoundError(f"Queue not found: {QUEUE_PATH}")

    queue = json.loads(QUEUE_PATH.read_text())
    pending = queue.get("pending_reviews", [])
    queue["_meta"]["note"] = "INTERNAL, NON-AUTHORITATIVE — pending HR_PRE approval"

    queue["pending_reviews"] = _mark_status(pending)
    QUEUE_PATH.write_text(json.dumps(queue, indent=2))
    return queue


if __name__ == "__main__":
    run()
