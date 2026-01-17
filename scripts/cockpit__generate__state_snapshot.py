"""
Script: cockpit__generate__state_snapshot.py
Intent:
- snapshot

Reads:
- registry/agent-registry.json
- state/legislative-state.json
- review/*_queue.json files
- audit/audit-log.jsonl

Writes:
- dashboards/cockpit_state.out.json

Schema:
- cockpit_state_snapshot schema (see _meta block)
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Paths
BASE_DIR = Path(__file__).parent.parent
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
STATE_PATH = BASE_DIR / "state" / "legislative-state.json"
REVIEW_DIR = BASE_DIR / "review"
AUDIT_LOG_PATH = BASE_DIR / "audit" / "audit-log.jsonl"
OUTPUT_DIR = BASE_DIR / "dashboards"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "cockpit_state.out.json"

# Add lib to path for revolving-door observability
sys.path.insert(0, str(BASE_DIR))

# Try to import revolving-door observability (optional)
try:
    from lib.revolving_door_observability import (
        get_revolving_door_kpis,
        get_revolving_door_events,
        get_revolving_door_status
    )
    from lib.revolving_door_intelligence import analyze_revolving_door_situation
    REVOLVING_DOOR_AVAILABLE = True
except ImportError:
    REVOLVING_DOOR_AVAILABLE = False


def load_json(path: Path) -> Dict[str, Any]:
    """Load JSON file, return {} if not found or invalid."""
    try:
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, Exception):
        return {}


def load_jsonl(path: Path, limit: int = 50) -> List[Dict[str, Any]]:
    """Load last N lines from JSONL file."""
    lines = []
    if not path.exists():
        return lines
    try:
        with open(path, "r", encoding="utf-8") as f:
            all_lines = f.readlines()
            for line in all_lines[-limit:]:
                line = line.strip()
                if line:
                    try:
                        lines.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except Exception:
        pass
    return lines


def parse_timestamp(ts_str: str) -> Optional[datetime]:
    """Parse ISO timestamp to datetime object."""
    # Use robust timestamp parser from lib
    try:
        from lib.timestamp_utils import parse_timestamp as robust_parse_timestamp
        return robust_parse_timestamp(ts_str)
    except ImportError:
        # Fallback to simple parsing if lib not available
        if not ts_str:
            return None
        try:
            ts_str = ts_str.replace("Z", "+00:00")
            dt = datetime.fromisoformat(ts_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            return None


def load_pending_reviews() -> List[Dict[str, Any]]:
    """Load all pending reviews from review queue files."""
    pending_reviews: List[Dict[str, Any]] = []
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
                
                pending_reviews.append({
                    "review_id": review.get("review_id", "unknown"),
                    "artifact_name": review.get("artifact_name", "Unknown Artifact"),
                    "artifact_path": str(relative_path),
                    "full_path": str(full_path) if str(full_path) else "",
                    "gate_id": gate_id,
                    "gate_name": gate_name,
                    "submitted_at": review.get("submitted_at", ""),
                    "submitted_by": review.get("submitted_by", "unknown"),
                    "review_effort_estimate": review.get("review_effort_estimate", ""),
                    "risk_level": review.get("risk_level", ""),
                })
        except Exception:
            continue
    
    return pending_reviews


def get_review_gate_from_artifact(agent_id: str, artifact_path: str = None) -> Optional[str]:
    """Get review gate from artifact metadata."""
    # Try to find artifact file and read requires_review from _meta
    if artifact_path:
        try:
            full_path = BASE_DIR / artifact_path if not Path(artifact_path).is_absolute() else Path(artifact_path)
            if full_path.exists():
                artifact_data = load_json(full_path)
                meta = artifact_data.get("_meta", {})
                return meta.get("requires_review")
        except Exception:
            pass
    
    # Fallback: try to find artifact in agent's output directory
    try:
        agent_artifacts_dir = BASE_DIR / "artifacts" / agent_id
        if agent_artifacts_dir.exists():
            for artifact_file in agent_artifacts_dir.glob("*.json"):
                artifact_data = load_json(artifact_file)
                meta = artifact_data.get("_meta", {})
                requires_review = meta.get("requires_review")
                if requires_review:
                    return requires_review
    except Exception:
        pass
    
    return None


def generate_alerts(registry_data: Dict[str, Any], state_data: Dict[str, Any], reviews: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate alerts from system state."""
    alerts: List[Dict[str, Any]] = []
    now = datetime.now(timezone.utc)
    
    # Check for agents waiting review
    agents_list = registry_data.get("agents", [])
    waiting_review = [a for a in agents_list if a.get("status") == "WAITING_REVIEW"]
    if waiting_review:
        for agent in waiting_review:
            agent_id = agent.get("agent_id")
            # Try to get review gate from artifact metadata
            review_gate = None
            # Check agent outputs for artifact path
            outputs = agent.get("outputs", [])
            if outputs:
                artifact_path = outputs[0] if isinstance(outputs, list) else outputs
                review_gate = get_review_gate_from_artifact(agent_id, artifact_path)
            
            # If still not found, try without path
            if not review_gate:
                review_gate = get_review_gate_from_artifact(agent_id)
            
            alerts.append({
                "level": "warning",
                "message": f"Agent {agent_id} awaiting review",
                "timestamp": now.isoformat() + "Z",
                "agent_id": agent_id,
                "review_gate": review_gate or "UNKNOWN"
            })
    
    # Check for stale agents
    for agent in agents_list:
        if agent.get("status") == "RUNNING":
            heartbeat_str = agent.get("last_heartbeat", "")
            if heartbeat_str:
                heartbeat_dt = parse_timestamp(heartbeat_str)
                if heartbeat_dt:
                    age_minutes = (now - heartbeat_dt.replace(tzinfo=timezone.utc)).total_seconds() / 60
                    if age_minutes > 30:  # Stale threshold
                        alerts.append({
                            "level": "warning",
                            "message": f"Agent {agent.get('agent_id')} may be stuck (last heartbeat {age_minutes:.0f} minutes ago)",
                            "timestamp": now.isoformat() + "Z",
                            "agent_id": agent.get("agent_id")
                        })
    
    # Check for pending reviews
    if reviews:
        alerts.append({
            "level": "info",
            "message": f"{len(reviews)} pending review(s) require human approval",
            "timestamp": now.isoformat() + "Z",
            "pending_count": len(reviews)
        })
    
    # Check for state lock
    if state_data.get("state_lock", False):
        alerts.append({
            "level": "warning",
            "message": "Legislative state is locked (orchestrator active)",
            "timestamp": now.isoformat() + "Z"
        })
    
    # Default info if no alerts
    if not alerts:
        alerts.append({
            "level": "info",
            "message": "System operating normally",
            "timestamp": now.isoformat() + "Z"
        })
    
    return alerts


def load_revolving_door_data(current_phase: str) -> Dict[str, Any]:
    """Load revolving-door KPIs and status (optional, graceful failure)."""
    if not REVOLVING_DOOR_AVAILABLE:
        return {
            "available": False,
            "error": "Revolving-door observability not available"
        }
    
    try:
        now = datetime.now(timezone.utc)
        
        # Get KPIs
        kpis = get_revolving_door_kpis(now)
        
        # Get active events
        active_events = get_revolving_door_events(now, include_expired=False)
        
        # Get status for each event
        event_statuses = []
        for event in active_events[:10]:  # Limit to 10 most recent
            status = get_revolving_door_status(event, now)
            event_statuses.append({
                "event_id": status.get("event_id"),
                "entity_id": status.get("entity_id"),
                "from_role": status.get("from_role"),
                "to_role": status.get("to_role"),
                "days_since": status.get("days_since"),
                "remaining_days": status.get("remaining_days"),
                "decay_status": status.get("decay_status"),
                "boost_factor": status.get("boost_factor"),
                "is_active": status.get("is_active")
            })
        
        # Analyze situation
        analysis = analyze_revolving_door_situation(now, current_phase)
        
        return {
            "available": True,
            "kpis": kpis,
            "active_events_count": len(active_events),
            "event_statuses": event_statuses,
            "summary": analysis.get("summary", {}),
            "current_phase": current_phase,
            "phase_sensitivity": {
                "PRE_EVT": 1.0,
                "INTRO_EVT": 0.9,
                "COMM_EVT": 0.7,
                "FLOOR_EVT": 0.4,
                "FINAL_EVT": 0.2,
                "IMPL_EVT": 0.0
            }.get(current_phase, 1.0)
        }
    except Exception as e:
        return {
            "available": True,
            "error": f"Failed to load revolving-door data: {str(e)}"
        }


def generate_snapshot() -> Dict[str, Any]:
    """Generate complete state snapshot from file-based sources."""
    now = datetime.now(timezone.utc)
    
    # Load data from files
    registry_data = load_json(REGISTRY_PATH)
    state_data = load_json(STATE_PATH)
    pending_reviews = load_pending_reviews()
    recent_audit_entries = load_jsonl(AUDIT_LOG_PATH, limit=20)
    
    # Get current phase for revolving-door analysis
    current_phase = state_data.get("current_state", "UNKNOWN")
    
    # Load revolving-door data (optional)
    revolving_door_data = load_revolving_door_data(current_phase)
    
    # Extract agent statistics
    agents_list = registry_data.get("agents", [])
    agent_counts = {
        "running": len([a for a in agents_list if a.get("status") == "RUNNING"]),
        "waiting_review": len([a for a in agents_list if a.get("status") == "WAITING_REVIEW"]),
        "idle": len([a for a in agents_list if a.get("status") == "IDLE"]),
        "retired": len([a for a in agents_list if a.get("status") == "RETIRED"]),
        "blocked": len([a for a in agents_list if a.get("status") == "BLOCKED"]),
        "total": len(agents_list)
    }
    
    # Generate alerts
    alerts = generate_alerts(registry_data, state_data, pending_reviews)
    
    # Compute conversion pipeline status (pending reviews by gate)
    conversion_pipeline_status = {}
    for review in pending_reviews:
        gate_id = review.get("gate_id", "UNKNOWN")
        if gate_id not in conversion_pipeline_status:
            conversion_pipeline_status[gate_id] = {
                "gate_name": review.get("gate_name", "Unknown Gate"),
                "pending_count": 0,
                "artifacts": []
            }
        conversion_pipeline_status[gate_id]["pending_count"] += 1
        conversion_pipeline_status[gate_id]["artifacts"].append({
            "artifact_name": review.get("artifact_name"),
            "submitted_at": review.get("submitted_at"),
            "risk_level": review.get("risk_level")
        })
    
    # Compute audit completeness explanation
    audit_completeness_explanation = None
    try:
        # Try to load KPI state for audit completeness
        kpi_state_path = BASE_DIR / "metrics" / "kpi_state.json"
        if kpi_state_path.exists():
            kpi_state = load_json(kpi_state_path)
            system_health = kpi_state.get("metrics", {}).get("system_health", {})
            audit_completeness = system_health.get("audit_completeness", {})
            decision_log_coverage = audit_completeness.get("decision_log_coverage", 0.0)
            
            if decision_log_coverage < 90.0:
                # Count actionable artifacts
                actionable_count = 0
                artifacts_with_logs = 0
                artifacts_dir = BASE_DIR / "artifacts"
                if artifacts_dir.exists():
                    for agent_dir in artifacts_dir.iterdir():
                        if not agent_dir.is_dir():
                            continue
                        for artifact_file in agent_dir.glob("*.json"):
                            try:
                                data = load_json(artifact_file)
                                meta = data.get("_meta", {})
                                if meta.get("status") == "ACTIONABLE" or meta.get("approved_at"):
                                    actionable_count += 1
                                    # Check if has decision log
                                    requires_review = meta.get("requires_review")
                                    if requires_review:
                                        queue_file = BASE_DIR / "review" / f"{requires_review}_queue.json"
                                        if queue_file.exists():
                                            queue_data = load_json(queue_file)
                                            approved_reviews = queue_data.get("approved_reviews", [])
                                            artifact_path = str(artifact_file.relative_to(BASE_DIR))
                                            for review_entry in approved_reviews:
                                                if artifact_file.name in str(review_entry.get("artifact_path", "")) or artifact_path in str(review_entry.get("artifact_path", "")):
                                                    artifacts_with_logs += 1
                                                    break
                                    else:
                                        artifacts_with_logs += 1  # No review required
                            except Exception:
                                continue
                
                missing_logs = actionable_count - artifacts_with_logs
                if missing_logs > 0:
                    audit_completeness_explanation = {
                        "coverage": decision_log_coverage,
                        "actionable_artifacts": actionable_count,
                        "artifacts_with_logs": artifacts_with_logs,
                        "missing_logs": missing_logs,
                        "reason": f"{missing_logs} actionable artifact(s) missing decision log entries"
                    }
    except Exception:
        pass
    
    # Build snapshot
    snapshot = {
        "_meta": {
            "generated_at": now.isoformat() + "Z",
            "source": "file_based",
            "schema_version": "1.0.0",
            "files_read": {
                "registry": str(REGISTRY_PATH.relative_to(BASE_DIR)) if REGISTRY_PATH.exists() else None,
                "state": str(STATE_PATH.relative_to(BASE_DIR)) if STATE_PATH.exists() else None,
                "review_dir": str(REVIEW_DIR.relative_to(BASE_DIR)) if REVIEW_DIR.exists() else None,
                "audit_log": str(AUDIT_LOG_PATH.relative_to(BASE_DIR)) if AUDIT_LOG_PATH.exists() else None
            }
        },
        "timestamp": now.isoformat() + "Z",
        "system": {
            "status": "active",
            "current_state": state_data.get("current_state", "UNKNOWN"),
            "state_definition": state_data.get("state_definition", ""),
            "state_lock": state_data.get("state_lock", False),
            "next_allowed_states": state_data.get("next_allowed_states", []),
            "state_advancement_rule": state_data.get("state_advancement_rule", ""),
            "agents": agent_counts
        },
        "legislative": {
            "current_state": state_data.get("current_state", "UNKNOWN"),
            "state_definition": state_data.get("state_definition", ""),
            "state_lock": state_data.get("state_lock", False),
            "state_history": state_data.get("state_history", []),
            "next_allowed_states": state_data.get("next_allowed_states", []),
            "state_advancement_rule": state_data.get("state_advancement_rule", "")
        },
        "agents": {
            "_meta": {
                "total_agents": agent_counts["total"],
                "active_agents": agent_counts["running"],
                "idle_agents": agent_counts["idle"],
                "waiting_review_agents": agent_counts["waiting_review"],
                "blocked_agents": agent_counts["blocked"],
                "retired_agents": agent_counts["retired"],
                "last_updated": registry_data.get("_meta", {}).get("last_updated", now.isoformat() + "Z")
            },
            "agents": agents_list
        },
        "reviews": pending_reviews,
        "review_gates": [
            {
                "gate_id": review.get("gate_id", "UNKNOWN"),
                "gate_name": review.get("gate_name", "Unknown Gate"),
                "status": "PENDING",
                "artifact_name": review.get("artifact_name"),
                "artifact_path": review.get("artifact_path"),
                "submitted_at": review.get("submitted_at"),
                "risk_level": review.get("risk_level", "")
            }
            for review in pending_reviews
        ],
        "alerts": alerts,
        "recent_activity": recent_audit_entries[-10:] if recent_audit_entries else [],
        "conversion_pipeline": {
            "status": conversion_pipeline_status,
            "total_pending": len(pending_reviews),
            "by_gate": {gate_id: info["pending_count"] for gate_id, info in conversion_pipeline_status.items()}
        },
        "audit_completeness": {
            "explanation": audit_completeness_explanation
        },
        "temporal": {
            "revolving_door": revolving_door_data
        }
    }
    
    return snapshot


def main() -> Optional[Path]:
    """Main execution: generate state snapshot."""
    print(f"[cockpit__generate__state_snapshot] Generating state snapshot...")
    
    try:
        snapshot = generate_snapshot()
        
        # Write snapshot
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False)
        
        print(f"[cockpit__generate__state_snapshot] Snapshot generated: {OUTPUT_FILE}")
        print(f"  - Agents: {snapshot['system']['agents']['total']} total ({snapshot['system']['agents']['running']} running)")
        print(f"  - Reviews: {len(snapshot['reviews'])} pending")
        print(f"  - Alerts: {len(snapshot['alerts'])}")
        print(f"  - State: {snapshot['system']['current_state']}")
        
        # Revolving-door status
        rd_data = snapshot.get("temporal", {}).get("revolving_door", {})
        if rd_data.get("available"):
            kpis = rd_data.get("kpis", {})
            print(f"  - Revolving-door: {kpis.get('active_count', 0)} active events")
        else:
            print(f"  - Revolving-door: Not available")
        
        return OUTPUT_FILE
        
    except Exception as e:
        print(f"[cockpit__generate__state_snapshot] ERROR: Error generating snapshot: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = main()
    if result:
        print(f"\nSnapshot ready: {result}")
    else:
        print("\nSnapshot generation failed")
        exit(1)
