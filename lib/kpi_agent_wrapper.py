"""
KPI-Aware Agent Wrapper

Wraps agent execution to read KPI state and adjust behavior:
- Slow origination when conversion drops
- Increase review prompts when audit coverage drops
- Adjust aggressiveness based on risk indicators
"""

import json
from pathlib import Path
from typing import Dict, Any, Callable, Optional
from functools import wraps

# Path setup
BASE_DIR = Path(__file__).parent.parent
KPI_STATE_PATH = BASE_DIR / "metrics" / "kpi_state.json"


def load_json(path: Path) -> Dict[str, Any]:
    """Load JSON file."""
    try:
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def get_kpi_state() -> Dict[str, Any]:
    """Get normalized KPI state."""
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


def kpi_conditioned_agent(
    agent_type: str = "Drafting",
    adjust_behavior: bool = True
):
    """
    Decorator to make agents KPI-aware.
    
    Args:
        agent_type: Type of agent (Drafting, Intelligence, Execution, Learning)
        adjust_behavior: Whether to adjust behavior based on KPIs
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Load KPI state
            kpi_state = get_kpi_state()
            risk_indicators = get_risk_indicators()
            operational = get_operational_metrics()
            system_health = get_system_health_metrics()
            
            # Adjust behavior based on KPIs
            if adjust_behavior:
                # Check low conversion rate
                if risk_indicators.get("low_conversion_rate", False):
                    conversion_rate = operational.get("conversion_rate", 0.0)
                    
                    if agent_type == "Drafting":
                        # Increase review prompts for drafting agents
                        kwargs["_kpi_adjustment"] = {
                            "reason": "low_conversion_rate",
                            "action": "increase_review_prompts",
                            "conversion_rate": conversion_rate,
                        }
                    
                    elif agent_type == "Intelligence":
                        # Slow origination when conversion drops
                        kwargs["_kpi_adjustment"] = {
                            "reason": "low_conversion_rate",
                            "action": "slow_origination",
                            "conversion_rate": conversion_rate,
                        }
                
                # Check audit completeness
                if risk_indicators.get("audit_completeness_low", False):
                    decision_log_coverage = system_health.get("decision_log_coverage", 0.0)
                    
                    if agent_type == "Drafting":
                        # Increase review prompts
                        existing_adjustment = kwargs.get("_kpi_adjustment", {})
                        existing_adjustment["audit_adjustment"] = {
                            "reason": "audit_completeness_low",
                            "action": "enforce_decision_logging",
                            "coverage": decision_log_coverage,
                        }
                        kwargs["_kpi_adjustment"] = existing_adjustment
                
                # Check high override rate
                if risk_indicators.get("high_override_rate", False):
                    override_frequency = system_health.get("override_frequency", 0.0)
                    
                    if agent_type == "Drafting":
                        # Reduce aggressiveness
                        existing_adjustment = kwargs.get("_kpi_adjustment", {})
                        existing_adjustment["override_adjustment"] = {
                            "reason": "high_override_rate",
                            "action": "reduce_aggressiveness",
                            "override_frequency": override_frequency,
                        }
                        kwargs["_kpi_adjustment"] = existing_adjustment
            
            # Execute agent with KPI context
            kwargs["_kpi_state"] = kpi_state
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def should_slow_origination() -> bool:
    """Check if origination should be slowed based on KPIs."""
    risk_indicators = get_risk_indicators()
    operational = get_operational_metrics()
    
    # Slow if conversion rate is low
    if risk_indicators.get("low_conversion_rate", False):
        conversion_rate = operational.get("conversion_rate", 0.0)
        return conversion_rate < 50.0
    
    return False


def should_increase_review_prompts() -> bool:
    """Check if review prompts should be increased."""
    risk_indicators = get_risk_indicators()
    system_health = get_system_health_metrics()
    
    # Increase if audit completeness is low
    if risk_indicators.get("audit_completeness_low", False):
        return True
    
    # Increase if conversion rate is low
    if risk_indicators.get("low_conversion_rate", False):
        return True
    
    return False


def should_reduce_aggressiveness() -> bool:
    """Check if agent aggressiveness should be reduced."""
    risk_indicators = get_risk_indicators()
    system_health = get_system_health_metrics()
    
    # Reduce if override rate is high
    if risk_indicators.get("high_override_rate", False):
        override_frequency = system_health.get("override_frequency", 0.0)
        return override_frequency > 40.0
    
    return False


def get_kpi_adjustments() -> Dict[str, Any]:
    """Get KPI-based behavior adjustments."""
    adjustments = {
        "slow_origination": should_slow_origination(),
        "increase_review_prompts": should_increase_review_prompts(),
        "reduce_aggressiveness": should_reduce_aggressiveness(),
    }
    
    return adjustments
