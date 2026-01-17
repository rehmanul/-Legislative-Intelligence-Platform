"""
Phase-Based Power Reweighting Library

Adjusts edge weights based on current legislative phase, since procedural power
varies by phase. For example, committee chairs have high procedural_power in
COMM_EVT but lower procedural_power in PRE_EVT or FLOOR_EVT.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import json
import logging
from datetime import datetime

from app.models import LegislativeState

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent


def load_phase_multipliers() -> Dict[str, Dict[str, float]]:
    """Load phase multipliers from configuration file."""
    config_path = BASE_DIR / "data" / "temporal" / "phase_multipliers.json"
    
    if not config_path.exists():
        logger.warning(f"Phase multipliers config not found at {config_path}, using defaults")
        return get_default_phase_multipliers()
    
    try:
        config = json.loads(config_path.read_text())
        return config.get("phase_multipliers", get_default_phase_multipliers())
    except Exception as e:
        logger.error(f"Failed to load phase multipliers: {e}, using defaults")
        return get_default_phase_multipliers()


def get_default_phase_multipliers() -> Dict[str, Dict[str, float]]:
    """Get default phase multipliers configuration."""
    return {
        "PRE_EVT": {
            "procedural_power": 0.3,
            "temporal_leverage": 0.5,
            "informational_advantage": 0.7,
            "institutional_memory": 0.8,
            "retaliation_capacity": 0.2
        },
        "INTRO_EVT": {
            "procedural_power": 0.4,
            "temporal_leverage": 0.6,
            "informational_advantage": 0.8,
            "institutional_memory": 0.8,
            "retaliation_capacity": 0.3
        },
        "COMM_EVT": {
            "procedural_power": 1.0,
            "temporal_leverage": 1.0,
            "informational_advantage": 0.9,
            "institutional_memory": 0.9,
            "retaliation_capacity": 0.6
        },
        "FLOOR_EVT": {
            "procedural_power": 0.4,
            "temporal_leverage": 0.8,
            "informational_advantage": 0.5,
            "institutional_memory": 0.7,
            "retaliation_capacity": 0.9
        },
        "FINAL_EVT": {
            "procedural_power": 0.5,
            "temporal_leverage": 0.9,
            "informational_advantage": 0.4,
            "institutional_memory": 0.6,
            "retaliation_capacity": 1.0
        },
        "IMPL_EVT": {
            "procedural_power": 0.2,
            "temporal_leverage": 0.3,
            "informational_advantage": 0.6,
            "institutional_memory": 0.8,
            "retaliation_capacity": 0.1
        }
    }


def apply_phase_reweighting(
    base_weights: Dict[str, float],
    current_phase: LegislativeState,
    phase_multipliers: Optional[Dict[str, Dict[str, float]]] = None
) -> Dict[str, float]:
    """
    Apply phase-based multipliers to edge weights.
    
    Example: Committee chairs have high procedural_power in COMM_EVT
    but lower procedural_power in PRE_EVT or FLOOR_EVT.
    
    Args:
        base_weights: Dictionary of weight axes (procedural_power, etc.)
        current_phase: Current legislative state
        phase_multipliers: Optional phase multipliers (loads from config if None)
    
    Returns:
        Dictionary of reweighted weights (same structure as base_weights)
    """
    if phase_multipliers is None:
        phase_multipliers = load_phase_multipliers()
    
    # Get multipliers for current phase
    phase_str = current_phase.value if hasattr(current_phase, 'value') else str(current_phase)
    multipliers = phase_multipliers.get(phase_str, {})
    
    # Apply multipliers to each weight axis
    reweighted = {}
    for axis, base_weight in base_weights.items():
        multiplier = multipliers.get(axis, 1.0)  # Default to 1.0 if not specified
        # Clamp to [0, 1] range
        reweighted[axis] = min(1.0, max(0.0, base_weight * multiplier))
    
    return reweighted


def get_phase_reweighting_summary(
    current_phase: LegislativeState,
    phase_multipliers: Optional[Dict[str, Dict[str, float]]] = None
) -> Dict[str, Any]:
    """
    Get summary of phase multipliers for current phase.
    
    Args:
        current_phase: Current legislative state
        phase_multipliers: Optional phase multipliers
    
    Returns:
        Summary dictionary with multipliers and descriptions
    """
    if phase_multipliers is None:
        phase_multipliers = load_phase_multipliers()
    
    phase_str = current_phase.value if hasattr(current_phase, 'value') else str(current_phase)
    multipliers = phase_multipliers.get(phase_str, {})
    
    # Identify which axes are boosted or suppressed
    boosted = [axis for axis, mult in multipliers.items() if mult > 1.0]
    suppressed = [axis for axis, mult in multipliers.items() if mult < 1.0]
    neutral = [axis for axis, mult in multipliers.items() if mult == 1.0]
    
    return {
        "phase": phase_str,
        "multipliers": multipliers,
        "boosted_axes": boosted,
        "suppressed_axes": suppressed,
        "neutral_axes": neutral
    }


if __name__ == "__main__":
    # Test phase reweighting
    from app.models import LegislativeState
    
    test_weights = {
        "procedural_power": 0.8,
        "temporal_leverage": 0.6,
        "informational_advantage": 0.7,
        "institutional_memory": 0.5,
        "retaliation_capacity": 0.4
    }
    
    # Test COMM_EVT (should boost procedural_power)
    reweighted_comm = apply_phase_reweighting(test_weights, LegislativeState.COMM_EVT)
    print(f"COMM_EVT reweighted: {reweighted_comm}")
    
    # Test PRE_EVT (should suppress procedural_power)
    reweighted_pre = apply_phase_reweighting(test_weights, LegislativeState.PRE_EVT)
    print(f"PRE_EVT reweighted: {reweighted_pre}")
