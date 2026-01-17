"""
Intro EVT validation helper (INTERNAL / NON-AUTHORITATIVE).

Checks:
- HR_PRE queue has ACTIVE entries aligned to latest per artifact_type
- Required artifacts and diagrams exist
- Reports missing/stale items without mutating state

Usage:
    python scripts/validate_intro_evt.py
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

BASE_DIR = Path(__file__).resolve().parent.parent
QUEUE_PATH = BASE_DIR / "review" / "HR_PRE_queue.json"
DASHBOARD_PATH = BASE_DIR / "dashboards" / "intro_evt_overview.json"

ARTIFACT_PATHS = {
    "PRE_CONCEPT": BASE_DIR / "artifacts" / "draft_concept_memo_pre_evt" / "PRE_CONCEPT.json",
    "INTRO_FRAME": BASE_DIR / "artifacts" / "draft_framing_intro_evt" / "INTRO_FRAME.json",
    "INTRO_WHITEPAPER": BASE_DIR / "artifacts" / "draft_whitepaper_intro_evt" / "INTRO_WHITEPAPER.json",
}

DIAGRAM_PATHS = {
    "INTRO_FRAME": BASE_DIR / "diagrams" / "INTRO_FRAME.mmd",
    "INTRO_WHITEPAPER": BASE_DIR / "diagrams" / "INTRO_WHITEPAPER.mmd",
}


def load_json(path: Path) -> Dict:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def newest_by_type(entries: List[Dict]) -> Dict[str, Dict]:
    latest: Dict[str, Dict] = {}
    for entry in entries:
        ts = entry.get("submitted_at", "")
        try:
            parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except Exception:
            parsed = datetime.min
        art_type = entry.get("artifact_type", "UNKNOWN")
        if art_type not in latest or parsed > latest[art_type]["_ts"]:
            latest[art_type] = {**entry, "_ts": parsed}
    return latest


def summarize():
    queue = load_json(QUEUE_PATH)
    pending = queue.get("pending_reviews", [])
    latest = newest_by_type(pending)

    artifacts_status = []
    for art_type, path in ARTIFACT_PATHS.items():
        artifacts_status.append(
            {
                "artifact_type": art_type,
                "path": str(path.relative_to(BASE_DIR)),
                "exists": path.exists(),
                "active_review_id": latest.get(art_type, {}).get("review_id"),
                "active_status": latest.get(art_type, {}).get("status"),
            }
        )

    diagrams_status = []
    for name, path in DIAGRAM_PATHS.items():
        diagrams_status.append(
            {
                "name": name,
                "path": str(path.relative_to(BASE_DIR)),
                "exists": path.exists(),
            }
        )

    return {
        "queue_loaded": bool(queue),
        "latest_by_type": {k: {"review_id": v.get("review_id"), "status": v.get("status")} for k, v in latest.items()},
        "artifacts": artifacts_status,
        "diagrams": diagrams_status,
        "note": "INTERNAL, NON-AUTHORITATIVE — pending HR_PRE approval",
    }


if __name__ == "__main__":
    report = summarize()
    print(json.dumps(report, indent=2))
