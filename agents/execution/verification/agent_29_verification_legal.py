"""
AGENT-29: Verification Agent — Legal

MODE: AGENT
ENTRY: workflow.tactics
OUTPUT: workflow.verification.legal
RESPONSIBILITY: Legal clearance
STOP_CONDITION: legal clearance logged
"""

from pathlib import Path
from typing import Any, Dict
from datetime import datetime
from agents.base.execution_agent_base import ExecutionAgentBase

AGENT_ID = "agent_29_verification_legal"
ENTRY_PATH = "tactics.*"
OUTPUT_PATH = "verification.legal"
RESPONSIBILITY = "Legal clearance"
FORBIDDEN = []


class Agent29VerificationLegal(ExecutionAgentBase):
    """Verification Agent — Legal - Performs legal clearance"""
    
    AGENT_ID = AGENT_ID
    ENTRY_PATH = ENTRY_PATH
    OUTPUT_PATH = OUTPUT_PATH
    RESPONSIBILITY = RESPONSIBILITY
    FORBIDDEN = FORBIDDEN
    
    def _is_stop_condition_met(self, output_value: Any) -> bool:
        """Check if legal clearance logged"""
        if not isinstance(output_value, dict):
            return False
        return "status" in output_value
    
    def execute(self) -> Dict[str, Any]:
        """Execute legal clearance"""
        entry_data = self.read_entry()
        
        # Extract tactics
        tactics = entry_data.get("tactics.*", {}) if isinstance(entry_data, dict) else entry_data
        if not isinstance(tactics, dict):
            tactics = {}
        
        # Perform legal clearance
        legal = {
            "status": "pending_review",
            "check_date": datetime.utcnow().isoformat() + "Z",
            "compliance_issues": [],
            "requires_human_review": True,
            "confidence": "speculative",
            "notes": "Legal clearance requires professional legal review"
        }
        
        return legal


def main(workflow_id: str) -> Path:
    """Main entry point for AGENT-29 Verification Legal"""
    agent = Agent29VerificationLegal(workflow_id)
    return agent.main()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: agent_29_verification_legal.py <workflow_id>")
        sys.exit(1)
    
    workflow_id = sys.argv[1]
    result = main(workflow_id)
    if result:
        print(f"✅ Agent completed. Output: {result}")
    else:
        print("❌ Agent failed")
        sys.exit(1)