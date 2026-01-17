"""
ASK-03: Committee Relevance Agent

MODE: ASK
ENTRY: workflow.context.bill_scope
OUTPUT: workflow.context.committees
RESPONSIBILITY: Map bill → committees
STOP_CONDITION: committee list populated
"""

from pathlib import Path
from typing import Any, List, Dict
from datetime import datetime
from agents.base.ask_agent_base import AskAgentBase

AGENT_ID = "ask_03_committee_relevance"
ENTRY_PATH = "context.bill_scope"
OUTPUT_PATH = "context.committees"
RESPONSIBILITY = "Map bill → committees"
FORBIDDEN = []


class Ask03CommitteeRelevanceAgent(AskAgentBase):
    """Committee Relevance Agent - Maps bills to committees"""
    
    AGENT_ID = AGENT_ID
    ENTRY_PATH = ENTRY_PATH
    OUTPUT_PATH = OUTPUT_PATH
    RESPONSIBILITY = RESPONSIBILITY
    FORBIDDEN = FORBIDDEN
    
    def _is_stop_condition_met(self, output_value: Any) -> bool:
        """Check if committee list is populated"""
        if not isinstance(output_value, list):
            return False
        return len(output_value) > 0
    
    def execute(self) -> List[Dict[str, Any]]:
        """
        Execute committee mapping.
        
        Reads bill_scope and maps to relevant committees.
        """
        entry_data = self.read_entry()
        
        # Extract bill scope
        bill_scope = entry_data if isinstance(entry_data, list) else []
        
        committees = []
        
        # Map each bill to committees
        for bill in bill_scope:
            bill_number = bill.get("bill_number", "TBD")
            chamber = bill.get("chamber", "unknown")
            
            # Standard committee mapping based on policy area
            policy_area = bill.get("policy_area", "general")
            
            # Create committee entries
            if chamber.lower() in ["house", "h.r.", "hr"]:
                committees.append({
                    "chamber": "House",
                    "committee": "Appropriations",  # Placeholder - would need actual mapping
                    "bill_number": bill_number,
                    "jurisdiction": "general",
                    "confidence": "speculative",
                    "notes": "Committee assignment requires verification"
                })
            elif chamber.lower() in ["senate", "s.", "s"]:
                committees.append({
                    "chamber": "Senate",
                    "committee": "Appropriations",  # Placeholder
                    "bill_number": bill_number,
                    "jurisdiction": "general",
                    "confidence": "speculative",
                    "notes": "Committee assignment requires verification"
                })
            else:
                # Unknown chamber - create placeholder for both
                committees.append({
                    "chamber": "House",
                    "committee": "TBD",
                    "bill_number": bill_number,
                    "jurisdiction": "general",
                    "confidence": "speculative",
                    "notes": "Chamber and committee require identification"
                })
        
        # If no bills, create default placeholder
        if not committees:
            committees.append({
                "chamber": "TBD",
                "committee": "TBD",
                "bill_number": "TBD",
                "jurisdiction": "general",
                "confidence": "speculative",
                "notes": "Committee mapping requires bill scope identification"
            })
        
        return committees


def main(workflow_id: str) -> Path:
    """Main entry point for ASK-03 Committee Relevance Agent"""
    agent = Ask03CommitteeRelevanceAgent(workflow_id)
    return agent.main()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: ask_03_committee_relevance.py <workflow_id>")
        sys.exit(1)
    
    workflow_id = sys.argv[1]
    result = main(workflow_id)
    if result:
        print(f"✅ Agent completed. Output: {result}")
    else:
        print("❌ Agent failed")
        sys.exit(1)