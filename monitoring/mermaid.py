"""
Mermaid diagram generation and saving for the dashboard.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pathlib import Path

from constants import BASE_DIR, ARTIFACT_AGENT_MAP, ARTIFACT_PATHS
from analysis import deduplicate_agents
from dash_types import DashboardBundle, ReviewItem


def generate_mermaid_chart(bundle: DashboardBundle, goal_progress: Optional[Dict[str, Any]] = None, pending_reviews: Optional[List[ReviewItem]] = None) -> str:
    dashboard = bundle.get("dashboard", {})
    registry = bundle.get("registry", {})
    state = bundle.get("state", {})
    agents = deduplicate_agents(registry.get("agents", []))
    current_state = state.get("current_state", "UNKNOWN")
    target_state = goal_progress.get("target_state", "UNKNOWN") if goal_progress else "UNKNOWN"
    overall_status = dashboard.get("overall_status", "UNKNOWN")

    missing_artifacts = goal_progress.get("missing_artifacts", []) if goal_progress else []
    completed_artifacts: List[str] = []
    for artifact_name, file_path in ARTIFACT_PATHS.items():
        if file_path.exists() and artifact_name not in missing_artifacts:
            completed_artifacts.append(artifact_name)

    active_agents = [a for a in agents if a.get("status") == "RUNNING"]
    waiting_agents = [a for a in agents if a.get("status") in ["WAITING_REVIEW", "BLOCKED"]]
    retired_agents = [a for a in agents if a.get("status") == "RETIRED"]

    lines: List[str] = []
    lines.append("---")
    lines.append("config:")
    lines.append("  layout: dagre")
    lines.append("  theme: default")
    lines.append("---")
    lines.append("flowchart TB")
    lines.append("")

    health_color = "🟢" if overall_status in ["OK", "HEALTHY"] else ("🟡" if overall_status == "WAITING_REVIEW" else "🔴")
    lines.append(f'STATUS["{health_color} System Status: {overall_status}"]:::status')
    lines.append("")

    lines.append('subgraph STATES["📜 State Progression"]')
    lines.append("direction LR")
    state_sequence = ["PRE_EVT", "INTRO_EVT", "COMM_EVT", "FLOOR_EVT"]
    state_nodes: List[str] = []
    for s in state_sequence:
        if s == current_state:
            lines.append(f'  {s}(("{s}<br/>CURRENT")):::current')
        elif s == target_state:
            lines.append(f'  {s}(("{s}<br/>TARGET")):::target')
        else:
            lines.append(f'  {s}(("{s}")):::state')
        state_nodes.append(s)
    lines.append("end")
    lines.append("")

    lines.append('subgraph ARTIFACTS["📦 Artifacts"]')
    lines.append("direction TB")
    for artifact_name in ["Concept Memo", "Legitimacy & Policy Framing", "Policy Whitepaper"]:
        node_id = artifact_name.replace(" ", "_").replace("&", "and")
        if artifact_name in completed_artifacts:
            lines.append(f'  {node_id}["✓ {artifact_name}"]:::complete')
        elif artifact_name in missing_artifacts:
            lines.append(f'  {node_id}["✗ {artifact_name}"]:::missing')
        else:
            lines.append(f'  {node_id}["○ {artifact_name}"]:::pending')
    lines.append("end")
    lines.append("")

    lines.append('subgraph AGENTS["🤖 Agents"]')
    lines.append("direction TB")
    if active_agents:
        lines.append('  subgraph ACTIVE["Active"]')
        for agent in active_agents[:5]:
            agent_id = agent.get("agent_id", "unknown").replace("-", "_")
            task = agent.get("current_task", "N/A")[:30]
            lines.append(f'    {agent_id}["🟢 {agent_id}<br/>{task}"]:::active')
        lines.append("  end")
    if waiting_agents:
        lines.append('  subgraph WAITING["Waiting on Human"]')
        for agent in waiting_agents:
            agent_id = agent.get("agent_id", "unknown").replace("-", "_")
            status = agent.get("status", "unknown")
            lines.append(f'    {agent_id}["🟡 {agent_id}<br/>{status}"]:::waiting')
        lines.append("  end")
    if retired_agents:
        lines.append('  subgraph RETIRED["Retired"]')
        for agent in retired_agents[:5]:
            agent_id = agent.get("agent_id", "unknown").replace("-", "_")
            lines.append(f'    {agent_id}["⚫ {agent_id}"]:::retired')
        lines.append("  end")
    lines.append("end")
    lines.append("")

    if pending_reviews:
        lines.append('subgraph GATES["🔺 Human Decision Gates"]')
        lines.append("direction TB")
        for review in pending_reviews:
            gate_id = review.get("gate_id", "UNKNOWN").replace("-", "_")
            gate_name = review.get("gate_name", "Unknown Gate")
            artifact_name = review.get("artifact_name", "Unknown")[:30]
            lines.append(f'  {gate_id}{{"{gate_name}<br/>{artifact_name}"}}:::gate')
        lines.append("end")
        lines.append("")

    lines.append("STATUS --> STATES")
    for i in range(len(state_nodes) - 1):
        lines.append(f"{state_nodes[i]} --> {state_nodes[i+1]}")
    if current_state == "INTRO_EVT":
        lines.append("INTRO_EVT --> ARTIFACTS")
    for artifact_name in ["Legitimacy & Policy Framing", "Policy Whitepaper"]:
        agent_id = ARTIFACT_AGENT_MAP.get(artifact_name, "").replace("-", "_")
        artifact_node = artifact_name.replace(" ", "_").replace("&", "and")
        if agent_id and any(a.get('agent_id') == ARTIFACT_AGENT_MAP.get(artifact_name) for a in agents):
            lines.append(f"{agent_id} --> {artifact_node}")
    if pending_reviews:
        for review in pending_reviews:
            gate_id = review.get("gate_id", "UNKNOWN").replace("-", "_")
            artifact_name = review.get("artifact_name", "")
            if artifact_name:
                artifact_node = artifact_name.replace(" ", "_").replace("&", "and")
                lines.append(f"{artifact_node} --> {gate_id}")

    lines.append("")
    lines.append("classDef status fill:#E0F2FE,stroke:#0369A1,stroke-width:3px")
    lines.append("classDef current fill:#FEF3C7,stroke:#92400E,stroke-width:3px")
    lines.append("classDef target fill:#D1FAE5,stroke:#065F46,stroke-width:2px")
    lines.append("classDef state fill:#F3F4F6,stroke:#6B7280,stroke-width:2px")
    lines.append("classDef complete fill:#D1FAE5,stroke:#065F46,stroke-width:2px")
    lines.append("classDef missing fill:#FEE2E2,stroke:#991B1B,stroke-width:2px")
    lines.append("classDef pending fill:#FEF3C7,stroke:#92400E,stroke-width:2px")
    lines.append("classDef active fill:#DBEAFE,stroke:#1E40AF,stroke-width:2px")
    lines.append("classDef waiting fill:#FEF3C7,stroke:#92400E,stroke-width:3px")
    lines.append("classDef retired fill:#E5E7EB,stroke:#6B7280,stroke-width:1px")
    lines.append("classDef gate fill:#FEE2E2,stroke:#991B1B,stroke-width:3px")
    return "\n".join(lines)


def save_mermaid_chart(chart_content: str, output_path: Optional[Path] = None) -> Path:
    if output_path is None:
        output_path = BASE_DIR / "monitoring" / "dashboard-status.mmd"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(chart_content)
    print(f"[INFO] Mermaid chart saved to: {output_path}")
    return output_path

