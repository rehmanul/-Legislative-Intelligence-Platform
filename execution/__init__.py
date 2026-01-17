"""
Execution Integration Layer - Phase 1

This package provides execution infrastructure for agent-orchestrator.
Phase 1 implements dry-run only execution with approval gates.

Components:
- channel: EXEC_RUN channel abstraction
- email_provider: SMTP email integration (dry-run mode)
- approval_manager: Pre-execution approval system
- monitor: Execution activity monitoring
- contact_manager: Contact storage and retrieval
- models: Execution-specific data models
- config: Configuration management
"""

__version__ = "1.0.0"

# Initialize email provider and register with channel registry
from .email_provider import EmailProvider
from .phone_provider import PhoneProvider
from .sms_provider import SMSProvider
from .channel import register_channel, ChannelType

# Register email channel (Phase 1: dry-run only)
_email_provider = EmailProvider()
register_channel(ChannelType.EMAIL, _email_provider)

# Register phone channel (Phase 3: dry-run only)
_phone_provider = PhoneProvider()
register_channel(ChannelType.PHONE, _phone_provider)

# Register SMS channel (Phase 3: dry-run only)
_sms_provider = SMSProvider()
register_channel(ChannelType.SMS, _sms_provider)

# Export templates (Phase 2)
from . import templates
