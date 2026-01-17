"""
Script: velocity__calculate__metrics.py
Intent:
- snapshot

Reads:
- state/legislative-state.json
- review/HR_*_queue.json (4 files)
- registry/agent-registry.json
- audit/audit-log.jsonl

Writes:
- dashboards/velocity_metrics.txt (operational, disposable)

Schema:
Terminal-readable metrics table showing throughput, waiting times, and bottlenecks.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict

# Path setup
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

# Constants
STATE_PATH = BASE_DIR / "state" / "legislative-state.json"
REVIEW_DIR = BASE_DIR / "review"
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
AUDIT_LOG_PATH = BASE_DIR / "audit" / "audit-log.jsonl"
DASHBOARDS_DIR = BASE_DIR / "dashboards"
DASHBOARDS_DIR.mkdir(parents=True, exist_ok=True)

# Thresholds (in minutes)
REVIEW_TIME_THRESHOLDS = {
    "HR_PRE": 90,
    "HR_LANG": 90,
    "HR_MSG": 30,
    "HR_RELEASE": 10,
}

# Expected state advancement times (in days)
STATE_ADVANCEMENT_EXPECTED = {
    "PRE_EVT": 7,  # PRE -> INTRO
    "INTRO_EVT": 14,  # INTRO -> COMM
    "COMM_EVT": 30,  # COMM -> FLOOR
    "FLOOR_EVT": 7,  # FLOOR -> FINAL
    "FINAL_EVT": 1,  # FINAL -> IMPL
}

# Expected agent execution times (in minutes)
AGENT_EXECUTION_EXPECTED = {
    "Intelligence": 60,
    "Drafting": 120,
    "Execution": None,  # Varies by action
    "Learning": 30,
}


def parse_timestamp(ts_str: str) -> Optional[datetime]:
    """Parse ISO timestamp to datetime object."""
    if not ts_str:
        return None
    try:
        ts_str = ts_str.replace("Z", "+00:00")
        return datetime.fromisoformat(ts_str)
    except Exception:
        return None


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds // 60)}m {int(seconds % 60)}s"
    hours = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    if hours < 24:
        return f"{hours}h {mins}m"
    days = int(hours // 24)
    hours_remainder = hours % 24
    return f"{days}d {hours_remainder}h {mins}m"


def load_json(path: Path) -> Dict[str, Any]:
    """Load JSON file, return {} if not found or invalid."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def calculate_time_in_state(state_data: Dict[str, Any]) -> Optional[float]:
    """Calculate time spent in current state in seconds."""
    state_history = state_data.get("state_history", [])
    if not state_history:
        return None
    
    current_state = state_data.get("current_state", "UNKNOWN")
    # Find when we entered current state
    for entry in reversed(state_history):
        if entry.get("state") == current_state:
            entered_at = entry.get("entered_at", "")
            if entered_at:
                dt = parse_timestamp(entered_at)
                if dt:
                    now = datetime.now(timezone.utc)
                    return (now - dt).total_seconds()
    
    return None


def calculate_review_times(review_gates: Dict[str, Dict[str, Any]], limit: int = 10) -> Dict[str, Dict[str, Any]]:
    """Calculate average review times by gate."""
    review_times = {}
    
    for gate_id, gate_data in review_gates.items():
        review_history = gate_data.get("review_history", [])
        
        # Get last N reviews with decisions
        completed_reviews = [
            r for r in review_history
            if r.get("decision") and r.get("decision_at") and r.get("submitted_at")
        ]
        completed_reviews.sort(key=lambda x: x.get("decision_at", ""), reverse=True)
        completed_reviews = completed_reviews[:limit]
        
        if not completed_reviews:
            review_times[gate_id] = {
                "count": 0,
                "avg_minutes": None,
                "threshold_minutes": REVIEW_TIME_THRESHOLDS.get(gate_id),
                "status": "no data"
            }
            continue
        
        # Calculate average time
        total_seconds = 0
        count = 0
        for review in completed_reviews:
            submitted_at = parse_timestamp(review.get("submitted_at", ""))
            decision_at = parse_timestamp(review.get("decision_at", ""))
            if submitted_at and decision_at:
                duration = (decision_at - submitted_at).total_seconds()
                if duration > 0:  # Sanity check
                    total_seconds += duration
                    count += 1
        
        if count > 0:
            avg_seconds = total_seconds / count
            avg_minutes = avg_seconds / 60
            threshold = REVIEW_TIME_THRESHOLDS.get(gate_id)
            
            if threshold:
                if avg_minutes < threshold:
                    status = "FAST"
                elif avg_minutes <= threshold * 1.2:
                    status = "NORMAL"
                else:
                    status = "SLOW"
            else:
                status = "NORMAL"
            
            review_times[gate_id] = {
                "count": count,
                "avg_minutes": avg_minutes,
                "avg_seconds": avg_seconds,
                "threshold_minutes": threshold,
                "status": status
            }
        else:
            review_times[gate_id] = {
                "count": 0,
                "avg_minutes": None,
                "threshold_minutes": threshold,
                "status": "no data"
            }
    
    return review_times


def calculate_agent_execution_times(registry_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Calculate average execution times by agent type."""
    agents = registry_data.get("agents", [])
    
    execution_times = defaultdict(list)
    
    for agent in agents:
        agent_type = agent.get("agent_type", "")
        spawned_at = parse_timestamp(agent.get("spawned_at", ""))
        terminated_at = parse_timestamp(agent.get("terminated_at", ""))
        
        if spawned_at and terminated_at:
            duration = (terminated_at - spawned_at).total_seconds()
            if duration > 0:
                execution_times[agent_type].append(duration)
    
    result = {}
    for agent_type, durations in execution_times.items():
        if durations:
            avg_seconds = sum(durations) / len(durations)
            avg_minutes = avg_seconds / 60
            expected_minutes = AGENT_EXECUTION_EXPECTED.get(agent_type)
            
            if expected_minutes:
                if avg_minutes < expected_minutes:
                    status = "FAST"
                elif avg_minutes <= expected_minutes * 1.2:
                    status = "NORMAL"
                else:
                    status = "SLOW"
            else:
                status = "NORMAL"
            
            result[agent_type] = {
                "count": len(durations),
                "avg_minutes": avg_minutes,
                "expected_minutes": expected_minutes,
                "status": status
            }
        else:
            result[agent_type] = {
                "count": 0,
                "avg_minutes": None,
                "expected_minutes": AGENT_EXECUTION_EXPECTED.get(agent_type),
                "status": "no data"
            }
    
    return result


def get_queue_depths(review_gates: Dict[str, Dict[str, Any]], registry_data: Dict[str, Any]) -> Dict[str, int]:
    """Get queue depths for pending reviews and blocked agents."""
    total_pending = sum(len(gate.get("pending_reviews", [])) for gate in review_gates.values())
    
    agents = registry_data.get("agents", [])
    blocked_count = sum(1 for a in agents if a.get("status") == "BLOCKED")
    waiting_review_count = sum(1 for a in agents if a.get("status") == "WAITING_REVIEW")
    
    return {
        "pending_reviews": total_pending,
        "blocked_agents": blocked_count,
        "waiting_review_agents": waiting_review_count,
        "waiting_state_advancement": 0  # Would need to check state advancement readiness
    }


def identify_bottlenecks(
    review_times: Dict[str, Dict[str, Any]],
    agent_times: Dict[str, Dict[str, Any]],
    queue_depths: Dict[str, int],
    review_gates: Dict[str, Dict[str, Any]],
    registry_data: Dict[str, Any]
) -> List[Tuple[str, str, Optional[str]]]:
    """Identify bottlenecks and return list of (priority, description, action_command)."""
    bottlenecks = []
    
    # Check review times
    for gate_id, times in review_times.items():
        if times.get("status") == "SLOW":
            avg = times.get("avg_minutes", 0)
            threshold = times.get("threshold_minutes", 0)
            if threshold:
                pct_over = ((avg - threshold) / threshold) * 100
                bottlenecks.append((
                    "HIGH",
                    f"{gate_id} reviews taking {avg:.0f}m ({pct_over:.0f}% over threshold of {threshold}m)",
                    "python scripts/cockpit__list__pending_approvals.py"
                ))
    
    # Check agent execution times
    for agent_type, times in agent_times.items():
        if times.get("status") == "SLOW":
            avg = times.get("avg_minutes", 0)
            expected = times.get("expected_minutes", 0)
            if expected:
                pct_over = ((avg - expected) / expected) * 100
                bottlenecks.append((
                    "MEDIUM",
                    f"{agent_type} agents taking {avg:.0f}m ({pct_over:.0f}% over expected {expected}m)",
                    None
                ))
    
    # Check pending reviews waiting too long
    for gate_id, gate_data in review_gates.items():
        pending = gate_data.get("pending_reviews", [])
        for review in pending:
            submitted_at = parse_timestamp(review.get("submitted_at", ""))
            if submitted_at:
                now = datetime.now(timezone.utc)
                age_seconds = (now - submitted_at).total_seconds()
                age_minutes = age_seconds / 60
                threshold = REVIEW_TIME_THRESHOLDS.get(gate_id, 90)
                
                if age_minutes > threshold:
                    bottlenecks.append((
                        "HIGH",
                        f"{review.get('artifact_name', 'Unknown')} waiting {age_minutes:.0f}m for {gate_id} review",
                        "python scripts/cockpit__list__pending_approvals.py"
                    ))
    
    # Check blocked agents
    if queue_depths.get("blocked_agents", 0) > 0:
        bottlenecks.append((
            "MEDIUM",
            f"{queue_depths['blocked_agents']} agents blocked awaiting authorization",
            "python scripts/cockpit__authorize_execution.py"
        ))
    
    return bottlenecks


def format_velocity_banner(status: str, message: str) -> str:
    """Create velocity status banner with ASCII art."""
    status_icons = {
        "FAST": "✓",
        "NORMAL": "•",
        "SLOW": "⚠",
        "BLOCKED": "✗"
    }
    status_labels = {
        "FAST": "⚡ VELOCITY STATUS: FAST ✓",
        "NORMAL": "⚡ VELOCITY STATUS: NORMAL •",
        "SLOW": "⚡ VELOCITY STATUS: SLOW ⚠",
        "BLOCKED": "⚡ VELOCITY STATUS: BLOCKED ✗"
    }
    
    label = status_labels.get(status, f"⚡ VELOCITY STATUS: {status}")
    
    # Create banner with box-drawing characters
    banner_width = 65
    lines = []
    lines.append("╔" + "═" * (banner_width - 2) + "╗")
    lines.append("║  " + label.ljust(banner_width - 6) + "  ║")
    lines.append("║  " + message.ljust(banner_width - 6) + "  ║")
    lines.append("╚" + "═" * (banner_width - 2) + "╝")
    
    return "\n".join(lines)


def format_time_progress(current_seconds: float, expected_days: int, state: str) -> str:
    """Create time visualization with progress bar and trend indicator."""
    if expected_days is None or expected_days <= 0:
        time_str = format_duration(current_seconds)
        return f"{state}: {time_str}\nStatus: No expected time →"
    
    expected_seconds = expected_days * 24 * 3600
    progress = min(current_seconds / expected_seconds, 1.0)  # Cap at 100%
    
    bar_width = 30
    filled = int(progress * bar_width)
    bar = "█" * filled + "░" * (bar_width - filled)
    
    progress_pct = int(progress * 100)
    current_str = format_duration(current_seconds)
    expected_str = f"{expected_days}d"
    
    # Determine status and trend
    if progress < 0.5:
        status = "FAST ✓ (well within expected range)"
        trend = "↓"
    elif progress < 1.0:
        status = "NORMAL • (within expected range)"
        trend = "→"
    elif progress < 1.2:
        status = "SLOW ⚠ (approaching limit)"
        trend = "↑"
    else:
        status = "SLOW ⚠ (over expected)"
        trend = "↑↑"
    
    lines = []
    lines.append(f"{state}: [{bar}] {current_str} / {expected_str} {trend}")
    lines.append(f"Status: {status} ({progress_pct}% of expected)")
    
    return "\n".join(lines)


def format_review_health(review_times: Dict[str, Dict[str, Any]]) -> str:
    """Format review cycle health with visual indicators and trend symbols."""
    lines = []
    for gate_id in ["HR_PRE", "HR_LANG", "HR_MSG", "HR_RELEASE"]:
        times = review_times.get(gate_id, {})
        count = times.get("count", 0)
        avg = times.get("avg_minutes")
        threshold = times.get("threshold_minutes")
        status = times.get("status", "no data")
        
        if avg is not None:
            status_symbol = "✓" if status == "FAST" else "⚠" if status == "SLOW" else "•"
            threshold_str = f"(threshold: {threshold}m)" if threshold else ""
            
            # Add trend indicator based on status relative to threshold
            if threshold:
                if avg < threshold * 0.5:
                    trend = "↓"  # Well below threshold
                elif avg < threshold:
                    trend = "→"  # Within threshold
                elif avg < threshold * 1.2:
                    trend = "↑"  # Approaching limit
                else:
                    trend = "↑↑"  # Over limit
            else:
                trend = "→"
            
            lines.append(f"  {gate_id}:     avg {avg:.0f}m  {threshold_str}  {status_symbol} {status} {trend}")
        else:
            lines.append(f"  {gate_id}:     no data")
    
    return "\n".join(lines)


def format_bottleneck_list(bottlenecks: List[Tuple[str, str, Optional[str]]]) -> str:
    """Format prioritized bottleneck list with actions."""
    if not bottlenecks:
        return "  No bottlenecks identified ✓"
    
    lines = []
    # Sort by priority
    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    bottlenecks.sort(key=lambda x: (priority_order.get(x[0], 99), x[1]))
    
    for idx, (priority, desc, action) in enumerate(bottlenecks[:5], 1):  # Top 5
        lines.append(f" {idx}. [{priority}] {desc}")
        if action:
            lines.append(f"    → {action}")
        if idx < len(bottlenecks[:5]):
            lines.append("")
    
    return "\n".join(lines)


def format_actions_needed(bottlenecks: List[Tuple[str, str, Optional[str]]], queue_depths: Dict[str, int]) -> str:
    """Create prioritized actions section with improved descriptions."""
    lines = []
    lines.append("ACTIONS NEEDED")
    lines.append("─" * 65)
    
    actions = []
    
    # Extract actions from bottlenecks
    for priority, desc, action in bottlenecks:
        if action:
            # Improve "Why" description
            if "reviews taking" in desc.lower() and "over threshold" in desc.lower():
                # Extract gate and time info
                parts = desc.split()
                gate_id = parts[0] if parts else "review gate"
                why = f"{gate_id} review cycle is exceeding threshold, slowing system velocity"
                impact = "Will reduce review cycle time and improve throughput"
            elif "blocked" in desc.lower() and "authorization" in desc.lower():
                why = "Execution agent is blocked and cannot proceed without authorization"
                impact = "Unblocks agent execution and allows workflow to continue"
            elif "waiting" in desc.lower() and "for" in desc.lower() and "review" in desc.lower():
                # Extract artifact name and time
                artifact_name = desc.split(" waiting")[0] if " waiting" in desc else "artifact"
                time_match = [w for w in desc.split() if "m" in w or "h" in w or "d" in w]
                time_str = time_match[0] if time_match else "extended period"
                why = f"{artifact_name} has been waiting {time_str} for review, exceeding threshold"
                impact = "Reduces wait time for artifact and prevents further delays"
            else:
                why = desc
                impact = "Improves system velocity"
            
            actions.append((priority, desc, why, impact, action))
    
    # Add queue-based actions
    if queue_depths.get("blocked_agents", 0) > 0 and not any("blocked" in a[1].lower() for a in actions):
        actions.append((
            "MEDIUM",
            f"Review {queue_depths['blocked_agents']} blocked execution agent(s)",
            f"{queue_depths['blocked_agents']} execution agent(s) blocked awaiting authorization",
            "Unblocks agent execution and allows workflow to continue",
            "python scripts/cockpit__authorize_execution.py"
        ))
    
    if queue_depths.get("pending_reviews", 0) > 0:
        if not any("pending" in a[1].lower() or "review" in a[1].lower() for a in actions):
            actions.append((
                "MEDIUM",
                f"Review {queue_depths['pending_reviews']} pending artifact(s)",
                f"{queue_depths['pending_reviews']} artifact(s) awaiting review in queue",
                "Reduces queue depth and improves throughput",
                "python scripts/cockpit__list__pending_approvals.py"
            ))
    
    if not actions:
        lines.append("  No immediate actions required ✓")
    else:
        # Sort by priority
        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        actions.sort(key=lambda x: (priority_order.get(x[0], 99), x[1]))
        
        for idx, (priority, what, why, impact, command) in enumerate(actions[:5], 1):  # Top 5
            lines.append(f"[{priority}] {what}")
            lines.append(f"  Why: {why}")
            lines.append(f"  Impact: {impact}")
            lines.append(f"  Action: {command}")
            if idx < len(actions[:5]):
                lines.append("")
    
    return "\n".join(lines)


def determine_velocity_status(
    time_in_state_seconds: Optional[float],
    expected_days: Optional[int],
    review_times: Dict[str, Dict[str, Any]],
    bottlenecks: List[Tuple[str, str, Optional[str]]]
) -> Tuple[str, str]:
    """Determine overall velocity status."""
    # Check for blocking conditions first
    if any(b[0] == "HIGH" and "blocked" in b[1].lower() for b in bottlenecks):
        return "BLOCKED", "Agents blocked, immediate action required"
    
    # Check time in state
    if time_in_state_seconds and expected_days:
        expected_seconds = expected_days * 24 * 3600
        if time_in_state_seconds > expected_seconds * 1.2:
            return "SLOW", "State advancement delayed, review bottlenecks"
        elif time_in_state_seconds > expected_seconds:
            return "SLOW", "Approaching expected time limit"
    
    # Check review times
    slow_reviews = [gate for gate, times in review_times.items() if times.get("status") == "SLOW"]
    if slow_reviews:
        return "SLOW", f"Review cycles slow: {', '.join(slow_reviews)}"
    
    # Check for high-priority bottlenecks
    if any(b[0] == "HIGH" for b in bottlenecks):
        return "SLOW", "High-priority bottlenecks detected"
    
    # Check if everything is fast
    fast_reviews = [gate for gate, times in review_times.items() if times.get("status") == "FAST"]
    if time_in_state_seconds and expected_days:
        expected_seconds = expected_days * 24 * 3600
        if time_in_state_seconds < expected_seconds * 0.5 and len(fast_reviews) == len([g for g in review_times.keys() if review_times[g].get("count", 0) > 0]):
            return "FAST", "System operating efficiently, no immediate action needed"
    
    return "NORMAL", "System operating within expected parameters"


def generate_velocity_metrics() -> str:
    """Generate velocity metrics text."""
    # Load canonical data
    state_data = load_json(STATE_PATH)
    registry_data = load_json(REGISTRY_PATH)
    
    # Load review gates
    review_gates = {}
    if REVIEW_DIR.exists():
        for queue_file in REVIEW_DIR.glob("HR_*_queue.json"):
            gate_data = load_json(queue_file)
            gate_id = gate_data.get("_meta", {}).get("review_gate", "UNKNOWN")
            review_gates[gate_id] = gate_data
    
    # Calculate metrics
    time_in_state_seconds = calculate_time_in_state(state_data)
    review_times = calculate_review_times(review_gates)
    agent_times = calculate_agent_execution_times(registry_data)
    queue_depths = get_queue_depths(review_gates, registry_data)
    bottlenecks = identify_bottlenecks(review_times, agent_times, queue_depths, review_gates, registry_data)
    
    # Determine velocity status
    current_state = state_data.get("current_state", "UNKNOWN")
    expected_days = STATE_ADVANCEMENT_EXPECTED.get(current_state)
    velocity_status, velocity_message = determine_velocity_status(
        time_in_state_seconds, expected_days, review_times, bottlenecks
    )
    
    # Build output
    output_lines = []
    
    # Status banner (always shown)
    output_lines.append(format_velocity_banner(velocity_status, velocity_message))
    output_lines.append("")
    
    # At-a-glance summary
    output_lines.append("AT-A-GLANCE")
    output_lines.append("─" * 65)
    if time_in_state_seconds and expected_days:
        time_str = format_duration(time_in_state_seconds)
        expected_seconds = expected_days * 24 * 3600
        progress_pct = int(min((time_in_state_seconds / expected_seconds) * 100, 100))
        status_icon = "✓" if velocity_status == "FAST" else "⚠" if velocity_status == "SLOW" else "•"
        output_lines.append(f"State:        {current_state} ({time_str} / {expected_days}d expected) [{progress_pct}%] {status_icon} {velocity_status}")
    else:
        time_str = format_duration(time_in_state_seconds) if time_in_state_seconds else "No data"
        output_lines.append(f"State:        {current_state} ({time_str})")
    
    # Review summary
    fast_reviews = [gate for gate, times in review_times.items() if times.get("status") == "FAST"]
    slow_reviews = [gate for gate, times in review_times.items() if times.get("status") == "SLOW"]
    if fast_reviews:
        output_lines.append(f"Reviews:      {', '.join(fast_reviews)}: FAST ✓")
    if slow_reviews:
        output_lines.append(f"Reviews:      {', '.join(slow_reviews)}: SLOW ⚠")
    if not fast_reviews and not slow_reviews:
        output_lines.append(f"Reviews:      No data")
    
    # Blocked agents
    if queue_depths.get("blocked_agents", 0) > 0:
        output_lines.append(f"Blocked:      {queue_depths['blocked_agents']} agent(s) awaiting authorization ⚠")
    else:
        output_lines.append(f"Blocked:      0 agents ✓")
    
    # Bottlenecks summary
    high_bottlenecks = [b for b in bottlenecks if b[0] == "HIGH"]
    medium_bottlenecks = [b for b in bottlenecks if b[0] == "MEDIUM"]
    if high_bottlenecks:
        output_lines.append(f"Bottlenecks:  {len(high_bottlenecks)} high-priority, {len(medium_bottlenecks)} medium-priority")
    elif medium_bottlenecks:
        output_lines.append(f"Bottlenecks:  {len(medium_bottlenecks)} medium-priority item(s)")
    else:
        output_lines.append(f"Bottlenecks:  None ✓")
    output_lines.append("")
    
    # Time in state with progress bar
    output_lines.append("TIME IN STATE")
    output_lines.append("─" * 65)
    if time_in_state_seconds and expected_days:
        output_lines.append(format_time_progress(time_in_state_seconds, expected_days, current_state))
    else:
        time_str = format_duration(time_in_state_seconds) if time_in_state_seconds else "No data"
        output_lines.append(f"{current_state}: {time_str}")
        output_lines.append("Status: No expected time")
    output_lines.append("")
    
    # Review cycle times
    output_lines.append("REVIEW CYCLE TIMES (last 10 reviews)")
    output_lines.append("─" * 65)
    output_lines.append(format_review_health(review_times))
    output_lines.append("")
    
    # Agent execution times
    output_lines.append("AGENT EXECUTION TIMES")
    output_lines.append("─" * 65)
    for agent_type in ["Intelligence", "Drafting", "Execution", "Learning"]:
        times = agent_times.get(agent_type, {})
        count = times.get("count", 0)
        avg = times.get("avg_minutes")
        expected = times.get("expected_minutes")
        status = times.get("status", "no data")
        
        if avg is not None:
            status_symbol = "✓" if status == "FAST" else "⚠" if status == "SLOW" else "•"
            expected_str = f"(expected: {expected}m)" if expected else ""
            output_lines.append(f"  {agent_type}: avg {avg:.0f}m  {expected_str}   {status_symbol}")
        else:
            output_lines.append(f"  {agent_type}:    no data")
    output_lines.append("")
    
    # Queue depths
    output_lines.append("QUEUE DEPTHS")
    output_lines.append("─" * 65)
    output_lines.append(f"  Pending reviews: {queue_depths['pending_reviews']}")
    output_lines.append(f"  Blocked agents:  {queue_depths['blocked_agents']}")
    output_lines.append(f"  Waiting state advancement: {queue_depths['waiting_state_advancement']}")
    output_lines.append("")
    
    # Bottlenecks
    output_lines.append("BOTTLENECKS")
    output_lines.append("─" * 65)
    output_lines.append(format_bottleneck_list(bottlenecks))
    output_lines.append("")
    
    # Actions needed
    output_lines.append(format_actions_needed(bottlenecks, queue_depths))
    
    return "\n".join(output_lines)


def main():
    """Main execution."""
    print("[velocity__calculate__metrics] Calculating velocity metrics...")
    
    try:
        metrics_text = generate_velocity_metrics()
        
        # Write to file
        output_file = DASHBOARDS_DIR / "velocity_metrics.txt"
        output_file.write_text(metrics_text, encoding="utf-8")
        
        print(f"[OK] Velocity metrics written to: {output_file}")
        try:
            print("\n" + metrics_text)
        except UnicodeEncodeError:
            # Fallback for Windows console encoding issues
            print("\n[Output written to file - view dashboards/velocity_metrics.txt]")
        
        return output_file
        
    except Exception as e:
        print(f"[ERROR] Error calculating velocity metrics: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)
