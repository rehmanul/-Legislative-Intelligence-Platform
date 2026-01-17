"""
Approval Manager - Pre-Execution Approval System.

GOVERNANCE REFACTOR: HR_* gates apply to LANGUAGE ARTIFACTS, not execution planning.
- Execution agents can create, queue, and simulate execution requests freely
- Approval is checked at actual send time (email_provider checks source artifact approval)
- This manager is retained for backward compatibility but approval happens at artifact level

Note: Execution planning and dry-run simulation do NOT require approval.
Only actual external communication requires approved language artifacts.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from uuid import uuid4

from .models import (
    ExecutionRequest,
    ExecutionApprovalRequest,
    ExecutionStatus,
    ChannelType
)
from .config import REQUIRE_APPROVAL, APPROVAL_QUEUE_FILE

# Import from app.models to use existing ReviewGateID
# Use relative import path
import sys
from pathlib import Path as PathLib
BASE_DIR = PathLib(__file__).parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

try:
    from app.models import ReviewGateID, LegislativeState
except ImportError:
    # Fallback if app.models not available (for testing)
    from enum import Enum
    class ReviewGateID(str, Enum):
        HR_PRE = "HR_PRE"
        HR_LANG = "HR_LANG"
        HR_MSG = "HR_MSG"
        HR_RELEASE = "HR_RELEASE"

logger = logging.getLogger(__name__)


class ApprovalManager:
    """
    Manages execution approvals via review gates.
    
    Integrates with existing HR_LANG, HR_MSG gates.
    Maintains approval queue (JSON-backed for Phase 1).
    """
    
    def __init__(self):
        """Initialize approval manager."""
        self._approval_queue: Dict[str, ExecutionApprovalRequest] = {}
        self._load_queue()
    
    def _load_queue(self) -> None:
        """Load approval queue from file."""
        if APPROVAL_QUEUE_FILE.exists():
            try:
                with open(APPROVAL_QUEUE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data.get("queue", []):
                        approval = ExecutionApprovalRequest(**item)
                        self._approval_queue[approval.execution_id] = approval
                logger.info(f"Loaded {len(self._approval_queue)} approvals from queue")
            except Exception as e:
                logger.error(f"Failed to load approval queue: {e}")
                self._approval_queue = {}
    
    def _save_queue(self) -> None:
        """Save approval queue to file."""
        try:
            APPROVAL_QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "_meta": {
                    "version": "1.0",
                    "updated_at": datetime.utcnow().isoformat(),
                    "count": len(self._approval_queue)
                },
                "queue": [approval.dict() for approval in self._approval_queue.values()]
            }
            with open(APPROVAL_QUEUE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save approval queue: {e}")
    
    def get_review_gate_for_state(self, legislative_state: str) -> Optional[str]:
        """
        Map legislative state to review gate.
        
        Args:
            legislative_state: Legislative state (PRE_EVT, COMM_EVT, etc.)
            
        Returns:
            Review gate ID (HR_LANG, HR_MSG, etc.) or None
        """
        mapping = {
            "COMM_EVT": ReviewGateID.HR_LANG.value,
            "FLOOR_EVT": ReviewGateID.HR_MSG.value,
            # PRE_EVT and INTRO_EVT don't have execution agents
            # FINAL_EVT uses HR_RELEASE (for Phase 2)
        }
        return mapping.get(legislative_state)
    
    def requires_approval(self, request: ExecutionRequest) -> bool:
        """
        Check if execution request requires approval.
        
        Args:
            request: Execution request
            
        Returns:
            True if approval required
        """
        if not REQUIRE_APPROVAL:
            return False
        
        if not request.requires_approval:
            return False
        
        # All execution requires approval in Phase 1
        return True
    
    def submit_for_approval(
        self,
        request: ExecutionRequest,
        legislative_state: str,
        content_preview: Optional[str] = None
    ) -> ExecutionApprovalRequest:
        """
        Submit execution request for approval.
        
        Args:
            request: Execution request
            legislative_state: Current legislative state
            content_preview: Preview of message content
            
        Returns:
            ExecutionApprovalRequest with PENDING status
        """
        # Determine review gate
        review_gate = request.review_gate
        if not review_gate:
            review_gate = self.get_review_gate_for_state(legislative_state)
        
        if not review_gate:
            raise ValueError(
                f"Cannot determine review gate for state {legislative_state}"
            )
        
        # Generate content preview if not provided
        if not content_preview:
            content_preview = self._generate_content_preview(request)
        
        # Create approval request
        approval = ExecutionApprovalRequest(
            execution_id=request.execution_id,
            action_type=request.action_type,
            target=request.target,
            content_preview=content_preview,
            review_gate=review_gate,
            workflow_id=request.workflow_id,
            agent_id=request.agent_id,
            status=ExecutionStatus.PENDING,
            metadata=request.metadata
        )
        
        # Add to queue
        self._approval_queue[approval.execution_id] = approval
        self._save_queue()
        
        logger.info(
            f"Execution request submitted for approval: {approval.execution_id} "
            f"(gate: {review_gate})"
        )
        
        return approval
    
    def _generate_content_preview(self, request: ExecutionRequest) -> str:
        """
        Generate content preview from request.
        
        Args:
            request: Execution request
            
        Returns:
            Content preview string
        """
        if request.action_type == ChannelType.EMAIL:
            content = request.content
            subject = content.get("subject", "(No Subject)")
            body = content.get("body", "")
            preview = f"Subject: {subject}\n\n{body[:200]}"
            if len(body) > 200:
                preview += "..."
            return preview
        else:
            return str(request.content)[:200]
    
    def is_approved(self, execution_id: str) -> bool:
        """
        Check if execution is approved.
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            True if approved
        """
        approval = self._approval_queue.get(execution_id)
        if not approval:
            return False
        
        return approval.status == ExecutionStatus.APPROVED
    
    def approve(
        self,
        execution_id: str,
        approved_by: str
    ) -> ExecutionApprovalRequest:
        """
        Approve an execution request.
        
        Args:
            execution_id: Execution identifier
            approved_by: Human identifier
            
        Returns:
            Updated ExecutionApprovalRequest
            
        Raises:
            ValueError: If execution not found
        """
        approval = self._approval_queue.get(execution_id)
        if not approval:
            raise ValueError(f"Execution approval not found: {execution_id}")
        
        if approval.status == ExecutionStatus.APPROVED:
            logger.warning(f"Execution already approved: {execution_id}")
            return approval
        
        approval.status = ExecutionStatus.APPROVED
        approval.approved_at = datetime.utcnow()
        approval.approved_by = approved_by
        
        self._save_queue()
        
        logger.info(f"Execution approved: {execution_id} by {approved_by}")
        
        return approval
    
    def reject(
        self,
        execution_id: str,
        rejected_by: str,
        reason: Optional[str] = None
    ) -> ExecutionApprovalRequest:
        """
        Reject an execution request.
        
        Args:
            execution_id: Execution identifier
            rejected_by: Human identifier
            reason: Rejection reason
            
        Returns:
            Updated ExecutionApprovalRequest
            
        Raises:
            ValueError: If execution not found
        """
        approval = self._approval_queue.get(execution_id)
        if not approval:
            raise ValueError(f"Execution approval not found: {execution_id}")
        
        approval.status = ExecutionStatus.REJECTED
        approval.rejected_at = datetime.utcnow()
        approval.rejected_by = rejected_by
        approval.rejection_reason = reason
        
        self._save_queue()
        
        logger.info(f"Execution rejected: {execution_id} by {rejected_by}")
        
        return approval
    
    def get_pending_approvals(
        self,
        workflow_id: Optional[str] = None,
        review_gate: Optional[str] = None
    ) -> List[ExecutionApprovalRequest]:
        """
        Get pending approval requests.
        
        Args:
            workflow_id: Filter by workflow (optional)
            review_gate: Filter by review gate (optional)
            
        Returns:
            List of pending ExecutionApprovalRequest
        """
        pending = [
            approval for approval in self._approval_queue.values()
            if approval.status == ExecutionStatus.PENDING
        ]
        
        if workflow_id:
            pending = [a for a in pending if a.workflow_id == workflow_id]
        
        if review_gate:
            pending = [a for a in pending if a.review_gate == review_gate]
        
        return pending
    
    def get_approval(self, execution_id: str) -> Optional[ExecutionApprovalRequest]:
        """
        Get approval request by execution ID.
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            ExecutionApprovalRequest or None
        """
        return self._approval_queue.get(execution_id)
    
    def check_approval_before_execute(
        self,
        execution_id: str
    ) -> tuple[bool, Optional[str]]:
        """
        Check if execution can proceed (approved).
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            Tuple of (can_execute, error_message)
        """
        if not REQUIRE_APPROVAL:
            return (True, None)
        
        approval = self._approval_queue.get(execution_id)
        if not approval:
            return (False, f"Execution approval not found: {execution_id}")
        
        if approval.status != ExecutionStatus.APPROVED:
            return (
                False,
                f"Execution not approved (status: {approval.status.value})"
            )
        
        return (True, None)


# Global approval manager instance
_approval_manager: Optional[ApprovalManager] = None


def get_approval_manager() -> ApprovalManager:
    """
    Get global approval manager instance.
    
    Returns:
        ApprovalManager instance
    """
    global _approval_manager
    if _approval_manager is None:
        _approval_manager = ApprovalManager()
    return _approval_manager
