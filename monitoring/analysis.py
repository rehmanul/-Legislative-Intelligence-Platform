"""
Analysis functions for dashboard-terminal: health checks, metrics, goals, and prioritization.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple

from constants import (
    STALE_HEARTBEAT_THRESHOLD_MINUTES,
    STUCK_AGENT_THRESHOLD_MINUTES,
    MONTHLY_DAYS,
    WEEKLY_DAYS,
    URGENT_HOURS,
    ARTIFACT_AGENT_MAP,
    GATE_AGENT_MAP,
    METRICS_PATH,
    STATE_SEQUENCE,
)
from dash_types import AgentRecord, DashboardBundle, GoalData, ReviewItem
from loaders import parse_timestamp, load_json


def deduplicate_agents(agents: List[AgentRecord]) -> List[AgentRecord]:
    """Deduplicate agents by agent_id, keeping the most recent one by heartbeat."""
    seen: Dict[str, AgentRecord] = {}
    for agent in agents or []:
        agent_id = agent.get("agent_id", "unknown")
        if agent_id not in seen:
            seen[agent_id] = agent
        else:
            current_ts = parse_timestamp(agent.get("last_heartbeat", ""))
            existing_ts = parse_timestamp(seen[agent_id].get("last_heartbeat", ""))
            if current_ts and existing_ts:
                if current_ts > existing_ts:
                    seen[agent_id] = agent
            elif current_ts:
                seen[agent_id] = agent
    return list(seen.values())


def check_agent_health(agent: AgentRecord, now: datetime) -> Tuple[bool, Optional[str], float]:
    """Check if agent is healthy; returns (is_healthy, issue_type, age_seconds)."""
    status = agent.get("status", "")
    heartbeat_str = agent.get("last_heartbeat", "")
    spawned_str = agent.get("spawned_at", "")
    heartbeat_dt = parse_timestamp(heartbeat_str)
    spawned_dt = parse_timestamp(spawned_str)

    if not heartbeat_dt:
        if status == "RUNNING":
            return (False, "NO_HEARTBEAT", 0)
        return (True, None, 0)

    age_seconds = (now - heartbeat_dt).total_seconds()
    if status == "RUNNING" and age_seconds > STALE_HEARTBEAT_THRESHOLD_MINUTES * 60:
        return (False, "STALE_HEARTBEAT", age_seconds)
    if status == "RUNNING" and spawned_dt:
        running_duration = (now - spawned_dt).total_seconds()
        if running_duration > STUCK_AGENT_THRESHOLD_MINUTES * 60:
            return (False, "STUCK", running_duration)
    return (True, None, age_seconds)


def collect_metrics(bundle: DashboardBundle) -> Dict[str, Any]:
    """Collect current metrics snapshot and append to history (JSONL)."""
    now = datetime.now(timezone.utc)
    registry = bundle.get("registry", {})
    dashboard = bundle.get("dashboard", {})
    agents = deduplicate_agents(registry.get("agents", []))

    status_counts: Dict[str, int] = defaultdict(int)
    type_counts: Dict[str, int] = defaultdict(int)
    healthy_count = 0
    unhealthy_count = 0

    for agent in agents:
        status = agent.get("status", "unknown")
        agent_type = agent.get("agent_type", "unknown")
        status_counts[status] += 1
        type_counts[agent_type] += 1
        is_healthy, _, _ = check_agent_health(agent, now)
        if is_healthy:
            healthy_count += 1
        else:
            unhealthy_count += 1

    metrics: Dict[str, Any] = {
        "timestamp": now.isoformat(),
        "agents": {
            "total": len(agents),
            "healthy": healthy_count,
            "unhealthy": unhealthy_count,
            "by_status": dict(status_counts),
            "by_type": dict(type_counts),
        },
        "task_queue": dashboard.get("task_queue", {}),
        "legislative_state": bundle.get("state", {}).get("current_state", "UNKNOWN"),
        "pending_approvals": dashboard.get("pending_approvals", 0),
    }
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(METRICS_PATH, "a", encoding="utf-8") as f:
        f.write(json_dumps(metrics) + "\n")
    return metrics


def analyze_recent_activity(audit_log_path) -> Dict[str, Any]:
    """Analyze audit log for recent activity metrics (last 24 hours)."""
    if not audit_log_path.exists():
        return {}
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=24)
    event_counts: Dict[str, int] = defaultdict(int)
    agent_activity: Dict[str, int] = defaultdict(int)
    task_completions = 0
    errors = 0
    try:
        with open(audit_log_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    event = json_loads_safe(line.strip())
                    event_ts = parse_timestamp(event.get("timestamp", ""))
                    if not event_ts or event_ts < cutoff:
                        continue
                    event_type = event.get("event_type", "")
                    agent_id = event.get("agent_id", "system")
                    event_counts[event_type] += 1
                    agent_activity[agent_id] += 1
                    if event_type == "task_completed":
                        task_completions += 1
                    elif event_type in ["error", "warning"]:
                        errors += 1
                except Exception:
                    continue
    except Exception:
        return {}
    return {
        "task_completions": task_completions,
        "errors": errors,
        "event_counts": dict(event_counts),
        "most_active_agents": dict(sorted(agent_activity.items(), key=lambda x: x[1], reverse=True)[:5]),
    }


def compute_goal_progress(state: Dict[str, Any], dashboard: Dict[str, Any], goal: GoalData) -> Dict[str, Any]:
    """Compute structured progress toward the goal."""
    current_state = state.get("current_state", "UNKNOWN")
    target_state = goal.get("target_state", "UNKNOWN")
    missing_artifacts = dashboard.get("missing_artifacts", [])
    pending_gates = dashboard.get("pending_gates", [])
    required_artifacts = goal.get("required_artifacts", [])
    if not missing_artifacts and required_artifacts:
        missing_artifacts = required_artifacts.copy()
    total_artifacts = len(required_artifacts)
    remaining_artifacts = len(missing_artifacts)
    required_gates = goal.get("required_gates", [])
    total_gates = len(required_gates)
    remaining_gates = len(pending_gates)
    return {
        "current_state": current_state,
        "target_state": target_state,
        "state_complete": current_state == target_state,
        "artifacts": {
            "total": total_artifacts,
            "remaining": remaining_artifacts,
            "completed": total_artifacts - remaining_artifacts,
        },
        "gates": {
            "total": total_gates,
            "remaining": remaining_gates,
            "completed": total_gates - remaining_gates,
        },
        "blocked": remaining_artifacts > 0 or remaining_gates > 0,
        "missing_artifacts": missing_artifacts,
        "pending_gates": pending_gates,
    }


def compute_next_agents(progress: Dict[str, Any]) -> List[Dict[str, str]]:
    """Map missing artifacts and pending gates to agents that must run."""
    agents_to_run: List[Dict[str, str]] = []
    for artifact in progress.get("missing_artifacts", []):
        agent = ARTIFACT_AGENT_MAP.get(artifact)
        if agent:
            agents_to_run.append({"agent_id": agent, "reason": f"Missing artifact: {artifact}"})
    for gate in progress.get("pending_gates", []):
        agent = GATE_AGENT_MAP.get(gate)
        if agent:
            agents_to_run.append({"agent_id": agent, "reason": f"Pending review gate: {gate}"})
    return agents_to_run


def categorize_by_time_horizon(
    bundle: DashboardBundle,
    goal_progress: Optional[Dict[str, Any]] = None,
    pending_reviews: Optional[List[ReviewItem]] = None,
    execution_status: Optional[List[Dict[str, Any]]] = None,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Categorize work items by time horizon: urgent, weekly, monthly."""
    if now is None:
        now = datetime.now(timezone.utc)
    urgent: List[Dict[str, Any]] = []
    weekly: List[Dict[str, Any]] = []
    monthly: List[Dict[str, Any]] = []

    # Pending reviews
    if pending_reviews:
        for review in pending_reviews:
            submitted_at = review.get("submitted_at", "")
            if submitted_at:
                submitted_dt = parse_timestamp(submitted_at)
                if submitted_dt:
                    age_hours = (now - submitted_dt).total_seconds() / 3600
                    item = {
                        "type": "review",
                        "priority": "HIGH" if age_hours > 24 else "MEDIUM",
                        "item": review,
                        "age_hours": age_hours,
                        "description": f"Review: {review.get('artifact_name', 'Unknown')} ({review.get('gate_name', 'Unknown Gate')})",
                    }
                    if age_hours > 24 or review.get("gate_id") in ["HR_PRE", "HR_LANG"]:
                        urgent.append(item)
                    elif age_hours <= WEEKLY_DAYS * 24:
                        weekly.append(item)
                    else:
                        monthly.append(item)

    # Missing artifacts
    if goal_progress:
        for artifact in goal_progress.get("missing_artifacts", []):
            urgent.append(
                {
                    "type": "artifact",
                    "priority": "HIGH",
                    "item": artifact,
                    "description": f"Missing artifact: {artifact}",
                }
            )

    # Execution failures/retries
    if execution_status:
        for exec_item in execution_status:
            status = exec_item.get("status", "")
            if status in ["FAILED", "RETRYING"]:
                agent_id = exec_item.get("agent_id", "unknown")
                attempt = exec_item.get("attempt", 0)
                max_retries = exec_item.get("max_retries", 5)
                error = exec_item.get("error", "Unknown error")
                urgent.append(
                    {
                        "type": "execution",
                        "priority": "HIGH",
                        "item": exec_item,
                        "description": f"Execution {status.lower()}: {agent_id} (attempt {attempt}/{max_retries})",
                        "error": (error[:100] if error else None),
                    }
                )

    # Agents waiting on human
    registry = bundle.get("registry", {})
    agents = deduplicate_agents(registry.get("agents", []))
    for agent in agents:
        status = agent.get("status", "")
        if status in ["WAITING_REVIEW", "BLOCKED"]:
            agent_id = agent.get("agent_id", "unknown")
            task = agent.get("current_task", "N/A")
            heartbeat_dt = parse_timestamp(agent.get("last_heartbeat", ""))
            age_hours = (now - heartbeat_dt).total_seconds() / 3600 if heartbeat_dt else 0
            item = {
                "type": "agent",
                "priority": "HIGH" if age_hours > 24 or status == "BLOCKED" else "MEDIUM",
                "item": agent,
                "age_hours": age_hours,
                "description": f"Agent {status}: {agent_id} - {task}",
            }
            if item["priority"] == "HIGH":
                urgent.append(item)
            elif age_hours <= WEEKLY_DAYS * 24:
                weekly.append(item)

    # State advancement planning
    if goal_progress:
        current_state = goal_progress.get("current_state", "UNKNOWN")
        target_state = goal_progress.get("target_state", "UNKNOWN")
        if current_state != target_state:
            try:
                current_idx = STATE_SEQUENCE.index(current_state)
                target_idx = STATE_SEQUENCE.index(target_state)
                states_remaining = target_idx - current_idx
                estimated_weeks = states_remaining * 2
                item = {
                    "type": "state_advancement",
                    "priority": "MEDIUM",
                    "item": {"current": current_state, "target": target_state},
                    "description": f"State advancement: {current_state} → {target_state} ({states_remaining} states remaining)",
                    "estimated_weeks": estimated_weeks,
                }
                if estimated_weeks <= 1:
                    weekly.append(item)
                elif estimated_weeks <= 4:
                    monthly.append(item)
            except ValueError:
                pass

    return {
        "urgent": sorted(urgent, key=lambda x: x.get("priority", "LOW") == "HIGH", reverse=True),
        "weekly": weekly,
        "monthly": monthly,
        "summary": {
            "urgent_count": len(urgent),
            "weekly_count": len(weekly),
            "monthly_count": len(monthly),
            "total": len(urgent) + len(weekly) + len(monthly),
        },
    }


# ---------- small JSON helpers ----------

def json_dumps(obj: Any) -> str:
    import json

    return json.dumps(obj, ensure_ascii=False)


def json_loads_safe(s: str) -> Dict[str, Any]:
    import json

    try:
        return json.loads(s)
    except Exception:
        return {}

