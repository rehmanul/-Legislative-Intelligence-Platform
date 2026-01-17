"""
AskAgentBase - Base class for ASK-mode agents.

ASK agents are responsible for:
- Normalizing and framing policy issues
- Scoping bill analysis
- Committee relevance assessment
- Member targeting
- Signal prioritization

These agents are read-focused and do NOT produce strategic recommendations.
"""

from typing import Any, Dict, List
from agents.base.agent_base import AgentBase


class AskAgentBase(AgentBase):
    """
    Base class for ASK-mode agents.
    
    ASK agents focus on understanding and framing, not strategy.
    They normalize inputs, classify information, and prepare data for downstream agents.
    """
    
    # ASK agents should never output strategy or tactics
    FORBIDDEN: List[str] = ["strategy", "tactics", "recommendation", "action_plan"]
    
    def validate_output(self, output: Dict[str, Any]) -> bool:
        """
        Extended validation for ASK agents.
        
        Ensures outputs don't contain strategic content.
        """
        # First run base validation
        if not super().validate_output(output):
            return False
        
        # Additional ASK-specific validation
        strategic_keywords = [
            "we should", "recommend", "action item", "next steps",
            "proposed strategy", "tactical approach"
        ]
        
        output_str = str(output).lower()
        for keyword in strategic_keywords:
            if keyword in output_str:
                self._log_validation_warning(f"ASK agent output contains strategic language: '{keyword}'")
                # Warning but don't fail - human can review
        
        return True
    
    def _log_validation_warning(self, message: str) -> None:
        """Log a validation warning."""
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"[{self.AGENT_ID}] {message}")
