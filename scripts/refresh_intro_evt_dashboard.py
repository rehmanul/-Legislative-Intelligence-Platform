"""
Refresh intro_evt_overview.json (INTERNAL / NON-AUTHORITATIVE).

Reads HR_PRE_queue.json, artifacts, and diagrams to update dashboard fields:
- last_updated (UTC ISO)
- diagram status (present/missing)
- validation note

Does NOT advance state, approve items, or trigger agents.

Usage:
    python scripts/refresh_intro_evt_dashboard.py
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

BASE_DIR = Path(__file__).resolve().parent.parent
QUEUE_PATH = BASE_DIR / "review" / "HR_PRE_queue.json"
DASHBOARD_PATH = BASE_DIR / "dashboards" / "intro_evt_overview.json"

ARTIFACT_PATHS = {
    "PRE_CONCEPT": "artifacts/draft_concept_memo_pre_evt/PRE_CONCEPT.json",
    "INTRO_FRAME": "artifacts/draft_framing_intro_evt/INTRO_FRAME.json",
    "INTRO_WHITEPAPER": "artifacts/draft_whitepaper_intro_evt/INTRO_WHITEPAPER.json",
}

DIAGRAM_PATHS = {
    "INTRO_FRAME": "diagrams/INTRO_FRAME.mmd",
    "INTRO_WHITEPAPER": "diagrams/INTRO_WHITEPAPER.mmd",
}


def load_json(path: Path) -> Dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def refresh():
    queue = load_json(QUEUE_PATH)
    dash = load_json(DASHBOARD_PATH)

    now = datetime.now(timezone.utc).isoformat()
    dash.setdefault("_meta", {})
    dash["_meta"]["last_updated"] = now
    dash["_meta"]["note"] = "INTERNAL, NON-AUTHORITATIVE — pending HR_PRE approval"

    # Diagram status
    diagrams = []
    for name, relpath in DIAGRAM_PATHS.items():
        exists = (BASE_DIR / relpath).exists()
        diagrams.append({"name": name, "path": relpath, "status": "present" if exists else "missing"})
    dash["diagrams"] = diagrams

    # Review summary string
    pending_decisions = len([r for r in queue.get("pending_reviews", []) if r.get("decision") is None])
    active_artifacts = len([r for r in queue.get("pending_reviews", []) if r.get("status") == "ACTIVE"])
    superseded_artifacts = len([r for r in queue.get("pending_reviews", []) if r.get("status") == "SUPERSEDED"])

    dash.setdefault("review_summary", {})
    dash["review_summary"]["pending_decisions"] = pending_decisions
    dash["review_summary"]["active_artifacts"] = active_artifacts
    dash["review_summary"]["superseded_artifacts"] = superseded_artifacts
    dash["review_summary"]["review_gate_status"] = "HR_PRE pending — INTERNAL, non-authoritative"

    DASHBOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    DASHBOARD_PATH.write_text(json.dumps(dash, indent=2))
    return dash


if __name__ == "__main__":
    refresh()
