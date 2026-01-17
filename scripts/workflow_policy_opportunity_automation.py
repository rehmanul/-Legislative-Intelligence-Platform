"""
Script: workflow_policy_opportunity_automation.py
Intent:
- temporal

Reads:
- agent-orchestrator/artifacts/policy/WIRELESS_CHARGING_INSURABLE_RISK_POLICY_OPPORTUNITY.json
- agent-orchestrator/agents/intel_policy_opportunity_analyzer_pre_evt.py
- agent-orchestrator/agents/draft_policy_opportunity_document_pre_evt.py

Writes:
- stdout (workflow execution log)

Schema:
Workflow automation script - no persistent outputs
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).parent.parent
AGENTS_DIR = BASE_DIR / "agents"
POLICY_DIR = BASE_DIR / "artifacts" / "policy"

def run_agent(agent_path: Path) -> bool:
    """Run an agent script"""
    try:
        print(f"\n{'='*60}")
        print(f"Running: {agent_path.name}")
        print(f"{'='*60}")
        
        result = subprocess.run(
            [sys.executable, str(agent_path)],
            capture_output=True,
            text=True,
            cwd=str(BASE_DIR)
        )
        
        if result.returncode == 0:
            print(result.stdout)
            print(f"✅ {agent_path.name} completed successfully")
            return True
        else:
            print(f"❌ {agent_path.name} failed")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running {agent_path.name}: {e}")
        return False

def main():
    """Execute policy opportunity workflow automation"""
    
    print("="*60)
    print("Policy Opportunity Workflow Automation")
    print(f"Started: {datetime.utcnow().isoformat()}Z")
    print("="*60)
    
    # Step 1: Check prerequisites
    print("\n[Step 1] Checking prerequisites...")
    policy_opp_file = POLICY_DIR / "WIRELESS_CHARGING_INSURABLE_RISK_POLICY_OPPORTUNITY.json"
    if not policy_opp_file.exists():
        print(f"❌ Policy opportunity file not found: {policy_opp_file}")
        print("   Please create the policy opportunity analysis first.")
        return False
    
    print(f"✅ Policy opportunity file found: {policy_opp_file}")
    
    # Step 2: Run intelligence agent
    print("\n[Step 2] Running intelligence agent...")
    intel_agent = AGENTS_DIR / "intel_policy_opportunity_analyzer_pre_evt.py"
    if not intel_agent.exists():
        print(f"⚠️  Intelligence agent not found: {intel_agent}")
        print("   Skipping intelligence analysis...")
    else:
        if not run_agent(intel_agent):
            print("⚠️  Intelligence agent failed, continuing...")
    
    # Step 3: Run drafting agent
    print("\n[Step 3] Running drafting agent...")
    draft_agent = AGENTS_DIR / "draft_policy_opportunity_document_pre_evt.py"
    if not draft_agent.exists():
        print(f"⚠️  Drafting agent not found: {draft_agent}")
        print("   Skipping document generation...")
    else:
        if not run_agent(draft_agent):
            print("⚠️  Drafting agent failed, continuing...")
    
    # Step 4: Generate artifacts index
    print("\n[Step 4] Generating artifacts index...")
    index_script = BASE_DIR / "scripts" / "generate_policy_opportunity_artifacts.py"
    if index_script.exists():
        run_agent(index_script)
    else:
        print(f"⚠️  Index script not found: {index_script}")
    
    # Summary
    print("\n" + "="*60)
    print("Workflow Automation Complete")
    print(f"Completed: {datetime.utcnow().isoformat()}Z")
    print("="*60)
    print("\nNext Steps:")
    print("1. Review generated artifacts in artifacts/policy/")
    print("2. Review agent outputs in artifacts/intel_policy_opportunity_analyzer_pre_evt/")
    print("3. Review drafted documents in artifacts/draft_policy_opportunity_document_pre_evt/")
    print("4. Submit artifacts for HR_PRE review if ready")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
