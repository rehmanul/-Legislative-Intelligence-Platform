"""
Edge Decay Calculation Library

Provides decay formulas for person-dependent, institution-dependent, and hybrid edges.
Decay models determine how edge weights decrease over time based on entity type and events.
"""

from datetime import datetime
from typing import Dict, Any, Optional, Literal
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent

DecayType = Literal["PERSON_DEPENDENT", "INSTITUTION_DEPENDENT", "HYBRID"]


def parse_timestamp(timestamp_str: str) -> datetime:
    """Parse ISO-8601 UTC timestamp."""
    if timestamp_str.endswith("Z"):
        timestamp_str = timestamp_str[:-1] + "+00:00"
    return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))


def person_dependent_decay(
    base_weight: float,
    days_since_activation: int,
    days_since_departure: Optional[int],
    half_life: int = 180,  # 6 months
    minimum_weight: float = 0.1
) -> float:
    """
    Person-dependent decay: accelerates after person leaves position.
    
    Args:
        base_weight: Original edge weight
        days_since_activation: Days since edge became active
        days_since_departure: Days since person left (None if still active)
        half_life: Days until weight decays to 50% of original
        minimum_weight: Floor weight (prevents edge from disappearing)
    
    Returns:
        Decayed weight
    """
    if days_since_departure is None:
        # No decay while person is active
        return base_weight
    else:
        # Exponential decay after departure
        decay_factor = 0.5 ** (days_since_departure / half_life)
        decayed = base_weight * decay_factor
        return max(decayed, minimum_weight)


def institution_dependent_decay(
    base_weight: float,
    days_since_institutional_change: Optional[int],
    half_life: int = 730,  # 2 years
    minimum_weight: float = 0.1
) -> float:
    """
    Institution-dependent decay: only decays on institutional change.
    
    Args:
        base_weight: Original edge weight
        days_since_institutional_change: Days since institutional change (None if no change)
        half_life: Days until weight decays to 50% of original
        minimum_weight: Floor weight
    
    Returns:
        Decayed weight
    """
    if days_since_institutional_change is None:
        return base_weight
    else:
        # Slower linear decay
        decay_factor = max(0.5, 1.0 - (days_since_institutional_change / (half_life * 2)))
        decayed = base_weight * decay_factor
        return max(decayed, minimum_weight)


def hybrid_decay(
    base_weight: float,
    person_days: Optional[int],
    institution_days: Optional[int],
    person_weight: float = 0.7,
    institution_weight: float = 0.3,
    person_half_life: int = 180,
    institution_half_life: int = 730,
    minimum_weight: float = 0.1
) -> float:
    """
    Hybrid decay: combination of person and institution-dependent decay.
    
    Args:
        base_weight: Original edge weight
        person_days: Days since person departure (None if active)
        institution_days: Days since institutional change (None if no change)
        person_weight: Weight given to person-dependent decay (0.0-1.0)
        institution_weight: Weight given to institution-dependent decay (0.0-1.0)
        person_half_life: Half-life for person-dependent decay
        institution_half_life: Half-life for institution-dependent decay
        minimum_weight: Floor weight
    
    Returns:
        Decayed weight
    """
    person_decayed = person_dependent_decay(
        base_weight, 0, person_days, person_half_life, minimum_weight
    )
    institution_decayed = institution_dependent_decay(
        base_weight, institution_days, institution_half_life, minimum_weight
    )
    # Weighted average favors person-dependent decay
    hybrid = (person_decayed * person_weight) + (institution_decayed * institution_weight)
    return max(hybrid, minimum_weight)


def classify_edge_decay_type(edge: Dict[str, Any]) -> DecayType:
    """
    Classify edge as person-dependent, institution-dependent, or hybrid.
    
    Classification rules:
    - Staff relationships -> PERSON_DEPENDENT
    - Committee authority -> INSTITUTION_DEPENDENT
    - Staff-committee relationships -> HYBRID
    
    Args:
        edge: Edge dictionary with edge_type, from_entity_id, to_entity_id
    
    Returns:
        Decay type classification
    """
    edge_type = edge.get("edge_type", "")
    from_id = edge.get("from_entity_id", "")
    to_id = edge.get("to_entity_id", "")
    
    # Person-dependent edges: staff relationships
    person_dependent_types = [
        "influences_drafting",
        "writes_report_language",
        "signals_pre_clearance",
        "routes_around",
        "translates_for",
        "pre_negotiates_with"
    ]
    
    # Institution-dependent edges: formal authority
    institution_dependent_types = [
        "has_formal_authority_over",
        "controls_agenda_of",
        "can_delay",
        "can_block"
    ]
    
    # Hybrid edges: staff-committee relationships
    hybrid_types = [
        "confers_legitimacy_to",
        "applies_reputational_pressure_to",
        "transfers_memory_to",
        "shares_precedent_with"
    ]
    
    if edge_type in person_dependent_types:
        return "PERSON_DEPENDENT"
    elif edge_type in institution_dependent_types:
        return "INSTITUTION_DEPENDENT"
    elif edge_type in hybrid_types:
        return "HYBRID"
    else:
        # Default to person-dependent for unknown types
        logger.warning(f"Unknown edge type '{edge_type}', defaulting to PERSON_DEPENDENT")
        return "PERSON_DEPENDENT"


def load_decay_config() -> Dict[str, Any]:
    """Load decay configuration from file."""
    config_path = BASE_DIR / "data" / "temporal" / "decay_config__default.json"
    
    if not config_path.exists():
        logger.warning(f"Decay config not found at {config_path}, using defaults")
        return get_default_decay_config()
    
    try:
        return json.loads(config_path.read_text())
    except Exception as e:
        logger.error(f"Failed to load decay config: {e}, using defaults")
        return get_default_decay_config()


def get_default_decay_config() -> Dict[str, Any]:
    """Get default decay configuration."""
    return {
        "decay_types": {
            "PERSON_DEPENDENT": {
                "decay_function": "EXPONENTIAL",
                "half_life_days": 180,
                "minimum_weight": 0.1
            },
            "INSTITUTION_DEPENDENT": {
                "decay_function": "LINEAR",
                "half_life_days": 730,
                "minimum_weight": 0.1
            },
            "HYBRID": {
                "person_weight": 0.7,
                "institution_weight": 0.3
            }
        },
        "entity_type_mappings": {},
        "default_params": {
            "staleness_threshold_days": {
                "person": {
                    "fresh": 90,
                    "stale": 180,
                    "very_stale": 180
                },
                "institution": {
                    "fresh": 180,
                    "stale": 365,
                    "very_stale": 365
                }
            }
        }
    }


def calculate_days_since_departure(
    edge: Dict[str, Any],
    current_time: datetime,
    entities_data: Optional[Dict[str, Any]] = None
) -> Optional[int]:
    """
    Calculate days since person departure for person-dependent edges.
    
    Args:
        edge: Edge dictionary
        current_time: Current timestamp
        entities_data: Optional entities data to check departure dates
    
    Returns:
        Days since departure or None if person still active
    """
    # Check decay_triggers for departure events
    decay_triggers = edge.get("decay_triggers", [])
    for trigger in decay_triggers:
        if "departure" in trigger.get("event_type", "").lower() or \
           "left" in trigger.get("event_type", "").lower():
            event_at = parse_timestamp(trigger["event_at"])
            days = (current_time - event_at).days
            return max(0, days)
    
    # TODO: Check entities_data for departure dates if provided
    # This would require entity schema integration
    
    return None


def calculate_days_since_institutional_change(
    edge: Dict[str, Any],
    current_time: datetime
) -> Optional[int]:
    """
    Calculate days since institutional change for institution-dependent edges.
    
    Args:
        edge: Edge dictionary
        current_time: Current timestamp
    
    Returns:
        Days since change or None if no change
    """
    # Check decay_triggers for institutional change events
    decay_triggers = edge.get("decay_triggers", [])
    for trigger in decay_triggers:
        event_type = trigger.get("event_type", "").lower()
        if "election" in event_type or \
           "reorganization" in event_type or \
           "institutional_change" in event_type:
            event_at = parse_timestamp(trigger["event_at"])
            days = (current_time - event_at).days
            return max(0, days)
    
    return None


def calculate_decayed_weight(
    edge: Dict[str, Any],
    current_time: datetime,
    decay_config: Optional[Dict[str, Any]] = None
) -> Dict[str, float]:
    """
    Calculate decayed weights for all weight axes in an edge.
    
    Args:
        edge: Edge dictionary with weights
        current_time: Current timestamp
        decay_config: Optional decay configuration (loads default if None)
    
    Returns:
        Dictionary of decayed weights (same structure as edge["weights"])
    """
    if decay_config is None:
        decay_config = load_decay_config()
    
    # Get base weights
    base_weights = edge.get("weights", {})
    if not base_weights:
        logger.warning(f"Edge {edge.get('edge_id')} has no weights")
        return {}
    
    # Classify decay type
    decay_type = classify_edge_decay_type(edge)
    
    # Get decay configuration for this type
    type_config = decay_config["decay_types"].get(decay_type, {})
    
    # Calculate decay parameters
    effective_from = parse_timestamp(edge.get("effective_from"))
    days_since_activation = (current_time - effective_from).days
    
    decayed_weights = {}
    
    if decay_type == "PERSON_DEPENDENT":
        half_life = type_config.get("half_life_days", 180)
        minimum = type_config.get("minimum_weight", 0.1)
        days_departure = calculate_days_since_departure(edge, current_time)
        
        for axis, base_weight in base_weights.items():
            decayed = person_dependent_decay(
                base_weight, days_since_activation, days_departure,
                half_life, minimum
            )
            decayed_weights[axis] = decayed
    
    elif decay_type == "INSTITUTION_DEPENDENT":
        half_life = type_config.get("half_life_days", 730)
        minimum = type_config.get("minimum_weight", 0.1)
        days_change = calculate_days_since_institutional_change(edge, current_time)
        
        for axis, base_weight in base_weights.items():
            decayed = institution_dependent_decay(
                base_weight, days_change, half_life, minimum
            )
            decayed_weights[axis] = decayed
    
    elif decay_type == "HYBRID":
        person_weight = type_config.get("person_weight", 0.7)
        institution_weight = type_config.get("institution_weight", 0.3)
        person_half_life = decay_config["decay_types"]["PERSON_DEPENDENT"].get("half_life_days", 180)
        institution_half_life = decay_config["decay_types"]["INSTITUTION_DEPENDENT"].get("half_life_days", 730)
        minimum = type_config.get("minimum_weight", 0.1)
        
        days_departure = calculate_days_since_departure(edge, current_time)
        days_change = calculate_days_since_institutional_change(edge, current_time)
        
        for axis, base_weight in base_weights.items():
            decayed = hybrid_decay(
                base_weight, days_departure, days_change,
                person_weight, institution_weight,
                person_half_life, institution_half_life, minimum
            )
            decayed_weights[axis] = decayed
    
    return decayed_weights


def is_edge_stale(
    edge: Dict[str, Any],
    staleness_threshold_days: Dict[str, Dict[str, int]]
) -> bool:
    """
    Check if edge is stale based on last confirmation.
    
    Args:
        edge: Edge dictionary
        staleness_threshold_days: Threshold configuration
    
    Returns:
        True if edge is stale
    """
    last_confirmed = edge.get("last_confirmed_at")
    if not last_confirmed:
        return True  # Never confirmed = stale
    
    # Classification determines threshold type
    decay_type = classify_edge_decay_type(edge)
    threshold_type = "person" if decay_type == "PERSON_DEPENDENT" else "institution"
    thresholds = staleness_threshold_days.get(threshold_type, {"stale": 180})
    
    try:
        last_confirmed_time = parse_timestamp(last_confirmed)
        current_time = datetime.utcnow()
        days_since = (current_time - last_confirmed_time).days
        
        stale_threshold = thresholds.get("stale", 180)
        return days_since >= stale_threshold
    except Exception as e:
        logger.error(f"Error checking staleness: {e}")
        return True  # Assume stale on error


if __name__ == "__main__":
    # Test decay calculations
    test_edge = {
        "edge_id": "test-123",
        "edge_type": "influences_drafting",
        "from_entity_id": "staff-1",
        "to_entity_id": "member-1",
        "effective_from": "2024-01-01T00:00:00Z",
        "weights": {
            "procedural_power": 0.8,
            "temporal_leverage": 0.6,
            "informational_advantage": 0.7,
            "institutional_memory": 0.5,
            "retaliation_capacity": 0.4
        },
        "decay_triggers": []
    }
    
    current_time = datetime.utcnow()
    decayed = calculate_decayed_weight(test_edge, current_time)
    print(f"Decayed weights: {decayed}")
