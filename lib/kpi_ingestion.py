"""
KPI Ingestion Module

Reads KPI JSON artifacts and normalizes them into agent-readable state.
Tags metrics by workflow, campaign, agent, and artifact type.
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Set
from collections import defaultdict

# Path setup
BASE_DIR = Path(__file__).parent.parent
METRICS_DIR = BASE_DIR / "metrics"
STRATEGIC_PATH = METRICS_DIR / "strategic_kpis.json"
OPERATIONAL_PATH = METRICS_DIR / "operational_kpis.json"
SYSTEM_HEALTH_PATH = METRICS_DIR / "system_health.json"
DASHBOARD_PATH = METRICS_DIR / "dashboard_kpis.json"
KPI_STATE_PATH = METRICS_DIR / "kpi_state.json"

# Additional paths for tagging
ARTIFACTS_DIR = BASE_DIR / "artifacts"
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
STATE_PATH = BASE_DIR / "state" / "legislative-state.json"


def load_json(path: Path) -> Dict[str, Any]:
    """Load JSON file, return {} if not found."""
    try:
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def extract_workflow_ids() -> Set[str]:
    """Extract workflow IDs from state file."""
    state_data = load_json(STATE_PATH)
    workflow_ids = set()
    
    # Check for workflow_id in _meta
    meta = state_data.get("_meta", {})
    workflow_id = meta.get("workflow_id")
    if workflow_id:
        workflow_ids.add(workflow_id)
    
    return workflow_ids


def extract_campaigns() -> Set[str]:
    """Extract campaign identifiers from artifacts."""
    campaigns = set()
    
    if ARTIFACTS_DIR.exists():
        for agent_dir in ARTIFACTS_DIR.iterdir():
            if not agent_dir.is_dir():
                continue
            for artifact_file in agent_dir.glob("*.json"):
                try:
                    data = load_json(artifact_file)
                    # Look for campaign tags or metadata
                    meta = data.get("_meta", {})
                    tags = meta.get("tags", [])
                    for tag in tags:
                        if "campaign" in tag.lower():
                            campaigns.add(tag)
                except Exception:
                    continue
    
    return campaigns


def extract_agent_ids() -> Set[str]:
    """Extract agent IDs from registry and artifacts."""
    agent_ids = set()
    
    # From registry
    registry_data = load_json(REGISTRY_PATH)
    agents = registry_data.get("agents", [])
    for agent in agents:
        agent_id = agent.get("agent_id")
        if agent_id:
            agent_ids.add(agent_id)
    
    # From artifacts
    if ARTIFACTS_DIR.exists():
        for agent_dir in ARTIFACTS_DIR.iterdir():
            if not agent_dir.is_dir():
                continue
            agent_ids.add(agent_dir.name)
            
            for artifact_file in agent_dir.glob("*.json"):
                try:
                    data = load_json(artifact_file)
                    meta = data.get("_meta", {})
                    agent_id = meta.get("agent_id")
                    if agent_id:
                        agent_ids.add(agent_id)
                except Exception:
                    continue
    
    return agent_ids


def extract_artifact_types() -> Set[str]:
    """Extract artifact types from artifacts."""
    artifact_types = set()
    
    if ARTIFACTS_DIR.exists():
        for agent_dir in ARTIFACTS_DIR.iterdir():
            if not agent_dir.is_dir():
                continue
            for artifact_file in agent_dir.glob("*.json"):
                try:
                    data = load_json(artifact_file)
                    meta = data.get("_meta", {})
                    artifact_type = meta.get("artifact_type")
                    if artifact_type:
                        artifact_types.add(artifact_type)
                except Exception:
                    continue
    
    return artifact_types


def normalize_kpi_state() -> Dict[str, Any]:
    """Normalize KPI JSON files into agent-readable state."""
    # Load source KPI files
    dashboard_data = load_json(DASHBOARD_PATH)
    strategic_data = load_json(STRATEGIC_PATH)
    operational_data = load_json(OPERATIONAL_PATH)
    system_health_data = load_json(SYSTEM_HEALTH_PATH)
    
    # Extract tags
    workflow_ids = list(extract_workflow_ids())
    campaigns = list(extract_campaigns())
    agent_ids = list(extract_agent_ids())
    artifact_types = list(extract_artifact_types())
    
    # Normalize strategic metrics
    strategic_outcomes = dashboard_data.get("strategic_outcomes", {})
    strategic_metrics = {
        "policy_movement": strategic_outcomes.get("policy_movement", {}),
        "access_gained": strategic_outcomes.get("access_gained", {}),
        "risk_reduced": strategic_outcomes.get("risk_reduced", {}),
        "narrative_alignment": strategic_outcomes.get("narrative_alignment", {}),
    }
    
    # Normalize operational metrics
    operational_effectiveness = dashboard_data.get("operational_effectiveness", {})
    time_to_approval = operational_effectiveness.get("time_to_approval", {})
    artifact_rework = operational_effectiveness.get("artifact_rework", {})
    execution_readiness = operational_effectiveness.get("execution_readiness", {})
    state_velocity = operational_effectiveness.get("state_transition_velocity", {})
    
    operational_metrics = {
        "review_gate_latency": time_to_approval.get("review_gate_latency", {}),
        "conversion_rate": artifact_rework.get("speculative_to_actionable_conversion_rate", 0.0),
        "rework_iterations": artifact_rework.get("rework_iterations", 0.0),
        "artifact_completeness": execution_readiness.get("artifact_completeness_score", 0.0),
        "dependency_satisfaction": execution_readiness.get("dependency_satisfaction_rate", 0.0),
        "state_velocity": state_velocity.get("days_per_state", {}),
    }
    
    # Normalize system health metrics
    system_health = dashboard_data.get("system_health", {})
    agent_accuracy = system_health.get("agent_accuracy", {})
    conversion_rates = system_health.get("conversion_rates", {})
    audit_completeness = system_health.get("audit_completeness", {})
    override_analysis = system_health.get("override_analysis", {})
    
    system_health_metrics = {
        "override_frequency": agent_accuracy.get("human_override_frequency", 0.0),
        "conversion_by_artifact_type": conversion_rates.get("conversion_rate_by_artifact_type", {}),
        "time_to_conversion": conversion_rates.get("time_to_conversion", 0.0),
        "decision_log_coverage": audit_completeness.get("decision_log_coverage", 0.0),
        "traceability_score": audit_completeness.get("traceability_score", 0.0),
        "override_risk_distribution": override_analysis.get("override_risk_distribution", {}),
    }
    
    # Extract risk indicators
    risk_indicators = dashboard_data.get("risk_indicators", {})
    
    # Build normalized state
    now = datetime.now(timezone.utc)
    normalized_state = {
        "_meta": {
            "generated_at": now.isoformat() + "Z",
            "source_version": dashboard_data.get("_meta", {}).get("calculation_version", "1.0.0"),
            "normalization_version": "1.0.0",
        },
        "metrics": {
            "strategic": strategic_metrics,
            "operational": operational_metrics,
            "system_health": system_health_metrics,
            "risk_indicators": risk_indicators,
        },
        "tags": {
            "workflow_id": workflow_ids,
            "campaign": campaigns,
            "agent_id": agent_ids,
            "artifact_type": artifact_types,
        }
    }
    
    return normalized_state


def ingest_kpis() -> Path:
    """Ingest KPIs and write normalized state."""
    print("[kpi_ingestion] Ingesting KPIs...")
    
    normalized_state = normalize_kpi_state()
    
    # Write normalized state
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    with open(KPI_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(normalized_state, f, indent=2, ensure_ascii=False)
    
    print(f"[kpi_ingestion] Normalized KPI state written to {KPI_STATE_PATH}")
    
    # Print summary
    risk_indicators = normalized_state["metrics"]["risk_indicators"]
    active_risks = [k for k, v in risk_indicators.items() if v]
    print(f"[kpi_ingestion] Active risk indicators: {len(active_risks)}/{len(risk_indicators)}")
    if active_risks:
        print(f"[kpi_ingestion]   Active: {', '.join(active_risks)}")
    
    return KPI_STATE_PATH


def get_kpi_state() -> Dict[str, Any]:
    """Get current normalized KPI state."""
    return load_json(KPI_STATE_PATH)


def get_risk_indicators() -> Dict[str, bool]:
    """Get current risk indicators."""
    state = get_kpi_state()
    return state.get("metrics", {}).get("risk_indicators", {})


def get_operational_metrics() -> Dict[str, Any]:
    """Get operational metrics."""
    state = get_kpi_state()
    return state.get("metrics", {}).get("operational", {})


def get_system_health_metrics() -> Dict[str, Any]:
    """Get system health metrics."""
    state = get_kpi_state()
    return state.get("metrics", {}).get("system_health", {})


if __name__ == "__main__":
    ingest_kpis()
