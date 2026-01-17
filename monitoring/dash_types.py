"""
Type hints and shared TypedDicts for the monitoring dashboard.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict


class AgentRecord(TypedDict, total=False):
    agent_id: str
    agent_type: str
    status: str
    scope: str
    current_task: str
    last_heartbeat: str
    risk_level: str
    outputs: List[str]
    spawned_at: str


class RegistryData(TypedDict, total=False):
    _meta: Dict[str, Any]
    agents: List[AgentRecord]


class StateData(TypedDict, total=False):
    _meta: Dict[str, Any]
    current_state: str
    state_definition: str
    next_allowed_states: List[str]


class DashboardData(TypedDict, total=False):
    overall_status: str
    pending_approvals: int
    task_queue: Dict[str, Any]
    missing_artifacts: List[str]
    pending_gates: List[str]
    blocking_issues: List[str]
    _api_enhanced: bool


class ReviewItem(TypedDict, total=False):
    review_id: str
    artifact_name: str
    artifact_path: str
    relative_path: str
    markdown_paths: List[str]
    gate_id: str
    gate_name: str
    submitted_at: str
    submitted_by: str
    review_effort_estimate: str
    risk_level: str


class GoalData(TypedDict, total=False):
    target_state: str
    required_artifacts: List[str]
    required_gates: List[str]


class ExecutionItem(TypedDict, total=False):
    agent_id: str
    status: str
    attempt: int
    max_retries: int
    retry_delay: float
    next_retry_at: str
    started_at: str
    error: str


class DashboardBundle(TypedDict, total=False):
    dashboard: DashboardData
    registry: RegistryData
    state: StateData
    execution_status: List[ExecutionItem]

