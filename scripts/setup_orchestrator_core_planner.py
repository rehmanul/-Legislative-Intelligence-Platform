#!/usr/bin/env python3
"""
Setup and fix orchestrator_core_planner workflow.
Creates it if it doesn't exist, or recovers it if it's in error state.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.storage import WorkflowStorage
from app.models import WorkflowState, OrchestratorState, LegislativeState

WORKFLOW_ID = "orchestrator_core_planner"
STORAGE_BASE_DIR = Path(__file__).parent.parent / "data"


def setup_workflow():
    """Setup or recover the orchestrator_core_planner workflow."""
    storage = WorkflowStorage(STORAGE_BASE_DIR)
    
    # Check if workflow exists
    workflow = storage.load_workflow(WORKFLOW_ID)
    
    if workflow:
        print(f"[INFO] Workflow {WORKFLOW_ID} exists")
        leg_state = workflow.legislative_state
        if hasattr(leg_state, 'value'):
            leg_state = leg_state.value
        orch_state = workflow.orchestrator_state
        if hasattr(orch_state, 'value'):
            orch_state = orch_state.value
        print(f"   Legislative State: {leg_state}")
        print(f"   Orchestrator State: {orch_state}")
        
        # Check if it's in error state (handle both enum and string)
        orch_state = workflow.orchestrator_state
        if hasattr(orch_state, 'value'):
            orch_state = orch_state.value
        
        if orch_state == OrchestratorState.ORCH_ERROR.value or orch_state == "ORCH_ERROR":
            print(f"\n[RECOVER] Workflow is in ORCH_ERROR state. Recovering...")
            workflow.orchestrator_state = OrchestratorState.ORCH_IDLE
            workflow.updated_at = datetime.utcnow()
            
            # Add diagnostic record
            from app.models import DiagnosticRecord
            diag = DiagnosticRecord(
                severity="INFO",
                error_code="WORKFLOW_RECOVERED",
                message="Workflow recovered from ORCH_ERROR to ORCH_IDLE",
                correlation_id=str(uuid4())
            )
            workflow.diagnostics.append(diag)
            storage.append_diagnostic(WORKFLOW_ID, diag)
            
            storage.save_workflow(workflow)
            print(f"[SUCCESS] Workflow recovered to ORCH_IDLE")
        else:
            print(f"[INFO] Workflow is already in {orch_state} state")
    else:
        print(f"[INFO] Workflow {WORKFLOW_ID} does not exist. Creating...")
        
        # Create new workflow starting in PRE_EVT
        workflow = WorkflowState(
            workflow_id=WORKFLOW_ID,
            legislative_state=LegislativeState.PRE_EVT,
            orchestrator_state=OrchestratorState.ORCH_IDLE,
            metadata={
                "description": "Core planner orchestrator workflow",
                "created_by": "setup_script"
            }
        )
        
        # Initialize state history
        workflow.state_history.append({
            "state": LegislativeState.PRE_EVT.value,
            "entered_at": workflow.created_at.isoformat() + "Z",
            "entered_by": "system",
            "reason": "Workflow created by setup script"
        })
        
        storage.save_workflow(workflow)
        print(f"[SUCCESS] Workflow created successfully")
        print(f"   Legislative State: {workflow.legislative_state.value}")
        print(f"   Orchestrator State: {workflow.orchestrator_state.value}")
    
    # Final status
    workflow = storage.load_workflow(WORKFLOW_ID)
    if workflow:
        print(f"\n[FINAL STATUS]")
        print(f"   Workflow ID: {workflow.workflow_id}")
        
        # Handle enum serialization (may be string or enum)
        leg_state = workflow.legislative_state
        if hasattr(leg_state, 'value'):
            leg_state = leg_state.value
        print(f"   Legislative State: {leg_state}")
        
        orch_state = workflow.orchestrator_state
        if hasattr(orch_state, 'value'):
            orch_state = orch_state.value
        print(f"   Orchestrator State: {orch_state}")
        
        print(f"   Created: {workflow.created_at}")
        print(f"   Updated: {workflow.updated_at}")
        
        if workflow.last_error:
            print(f"\n[LAST ERROR]")
            print(f"   Code: {workflow.last_error.error_code}")
            print(f"   Message: {workflow.last_error.message}")
        
        return True
    else:
        print(f"[ERROR] Failed to verify workflow creation")
        return False


if __name__ == "__main__":
    try:
        success = setup_workflow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"[ERROR] Failed to setup workflow: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
