"""
Script: api__execute__agent.py
Intent: snapshot
Purpose: Execute agents via the FastAPI orchestrator API

This script demonstrates Method 3 - API-based agent execution.
It checks backend health, gets/creates workflows, and executes agents via HTTP API.

Usage:
    python scripts/api__execute__agent.py --agent-id intel_signal_scan_pre_evt
    python scripts/api__execute__agent.py --batch --state PRE_EVT --type Intelligence
    python scripts/api__execute__agent.py --list-agents
"""

import json
import sys
import argparse
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

# Add parent directory to path for imports
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

try:
    import requests
except ImportError:
    print("[ERROR] requests library not installed")
    print("[INFO] Install with: pip install requests")
    sys.exit(1)

# API Configuration
DEFAULT_API_BASE_URL = "http://localhost:8000"
API_BASE_URL = None  # Will be set from environment or registry

# Paths
REGISTRY_PATH = BASE_DIR.parent / "infrastructure" / "ports.registry.json"
STATE_PATH = BASE_DIR / "state" / "legislative-state.json"


def get_api_base_url() -> str:
    """Get API base URL from registry or environment."""
    global API_BASE_URL
    
    if API_BASE_URL:
        return API_BASE_URL
    
    # Try to get from port registry
    try:
        if REGISTRY_PATH.exists():
            with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
                registry = json.load(f)
            
            for system in registry.get("systems", []):
                if system.get("system_name") == "agent-orchestrator":
                    for service in system.get("services", []):
                        if service.get("service_name") == "backend":
                            port = service.get("port", 8000)
                            API_BASE_URL = f"http://localhost:{port}"
                            return API_BASE_URL
    except Exception as e:
        print(f"[WARN] Could not read port registry: {e}")
    
    # Fallback to default
    API_BASE_URL = DEFAULT_API_BASE_URL
    return API_BASE_URL


def check_backend_health(base_url: str) -> bool:
    """Check if backend is running and healthy."""
    try:
        response = requests.get(f"{base_url}/api/v1/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Backend is healthy")
            print(f"   Status: {health.get('status')}")
            print(f"   Active workflows: {health.get('active_workflows', 0)}")
            print(f"   Version: {health.get('version')}")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to backend at {base_url}")
        print(f"   Make sure the orchestrator is running:")
        print(f"   python agent-orchestrator/start_orchestrator.py")
        return False
    except Exception as e:
        print(f"❌ Error checking backend health: {e}")
        return False


def get_workflow_id(base_url: str, create_if_missing: bool = True) -> Optional[str]:
    """Get workflow ID from state file or create new one."""
    # Try to get from state file
    if STATE_PATH.exists():
        try:
            with open(STATE_PATH, 'r', encoding='utf-8') as f:
                state = json.load(f)
            workflow_id = state.get("_meta", {}).get("workflow_id")
            if workflow_id:
                print(f"📋 Found workflow ID: {workflow_id}")
                return workflow_id
        except Exception as e:
            print(f"[WARN] Could not read state file: {e}")
    
    # Try to list workflows from API
    try:
        # Note: This endpoint may not exist, so we'll create if needed
        if create_if_missing:
            return create_workflow(base_url)
    except Exception:
        pass
    
    # Create new workflow if allowed
    if create_if_missing:
        return create_workflow(base_url)
    
    return None


def create_workflow(base_url: str, initial_state: str = "PRE_EVT") -> str:
    """Create a new workflow via API."""
    print(f"🆕 Creating new workflow in state: {initial_state}")
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/workflows",
            json={
                "initial_state": initial_state,
                "metadata": {
                    "description": "Created via API execution script",
                    "created_by": "api__execute__agent.py",
                    "created_at": datetime.utcnow().isoformat() + "Z"
                }
            },
            timeout=10
        )
        
        if response.status_code == 201:
            workflow = response.json()
            workflow_id = workflow["workflow_id"]
            print(f"✅ Created workflow: {workflow_id}")
            return workflow_id
        else:
            print(f"❌ Failed to create workflow: {response.status_code}")
            print(f"   Response: {response.text}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error creating workflow: {e}")
        sys.exit(1)


def get_execution_status(base_url: str, workflow_id: str, agent_id: str) -> Optional[Dict[str, Any]]:
    """Get execution status for an agent."""
    try:
        # First try to get from agent status endpoint
        response = requests.get(
            f"{base_url}/api/v1/workflows/{workflow_id}/agents/{agent_id}/status",
            timeout=5
        )
        
        if response.status_code == 200:
            return response.json()
        
        # Fallback: Try workflow status endpoint
        response = requests.get(
            f"{base_url}/api/v1/workflows/{workflow_id}/status",
            timeout=5
        )
        
        if response.status_code == 200:
            status = response.json()
            # Extract agent-specific status if available
            agents = status.get("agents", {})
            if agent_id in agents:
                return agents[agent_id]
        
        return None
    except Exception:
        return None


def poll_execution_status(
    base_url: str,
    workflow_id: str,
    agent_id: str,
    max_wait: int = 300,
    poll_interval: int = 2
) -> Dict[str, Any]:
    """Poll execution status until completion or timeout."""
    print(f"⏳ Waiting for agent completion (max {max_wait}s, polling every {poll_interval}s)...")
    
    start_time = time.time()
    last_status = None
    
    while (time.time() - start_time) < max_wait:
        status = get_execution_status(base_url, workflow_id, agent_id)
        
        if status:
            current_status = status.get("status", "UNKNOWN")
            
            # Show status change
            if current_status != last_status:
                print(f"   Status: {current_status}")
                last_status = current_status
            
            # Check if completed
            if current_status in ["COMPLETED", "SUCCESS", "FAILED", "TERMINATED"]:
                if status.get("error"):
                    print(f"   Error: {status.get('error')}")
                if status.get("output_file"):
                    print(f"   Output: {status.get('output_file')}")
                if status.get("execution_time"):
                    print(f"   Execution time: {status.get('execution_time'):.2f}s")
                return status
        
        time.sleep(poll_interval)
        elapsed = int(time.time() - start_time)
        if elapsed % 10 == 0:  # Print every 10 seconds
            print(f"   Still waiting... ({elapsed}s elapsed)")
    
    print(f"⏰ Timeout after {max_wait}s - agent may still be running")
    return {"status": "TIMEOUT", "message": f"Polling timeout after {max_wait}s"}


def verify_agent_output(agent_id: str) -> Dict[str, Any]:
    """Verify agent output files exist."""
    artifacts_dir = BASE_DIR / "artifacts" / agent_id
    
    if not artifacts_dir.exists():
        return {
            "verified": False,
            "message": f"Artifacts directory not found: {artifacts_dir}",
            "files": []
        }
    
    # Find JSON output files
    output_files = list(artifacts_dir.glob("*.json"))
    
    if not output_files:
        return {
            "verified": False,
            "message": f"No JSON output files found in {artifacts_dir}",
            "files": []
        }
    
    verified_files = []
    for output_file in output_files:
        try:
            # Try to parse JSON to verify it's valid
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Check for _meta block
            has_meta = "_meta" in data
            artifact_type = data.get("_meta", {}).get("artifact_type", "UNKNOWN")
            
            verified_files.append({
                "path": str(output_file.relative_to(BASE_DIR)),
                "size": output_file.stat().st_size,
                "has_meta": has_meta,
                "artifact_type": artifact_type
            })
        except json.JSONDecodeError:
            verified_files.append({
                "path": str(output_file.relative_to(BASE_DIR)),
                "size": output_file.stat().st_size,
                "valid_json": False
            })
    
    return {
        "verified": len(verified_files) > 0,
        "message": f"Found {len(verified_files)} output file(s)",
        "files": verified_files
    }


def execute_agent(
    base_url: str,
    workflow_id: str,
    agent_id: str,
    agent_type: str,
    scope: str,
    risk_level: str = "LOW",
    wait_for_completion: bool = False,
    verify_output: bool = False,
    max_wait: int = 300
) -> Dict[str, Any]:
    """Execute a single agent via API."""
    print(f"\n🚀 Executing agent: {agent_id}")
    print(f"   Type: {agent_type}")
    print(f"   Scope: {scope}")
    print(f"   Risk Level: {risk_level}")
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/workflows/{workflow_id}/agents/execute",
            json={
                "agent_id": agent_id,
                "agent_type": agent_type,
                "scope": scope,
                "risk_level": risk_level,
                "metadata": {
                    "executed_via": "api__execute__agent.py",
                    "executed_at": datetime.utcnow().isoformat() + "Z"
                }
            },
            timeout=30
        )
        
        if response.status_code == 202:  # Accepted
            result = response.json()
            print(f"✅ Agent queued for execution")
            print(f"   Status: {result.get('status')}")
            print(f"   Agent ID: {result.get('agent_id')}")
            
            # Wait for completion if requested
            output_verification = None
            if wait_for_completion:
                print()
                final_status = poll_execution_status(base_url, workflow_id, agent_id, max_wait=max_wait)
                result.update(final_status)
                
                # Verify output if requested
                if verify_output:
                    print()
                    print("🔍 Verifying output files...")
                    output_verification = verify_agent_output(agent_id)
                    if output_verification["verified"]:
                        print(f"✅ {output_verification['message']}")
                        for file_info in output_verification["files"]:
                            print(f"   • {file_info['path']} ({file_info.get('size', 0)} bytes)")
                            if file_info.get("has_meta"):
                                print(f"     Artifact Type: {file_info.get('artifact_type')}")
                    else:
                        print(f"⚠️  {output_verification['message']}")
                    result["output_verification"] = output_verification
            
            return result
        else:
            error_data = response.json() if response.content else {}
            error_detail = error_data.get("detail", {})
            
            # Enhanced error message
            if isinstance(error_detail, dict):
                error_code = error_detail.get("error_code", "UNKNOWN_ERROR")
                error_msg = error_detail.get("message", response.text)
                correlation_id = error_detail.get("correlation_id")
                
                suggestions = []
                if "WORKFLOW_NOT_FOUND" in error_code:
                    suggestions.append("   → Verify workflow ID or create a new workflow")
                elif "AGENT_NOT_FOUND" in error_code:
                    suggestions.append(f"   → Check agent_id '{agent_id}' exists in registry")
                elif "EXECUTOR_NOT_AVAILABLE" in error_code:
                    suggestions.append("   → Check backend executor service is running")
                elif response.status_code == 404:
                    suggestions.append(f"   → Verify endpoint exists: POST /api/v1/workflows/{{id}}/agents/execute")
                elif response.status_code == 500:
                    suggestions.append("   → Check backend logs for detailed error information")
                    if correlation_id:
                        suggestions.append(f"   → Correlation ID: {correlation_id}")
                
                print(f"❌ Failed to execute agent: {response.status_code}")
                print(f"   Error Code: {error_code}")
                print(f"   Message: {error_msg}")
                if suggestions:
                    print("   Suggestions:")
                    for suggestion in suggestions:
                        print(suggestion)
                
                return {"success": False, "error": error_msg, "error_code": error_code}
            else:
                error_msg = str(error_detail) if error_detail else response.text
                print(f"❌ Failed to execute agent: {response.status_code}")
                print(f"   Error: {error_msg}")
                return {"success": False, "error": error_msg}
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to backend")
        print(f"   → Verify backend is running: python agent-orchestrator/start_orchestrator.py")
        print(f"   → Check API URL: {base_url}")
        return {"success": False, "error": "Connection error"}
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out (agent may still be executing)")
        print(f"   → Check backend is responsive")
        print(f"   → Agent execution may continue in background")
        return {"success": False, "error": "Request timeout"}
    except Exception as e:
        print(f"❌ Error executing agent: {e}")
        print(f"   → Check network connectivity")
        print(f"   → Verify API endpoint is correct")
        return {"success": False, "error": str(e)}


def list_agents(base_url: str, workflow_id: str) -> List[Dict[str, Any]]:
    """List all agents for a workflow."""
    try:
        response = requests.get(
            f"{base_url}/api/v1/workflows/{workflow_id}/agents",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            agents = data.get("agents", [])
            print(f"\n📋 Found {len(agents)} agents:")
            for agent in agents:
                status = agent.get("status", "UNKNOWN")
                agent_id = agent.get("agent_id", "unknown")
                agent_type = agent.get("agent_type", "Unknown")
                print(f"   • {agent_id} ({agent_type}) - {status}")
            return agents
        else:
            print(f"❌ Failed to list agents: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error listing agents: {e}")
        return []


def get_agents_for_state(state: str, agent_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get agents from registry filtered by state and type."""
    registry_path = BASE_DIR / "registry" / "agent-registry.json"
    
    if not registry_path.exists():
        print(f"[WARN] Registry not found at {registry_path}")
        return []
    
    try:
        with open(registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        agents = registry.get("agents", [])
        filtered = []
        
        for agent in agents:
            agent_id = agent.get("agent_id", "")
            agent_type_val = agent.get("agent_type", "")
            
            # Filter by state (agent_id contains state)
            if state and state not in agent_id:
                continue
            
            # Filter by type
            if agent_type and agent_type_val != agent_type:
                continue
            
            filtered.append({
                "agent_id": agent_id,
                "agent_type": agent_type_val,
                "scope": agent.get("scope", ""),
                "risk_level": agent.get("risk_level", "LOW"),
                "status": agent.get("status", "UNKNOWN")
            })
        
        return filtered
    except Exception as e:
        print(f"[WARN] Error reading registry: {e}")
        return []


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description="Execute agents via FastAPI orchestrator API (Method 3)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Execute a single agent (queued, returns immediately)
  python scripts/api__execute__agent.py --agent-id intel_signal_scan_pre_evt
  
  # Execute and wait for completion
  python scripts/api__execute__agent.py --agent-id intel_signal_scan_pre_evt --wait
  
  # Execute, wait, and verify output files
  python scripts/api__execute__agent.py --agent-id intel_signal_scan_pre_evt --wait --verify-output
  
  # Execute all Intelligence agents for PRE_EVT (batch)
  python scripts/api__execute__agent.py --batch --state PRE_EVT --type Intelligence
  
  # Batch execution with waiting and verification
  python scripts/api__execute__agent.py --batch --state PRE_EVT --type Intelligence --wait --verify-output
  
  # List all agents
  python scripts/api__execute__agent.py --list-agents
  
  # Execute with custom API URL
  python scripts/api__execute__agent.py --agent-id intel_signal_scan_pre_evt --api-url http://localhost:8001
  
  # Show workflow status after execution
  python scripts/api__execute__agent.py --agent-id intel_signal_scan_pre_evt --workflow-status
        """
    )
    
    parser.add_argument(
        "--agent-id",
        type=str,
        help="Agent ID to execute (e.g., intel_signal_scan_pre_evt)"
    )
    parser.add_argument(
        "--agent-type",
        type=str,
        help="Agent type (Intelligence, Drafting, Execution, Learning)"
    )
    parser.add_argument(
        "--scope",
        type=str,
        help="Agent scope description"
    )
    parser.add_argument(
        "--risk-level",
        type=str,
        default="LOW",
        choices=["LOW", "MEDIUM", "HIGH"],
        help="Risk level (default: LOW)"
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Execute multiple agents (use with --state and --type)"
    )
    parser.add_argument(
        "--state",
        type=str,
        help="Legislative state to filter agents (PRE_EVT, INTRO_EVT, etc.)"
    )
    parser.add_argument(
        "--type",
        type=str,
        choices=["Intelligence", "Drafting", "Execution", "Learning"],
        help="Agent type to filter for batch execution"
    )
    parser.add_argument(
        "--list-agents",
        action="store_true",
        help="List all agents for current workflow"
    )
    parser.add_argument(
        "--api-url",
        type=str,
        help="API base URL (default: from port registry or http://localhost:8000)"
    )
    parser.add_argument(
        "--workflow-id",
        type=str,
        help="Workflow ID (default: from state file or create new)"
    )
    parser.add_argument(
        "--wait",
        action="store_true",
        help="Wait for agent execution to complete (polls status)"
    )
    parser.add_argument(
        "--max-wait",
        type=int,
        default=300,
        help="Maximum seconds to wait for completion (default: 300)"
    )
    parser.add_argument(
        "--verify-output",
        action="store_true",
        help="Verify agent output files exist after execution (requires --wait)"
    )
    parser.add_argument(
        "--workflow-status",
        action="store_true",
        help="Show workflow status after execution"
    )
    
    args = parser.parse_args()
    
    # Get API URL
    if args.api_url:
        global API_BASE_URL
        API_BASE_URL = args.api_url
    
    base_url = get_api_base_url()
    print("=" * 80)
    print("AGENT EXECUTION VIA API (Method 3)")
    print("=" * 80)
    print(f"API Base URL: {base_url}")
    print()
    
    # Check backend health
    print("[1/4] Checking backend health...")
    if not check_backend_health(base_url):
        print("\n❌ Backend is not available. Please start it first:")
        print(f"   python agent-orchestrator/start_orchestrator.py")
        sys.exit(1)
    print()
    
    # Get workflow ID
    print("[2/4] Getting workflow ID...")
    workflow_id = args.workflow_id or get_workflow_id(base_url, create_if_missing=True)
    if not workflow_id:
        print("❌ Could not determine workflow ID")
        sys.exit(1)
    print()
    
    # List agents if requested
    if args.list_agents:
        print("[3/4] Listing agents...")
        list_agents(base_url, workflow_id)
        print()
        return 0
    
    # Execute agents
    print("[3/4] Executing agents...")
    
    if args.batch:
        # Batch execution
        if not args.state:
            print("❌ --state required for batch execution")
            sys.exit(1)
        
        agents = get_agents_for_state(args.state, args.type)
        
        if not agents:
            print(f"❌ No agents found for state={args.state}, type={args.type}")
            sys.exit(1)
        
        print(f"Found {len(agents)} agents to execute:")
        for agent in agents:
            print(f"   • {agent['agent_id']}")
        print()
        
        results = []
        for i, agent in enumerate(agents, 1):
            print(f"\n[{i}/{len(agents)}]")
            result = execute_agent(
                base_url=base_url,
                workflow_id=workflow_id,
                agent_id=agent["agent_id"],
                agent_type=agent["agent_type"],
                scope=agent["scope"],
                risk_level=agent["risk_level"],
                wait_for_completion=args.wait,
                verify_output=args.verify_output,
                max_wait=args.max_wait
            )
            results.append(result)
            
            # Delay between requests (unless waiting for completion, then delay longer)
            if not args.wait:
                time.sleep(0.5)
            else:
                time.sleep(1)  # Longer delay if waiting
        
        print()
        print("[4/4] Batch execution complete")
        successful = sum(1 for r in results if r.get("success") or r.get("status") in ["COMPLETED", "PENDING", "RUNNING"])
        failed = sum(1 for r in results if r.get("error") or r.get("status") in ["FAILED", "TERMINATED"])
        print(f"   Queued/Completed: {successful}/{len(results)}")
        if failed > 0:
            print(f"   Failed: {failed}/{len(results)}")
        
        # Show workflow status if requested
        if args.workflow_status:
            print()
            print("📊 Workflow Status:")
            try:
                status_response = requests.get(
                    f"{base_url}/api/v1/workflows/{workflow_id}/status",
                    timeout=10
                )
                if status_response.status_code == 200:
                    status = status_response.json()
                    print(f"   Legislative State: {status.get('legislative_state', 'UNKNOWN')}")
                    print(f"   Orchestrator State: {status.get('orchestrator_state', 'UNKNOWN')}")
                    if status.get("review_gates"):
                        gates = status.get("review_gates", [])
                        pending = [g for g in gates if g.get("status") == "PENDING"]
                        if pending:
                            print(f"   ⚠️  {len(pending)} review gate(s) pending")
            except Exception as e:
                print(f"   ⚠️  Error fetching workflow status: {e}")
        
    elif args.agent_id:
        # Single agent execution
        agent_type = args.agent_type or "Intelligence"
        scope = args.scope or f"Execute {args.agent_id}"
        
        # If verify-output requested but not wait, enable wait
        wait_for_completion = args.wait or args.verify_output
        verify_output = args.verify_output
        
        result = execute_agent(
            base_url=base_url,
            workflow_id=workflow_id,
            agent_id=args.agent_id,
            agent_type=agent_type,
            scope=scope,
            risk_level=args.risk_level,
            wait_for_completion=wait_for_completion,
            verify_output=verify_output,
            max_wait=args.max_wait
        )
        
        print()
        print("[4/4] Execution complete")
        
        # Show workflow status if requested
        if args.workflow_status:
            print()
            print("📊 Workflow Status:")
            try:
                status_response = requests.get(
                    f"{base_url}/api/v1/workflows/{workflow_id}/status",
                    timeout=10
                )
                if status_response.status_code == 200:
                    status = status_response.json()
                    print(f"   Legislative State: {status.get('legislative_state', 'UNKNOWN')}")
                    print(f"   Orchestrator State: {status.get('orchestrator_state', 'UNKNOWN')}")
                    if status.get("review_gates"):
                        gates = status.get("review_gates", [])
                        pending = [g for g in gates if g.get("status") == "PENDING"]
                        if pending:
                            print(f"   ⚠️  {len(pending)} review gate(s) pending")
                else:
                    print(f"   ⚠️  Could not fetch workflow status: {status_response.status_code}")
            except Exception as e:
                print(f"   ⚠️  Error fetching workflow status: {e}")
        
        if result.get("success") or result.get("status") in ["PENDING", "RUNNING", "COMPLETED"]:
            if wait_for_completion and result.get("status") == "COMPLETED":
                print("✅ Agent execution completed successfully")
            elif wait_for_completion:
                print(f"✅ Agent execution finished with status: {result.get('status')}")
            else:
                print("✅ Agent execution queued successfully")
        else:
            print("❌ Agent execution failed")
            if result.get("error"):
                print(f"   Error: {result.get('error')}")
            sys.exit(1)
    else:
        print("❌ Must specify --agent-id, --batch, or --list-agents")
        parser.print_help()
        sys.exit(1)
    
    print()
    print("=" * 80)
    print("Next steps:")
    print(f"  1. Monitor execution: Check agent registry or dashboard")
    print(f"  2. View outputs: artifacts/<agent_id>/")
    print(f"  3. Check status: GET {base_url}/api/v1/workflows/{workflow_id}/status")
    print("=" * 80)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
