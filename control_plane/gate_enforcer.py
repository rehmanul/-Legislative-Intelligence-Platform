"""
Gate Enforcer - Centralized gate blocking logic.

This module enforces human review gate requirements and validates role-based approvals.
"""

import json
import logging
from typing import Optional, Tuple, List, Dict, Any
from datetime import datetime
from pathlib import Path

from app.models import (
    ReviewGateID,
    ReviewGateState,
    WorkflowState,
    DiagnosticRecord,
)
from .escalation import EscalationHandler

logger = logging.getLogger(__name__)


# Role requirements for each gate (can be extended from configuration)
GATE_ROLE_REQUIREMENTS: Dict[ReviewGateID, List[str]] = {
    ReviewGateID.HR_PRE: ["Policy Strategist", "Legal Reviewer"],  # Policy direction approval
    ReviewGateID.HR_LANG: ["Legal Reviewer", "Compliance Officer"],  # Legislative language
    ReviewGateID.HR_MSG: ["Communications Director", "Policy Strategist"],  # Messaging
    ReviewGateID.HR_RELEASE: ["Executive Director", "Legal Reviewer"],  # Public release
}


class GateEnforcer:
    """Centralized gate enforcement with role validation."""
    
    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize gate enforcer.
        
        Args:
            base_dir: Base directory for review queues (defaults to agent-orchestrator root)
        """
        if base_dir is None:
            # Default to agent-orchestrator directory
            base_dir = Path(__file__).parent.parent
        
        self.base_dir = Path(base_dir)
        self.review_dir = self.base_dir / "review"
        self.review_dir.mkdir(exist_ok=True)
        self.escalation_handler = EscalationHandler(base_dir=self.base_dir)
    
    def require_gate(
        self,
        gate_id: ReviewGateID,
        artifact_id: str,
        workflow: Optional[WorkflowState] = None
    ) -> Tuple[bool, Optional[str], Optional[DiagnosticRecord]]:
        """
        Require a review gate to be approved before proceeding.
        
        Args:
            gate_id: Review gate identifier
            artifact_id: Artifact identifier requiring review
            workflow: Optional workflow state for context
            
        Returns:
            (is_approved, blocking_reason, diagnostic)
        """
        # Check review queue for approval
        queue_file = self.review_dir / f"{gate_id.value}_queue.json"
        
        if not queue_file.exists():
            reason = f"Review gate {gate_id.value} queue not found"
            diag = DiagnosticRecord(
                severity="ERROR",
                error_code="GATE_QUEUE_NOT_FOUND",
                message=reason,
                context={
                    "gate_id": gate_id.value,
                    "artifact_id": artifact_id
                }
            )
            logger.warning(f"[GateEnforcer] {reason}")
            return False, reason, diag
        
        # Load queue
        try:
            queue_data = json.loads(queue_file.read_text(encoding="utf-8"))
        except Exception as e:
            reason = f"Failed to load review queue: {e}"
            diag = DiagnosticRecord(
                severity="ERROR",
                error_code="GATE_QUEUE_LOAD_FAILED",
                message=reason,
                context={
                    "gate_id": gate_id.value,
                    "artifact_id": artifact_id,
                    "error": str(e)
                }
            )
            logger.error(f"[GateEnforcer] {reason}", exc_info=True)
            return False, reason, diag
        
        # Check approved reviews
        approved_reviews = queue_data.get("approved_reviews", [])
        for review in approved_reviews:
            if review.get("artifact_path", "").endswith(artifact_id) or \
               review.get("artifact_id") == artifact_id or \
               review.get("review_id") == artifact_id:
                if review.get("decision") == "APPROVE" and review.get("status") == "APPROVED":
                    logger.info(
                        f"[GateEnforcer] Gate {gate_id.value} approved for artifact {artifact_id}"
                    )
                    return True, None, None
        
        # Check pending reviews - artifact is in queue but not approved
        pending_reviews = queue_data.get("pending_reviews", [])
        for review in pending_reviews:
            if review.get("artifact_path", "").endswith(artifact_id) or \
               review.get("artifact_id") == artifact_id or \
               review.get("review_id") == artifact_id:
                reason = f"Artifact {artifact_id} pending review at gate {gate_id.value}"
                logger.info(f"[GateEnforcer] {reason}")
                return False, reason, None
        
        # Check workflow review gates if provided
        if workflow:
            gate_status = workflow.review_gates.get(gate_id)
            if gate_status:
                if gate_status.state == ReviewGateState.APPROVED:
                    logger.info(
                        f"[GateEnforcer] Gate {gate_id.value} approved in workflow state"
                    )
                    return True, None, None
                elif gate_status.state == ReviewGateState.PENDING:
                    reason = f"Gate {gate_id.value} is pending approval"
                    return False, reason, None
        
        # Gate not approved
        reason = f"Review gate {gate_id.value} not approved for artifact {artifact_id}"
        logger.warning(f"[GateEnforcer] {reason}")
        return False, reason, None
    
    def validate_human_role(
        self,
        gate_id: ReviewGateID,
        decision_maker: str,
        required_roles: Optional[List[str]] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that decision_maker has required role for gate.
        
        Args:
            gate_id: Review gate identifier
            decision_maker: Human identifier (format: "human:role" or just role name)
            required_roles: Override default required roles (optional)
            
        Returns:
            (is_valid, error_message)
        """
        # Get required roles for gate
        if required_roles is None:
            required_roles = GATE_ROLE_REQUIREMENTS.get(gate_id, [])
        
        if not required_roles:
            # No role requirements - permit (default to permissive)
            logger.debug(f"[GateEnforcer] No role requirements for gate {gate_id.value}")
            return True, None
        
        # Extract role from decision_maker
        # Format can be: "human:Policy Strategist" or "Policy Strategist" or just identifier
        role = None
        if ":" in decision_maker:
            role = decision_maker.split(":", 1)[1].strip()
        else:
            # Try to match by name or use as-is
            role = decision_maker
        
        # Check if role matches required roles
        role_lower = role.lower()
        required_lower = [r.lower() for r in required_roles]
        
        if any(role_lower == req.lower() or role_lower in req.lower() or req.lower() in role_lower
               for req in required_roles):
            logger.info(
                f"[GateEnforcer] Role validation passed: {role} for gate {gate_id.value}"
            )
            return True, None
        
        error_msg = (
            f"Decision maker '{decision_maker}' (role: {role}) does not have required role "
            f"for gate {gate_id.value}. Required roles: {', '.join(required_roles)}"
        )
        logger.warning(f"[GateEnforcer] {error_msg}")
        
        # Escalate role mismatch
        self.escalation_handler.escalate(
            reason=f"Role validation failed: {error_msg}",
            severity="HIGH",
            context={
                "gate_id": gate_id.value,
                "decision_maker": decision_maker,
                "required_roles": required_roles,
                "provided_role": role
            }
        )
        
        return False, error_msg
    
    def halt_on_violation(
        self,
        violation_type: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        workflow_id: Optional[str] = None
    ) -> DiagnosticRecord:
        """
        Halt workflow on gate violation with escalation.
        
        Args:
            violation_type: Type of violation (e.g., "GATE_BYPASS", "ROLE_MISMATCH")
            message: Human-readable violation message
            context: Additional context
            workflow_id: Optional workflow identifier
            
        Returns:
            DiagnosticRecord for the violation
        """
        logger.error(f"[GateEnforcer] HALT: {violation_type} - {message}")
        
        # Create diagnostic
        diag = DiagnosticRecord(
            severity="ERROR",
            error_code=violation_type,
            message=message,
            context=context or {}
        )
        
        # Escalate violation
        self.escalation_handler.escalate(
            reason=f"Gate violation: {message}",
            severity="CRITICAL",
            context={
                "violation_type": violation_type,
                "message": message,
                "workflow_id": workflow_id,
                **(context or {})
            }
        )
        
        return diag
    
    def check_gate_approval_status(
        self,
        gate_id: ReviewGateID,
        workflow: Optional[WorkflowState] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if a gate is approved (for any artifact).
        
        Args:
            gate_id: Review gate identifier
            workflow: Optional workflow state for context
            
        Returns:
            (is_approved, status_message)
        """
        # Check workflow review gates first
        if workflow:
            gate_status = workflow.review_gates.get(gate_id)
            if gate_status:
                if gate_status.state == ReviewGateState.APPROVED:
                    return True, f"Gate {gate_id.value} approved"
                elif gate_status.state == ReviewGateState.PENDING:
                    return False, f"Gate {gate_id.value} pending approval"
                elif gate_status.state == ReviewGateState.REJECTED:
                    return False, f"Gate {gate_id.value} rejected"
        
        # Check review queue
        queue_file = self.review_dir / f"{gate_id.value}_queue.json"
        if queue_file.exists():
            try:
                queue_data = json.loads(queue_file.read_text(encoding="utf-8"))
                approved_count = len(queue_data.get("approved_reviews", []))
                pending_count = len(queue_data.get("pending_reviews", []))
                
                if approved_count > 0:
                    return True, f"Gate {gate_id.value} has {approved_count} approved review(s)"
                elif pending_count > 0:
                    return False, f"Gate {gate_id.value} has {pending_count} pending review(s)"
            except Exception as e:
                logger.warning(f"[GateEnforcer] Failed to check queue: {e}")
        
        return False, f"Gate {gate_id.value} not approved"
