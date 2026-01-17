"""
Mode Configuration Utility
Implements dependency failure policy: PRODUCTION (fail-fast) vs DEVELOPMENT (graceful degradation)
"""

import os
from typing import Literal

SystemMode = Literal["PRODUCTION", "DEVELOPMENT"]


def get_system_mode() -> SystemMode:
    """
    Get system mode from environment variable.
    
    Returns:
        SystemMode: "PRODUCTION" or "DEVELOPMENT"
    
    Raises:
        ValueError: If mode is not set or invalid
    """
    mode = os.getenv("SYSTEM_MODE", "").upper()
    
    if not mode:
        raise ValueError(
            "SYSTEM_MODE environment variable must be set. "
            "Set SYSTEM_MODE=PRODUCTION or SYSTEM_MODE=DEVELOPMENT"
        )
    
    if mode not in ("PRODUCTION", "DEVELOPMENT"):
        raise ValueError(
            f"Invalid SYSTEM_MODE: {mode}. Must be 'PRODUCTION' or 'DEVELOPMENT'"
        )
    
    return mode  # type: ignore


def is_production_mode() -> bool:
    """Check if system is in PRODUCTION mode"""
    try:
        return get_system_mode() == "PRODUCTION"
    except ValueError:
        # If mode not set, default to DEVELOPMENT for safety
        return False


def is_development_mode() -> bool:
    """Check if system is in DEVELOPMENT mode"""
    try:
        return get_system_mode() == "DEVELOPMENT"
    except ValueError:
        # If mode not set, default to DEVELOPMENT for safety
        return True


def validate_mode() -> SystemMode:
    """
    Validate mode is set and return it.
    Called at agent startup to ensure mode is configured.
    """
    return get_system_mode()
