"""
Phase State Manager - Single source of truth for workflow state.

This module wraps StateValidator functionality and provides a clean interface
for state transitions with explicit human approval requirements.
"""

import logging
from typing import Optional, Tuple, List, Dict, Any
from datetime import datetime
from pathlib import Path

from app.models import (
    LegislativeState,
    OrchestratorState,
    WorkflowState,
    ExternalConfirmation,
    DiagnosticRecord,
)
from app.validator import StateValidator, ValidationError
from app.invariants_loader import INVARIANTS
from app.storage import WorkflowStorage

logger = logging.getLogger(__name__)


class PhaseStateManager:
    """Single source of truth for workflow phase/state management."""
    
    def __init__(self, storage: WorkflowStorage):
        """
        Initialize phase state manager.
        
        Args:
            storage: WorkflowStorage instance for persistence
        """
        self.storage = storage
        self.validator = StateValidator()
    
    def get_current_phase(self, workflow_id: str) -> Optional[LegislativeState]:
        """
        Get current legislative phase for workflow.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            Current legislative state, or None if workflow not found
        """
        workflow = self.storage.load_workflow(workflow_id)
        if not workflow:
            return None
        return workflow.legislative_state
    
    def request_transition(
        self,
        workflow_id: str,
        target_state: LegislativeState,
        external_confirmation: Optional[ExternalConfirmation] = None,
        approved_by: Optional[str] = None
    ) -> Tuple[bool, List[str], List[DiagnosticRecord]]:
        """
        Request a state transition with validation.
        
        This is the ONLY way to transition states. All transitions require:
        - Valid sequential transition
        - Required artifacts approved
        - Required review gates approved
        - External confirmation (if required)
        - Human approval (implicit in approved_by parameter)
        
        Args:
            workflow_id: Workflow identifier
            target_state: Target legislative state
            external_confirmation: External event confirmation (if required)
            approved_by: Human identifier who authorized transition
            
        Returns:
            (success, blocking_issues, diagnostics)
        """
        workflow = self.storage.load_workflow(workflow_id)
        if not workflow:
            diag = DiagnosticRecord(
                severity="ERROR",
                error_code="WORKFLOW_NOT_FOUND",
                message=f"Workflow {workflow_id} not found",
                context={"workflow_id": workflow_id, "target_state": target_state.value}
            )
            return False, [f"Workflow {workflow_id} not found"], [diag]
        
        # Validate transition using existing validator
        is_valid, blocking_issues, diagnostics = self.validator.validate_transition(
            workflow=workflow,
            target_state=target_state,
            external_confirmation=external_confirmation
        )
        
        if not is_valid:
            # Log blocking issues
            for issue in blocking_issues:
                logger.warning(f"[PhaseStateManager] Transition blocked: {issue}")
            
            # Add transition attempt to diagnostics
            # Handle both enum and string (from deserialization with use_enum_values=True)
            from_state_value = workflow.legislative_state.value if hasattr(workflow.legislative_state, 'value') else str(workflow.legislative_state)
            diag = DiagnosticRecord(
                severity="ERROR",
                error_code="TRANSITION_BLOCKED",
                message=f"State transition blocked: {workflow.legislative_state} -> {target_state}",
                context={
                    "from_state": from_state_value,
                    "to_state": target_state.value,
                    "blocking_issues": blocking_issues,
                    "approved_by": approved_by
                }
            )
            diagnostics.append(diag)
            
            # Store diagnostics
            self.storage.append_diagnostic(workflow_id, diag)
            
            return False, blocking_issues, diagnostics
        
        # Transition is valid - execute it
        try:
            # Record previous state before updating
            previous_state = workflow.legislative_state
            
            # Update state
            workflow.legislative_state = target_state
            workflow.updated_at = datetime.utcnow()
            
            # Record state history
            # Handle both enum and string (from deserialization with use_enum_values=True)
            from_state_value = previous_state.value if hasattr(previous_state, 'value') else str(previous_state)
            state_entry = {
                "from_state": from_state_value,
                "to_state": target_state.value,
                "transitioned_at": datetime.utcnow().isoformat() + "Z",
                "approved_by": approved_by,
                "external_confirmation": external_confirmation.model_dump() if external_confirmation else None
            }
            workflow.state_history.append(state_entry)
            
            # Store external confirmation if provided
            if external_confirmation:
                workflow.external_confirmations[external_confirmation.event_type] = external_confirmation
            
            # Save workflow
            self.storage.save_workflow(workflow)
            
            logger.info(
                f"[PhaseStateManager] State transition successful: "
                f"{workflow.legislative_state} -> {target_state} "
                f"(approved_by: {approved_by})"
            )
            
            return True, [], diagnostics
            
        except Exception as e:
            logger.error(f"[PhaseStateManager] Failed to execute transition: {e}", exc_info=True)
            
            # Handle both enum and string (from deserialization with use_enum_values=True)
            from_state_value = workflow.legislative_state.value if hasattr(workflow.legislative_state, 'value') else str(workflow.legislative_state)
            diag = DiagnosticRecord(
                severity="ERROR",
                error_code="TRANSITION_EXECUTION_FAILED",
                message=f"State transition validation passed but execution failed: {e}",
                context={
                    "from_state": from_state_value,
                    "to_state": target_state.value,
                    "error": str(e)
                }
            )
            diagnostics.append(diag)
            self.storage.append_diagnostic(workflow_id, diag)
            
            return False, [f"Transition execution failed: {e}"], diagnostics
    
    def block_transition(
        self,
        workflow_id: str,
        reason: str,
        error_code: str = "TRANSITION_BLOCKED",
        context: Optional[Dict[str, Any]] = None
    ) -> DiagnosticRecord:
        """
        Block a state transition with explicit reason.
        
        Args:
            workflow_id: Workflow identifier
            reason: Human-readable reason for blocking
            error_code: Error code for diagnostics
            context: Additional context
            
        Returns:
            DiagnosticRecord created for this block
        """
        workflow = self.storage.load_workflow(workflow_id)
        if workflow:
            workflow.orchestrator_state = OrchestratorState.ORCH_ERROR
        
        diag = DiagnosticRecord(
            severity="ERROR",
            error_code=error_code,
            message=reason,
            context=context or {}
        )
        
        if workflow:
            self.storage.append_diagnostic(workflow_id, diag)
            if workflow:
                workflow.last_error = diag
                self.storage.save_workflow(workflow)
        
        logger.error(f"[PhaseStateManager] Transition blocked: {reason}")
        
        return diag
    
    def is_terminal_state(self, state: LegislativeState) -> bool:
        """
        Check if state is terminal (no exit transitions).
        
        Args:
            state: Legislative state to check
            
        Returns:
            True if terminal, False otherwise
        """
        return INVARIANTS.is_terminal_state(state)
    
    def get_valid_next_state(self, current_state: LegislativeState) -> Optional[LegislativeState]:
        """
        Get valid next state from current state.
        
        Args:
            current_state: Current legislative state
            
        Returns:
            Valid next state, or None if terminal or invalid
        """
        return INVARIANTS.get_valid_next_state(current_state)
