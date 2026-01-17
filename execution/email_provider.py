"""
Email Provider - SMTP Integration (Dry-Run Only).

Provides email sending capability via SMTP.
In Phase 1, all emails are logged but not sent (dry-run mode).
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from email.utils import formataddr, parseaddr

from .channel import ExecutionChannel
from .models import (
    ExecutionRequest,
    ExecutionResult,
    ValidationResult,
    ExecutionStatusResponse,
    ChannelType,
    ExecutionStatus
)
from .config import (
    DRY_RUN_MODE,
    DRY_RUN_LOG_FILE,
    SMTP_SERVER,
    SMTP_PORT,
    SMTP_USERNAME,
    SMTP_PASSWORD,
    SMTP_USE_TLS,
    FROM_EMAIL,
    REPLY_TO_EMAIL
)

logger = logging.getLogger(__name__)


class EmailProvider(ExecutionChannel):
    """
    Email execution channel using SMTP.
    
    In dry-run mode, logs emails to dry-run-log.jsonl instead of sending.
    """
    
    def __init__(self):
        """Initialize email provider."""
        super().__init__(ChannelType.EMAIL)
        self._execution_status: Dict[str, ExecutionStatusResponse] = {}
    
    def execute(
        self,
        request: ExecutionRequest,
        dry_run: Optional[bool] = None
    ) -> ExecutionResult:
        """
        Execute email send (or log in dry-run mode).
        
        Args:
            request: Email execution request
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
            # GOVERNANCE: Check artifact approval before actual external communication
            # Dry-run and planning don't require approval - only actual sends
            approval_check = self._check_artifact_approval(request)
            if not approval_check["approved"]:
                return ExecutionResult(
                    execution_id=request.execution_id,
                    success=False,
                    error=approval_check["error"],
                    error_code="ARTIFACT_NOT_APPROVED",
                    dry_run=False,
                    metadata={
                        "source_artifact": approval_check.get("source_artifact"),
                        "review_gate": approval_check.get("review_gate"),
                        "note": "External communication blocked - source language artifact not approved"
                    }
                )
            
            # Phase 2: Actual SMTP send will be implemented here
            # For Phase 1, this should never be reached (DRY_RUN_MODE = True)
            logger.warning(
                f"Email execution attempted but DRY_RUN_MODE is True. "
                f"Execution ID: {request.execution_id}"
            )
            return ExecutionResult(
                execution_id=request.execution_id,
                success=False,
                error="SMTP sending disabled in Phase 1",
                error_code="PHASE1_RESTRICTION",
                dry_run=True,
                metadata={"note": "Phase 1 does not support live email sending"}
            )
        else:
            # Dry-run: Log to file (no approval needed for simulation)
            return self._log_dry_run(request)
    
    def _log_dry_run(self, request: ExecutionRequest) -> ExecutionResult:
        """
        Log email to dry-run log file.
        
        Args:
            request: Email execution request
            
        Returns:
            ExecutionResult indicating successful dry-run log
        """
        try:
            # Extract email content
            content = request.content
            subject = content.get("subject", "(No Subject)")
            body = content.get("body", "")
            html_body = content.get("html_body")
            
            # Create dry-run log entry
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "execution_id": request.execution_id,
                "action_type": "EMAIL",
                "dry_run": True,
                "to": request.target,
                "from": FROM_EMAIL or "(Not configured)",
                "subject": subject,
                "body_preview": body[:200] + "..." if len(body) > 200 else body,
                "has_html": html_body is not None,
                "workflow_id": request.workflow_id,
                "agent_id": request.agent_id,
                "metadata": request.metadata
            }
            
            # Append to dry-run log
            DRY_RUN_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(DRY_RUN_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
            
            logger.info(
                f"Dry-run email logged: {request.execution_id} "
                f"to {request.target} (subject: {subject})"
            )
            
            # Store status
            self._execution_status[request.execution_id] = ExecutionStatusResponse(
                execution_id=request.execution_id,
                status=ExecutionStatus.EXECUTED,
                created_at=request.created_at,
                executed_at=datetime.utcnow(),
                result=ExecutionResult(
                    execution_id=request.execution_id,
                    success=True,
                    message_id=f"dry-run-{request.execution_id}",
                    dry_run=True,
                    metadata={"logged_to": str(DRY_RUN_LOG_FILE)}
                )
            )
            
            return ExecutionResult(
                execution_id=request.execution_id,
                success=True,
                message_id=f"dry-run-{request.execution_id}",
                dry_run=True,
                metadata={
                    "logged_to": str(DRY_RUN_LOG_FILE),
                    "note": "Email logged in dry-run mode, not sent"
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to log dry-run email: {e}")
            return ExecutionResult(
                execution_id=request.execution_id,
                success=False,
                error=str(e),
                error_code="DRY_RUN_LOG_ERROR",
                dry_run=True
            )
    
    def validate(self, request: ExecutionRequest) -> ValidationResult:
        """
        Validate email execution request.
        
        Args:
            request: Email execution request
            
        Returns:
            ValidationResult with validation status
        """
        errors = []
        warnings = []
        
        # Validate action type
        if request.action_type != ChannelType.EMAIL:
            errors.append(f"Invalid action type: {request.action_type}, expected EMAIL")
        
        # Validate target (email address)
        if not request.target:
            errors.append("Email target (to) is required")
        else:
            # Basic email validation
            name, addr = parseaddr(request.target)
            if not addr or '@' not in addr:
                errors.append(f"Invalid email address format: {request.target}")
        
        # Validate content structure
        if not request.content:
            errors.append("Email content is required")
        else:
            if "subject" not in request.content:
                warnings.append("Email subject not provided")
            if "body" not in request.content and "html_body" not in request.content:
                errors.append("Email body or html_body is required")
        
        # Validate FROM email (warning only in dry-run)
        if not FROM_EMAIL and not DRY_RUN_MODE:
            warnings.append("FROM_EMAIL not configured")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _check_artifact_approval(self, request: ExecutionRequest) -> Dict[str, Any]:
        """
        Check if source language artifact is approved before actual send.
        
        GOVERNANCE: HR_* gates apply to language artifacts, not execution planning.
        This check runs only for actual external communication (not dry-run).
        
        Args:
            request: Execution request
            
        Returns:
            Dictionary with 'approved' (bool), 'error' (str if not approved),
            'source_artifact', 'review_gate'
        """
        source_artifact_path = request.metadata.get("source_artifact")
        
        # If no source artifact specified, allow (planning/simulation)
        if not source_artifact_path:
            return {
                "approved": True,
                "source_artifact": None,
                "review_gate": None
            }
        
        # Check if artifact file exists and is approved
        try:
            from pathlib import Path as PathLib
            BASE_DIR = PathLib(__file__).parent.parent.parent
            
            artifact_path = BASE_DIR / source_artifact_path
            if not artifact_path.exists():
                return {
                    "approved": False,
                    "error": f"Source artifact not found: {source_artifact_path}",
                    "source_artifact": source_artifact_path,
                    "review_gate": None
                }
            
            # Load artifact and check approval status
            artifact_data = json.loads(artifact_path.read_text(encoding="utf-8"))
            meta = artifact_data.get("_meta", {})
            
            # Check if artifact is approved
            status = meta.get("status", "SPECULATIVE")
            requires_review = meta.get("requires_review")
            
            if status == "ACTIONABLE" and (not requires_review or meta.get("human_review_required") == False):
                return {
                    "approved": True,
                    "source_artifact": source_artifact_path,
                    "review_gate": requires_review
                }
            else:
                return {
                    "approved": False,
                    "error": f"Source artifact not approved (status: {status}, review_gate: {requires_review})",
                    "source_artifact": source_artifact_path,
                    "review_gate": requires_review
                }
                
        except Exception as e:
            logger.error(f"Failed to check artifact approval: {e}")
            # Fail open for planning/simulation - strict only for actual sends
            return {
                "approved": True,  # Allow if check fails (planning can proceed)
                "error": None,
                "source_artifact": source_artifact_path,
                "review_gate": None,
                "check_error": str(e)
            }
    
    def get_status(self, execution_id: str) -> ExecutionStatusResponse:
        """
        Get status of email execution.
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            ExecutionStatusResponse with current status
        """
        if execution_id in self._execution_status:
            return self._execution_status[execution_id]
        
        # Return default status if not found
        return ExecutionStatusResponse(
            execution_id=execution_id,
            status=ExecutionStatus.PENDING,
            created_at=datetime.utcnow()
        )
    
    def render_template(
        self,
        template_name: str,
        context: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Render email template (stub for Phase 2).
        
        Args:
            template_name: Name of template
            context: Template context variables
            
        Returns:
            Dictionary with 'subject', 'body', and optionally 'html_body'
            
        Note:
            Phase 2 will implement Jinja2 template rendering.
        """
        # Phase 1: Return context as-is (no template rendering)
        logger.debug(f"Template rendering requested for {template_name} (Phase 1 stub)")
        
        return {
            "subject": context.get("subject", "(No Subject)"),
            "body": context.get("body", ""),
            "html_body": context.get("html_body")
        }
