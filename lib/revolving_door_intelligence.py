"""
Revolving-Door Operational Intelligence

Analyzes active revolving-door events to provide timing, decay, and leverage signals
for human operators. Surfaces who matters now, who is decaying, and who will stop
mattering soon.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Literal
from pathlib import Path
import json
import logging

from .revolving_door_observability import (
    get_revolving_door_events,
    get_revolving_door_status,
    get_revolving_door_kpis
)
from .edge_decay import parse_timestamp

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent

ImpactCategory = Literal["HIGH-IMPACT-NOW", "DECAYING-BUT-RELEVANT", "NEAR-EXPIRY", "SAFE-TO-IGNORE"]


def classify_revolving_door_impact(
    event_status: Dict[str, Any],
    current_phase: Optional[str] = None
) -> ImpactCategory:
    """
    Classify revolving-door event into impact category.
    
    Categories:
    - HIGH-IMPACT-NOW: < 90 days, full boost, early phase (PRE/INTRO/COMM)
    - DECAYING-BUT-RELEVANT: 90-120 days, decaying boost, still in early/mid phase
    - NEAR-EXPIRY: 120-180 days, significant decay, or late phase
    - SAFE-TO-IGNORE: Expired, or IMPL_EVT phase (no boost)
    
    Args:
        event_status: Status dictionary from get_revolving_door_status()
        current_phase: Current legislative phase (optional)
    
    Returns:
        Impact category
    """
    if event_status.get("is_expired"):
        return "SAFE-TO-IGNORE"
    
    # IMPL_EVT phase has 0.0 boost (no revolving-door influence)
    if current_phase == "IMPL_EVT":
        return "SAFE-TO-IGNORE"
    
    days_since = event_status.get("days_since", 0)
    remaining_days = event_status.get("remaining_days")
    decay_status = event_status.get("decay_status", "FULL")
    boost_factor = event_status.get("boost_factor", 0.0)
    
    # High impact: full boost, early phase, plenty of time
    if decay_status == "FULL" and days_since < 90:
        if current_phase in ["PRE_EVT", "INTRO_EVT", "COMM_EVT"]:
            return "HIGH-IMPACT-NOW"
        elif current_phase in ["FLOOR_EVT", "FINAL_EVT"]:
            # Full boost but late phase (reduced by phase sensitivity)
            return "DECAYING-BUT-RELEVANT"
    
    # Decaying but still relevant: 90-120 days, or early phase with decay
    if decay_status == "DECAYING" and days_since < 120:
        if current_phase in ["PRE_EVT", "INTRO_EVT", "COMM_EVT"]:
            return "DECAYING-BUT-RELEVANT"
        elif current_phase in ["FLOOR_EVT", "FINAL_EVT"]:
            return "NEAR-EXPIRY"
    
    # Near expiry: 120-180 days, or late phase
    if remaining_days and remaining_days < 60:
        return "NEAR-EXPIRY"
    
    if days_since >= 120:
        return "NEAR-EXPIRY"
    
    # Default: safe to ignore if boost is very low
    if boost_factor < 0.1:
        return "SAFE-TO-IGNORE"
    
    # Fallback classification
    if decay_status == "FULL":
        return "HIGH-IMPACT-NOW"
    elif decay_status == "DECAYING":
        return "DECAYING-BUT-RELEVANT"
    else:
        return "SAFE-TO-IGNORE"


def analyze_revolving_door_situation(
    current_time: Optional[datetime] = None,
    current_phase: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyze current revolving-door situation and classify events.
    
    Args:
        current_time: Current timestamp (defaults to now)
        current_phase: Current legislative phase (optional)
    
    Returns:
        Analysis dictionary with classified events and summaries
    """
    if current_time is None:
        current_time = datetime.utcnow()
    
    # Get active events
    active_events = get_revolving_door_events(current_time, include_expired=False)
    
    # Get status for each event
    classified_events = {
        "HIGH-IMPACT-NOW": [],
        "DECAYING-BUT-RELEVANT": [],
        "NEAR-EXPIRY": [],
        "SAFE-TO-IGNORE": []
    }
    
    for event in active_events:
        status = get_revolving_door_status(event, current_time)
        category = classify_revolving_door_impact(status, current_phase)
        
        classified_events[category].append({
            "event": event,
            "status": status,
            "category": category
        })
    
    # Get KPIs
    kpis = get_revolving_door_kpis(current_time)
    
    return {
        "analysis_time": current_time.isoformat() + "Z",
        "current_phase": current_phase or "UNKNOWN",
        "total_active_events": len(active_events),
        "classified_events": classified_events,
        "kpis": kpis,
        "summary": {
            "high_impact_count": len(classified_events["HIGH-IMPACT-NOW"]),
            "decaying_relevant_count": len(classified_events["DECAYING-BUT-RELEVANT"]),
            "near_expiry_count": len(classified_events["NEAR-EXPIRY"]),
            "safe_to_ignore_count": len(classified_events["SAFE-TO-IGNORE"])
        }
    }


def interpret_phase_timing(
    event_status: Dict[str, Any],
    current_phase: str
) -> Dict[str, Any]:
    """
    Interpret why revolving-door event matters in current phase and when it stops mattering.
    
    Args:
        event_status: Status dictionary from get_revolving_door_status()
        current_phase: Current legislative phase
    
    Returns:
        Interpretation dictionary with phase relevance, expiration timing, affected axes
    """
    days_since = event_status.get("days_since", 0)
    remaining_days = event_status.get("remaining_days")
    decay_status = event_status.get("decay_status", "FULL")
    effective_boosts = event_status.get("effective_boosts", {})
    
    # Phase sensitivity factors
    phase_sensitivity_map = {
        "PRE_EVT": 1.0,
        "INTRO_EVT": 0.9,
        "COMM_EVT": 0.7,
        "FLOOR_EVT": 0.4,
        "FINAL_EVT": 0.2,
        "IMPL_EVT": 0.0
    }
    
    phase_sensitivity = phase_sensitivity_map.get(current_phase, 1.0)
    
    # Determine which axes are realistically amplified
    amplified_axes = []
    for axis, boost in effective_boosts.items():
        # Apply phase sensitivity to effective boost
        phase_adjusted_boost = boost * phase_sensitivity
        if phase_adjusted_boost > 0.05:  # Threshold: meaningful boost
            amplified_axes.append({
                "axis": axis,
                "base_boost": boost,
                "phase_adjusted_boost": round(phase_adjusted_boost, 4),
                "meaningful": True
            })
    
    # When it stops mattering
    if remaining_days:
        stops_mattering_at = (datetime.utcnow() + timedelta(days=remaining_days)).isoformat() + "Z"
    else:
        stops_mattering_at = "UNKNOWN"
    
    # Phase-specific interpretation
    if current_phase == "IMPL_EVT":
        phase_relevance = "No relevance - implementation phase has 0.0 phase sensitivity"
        stops_mattering = "Immediately (no boost in IMPL_EVT)"
    elif current_phase in ["PRE_EVT", "INTRO_EVT", "COMM_EVT"]:
        phase_relevance = f"High relevance - early phases have {phase_sensitivity:.0%} sensitivity"
        if remaining_days:
            stops_mattering = f"In {remaining_days} days (expiration) or when phase advances to FLOOR_EVT/FINAL_EVT"
        else:
            stops_mattering = "When phase advances to FLOOR_EVT/FINAL_EVT"
    elif current_phase in ["FLOOR_EVT", "FINAL_EVT"]:
        phase_relevance = f"Reduced relevance - late phases have {phase_sensitivity:.0%} sensitivity"
        if remaining_days:
            stops_mattering = f"In {remaining_days} days (expiration)"
        else:
            stops_mattering = "At expiration"
    else:
        phase_relevance = "Unknown phase - cannot determine relevance"
        stops_mattering = "Unknown"
    
    return {
        "current_phase": current_phase,
        "phase_sensitivity": phase_sensitivity,
        "phase_relevance": phase_relevance,
        "amplified_axes": amplified_axes,
        "stops_mattering_at": stops_mattering_at,
        "stops_mattering_reason": stops_mattering,
        "decay_status": decay_status,
        "days_since": days_since,
        "remaining_days": remaining_days,
        "what_must_not_be_inferred": [
            "This does not imply legal or ethical judgment",
            "This does not predict future behavior",
            "This models structural advantage only",
            "Confidence is MEDIUM by design",
            "All influence is temporary and decaying"
        ]
    }


if __name__ == "__main__":
    # Test intelligence functions
    current_time = datetime.utcnow()
    analysis = analyze_revolving_door_situation(current_time, current_phase="COMM_EVT")
    print(f"Analysis: {json.dumps(analysis, indent=2, default=str)}")
