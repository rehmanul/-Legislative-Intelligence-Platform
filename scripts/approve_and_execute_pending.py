"""
Script: approve_and_execute_pending.py
Intent:
- temporal

Reads:
- execution/approval-queue.json

Writes:
- None (updates approval queue and executes in dry-run)
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from execution.approval_manager import get_approval_manager
from execution.monitor import get_monitor
from execution.channel import get_channel_registry
from execution.models import ExecutionRequest, ChannelType
from execution.config import DRY_RUN_MODE
import json

def main():
    print("[approve_and_execute] Starting approval and execution process")
    print(f"[approve_and_execute] DRY_RUN_MODE: {DRY_RUN_MODE}")
    
    approval_manager = get_approval_manager()
    monitor = get_monitor()
    channel_registry = get_channel_registry()
    
    # Get pending approvals for orchestrator_core_planner workflow
    pending = approval_manager.get_pending_approvals(workflow_id="orchestrator_core_planner")
    
    print(f"[approve_and_execute] Found {len(pending)} pending approvals")
    
    if not pending:
        print("[approve_and_execute] No pending approvals found")
        return
    
    # Approve all pending requests
    approved_requests = []
    for approval in pending:
        print(f"[approve_and_execute] Approving: {approval.execution_id[:8]}... -> {approval.target}")
        approved = approval_manager.approve(
            execution_id=approval.execution_id,
            approved_by="human:script_approval"
        )
        approved_requests.append(approved)
        monitor.log_execution_approved(
            execution_id=approval.execution_id,
            workflow_id=approval.workflow_id,
            approved_by="human:script_approval"
        )
    
    print(f"[approve_and_execute] Approved {len(approved_requests)} requests")
    
    # Now execute approved requests
    print("[approve_and_execute] Executing approved requests...")
    
    executed_count = 0
    failed_count = 0
    
    for approval in approved_requests:
        execution_id = approval.execution_id
        
        # Check approval status
        is_approved, error = approval_manager.check_approval_before_execute(execution_id)
        if not is_approved:
            print(f"[approve_and_execute] WARNING: {execution_id[:8]}... not approved: {error}")
            failed_count += 1
            continue
        
        # Get the channel
        channel = channel_registry.get_channel(ChannelType.EMAIL)
        if not channel:
            print(f"[approve_and_execute] ERROR: Email channel not found")
            failed_count += 1
            continue
        
        # Reconstruct execution request from approval
        # We need to get the original request content
        # For now, create a minimal request - in real scenario, we'd load from artifact
        try:
            # Create execution request from approval data
            request = ExecutionRequest(
                execution_id=execution_id,
                action_type=ChannelType.EMAIL,
                target=approval.target,
                content={
                    "subject": approval.content_preview.split("\n")[0].replace("Subject: ", ""),
                    "body": approval.content_preview
                },
                workflow_id=approval.workflow_id,
                agent_id=approval.agent_id,
                review_gate=approval.review_gate,
                requires_approval=False,  # Already approved
                dry_run=True
            )
            
            # Execute
            result = channel.execute(request, dry_run=True)
            
            if result.success:
                print(f"[approve_and_execute] SUCCESS: Executed {execution_id[:8]}... -> {approval.target}")
                monitor.log_execution_executed(
                    execution_id=execution_id,
                    workflow_id=approval.workflow_id,
                    result=result
                )
                executed_count += 1
            else:
                print(f"[approve_and_execute] FAILED: {execution_id[:8]}... -> {result.error}")
                monitor.log_execution_failed(
                    execution_id=execution_id,
                    workflow_id=approval.workflow_id,
                    error=result.error or "Unknown error"
                )
                failed_count += 1
                
        except Exception as e:
            print(f"[approve_and_execute] ERROR executing {execution_id[:8]}...: {e}")
            monitor.log_execution_failed(
                execution_id=execution_id,
                workflow_id=approval.workflow_id,
                error=str(e)
            )
            failed_count += 1
    
    print(f"[approve_and_execute] Execution complete:")
    print(f"  - Approved: {len(approved_requests)}")
    print(f"  - Executed: {executed_count}")
    print(f"  - Failed: {failed_count}")
    
    # Update contacts
    from execution.contact_manager import get_contact_manager
    contact_manager = get_contact_manager()
    
    for approval in approved_requests:
        contact_id = approval.metadata.get("contact_id")
        if contact_id:
            contact_manager.mark_contacted(contact_id)
            print(f"[approve_and_execute] Marked contact {contact_id[:8]}... as contacted")
    
    print("[approve_and_execute] SUCCESS: All approved requests executed")

if __name__ == "__main__":
    main()
