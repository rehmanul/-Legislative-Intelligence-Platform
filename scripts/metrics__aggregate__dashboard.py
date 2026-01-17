"""
Script: metrics__aggregate__dashboard.py
Intent:
- snapshot

Reads:
- metrics/strategic_kpis.json
- metrics/operational_kpis.json
- metrics/system_health.json

Writes:
- metrics/dashboard_kpis.json (aggregated dashboard-ready KPIs with risk indicators)

Schema:
- schemas/metrics.schema.json (DASHBOARD_KPIS report type)
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional

# Path setup
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

# Constants
METRICS_DIR = BASE_DIR / "metrics"
STRATEGIC_PATH = METRICS_DIR / "strategic_kpis.json"
OPERATIONAL_PATH = METRICS_DIR / "operational_kpis.json"
SYSTEM_HEALTH_PATH = METRICS_DIR / "system_health.json"
OUTPUT_PATH = METRICS_DIR / "dashboard_kpis.json"

# Risk thresholds (from plan)
RISK_THRESHOLDS = {
    "high_override_rate": 40.0,  # >40%
    "long_review_latency_multiplier": 1.5,  # >target + 50%
    "low_conversion_rate": 50.0,  # <50%
    "missing_dependencies": 90.0,  # <90%
    "state_progression_multiplier": 2.0,  # >target + 100%
    "audit_completeness_low": 90.0,  # <90%
}

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


def load_json(path: Path) -> Dict[str, Any]:
    """Load JSON file, return {} if not found or invalid."""
    try:
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def calculate_risk_indicators(
    strategic: Dict[str, Any],
    operational: Dict[str, Any],
    system_health: Dict[str, Any]
) -> Dict[str, bool]:
    """Calculate early warning risk indicators."""
    risk_indicators = {}
    
    # High override rate
    override_frequency = system_health.get("system_health", {}).get("agent_accuracy", {}).get("human_override_frequency", 0.0)
    risk_indicators["high_override_rate"] = override_frequency > RISK_THRESHOLDS["high_override_rate"]
    
    # Long review gate latency
    review_latency = operational.get("operational_effectiveness", {}).get("time_to_approval", {}).get("review_gate_latency", {})
    long_latency = False
    for gate_id, target_hours in TARGET_LATENCY_HOURS.items():
        actual_hours = review_latency.get(gate_id, 0.0)
        threshold = target_hours * RISK_THRESHOLDS["long_review_latency_multiplier"]
        if actual_hours > threshold:
            long_latency = True
            break
    risk_indicators["long_review_latency"] = long_latency
    
    # Low conversion rate
    conversion_rate = operational.get("operational_effectiveness", {}).get("artifact_rework", {}).get("speculative_to_actionable_conversion_rate", 100.0)
    risk_indicators["low_conversion_rate"] = conversion_rate < RISK_THRESHOLDS["low_conversion_rate"]
    
    # Missing dependencies
    dependency_satisfaction = operational.get("operational_effectiveness", {}).get("execution_readiness", {}).get("dependency_satisfaction_rate", 100.0)
    risk_indicators["missing_dependencies"] = dependency_satisfaction < RISK_THRESHOLDS["missing_dependencies"]
    
    # State progression stalls
    state_velocity = operational.get("operational_effectiveness", {}).get("state_transition_velocity", {}).get("days_per_state", {})
    progression_stalls = False
    for state, target_days in TARGET_STATE_DAYS.items():
        actual_days = state_velocity.get(state, 0.0)
        threshold = target_days * RISK_THRESHOLDS["state_progression_multiplier"]
        if actual_days > threshold:
            progression_stalls = True
            break
    risk_indicators["state_progression_stalls"] = progression_stalls
    
    # Audit completeness low
    audit_completeness = system_health.get("system_health", {}).get("audit_completeness", {}).get("decision_log_coverage", 100.0)
    risk_indicators["audit_completeness_low"] = audit_completeness < RISK_THRESHOLDS["audit_completeness_low"]
    
    return risk_indicators


def calculate_trends(
    strategic: Dict[str, Any],
    operational: Dict[str, Any],
    system_health: Dict[str, Any]
) -> Dict[str, Any]:
    """Calculate period-over-period trends (placeholder - would compare with historical data)."""
    # This would compare current metrics with previous period
    # For now, return empty trends
    return {
        "note": "Trends require historical data comparison - not yet implemented",
    }


def main() -> Optional[Path]:
    """Aggregate all KPI categories into dashboard-ready format."""
    print(f"[metrics__aggregate__dashboard] Aggregating dashboard KPIs...")
    
    # Load all KPI reports
    strategic = load_json(STRATEGIC_PATH)
    operational = load_json(OPERATIONAL_PATH)
    system_health = load_json(SYSTEM_HEALTH_PATH)
    
    # Check if all reports exist
    if not strategic or not operational or not system_health:
        print("[ERROR] Missing KPI reports. Run individual calculation scripts first.")
        print(f"   Strategic: {STRATEGIC_PATH.exists()}")
        print(f"   Operational: {OPERATIONAL_PATH.exists()}")
        print(f"   System Health: {SYSTEM_HEALTH_PATH.exists()}")
        return None
    
    # Calculate risk indicators
    risk_indicators = calculate_risk_indicators(strategic, operational, system_health)
    
    # Calculate trends (placeholder)
    trends = calculate_trends(strategic, operational, system_health)
    
    # Build aggregated output
    now = datetime.now(timezone.utc)
    output = {
        "_meta": {
            "report_type": "DASHBOARD_KPIS",
            "generated_at": now.isoformat() + "Z",
            "calculation_version": "1.0.0",
            "source_versions": {
                "artifact_schema_version": "1.0.0",
                "decision_log_schema_version": "1.0.0",
                "phase_state_schema_version": "1.0.0",
            }
        },
        "strategic_outcomes": strategic.get("strategic_outcomes", {}),
        "operational_effectiveness": operational.get("operational_effectiveness", {}),
        "system_health": system_health.get("system_health", {}),
        "risk_indicators": risk_indicators,
        "trends": trends,
    }
    
    # Write output
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"[metrics__aggregate__dashboard] Dashboard KPIs aggregated")
    print(f"   Output: {OUTPUT_PATH}")
    print(f"   Risk Indicators: {risk_indicators}")
    
    # Count active risks
    active_risks = sum(1 for v in risk_indicators.values() if v)
    print(f"   Active Risk Indicators: {active_risks}/{len(risk_indicators)}")
    
    return OUTPUT_PATH


if __name__ == "__main__":
    result = main()
    if result:
        print(f"[OK] Dashboard aggregation complete: {result}")
    else:
        print("[ERROR] Dashboard aggregation failed")
        sys.exit(1)
