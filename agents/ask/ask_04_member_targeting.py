"""
ASK-04: Member Targeting Agent

MODE: ASK
ENTRY: workflow.context.committees
OUTPUT: workflow.context.target_members
RESPONSIBILITY: Select Members of Congress
STOP_CONDITION: target_members populated
"""

from pathlib import Path
from typing import Any, List, Dict
from datetime import datetime
from agents.base.ask_agent_base import AskAgentBase

AGENT_ID = "ask_04_member_targeting"
ENTRY_PATH = "context.committees"
OUTPUT_PATH = "context.target_members"
RESPONSIBILITY = "Select Members of Congress"
FORBIDDEN = []


class Ask04MemberTargetingAgent(AskAgentBase):
    """Member Targeting Agent - Selects Members of Congress"""
    
    AGENT_ID = AGENT_ID
    ENTRY_PATH = ENTRY_PATH
    OUTPUT_PATH = OUTPUT_PATH
    RESPONSIBILITY = RESPONSIBILITY
    FORBIDDEN = FORBIDDEN
    
    def _is_stop_condition_met(self, output_value: Any) -> bool:
        """Check if target_members list is populated"""
        if not isinstance(output_value, list):
            return False
        return len(output_value) > 0
    
    def execute(self) -> List[Dict[str, Any]]:
        """
        Execute member targeting.
        
        Reads committees and selects relevant Members of Congress.
        """
        entry_data = self.read_entry()
        
        # Extract committees
        committees = entry_data if isinstance(entry_data, list) else []
        
        target_members = []
        
        # For each committee, identify key members
        for committee in committees:
            chamber = committee.get("chamber", "unknown")
            committee_name = committee.get("committee", "TBD")
            
            # Create placeholder member entries
            # In real implementation, would query member database
            target_members.append({
                "member_id": "TBD",
                "chamber": chamber,
                "committee": committee_name,
                "role": "member",  # member, chair, ranking_member
                "priority": "medium",
                "confidence": "speculative",
                "notes": f"Member identification needed for {chamber} {committee_name}"
            })
        
        # If no committees, create default placeholder
        if not target_members:
            target_members.append({
                "member_id": "TBD",
                "chamber": "TBD",
                "committee": "TBD",
                "role": "member",
                "priority": "medium",
                "confidence": "speculative",
                "notes": "Member targeting requires committee identification"
            })
        
        return target_members


def main(workflow_id: str) -> Path:
    """Main entry point for ASK-04 Member Targeting Agent"""
    agent = Ask04MemberTargetingAgent(workflow_id)
    return agent.main()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: ask_04_member_targeting.py <workflow_id>")
        sys.exit(1)
    
    workflow_id = sys.argv[1]
    result = main(workflow_id)
    if result:
        print(f"✅ Agent completed. Output: {result}")
    else:
        print("❌ Agent failed")
        sys.exit(1)