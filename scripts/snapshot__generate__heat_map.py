"""
Script: snapshot__generate__heat_map.py
Intent:
- snapshot

Reads:
- registry/agent-registry.json
- state/legislative-state.json
- review/HR_*_queue.json (4 files)
- audit/audit-log.jsonl (optional, for recent errors)

Writes:
- dashboards/heat_map_snapshot.txt (operational, disposable)

Schema:
Terminal-readable text block showing system health snapshot with status indicators.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

# Path setup
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

# Constants
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
STATE_PATH = BASE_DIR / "state" / "legislative-state.json"
REVIEW_DIR = BASE_DIR / "review"
AUDIT_LOG_PATH = BASE_DIR / "audit" / "audit-log.jsonl"
DASHBOARDS_DIR = BASE_DIR / "dashboards"
DASHBOARDS_DIR.mkdir(parents=True, exist_ok=True)

# Thresholds for status determination
BLOCKED_YELLOW_THRESHOLD = 2
BLOCKED_RED_THRESHOLD = 5
REVIEW_YELLOW_THRESHOLD = 3
REVIEW_RED_THRESHOLD = 10

# State definitions
STATE_DEFINITIONS = {
    "PRE_EVT": "Policy Opportunity Detected",
    "INTRO_EVT": "Bill Vehicle Identified",
    "COMM_EVT": "Committee Referral",
    "FLOOR_EVT": "Floor Scheduled",
    "FINAL_EVT": "Vote Imminent",
    "IMPL_EVT": "Law Enacted",
}

# Review gate definitions
REVIEW_GATES = {
    "HR_PRE": "Concept Direction Review",
    "HR_LANG": "Legislative Language Review",
    "HR_MSG": "Messaging & Narrative Review",
    "HR_RELEASE": "Public Release Authorization",
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


def count_agents_by_status(agents: List[Dict[str, Any]]) -> Dict[str, int]:
    """Count agents by status."""
    counts = {
        "RUNNING": 0,
        "WAITING_REVIEW": 0,
        "BLOCKED": 0,
        "IDLE": 0,
        "RETIRED": 0,
        "FAILED": 0,
    }
    for agent in agents:
        status = agent.get("status", "UNKNOWN")
        if status in counts:
            counts[status] += 1
    return counts


def load_review_gates() -> Dict[str, Dict[str, Any]]:
    """Load all review gate queue files."""
    gates = {}
    if not REVIEW_DIR.exists():
        return gates
    
    for queue_file in REVIEW_DIR.glob("HR_*_queue.json"):
        gate_data = load_json(queue_file)
        gate_id = gate_data.get("_meta", {}).get("review_gate", "UNKNOWN")
        gates[gate_id] = gate_data
    
    return gates


def get_review_gate_summary(gate_data: Dict[str, Any]) -> Tuple[int, Optional[str]]:
    """Get pending count and last review status for a gate."""
    pending_count = len(gate_data.get("pending_reviews", []))
    
    # Get last review from history
    review_history = gate_data.get("review_history", [])
    last_review = None
    if review_history:
        last_review = review_history[-1]
        decision = last_review.get("decision", "")
        decision_at = last_review.get("decision_at", "")
        if decision_at:
            dt = parse_timestamp(decision_at)
            if dt:
                now = datetime.now(timezone.utc)
                age_seconds = (now - dt).total_seconds()
                age_str = format_duration(age_seconds)
                return pending_count, f"{decision} {age_str} ago"
    
    return pending_count, None


def analyze_state_advancement(state_data: Dict[str, Any], review_gates: Dict[str, Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """Analyze state advancement readiness."""
    current_state = state_data.get("current_state", "UNKNOWN")
    next_states = state_data.get("next_allowed_states", [])
    advancement_rule = state_data.get("state_advancement_rule", "")
    
    if not next_states:
        return False, ["No next states allowed (terminal state)"]
    
    next_state = next_states[0]
    blocking_reasons = []
    ready = True
    
    # Check for required approvals based on current state
    if current_state == "INTRO_EVT" and next_state == "COMM_EVT":
        # Need HR_PRE approval for INTRO artifacts
        hr_pre = review_gates.get("HR_PRE", {})
        pending = hr_pre.get("pending_reviews", [])
        if pending:
            ready = False
            blocking_reasons.append(f"HR_PRE approval pending ({len(pending)} items)")
        # Check if external confirmation needed
        if "external confirmation" in advancement_rule.lower():
            blocking_reasons.append("External confirmation: committee_referral")
    
    # Add more state-specific checks as needed
    
    return ready, blocking_reasons


def get_blocking_conditions(agents: List[Dict[str, Any]], review_gates: Dict[str, Dict[str, Any]]) -> List[str]:
    """Get list of blocking conditions."""
    blocking = []
    
    # Agents waiting for review
    waiting_agents = [a for a in agents if a.get("status") == "WAITING_REVIEW"]
    for agent in waiting_agents:
        agent_id = agent.get("agent_id", "unknown")
        # Try to determine which gate
        gate_id = "HR_PRE"  # Default, could be improved
        blocking.append(f"{agent_id}: WAITING_REVIEW ({gate_id})")
    
    # Blocked agents
    blocked_agents = [a for a in agents if a.get("status") == "BLOCKED"]
    for agent in blocked_agents:
        agent_id = agent.get("agent_id", "unknown")
        task = agent.get("current_task", "Blocked")
        blocking.append(f"{agent_id}: BLOCKED ({task})")
    
    return blocking


def check_recent_errors() -> bool:
    """Check for recent errors in audit log."""
    if not AUDIT_LOG_PATH.exists():
        return False
    
    try:
        now = datetime.now(timezone.utc)
        with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
            # Check last 20 lines for errors
            for line in lines[-20:]:
                try:
                    event = json.loads(line.strip())
                    event_type = event.get("event_type", "")
                    if event_type == "error":
                        timestamp = event.get("timestamp", "")
                        dt = parse_timestamp(timestamp)
                        if dt:
                            age_seconds = (now - dt).total_seconds()
                            # Consider errors in last hour as recent
                            if age_seconds < 3600:
                                return True
                except Exception:
                    continue
    except Exception:
        pass
    
    return False


def determine_overall_status(
    agent_counts: Dict[str, int],
    review_gates: Dict[str, Dict[str, Any]],
    state_ready: bool,
    has_errors: bool
) -> Tuple[str, str]:
    """Determine overall system status (GREEN/YELLOW/RED)."""
    blocked_count = agent_counts.get("BLOCKED", 0)
    waiting_count = agent_counts.get("WAITING_REVIEW", 0)
    
    # Count total pending reviews
    total_pending = sum(len(gate.get("pending_reviews", [])) for gate in review_gates.values())
    
    # Red conditions
    if has_errors:
        return "RED", "Recent errors in audit log"
    if blocked_count >= BLOCKED_RED_THRESHOLD:
        return "RED", f"{blocked_count} agents blocked (threshold: {BLOCKED_RED_THRESHOLD})"
    if total_pending >= REVIEW_RED_THRESHOLD:
        return "RED", f"{total_pending} pending reviews (threshold: {REVIEW_RED_THRESHOLD})"
    
    # Yellow conditions
    if blocked_count >= BLOCKED_YELLOW_THRESHOLD:
        return "YELLOW", f"{blocked_count} agents blocked"
    if total_pending >= REVIEW_YELLOW_THRESHOLD:
        return "YELLOW", f"{total_pending} pending reviews"
    if waiting_count > 0:
        return "YELLOW", f"{waiting_count} agents waiting for review"
    if not state_ready:
        return "YELLOW", "State advancement blocked"
    
    # Green
    return "GREEN", "All systems operational"


def format_status_banner(status: str, reason: str) -> str:
    """Create color-coded status banner with ASCII art."""
    status_icons = {
        "GREEN": "✓",
        "YELLOW": "⚠",
        "RED": "✗"
    }
    status_labels = {
        "GREEN": "SYSTEM STATUS: GREEN ✓",
        "YELLOW": "🔥 SYSTEM STATUS: YELLOW ⚠",
        "RED": "🔥 SYSTEM STATUS: RED ✗"
    }
    
    icon = status_icons.get(status, "?")
    label = status_labels.get(status, f"SYSTEM STATUS: {status}")
    
    # Create banner with box-drawing characters
    banner_width = 65
    lines = []
    lines.append("╔" + "═" * (banner_width - 2) + "╗")
    lines.append("║  " + label.ljust(banner_width - 6) + "  ║")
    lines.append("║  " + reason.ljust(banner_width - 6) + "  ║")
    lines.append("╚" + "═" * (banner_width - 2) + "╝")
    
    return "\n".join(lines)


def format_at_a_glance(
    state_data: Dict[str, Any],
    agent_counts: Dict[str, int],
    review_gates: Dict[str, Dict[str, Any]],
    state_ready: bool,
    time_in_state: Optional[str]
) -> str:
    """Create at-a-glance summary section with 3-5 key metrics."""
    lines = []
    lines.append("AT-A-GLANCE")
    lines.append("─" * 65)
    
    # State
    current_state = state_data.get("current_state", "UNKNOWN")
    state_def = STATE_DEFINITIONS.get(current_state, current_state)
    time_str = f" ({time_in_state} in state)" if time_in_state else ""
    lines.append(f"State:        {current_state} ({state_def}){time_str}")
    
    # Agent summary
    running = agent_counts.get("RUNNING", 0)
    waiting = agent_counts.get("WAITING_REVIEW", 0)
    blocked = agent_counts.get("BLOCKED", 0)
    idle = agent_counts.get("IDLE", 0)
    agent_summary = f"{running} RUNNING | {waiting} WAITING_REVIEW | {blocked} BLOCKED"
    if idle > 0:
        agent_summary += f" | {idle} IDLE"
    lines.append(f"Agents:       {agent_summary}")
    
    # Review summary
    total_pending = sum(len(gate.get("pending_reviews", [])) for gate in review_gates.values())
    if total_pending > 0:
        pending_breakdown = []
        for gate_id in ["HR_PRE", "HR_LANG", "HR_MSG", "HR_RELEASE"]:
            gate_data = review_gates.get(gate_id, {})
            pending = len(gate_data.get("pending_reviews", []))
            if pending > 0:
                pending_breakdown.append(f"{pending} {gate_id}")
        if pending_breakdown:
            lines.append(f"Reviews:      {total_pending} pending ({', '.join(pending_breakdown)})")
        else:
            lines.append(f"Reviews:      {total_pending} pending")
    else:
        lines.append(f"Reviews:      0 pending")
    
    # Advancement status
    if state_ready:
        lines.append(f"Advancement:  READY ✓")
    else:
        next_states = state_data.get("next_allowed_states", [])
        if next_states:
            lines.append(f"Advancement:  BLOCKED (requirements not met)")
        else:
            lines.append(f"Advancement:  N/A (terminal state)")
    
    return "\n".join(lines)


def format_visual_progress(current_seconds: float, expected_days: int, label: str) -> str:
    """Create ASCII progress bar for time visualization."""
    if expected_days is None or expected_days <= 0:
        return f"{label}: No expected time"
    
    expected_seconds = expected_days * 24 * 3600
    progress = min(current_seconds / expected_seconds, 1.0)  # Cap at 100%
    
    bar_width = 30
    filled = int(progress * bar_width)
    bar = "█" * filled + "░" * (bar_width - filled)
    
    progress_pct = int(progress * 100)
    current_str = format_duration(current_seconds)
    expected_str = f"{expected_days}d"
    
    return f"{label}: [{bar}] {current_str} / {expected_str} ({progress_pct}% complete)"


def format_actions_needed(
    blocking_conditions: List[str],
    bottlenecks: List[Tuple[str, str]],
    review_gates: Dict[str, Dict[str, Any]],
    state_ready: bool
) -> str:
    """Create prioritized actions section with clear commands."""
    lines = []
    lines.append("IMMEDIATE ACTIONS")
    lines.append("─" * 65)
    
    actions = []
    
    # High priority: Blocked agents
    blocked_agents = [b for b in blocking_conditions if "BLOCKED" in b]
    if blocked_agents:
        for agent_block in blocked_agents[:3]:  # Limit to 3
            agent_id = agent_block.split(":")[0] if ":" in agent_block else "agent"
            actions.append((
                "HIGH",
                f"Authorize blocked execution agent: {agent_id}",
                f"python scripts/cockpit__authorize_execution.py"
            ))
    
    # High priority: Pending reviews over threshold
    # Use standard thresholds (in minutes)
    review_thresholds = {
        "HR_PRE": 90,
        "HR_LANG": 90,
        "HR_MSG": 30,
        "HR_RELEASE": 10,
    }
    for gate_id, gate_data in review_gates.items():
        pending = gate_data.get("pending_reviews", [])
        if pending:
            threshold = review_thresholds.get(gate_id, 90)
            urgent = []
            for review in pending:
                submitted_at = parse_timestamp(review.get("submitted_at", ""))
                if submitted_at:
                    now = datetime.now(timezone.utc)
                    age_minutes = (now - submitted_at).total_seconds() / 60
                    if age_minutes > threshold:
                        urgent.append(review)
            
            if urgent:
                actions.append((
                    "HIGH",
                    f"Review {len(urgent)} urgent {gate_id} artifact(s) (over {threshold}m threshold)",
                    f"python scripts/cockpit__list__pending_approvals.py"
                ))
            elif len(pending) >= 3:
                actions.append((
                    "MEDIUM",
                    f"Review {len(pending)} pending {gate_id} artifact(s)",
                    f"python scripts/cockpit__list__pending_approvals.py"
                ))
    
    # Medium priority: Bottlenecks
    for priority, desc in bottlenecks[:3]:  # Top 3 bottlenecks
        if priority == "HIGH" and not any(a[0] == "HIGH" and "bottleneck" not in a[1].lower() for a in actions):
            actions.append((
                priority,
                f"Address bottleneck: {desc}",
                "python scripts/velocity__calculate__metrics.py"
            ))
    
    # State advancement
    if not state_ready:
        next_states = review_gates.get("_state_data", {}).get("next_allowed_states", [])
        if next_states:
            actions.append((
                "MEDIUM",
                "Review state advancement requirements",
                "python scripts/cockpit__advance_state.py"
            ))
    
    if not actions:
        lines.append("  No immediate actions required ✓")
    else:
        # Sort by priority
        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        actions.sort(key=lambda x: (priority_order.get(x[0], 99), x[1]))
        
        for idx, (priority, what, command) in enumerate(actions[:5], 1):  # Top 5
            lines.append(f"{idx}. [{priority}] {what}")
            lines.append(f"   → {command}")
            if idx < len(actions[:5]):
                lines.append("")
    
    return "\n".join(lines)


def determine_display_mode(status: str) -> str:
    """Determine display mode based on status (minimal/standard/expanded)."""
    if status == "GREEN":
        return "minimal"
    elif status == "YELLOW":
        return "standard"
    else:  # RED
        return "expanded"


def calculate_time_in_state(state_data: Dict[str, Any]) -> Optional[str]:
    """Calculate time spent in current state."""
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
                    age_seconds = (now - dt).total_seconds()
                    return format_duration(age_seconds)
    
    return None


def generate_heat_map() -> str:
    """Generate heat map snapshot text."""
    # Load canonical data
    registry_data = load_json(REGISTRY_PATH)
    state_data = load_json(STATE_PATH)
    review_gates = load_review_gates()
    
    agents = registry_data.get("agents", [])
    agent_counts = count_agents_by_status(agents)
    
    # Analyze state advancement
    state_ready, blocking_reasons = analyze_state_advancement(state_data, review_gates)
    
    # Check for errors
    has_errors = check_recent_errors()
    
    # Determine overall status
    status_color, status_reason = determine_overall_status(
        agent_counts, review_gates, state_ready, has_errors
    )
    
    # Calculate time in state
    time_in_state = calculate_time_in_state(state_data)
    
    # Determine display mode
    display_mode = determine_display_mode(status_color)
    
    # Build output
    output_lines = []
    
    # Status banner (always shown)
    output_lines.append(format_status_banner(status_color, status_reason))
    output_lines.append("")
    
    # At-a-glance summary (always shown)
    output_lines.append(format_at_a_glance(state_data, agent_counts, review_gates, state_ready, time_in_state))
    output_lines.append("")
    
    # Detailed sections (conditional based on display mode)
    if display_mode in ["standard", "expanded"]:
        # Agent status
        output_lines.append("AGENT STATUS")
        output_lines.append("─" * 65)
        output_lines.append(f"  RUNNING:       {agent_counts['RUNNING']}")
        output_lines.append(f"  WAITING_REVIEW: {agent_counts['WAITING_REVIEW']}")
        output_lines.append(f"  BLOCKED:       {agent_counts['BLOCKED']}")
        output_lines.append(f"  IDLE:          {agent_counts['IDLE']}")
        output_lines.append(f"  RETIRED:       {agent_counts['RETIRED']}")
        output_lines.append("")
        
        # Review gates
        output_lines.append("REVIEW GATES")
        output_lines.append("─" * 65)
        for gate_id in ["HR_PRE", "HR_LANG", "HR_MSG", "HR_RELEASE"]:
            gate_data = review_gates.get(gate_id, {})
            pending_count, last_review = get_review_gate_summary(gate_data)
            gate_name = REVIEW_GATES.get(gate_id, gate_id)
            if pending_count > 0:
                output_lines.append(f"  {gate_id}: {pending_count} pending")
            elif last_review:
                output_lines.append(f"  {gate_id}: 0 pending (last: {last_review})")
            else:
                output_lines.append(f"  {gate_id}: 0 pending")
        output_lines.append("")
        
        # State advancement
        output_lines.append("STATE ADVANCEMENT")
        output_lines.append("─" * 65)
        current_state = state_data.get("current_state", "UNKNOWN")
        next_states = state_data.get("next_allowed_states", [])
        if next_states:
            next_state = next_states[0]
            output_lines.append(f"  Current: {current_state}")
            output_lines.append(f"  Next:    {next_state}")
            if state_ready:
                output_lines.append("  Ready:   YES ✓")
            else:
                output_lines.append("  Ready:   NO ✗")
                for reason in blocking_reasons:
                    output_lines.append(f"    Missing: {reason}")
        else:
            output_lines.append(f"  Current: {current_state}")
            output_lines.append("  Next:    N/A (terminal state)")
        output_lines.append("")
        
        # Blocking conditions (expanded mode only)
        if display_mode == "expanded":
            blocking = get_blocking_conditions(agents, review_gates)
            if blocking:
                output_lines.append("BLOCKING CONDITIONS")
                output_lines.append("─" * 65)
                for condition in blocking[:10]:  # More in expanded mode
                    output_lines.append(f"  - {condition}")
                if len(blocking) > 10:
                    output_lines.append(f"  ... and {len(blocking) - 10} more")
                output_lines.append("")
    
    # Actions needed (always shown, but more detailed in expanded mode)
    blocking = get_blocking_conditions(agents, review_gates)
    # Get bottlenecks from velocity if available (simplified for now)
    bottlenecks = []
    if display_mode == "expanded":
        # In expanded mode, we could load velocity data, but for now use blocking conditions
        bottlenecks = [(status_color if status_color != "GREEN" else "MEDIUM", bc) for bc in blocking[:3]]
    
    output_lines.append(format_actions_needed(blocking, bottlenecks, review_gates, state_ready))
    
    return "\n".join(output_lines)


def main():
    """Main execution."""
    print("[snapshot__generate__heat_map] Generating heat map snapshot...")
    
    try:
        heat_map_text = generate_heat_map()
        
        # Write to file
        output_file = DASHBOARDS_DIR / "heat_map_snapshot.txt"
        output_file.write_text(heat_map_text, encoding="utf-8")
        
        print(f"[OK] Heat map snapshot written to: {output_file}")
        try:
            print("\n" + heat_map_text)
        except UnicodeEncodeError:
            # Fallback for Windows console encoding issues
            print("\n[Output written to file - view dashboards/heat_map_snapshot.txt]")
        
        return output_file
        
    except Exception as e:
        print(f"[ERROR] Error generating heat map: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)
