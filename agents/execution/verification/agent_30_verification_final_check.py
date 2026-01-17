"""
AGENT-30: Verification Agent — Final Check

MODE: AGENT
ENTRY: workflow.*
OUTPUT: workflow.status.execution_ready
RESPONSIBILITY: Final verification check
STOP_CONDITION: execution_ready = true
"""

from pathlib import Path
from typing import Any
from datetime import datetime
from agents.base.execution_agent_base import ExecutionAgentBase

AGENT_ID = "agent_30_verification_final_check"
ENTRY_PATH = ["context.*", "data.*", "strategy.*", "members.*", "tactics.*", "verification.*"]
OUTPUT_PATH = "status.execution_ready"
RESPONSIBILITY = "Final verification check"
FORBIDDEN = []


class Agent30VerificationFinalCheck(ExecutionAgentBase):
    """Verification Agent — Final Check - Performs final verification"""
    
    AGENT_ID = AGENT_ID
    ENTRY_PATH = ENTRY_PATH
    OUTPUT_PATH = OUTPUT_PATH
    RESPONSIBILITY = RESPONSIBILITY
    FORBIDDEN = FORBIDDEN
    
    def _is_stop_condition_met(self, output_value: Any) -> bool:
        """Check if execution_ready = true"""
        return output_value is True
    
    def execute(self) -> bool:
        """Execute final verification check"""
        entry_data = self.read_entry()
        
        # Load full workflow for comprehensive check
        workflow = self.workflow_manager.load_workflow(self.workflow_id)
        
        # Check all prerequisites
        context = workflow.get("context", {})
        data = workflow.get("data", {})
        strategy = workflow.get("strategy", {})
        members = workflow.get("members", {})
        tactics = workflow.get("tactics", {})
        verification = workflow.get("verification", {})
        
        # All sections must be present and non-empty
        prerequisites_met = (
            len(context) > 0 and
            len(data) > 0 and
            len(strategy) > 0 and
            len(members) > 0 and
            len(tactics) > 0 and
            len(verification) > 0
        )
        
        if not prerequisites_met:
            self.log_event("warning", "Cannot set execution_ready - prerequisites not met")
            return False
        
        # All verification checks must pass
        ethics_status = verification.get("ethics", {}).get("status", "pending")
        legal_status = verification.get("legal", {}).get("status", "pending")
        
        # For now, execution_ready requires human approval
        # This will be set to True after human gates are passed
        execution_ready = False
        
        return execution_ready


def main(workflow_id: str) -> Path:
    """Main entry point for AGENT-30 Verification Final Check"""
    agent = Agent30VerificationFinalCheck(workflow_id)
    return agent.main()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: agent_30_verification_final_check.py <workflow_id>")
        sys.exit(1)
    
    workflow_id = sys.argv[1]
    result = main(workflow_id)
    if result:
        print(f"✅ Agent completed. Output: {result}")
    else:
        print("❌ Agent failed")
        sys.exit(1)