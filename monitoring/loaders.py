"""
I/O loaders for dashboard data: files and optional API.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import requests  # type: ignore
except ImportError:
    requests = None  # type: ignore

from constants import (
    API_BASE_URL,
    AUDIT_LOG_PATH,
    BASE_DIR,
    DASHBOARD_STATUS_PATH,
    REVIEW_DIR,
    STATE_PATH,
    AGENT_REGISTRY_PATH,
    GOAL_PATH,
    USE_API,
    WORKFLOW_ID,
)
from dash_types import (
    DashboardBundle,
    DashboardData,
    GoalData,
    RegistryData,
    ReviewItem,
    StateData,
    ExecutionItem,
)


# ---------- Generic helpers ----------

def load_json(path: Path) -> Dict[str, Any]:
    """Load JSON file, return {} if not found or invalid."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def parse_timestamp(ts_str: str) -> Optional[datetime]:
    """Parse ISO timestamp to datetime object."""
    if not ts_str:
        return None
    try:
        ts_str = ts_str.replace("Z", "+00:00")
        return datetime.fromisoformat(ts_str)
    except Exception:
        return None


def format_timestamp(ts_str: str) -> str:
    """Format ISO timestamp to readable format HH:MM:SS."""
    dt = parse_timestamp(ts_str)
    if dt:
        return dt.strftime("%H:%M:%S")
    return ts_str


# ---------- API loaders ----------

def load_agents_from_api(workflow_id: Optional[str]) -> Optional[RegistryData]:
    """Load agents from API if available."""
    if not USE_API or not workflow_id or requests is None:
        return None
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/workflows/{workflow_id}/agents", timeout=5)
        if response.status_code != 200:
            return None
        data = response.json()
        agents: List[Dict[str, Any]] = []
        for agent in data.get("agents", []):
            agent_dict = agent if isinstance(agent, dict) else (
                agent.model_dump() if hasattr(agent, "model_dump") else (agent.dict() if hasattr(agent, "dict") else {})
            )
            status = agent_dict.get("status", "")
            status_str = status.value if hasattr(status, "value") else str(status)

            heartbeat_at = agent_dict.get("heartbeat_at")
            if heartbeat_at:
                heartbeat_str = heartbeat_at.isoformat() + "Z" if hasattr(heartbeat_at, "isoformat") else str(heartbeat_at)
            else:
                heartbeat_str = ""

            spawned_at = agent_dict.get("spawned_at")
            if spawned_at:
                spawned_str = spawned_at.isoformat() + "Z" if hasattr(spawned_at, "isoformat") else str(spawned_at)
            else:
                spawned_str = ""

            agents.append(
                {
                    "agent_id": agent_dict.get("agent_id", ""),
                    "agent_type": agent_dict.get("agent_type", ""),
                    "status": status_str,
                    "scope": agent_dict.get("scope", ""),
                    "current_task": agent_dict.get("current_task", ""),
                    "last_heartbeat": heartbeat_str,
                    "risk_level": agent_dict.get("risk_level", "LOW"),
                    "outputs": agent_dict.get("outputs", []),
                    "spawned_at": spawned_str,
                }
            )
        return {
            "_meta": {
                "source": "api",
                "workflow_id": workflow_id,
                "total_agents": len(agents),
                "active_agents": len([a for a in agents if a.get("status") == "RUNNING"]),
            },
            "agents": agents,
        }
    except Exception:
        return None


def load_state_from_api(workflow_id: Optional[str]) -> Optional[StateData]:
    """Load state from API if available."""
    if not USE_API or requests is None:
        return None
    try:
        params: Dict[str, Any] = {}
        if workflow_id:
            params["workflow_id"] = workflow_id
        response = requests.get(f"{API_BASE_URL}/api/v1/state/current", params=params, timeout=5)
        if response.status_code != 200:
            return None
        data = response.json()
        return {
            "_meta": {
                "state_version": "1.0",
                "last_updated": datetime.now(timezone.utc).isoformat() + "Z",
                "authority": "api",
            },
            "current_state": data.get("current_state", "UNKNOWN"),
            "state_definition": data.get("state_definition", ""),
            "next_allowed_states": data.get("next_allowed_states", []),
        }
    except Exception:
        return None


def load_workflow_status_from_api(workflow_id: Optional[str]) -> Optional[Dict[str, Any]]:
    """Load workflow status from API."""
    if not USE_API or not workflow_id or requests is None:
        return None
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/workflows/{workflow_id}/status", timeout=5)
        if response.status_code != 200:
            return None
        return response.json()
    except Exception:
        return None


def load_execution_status(workflow_id: Optional[str]) -> Optional[List[ExecutionItem]]:
    """Load execution status from API."""
    if not USE_API or requests is None:
        return None
    try:
        if not workflow_id:
            return None
        url = f"{API_BASE_URL}/api/v1/workflows/{workflow_id}/agents/executions"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()  # type: ignore[return-value]
        return None
    except Exception:
        return None


# ---------- File loaders ----------

def load_goal() -> GoalData:
    """Load goal definition from file."""
    data = load_json(GOAL_PATH)
    return data  # type: ignore[return-value]


def load_pending_reviews() -> List[ReviewItem]:
    """Load all pending reviews from review queue files."""
    pending_reviews: List[ReviewItem] = []
    if not REVIEW_DIR.exists():
        return pending_reviews
    for queue_file in REVIEW_DIR.glob("*_queue.json"):
        try:
            queue_data = load_json(queue_file)
            gate_name = queue_data.get("_meta", {}).get("review_gate_name", "Unknown Gate")
            gate_id = queue_data.get("_meta", {}).get("review_gate", "UNKNOWN")
            for review in queue_data.get("pending_reviews", []):
                artifact_path = review.get("artifact_path", "")
                if artifact_path:
                    full_path = Path(artifact_path) if Path(artifact_path).is_absolute() else BASE_DIR / artifact_path
                    relative_path = artifact_path if not Path(artifact_path).is_absolute() else artifact_path
                else:
                    full_path = Path("")
                    relative_path = ""
                md_paths: List[str] = []
                if full_path and full_path.exists():
                    md_file = full_path.with_suffix(".md")
                    if md_file.exists():
                        md_paths.append(str(md_file))
                    review_md = full_path.parent / f"{full_path.stem}_REVIEW.md"
                    if review_md.exists():
                        md_paths.append(str(review_md))
                pending_reviews.append(
                    {
                        "review_id": review.get("review_id", "unknown"),
                        "artifact_name": review.get("artifact_name", "Unknown Artifact"),
                        "artifact_path": str(full_path) if str(full_path) else "",
                        "relative_path": relative_path,
                        "markdown_paths": md_paths,
                        "gate_id": gate_id,
                        "gate_name": gate_name,
                        "submitted_at": review.get("submitted_at", ""),
                        "submitted_by": review.get("submitted_by", "unknown"),
                        "review_effort_estimate": review.get("review_effort_estimate", ""),
                        "risk_level": review.get("risk_level", ""),
                    }
                )
        except Exception:
            continue
    return pending_reviews


def load_dashboard_data() -> DashboardBundle:
    """
    Load all dashboard data from files and/or API.
    Fixes prior early-return bug to ensure a single authoritative implementation.
    """
    # Determine workflow_id
    workflow_id: Optional[str] = WORKFLOW_ID
    if not workflow_id and STATE_PATH.exists():
        state_data_raw = load_json(STATE_PATH)
        workflow_id = state_data_raw.get("_meta", {}).get("workflow_id")

    # Registry (API preferred)
    registry_data: Optional[RegistryData] = None
    if USE_API and workflow_id:
        registry_data = load_agents_from_api(workflow_id)
    if not registry_data:
        registry_data = load_json(AGENT_REGISTRY_PATH) or {}
        if registry_data and USE_API:
            registry_data.setdefault("_meta", {})
            registry_data["_meta"]["source"] = "file"

    # State (API preferred)
    state_data: Optional[StateData] = None
    if USE_API:
        state_data = load_state_from_api(workflow_id)
    if not state_data:
        state_data = load_json(STATE_PATH) or {}
        if state_data and USE_API:
            state_data.setdefault("_meta", {})
            state_data["_meta"]["source"] = "file"

    # Dashboard status (file)
    dashboard_data: DashboardData = load_json(DASHBOARD_STATUS_PATH) or {}

    # Enhance from API workflow status
    if USE_API and workflow_id:
        workflow_status = load_workflow_status_from_api(workflow_id)
        if workflow_status:
            dashboard_data["pending_approvals"] = len(workflow_status.get("pending_gates", []))
            dashboard_data["can_advance"] = workflow_status.get("can_advance", False)  # type: ignore[assignment]
            dashboard_data["blocking_issues"] = workflow_status.get("blocking_issues", [])  # type: ignore[assignment]
            dashboard_data["_api_enhanced"] = True  # type: ignore[assignment]

    # Execution status (API only)
    execution_status = load_execution_status(workflow_id) if USE_API and workflow_id else None

    return {
        "dashboard": dashboard_data,
        "registry": registry_data or {},
        "state": state_data or {},
        "execution_status": execution_status or [],
    }

