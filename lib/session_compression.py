"""
Session Compression Library

Models how relationships compress and power dynamics shift as legislative sessions end.
Compression factors increase temporal leverage and procedural power as session ends.
"""

from datetime import datetime, date
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
import logging

from .edge_decay import parse_timestamp

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent


def load_session_boundaries() -> Dict[str, Any]:
    """Load session boundaries configuration."""
    config_path = BASE_DIR / "data" / "temporal" / "session_boundaries.json"
    
    if not config_path.exists():
        logger.warning(f"Session boundaries config not found at {config_path}, using defaults")
        return get_default_session_boundaries()
    
    try:
        return json.loads(config_path.read_text())
    except Exception as e:
        logger.error(f"Failed to load session boundaries: {e}, using defaults")
        return get_default_session_boundaries()


def get_default_session_boundaries() -> Dict[str, Any]:
    """Get default session boundaries for 118th Congress (2023-2025)."""
    return {
        "congress": 118,
        "sessions": [
            {
                "session": 1,
                "start_date": "2023-01-03",
                "end_date": "2023-12-31",
                "recess_periods": [
                    {"start": "2023-07-28", "end": "2023-09-05"},
                    {"start": "2023-11-21", "end": "2023-12-01"}
                ]
            },
            {
                "session": 2,
                "start_date": "2024-01-08",
                "end_date": "2025-01-03",
                "recess_periods": [
                    {"start": "2024-07-26", "end": "2024-09-09"},
                    {"start": "2024-11-22", "end": "2024-12-02"}
                ]
            }
        ],
        "lame_duck_periods": [
            {"start": "2024-11-05", "end": "2025-01-03"}  # Post-election, pre-swearing-in
        ]
    }


def get_current_session(current_date: datetime) -> Optional[Dict[str, Any]]:
    """
    Get current session information.
    
    Args:
        current_date: Current date/time
    
    Returns:
        Session dictionary or None if no session found
    """
    boundaries = load_session_boundaries()
    current_date_str = current_date.date().isoformat()
    
    for session in boundaries.get("sessions", []):
        start_date = session.get("start_date")
        end_date = session.get("end_date")
        
        if start_date <= current_date_str <= end_date:
            return session
    
    return None


def is_lame_duck_period(current_date: datetime) -> bool:
    """
    Check if current date is in a lame-duck period.
    
    Args:
        current_date: Current date/time
    
    Returns:
        True if in lame-duck period
    """
    boundaries = load_session_boundaries()
    current_date_str = current_date.date().isoformat()
    
    for period in boundaries.get("lame_duck_periods", []):
        start = period.get("start")
        end = period.get("end")
        
        if start <= current_date_str <= end:
            return True
    
    return False


def calculate_days_until_session_end(current_date: datetime) -> Optional[int]:
    """
    Calculate days until current session ends.
    
    Args:
        current_date: Current date/time
    
    Returns:
        Days until session end, or None if not in session
    """
    session = get_current_session(current_date)
    if not session:
        return None
    
    end_date_str = session.get("end_date")
    if not end_date_str:
        return None
    
    try:
        end_date = date.fromisoformat(end_date_str)
        current_date_obj = current_date.date()
        days = (end_date - current_date_obj).days
        return max(0, days)
    except Exception as e:
        logger.error(f"Error calculating days until session end: {e}")
        return None


def calculate_session_compression(
    days_until_session_end: Optional[int],
    compression_start_days: int = 60
) -> float:
    """
    Calculate compression factor as session approaches end.
    
    Compression factor: 1.0 (no compression) → 1.5 (maximum compression)
    - Compression starts 60 days before session end
    - Reaches 1.5x weight at session end
    - Lame-duck period: 2.0x compression
    
    Args:
        days_until_session_end: Days until session end (None if not in session)
        compression_start_days: Days before end when compression starts
    
    Returns:
        Compression factor (1.0 = no compression, >1.0 = increased weight)
    """
    if days_until_session_end is None:
        return 1.0  # Not in session, no compression
    
    if days_until_session_end < 0:
        # Past session end (shouldn't happen, but handle gracefully)
        return 2.0  # Maximum compression
    
    if days_until_session_end > compression_start_days:
        return 1.0  # Too early for compression
    
    # Linear compression from 1.0 to 1.5
    # At compression_start_days: 1.0
    # At 0 days: 1.5
    compression_ratio = 1.0 + (0.5 * (1.0 - days_until_session_end / compression_start_days))
    return compression_ratio


def apply_session_compression(
    weights: Dict[str, float],
    compression_factor: float,
    affected_axes: Optional[List[str]] = None
) -> Dict[str, float]:
    """
    Apply session compression to specific weight axes.
    
    As session ends, temporal_leverage and procedural_power become more valuable.
    
    Args:
        weights: Dictionary of weight axes
        compression_factor: Compression factor to apply (>1.0 increases weights)
        affected_axes: List of axes to compress (defaults to temporal_leverage and procedural_power)
    
    Returns:
        Dictionary of compressed weights (same structure as weights)
    """
    if affected_axes is None:
        affected_axes = ["temporal_leverage", "procedural_power"]
    
    compressed = weights.copy()
    for axis in affected_axes:
        if axis in compressed:
            compressed[axis] = min(1.0, compressed[axis] * compression_factor)
    
    return compressed


def get_session_compression_for_date(current_date: datetime) -> float:
    """
    Get compression factor for current date.
    
    Args:
        current_date: Current date/time
    
    Returns:
        Compression factor
    """
    # Check if lame-duck period (maximum compression)
    if is_lame_duck_period(current_date):
        return 2.0
    
    # Calculate compression based on days until session end
    days_until_end = calculate_days_until_session_end(current_date)
    if days_until_end is None:
        return 1.0  # Not in session
    
    return calculate_session_compression(days_until_end)


def apply_session_compression_to_weights(
    weights: Dict[str, float],
    current_date: datetime,
    affected_axes: Optional[List[str]] = None
) -> Dict[str, float]:
    """
    Apply session compression to weights based on current date.
    
    Convenience function that combines compression calculation and application.
    
    Args:
        weights: Dictionary of weight axes
        current_date: Current date/time
        affected_axes: List of axes to compress
    
    Returns:
        Dictionary of compressed weights
    """
    compression_factor = get_session_compression_for_date(current_date)
    return apply_session_compression(weights, compression_factor, affected_axes)


if __name__ == "__main__":
    # Test session compression
    test_weights = {
        "procedural_power": 0.8,
        "temporal_leverage": 0.6,
        "informational_advantage": 0.7,
        "institutional_memory": 0.5,
        "retaliation_capacity": 0.4
    }
    
    # Test 30 days before session end (should have compression)
    current_date = datetime(2024, 11, 1)  # 30 days before 2024 session end
    compression = get_session_compression_for_date(current_date)
    compressed = apply_session_compression_to_weights(test_weights, current_date)
    
    print(f"Compression factor: {compression}")
    print(f"Original weights: {test_weights}")
    print(f"Compressed weights: {compressed}")
