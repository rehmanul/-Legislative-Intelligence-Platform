"""
Graph Query Interface
Query Congressional influence graph (who influences X, what is Y's power, filter by state/policy)
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Set
from datetime import datetime

def load_graph(base_dir: Path) -> Dict[str, Any]:
    """Load graph data"""
    graph_file = base_dir / "data" / "graph" / "graph.json"
    if graph_file.exists():
        try:
            return json.loads(graph_file.read_text(encoding='utf-8'))
        except:
            pass
    return {"nodes": {}, "edges": []}

def load_classifications(base_dir: Path) -> Dict[str, List[Dict[str, Any]]]:
    """Load power classifications"""
    classifications_dir = base_dir / "data" / "power_classifications"
    classifications = {}
    
    if classifications_dir.exists():
        for file in classifications_dir.glob("*_all.json"):
            try:
                data = json.loads(file.read_text(encoding='utf-8'))
                if isinstance(data, list):
                    for cls in data:
                        entity_id = cls.get("entity_id")
                        if entity_id:
                            classifications.setdefault(entity_id, []).append(cls)
            except:
                pass
    
    return classifications

def who_influences(
    entity_id: str,
    base_dir: Path,
    edge_types: Optional[List[str]] = None,
    legislative_state: Optional[str] = None,
    min_weight: float = 0.0
) -> List[Dict[str, Any]]:
    """
    Find all entities that influence a target entity
    
    Args:
        entity_id: Target entity ID
        base_dir: Base directory for data files
        edge_types: Filter by edge types (None = all types)
        legislative_state: Filter by legislative state (None = all states)
        min_weight: Minimum aggregate weight threshold
    
    Returns:
        List of influencing entities with edge details
    """
    graph = load_graph(base_dir)
    nodes = graph.get("nodes", {})
    edges = graph.get("edges", [])
    
    # Find all edges pointing to entity_id
    influencing_edges = [
        e for e in edges
        if e.get("to_entity_id") == entity_id
        and e.get("edge_status") == "ACTIVE"
    ]
    
    # Filter by edge types
    if edge_types:
        influencing_edges = [e for e in influencing_edges if e.get("edge_type") in edge_types]
    
    # Filter by legislative state
    if legislative_state:
        influencing_edges = [
            e for e in influencing_edges
            if e.get("legislative_state") == legislative_state or e.get("legislative_state") is None
        ]
    
    # Calculate aggregate weight and filter
    results = []
    for edge in influencing_edges:
        weights = edge.get("weights", {})
        aggregate_weight = sum(weights.values()) / len(weights) if weights else 0.0
        
        if aggregate_weight >= min_weight:
            from_entity_id = edge.get("from_entity_id")
            from_entity = nodes.get(from_entity_id, {})
            
            results.append({
                "influencing_entity_id": from_entity_id,
                "influencing_entity": from_entity.get("name", from_entity_id),
                "entity_type": from_entity.get("entity_type"),
                "edge_type": edge.get("edge_type"),
                "edge_id": edge.get("edge_id"),
                "weights": weights,
                "aggregate_weight": aggregate_weight,
                "legislative_state": edge.get("legislative_state")
            })
    
    # Sort by aggregate weight (descending)
    results.sort(key=lambda x: x.get("aggregate_weight", 0.0), reverse=True)
    
    return results

def what_is_power(
    entity_id: str,
    base_dir: Path,
    legislative_state: Optional[str] = None,
    policy_area: Optional[str] = None,
    bill_id: Optional[str] = None,
    committee_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Get power classification for an entity
    
    Args:
        entity_id: Entity ID
        base_dir: Base directory for data files
        legislative_state: Filter by legislative state
        policy_area: Filter by policy area
        bill_id: Filter by bill ID
        committee_id: Filter by committee ID
    
    Returns:
        Power classification record (PRIMARY/SECONDARY/SHADOW) or None
    """
    classifications = load_classifications(base_dir)
    entity_classifications = classifications.get(entity_id, [])
    
    if not entity_classifications:
        return None
    
    # Filter by context
    filtered = []
    for cls in entity_classifications:
        context = cls.get("context", {})
        
        # Check if context matches
        matches = True
        if legislative_state and context.get("legislative_state") != legislative_state:
            matches = False
        if policy_area and context.get("policy_area") != policy_area:
            matches = False
        if bill_id and context.get("bill_id") != bill_id:
            matches = False
        if committee_id and context.get("committee_id") != committee_id:
            matches = False
        
        if matches:
            filtered.append(cls)
    
    if not filtered:
        # Return most recent if no context match
        entity_classifications.sort(
            key=lambda c: c.get("temporal_validity", {}).get("effective_from", ""),
            reverse=True
        )
        return entity_classifications[0] if entity_classifications else None
    
    # Resolve conflicts (most specific wins)
    if len(filtered) > 1:
        # Sort by specificity
        def specificity_score(c: Dict[str, Any]) -> int:
            ctx = c.get("context", {})
            score = 0
            if ctx.get("bill_id"):
                score += 100
            if ctx.get("committee_id"):
                score += 10
            if ctx.get("policy_area"):
                score += 5
            if ctx.get("legislative_state"):
                score += 1
            return score
        
        filtered.sort(key=specificity_score, reverse=True)
    
    return filtered[0]

def find_influence_path(
    from_entity_id: str,
    to_entity_id: str,
    base_dir: Path,
    max_depth: int = 3,
    legislative_state: Optional[str] = None
) -> Optional[List[Dict[str, Any]]]:
    """
    Find influence path between two entities (BFS)
    
    Returns:
        List of edges forming the path, or None if no path found
    """
    graph = load_graph(base_dir)
    edges = graph.get("edges", [])
    
    # Build adjacency list
    adjacency = {}
    for edge in edges:
        if edge.get("edge_status") != "ACTIVE":
            continue
        if legislative_state and edge.get("legislative_state") != legislative_state:
            continue
        
        from_id = edge.get("from_entity_id")
        to_id = edge.get("to_entity_id")
        if from_id not in adjacency:
            adjacency[from_id] = []
        adjacency[from_id].append((to_id, edge))
    
    # BFS
    queue = [(from_entity_id, [])]
    visited = {from_entity_id}
    
    while queue and len(queue[0][1]) < max_depth:
        current, path = queue.pop(0)
        
        if current == to_entity_id:
            return path
        
        for neighbor, edge in adjacency.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [edge]))
    
    return None

def filter_by_state(
    entities: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    legislative_state: str
) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Filter entities and edges by legislative state
    
    Returns:
        (filtered_entities, filtered_edges)
    """
    # Filter edges
    filtered_edges = [
        e for e in edges
        if e.get("legislative_state") == legislative_state or e.get("legislative_state") is None
    ]
    
    # Get entity IDs from filtered edges
    relevant_entity_ids = set()
    for edge in filtered_edges:
        relevant_entity_ids.add(edge.get("from_entity_id"))
        relevant_entity_ids.add(edge.get("to_entity_id"))
    
    # Filter entities
    filtered_entities = [
        e for e in entities
        if e.get("entity_id") in relevant_entity_ids
    ]
    
    return filtered_entities, filtered_edges

def filter_by_policy_area(
    entities: List[Dict[str, Any]],
    policy_area: str
) -> List[Dict[str, Any]]:
    """
    Filter entities by policy area (checks tags, policy_focus_tags, industry_tags)
    """
    filtered = []
    
    for entity in entities:
        entity_type = entity.get("entity_type")
        
        # Check relevant tags based on entity type
        tags = []
        if entity_type == "industry_org":
            tags = entity.get("industry_tags", [])
        elif entity_type == "nonprofit_org":
            tags = entity.get("policy_focus_tags", [])
        elif entity_type == "coalition":
            tags = entity.get("policy_focus_tags", [])
        
        # Check if policy area matches
        if policy_area.lower() in [tag.lower() for tag in tags]:
            filtered.append(entity)
    
    return filtered

def get_entity_summary(
    entity_id: str,
    base_dir: Path,
    legislative_state: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get comprehensive summary for an entity:
    - Entity details
    - Power classification
    - Influencing entities
    - Entities influenced by this entity
    """
    graph = load_graph(base_dir)
    nodes = graph.get("nodes", {})
    edges = graph.get("edges", [])
    
    entity = nodes.get(entity_id)
    if not entity:
        return {"error": f"Entity {entity_id} not found"}
    
    # Get power classification
    power = what_is_power(entity_id, base_dir, legislative_state=legislative_state)
    
    # Get influencing entities
    influencing = who_influences(entity_id, base_dir, legislative_state=legislative_state)
    
    # Get entities influenced by this entity
    influenced = [
        {
            "entity_id": e.get("to_entity_id"),
            "entity": nodes.get(e.get("to_entity_id"), {}).get("name", e.get("to_entity_id")),
            "edge_type": e.get("edge_type"),
            "weights": e.get("weights", {})
        }
        for e in edges
        if e.get("from_entity_id") == entity_id
        and e.get("edge_status") == "ACTIVE"
        and (not legislative_state or e.get("legislative_state") == legislative_state or e.get("legislative_state") is None)
    ]
    
    return {
        "entity_id": entity_id,
        "entity": entity,
        "power_classification": power,
        "influencing_entities": influencing,
        "influenced_entities": influenced,
        "summary": {
            "total_influencing": len(influencing),
            "total_influenced": len(influenced),
            "power_type": power.get("control_type") if power else "UNKNOWN"
        }
    }
