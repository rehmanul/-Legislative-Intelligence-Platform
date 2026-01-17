"""
Terminal rendering for the human-review dashboard.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from constants import (
    AUDIT_LOG_PATH,
    ARTIFACT_AGENT_MAP,
    ARTIFACT_PATHS,
)
from analysis import (
    deduplicate_agents,
    categorize_by_time_horizon,
)
from loaders import parse_timestamp
from dash_types import DashboardBundle, ReviewItem


def format_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds // 60)}m {int(seconds % 60)}s"
    hours = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    return f"{hours}h {mins}m"


def format_countdown(seconds: int) -> str:
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins:02d}:{secs:02d}"


def translate_state_to_meaning(state_code: str) -> str:
    """Translate state code to human-readable meaning (enhanced with subtitles)"""
    # Import enhanced state descriptions
    try:
        from monitoring.state_descriptions import get_state_description
        desc = get_state_description(state_code)
        return f"{desc['subtitle']}: {desc['description']}"
    except ImportError:
        # Fallback to original if module not available
        meanings = {
            "PRE_EVT": "Policy Opportunity Phase: Preparing concept and initial intelligence gathering",
            "INTRO_EVT": "Bill Vehicle Phase: Shaping legitimacy and framing. No outreach or execution has begun.",
            "COMM_EVT": "Committee Phase: Committee engagement phase. Drafting language and building support.",
            "FLOOR_EVT": "Floor Activity Phase: Floor action phase. Messaging and vote coordination.",
            "FINAL_EVT": "Vote Phase: Final passage phase. Final vote coordination, constituent narrative development, and release authorization.",
            "IMPL_EVT": "Implementation Phase: Implementation and oversight phase. Monitoring implementation, tracking outcomes, and learning from execution.",
            "UNKNOWN": "State unknown",
        }
        return meanings.get(state_code, f"State: {state_code}")


def get_artifact_purpose(artifact_name: str) -> str:
    purposes = {
        "Legitimacy & Policy Framing": "Articulates legitimacy, narrative framing, and policy justification for sponsor targeting",
        "Policy Whitepaper": "Academic and technical validation document for policy approach",
        "Concept Memo": "Initial concept direction and strategic approach",
        "Draft Legislative Language": "Actual bill language for committee consideration",
        "Amendment Strategy": "Strategy for amendments and modifications",
        "Committee Briefing": "Briefing materials for committee members",
        "Floor Messaging & Talking Points": "Messaging for floor debate and vote coordination",
    }
    return purposes.get(artifact_name, "Purpose not documented")


def get_time_since_progress(agents: List[Dict[str, Any]], now: datetime) -> str:
    last_progress: Optional[datetime] = None
    for agent in agents:
        if agent.get("status") in ["IDLE", "WAITING_REVIEW"]:
            heartbeat_str = agent.get("last_heartbeat", "")
            heartbeat_dt = parse_timestamp(heartbeat_str)
            if heartbeat_dt:
                if last_progress is None or heartbeat_dt > last_progress:
                    last_progress = heartbeat_dt
    if last_progress:
        age_seconds = (now - last_progress).total_seconds()
        if age_seconds < 3600:
            return f"{int(age_seconds // 60)} minutes ago"
        elif age_seconds < 86400:
            return f"{int(age_seconds // 3600)} hours ago"
        else:
            return f"{int(age_seconds // 86400)} days ago"
    return "Unknown"


def render_dashboard(
    bundle: DashboardBundle,
    seconds_until_refresh: int,
    metrics: Optional[Dict[str, Any]] = None,
    activity: Optional[Dict[str, Any]] = None,
    goal_progress: Optional[Dict[str, Any]] = None,
    next_agents: Optional[List[Dict[str, str]]] = None,
    pending_reviews: Optional[List[ReviewItem]] = None,
    execution_status: Optional[List[Dict[str, Any]]] = None,
    first_render: bool = False,
) -> None:
    """Render the human-review focused dashboard."""
    if first_render:
        os.system("cls" if os.name == "nt" else "clear")
        sys.stdout.flush()

    dashboard = bundle.get("dashboard", {})
    registry = bundle.get("registry", {})
    state = bundle.get("state", {})
    now = datetime.now(timezone.utc)

    agents = deduplicate_agents(registry.get("agents", []))

    print("=" * 80)
    print("HUMAN-REVIEW DASHBOARD")
    print("=" * 80)

    overall_status = dashboard.get("overall_status", "UNKNOWN")
    state_cursor = state.get("current_state", "UNKNOWN")
    time_horizons = categorize_by_time_horizon(bundle, goal_progress, pending_reviews, execution_status, now)

    if overall_status == "WAITING_REVIEW":
        health_status = "System is healthy but paused awaiting human review."
    elif overall_status == "DEGRADED":
        health_status = "System is degraded. Some agents may need attention."
    elif overall_status == "FAILING":
        health_status = "System is failing. Immediate attention required."
    else:
        health_status = "System is healthy and operating normally."

    if goal_progress and goal_progress.get("blocked"):
        missing_artifacts = goal_progress.get("missing_artifacts", [])
        reason = f"Missing required artifacts: {', '.join(missing_artifacts[:2])}" if missing_artifacts else "Awaiting human review or state advancement"
    else:
        reason = "No blockers detected"

    time_since = get_time_since_progress(agents, now)

    print(f"\n🟢 SYSTEM HEALTH SUMMARY")
    print("-" * 80)
    print(f"Health: {health_status}")
    print(f"Primary reason: {reason}")
    print(f"Last meaningful progress: {time_since}")
    print(f"Current phase: {translate_state_to_meaning(state_cursor)}")

    summary = time_horizons.get("summary", {})
    print(f"\n⏰ TIME HORIZON SUMMARY")
    print(f"  Urgent (next 48h): {summary.get('urgent_count', 0)} items")
    print(f"  This Week: {summary.get('weekly_count', 0)} items")
    print(f"  This Month: {summary.get('monthly_count', 0)} items")

    print(f"\n🟡 HUMAN DECISION REQUIRED")
    print("-" * 80)
    human_action_needed = False
    if pending_reviews:
        human_action_needed = True
        for review in pending_reviews:
            artifact_name = review.get("artifact_name", "Unknown Artifact")
            gate_name = review.get("gate_name", "Unknown Gate")
            gate_id = review.get("gate_id", "UNKNOWN")
            print(f"\nREQUIRED HUMAN ACTION:")
            print(f"  • Review: {artifact_name}")
            print(f"  • Purpose: {get_artifact_purpose(artifact_name)}")
            print(f"  • Gate: {gate_name} ({gate_id})")
            if gate_id == "HR_PRE":
                print("  • Unlocks: State advancement to COMM_EVT and drafting agents")
            elif gate_id == "HR_LANG":
                print("  • Unlocks: Committee engagement and amendment strategy")
            elif gate_id == "HR_MSG":
                print("  • Unlocks: Floor messaging and vote coordination")
            else:
                print("  • Unlocks: Next phase activities")
            print("  • If ignored: Workflow remains blocked, no state advancement")
            print(f"  • File: {review.get('artifact_path', 'Path not available')}")

    blocked_agents = [a for a in agents if a.get("status") == "BLOCKED"]
    if blocked_agents:
        human_action_needed = True
        for agent in blocked_agents:
            agent_id = agent.get("agent_id", "unknown")
            task = agent.get("current_task", "Blocked")
            print(f"\nREQUIRED HUMAN ACTION:")
            print(f"  • Agent: {agent_id}")
            print(f"  • Status: {task}")
            print(f"  • Action: Authorization required to proceed")
    if not human_action_needed:
        print("✅ No human action required at this time.")

    print(f"\n🧭 STATE PROGRESSION MAP")
    print("-" * 80)
    state_sequence = ["PRE_EVT", "INTRO_EVT", "COMM_EVT", "FLOOR_EVT"]
    current_state = state.get("current_state", "UNKNOWN")
    target_state = goal_progress.get("target_state", "UNKNOWN") if goal_progress else "UNKNOWN"
    try:
        current_idx = state_sequence.index(current_state)
        target_idx = state_sequence.index(target_state) if target_state in state_sequence else current_idx
        for i, s in enumerate(state_sequence):
            marker = "✓" if i <= current_idx else ("→" if i == current_idx + 1 else " ")
            print(f"  {marker} {s}: {translate_state_to_meaning(s)}")
    except ValueError:
        print(f"  Current: {current_state}")
        print(f"  Target: {target_state}")

    print(f"\n📦 ARTIFACT COMPLETENESS")
    print("-" * 80)
    if goal_progress:
        required_artifacts = goal_progress.get("missing_artifacts", [])
        agents_map = {a.get("agent_id"): a for a in agents}
        if required_artifacts:
            print("Required (Missing):")
            for artifact in required_artifacts:
                agent_id = ARTIFACT_AGENT_MAP.get(artifact, "unknown")
                agent = agents_map.get(agent_id)
                status = agent.get("status", "UNKNOWN") if agent else "NOT_STARTED"
                file_path = ARTIFACT_PATHS.get(artifact)
                exists = file_path.exists() if file_path else False
                print(f"  • {artifact}")
                print(f"    Purpose: {get_artifact_purpose(artifact)}")
                print(f"    Owning agent: {agent_id}")
                if exists:
                    print("    Status: File exists, may be awaiting review")
                elif status == "RETIRED":
                    print("    Status: Agent retired (artifact not generated)")
                elif status == "WAITING_REVIEW":
                    print("    Status: Agent reports generated, but file not found")
                else:
                    print("    Status: Not yet generated")
                print()
        else:
            print("All required artifacts are present or generated.")
        completed_artifacts = []
        for artifact_name, file_path in ARTIFACT_PATHS.items():
            if file_path.exists() and artifact_name not in required_artifacts:
                completed_artifacts.append(artifact_name)
        if completed_artifacts:
            print("Generated:")
            for artifact in completed_artifacts:
                print(f"  ✓ {artifact}")
    
    # Policy Artifacts (READ-ONLY CONTEXT)
    POLICY_DIR = BASE_DIR / "artifacts" / "policy"
    if POLICY_DIR.exists():
        policy_files = list(POLICY_DIR.glob("*.md"))
        policy_docs = [f for f in policy_files if f.name not in [
            "README.md", "INDEX.md", "QUICK_REFERENCE.md", "REVIEW_CHECKLIST.md", 
            "IMPLEMENTATION_SUMMARY.md", "COMPLETION_SUMMARY.md", "AGENT_INTEGRATION_GUIDE.md",
            "INTEGRATION_COMPLETE.md"
        ]]
        
        if policy_docs:
            print(f"\n📋 POLICY ARTIFACTS (READ-ONLY CONTEXT)")
            print("-" * 80)
            print(f"Available: {len(policy_docs)} policy documents")
            print("Location: artifacts/policy/")
            print("Status: READ-ONLY POLICY CONTEXT")
            print("\nDocuments:")
            for doc in sorted(policy_docs)[:5]:  # Show first 5
                print(f"  • {doc.stem}")
            if len(policy_docs) > 5:
                print(f"  ... and {len(policy_docs) - 5} more")
            print(f"\nQuick Access: artifacts/policy/QUICK_REFERENCE.md")

    if execution_status:
        print(f"\n⚙️ EXECUTION STATUS")
        print("-" * 80)
        running_executions = [e for e in execution_status if e.get("status") == "RUNNING"]
        retrying_executions = [e for e in execution_status if e.get("status") == "RETRYING"]
        failed_executions = [e for e in execution_status if e.get("status") == "FAILED"]
        completed_executions = [e for e in execution_status if e.get("status") == "COMPLETED"]
        pending_executions = [e for e in execution_status if e.get("status") == "PENDING"]
        if running_executions:
            print(f"Running ({len(running_executions)}):")
            for exec in running_executions[:5]:
                agent_id = exec.get("agent_id", "unknown")
                attempt = exec.get("attempt", 0)
                max_retries = exec.get("max_retries", 5)
                started_at = exec.get("started_at")
                if started_at:
                    dt = parse_timestamp(started_at)
                    if dt:
                        running_time = (now - dt).total_seconds()
                        print(f"  • {agent_id} (attempt {attempt}/{max_retries}, running {format_duration(running_time)})")
                    else:
                        print(f"  • {agent_id} (attempt {attempt}/{max_retries})")
                else:
                    print(f"  • {agent_id} (attempt {attempt}/{max_retries})")
            if len(running_executions) > 5:
                print(f"  ... and {len(running_executions) - 5} more")
        if retrying_executions:
            print(f"\nRetrying ({len(retrying_executions)}):")
            for exec in retrying_executions[:5]:
                agent_id = exec.get("agent_id", "unknown")
                attempt = exec.get("attempt", 0)
                max_retries = exec.get("max_retries", 5)
                retry_delay = exec.get("retry_delay", 0)
                next_retry_at = exec.get("next_retry_at")
                error = exec.get("error", "Unknown error")
                if next_retry_at:
                    dt = parse_timestamp(next_retry_at)
                    if dt:
                        time_until = (dt - now).total_seconds()
                        if time_until > 0:
                            print(f"  • {agent_id} (attempt {attempt}/{max_retries}, retry in {format_duration(time_until)})")
                        else:
                            print(f"  • {agent_id} (attempt {attempt}/{max_retries}, retry pending)")
                    else:
                        print(f"  • {agent_id} (attempt {attempt}/{max_retries}, delay {retry_delay:.1f}s)")
                else:
                    print(f"  • {agent_id} (attempt {attempt}/{max_retries}, delay {retry_delay:.1f}s)")
                if error:
                    print(f"    Error: {error[:60]}...")
            if len(retrying_executions) > 5:
                print(f"  ... and {len(retrying_executions) - 5} more")
        if failed_executions:
            print(f"\nFailed ({len(failed_executions)}):")
            for exec in failed_executions[:3]:
                agent_id = exec.get("agent_id", "unknown")
                attempt = exec.get("attempt", 0)
                error = exec.get("error", "Unknown error")
                print(f"  • {agent_id} (failed after {attempt} attempts)")
                if error:
                    print(f"    Error: {error[:60]}...")
            if len(failed_executions) > 3:
                print(f"  ... and {len(failed_executions) - 3} more")
        if pending_executions:
            print(f"\nPending ({len(pending_executions)}):")
            for exec in pending_executions[:3]:
                agent_id = exec.get("agent_id", "unknown")
                print(f"  • {agent_id}")
            if len(pending_executions) > 3:
                print(f"  ... and {len(pending_executions) - 3} more")
        total_executions = len(execution_status)
        if total_executions > 0:
            success_rate = len(completed_executions) / total_executions * 100
            print(f"\nSummary: {total_executions} total, {len(completed_executions)} completed ({success_rate:.0f}% success)")

    print(f"\n🤖 AGENT LIFECYCLE STATUS")
    print("-" * 80)
    active_agents = [a for a in agents if a.get("status") == "RUNNING"]
    waiting_agents = [a for a in agents if a.get("status") in ["WAITING_REVIEW", "BLOCKED"]]
    retired_normal = [a for a in agents if a.get("status") == "RETIRED" and "Auto-retired" not in a.get("current_task", "")]
    retired_abnormal = [a for a in agents if a.get("status") == "RETIRED" and "Auto-retired" in a.get("current_task", "")]
    idle_agents = [a for a in agents if a.get("status") == "IDLE"]
    if active_agents:
        print("\nActive (Running):")
        for agent in active_agents:
            agent_id = agent.get("agent_id", "unknown")
            task = agent.get("current_task", "N/A")
            print(f"  • {agent_id}: {task}")
    if waiting_agents:
        print("\nWaiting on Human:")
        for agent in waiting_agents:
            agent_id = agent.get("agent_id", "unknown")
            status = agent.get("status", "unknown")
            task = agent.get("current_task", "N/A")
            print(f"  • {agent_id} ({status}): {task}")
    if retired_normal:
        print("\nRetired (Normal Completion):")
        for agent in retired_normal[:5]:
            agent_id = agent.get("agent_id", "unknown")
            print(f"  • {agent_id}: Auto-retired after task completion (normal)")
    if retired_abnormal:
        print("\nRetired (Stale/Abnormal):")
        for agent in retired_abnormal:
            agent_id = agent.get("agent_id", "unknown")
            task = agent.get("current_task", "N/A")
            print(f"  • {agent_id}: {task}")
    if idle_agents:
        print("\nIdle (Task Complete):")
        for agent in idle_agents[:3]:
            agent_id = agent.get("agent_id", "unknown")
            print(f"  • {agent_id}: Task completed, agent idle")

    print(f"\n📝 RECENT EVENTS")
    print("-" * 80)
    try:
        if AUDIT_LOG_PATH.exists():
            with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as f:
                lines = f.readlines()
                recent_events: List[str] = []
                for line in lines[-5:]:
                    try:
                        import json

                        event = json.loads(line.strip())
                        event_type = event.get("event_type", "unknown")
                        timestamp = event.get("timestamp", "")
                        timestamp_fmt = parse_timestamp(timestamp).strftime("%H:%M:%S") if parse_timestamp(timestamp) else timestamp
                        agent_id = event.get("agent_id", "system")
                        event_translations = {
                            "task_completed": "Task completed",
                            "agent_retired": "Agent retired",
                            "agent_spawned": "Agent started",
                            "task_started": "Task started",
                            "error": "Error occurred",
                        }
                        event_desc = event_translations.get(event_type, event_type)
                        recent_events.append(f"  {timestamp_fmt} | {event_desc} | {agent_id}")
                    except Exception:
                        continue
                if recent_events:
                    for event_line in recent_events:
                        print(event_line)
                else:
                    print("  No recent events")
        else:
            print("  Event log not available")
    except Exception:
        print("  Unable to read events")

    urgent_items = time_horizons.get("urgent", [])
    if urgent_items:
        print(f"\n🚨 URGENT (Next 48 Hours)")
        print("-" * 80)
        for item in urgent_items[:5]:
            print(f"  • {item.get('description', 'Unknown item')}")
            if item.get("age_hours"):
                print(f"    Age: {item['age_hours']:.1f} hours")
            if item.get("error"):
                print(f"    Error: {item['error']}")
        if len(urgent_items) > 5:
            print(f"  ... and {len(urgent_items) - 5} more urgent items")

    if retired_normal or retired_abnormal or idle_agents:
        print(f"\n🚦 SAFE TO IGNORE")
        print("-" * 80)
        print("These agents are retired or idle and require no action:")
        all_retired = retired_normal + retired_abnormal
        for agent in all_retired[:5]:
            agent_id = agent.get("agent_id", "unknown")
            print(f"  • {agent_id}")
        if len(all_retired) > 5:
            print(f"  ... and {len(all_retired) - 5} more")

    print("\n" + "=" * 80)
    print(f"Next refresh in: {format_countdown(seconds_until_refresh)} | Press Ctrl+C to stop")
    print("=" * 80)
    sys.stdout.flush()

