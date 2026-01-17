"""
Script: metrics__calculate__system_health.py
Intent:
- snapshot

Reads:
- review/HR_*_queue.json (decision logs)
- registry/agent-registry.json (agent types)
- artifacts/{agent_id}/*.json (artifact status)
- audit/audit-log.jsonl (audit trail)

Writes:
- metrics/system_health.json (system health KPIs)

Schema:
- schemas/metrics.schema.json (SYSTEM_HEALTH report type)
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from collections import defaultdict

# Path setup
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

# Constants
ARTIFACTS_DIR = BASE_DIR / "artifacts"
REVIEW_DIR = BASE_DIR / "review"
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
AUDIT_LOG_PATH = BASE_DIR / "audit" / "audit-log.jsonl"
METRICS_DIR = BASE_DIR / "metrics"
METRICS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = METRICS_DIR / "system_health.json"


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


def calculate_agent_accuracy() -> Dict[str, Any]:
    """Calculate agent accuracy vs correction metrics."""
    # Load agent registry
    registry_data = load_json(REGISTRY_PATH)
    agents = registry_data.get("agents", [])
    
    # Build agent_id -> agent_type mapping
    agent_type_map = {}
    for agent in agents:
        agent_id = agent.get("agent_id", "")
        agent_type = agent.get("agent_type", "Unknown")
        agent_type_map[agent_id] = agent_type
    
    # Count decisions by agent type
    decisions_by_type = defaultdict(lambda: {"total": 0, "modified": 0, "rejected": 0, "approved": 0})
    total_decisions = 0
    total_overrides = 0
    
    # Load review queues
    for gate_id in ["HR_PRE", "HR_LANG", "HR_MSG", "HR_RELEASE"]:
        queue_file = REVIEW_DIR / f"{gate_id}_queue.json"
        queue_data = load_json(queue_file)
        
        approved_reviews = queue_data.get("approved_reviews", [])
        for review in approved_reviews:
            decision = review.get("decision", "").lower()
            artifact_id = review.get("artifact_id") or review.get("submitted_by", "")
            
            # Get agent type
            agent_type = agent_type_map.get(artifact_id, "Unknown")
            
            decisions_by_type[agent_type]["total"] += 1
            total_decisions += 1
            
            if decision == "modified" or decision == "rejected":
                decisions_by_type[agent_type]["modified"] += 1
                total_overrides += 1
            elif decision == "approved":
                decisions_by_type[agent_type]["approved"] += 1
    
    # Calculate override frequency
    human_override_frequency = (total_overrides / total_decisions * 100) if total_decisions > 0 else 0.0
    
    # Calculate correction rate by type
    correction_rate_by_type = {}
    for agent_type, counts in decisions_by_type.items():
        total = counts["total"]
        overrides = counts["modified"] + counts["rejected"]
        rate = (overrides / total * 100) if total > 0 else 0.0
        correction_rate_by_type[agent_type] = round(rate, 2)
    
    return {
        "human_override_frequency": round(human_override_frequency, 2),
        "correction_rate_by_type": correction_rate_by_type,
    }


def calculate_conversion_rates() -> Dict[str, Any]:
    """Calculate speculative to actionable conversion rates."""
    # Count artifacts by type and status
    artifacts_by_type = defaultdict(lambda: {"speculative": 0, "actionable": 0})
    conversion_times = []
    
    if ARTIFACTS_DIR.exists():
        for agent_dir in ARTIFACTS_DIR.iterdir():
            if not agent_dir.is_dir():
                continue
            for artifact_file in agent_dir.glob("*.json"):
                try:
                    data = load_json(artifact_file)
                    meta = data.get("_meta", {})
                    artifact_type = meta.get("artifact_type", "UNKNOWN")
                    status = meta.get("status", "SPECULATIVE")
                    
                    if status == "SPECULATIVE":
                        artifacts_by_type[artifact_type]["speculative"] += 1
                    elif status == "ACTIONABLE":
                        artifacts_by_type[artifact_type]["actionable"] += 1
                        
                        # Calculate conversion time
                        generated_at_str = meta.get("generated_at")
                        approved_at_str = meta.get("approved_at")
                        
                        if generated_at_str and approved_at_str:
                            generated_at = parse_timestamp(generated_at_str)
                            approved_at = parse_timestamp(approved_at_str)
                            
                            if generated_at and approved_at:
                                delta = approved_at - generated_at
                                hours = delta.total_seconds() / 3600
                                conversion_times.append(hours)
                except Exception:
                    continue
    
    # Calculate conversion rates by type
    conversion_rate_by_type = {}
    for artifact_type, counts in artifacts_by_type.items():
        speculative = counts["speculative"]
        actionable = counts["actionable"]
        total = speculative + actionable
        
        if total > 0:
            rate = (actionable / total * 100)
            conversion_rate_by_type[artifact_type] = round(rate, 2)
    
    # Average time to conversion
    avg_time_to_conversion = (sum(conversion_times) / len(conversion_times)) if conversion_times else 0.0
    
    return {
        "conversion_rate_by_artifact_type": conversion_rate_by_type,
        "time_to_conversion": round(avg_time_to_conversion, 2),
    }


def calculate_audit_completeness() -> Dict[str, Any]:
    """Calculate audit completeness metrics."""
    # Count approved artifacts
    approved_artifacts = 0
    artifacts_with_decision_logs = 0
    
    # Count state transitions
    total_transitions = 0
    transitions_with_audit_trail = 0
    
    # Scan artifacts
    if ARTIFACTS_DIR.exists():
        for agent_dir in ARTIFACTS_DIR.iterdir():
            if not agent_dir.is_dir():
                continue
            for artifact_file in agent_dir.glob("*.json"):
                try:
                    data = load_json(artifact_file)
                    meta = data.get("_meta", {})
                    
                    # Check if artifact is actionable (approved)
                    status = meta.get("status", "SPECULATIVE")
                    approved_at = meta.get("approved_at")
                    
                    # Count as approved if status is ACTIONABLE OR has approved_at timestamp
                    if status == "ACTIONABLE" or approved_at:
                        approved_artifacts += 1
                        
                        # Check if decision log exists
                        requires_review = meta.get("requires_review")
                        if requires_review:
                            gate_file = REVIEW_DIR / f"{requires_review}_queue.json"
                            queue_data = load_json(gate_file)
                            approved_reviews = queue_data.get("approved_reviews", [])
                            
                            # Check if this artifact has a decision log entry
                            # Match by artifact path (relative or absolute), artifact name, or agent_id
                            artifact_relative_path = str(artifact_file.relative_to(BASE_DIR))
                            artifact_id = meta.get("agent_id", "")
                            artifact_name = meta.get("artifact_name", "")
                            
                            has_log = False
                            for review in approved_reviews:
                                review_path = review.get("artifact_path", "")
                                review_artifact_id = review.get("artifact_id", "")
                                review_artifact_name = review.get("artifact_name", "")
                                
                                # Match by path (relative or filename)
                                if (artifact_relative_path in review_path or 
                                    artifact_file.name in review_path or
                                    review_path in artifact_relative_path):
                                    has_log = True
                                    break
                                
                                # Match by artifact ID
                                if artifact_id and review_artifact_id and artifact_id == review_artifact_id:
                                    has_log = True
                                    break
                                
                                # Match by artifact name
                                if artifact_name and review_artifact_name and artifact_name == review_artifact_name:
                                    has_log = True
                                    break
                            
                            if has_log:
                                artifacts_with_decision_logs += 1
                        else:
                            # No review required, count as having decision log (auto-approved)
                            artifacts_with_decision_logs += 1
                except Exception:
                    continue
    
    # Decision log coverage
    decision_log_coverage = (artifacts_with_decision_logs / approved_artifacts * 100) if approved_artifacts > 0 else 0.0
    
    # Traceability score (simplified - would need full audit trail validation)
    # For now, assume high traceability if decision logs exist
    traceability_score = decision_log_coverage  # Simplified
    
    return {
        "decision_log_coverage": round(decision_log_coverage, 2),
        "traceability_score": round(traceability_score, 2),
    }


def calculate_override_analysis() -> Dict[str, Any]:
    """Calculate override risk distribution and rationale quality."""
    override_risks = defaultdict(int)
    total_overrides = 0
    overrides_with_rationale = 0
    
    # Load review queues
    for gate_id in ["HR_PRE", "HR_LANG", "HR_MSG", "HR_RELEASE"]:
        queue_file = REVIEW_DIR / f"{gate_id}_queue.json"
        queue_data = load_json(queue_file)
        
        approved_reviews = queue_data.get("approved_reviews", [])
        for review in approved_reviews:
            decision = review.get("decision", "").lower()
            
            if decision == "modified" or decision == "rejected":
                total_overrides += 1
                
                # Get override risk
                override_risk = review.get("override_risk", "LOW")
                override_risks[override_risk] += 1
                
                # Check rationale quality
                rationale = review.get("rationale") or review.get("decision_rationale", "")
                if rationale and len(rationale) > 50:
                    overrides_with_rationale += 1
    
    # Calculate distribution percentages
    risk_distribution = {}
    for risk_level in ["LOW", "MEDIUM", "HIGH"]:
        count = override_risks.get(risk_level, 0)
        percentage = (count / total_overrides * 100) if total_overrides > 0 else 0.0
        risk_distribution[risk_level] = round(percentage, 2)
    
    # Rationale quality
    rationale_quality = (overrides_with_rationale / total_overrides * 100) if total_overrides > 0 else 0.0
    
    return {
        "override_risk_distribution": risk_distribution,
        "override_rationale_quality": round(rationale_quality, 2),
    }


def main() -> Optional[Path]:
    """Calculate system health KPIs."""
    print(f"[metrics__calculate__system_health] Calculating system health KPIs...")
    
    # Calculate all KPI categories
    agent_accuracy = calculate_agent_accuracy()
    conversion_rates = calculate_conversion_rates()
    audit_completeness = calculate_audit_completeness()
    override_analysis = calculate_override_analysis()
    
    # Build output
    now = datetime.now(timezone.utc)
    output = {
        "_meta": {
            "report_type": "SYSTEM_HEALTH",
            "generated_at": now.isoformat() + "Z",
            "calculation_version": "1.0.0",
            "source_versions": {
                "artifact_schema_version": "1.0.0",
                "decision_log_schema_version": "1.0.0",
                "phase_state_schema_version": "1.0.0",
            }
        },
        "system_health": {
            "agent_accuracy": agent_accuracy,
            "conversion_rates": conversion_rates,
            "audit_completeness": audit_completeness,
            "override_analysis": override_analysis,
        }
    }
    
    # Write output
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"[metrics__calculate__system_health] System health KPIs calculated")
    print(f"   Output: {OUTPUT_PATH}")
    print(f"   Agent Accuracy: {agent_accuracy}")
    print(f"   Conversion Rates: {conversion_rates}")
    print(f"   Audit Completeness: {audit_completeness}")
    print(f"   Override Analysis: {override_analysis}")
    
    return OUTPUT_PATH


if __name__ == "__main__":
    result = main()
    if result:
        print(f"[OK] Metrics calculation complete: {result}")
    else:
        print("[ERROR] Metrics calculation failed")
        sys.exit(1)
