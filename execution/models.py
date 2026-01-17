"""
Execution-specific data models.

Defines models for execution requests, results, approvals, and activity tracking.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, EmailStr, validator


class ChannelType(str, Enum):
    """Execution channel types."""
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    SMS = "SMS"
    SOCIAL_MEDIA = "SOCIAL_MEDIA"
    DOCUMENT_SUBMISSION = "DOCUMENT_SUBMISSION"


class ExecutionStatus(str, Enum):
    """Status of an execution action."""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"
    TERMINATED = "TERMINATED"


class ExecutionAction(BaseModel):
    """Base model for execution actions."""
    action_id: str = Field(default_factory=lambda: str(uuid4()))
    action_type: ChannelType
    workflow_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExecutionRequest(BaseModel):
    """Request to execute an action."""
    execution_id: str = Field(default_factory=lambda: str(uuid4()))
    action_type: ChannelType
    target: str  # Email address, phone number, etc.
    content: Dict[str, Any]  # Channel-specific content
    workflow_id: str
    agent_id: Optional[str] = None
    review_gate: Optional[str] = None  # HR_LANG, HR_MSG, etc.
    requires_approval: bool = True
    dry_run: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator('target')
    def validate_target(cls, v, values):
        """Validate target based on action type."""
        action_type = values.get('action_type')
        if action_type == ChannelType.EMAIL:
            # Basic email validation (full validation in email_provider)
            if '@' not in v:
                raise ValueError(f"Invalid email address: {v}")
        return v


class ExecutionResult(BaseModel):
    """Result of an execution action."""
    execution_id: str
    success: bool
    message_id: Optional[str] = None  # Email message ID, etc.
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    error: Optional[str] = None
    error_code: Optional[str] = None
    dry_run: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExecutionApprovalRequest(BaseModel):
    """Request for execution approval."""
    execution_id: str
    action_type: ChannelType
    target: str
    content_preview: str  # Preview of message content
    review_gate: str  # HR_LANG, HR_MSG, etc.
    workflow_id: str
    agent_id: Optional[str] = None
    status: ExecutionStatus = ExecutionStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    rejected_at: Optional[datetime] = None
    rejected_by: Optional[str] = None
    rejection_reason: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExecutionActivity(BaseModel):
    """Activity log entry for execution."""
    activity_id: str = Field(default_factory=lambda: str(uuid4()))
    execution_id: str
    event_type: str  # execution_requested, execution_approved, execution_executed, etc.
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    workflow_id: str
    agent_id: Optional[str] = None
    status: ExecutionStatus
    message: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ValidationResult(BaseModel):
    """Result of execution request validation."""
    valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class ExecutionStatusResponse(BaseModel):
    """Status response for execution query."""
    execution_id: str
    status: ExecutionStatus
    created_at: datetime
    executed_at: Optional[datetime] = None
    result: Optional[ExecutionResult] = None
    approval: Optional[ExecutionApprovalRequest] = None
