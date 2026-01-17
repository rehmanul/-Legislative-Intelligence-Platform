"""
Shared constants and paths for the monitoring dashboard.
"""

from __future__ import annotations

import os
from pathlib import Path

# Base directories
MONITORING_DIR: Path = Path(__file__).parent
BASE_DIR: Path = MONITORING_DIR.parent

# Paths
DASHBOARD_STATUS_PATH: Path = MONITORING_DIR / "dashboard-status.json"
AGENT_REGISTRY_PATH: Path = BASE_DIR / "registry" / "agent-registry.json"
STATE_PATH: Path = BASE_DIR / "state" / "legislative-state.json"
AUDIT_LOG_PATH: Path = BASE_DIR / "audit" / "audit-log.jsonl"
METRICS_PATH: Path = MONITORING_DIR / "metrics-history.jsonl"
GOAL_PATH: Path = BASE_DIR / "goals" / "workflow-goal.json"
REVIEW_DIR: Path = BASE_DIR / "review"

# API configuration
API_BASE_URL: str = os.getenv("ORCHESTRATOR_API_URL", "http://localhost:8000")
USE_API: bool = os.getenv("DASHBOARD_USE_API", "false").lower() == "true"
WORKFLOW_ID: str | None = os.getenv("WORKFLOW_ID") or None

# Refresh intervals (seconds)
DATA_REFRESH_INTERVAL: int = 300  # 5 minutes
HEARTBEAT_INTERVAL: int = 10  # 10 seconds
METRICS_COLLECTION_INTERVAL: int = 300  # 5 minutes

# Health check thresholds (minutes)
STUCK_AGENT_THRESHOLD_MINUTES: int = 30  # Agent stuck in RUNNING > 30 min
STALE_HEARTBEAT_THRESHOLD_MINUTES: int = 15  # No heartbeat > 15 min

# Time horizon thresholds
URGENT_HOURS: int = 48  # Items requiring action within 48 hours
WEEKLY_DAYS: int = 7    # Items for this week
MONTHLY_DAYS: int = 30  # Items for this month

# State progression sequence
STATE_SEQUENCE = ["PRE_EVT", "INTRO_EVT", "COMM_EVT", "FLOOR_EVT"]

# Artifact → Agent mapping
ARTIFACT_AGENT_MAP = {
    "Concept Memo": "draft_concept_memo_pre_evt",
    "Legitimacy & Policy Framing": "draft_framing_intro_evt",
    "Policy Whitepaper": "draft_whitepaper_intro_evt",
    "Draft Legislative Language": "draft_legislative_language_comm_evt",
    "Amendment Strategy": "draft_amendment_strategy_comm_evt",
    "Committee Briefing": "draft_committee_briefing_comm_evt",
    "Floor Messaging & Talking Points": "draft_messaging_floor_evt",
    "Stakeholder Landscape Map": "intel_stakeholder_map_pre_evt",
}

# Review gate → primary agent mapping
GATE_AGENT_MAP = {
    "HR_PRE": "draft_framing_intro_evt",
    "HR_LANG": "draft_legislative_language_comm_evt",
    "HR_MSG": "draft_messaging_floor_evt",
    "HR_RELEASE": None,
}

# Known artifact file paths (subset used to verify existence)
ARTIFACT_PATHS = {
    "Legitimacy & Policy Framing": BASE_DIR / "artifacts" / "draft_framing_intro_evt" / "INTRO_FRAME.json",
    "Policy Whitepaper": BASE_DIR / "artifacts" / "draft_whitepaper_intro_evt" / "INTRO_WHITEPAPER.json",
    "Concept Memo": BASE_DIR / "artifacts" / "draft_concept_memo_pre_evt" / "PRE_CONCEPT.json",
}

