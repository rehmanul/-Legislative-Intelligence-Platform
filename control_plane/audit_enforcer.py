"""
Audit Completeness Enforcer

Enforces decision log completeness before state transitions.
Blocks execution paths if audit requirements are unmet.
"""

import json
import logging
from typing import Optional, Tuple, List, Dict, Any
from datetime import datetime, timezone
from pathlib import Path

from app.models import (
    ReviewGateID,
    WorkflowState,
    DiagnosticRecord,
)

logger = logging.getLogger(__name__)


class AuditEnforcer:
    """Enforces audit completeness requirements."""
    
    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize audit enforcer.
        
        Args:
            base_dir: Base directory (defaults to agent-orchestrator root)
        """
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        
        self.base_dir = Path(base_dir)
        self.review_dir = self.base_dir / "review"
        self.artifacts_dir = self.base_dir / "artifacts"
        self.audit_log_path = self.base_dir / "audit" / "audit-log.jsonl"
    
    def check_decision_log_completeness(
        self,
        artifact_id: str,
        gate_id: Optional[ReviewGateID] = None
    ) -> Tuple[bool, Optional[str], Optional[DiagnosticRecord]]:
        """
        Check if artifact has corresponding decision log entry.
        
        Args:
            artifact_id: Artifact identifier
            gate_id: Optional review gate ID
            
        Returns:
            (is_complete, blocking_reason, diagnostic)
        """
        # Find artifact file
        artifact_file = None
        for agent_dir in self.artifacts_dir.iterdir():
            if not agent_dir.is_dir():
                continue
            for af in agent_dir.glob("*.json"):
                if artifact_id in af.name or artifact_id in str(af):
                    artifact_file = af
                    break
            if artifact_file:
                break
        
        if not artifact_file or not artifact_file.exists():
            reason = f"Artifact {artifact_id} not found"
            diag = DiagnosticRecord(
                severity="ERROR",
                error_code="ARTIFACT_NOT_FOUND",
                message=reason,
                context={"artifact_id": artifact_id}
            )
            return False, reason, diag
        
        # Load artifact
        try:
            artifact_data = json.loads(artifact_file.read_text(encoding="utf-8"))
        except Exception as e:
            reason = f"Failed to load artifact: {e}"
            diag = DiagnosticRecord(
                severity="ERROR",
                error_code="ARTIFACT_LOAD_FAILED",
                message=reason,
                context={"artifact_id": artifact_id, "error": str(e)}
            )
            return False, reason, diag
        
        meta = artifact_data.get("_meta", {})
        approved_at = meta.get("approved_at")
        requires_review = meta.get("requires_review")
        
        # If artifact is not approved, no decision log required yet
        if not approved_at:
            return True, None, None
        
        # If artifact doesn't require review, no decision log needed
        if not requires_review:
            return True, None, None
        
        # Check for decision log entry
        gate_id_str = gate_id.value if gate_id else requires_review
        queue_file = self.review_dir / f"{gate_id_str}_queue.json"
        
        if not queue_file.exists():
            reason = f"Review queue {gate_id_str} not found for approved artifact {artifact_id}"
            diag = DiagnosticRecord(
                severity="ERROR",
                error_code="AUDIT_INCOMPLETE",
                message=reason,
                context={
                    "artifact_id": artifact_id,
                    "gate_id": gate_id_str,
                    "approved_at": approved_at
                }
            )
            logger.warning(f"[AuditEnforcer] {reason}")
            return False, reason, diag
        
        # Load queue and check for decision log
        try:
            queue_data = json.loads(queue_file.read_text(encoding="utf-8"))
            approved_reviews = queue_data.get("approved_reviews", [])
            
            # Check if artifact has decision log entry
            has_decision_log = False
            for review in approved_reviews:
                review_artifact_path = review.get("artifact_path", "")
                review_artifact_id = review.get("artifact_id", "")
                
                if (artifact_id in review_artifact_path or 
                    artifact_id == review_artifact_id or
                    artifact_file.name in review_artifact_path):
                    has_decision_log = True
                    break
            
            if not has_decision_log:
                reason = f"Approved artifact {artifact_id} missing decision log entry in {gate_id_str}"
                diag = DiagnosticRecord(
                    severity="ERROR",
                    error_code="AUDIT_INCOMPLETE",
                    message=reason,
                    context={
                        "artifact_id": artifact_id,
                        "gate_id": gate_id_str,
                        "approved_at": approved_at
                    }
                )
                logger.warning(f"[AuditEnforcer] {reason}")
                return False, reason, diag
            
            return True, None, None
            
        except Exception as e:
            reason = f"Failed to check decision log: {e}"
            diag = DiagnosticRecord(
                severity="ERROR",
                error_code="DECISION_LOG_CHECK_FAILED",
                message=reason,
                context={"artifact_id": artifact_id, "error": str(e)}
            )
            logger.error(f"[AuditEnforcer] {reason}", exc_info=True)
            return False, reason, diag
    
    def validate_state_transition_audit(
        self,
        workflow: WorkflowState,
        target_state: str
    ) -> Tuple[bool, List[str], List[DiagnosticRecord]]:
        """
        Validate that all required artifacts have decision logs before state transition.
        
        Args:
            workflow: Workflow state
            target_state: Target legislative state
            
        Returns:
            (is_valid, blocking_issues, diagnostics)
        """
        blocking_issues = []
        diagnostics = []
        
        # Get required artifacts for current state
        required_artifacts = workflow.artifacts
        
        # Check each artifact that requires review
        for artifact_name, artifact_status in required_artifacts.items():
            if not artifact_status.exists:
                continue
            
            if artifact_status.requires_review:
                artifact_id = artifact_status.artifact_id or artifact_name
                gate_id = ReviewGateID(artifact_status.review_gate) if artifact_status.review_gate else None
                
                is_complete, reason, diag = self.check_decision_log_completeness(
                    artifact_id, gate_id
                )
                
                if not is_complete:
                    blocking_issues.append(reason or f"Missing decision log for {artifact_name}")
                    if diag:
                        diagnostics.append(diag)
        
        is_valid = len(blocking_issues) == 0
        return is_valid, blocking_issues, diagnostics
    
    def halt_on_audit_violation(
        self,
        violation_type: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        workflow_id: Optional[str] = None
    ) -> DiagnosticRecord:
        """
        Halt workflow on audit violation.
        
        Args:
            violation_type: Type of violation
            message: Human-readable violation message
            context: Additional context
            workflow_id: Optional workflow identifier
            
        Returns:
            DiagnosticRecord for the violation
        """
        logger.error(f"[AuditEnforcer] HALT: {violation_type} - {message}")
        
        diag = DiagnosticRecord(
            severity="ERROR",
            error_code=violation_type,
            message=message,
            context=context or {}
        )
        
        # Log to audit log
        audit_event = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "event_type": "audit_violation",
            "violation_type": violation_type,
            "message": message,
            "workflow_id": workflow_id,
            **(context or {})
        }
        
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.audit_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(audit_event) + "\n")
        
        return diag
