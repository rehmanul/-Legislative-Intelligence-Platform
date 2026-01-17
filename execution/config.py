"""
Execution configuration.

Manages configuration for execution channels, approval, and monitoring.
All execution is in dry-run mode by default.
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# ============================================================================
# SMTP Configuration
# ============================================================================

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

# Email Settings
FROM_EMAIL = os.getenv("FROM_EMAIL", "")
REPLY_TO_EMAIL = os.getenv("REPLY_TO_EMAIL", "")

# ============================================================================
# Execution Settings
# ============================================================================

# DRY_RUN_MODE must remain TRUE for Phase 1
DRY_RUN_MODE = os.getenv("DRY_RUN_MODE", "true").lower() == "true"

# REQUIRE_APPROVAL must remain TRUE for Phase 1
REQUIRE_APPROVAL = os.getenv("REQUIRE_APPROVAL", "true").lower() == "true"

# ============================================================================
# File Paths
# ============================================================================

# Execution data directory
EXECUTION_DIR = BASE_DIR / "execution"
EXECUTION_DIR.mkdir(exist_ok=True)

# Contact storage
CONTACTS_FILE = EXECUTION_DIR / "contacts.json"

# Activity logging
ACTIVITY_LOG_FILE = EXECUTION_DIR / "activity-log.jsonl"

# Approval queue (JSON-backed for Phase 1)
APPROVAL_QUEUE_FILE = EXECUTION_DIR / "approval-queue.json"

# Template directory (for Phase 2)
TEMPLATE_DIR = BASE_DIR / "execution" / "templates"
TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)

# Dry-run log
DRY_RUN_LOG_FILE = EXECUTION_DIR / "dry-run-log.jsonl"

# ============================================================================
# Validation
# ============================================================================

def validate_config() -> list:
    """
    Validate configuration settings.
    
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    if not DRY_RUN_MODE:
        errors.append("DRY_RUN_MODE must be True in Phase 1")
    
    if not REQUIRE_APPROVAL:
        errors.append("REQUIRE_APPROVAL must be True in Phase 1")
    
    # SMTP config validation (warnings only, not required in dry-run)
    if not DRY_RUN_MODE:
        if not SMTP_SERVER:
            errors.append("SMTP_SERVER required when not in dry-run mode")
        if not FROM_EMAIL:
            errors.append("FROM_EMAIL required when not in dry-run mode")
    
    return errors
