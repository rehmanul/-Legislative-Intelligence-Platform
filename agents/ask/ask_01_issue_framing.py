"""
ASK-01: Issue Framing Agent

MODE: ASK
ENTRY: workflow.context.raw_inputs
OUTPUT: workflow.context.issue_frame
RESPONSIBILITY: Normalize the policy issue into a single frame
FORBIDDEN: Strategy, Tactics
STOP_CONDITION: issue_frame is non-empty and timestamped
"""

from pathlib import Path
from typing import Any, Dict
from datetime import datetime
from agents.base.ask_agent_base import AskAgentBase

BASE_DIR = Path(__file__).parent.parent.parent

AGENT_ID = "ask_01_issue_framing"
ENTRY_PATH = "context.raw_inputs"
OUTPUT_PATH = "context.issue_frame"
RESPONSIBILITY = "Normalize the policy issue into a single frame"
FORBIDDEN = ["Strategy", "Tactics"]


class Ask01IssueFramingAgent(AskAgentBase):
    """Issue Framing Agent - Normalizes policy issue into single frame"""
    
    AGENT_ID = AGENT_ID
    ENTRY_PATH = ENTRY_PATH
    OUTPUT_PATH = OUTPUT_PATH
    RESPONSIBILITY = RESPONSIBILITY
    FORBIDDEN = FORBIDDEN
    
    def _is_stop_condition_met(self, output_value: Any) -> bool:
        """Check if issue_frame is non-empty and timestamped"""
        if not isinstance(output_value, dict):
            return False
        
        if not output_value:
            return False
        
        # Check for timestamp
        if "timestamp" not in output_value and "created_at" not in output_value:
            return False
        
        # Check for issue description
        required_fields = ["issue_description", "policy_area", "key_question"]
        if not any(field in output_value for field in required_fields):
            return False
        
        return True
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute issue framing transformation.
        
        Reads raw_inputs and normalizes into structured issue_frame.
        """
        entry_data = self.read_entry()
        
        # Extract raw inputs
        raw_inputs = entry_data if isinstance(entry_data, dict) else {}
        
        # Normalize into structured frame
        issue_frame = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "issue_description": raw_inputs.get("issue_description", ""),
            "policy_area": raw_inputs.get("policy_area", ""),
            "key_question": raw_inputs.get("key_question", ""),
            "stakeholders_mentioned": raw_inputs.get("stakeholders", []),
            "urgency_indicator": raw_inputs.get("urgency", "unknown"),
            "geographic_scope": raw_inputs.get("scope", "unknown"),
            "source_materials": raw_inputs.get("sources", []),
            "speculative_notes": "This frame is generated from raw inputs and requires human validation"
        }
        
        # If no issue_description, attempt to extract from raw_inputs structure
        if not issue_frame["issue_description"]:
            # Try to infer from other fields
            for key, value in raw_inputs.items():
                if isinstance(value, str) and len(value) > 50:
                    issue_frame["issue_description"] = value[:500]  # Truncate if too long
                    break
        
        return issue_frame


def main(workflow_id: str) -> Path:
    """
    Main entry point for ASK-01 Issue Framing Agent.
    
    Args:
        workflow_id: Workflow identifier
        
    Returns:
        Path to output (workflow path format)
    """
    agent = Ask01IssueFramingAgent(workflow_id)
    return agent.main()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: ask_01_issue_framing.py <workflow_id>")
        sys.exit(1)
    
    workflow_id = sys.argv[1]
    result = main(workflow_id)
    if result:
        print(f"✅ Agent completed. Output: {result}")
    else:
        print("❌ Agent failed")
        sys.exit(1)