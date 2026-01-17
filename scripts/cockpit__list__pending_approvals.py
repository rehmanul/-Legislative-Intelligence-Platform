"""
Script: cockpit__list__pending_approvals.py
Intent:
- snapshot

Reads:
- review/HR_*_queue.json (4 files)
- state/legislative-state.json
- registry/agent-registry.json

Writes:
- dashboards/cockpit_pending.txt (operational, disposable)

Schema:
Copy-paste friendly approval list showing all pending reviews, state advancement readiness, and execution authorizations.
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
REVIEW_DIR = BASE_DIR / "review"
STATE_PATH = BASE_DIR / "state" / "legislative-state.json"
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
DASHBOARDS_DIR = BASE_DIR / "dashboards"
DASHBOARDS_DIR.mkdir(parents=True, exist_ok=True)

# Review gate definitions
REVIEW_GATES = {
    "HR_PRE": "Concept Direction Review",
    "HR_LANG": "Legislative Language Review",
    "HR_MSG": "Messaging & Narrative Review",
    "HR_RELEASE": "Public Release Authorization",
}

# State definitions
STATE_DEFINITIONS = {
    "PRE_EVT": "Policy Opportunity Detected",
    "INTRO_EVT": "Bill Vehicle Identified",
    "COMM_EVT": "Committee Referral",
    "FLOOR_EVT": "Floor Scheduled",
    "FINAL_EVT": "Vote Imminent",
    "IMPL_EVT": "Law Enacted",
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


def analyze_state_advancement(state_data: Dict[str, Any], review_gates: Dict[str, Dict[str, Any]]) -> Tuple[bool, List[str], List[str]]:
    """Analyze state advancement readiness."""
    current_state = state_data.get("current_state", "UNKNOWN")
    next_states = state_data.get("next_allowed_states", [])
    advancement_rule = state_data.get("state_advancement_rule", "")
    
    if not next_states:
        return False, ["No next states allowed (terminal state)"], []
    
    next_state = next_states[0]
    blocking_reasons = []
    met_requirements = []
    ready = True
    
    # Check for required approvals based on current state
    if current_state == "INTRO_EVT" and next_state == "COMM_EVT":
        # Need HR_PRE approval for INTRO artifacts
        hr_pre = review_gates.get("HR_PRE", {})
        pending = hr_pre.get("pending_reviews", [])
        approved = hr_pre.get("review_history", [])
        has_approved = any(r.get("decision") == "APPROVED" for r in approved)
        
        if pending:
            ready = False
            blocking_reasons.append(f"HR_PRE approval pending ({len(pending)} items)")
        elif has_approved:
            met_requirements.append("HR_PRE approval (approved)")
        else:
            ready = False
            blocking_reasons.append("HR_PRE approval required")
        
        # Check if external confirmation needed
        if "external confirmation" in advancement_rule.lower():
            blocking_reasons.append("External confirmation: committee_referral")
    
    return ready, blocking_reasons, met_requirements


def get_execution_authorizations(registry_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get execution agents awaiting authorization."""
    agents = registry_data.get("agents", [])
    blocked_execution = []
    
    for agent in agents:
        if agent.get("status") == "BLOCKED" and agent.get("agent_type") == "Execution":
            blocked_execution.append({
                "agent_id": agent.get("agent_id", "unknown"),
                "current_task": agent.get("current_task", "Blocked"),
                "risk_level": agent.get("risk_level", "UNKNOWN"),
                "guidance_signed": agent.get("guidance_signed", False),
            })
    
    return blocked_execution


def generate_cockpit_list() -> str:
    """Generate cockpit pending approvals list."""
    # Load canonical data
    review_gates = {}
    if REVIEW_DIR.exists():
        for queue_file in REVIEW_DIR.glob("HR_*_queue.json"):
            gate_data = load_json(queue_file)
            gate_id = gate_data.get("_meta", {}).get("review_gate", "UNKNOWN")
            review_gates[gate_id] = gate_data
    
    state_data = load_json(STATE_PATH)
    registry_data = load_json(REGISTRY_PATH)
    
    # Analyze state advancement
    state_ready, blocking_reasons, met_requirements = analyze_state_advancement(state_data, review_gates)
    
    # Get execution authorizations
    execution_auths = get_execution_authorizations(registry_data)
    
    # Build output
    output_lines = []
    output_lines.append("PENDING APPROVALS")
    output_lines.append("=" * 80)
    output_lines.append("")
    
    # Review gates
    has_pending = False
    for gate_id in ["HR_PRE", "HR_LANG", "HR_MSG", "HR_RELEASE"]:
        gate_data = review_gates.get(gate_id, {})
        gate_name = REVIEW_GATES.get(gate_id, gate_id)
        pending_reviews = gate_data.get("pending_reviews", [])
        
        if pending_reviews:
            has_pending = True
            output_lines.append(f"{gate_id} ({gate_name})")
            for idx, review in enumerate(pending_reviews, 1):
                artifact_name = review.get("artifact_name", "Unknown Artifact")
                agent_id = review.get("submitted_by", "unknown")
                risk_level = review.get("risk_level", "UNKNOWN")
                effort = review.get("review_effort_estimate", "Unknown")
                submitted_at = review.get("submitted_at", "")
                
                # Calculate age
                age_str = "Unknown"
                if submitted_at:
                    dt = parse_timestamp(submitted_at)
                    if dt:
                        now = datetime.now(timezone.utc)
                        age_seconds = (now - dt).total_seconds()
                        age_str = format_duration(age_seconds)
                
                output_lines.append(f"  [{idx}] {artifact_name}")
                output_lines.append(f"      Agent: {agent_id}")
                output_lines.append(f"      Risk: {risk_level}")
                output_lines.append(f"      Effort: {effort}")
                output_lines.append(f"      Submitted: {age_str} ago")
                output_lines.append(f"      [APPROVE] [REJECT] [VIEW]")
                output_lines.append("")
        else:
            output_lines.append(f"{gate_id} ({gate_name})")
            output_lines.append("  [No pending reviews]")
            output_lines.append("")
    
    if not has_pending:
        output_lines.append("No pending reviews at this time.")
        output_lines.append("")
    
    # State advancement
    output_lines.append("STATE ADVANCEMENT")
    output_lines.append("-" * 80)
    current_state = state_data.get("current_state", "UNKNOWN")
    next_states = state_data.get("next_allowed_states", [])
    
    if next_states:
        next_state = next_states[0]
        current_def = STATE_DEFINITIONS.get(current_state, current_state)
        next_def = STATE_DEFINITIONS.get(next_state, next_state)
        
        output_lines.append(f"Current: {current_state} ({current_def})")
        output_lines.append(f"Next:    {next_state} ({next_def})")
        output_lines.append("Requirements:")
        
        for req in met_requirements:
            output_lines.append(f"  [OK] {req}")
        
        for req in blocking_reasons:
            output_lines.append(f"  [X] {req}")
        
        if state_ready:
            output_lines.append("")
            output_lines.append("[ADVANCE STATE] (ready)")
        else:
            output_lines.append("")
            output_lines.append("[ADVANCE STATE] (disabled: requirements not met)")
    else:
        output_lines.append(f"Current: {current_state}")
        output_lines.append("Next:    N/A (terminal state)")
    
    output_lines.append("")
    
    # Execution authorizations
    output_lines.append("EXECUTION AUTHORIZATIONS")
    output_lines.append("-" * 80)
    if execution_auths:
        for auth in execution_auths:
            agent_id = auth.get("agent_id", "unknown")
            task = auth.get("current_task", "Blocked")
            risk = auth.get("risk_level", "UNKNOWN")
            guidance = "[OK]" if auth.get("guidance_signed") else "[X]"
            
            output_lines.append(f"Agent: {agent_id}")
            output_lines.append(f"  Status: {task}")
            output_lines.append(f"  Risk: {risk}")
            output_lines.append(f"  Guidance signed: {guidance}")
            output_lines.append(f"  [AUTHORIZE] [VIEW PLAN]")
            output_lines.append("")
    else:
        output_lines.append("[No pending authorizations]")
    
    # Recent review history (last 5)
    output_lines.append("")
    output_lines.append("RECENT REVIEW HISTORY (Last 5)")
    output_lines.append("-" * 80)
    
    all_history = []
    for gate_id, gate_data in review_gates.items():
        history = gate_data.get("review_history", [])
        for review in history:
            review["gate_id"] = gate_id
            all_history.append(review)
    
    # Sort by decision_at (most recent first)
    all_history.sort(key=lambda x: x.get("decision_at", ""), reverse=True)
    
    for review in all_history[:5]:
        gate_id = review.get("gate_id", "UNKNOWN")
        artifact_name = review.get("artifact_name", "Unknown")
        decision = review.get("decision", "UNKNOWN")
        decision_at = review.get("decision_at", "")
        decision_by = review.get("decision_by", "unknown")
        
        age_str = "Unknown"
        if decision_at:
            dt = parse_timestamp(decision_at)
            if dt:
                now = datetime.now(timezone.utc)
                age_seconds = (now - dt).total_seconds()
                age_str = format_duration(age_seconds)
        
        output_lines.append(f"{gate_id}: {artifact_name} - {decision} by {decision_by} ({age_str} ago)")
    
    if not all_history:
        output_lines.append("No review history available.")
    
    return "\n".join(output_lines)


def main():
    """Main execution."""
    print("[cockpit__list__pending_approvals] Generating cockpit pending approvals list...")
    
    try:
        cockpit_text = generate_cockpit_list()
        
        # Write to file
        output_file = DASHBOARDS_DIR / "cockpit_pending.txt"
        output_file.write_text(cockpit_text, encoding="utf-8")
        
        print(f"[OK] Cockpit pending approvals list written to: {output_file}")
        print("\n" + cockpit_text)
        
        return output_file
        
    except Exception as e:
        print(f"[ERROR] Error generating cockpit list: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)
