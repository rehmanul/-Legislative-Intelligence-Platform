"""
ASK-02: Bill Scope Agent

MODE: ASK
ENTRY: workflow.context.issue_frame
OUTPUT: workflow.context.bill_scope
RESPONSIBILITY: Identify bill(s) affected
FORBIDDEN: Opinionated strategy
STOP_CONDITION: bill_scope list populated
"""

from pathlib import Path
from typing import Any, List, Dict
from datetime import datetime
from agents.base.ask_agent_base import AskAgentBase

AGENT_ID = "ask_02_bill_scope"
ENTRY_PATH = "context.issue_frame"
OUTPUT_PATH = "context.bill_scope"
RESPONSIBILITY = "Identify bill(s) affected"
FORBIDDEN = ["Opinionated strategy"]


class Ask02BillScopeAgent(AskAgentBase):
    """Bill Scope Agent - Identifies bills affected by the issue"""
    
    AGENT_ID = AGENT_ID
    ENTRY_PATH = ENTRY_PATH
    OUTPUT_PATH = OUTPUT_PATH
    RESPONSIBILITY = RESPONSIBILITY
    FORBIDDEN = FORBIDDEN
    
    def _is_stop_condition_met(self, output_value: Any) -> bool:
        """Check if bill_scope list is populated"""
        if not isinstance(output_value, list):
            return False
        return len(output_value) > 0
    
    def execute(self) -> List[Dict[str, Any]]:
        """
        Execute bill scope identification.
        
        Reads issue_frame and identifies affected bills.
        """
        entry_data = self.read_entry()
        
        # Extract issue frame
        issue_frame = entry_data if isinstance(entry_data, dict) else {}
        
        # Identify bills from issue frame
        bill_scope = []
        
        # Check if bills are explicitly mentioned
        if "bill_numbers" in issue_frame:
            for bill_num in issue_frame["bill_numbers"]:
                bill_scope.append({
                    "bill_number": bill_num,
                    "chamber": issue_frame.get("chamber", "unknown"),
                    "status": "identified",
                    "confidence": "speculative"
                })
        
        # If no explicit bills, try to infer from policy_area
        if not bill_scope and "policy_area" in issue_frame:
            policy_area = issue_frame["policy_area"]
            # Create placeholder bill scope entry
            bill_scope.append({
                "policy_area": policy_area,
                "bill_number": "TBD",
                "chamber": "unknown",
                "status": "requires_identification",
                "confidence": "speculative",
                "notes": f"Bill identification needed for policy area: {policy_area}"
            })
        
        # If still empty, create default placeholder
        if not bill_scope:
            bill_scope.append({
                "bill_number": "TBD",
                "chamber": "unknown",
                "status": "requires_identification",
                "confidence": "speculative",
                "notes": "Bill scope identification required - no bills found in issue frame"
            })
        
        return bill_scope


def main(workflow_id: str) -> Path:
    """Main entry point for ASK-02 Bill Scope Agent"""
    agent = Ask02BillScopeAgent(workflow_id)
    return agent.main()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: ask_02_bill_scope.py <workflow_id>")
        sys.exit(1)
    
    workflow_id = sys.argv[1]
    result = main(workflow_id)
    if result:
        print(f"✅ Agent completed. Output: {result}")
    else:
        print("❌ Agent failed")
        sys.exit(1)