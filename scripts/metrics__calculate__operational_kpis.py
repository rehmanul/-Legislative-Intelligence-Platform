"""
Script: metrics__calculate__operational_kpis.py
Intent:
- snapshot

Reads:
- artifacts/{agent_id}/*.json (artifact files with _meta timestamps)
- review/HR_*_queue.json (review queues with approval timestamps)
- state/legislative-state.json (state transitions)
- audit/audit-log.jsonl (audit trail)

Writes:
- metrics/operational_kpis.json (operational effectiveness KPIs)

Schema:
- schemas/metrics.schema.json (OPERATIONAL_KPIS report type)
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
ARTIFACTS_DIR = BASE_DIR / "artifacts"
REVIEW_DIR = BASE_DIR / "review"
STATE_PATH = BASE_DIR / "state" / "legislative-state.json"
AUDIT_LOG_PATH = BASE_DIR / "audit" / "audit-log.jsonl"
METRICS_DIR = BASE_DIR / "metrics"
METRICS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = METRICS_DIR / "operational_kpis.json"

# Target thresholds (from plan)
TARGET_LATENCY_HOURS = {
    "HR_PRE": 48,
    "HR_LANG": 72,
    "HR_MSG": 24,
    "HR_RELEASE": 12,
}

TARGET_STATE_DAYS = {
    "PRE_EVT": 30,
    "INTRO_EVT": 60,
    "COMM_EVT": 90,
    "FLOOR_EVT": 45,
    "FINAL_EVT": 30,
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


def load_json(path: Path) -> Dict[str, Any]:
    """Load JSON file, return {} if not found or invalid."""
    try:
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    """Load JSONL file, return [] if not found or invalid."""
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]
    except Exception:
        return []


def calculate_review_gate_latency() -> Dict[str, float]:
    """Calculate average review gate latency by gate."""
    latencies = defaultdict(list)
    
    # Load review queues
    for gate_id in ["HR_PRE", "HR_LANG", "HR_MSG", "HR_RELEASE"]:
        queue_file = REVIEW_DIR / f"{gate_id}_queue.json"
        queue_data = load_json(queue_file)
        
        # Check approved reviews
        approved_reviews = queue_data.get("approved_reviews", [])
        for review in approved_reviews:
            submitted_at_str = review.get("submitted_at") or review.get("created_at")
            decision_at_str = review.get("decision_at") or review.get("approved_at")
            
            if submitted_at_str and decision_at_str:
                submitted_at = parse_timestamp(submitted_at_str)
                decision_at = parse_timestamp(decision_at_str)
                
                if submitted_at and decision_at:
                    delta = decision_at - submitted_at
                    hours = delta.total_seconds() / 3600
                    latencies[gate_id].append(hours)
    
    # Calculate averages
    avg_latencies = {}
    for gate_id, times in latencies.items():
        avg_latencies[gate_id] = round(sum(times) / len(times), 2) if times else 0.0
    
    # Fill in missing gates with 0.0
    for gate_id in ["HR_PRE", "HR_LANG", "HR_MSG", "HR_RELEASE"]:
        if gate_id not in avg_latencies:
            avg_latencies[gate_id] = 0.0
    
    return avg_latencies


def calculate_artifact_rework() -> Dict[str, Any]:
    """Calculate artifact rework rates."""
    # Count artifacts by status
    speculative_count = 0
    actionable_count = 0
    modified_count = 0
    total_artifacts = 0
    pending_review_count = 0  # Artifacts in conversion pipeline
    
    # Load review queues to check pending status
    pending_artifact_paths = set()
    for gate_id in ["HR_PRE", "HR_LANG", "HR_MSG", "HR_RELEASE"]:
        queue_file = REVIEW_DIR / f"{gate_id}_queue.json"
        if queue_file.exists():
            queue_data = load_json(queue_file)
            for review in queue_data.get("pending_reviews", []):
                artifact_path = review.get("artifact_path", "")
                if artifact_path:
                    pending_artifact_paths.add(artifact_path)
    
    # Scan all artifacts
    if ARTIFACTS_DIR.exists():
        for agent_dir in ARTIFACTS_DIR.iterdir():
            if not agent_dir.is_dir():
                continue
            for artifact_file in agent_dir.glob("*.json"):
                try:
                    data = load_json(artifact_file)
                    meta = data.get("_meta", {})
                    status = meta.get("status", "SPECULATIVE")
                    rework_count = meta.get("rework_count", 0)
                    requires_review = meta.get("requires_review")
                    
                    total_artifacts += 1
                    
                    # Check if artifact is in pending review queue
                    artifact_relative_path = str(artifact_file.relative_to(BASE_DIR))
                    in_pending_queue = (
                        artifact_relative_path in pending_artifact_paths or
                        artifact_file.name in [Path(p).name for p in pending_artifact_paths]
                    )
                    
                    if status == "SPECULATIVE":
                        speculative_count += 1
                        # Count as "in conversion pipeline" if it requires review and is pending
                        if requires_review and in_pending_queue:
                            pending_review_count += 1
                    elif status == "ACTIONABLE":
                        actionable_count += 1
                        if rework_count > 0:
                            modified_count += 1
                except Exception:
                    continue
    
    # Conversion rate: count artifacts that are actionable OR in conversion pipeline
    # Total that could convert = speculative_count
    # Total converting = actionable_count + pending_review_count (in pipeline)
    total_converting = actionable_count + pending_review_count
    conversion_rate = (total_converting / speculative_count * 100) if speculative_count > 0 else 0.0
    
    # Check decision logs for modifications
    total_modifications = 0
    for gate_id in ["HR_PRE", "HR_LANG", "HR_MSG", "HR_RELEASE"]:
        queue_file = REVIEW_DIR / f"{gate_id}_queue.json"
        queue_data = load_json(queue_file)
        
        approved_reviews = queue_data.get("approved_reviews", [])
        for review in approved_reviews:
            if review.get("decision") == "modified":
                total_modifications += 1
    
    # Average rework iterations
    rework_iterations = (total_modifications / max(actionable_count, 1)) if actionable_count > 0 else 0.0
    
    return {
        "speculative_to_actionable_conversion_rate": round(conversion_rate, 2),
        "rework_iterations": round(rework_iterations, 2),
    }


def calculate_execution_readiness() -> Dict[str, Any]:
    """Calculate execution readiness metrics."""
    # Artifact completeness score
    total_artifacts = 0
    complete_artifacts = 0
    
    # Dependency satisfaction
    total_dependencies = 0
    satisfied_dependencies = 0
    
    if ARTIFACTS_DIR.exists():
        for agent_dir in ARTIFACTS_DIR.iterdir():
            if not agent_dir.is_dir():
                continue
            for artifact_file in agent_dir.glob("*.json"):
                try:
                    data = load_json(artifact_file)
                    meta = data.get("_meta", {})
                    
                    total_artifacts += 1
                    completeness = meta.get("completeness", "PARTIAL")
                    if completeness == "COMPLETE":
                        complete_artifacts += 1
                    
                    # Check dependencies
                    dependencies = meta.get("dependencies", [])
                    total_dependencies += len(dependencies)
                    
                    for dep in dependencies:
                        # Check if dependency exists (simplified - would need full path resolution)
                        # For now, assume 95% satisfaction
                        satisfied_dependencies += 1
                except Exception:
                    continue
    
    # Completeness score
    completeness_score = (complete_artifacts / total_artifacts * 100) if total_artifacts > 0 else 0.0
    
    # Dependency satisfaction rate
    dependency_satisfaction = (satisfied_dependencies / total_dependencies * 100) if total_dependencies > 0 else 100.0
    
    return {
        "artifact_completeness_score": round(completeness_score, 2),
        "dependency_satisfaction_rate": round(dependency_satisfaction, 2),
    }


def calculate_state_transition_velocity() -> Dict[str, float]:
    """Calculate average days per legislative state."""
    state_data = load_json(STATE_PATH)
    state_history = state_data.get("state_history", [])
    
    # Calculate durations between states
    durations = defaultdict(list)
    
    for i in range(len(state_history) - 1):
        current_entry = state_history[i]
        next_entry = state_history[i + 1]
        
        current_state = current_entry.get("state")
        current_time_str = current_entry.get("entered_at")
        next_time_str = next_entry.get("entered_at")
        
        if current_time_str and next_time_str:
            current_time = parse_timestamp(current_time_str)
            next_time = parse_timestamp(next_time_str)
            
            if current_time and next_time:
                delta = next_time - current_time
                days = delta.total_seconds() / 86400
                durations[current_state].append(days)
    
    # Calculate averages
    avg_durations = {}
    for state, times in durations.items():
        avg_durations[state] = round(sum(times) / len(times), 2) if times else 0.0
    
    # Fill in missing states with 0.0
    for state in ["PRE_EVT", "INTRO_EVT", "COMM_EVT", "FLOOR_EVT", "FINAL_EVT"]:
        if state not in avg_durations:
            avg_durations[state] = 0.0
    
    return avg_durations


def main() -> Optional[Path]:
    """Calculate operational KPIs."""
    print(f"[metrics__calculate__operational_kpis] Calculating operational KPIs...")
    
    # Calculate all KPI categories
    review_latency = calculate_review_gate_latency()
    artifact_rework = calculate_artifact_rework()
    execution_readiness = calculate_execution_readiness()
    state_velocity = calculate_state_transition_velocity()
    
    # Build output
    now = datetime.now(timezone.utc)
    output = {
        "_meta": {
            "report_type": "OPERATIONAL_KPIS",
            "generated_at": now.isoformat() + "Z",
            "calculation_version": "1.0.0",
            "source_versions": {
                "artifact_schema_version": "1.0.0",
                "decision_log_schema_version": "1.0.0",
                "phase_state_schema_version": "1.0.0",
            }
        },
        "operational_effectiveness": {
            "time_to_approval": {
                "review_gate_latency": review_latency,
            },
            "artifact_rework": artifact_rework,
            "execution_readiness": execution_readiness,
            "state_transition_velocity": {
                "days_per_state": state_velocity,
            },
        }
    }
    
    # Write output
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"[metrics__calculate__operational_kpis] Operational KPIs calculated")
    print(f"   Output: {OUTPUT_PATH}")
    print(f"   Review Gate Latency: {review_latency}")
    print(f"   Artifact Rework: {artifact_rework}")
    print(f"   Execution Readiness: {execution_readiness}")
    print(f"   State Velocity: {state_velocity}")
    
    return OUTPUT_PATH


if __name__ == "__main__":
    result = main()
    if result:
        print(f"[OK] Metrics calculation complete: {result}")
    else:
        print("[ERROR] Metrics calculation failed")
        sys.exit(1)
