"""
Terminal Dashboard for Agent Health Monitoring (24/7 Enhanced)
Runs inside Cursor terminal, refreshes data every 5 minutes, updates display every 10 seconds
Tracks historical metrics, detects stuck agents, and provides performance analytics
"""

import json
import time
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import defaultdict

try:
    import requests  # type: ignore
except ImportError:
    requests = None  # type: ignore  # Graceful fallback if requests is not installed

# Add app directory to path for API imports
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / "app"))

DASHBOARD_STATUS_PATH = Path(__file__).parent / "dashboard-status.json"
AGENT_REGISTRY_PATH = Path(__file__).parent.parent / "registry" / "agent-registry.json"
STATE_PATH = Path(__file__).parent.parent / "state" / "legislative-state.json"
AUDIT_LOG_PATH = Path(__file__).parent.parent / "audit" / "audit-log.jsonl"
METRICS_PATH = Path(__file__).parent / "metrics-history.jsonl"
GOAL_PATH = Path(__file__).parent.parent / "goals" / "workflow-goal.json"
REVIEW_DIR = Path(__file__).parent.parent / "review"

# API Configuration
API_BASE_URL = os.getenv("ORCHESTRATOR_API_URL", "http://localhost:8000")
USE_API = os.getenv("DASHBOARD_USE_API", "false").lower() == "true"
WORKFLOW_ID = os.getenv("WORKFLOW_ID")  # Optional workflow ID for API mode

# Refresh intervals
DATA_REFRESH_INTERVAL = 300  # 5 minutes
HEARTBEAT_INTERVAL = 10  # 10 seconds
METRICS_COLLECTION_INTERVAL = 300  # 5 minutes (same as data refresh)

# Health check thresholds
STUCK_AGENT_THRESHOLD_MINUTES = 30  # Agent stuck in RUNNING > 30 min
STALE_HEARTBEAT_THRESHOLD_MINUTES = 15  # No heartbeat > 15 min

def load_json(path):
    """Load JSON file, return empty dict if not found"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def parse_timestamp(ts_str):
    """Parse ISO timestamp to datetime object"""
    try:
        # Handle both Z and +00:00 formats
        ts_str = ts_str.replace('Z', '+00:00')
        return datetime.fromisoformat(ts_str)
    except:
        return None

def format_timestamp(ts_str):
    """Format ISO timestamp to readable format"""
    dt = parse_timestamp(ts_str)
    if dt:
        return dt.strftime("%H:%M:%S")
    return ts_str

def format_duration(seconds):
    """Format seconds into human-readable duration"""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds // 60)}m {int(seconds % 60)}s"
    else:
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        return f"{hours}h {mins}m"

def format_countdown(seconds):
    """Format seconds into MM:SS countdown"""
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins:02d}:{secs:02d}"

def get_status_color(status):
    """Return status indicator"""
    colors = {
        "OK": "🟢",
        "DEGRADED": "🟡",
        "FAILING": "🔴",
        "RUNNING": "🟢",
        "IDLE": "⚪",
        "BLOCKED": "🟡",
        "WAITING_REVIEW": "🟡",
        "FAILED": "🔴",
        "RETIRED": "⚫"
    }
    return colors.get(status, "⚪")

def deduplicate_agents(agents):
    """Deduplicate agents by agent_id, keeping the most recent one"""
    seen = {}
    for agent in agents:
        agent_id = agent.get("agent_id", "unknown")
        if agent_id not in seen:
            seen[agent_id] = agent
        else:
            # Compare timestamps to keep most recent
            current_ts = parse_timestamp(agent.get("last_heartbeat", ""))
            existing_ts = parse_timestamp(seen[agent_id].get("last_heartbeat", ""))
            
            if current_ts and existing_ts:
                if current_ts > existing_ts:
                    seen[agent_id] = agent
            elif current_ts:
                seen[agent_id] = agent
            # Otherwise keep existing
    return list(seen.values())

def check_agent_health(agent, now):
    """Check if agent is healthy, return (is_healthy, issue_type, age_seconds)"""
    status = agent.get("status", "")
    heartbeat_str = agent.get("last_heartbeat", "")
    spawned_str = agent.get("spawned_at", "")
    
    heartbeat_dt = parse_timestamp(heartbeat_str)
    spawned_dt = parse_timestamp(spawned_str)
    
    if not heartbeat_dt:
        # Only flag missing heartbeat for RUNNING agents
        if status == "RUNNING":
            return (False, "NO_HEARTBEAT", 0)
        return (True, None, 0)  # IDLE/other statuses don't need heartbeats
    
    age_seconds = (now - heartbeat_dt).total_seconds()
    
    # Only check for stale heartbeat on RUNNING agents
    # IDLE, WAITING_REVIEW, BLOCKED agents don't need frequent heartbeats
    if status == "RUNNING":
        if age_seconds > STALE_HEARTBEAT_THRESHOLD_MINUTES * 60:
            return (False, "STALE_HEARTBEAT", age_seconds)
    
    # Check for stuck agent (RUNNING too long)
    if status == "RUNNING" and spawned_dt:
        running_duration = (now - spawned_dt).total_seconds()
        if running_duration > STUCK_AGENT_THRESHOLD_MINUTES * 60:
            return (False, "STUCK", running_duration)
    
    return (True, None, age_seconds)

def collect_metrics(data):
    """Collect current metrics snapshot and append to history"""
    now = datetime.now(timezone.utc)
    registry = data["registry"]
    dashboard = data["dashboard"]
    
    agents = deduplicate_agents(registry.get("agents", []))
    
    # Count agents by status
    status_counts = defaultdict(int)
    type_counts = defaultdict(int)
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
    
    # Collect metrics
    metrics = {
        "timestamp": now.isoformat(),
        "agents": {
            "total": len(agents),
            "healthy": healthy_count,
            "unhealthy": unhealthy_count,
            "by_status": dict(status_counts),
            "by_type": dict(type_counts)
        },
        "task_queue": dashboard.get("task_queue", {}),
        "legislative_state": data["state"].get("current_state", "UNKNOWN"),
        "pending_approvals": dashboard.get("pending_approvals", 0)
    }
    
    # Append to metrics history (JSONL format)
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(METRICS_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(metrics) + '\n')
    
    return metrics

def analyze_recent_activity(hours=24):
    """Analyze audit log for recent activity metrics"""
    if not AUDIT_LOG_PATH.exists():
        return {}
    
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=hours)
    
    event_counts = defaultdict(int)
    agent_activity = defaultdict(int)
    task_completions = 0
    errors = 0
    
    try:
        with open(AUDIT_LOG_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    event = json.loads(line.strip())
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
                except:
                    pass
    except:
        pass
    
    return {
        "task_completions": task_completions,
        "errors": errors,
        "event_counts": dict(event_counts),
        "most_active_agents": dict(sorted(agent_activity.items(), key=lambda x: x[1], reverse=True)[:5])
    }

def load_goal():
    """Load goal definition from file"""
    return load_json(GOAL_PATH)

def compute_goal_progress(state, dashboard, goal):
    """
    Returns structured progress toward the goal.
    """
    current_state = state.get("current_state", "UNKNOWN")
    target_state = goal.get("target_state", "UNKNOWN")
    
    # Get missing artifacts and pending gates from dashboard
    # These should be populated by the orchestrator
    missing_artifacts = dashboard.get("missing_artifacts", [])
    pending_gates = dashboard.get("pending_gates", [])
    
    # If not in dashboard, try to infer from required artifacts
    required_artifacts = goal.get("required_artifacts", [])
    if not missing_artifacts and required_artifacts:
        # For now, assume all are missing if not specified
        # In production, this would check actual artifact status
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
            "completed": total_artifacts - remaining_artifacts
        },
        "gates": {
            "total": total_gates,
            "remaining": remaining_gates,
            "completed": total_gates - remaining_gates
        },
        "blocked": remaining_artifacts > 0 or remaining_gates > 0,
        "missing_artifacts": missing_artifacts,
        "pending_gates": pending_gates
    }

# Mapping from artifact names to agent IDs that produce them
ARTIFACT_AGENT_MAP = {
    "Concept Memo": "draft_concept_memo_pre_evt",
    "Legitimacy & Policy Framing": "draft_framing_intro_evt",
    "Policy Whitepaper": "draft_whitepaper_intro_evt",
    "Draft Legislative Language": "draft_legislative_language_comm_evt",
    "Amendment Strategy": "draft_amendment_strategy_comm_evt",
    "Committee Briefing": "draft_committee_briefing_comm_evt",
    "Floor Messaging & Talking Points": "draft_messaging_floor_evt",
    "Stakeholder Landscape Map": "intel_stakeholder_map_pre_evt",  # Can be pre/intro/comm_evt variants
}

# Mapping from review gate IDs to primary agent IDs that produce artifacts for that gate
# Note: Gates review artifacts, so this maps to agents that produce artifacts requiring that gate
GATE_AGENT_MAP = {
    "HR_PRE": "draft_framing_intro_evt",  # Primary agent for HR_PRE in INTRO_EVT
    "HR_LANG": "draft_legislative_language_comm_evt",
    "HR_MSG": "draft_messaging_floor_evt",
    "HR_RELEASE": None,  # No specific agent for final release gate
}

def compute_next_agents(progress):
    """Map missing artifacts and pending gates to agents that must run"""
    agents_to_run = []
    
    for artifact in progress.get("missing_artifacts", []):
        agent = ARTIFACT_AGENT_MAP.get(artifact)
        if agent:
            agents_to_run.append({
                "agent_id": agent,
                "reason": f"Missing artifact: {artifact}"
            })
    
    for gate in progress.get("pending_gates", []):
        agent = GATE_AGENT_MAP.get(gate)
        if agent:
            agents_to_run.append({
                "agent_id": agent,
                "reason": f"Pending review gate: {gate}"
            })
    
    return agents_to_run

# Time horizon thresholds
URGENT_HOURS = 48  # Items requiring action within 48 hours
WEEKLY_DAYS = 7    # Items for this week
MONTHLY_DAYS = 30  # Items for this month

def categorize_by_time_horizon(data, goal_progress=None, pending_reviews=None, execution_status=None, now=None):
    """
    Categorize work items by time horizon: urgent, weekly, monthly
    Returns dict with 'urgent', 'weekly', 'monthly' lists
    """
    if now is None:
        now = datetime.now(timezone.utc)
    
    urgent = []
    weekly = []
    monthly = []
    
    # 1. Pending reviews (blocking state advancement = urgent)
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
                        "description": f"Review: {review.get('artifact_name', 'Unknown')} ({review.get('gate_name', 'Unknown Gate')})"
                    }
                    if age_hours > 24 or review.get("gate_id") in ["HR_PRE", "HR_LANG"]:
                        urgent.append(item)
                    elif age_hours <= WEEKLY_DAYS * 24:
                        weekly.append(item)
                    else:
                        monthly.append(item)
    
    # 2. Missing artifacts (blocking = urgent)
    if goal_progress:
        missing_artifacts = goal_progress.get("missing_artifacts", [])
        for artifact in missing_artifacts:
            item = {
                "type": "artifact",
                "priority": "HIGH",
                "item": artifact,
                "description": f"Missing artifact: {artifact}"
            }
            urgent.append(item)
    
    # 3. Execution failures/retries (urgent)
    if execution_status:
        for exec_item in execution_status:
            status = exec_item.get("status", "")
            if status in ["FAILED", "RETRYING"]:
                agent_id = exec_item.get("agent_id", "unknown")
                attempt = exec_item.get("attempt", 0)
                max_retries = exec_item.get("max_retries", 5)
                error = exec_item.get("error", "Unknown error")
                
                item = {
                    "type": "execution",
                    "priority": "HIGH",
                    "item": exec_item,
                    "description": f"Execution {status.lower()}: {agent_id} (attempt {attempt}/{max_retries})",
                    "error": error[:100] if error else None
                }
                urgent.append(item)
    
    # 4. Agents waiting on human (blocking = urgent)
    registry = data.get("registry", {})
    agents = registry.get("agents", [])
    if agents:
        agents = deduplicate_agents(agents)
        for agent in agents:
            status = agent.get("status", "")
            if status in ["WAITING_REVIEW", "BLOCKED"]:
                agent_id = agent.get("agent_id", "unknown")
                task = agent.get("current_task", "N/A")
                heartbeat_str = agent.get("last_heartbeat", "")
                heartbeat_dt = parse_timestamp(heartbeat_str)
                
                age_hours = 0
                if heartbeat_dt:
                    age_hours = (now - heartbeat_dt).total_seconds() / 3600
                
                item = {
                    "type": "agent",
                    "priority": "HIGH" if age_hours > 24 else "MEDIUM",
                    "item": agent,
                    "age_hours": age_hours,
                    "description": f"Agent {status}: {agent_id} - {task}"
                }
                if age_hours > 24 or status == "BLOCKED":
                    urgent.append(item)
                elif age_hours <= WEEKLY_DAYS * 24:
                    weekly.append(item)
    
    # 5. State advancement needs (weekly/monthly planning)
    if goal_progress:
        current_state = goal_progress.get("current_state", "UNKNOWN")
        target_state = goal_progress.get("target_state", "UNKNOWN")
        if current_state != target_state:
            # Estimate time to next state based on current state
            state_sequence = ["PRE_EVT", "INTRO_EVT", "COMM_EVT", "FLOOR_EVT", "FINAL_EVT", "IMPL_EVT"]
            try:
                current_idx = state_sequence.index(current_state)
                target_idx = state_sequence.index(target_state)
                states_remaining = target_idx - current_idx
                
                # Rough estimates: each state transition takes 1-4 weeks
                estimated_weeks = states_remaining * 2  # Conservative estimate
                
                item = {
                    "type": "state_advancement",
                    "priority": "MEDIUM",
                    "item": {"current": current_state, "target": target_state},
                    "description": f"State advancement: {current_state} → {target_state} ({states_remaining} states remaining)",
                    "estimated_weeks": estimated_weeks
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
            "total": len(urgent) + len(weekly) + len(monthly)
        }
    }

def load_agents_from_api(workflow_id=None):
    """Load agents from API if available."""
    if not USE_API or not workflow_id or requests is None:
        return None
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/workflows/{workflow_id}/agents",
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            # Convert AgentRegistration models to dict format
            agents = []
            for agent in data.get("agents", []):
                # Handle both dict and Pydantic model
                if isinstance(agent, dict):
                    agent_dict = agent
                else:
                    # Pydantic model
                    if hasattr(agent, 'model_dump'):
                        agent_dict = agent.model_dump()
                    elif hasattr(agent, 'dict'):
                        agent_dict = agent.dict()
                    else:
                        agent_dict = {}
                
                # Extract status (handle enum)
                status = agent_dict.get("status", "")
                if hasattr(status, 'value'):
                    status_str = status.value
                else:
                    status_str = str(status)
                
                # Extract timestamps
                heartbeat_at = agent_dict.get("heartbeat_at")
                if heartbeat_at:
                    if hasattr(heartbeat_at, 'isoformat'):
                        heartbeat_str = heartbeat_at.isoformat() + "Z"
                    else:
                        heartbeat_str = str(heartbeat_at)
                else:
                    heartbeat_str = ""
                
                spawned_at = agent_dict.get("spawned_at")
                if spawned_at:
                    if hasattr(spawned_at, 'isoformat'):
                        spawned_str = spawned_at.isoformat() + "Z"
                    else:
                        spawned_str = str(spawned_at)
                else:
                    spawned_str = ""
                
                # Convert to registry format
                agents.append({
                    "agent_id": agent_dict.get("agent_id", ""),
                    "agent_type": agent_dict.get("agent_type", ""),
                    "status": status_str,
                    "scope": agent_dict.get("scope", ""),
                    "current_task": agent_dict.get("current_task", ""),
                    "last_heartbeat": heartbeat_str,
                    "risk_level": agent_dict.get("risk_level", "LOW"),
                    "outputs": agent_dict.get("outputs", []),
                    "spawned_at": spawned_str
                })
            
            return {
                "_meta": {
                    "source": "api",
                    "workflow_id": workflow_id,
                    "total_agents": len(agents),
                    "active_agents": len([a for a in agents if a.get("status") == "RUNNING"])
                },
                "agents": agents
            }
    except Exception as e:
        # Silently fail - fall back to file-based
        pass
    return None


def load_state_from_api(workflow_id=None):
    """Load state from API if available."""
    if not USE_API or requests is None:
        return None
    
    try:
        params = {}
        if workflow_id:
            params["workflow_id"] = workflow_id
        
        response = requests.get(
            f"{API_BASE_URL}/api/v1/state/current",
            params=params,
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            return {
                "_meta": {
                    "state_version": "1.0",
                    "last_updated": datetime.now(timezone.utc).isoformat() + "Z",
                    "authority": "api"
                },
                "current_state": data.get("current_state", "UNKNOWN"),
                "state_definition": data.get("state_definition", ""),
                "next_allowed_states": data.get("next_allowed_states", [])
            }
    except Exception as e:
        # Silently fail - fall back to file-based
        pass
    return None


def load_workflow_status_from_api(workflow_id):
    """Load workflow status from API."""
    if not USE_API or not workflow_id or requests is None:
        return None
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/workflows/{workflow_id}/status",
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        pass
    return None


def load_execution_status(workflow_id=None):
    """Load execution status from API"""
    if not USE_API or not requests:
        return None
    
    try:
        workflow_id = workflow_id or WORKFLOW_ID
        if not workflow_id:
            return None
        
        url = f"{API_BASE_URL}/api/v1/workflows/{workflow_id}/agents/executions"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return None

def load_pending_reviews():
    """Load all pending reviews from review queue files."""
    pending_reviews = []
    
    if not REVIEW_DIR.exists():
        return pending_reviews
    
    # Find all review queue files
    for queue_file in REVIEW_DIR.glob("*_queue.json"):
        try:
            queue_data = load_json(queue_file)
            gate_name = queue_data.get("_meta", {}).get("review_gate_name", "Unknown Gate")
            gate_id = queue_data.get("_meta", {}).get("review_gate", "UNKNOWN")
            
            # Get pending reviews
            for review in queue_data.get("pending_reviews", []):
                artifact_path = review.get("artifact_path", "")
                # Convert relative path to absolute path
                if artifact_path:
                    if Path(artifact_path).is_absolute():
                        full_path = Path(artifact_path)
                        relative_path = artifact_path
                    else:
                        full_path = BASE_DIR / artifact_path
                        relative_path = artifact_path
                    
                    # Check for associated markdown files (common pattern: artifact.json -> artifact.md or artifact_REVIEW.md)
                    md_paths = []
                    if full_path.exists():
                        # Check for .md file with same name
                        md_file = full_path.with_suffix('.md')
                        if md_file.exists():
                            md_paths.append(str(md_file))
                        # Check for _REVIEW.md file
                        review_md = full_path.parent / f"{full_path.stem}_REVIEW.md"
                        if review_md.exists():
                            md_paths.append(str(review_md))
                    
                    pending_reviews.append({
                        "review_id": review.get("review_id", "unknown"),
                        "artifact_name": review.get("artifact_name", "Unknown Artifact"),
                        "artifact_path": str(full_path),
                        "relative_path": relative_path,
                        "markdown_paths": md_paths,
                        "gate_id": gate_id,
                        "gate_name": gate_name,
                        "submitted_at": review.get("submitted_at", ""),
                        "submitted_by": review.get("submitted_by", "unknown"),
                        "review_effort_estimate": review.get("review_effort_estimate", ""),
                        "risk_level": review.get("risk_level", "")
                    })
        except Exception:
            continue
    
    return pending_reviews


def load_dashboard_data():
    """Load all dashboard data"""
    # ... existing code ...
    execution_status = load_execution_status()
    return {
        # ... existing data ...
        "execution_status": execution_status
    }
    """Load all dashboard data from files and/or API"""
    # Try to get workflow_id
    workflow_id = WORKFLOW_ID
    if not workflow_id and STATE_PATH.exists():
        try:
            state_data = load_json(STATE_PATH)
            workflow_id = state_data.get("_meta", {}).get("workflow_id")
        except:
            pass
    
    # Load agents (try API first, fallback to file)
    registry_data = None
    if USE_API and workflow_id:
        registry_data = load_agents_from_api(workflow_id)
    
    if not registry_data:
        registry_data = load_json(AGENT_REGISTRY_PATH)
        if registry_data and USE_API:
            # Mark as file-based
            if "_meta" not in registry_data:
                registry_data["_meta"] = {}
            registry_data["_meta"]["source"] = "file"
    
    # Load state (try API first, fallback to file)
    state_data = None
    if USE_API:
        state_data = load_state_from_api(workflow_id)
    
    if not state_data:
        state_data = load_json(STATE_PATH)
        if state_data and USE_API:
            if "_meta" not in state_data:
                state_data["_meta"] = {}
            state_data["_meta"]["source"] = "file"
    
    # Load dashboard status (file-based for now)
    dashboard_data = load_json(DASHBOARD_STATUS_PATH)
    
    # If API mode and workflow_id available, enhance dashboard with API data
    if USE_API and workflow_id:
        workflow_status = load_workflow_status_from_api(workflow_id)
        if workflow_status:
            # Merge API status into dashboard
            dashboard_data["pending_approvals"] = len(workflow_status.get("pending_gates", []))
            dashboard_data["can_advance"] = workflow_status.get("can_advance", False)
            dashboard_data["blocking_issues"] = workflow_status.get("blocking_issues", [])
            dashboard_data["_api_enhanced"] = True
    
    # Load execution status (API only)
    execution_status = None
    if USE_API and workflow_id:
        execution_status = load_execution_status(workflow_id)
    
    return {
        "dashboard": dashboard_data,
        "registry": registry_data or {},
        "state": state_data or {},
        "execution_status": execution_status
    }

def translate_state_to_meaning(state_code):
    """Translate abstract state codes to human-readable meaning (enhanced with subtitles)"""
    # Import enhanced state descriptions
    try:
        from monitoring.state_descriptions import get_state_description
        desc = get_state_description(state_code)
        return f"{desc['subtitle']}: {desc['description']}"
    except ImportError:
        # Fallback to original if module not available
        state_meanings = {
            "PRE_EVT": "Policy Opportunity Phase: Preparing concept and initial intelligence gathering",
            "INTRO_EVT": "Bill Vehicle Phase: Shaping legitimacy and framing. No outreach or execution has begun.",
            "COMM_EVT": "Committee Phase: Committee engagement phase. Drafting language and building support.",
            "FLOOR_EVT": "Floor Activity Phase: Floor action phase. Messaging and vote coordination.",
            "FINAL_EVT": "Vote Phase: Final passage phase. Final vote coordination, constituent narrative development, and release authorization.",
            "IMPL_EVT": "Implementation Phase: Implementation and oversight phase. Monitoring implementation, tracking outcomes, and learning from execution.",
            "UNKNOWN": "State unknown"
        }
        return state_meanings.get(state_code, f"State: {state_code}")

def get_artifact_purpose(artifact_name):
    """Get human-readable purpose for artifact"""
    purposes = {
        "Legitimacy & Policy Framing": "Articulates legitimacy, narrative framing, and policy justification for sponsor targeting",
        "Policy Whitepaper": "Academic and technical validation document for policy approach",
        "Concept Memo": "Initial concept direction and strategic approach",
        "Draft Legislative Language": "Actual bill language for committee consideration",
        "Amendment Strategy": "Strategy for amendments and modifications",
        "Committee Briefing": "Briefing materials for committee members",
        "Floor Messaging & Talking Points": "Messaging for floor debate and vote coordination"
    }
    return purposes.get(artifact_name, "Purpose not documented")

def get_time_since_progress(agents, now):
    """Calculate time since last meaningful progress (task completion or state change)"""
    last_progress = None
    for agent in agents:
        # Check for completed tasks
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

def render_dashboard(data, seconds_until_refresh, metrics=None, activity=None, goal_progress=None, next_agents=None, pending_reviews=None, execution_status=None, first_render=False):
    """Render human-review focused dashboard"""
    # Only clear screen on first render
    if first_render:
        os.system('cls' if os.name == 'nt' else 'clear')
        sys.stdout.flush()
    
    dashboard = data.get("dashboard", {})
    registry = data.get("registry", {})
    state = data.get("state", {})
    now = datetime.now(timezone.utc)
    
    # Get deduplicated agents
    agents = registry.get("agents", [])
    if agents:
        agents = deduplicate_agents(agents)
    
    # ========================================================================
    # 1️⃣ SYSTEM HEALTH SUMMARY (TOP)
    # ========================================================================
    print("=" * 80)
    print("HUMAN-REVIEW DASHBOARD")
    print("=" * 80)
    
    overall_status = dashboard.get("overall_status", "UNKNOWN")
    state_cursor = state.get("current_state", "UNKNOWN")
    pending = dashboard.get("pending_approvals", 0)
    
    # Categorize work by time horizon
    time_horizons = categorize_by_time_horizon(data, goal_progress, pending_reviews, execution_status, now)
    
    # Determine health status in plain language
    if overall_status == "WAITING_REVIEW":
        health_status = "System is healthy but paused awaiting human review."
    elif overall_status == "DEGRADED":
        health_status = "System is degraded. Some agents may need attention."
    elif overall_status == "FAILING":
        health_status = "System is failing. Immediate attention required."
    else:
        health_status = "System is healthy and operating normally."
    
    # Primary reason for non-progress
    if goal_progress and goal_progress.get("blocked"):
        missing_artifacts = goal_progress.get("missing_artifacts", [])
        if missing_artifacts:
            reason = f"Missing required artifacts: {', '.join(missing_artifacts[:2])}"
        else:
            reason = "Awaiting human review or state advancement"
    else:
        reason = "No blockers detected"
    
    # Time since last progress
    time_since = get_time_since_progress(agents, now)
    
    print(f"\n🟢 SYSTEM HEALTH SUMMARY")
    print("-" * 80)
    print(f"Health: {health_status}")
    print(f"Primary reason: {reason}")
    print(f"Last meaningful progress: {time_since}")
    print(f"Current phase: {translate_state_to_meaning(state_cursor)}")
    
    # Time horizon summary
    summary = time_horizons.get("summary", {})
    print(f"\n⏰ TIME HORIZON SUMMARY")
    print(f"  Urgent (next 48h): {summary.get('urgent_count', 0)} items")
    print(f"  This Week: {summary.get('weekly_count', 0)} items")
    print(f"  This Month: {summary.get('monthly_count', 0)} items")
    
    # ========================================================================
    # 2️⃣ HUMAN DECISION REQUIRED (IF ANY)
    # ========================================================================
    print(f"\n🟡 HUMAN DECISION REQUIRED")
    print("-" * 80)
    
    human_action_needed = False
    
    # Check for pending reviews
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
            
            # What unlocks
            if gate_id == "HR_PRE":
                print(f"  • Unlocks: State advancement to COMM_EVT and drafting agents")
            elif gate_id == "HR_LANG":
                print(f"  • Unlocks: Committee engagement and amendment strategy")
            elif gate_id == "HR_MSG":
                print(f"  • Unlocks: Floor messaging and vote coordination")
            else:
                print(f"  • Unlocks: Next phase activities")
            
            # What happens if ignored
            print(f"  • If ignored: Workflow remains blocked, no state advancement")
            print(f"  • File: {review.get('artifact_path', 'Path not available')}")
    
    # Check for blocked agents
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
    
    # ========================================================================
    # 3️⃣ STATE PROGRESSION MAP
    # ========================================================================
    print(f"\n🧭 STATE PROGRESSION MAP")
    print("-" * 80)
    
    current_state = state.get("current_state", "UNKNOWN")
    target_state = goal_progress.get("target_state", "UNKNOWN") if goal_progress else "UNKNOWN"
    
    state_sequence = ["PRE_EVT", "INTRO_EVT", "COMM_EVT", "FLOOR_EVT"]
    try:
        current_idx = state_sequence.index(current_state)
        target_idx = state_sequence.index(target_state) if target_state in state_sequence else current_idx
        
        # Show progression
        for i, s in enumerate(state_sequence):
            if i <= current_idx:
                marker = "✓"
            elif i == current_idx + 1:
                marker = "→"
            else:
                marker = " "
            print(f"  {marker} {s}: {translate_state_to_meaning(s)}")
    except ValueError:
        print(f"  Current: {current_state}")
        print(f"  Target: {target_state}")
    
    # ========================================================================
    # 4️⃣ ARTIFACT COMPLETENESS
    # ========================================================================
    print(f"\n📦 ARTIFACT COMPLETENESS")
    print("-" * 80)
    
    if goal_progress:
        required_artifacts = goal_progress.get("missing_artifacts", [])
        all_required = goal_progress.get("artifacts", {}).get("total", 0)
        
        # Artifact file paths mapping
        ARTIFACT_PATHS = {
            "Legitimacy & Policy Framing": BASE_DIR / "artifacts" / "draft_framing_intro_evt" / "INTRO_FRAME.json",
            "Policy Whitepaper": BASE_DIR / "artifacts" / "draft_whitepaper_intro_evt" / "INTRO_WHITEPAPER.json",
            "Concept Memo": BASE_DIR / "artifacts" / "draft_concept_memo_pre_evt" / "PRE_CONCEPT.json",
        }
        
        # Check which artifacts actually exist
        completed_artifacts = []
        for artifact_name, file_path in ARTIFACT_PATHS.items():
            if file_path.exists():
                completed_artifacts.append(artifact_name)
        
        # Show required artifacts
        if required_artifacts:
            print("Required (Missing):")
            for artifact in required_artifacts:
                agent_id = ARTIFACT_AGENT_MAP.get(artifact, "unknown")
                agent = next((a for a in agents if a.get("agent_id") == agent_id), None)
                status = agent.get("status", "UNKNOWN") if agent else "NOT_STARTED"
                file_path = ARTIFACT_PATHS.get(artifact)
                exists = file_path.exists() if file_path else False
                
                print(f"  • {artifact}")
                print(f"    Purpose: {get_artifact_purpose(artifact)}")
                print(f"    Owning agent: {agent_id}")
                if exists:
                    print(f"    Status: File exists, may be awaiting review")
                elif status == "RETIRED":
                    print(f"    Status: Agent retired (artifact not generated)")
                elif status == "WAITING_REVIEW":
                    print(f"    Status: Agent reports generated, but file not found")
                else:
                    print(f"    Status: Not yet generated")
                print()
        else:
            print("All required artifacts are present or generated.")
        
        # Show completed artifacts
        if completed_artifacts:
            print("Generated:")
            for artifact in completed_artifacts:
                if artifact not in required_artifacts:  # Only show if not in missing list
                    print(f"  ✓ {artifact}")
    
    # ========================================================================
    # 4.5️⃣ POLICY ARTIFACTS (READ-ONLY CONTEXT)
    # ========================================================================
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
    
    # ========================================================================
    # 5️⃣ EXECUTION STATUS (RETRY & HEALTH)
    # ========================================================================
    if execution_status:
        print(f"\n⚙️ EXECUTION STATUS")
        print("-" * 80)
        
        # Group executions by status
        running_executions = [e for e in execution_status if e.get("status") == "RUNNING"]
        retrying_executions = [e for e in execution_status if e.get("status") == "RETRYING"]
        failed_executions = [e for e in execution_status if e.get("status") == "FAILED"]
        completed_executions = [e for e in execution_status if e.get("status") == "COMPLETED"]
        pending_executions = [e for e in execution_status if e.get("status") == "PENDING"]
        
        # Show running executions
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
        
        # Show retrying executions
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
        
        # Show failed executions (max retries exceeded)
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
        
        # Show pending executions
        if pending_executions:
            print(f"\nPending ({len(pending_executions)}):")
            for exec in pending_executions[:3]:
                agent_id = exec.get("agent_id", "unknown")
                print(f"  • {agent_id}")
            if len(pending_executions) > 3:
                print(f"  ... and {len(pending_executions) - 3} more")
        
        # Summary stats
        total_executions = len(execution_status)
        if total_executions > 0:
            success_rate = len(completed_executions) / total_executions * 100
            print(f"\nSummary: {total_executions} total, {len(completed_executions)} completed ({success_rate:.0f}% success)")
    
    # ========================================================================
    # 6️⃣ AGENT LIFECYCLE STATUS
    # ========================================================================
    print(f"\n🤖 AGENT LIFECYCLE STATUS")
    print("-" * 80)
    
    # Group agents by status
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
        for agent in retired_normal[:5]:  # Limit display
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
        for agent in idle_agents[:3]:  # Limit display
            agent_id = agent.get("agent_id", "unknown")
            print(f"  • {agent_id}: Task completed, agent idle")
    
    # ========================================================================
    # 6️⃣ RECENT EVENTS (COLLAPSIBLE)
    # ========================================================================
    print(f"\n📝 RECENT EVENTS")
    print("-" * 80)
    
    try:
        if AUDIT_LOG_PATH.exists():
            with open(AUDIT_LOG_PATH, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                recent_events = []
                for line in lines[-5:]:  # Last 5 events
                    try:
                        event = json.loads(line.strip())
                        event_type = event.get("event_type", "unknown")
                        timestamp = format_timestamp(event.get("timestamp", ""))
                        agent_id = event.get("agent_id", "system")
                        
                        # Translate event types to plain language
                        event_translations = {
                            "task_completed": "Task completed",
                            "agent_retired": "Agent retired",
                            "agent_spawned": "Agent started",
                            "task_started": "Task started",
                            "error": "Error occurred"
                        }
                        event_desc = event_translations.get(event_type, event_type)
                        
                        recent_events.append(f"  {timestamp} | {event_desc} | {agent_id}")
                    except:
                        pass
                
                if recent_events:
                    for event_line in recent_events:
                        print(event_line)
                else:
                    print("  No recent events")
        else:
            print("  Event log not available")
    except:
        print("  Unable to read events")
    
    # ========================================================================
    # 7️⃣ TIME HORIZON PRIORITIES
    # ========================================================================
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
    
    # ========================================================================
    # 8️⃣ SAFE TO IGNORE (OPTIONAL)
    # ========================================================================
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
    
    # Footer
    print("\n" + "=" * 80)
    print(f"Next refresh in: {format_countdown(seconds_until_refresh)} | Press Ctrl+C to stop")
    print("=" * 80)
    sys.stdout.flush()

def generate_mermaid_chart(data, goal_progress=None, pending_reviews=None):
    """Generate Mermaid flowchart chart from dashboard data"""
    dashboard = data.get("dashboard", {})
    registry = data.get("registry", {})
    state = data.get("state", {})
    now = datetime.now(timezone.utc)
    
    # Get deduplicated agents
    agents = registry.get("agents", [])
    if agents:
        agents = deduplicate_agents(agents)
    
    current_state = state.get("current_state", "UNKNOWN")
    target_state = goal_progress.get("target_state", "UNKNOWN") if goal_progress else "UNKNOWN"
    overall_status = dashboard.get("overall_status", "UNKNOWN")
    
    # Artifact file paths
    ARTIFACT_PATHS = {
        "Legitimacy & Policy Framing": BASE_DIR / "artifacts" / "draft_framing_intro_evt" / "INTRO_FRAME.json",
        "Policy Whitepaper": BASE_DIR / "artifacts" / "draft_whitepaper_intro_evt" / "INTRO_WHITEPAPER.json",
        "Concept Memo": BASE_DIR / "artifacts" / "draft_concept_memo_pre_evt" / "PRE_CONCEPT.json",
    }
    
    # Group agents
    active_agents = [a for a in agents if a.get("status") == "RUNNING"]
    waiting_agents = [a for a in agents if a.get("status") in ["WAITING_REVIEW", "BLOCKED"]]
    retired_agents = [a for a in agents if a.get("status") == "RETIRED"]
    
    # Check artifact status
    missing_artifacts = goal_progress.get("missing_artifacts", []) if goal_progress else []
    completed_artifacts = []
    for artifact_name, file_path in ARTIFACT_PATHS.items():
        if file_path.exists() and artifact_name not in missing_artifacts:
            completed_artifacts.append(artifact_name)
    
    # Build Mermaid chart
    lines = []
    lines.append("---")
    lines.append("config:")
    lines.append("  layout: dagre")
    lines.append("  theme: default")
    lines.append("---")
    lines.append("flowchart TB")
    lines.append("")
    
    # System status node
    health_color = "🟢" if overall_status in ["OK", "HEALTHY"] else "🟡" if overall_status == "WAITING_REVIEW" else "🔴"
    lines.append(f'STATUS["{health_color} System Status: {overall_status}"]:::status')
    lines.append("")
    
    # State progression subgraph
    lines.append('subgraph STATES["📜 State Progression"]')
    lines.append("direction LR")
    
    state_sequence = ["PRE_EVT", "INTRO_EVT", "COMM_EVT", "FLOOR_EVT"]
    state_nodes = []
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
    
    # Artifacts subgraph
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
    
    # Agents subgraph
    lines.append('subgraph AGENTS["🤖 Agents"]')
    lines.append("direction TB")
    
    if active_agents:
        lines.append('  subgraph ACTIVE["Active"]')
        for agent in active_agents[:5]:  # Limit to 5
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
        for agent in retired_agents[:5]:  # Limit to 5
            agent_id = agent.get("agent_id", "unknown").replace("-", "_")
            lines.append(f'    {agent_id}["⚫ {agent_id}"]:::retired')
        lines.append("  end")
    
    lines.append("end")
    lines.append("")
    
    # Human decision gates
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
    
    # Connections
    lines.append("STATUS --> STATES")
    
    # State progression
    for i in range(len(state_nodes) - 1):
        lines.append(f"{state_nodes[i]} --> {state_nodes[i+1]}")
    
    # Artifacts to states
    if current_state == "INTRO_EVT":
        lines.append("INTRO_EVT --> ARTIFACTS")
    
    # Agents to artifacts
    for artifact_name in ["Legitimacy & Policy Framing", "Policy Whitepaper"]:
        agent_id = ARTIFACT_AGENT_MAP.get(artifact_name, "").replace("-", "_")
        artifact_node = artifact_name.replace(" ", "_").replace("&", "and")
        if agent_id and any(a.get("agent_id") == ARTIFACT_AGENT_MAP.get(artifact_name) for a in agents):
            lines.append(f"{agent_id} --> {artifact_node}")
    
    # Gates to artifacts
    if pending_reviews:
        for review in pending_reviews:
            gate_id = review.get("gate_id", "UNKNOWN").replace("-", "_")
            artifact_name = review.get("artifact_name", "")
            if artifact_name:
                artifact_node = artifact_name.replace(" ", "_").replace("&", "and")
                lines.append(f"{artifact_node} --> {gate_id}")
    
    # Styling
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

def show_loading_indicator(message="Loading", stop_event=None):
    """Show animated loading indicator"""
    import threading
    
    # Use simple ASCII characters that work on all terminals
    spinner = ['|', '/', '-', '\\']
    
    def animate():
        i = 0
        while not stop_event.is_set():
            print(f'\r{message} {spinner[i % len(spinner)]}', end='', flush=True)
            i += 1
            time.sleep(0.15)
        print('\r' + ' ' * (len(message) + 10) + '\r', end='', flush=True)  # Clear line
    
    if stop_event is None:
        # Simple one-time spinner
        for i in range(12):
            print(f'\r{message} {spinner[i % len(spinner)]}', end='', flush=True)
            time.sleep(0.15)
        print('\r' + ' ' * (len(message) + 10) + '\r', end='', flush=True)
        return None
    else:
        # Threaded spinner
        thread = threading.Thread(target=animate, daemon=True)
        thread.start()
        return thread


def save_mermaid_chart(chart_content, output_path=None):
    """Save Mermaid chart to file"""
    if output_path is None:
        output_path = BASE_DIR / "monitoring" / "dashboard-status.mmd"
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(chart_content)
    
    print(f"[INFO] Mermaid chart saved to: {output_path}")
    return output_path

def main():
    """Main dashboard loop"""
    # Check for --mermaid flag
    generate_mermaid_only = "--mermaid" in sys.argv or "-m" in sys.argv
    
    # Print immediately so user knows script is running
    print("=" * 80)
    print("Agent Health Dashboard - Starting...")
    print("=" * 80)
    
    # Set UTF-8 encoding for Windows console to support emojis
    try:
        if sys.platform == 'win32':
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception as e:
        print(f"Warning: Could not set UTF-8 encoding: {e}")
    
    print("Starting Agent Health Dashboard (24/7 Enhanced)...")
    print(f"Data refresh: every {DATA_REFRESH_INTERVAL // 60} minutes")
    print(f"Display update: every {HEARTBEAT_INTERVAL} seconds")
    print(f"Metrics collection: every {METRICS_COLLECTION_INTERVAL // 60} minutes")
    print()
    
    # Load initial data with progress feedback
    print("Loading dashboard data", end='', flush=True)
    try:
        print(".", end='', flush=True)
        data = load_dashboard_data()
        print(".", end='', flush=True)
        goal = load_goal()
        print(".", end='', flush=True)
        pending_reviews = load_pending_reviews()
        print(" [OK]\n")
    except Exception as e:
        print(f" [ERROR]\n")
        print(f"ERROR loading data: {e}")
        import traceback
        traceback.print_exc()
        return
    
    last_data_refresh = time.time()
    last_metrics_collection = time.time()
    last_activity_analysis = time.time()
    
    metrics = None
    activity = None
    goal_progress = None
    next_agents = None
    
    # Compute initial goal progress
    if goal and "state" in data and "dashboard" in data:
        goal_progress = compute_goal_progress(
            state=data.get("state", {}),
            dashboard=data.get("dashboard", {}),
            goal=goal
        )
        next_agents = compute_next_agents(goal_progress)
    
    # Generate Mermaid chart if requested
    if generate_mermaid_only:
        try:
            chart = generate_mermaid_chart(data, goal_progress, pending_reviews)
            output_path = save_mermaid_chart(chart)
            print(f"\n[SUCCESS] Mermaid chart generated and saved to: {output_path}")
            print("\nYou can view it in:")
            print("  - Mermaid Live Editor: https://mermaid.live")
            print("  - VS Code with Mermaid extension")
            print("  - Any Mermaid-compatible viewer")
            return
        except Exception as e:
            print(f"\n[ERROR] Failed to generate Mermaid chart: {e}")
            import traceback
            traceback.print_exc()
            return
    
    # Track last displayed data to detect changes
    last_pending_count = len(pending_reviews) if pending_reviews else 0
    last_state = goal_progress.get("current_state") if goal_progress else None
    agents = data.get("registry", {}).get("agents", [])
    if agents:
        agents = deduplicate_agents(agents)
        last_agent_count = len(agents)
    else:
        last_agent_count = 0
    first_render = True
    
    # Load execution status
    execution_status = data.get("execution_status")
    
    # Render immediately after loading
    print("Rendering dashboard...", flush=True)
    seconds_until_refresh = int(DATA_REFRESH_INTERVAL)
    try:
        render_dashboard(data, seconds_until_refresh, metrics, activity, goal_progress, next_agents, pending_reviews, execution_status, first_render=True)
        sys.stdout.flush()  # Ensure all output is flushed
    except Exception as e:
        print(f"\nERROR rendering dashboard: {e}")
        import traceback
        traceback.print_exc()
        return
    first_render = False
    
    try:
        while True:
            current_time = time.time()
            time_since_refresh = current_time - last_data_refresh
            time_since_metrics = current_time - last_metrics_collection
            time_since_activity = current_time - last_activity_analysis
            
            data_changed = False
            
            # Refresh data if interval has passed
            if time_since_refresh >= DATA_REFRESH_INTERVAL:
                data = load_dashboard_data()
                execution_status = data.get("execution_status")
                goal = load_goal()  # Reload goal in case it changed
                last_data_refresh = current_time
                time_since_refresh = 0
                data_changed = True
            
            # Load pending reviews (refresh with data)
            new_pending_reviews = load_pending_reviews()
            new_pending_count = len(new_pending_reviews) if new_pending_reviews else 0
            if new_pending_count != last_pending_count or (new_pending_reviews != pending_reviews and pending_reviews is not None):
                pending_reviews = new_pending_reviews
                last_pending_count = new_pending_count
                data_changed = True
            
            # Compute goal progress (refresh with data)
            if goal:
                if "state" in data and "dashboard" in data:
                    new_goal_progress = compute_goal_progress(
                        state=data.get("state", {}),
                        dashboard=data.get("dashboard", {}),
                        goal=goal
                    )
                    if new_goal_progress:
                        current_state = new_goal_progress.get("current_state")
                        if current_state != last_state:
                            goal_progress = new_goal_progress
                            next_agents = compute_next_agents(goal_progress)
                            last_state = current_state
                            data_changed = True
                        elif goal_progress is None:
                            goal_progress = new_goal_progress
                            next_agents = compute_next_agents(goal_progress)
                            data_changed = True
                elif next_agents is None and goal_progress:
                    next_agents = compute_next_agents(goal_progress)
                    data_changed = True
            
            # Check if agent count changed
            agents = data.get("registry", {}).get("agents", [])
            if agents:
                agents = deduplicate_agents(agents)
                new_agent_count = len(agents)
                if new_agent_count != last_agent_count:
                    last_agent_count = new_agent_count
                    data_changed = True
            
            # Collect metrics periodically (but don't trigger re-render)
            if time_since_metrics >= METRICS_COLLECTION_INTERVAL:
                metrics = collect_metrics(data)
                last_metrics_collection = current_time
            
            # Analyze activity periodically (but don't trigger re-render)
            if time_since_activity >= 900:  # 15 minutes
                activity = analyze_recent_activity(hours=24)
                last_activity_analysis = current_time
            
            # Only render if data changed or it's the first render
            if data_changed or first_render:
                # Calculate seconds until next refresh
                seconds_until_refresh = int(DATA_REFRESH_INTERVAL - time_since_refresh)
                
                # Render dashboard with countdown
                render_dashboard(data, seconds_until_refresh, metrics, activity, goal_progress, next_agents, pending_reviews, execution_status, first_render=first_render)
                
                first_render = False
            
            # Wait for heartbeat interval
            time.sleep(HEARTBEAT_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n\nDashboard stopped by user")
    except Exception as e:
        print(f"\n\nDashboard error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDashboard stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
