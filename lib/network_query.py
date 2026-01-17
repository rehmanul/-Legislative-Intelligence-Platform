"""
Network Query Utilities

High-level query functions for the Congressional network graph.
Provides abstraction over raw edge/entity data.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from datetime import datetime

# Base directory
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
ENTITIES_DIR = DATA_DIR / "entities"
EDGES_DIR = DATA_DIR / "edges"


def load_edges() -> List[Dict[str, Any]]:
    """Load all influence edges."""
    edges_file = EDGES_DIR / "influence_edges__derived.json"
    if not edges_file.exists():
        return []
    
    try:
        with open(edges_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("edges", [])
    except Exception as e:
        print(f"Warning: Failed to load edges: {e}")
        return []


def load_staff() -> List[Dict[str, Any]]:
    """Load all staff entities."""
    staff_file = ENTITIES_DIR / "staff__snapshot.json"
    if not staff_file.exists():
        return []
    
    try:
        with open(staff_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("staff", [])
    except Exception as e:
        print(f"Warning: Failed to load staff: {e}")
        return []


def get_influence_paths(
    from_id: str,
    to_id: str,
    max_depth: int = 3,
    edge_type: Optional[str] = None,
    legislative_state: Optional[str] = None
) -> List[List[Dict[str, Any]]]:
    """
    Find all influence paths from one entity to another.
    
    Args:
        from_id: Source entity ID
        to_id: Target entity ID
        max_depth: Maximum path length (default: 3)
        edge_type: Filter by edge type (optional)
        legislative_state: Filter by legislative state (optional)
    
    Returns:
        List of paths, where each path is a list of edges
    """
    edges = load_edges()
    
    # Filter edges
    filtered_edges = [
        e for e in edges
        if e.get("edge_status") == "ACTIVE"
        and (edge_type is None or e.get("edge_type") == edge_type)
        and (legislative_state is None or e.get("legislative_state") == legislative_state or e.get("legislative_state") is None)
    ]
    
    # Build adjacency list
    graph: Dict[str, List[Dict[str, Any]]] = {}
    for edge in filtered_edges:
        from_entity = edge.get("from_entity_id")
        if from_entity not in graph:
            graph[from_entity] = []
        graph[from_entity].append(edge)
    
    # DFS to find paths
    paths: List[List[Dict[str, Any]]] = []
    
    def dfs(current: str, target: str, path: List[Dict[str, Any]], depth: int, visited: Set[str]):
        if depth > max_depth:
            return
        
        if current == target and len(path) > 0:
            paths.append(path.copy())
            return
        
        if current not in graph:
            return
        
        visited.add(current)
        
        for edge in graph[current]:
            next_entity = edge.get("to_entity_id")
            if next_entity not in visited:
                path.append(edge)
                dfs(next_entity, target, path, depth + 1, visited)
                path.pop()
        
        visited.remove(current)
    
    dfs(from_id, to_id, [], 0, set())
    return paths


def get_entities_with_influence_type(
    entity_id: str,
    edge_type: str,
    direction: str = "outgoing"
) -> List[str]:
    """
    Get entities connected to a given entity by a specific edge type.
    
    Args:
        entity_id: Entity ID to query
        edge_type: Type of influence edge
        direction: "outgoing" (entity influences others) or "incoming" (others influence entity)
    
    Returns:
        List of connected entity IDs
    """
    edges = load_edges()
    
    filtered_edges = [
        e for e in edges
        if e.get("edge_status") == "ACTIVE"
        and e.get("edge_type") == edge_type
    ]
    
    connected_ids = set()
    
    if direction == "outgoing":
        for edge in filtered_edges:
            if edge.get("from_entity_id") == entity_id:
                connected_ids.add(edge.get("to_entity_id"))
    else:  # incoming
        for edge in filtered_edges:
            if edge.get("to_entity_id") == entity_id:
                connected_ids.add(edge.get("from_entity_id"))
    
    return list(connected_ids)


def get_power_actors_for_state(
    state: str,
    context: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Get power actors for a specific legislative state.
    
    Args:
        state: Legislative state (PRE_EVT, INTRO_EVT, COMM_EVT, etc.)
        context: Additional context (bill_id, policy_area, etc.)
    
    Returns:
        List of power actors with their influence edges
    """
    edges = load_edges()
    
    # Filter edges relevant to this state
    state_edges = [
        e for e in edges
        if e.get("edge_status") == "ACTIVE"
        and (e.get("legislative_state") == state or e.get("legislative_state") is None)
    ]
    
    # Group by from_entity_id and calculate aggregate power
    actor_power: Dict[str, Dict[str, Any]] = {}
    
    for edge in state_edges:
        from_id = edge.get("from_entity_id")
        if from_id not in actor_power:
            actor_power[from_id] = {
                "entity_id": from_id,
                "edges": [],
                "total_procedural_power": 0.0,
                "total_temporal_leverage": 0.0,
                "edge_count": 0
            }
        
        actor_power[from_id]["edges"].append(edge)
        weights = edge.get("weights", {})
        actor_power[from_id]["total_procedural_power"] += weights.get("procedural_power", 0.0)
        actor_power[from_id]["total_temporal_leverage"] += weights.get("temporal_leverage", 0.0)
        actor_power[from_id]["edge_count"] += 1
    
    # Convert to list and sort by power
    actors = list(actor_power.values())
    actors.sort(key=lambda x: x["total_procedural_power"] + x["total_temporal_leverage"], reverse=True)
    
    return actors


def get_active_edges_for_entity(entity_id: str) -> List[Dict[str, Any]]:
    """Get all active edges for a given entity."""
    edges = load_edges()
    
    return [
        e for e in edges
        if e.get("edge_status") == "ACTIVE"
        and (e.get("from_entity_id") == entity_id or e.get("to_entity_id") == entity_id)
    ]
