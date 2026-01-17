"""
Revolving-Door Observability Library

Provides visibility and inspection tools for revolving-door influence events.
Includes timeline views, remaining-days indicators, decay status, and KPI tracking.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import logging

from .crisis_handler import load_active_crisis_events, parse_timestamp
from .edge_decay import parse_timestamp as parse_ts

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent

CRISIS_EVENTS_FILE = BASE_DIR / "data" / "temporal" / "crisis_events.jsonl"


def get_revolving_door_events(current_time: Optional[datetime] = None, include_expired: bool = False) -> List[Dict[str, Any]]:
    """
    Get all revolving-door events (active or expired).
    
    Args:
        current_time: Current timestamp (defaults to now)
        include_expired: If True, include expired events
    
    Returns:
        List of revolving-door event dictionaries
    """
    if current_time is None:
        current_time = datetime.utcnow()
    
    if not CRISIS_EVENTS_FILE.exists():
        return []
    
    revolving_door_events = []
    
    try:
        with open(CRISIS_EVENTS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    event = json.loads(line)
                    if event.get("event_type") == "REVOLVING_DOOR":
                        if not include_expired:
                            # Check if expired
                            expires_at = event.get("expires_at")
                            if expires_at:
                                expires_time = parse_ts(expires_at)
                                if current_time > expires_time:
                                    continue  # Skip expired
                        revolving_door_events.append(event)
                except json.JSONDecodeError:
                    continue
    
    except Exception as e:
        logger.error(f"Failed to load revolving-door events: {e}")
    
    return revolving_door_events


def get_revolving_door_status(event: Dict[str, Any], current_time: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Get status information for a revolving-door event.
    
    Returns: remaining_days, decay_status, boost_magnitude, phase_sensitivity_factor
    """
    if current_time is None:
        current_time = datetime.utcnow()
    
    event_at = parse_ts(event.get("event_at"))
    expires_at = parse_ts(event.get("expires_at")) if event.get("expires_at") else None
    
    days_since = (current_time - event_at).days
    
    if expires_at:
        remaining_days = (expires_at - current_time).days
        is_expired = remaining_days <= 0
    else:
        remaining_days = 180 - days_since  # Default max
        is_expired = days_since >= 180
    
    # Decay status
    if is_expired:
        decay_status = "EXPIRED"
        boost_factor = 0.0
    elif days_since < 90:
        decay_status = "FULL"  # Full boost
        boost_factor = 1.0
    elif days_since < 180:
        decay_status = "DECAYING"  # Decaying boost
        # Exponential decay: 0.5^((days-90)/90)
        boost_factor = 0.5 ** ((days_since - 90) / 90)
    else:
        decay_status = "EXPIRED"
        boost_factor = 0.0
    
    # Calculate effective boost magnitudes (with decay)
    weight_overrides = event.get("weight_overrides", {})
    effective_boosts = {
        axis: round(boost * boost_factor, 4)
        for axis, boost in weight_overrides.items()
    }
    
    return {
        "event_id": event.get("event_id"),
        "entity_id": event.get("affected_entities", [None])[0] if event.get("affected_entities") else None,
        "from_role": event.get("description", "").split("→")[0].strip() if "→" in event.get("description", "") else None,
        "to_role": event.get("description", "").split("→")[1].strip() if "→" in event.get("description", "") else None,
        "event_at": event.get("event_at"),
        "expires_at": event.get("expires_at"),
        "days_since": days_since,
        "remaining_days": max(0, remaining_days) if expires_at else None,
        "decay_status": decay_status,
        "boost_factor": round(boost_factor, 4),
        "base_boosts": weight_overrides,
        "effective_boosts": effective_boosts,
        "is_expired": is_expired,
        "is_active": not is_expired
    }


def get_revolving_door_kpis(current_time: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Calculate KPI metrics for revolving-door events.
    
    Returns:
        Dictionary with active_count, average_remaining_days, expiration_compliance, etc.
    """
    if current_time is None:
        current_time = datetime.utcnow()
    
    active_events = get_revolving_door_events(current_time, include_expired=False)
    all_events = get_revolving_door_events(current_time, include_expired=True)
    
    # Calculate KPIs
    active_count = len(active_events)
    total_count = len(all_events)
    
    # Average remaining days (for active events)
    remaining_days_list = []
    for event in active_events:
        status = get_revolving_door_status(event, current_time)
        if status.get("remaining_days") is not None:
            remaining_days_list.append(status["remaining_days"])
    
    average_remaining_days = (
        sum(remaining_days_list) / len(remaining_days_list)
        if remaining_days_list
        else None
    )
    
    # Expiration compliance: all events must expire within 180 days (100% required)
    expiration_compliant = 0
    expiration_non_compliant = 0
    
    for event in all_events:
        event_at = parse_ts(event.get("event_at"))
        expires_at = parse_ts(event.get("expires_at")) if event.get("expires_at") else None
        
        if expires_at:
            duration_days = (expires_at - event_at).days
            if duration_days <= 180:
                expiration_compliant += 1
            else:
                expiration_non_compliant += 1
        else:
            # No expiration set (should not happen for revolving-door, but check)
            expiration_non_compliant += 1
    
    expiration_compliance_rate = (
        expiration_compliant / total_count * 100
        if total_count > 0
        else 100.0
    )
    
    # Decay status distribution
    decay_status_counts = {"FULL": 0, "DECAYING": 0, "EXPIRED": 0}
    for event in active_events:
        status = get_revolving_door_status(event, current_time)
        decay_status = status.get("decay_status", "EXPIRED")
        if decay_status in decay_status_counts:
            decay_status_counts[decay_status] += 1
    
    return {
        "active_count": active_count,
        "total_count": total_count,
        "expired_count": total_count - active_count,
        "average_remaining_days": round(average_remaining_days, 1) if average_remaining_days else None,
        "expiration_compliance": {
            "compliant": expiration_compliant,
            "non_compliant": expiration_non_compliant,
            "compliance_rate": round(expiration_compliance_rate, 2),
            "required": 100.0
        },
        "decay_status_distribution": decay_status_counts,
        "health_status": "HEALTHY" if expiration_compliance_rate == 100.0 and active_count < 100 else "REVIEW_NEEDED"
    }


def get_revolving_door_timeline(entity_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Get timeline view of revolving-door events, sorted by event_at (newest first).
    
    Args:
        entity_id: Optional entity ID to filter by
        limit: Maximum number of events to return
    
    Returns:
        List of event status dictionaries with timeline information
    """
    current_time = datetime.utcnow()
    events = get_revolving_door_events(current_time, include_expired=True)
    
    # Filter by entity if specified
    if entity_id:
        events = [
            e for e in events
            if entity_id in e.get("affected_entities", [])
        ]
    
    # Sort by event_at (newest first)
    events.sort(
        key=lambda e: parse_ts(e.get("event_at")),
        reverse=True
    )
    
    # Get status for each event
    timeline = []
    for event in events[:limit]:
        status = get_revolving_door_status(event, current_time)
        timeline.append(status)
    
    return timeline


def get_edges_affected_by_revolving_door(
    edges: List[Dict[str, Any]],
    current_time: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """
    Get edges that are currently affected by active revolving-door events.
    
    Args:
        edges: List of edge dictionaries
        current_time: Current timestamp
    
    Returns:
        List of dictionaries with edge and revolving-door event information
    """
    if current_time is None:
        current_time = datetime.utcnow()
    
    active_events = get_revolving_door_events(current_time, include_expired=False)
    
    affected_edges = []
    
    for edge in edges:
        from_id = edge.get("from_entity_id")
        to_id = edge.get("to_entity_id")
        
        # Check if edge is affected by any active revolving-door event
        for event in active_events:
            affected_entities = event.get("affected_entities", [])
            
            if from_id in affected_entities or to_id in affected_entities:
                status = get_revolving_door_status(event, current_time)
                affected_edges.append({
                    "edge": edge,
                    "event": event,
                    "status": status
                })
                break  # Only track first matching event per edge
    
    return affected_edges


if __name__ == "__main__":
    # Test observability functions
    current_time = datetime.utcnow()
    
    # Get KPIs
    kpis = get_revolving_door_kpis(current_time)
    print(f"KPIs: {json.dumps(kpis, indent=2, default=str)}")
    
    # Get timeline
    timeline = get_revolving_door_timeline(limit=10)
    print(f"\nTimeline ({len(timeline)} events):")
    for item in timeline[:5]:
        print(f"  {item.get('entity_id')}: {item.get('decay_status')}, {item.get('remaining_days')} days remaining")
