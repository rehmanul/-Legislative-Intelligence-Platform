"""
Integration Test Script for Agent Contract System

Demonstrates end-to-end workflow execution:
1. Create workflow
2. Execute ASK agents
3. Execute PLAN agents  
4. Execute AGENT agents (sample)
5. Show workflow state
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.workflow_manager import get_workflow_manager
from app.workflow_orchestrator import get_workflow_orchestrator


def create_test_workflow(workflow_manager):
    """Create a test workflow with initial data"""
    workflow_id = f"test_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    initial_data = {
        "context": {
            "raw_inputs": {
                "issue_description": "Test policy issue: Renewable energy tax credits",
                "policy_area": "energy",
                "key_question": "Should Congress extend renewable energy tax credits?",
                "urgency": "high",
                "scope": "federal"
            },
            "raw_signals": [
                {"source": "media", "content": "Renewable energy sector growing", "priority": 7},
                {"source": "industry", "content": "Tax credit expiration concerns", "priority": 8}
            ],
            "raw_media": [
                "News article: Renewable energy boom",
                "Editorial: Tax credit importance"
            ],
            "raw_filings": [
                "Industry filing: Extension request"
            ],
            "opposition": {
                "entities": ["Fossil Fuel Lobby"],
                "risk_level": "medium"
            },
            "stakeholders": {
                "allies": ["Solar Industry Association", "Environmental NGOs"],
                "opponents": ["Fossil Fuel Lobby"],
                "neutrals": []
            },
            "constituents": {
                "affected_groups": ["Solar workers", "Homeowners with solar"]
            },
            "calendar": {
                "session": "2026",
                "deadline": "2026-12-31"
            }
        }
    }
    
    workflow = workflow_manager.create_workflow(workflow_id, initial_data)
    print(f"[OK] Created workflow: {workflow_id}")
    return workflow_id


def execute_ask_phase(workflow_id, orchestrator):
    """Execute all ASK mode agents"""
    print("\n=== ASK MODE ===")
    
    ask_agents = [
        "ask_01_issue_framing",
        "ask_02_bill_scope",
        "ask_03_committee_relevance",
        "ask_04_member_targeting",
        "ask_05_signal_prioritization"
    ]
    
    for agent_id in ask_agents:
        print(f"\n[EXEC] Executing {agent_id}...")
        result = orchestrator.execute_next_agent(workflow_id)
        if result:
            if result.get("status") == "completed":
                print(f"   [OK] {agent_id} completed")
            elif result.get("action") == "mode_transition":
                print(f"   [TRANSITION] Mode transition: {result.get('from')} -> {result.get('to')}")
            else:
                print(f"   [WARN] {agent_id}: {result.get('status')}")
        else:
            print(f"   [SKIP] {agent_id} skipped (stop condition met)")


def execute_plan_phase(workflow_id, orchestrator):
    """Execute all PLAN mode agents"""
    print("\n=== PLAN MODE ===")
    
    plan_agents = [
        "plan_01_workflow_sequencer",
        "plan_02_agent_registry",
        "plan_03_dependency_resolver",
        "plan_04_human_gate_planner",
        "plan_05_execution_lock"
    ]
    
    for agent_id in plan_agents:
        print(f"\n📋 Executing {agent_id}...")
        result = orchestrator.execute_next_agent(workflow_id)
        if result:
            if result.get("status") == "completed":
                print(f"   ✅ {agent_id} completed")
            elif result.get("action") == "mode_transition":
                print(f"   🔄 Mode transition: {result.get('from')} → {result.get('to')}")
            else:
                print(f"   ⚠️  {agent_id}: {result.get('status')}")
        else:
            print(f"   ⏭️  {agent_id} skipped")


def execute_sample_agent_phase(workflow_id, orchestrator, max_agents=5):
    """Execute sample AGENT mode agents"""
    print(f"\n=== AGENT MODE (First {max_agents} agents) ===")
    
    for i in range(max_agents):
        print(f"\n📋 Executing next agent...")
        result = orchestrator.execute_next_agent(workflow_id)
        if result:
            agent_id = result.get("agent_id", "unknown")
            if result.get("status") == "completed":
                print(f"   ✅ {agent_id} completed")
            elif result.get("status") == "failed":
                print(f"   ❌ {agent_id} failed: {result.get('error')}")
            else:
                print(f"   ⚠️  {agent_id}: {result}")
        else:
            print(f"   ℹ️  No agent ready to execute (may need dependencies or approval)")


def print_workflow_summary(workflow_manager, workflow_id):
    """Print workflow state summary"""
    workflow = workflow_manager.load_workflow(workflow_id)
    
    print("\n" + "="*60)
    print("WORKFLOW SUMMARY")
    print("="*60)
    print(f"Workflow ID: {workflow_id}")
    print(f"Current Mode: {workflow['status']['current_mode']}")
    print(f"Execution Ready: {workflow['status']['execution_ready']}")
    
    # Plan status
    plan = workflow.get("plan", {})
    print(f"\nPlan Locked: {plan.get('locked', False)}")
    print(f"Sequence Length: {len(plan.get('sequence', []))}")
    print(f"Agents Registered: {len(plan.get('agent_registry', {}))}")
    print(f"Human Gates: {len(plan.get('human_gates', []))}")
    
    # Executed agents
    agent_registry = plan.get("agent_registry", {})
    executed = [aid for aid, info in agent_registry.items() if info.get("executed", False)]
    print(f"\nExecuted Agents: {len(executed)}/{len(agent_registry)}")
    if executed:
        print("  " + "\n  ".join(executed[:10]))
        if len(executed) > 10:
            print(f"  ... and {len(executed) - 10} more")
    
    # Context status
    context = workflow.get("context", {})
    print(f"\nContext Status:")
    print(f"  Issue Frame: {'[OK]' if context.get('issue_frame') else '[MISSING]'}")
    print(f"  Bill Scope: {len(context.get('bill_scope', []))} bills")
    print(f"  Committees: {len(context.get('committees', []))} committees")
    print(f"  Target Members: {len(context.get('target_members', []))} members")
    
    # Data status
    data = workflow.get("data", {})
    signals = data.get("signals", {})
    print(f"\nSignals Collected:")
    for signal_type, signal_list in signals.items():
        print(f"  {signal_type}: {len(signal_list)} signals")
    
    # Strategy status
    strategy = workflow.get("strategy", {})
    print(f"\nStrategy Status:")
    for key in ["narrative", "vote_math", "timing", "coalition", "risks"]:
        value = strategy.get(key)
        if isinstance(value, dict):
            status = "[OK]" if len(value) > 0 else "[MISSING]"
        elif isinstance(value, list):
            status = "[OK]" if len(value) > 0 else "[MISSING]"
        else:
            status = "[MISSING]"
        print(f"  {key}: {status}")
    
    print("\n" + "="*60)
    print(f"[OK] Workflow state saved to: data/workflows/{workflow_id}/workflow.json")
    print("="*60)


def main():
    """Run integration test"""
    print("="*60)
    print("AGENT CONTRACT SYSTEM - INTEGRATION TEST")
    print("="*60)
    
    try:
        # Initialize
        workflow_manager = get_workflow_manager()
        orchestrator = get_workflow_orchestrator()
        
        # Create workflow
        workflow_id = create_test_workflow(workflow_manager)
        
        # Execute ASK phase
        execute_ask_phase(workflow_id, orchestrator)
        
        # Execute PLAN phase
        execute_plan_phase(workflow_id, orchestrator)
        
        # Execute sample AGENT phase
        execute_sample_agent_phase(workflow_id, orchestrator, max_agents=5)
        
        # Print summary
        print_workflow_summary(workflow_manager, workflow_id)
        
        print(f"\n[OK] Test completed successfully!")
        print(f"[FILE] View workflow: data/workflows/{workflow_id}/workflow.json")
        print(f"[COCKPIT] Open cockpit: dashboards/workflow_cockpit.html?workflow_id={workflow_id}")
        
        return workflow_id
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    workflow_id = main()
    if workflow_id:
        sys.exit(0)
    else:
        sys.exit(1)
