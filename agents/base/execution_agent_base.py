"""
ExecutionAgentBase - Base class for EXECUTION-mode agents.

EXECUTION agents are responsible for:
- Strategy synthesis (narrative, vote math, timing, coalition, risk)
- Verification checks (assumptions, ethics, counter-lobby, legal, final)
- Member engagement execution

These agents produce actionable outputs and require human review gates.
"""

from typing import Any, Dict, List, Optional
from pathlib import Path
from agents.base.agent_base import AgentBase


class ExecutionAgentBase(AgentBase):
    """
    Base class for EXECUTION-mode agents.
    
    EXECUTION agents produce strategic outputs that may include:
    - Strategy recommendations
    - Tactical plans
    - Verification reports
    - Member engagement plans
    
    All EXECUTION agent outputs require human review before action.
    """
    
    # Execution agents can output strategy, but must include review markers
    FORBIDDEN: List[str] = []  # No forbidden content - strategy is allowed
    
    # Review gate configuration
    REQUIRES_HUMAN_REVIEW: bool = True
    REVIEW_GATE: Optional[str] = None  # e.g., "HR_LANG", "HR_PRE"
    
    def validate_output(self, output: Dict[str, Any]) -> bool:
        """
        Extended validation for EXECUTION agents.
        
        Ensures outputs include review markers when required.
        """
        # First run base validation
        if not super().validate_output(output):
            return False
        
        # Ensure output includes confidence level
        if "confidence" not in output:
            output["confidence"] = "requires_review"
        
        # Ensure output includes review flag
        if self.REQUIRES_HUMAN_REVIEW:
            output["_requires_human_review"] = True
            output["_review_gate"] = self.REVIEW_GATE
        
        return True
    
    def write_output(self, data: Dict[str, Any]) -> Path:
        """
        Extended output writing for EXECUTION agents.
        
        Adds execution-specific metadata.
        """
        # Add execution-specific metadata
        data["_execution_metadata"] = {
            "requires_human_review": self.REQUIRES_HUMAN_REVIEW,
            "review_gate": self.REVIEW_GATE,
            "agent_type": "EXECUTION",
            "action_authorized": False,  # Always false until human review
        }
        
        return super().write_output(data)
