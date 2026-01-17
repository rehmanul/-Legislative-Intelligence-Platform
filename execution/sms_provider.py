"""
SMS Provider - SMS Integration (Dry-Run Only).

Provides SMS sending capability via SMS API.
In Phase 3, all SMS messages are logged but not sent (dry-run mode).
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from .channel import ExecutionChannel
from .models import (
    ExecutionRequest,
    ExecutionResult,
    ValidationResult,
    ExecutionStatusResponse,
    ChannelType,
    ExecutionStatus
)
from .config import DRY_RUN_MODE, DRY_RUN_LOG_FILE

logger = logging.getLogger(__name__)


class SMSProvider(ExecutionChannel):
    """
    SMS execution channel using SMS API.
    
    In dry-run mode, logs SMS to dry-run-log.jsonl instead of sending.
    """
    
    def __init__(self):
        """Initialize SMS provider."""
        super().__init__(ChannelType.SMS)
        self._execution_status: Dict[str, ExecutionStatusResponse] = {}
    
    def execute(
        self,
        request: ExecutionRequest,
        dry_run: Optional[bool] = None
    ) -> ExecutionResult:
        """
        Execute SMS send (or log in dry-run mode).
        
        Args:
            request: SMS execution request
            dry_run: Override dry-run mode
            
        Returns:
            ExecutionResult with send status
        """
        # Validate request
        validation = self.validate(request)
        if not validation.valid:
            return ExecutionResult(
                execution_id=request.execution_id,
                success=False,
                error="Validation failed",
                error_code="VALIDATION_ERROR",
                dry_run=self._should_execute(request, dry_run),
                metadata={"validation_errors": validation.errors}
            )
        
        # Check if should actually execute
        should_execute = self._should_execute(request, dry_run)
        
        if should_execute:
            logger.warning(f"SMS execution attempted but DRY_RUN_MODE is True.")
            return ExecutionResult(
                execution_id=request.execution_id,
                success=False,
                error="SMS sending disabled in Phase 3 (dry-run mode)",
                error_code="DRY_RUN_MODE",
                dry_run=True,
                metadata={"message": "SMS messages are logged but not sent in dry-run mode"}
            )
        else:
            return self._log_dry_run(request)
    
    def _log_dry_run(self, request: ExecutionRequest) -> ExecutionResult:
        """
        Log SMS to dry-run log file.
        
        Args:
            request: Execution request
            
        Returns:
            ExecutionResult with dry-run status
        """
        try:
            # Extract SMS details
            message = request.content.get("message", "")
            
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "execution_id": request.execution_id,
                "action_type": "SMS",
                "dry_run": True,
                "to": request.target,
                "from": "(Not configured)",
                "message_preview": message[:160] if message else "",
                "message_length": len(message) if message else 0,
                "workflow_id": request.workflow_id,
                "agent_id": request.agent_id,
                "metadata": request.metadata
            }
            
            # Append to dry-run log
            DRY_RUN_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(DRY_RUN_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, default=str) + "\n")
            
            logger.info(f"Dry-run SMS logged: {request.execution_id} -> {request.target}")
            
            return ExecutionResult(
                execution_id=request.execution_id,
                success=True,
                message_id=f"dry-run-{request.execution_id}",
                dry_run=True,
                metadata={"logged_to": str(DRY_RUN_LOG_FILE)}
            )
        except Exception as e:
            logger.error(f"Error logging dry-run SMS: {e}", exc_info=True)
            return ExecutionResult(
                execution_id=request.execution_id,
                success=False,
                error=f"Failed to log dry-run: {str(e)}",
                error_code="LOG_ERROR",
                dry_run=True
            )
    
    def validate(self, request: ExecutionRequest) -> ValidationResult:
        """
        Validate SMS execution request.
        
        Args:
            request: Execution request to validate
            
        Returns:
            ValidationResult
        """
        errors = []
        warnings = []
        
        # Validate target (phone number)
        if not request.target:
            errors.append("Phone number (target) is required")
        elif not self._is_valid_phone_number(request.target):
            errors.append(f"Invalid phone number format: {request.target}")
        
        # Validate content
        if not request.content:
            errors.append("SMS content (message) is required")
        elif "message" not in request.content:
            errors.append("SMS message is required in content.message")
        else:
            message = request.content.get("message", "")
            if len(message) > 1600:  # SMS limit (10 concatenated messages)
                warnings.append(f"SMS message is very long ({len(message)} chars), may be split")
            if len(message) == 0:
                errors.append("SMS message cannot be empty")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _is_valid_phone_number(self, phone: str) -> bool:
        """
        Basic phone number validation.
        
        Args:
            phone: Phone number string
            
        Returns:
            True if valid format
        """
        # Remove common formatting
        cleaned = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace("+", "")
        # Check if it's all digits and reasonable length (10-15 digits)
        return cleaned.isdigit() and 10 <= len(cleaned) <= 15
    
    def get_status(self, execution_id: str) -> ExecutionStatusResponse:
        """
        Get execution status.
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            ExecutionStatusResponse
        """
        status_response = self._execution_status.get(execution_id)
        if not status_response:
            # Return default status
            return ExecutionStatusResponse(
                execution_id=execution_id,
                status=ExecutionStatus.PENDING,
                created_at=datetime.utcnow(),
                executed_at=None,
                result=None,
                approval=None
            )
        return status_response
