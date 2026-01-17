#!/usr/bin/env python3
"""
Script to check and fix workflow status.
Can recover workflows from ORCH_ERROR state.
"""

import sys
import json
import requests
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.storage import WorkflowStorage
from app.models import WorkflowState, OrchestratorState, LegislativeState

API_BASE_URL = "http://localhost:8000/api/v1"
STORAGE_BASE_DIR = Path(__file__).parent.parent / "data"


def check_api_server() -> bool:
    """Check if API server is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def get_workflow_status_api(workflow_id: str) -> Optional[Dict[str, Any]]:
    """Get workflow status via API."""
    try:
        response = requests.get(f"{API_BASE_URL}/workflows/{workflow_id}/status", timeout=5)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            print(f"[ERROR] Workflow {workflow_id} not found")
            return None
        else:
            print(f"[ERROR] Error getting workflow status: {response.status_code}")
            print(response.text)
            return None
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to API server. Is it running?")
        return None
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return None


def recover_workflow_api(workflow_id: str) -> bool:
    """Recover workflow from ORCH_ERROR via API."""
    try:
        response = requests.post(f"{API_BASE_URL}/workflows/{workflow_id}/recover", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"[SUCCESS] Workflow {workflow_id} recovered successfully")
            print(f"   Orchestrator state: {data.get('orchestrator_state')}")
            return True
        elif response.status_code == 400:
            error = response.json()
            print(f"[WARNING] {error.get('detail', {}).get('message', 'Cannot recover workflow')}")
            return False
        else:
            print(f"[ERROR] Error recovering workflow: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False


def get_workflow_status_direct(workflow_id: str) -> Optional[WorkflowState]:
    """Get workflow status directly from storage."""
    try:
        storage = WorkflowStorage(STORAGE_BASE_DIR)
        workflow = storage.load_workflow(workflow_id)
        return workflow
    except Exception as e:
        print(f"[ERROR] Error loading workflow: {e}")
        return None


def recover_workflow_direct(workflow_id: str) -> bool:
    """Recover workflow directly from storage."""
    try:
        storage = WorkflowStorage(STORAGE_BASE_DIR)
        workflow = storage.load_workflow(workflow_id)
        
        if not workflow:
            print(f"[ERROR] Workflow {workflow_id} not found")
            return False
        
        orch_state = workflow.orchestrator_state
        if hasattr(orch_state, 'value'):
            orch_state = orch_state.value
        
        if orch_state != OrchestratorState.ORCH_ERROR.value and orch_state != "ORCH_ERROR":
            print(f"[WARNING] Workflow is not in ORCH_ERROR state (current: {orch_state})")
            return False
        
        # Recover
        workflow.orchestrator_state = OrchestratorState.ORCH_IDLE
        workflow.updated_at = datetime.utcnow()
        storage.save_workflow(workflow)
        
        print(f"[SUCCESS] Workflow {workflow_id} recovered from ORCH_ERROR to ORCH_IDLE")
        return True
    except Exception as e:
        print(f"[ERROR] Error recovering workflow: {e}")
        return False


def list_all_workflows() -> list[str]:
    """List all workflow IDs."""
    try:
        storage = WorkflowStorage(STORAGE_BASE_DIR)
        return storage.list_workflows()
    except Exception as e:
        print(f"[ERROR] Error listing workflows: {e}")
        return []


def main():
    """Main function."""
    import argparse
    from datetime import datetime
    
    parser = argparse.ArgumentParser(description="Check and fix workflow status")
    parser.add_argument("workflow_id", nargs="?", help="Workflow ID to check/fix (or 'list' to list all)")
    parser.add_argument("--recover", action="store_true", help="Recover workflow from ORCH_ERROR state")
    parser.add_argument("--direct", action="store_true", help="Use direct storage access instead of API")
    
    args = parser.parse_args()
    
    # List workflows if requested
    if args.workflow_id == "list" or not args.workflow_id:
        print("[INFO] Listing all workflows...")
        workflows = list_all_workflows()
        if not workflows:
            print("   No workflows found")
        else:
            for wf_id in workflows:
                print(f"   - {wf_id}")
        return
    
    workflow_id = args.workflow_id
    
    # Check if API server is available
    use_api = not args.direct and check_api_server()
    
    if use_api:
        print(f"[INFO] Checking workflow {workflow_id} via API...")
        status = get_workflow_status_api(workflow_id)
        
        if status:
            print(f"\n[STATUS] Workflow Status:")
            print(f"   Legislative State: {status.get('legislative_state')}")
            print(f"   Orchestrator State: {status.get('orchestrator_state')}")
            print(f"   Can Advance: {status.get('can_advance')}")
            
            if status.get('last_error'):
                error = status['last_error']
                print(f"\n[ERROR] Last Error:")
                print(f"   Code: {error.get('error_code')}")
                print(f"   Message: {error.get('message')}")
            
            if status.get('blocking_issues'):
                print(f"\n[BLOCKING] Blocking Issues:")
                for issue in status['blocking_issues']:
                    print(f"   - {issue}")
            
            # Recover if requested
            if args.recover:
                print(f"\n[RECOVER] Recovering workflow...")
                if recover_workflow_api(workflow_id):
                    # Re-check status
                    print(f"\n[INFO] Re-checking status...")
                    status = get_workflow_status_api(workflow_id)
                    if status:
                        print(f"   Orchestrator State: {status.get('orchestrator_state')}")
                else:
                    print("[ERROR] Recovery failed")
            elif status.get('orchestrator_state') == 'ORCH_ERROR':
                print(f"\n[INFO] Workflow is in ORCH_ERROR state. Use --recover to fix it.")
    else:
        print(f"[INFO] Checking workflow {workflow_id} directly from storage...")
        workflow = get_workflow_status_direct(workflow_id)
        
        if workflow:
            print(f"\n[STATUS] Workflow Status:")
            leg_state = workflow.legislative_state
            if hasattr(leg_state, 'value'):
                leg_state = leg_state.value
            orch_state = workflow.orchestrator_state
            if hasattr(orch_state, 'value'):
                orch_state = orch_state.value
            print(f"   Legislative State: {leg_state}")
            print(f"   Orchestrator State: {orch_state}")
            
            if workflow.last_error:
                print(f"\n[ERROR] Last Error:")
                print(f"   Code: {workflow.last_error.error_code}")
                print(f"   Message: {workflow.last_error.message}")
            
            # Recover if requested
            if args.recover:
                print(f"\n[RECOVER] Recovering workflow...")
                if recover_workflow_direct(workflow_id):
                    # Re-check status
                    workflow = get_workflow_status_direct(workflow_id)
                    if workflow:
                        orch_state = workflow.orchestrator_state
                        if hasattr(orch_state, 'value'):
                            orch_state = orch_state.value
                        print(f"   Orchestrator State: {orch_state}")
                else:
                    print("[ERROR] Recovery failed")
            elif orch_state == OrchestratorState.ORCH_ERROR.value or orch_state == "ORCH_ERROR":
                print(f"\n[INFO] Workflow is in ORCH_ERROR state. Use --recover to fix it.")


if __name__ == "__main__":
    main()
