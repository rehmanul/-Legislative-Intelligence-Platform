"""
Adaptive Network Query Utilities

Query utilities that adapt to legislative state and temporal dynamics.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from .network_query import load_edges, get_power_actors_for_state


def get_active_influence_paths(
    from_id: str,
    to_id: str,
    state: Optional[str] = None
) -> List[List[Dict[str, Any]]]:
    """
    Get active influence paths for a specific legislative state.
    
    Args:
        from_id: Source entity ID
        to_id: Target entity ID
        state: Legislative state (PRE_EVT, INTRO_EVT, etc.)
    
    Returns:
        List of active paths (only edges with ACTIVE status)
    """
    from .network_query import get_influence_paths
    
    paths = get_influence_paths(from_id, to_id, max_depth=3, legislative_state=state)
    
    # Filter to only active edges
    active_paths = []
    for path in paths:
        active_path = [e for e in path if e.get("edge_status") == "ACTIVE"]
        if active_path:
            active_paths.append(active_path)
    
    return active_paths


def predict_edge_strength_after_event(
    entity_id: str,
    event_type: str
) -> Dict[str, float]:
    """
    Predict edge strength changes after a hypothetical event.
    
    Args:
        entity_id: Entity ID
        event_type: Type of event (e.g., "committee_assignment", "staff_departure")
    
    Returns:
        Predicted weight changes
    """
    # Placeholder prediction logic
    # In production, this would use historical data and patterns
    
    predictions = {
        "procedural_power": 0.0,
        "temporal_leverage": 0.0,
        "informational_advantage": 0.0,
        "institutional_memory": 0.0,
        "retaliation_capacity": 0.0
    }
    
    # Example predictions based on event type
    if event_type == "committee_assignment":
        predictions["procedural_power"] = +0.2
        predictions["temporal_leverage"] = +0.1
    elif event_type == "staff_departure":
        predictions["institutional_memory"] = -0.3
        predictions["informational_advantage"] = -0.2
    elif event_type == "leadership_change":
        predictions["procedural_power"] = +0.3
        predictions["retaliation_capacity"] = +0.2
    
    return predictions


def get_network_state_for_legislative_state(state: str) -> Dict[str, Any]:
    """
    Get network state snapshot for a specific legislative state.
    
    Args:
        state: Legislative state (PRE_EVT, INTRO_EVT, etc.)
    
    Returns:
        Network state summary
    """
    edges = load_edges()
    
    # Filter edges for this state
    state_edges = [
        e for e in edges
        if e.get("edge_status") == "ACTIVE"
        and (e.get("legislative_state") == state or e.get("legislative_state") is None)
    ]
    
    # Get power actors
    power_actors = get_power_actors_for_state(state)
    
    return {
        "legislative_state": state,
        "active_edges": len(state_edges),
        "power_actors": len(power_actors),
        "top_power_actors": power_actors[:10]  # Top 10 by power
    }
