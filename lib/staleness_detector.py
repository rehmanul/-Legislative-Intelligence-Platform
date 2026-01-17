"""
Staleness Detection Library

Detects edges that have not been confirmed recently and require validation.
Provides staleness status classification and audit capabilities.
"""

from datetime import datetime
from typing import Dict, Any, Optional, Literal
from pathlib import Path
import json
import logging

from .edge_decay import parse_timestamp, classify_edge_decay_type, load_decay_config

logger = logging.getLogger(__name__)

StalenessStatus = Literal["FRESH", "STALE", "VERY_STALE"]


def check_edge_staleness(
    edge: Dict[str, Any],
    current_time: datetime,
    thresholds: Optional[Dict[str, Dict[str, int]]] = None,
    revolving_door_active: bool = False
) -> Dict[str, Any]:
    """
    Check if edge is stale based on last confirmation.
    
    Thresholds:
    - FRESH: < 90 days (person-dependent), < 180 days (institution-dependent)
    - STALE: 90-180 days (person), 180-365 days (institution)
    - VERY_STALE: > 180 days (person), > 365 days (institution)
    
    For revolving-door edges: Fast-track thresholds (30 days vs 90 days)
    
    Args:
        edge: Edge dictionary
        current_time: Current timestamp
        thresholds: Optional threshold configuration (loads from config if None)
        revolving_door_active: If True, apply faster staleness threshold (30 days)
    
    Returns:
        Dictionary with status, days_since_confirmation, requires_revalidation
    """
    if thresholds is None:
        decay_config = load_decay_config()
        thresholds = decay_config.get("default_params", {}).get("staleness_threshold_days", {})
    
    # Apply faster threshold for revolving-door edges
    if revolving_door_active:
        # Fast-track: 30 days for revolving-door edges (vs 90 days normal)
        revolving_door_thresholds = {
            "person": {"fresh": 15, "stale": 30, "very_stale": 45},
            "institution": {"fresh": 30, "stale": 60, "very_stale": 90}
        }
        # Merge with defaults, revolving-door takes precedence
        thresholds = thresholds.copy()
        for key in ["person", "institution"]:
            if key in revolving_door_thresholds:
                thresholds[key] = revolving_door_thresholds[key]
    
    last_confirmed = edge.get("last_confirmed_at")
    if not last_confirmed:
        return {
            "status": "VERY_STALE",
            "days_since_confirmation": None,
            "days_uncertain": None,
            "requires_revalidation": True
        }
    
    try:
        days_since = (current_time - parse_timestamp(last_confirmed)).days
        decay_type = classify_edge_decay_type(edge)
        
        if decay_type == "PERSON_DEPENDENT":
            threshold_config = thresholds.get("person", {"fresh": 90, "stale": 180})
        else:
            threshold_config = thresholds.get("institution", {"fresh": 180, "stale": 365})
        
        fresh_threshold = threshold_config.get("fresh", 90)
        stale_threshold = threshold_config.get("stale", 180)
        very_stale_threshold = threshold_config.get("very_stale", stale_threshold)
        
        if days_since < fresh_threshold:
            status = "FRESH"
            requires_revalidation = False
        elif days_since < stale_threshold:
            status = "STALE"
            requires_revalidation = True
        elif days_since < very_stale_threshold:
            status = "STALE"
            requires_revalidation = True
        else:
            status = "VERY_STALE"
            requires_revalidation = True
        
        return {
            "status": status,
            "days_since_confirmation": days_since,
            "days_uncertain": days_since if status != "FRESH" else None,
            "requires_revalidation": requires_revalidation
        }
    except Exception as e:
        logger.error(f"Error checking staleness for edge {edge.get('edge_id')}: {e}")
        return {
            "status": "VERY_STALE",
            "days_since_confirmation": None,
            "days_uncertain": None,
            "requires_revalidation": True,
            "error": str(e)
        }


def update_edge_staleness(
    edge: Dict[str, Any],
    current_time: datetime,
    thresholds: Optional[Dict[str, Dict[str, int]]] = None
) -> Dict[str, Any]:
    """
    Update edge with current staleness status and add warning if needed.
    
    Args:
        edge: Edge dictionary (will be modified)
        current_time: Current timestamp
        thresholds: Optional threshold configuration
    
    Returns:
        Updated edge dictionary
    """
    staleness_check = check_edge_staleness(edge, current_time, thresholds)
    
    # Update staleness status
    edge["staleness_status"] = staleness_check["status"]
    
    # Add warning if stale or very stale
    if staleness_check["status"] != "FRESH":
        if "staleness_warnings" not in edge:
            edge["staleness_warnings"] = []
        
        warning = {
            "warned_at": current_time.isoformat() + "Z",
            "status": staleness_check["status"],
            "days_since_confirmation": staleness_check.get("days_since_confirmation"),
            "requires_revalidation": staleness_check["requires_revalidation"]
        }
        
        # Only add if this is a new status or time has passed
        existing_warnings = edge.get("staleness_warnings", [])
        last_warning = existing_warnings[-1] if existing_warnings else None
        
        if not last_warning or last_warning.get("status") != staleness_check["status"]:
            edge["staleness_warnings"].append(warning)
    
    return edge


def get_stale_edges(
    edges: list[Dict[str, Any]],
    current_time: Optional[datetime] = None,
    status_filter: Optional[list[StalenessStatus]] = None
) -> list[Dict[str, Any]]:
    """
    Filter edges by staleness status.
    
    Args:
        edges: List of edge dictionaries
        current_time: Current timestamp (defaults to now)
        status_filter: Optional list of statuses to include (defaults to STALE and VERY_STALE)
    
    Returns:
        List of stale edges
    """
    if current_time is None:
        current_time = datetime.utcnow()
    
    if status_filter is None:
        status_filter = ["STALE", "VERY_STALE"]
    
    stale_edges = []
    for edge in edges:
        staleness_check = check_edge_staleness(edge, current_time)
        if staleness_check["status"] in status_filter:
            stale_edges.append({
                "edge": edge,
                "staleness": staleness_check
            })
    
    return stale_edges


def generate_staleness_summary(
    edges: list[Dict[str, Any]],
    current_time: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Generate summary statistics for edge staleness.
    
    Args:
        edges: List of edge dictionaries
        current_time: Current timestamp
    
    Returns:
        Summary dictionary with counts and statistics
    """
    if current_time is None:
        current_time = datetime.utcnow()
    
    summary = {
        "total_edges": len(edges),
        "fresh": 0,
        "stale": 0,
        "very_stale": 0,
        "never_confirmed": 0,
        "by_decay_type": {
            "PERSON_DEPENDENT": {"fresh": 0, "stale": 0, "very_stale": 0},
            "INSTITUTION_DEPENDENT": {"fresh": 0, "stale": 0, "very_stale": 0},
            "HYBRID": {"fresh": 0, "stale": 0, "very_stale": 0}
        },
        "requires_revalidation": 0
    }
    
    for edge in edges:
        staleness_check = check_edge_staleness(edge, current_time)
        status = staleness_check["status"]
        
        summary[status.lower()] = summary.get(status.lower(), 0) + 1
        
        if not edge.get("last_confirmed_at"):
            summary["never_confirmed"] += 1
        
        if staleness_check["requires_revalidation"]:
            summary["requires_revalidation"] += 1
        
        # Count by decay type
        from .edge_decay import classify_edge_decay_type
        decay_type = classify_edge_decay_type(edge)
        if decay_type in summary["by_decay_type"]:
            summary["by_decay_type"][decay_type][status.lower()] += 1
    
    return summary


if __name__ == "__main__":
    # Test staleness detection
    test_edge = {
        "edge_id": "test-123",
        "edge_type": "influences_drafting",
        "from_entity_id": "staff-1",
        "to_entity_id": "member-1",
        "effective_from": "2024-01-01T00:00:00Z",
        "last_confirmed_at": "2024-06-01T00:00:00Z",  # 200+ days ago
        "weights": {
            "procedural_power": 0.8,
            "temporal_leverage": 0.6,
            "informational_advantage": 0.7,
            "institutional_memory": 0.5,
            "retaliation_capacity": 0.4
        }
    }
    
    current_time = datetime.utcnow()
    staleness = check_edge_staleness(test_edge, current_time)
    print(f"Staleness check: {staleness}")
