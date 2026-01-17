"""
DraftAgentBase - Base class for DRAFT-mode agents.

DRAFT agents are responsible for:
- Narrative drafting (economic harm, human story, insurance lens, etc.)
- Vehicle drafting (amendments, pilot programs, report language, sense of congress)

These agents produce content that REQUIRES professional guidance signatures
before execution. Without signed guidance, DRAFT agents are BLOCKED.
"""

from typing import Any, Dict, List, Optional
from pathlib import Path
import json
from agents.base.agent_base import AgentBase


class DraftAgentBase(AgentBase):
    """
    Base class for DRAFT-mode agents.
    
    DRAFT agents produce content that requires:
    - Legal Counsel signature
    - Compliance Officer signature
    - Policy Director signature
    - Academic Validator signature
    
    Without all four signatures, DRAFT agents are BLOCKED.
    """
    
    # Draft agents can produce strategic content, but require guidance
    FORBIDDEN: List[str] = []
    
    # Draft agents ALWAYS require human review
    REQUIRES_HUMAN_REVIEW: bool = True
    
    # Professional guidance is REQUIRED
    REQUIRES_PROFESSIONAL_GUIDANCE: bool = True
    REQUIRED_SIGNATURES: List[str] = [
        "legal_counsel",
        "compliance_officer",
        "policy_director",
        "academic_validator"
    ]
    
    def _check_guidance_signatures(self) -> bool:
        """
        Check if all required professional guidance signatures are present.
        
        Returns:
            True if all signatures are present, False otherwise
        """
        guidance_file = self.base_dir / "guidance" / "PROFESSIONAL_GUIDANCE.json"
        
        if not guidance_file.exists():
            return False
        
        try:
            with open(guidance_file, "r", encoding="utf-8") as f:
                guidance = json.load(f)
            
            signatures = guidance.get("_meta", {}).get("signatures", {})
            
            for sig_type in self.REQUIRED_SIGNATURES:
                sig = signatures.get(sig_type, {})
                if not sig.get("signed", False):
                    return False
            
            return True
            
        except Exception:
            return False
    
    def main(self) -> Optional[Path]:
        """
        Main execution entry point for DRAFT agents.
        
        Blocks execution if professional guidance is not signed.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Check for professional guidance
        if self.REQUIRES_PROFESSIONAL_GUIDANCE:
            if not self._check_guidance_signatures():
                logger.error(
                    f"[{self.AGENT_ID}] BLOCKED: Professional guidance not signed. "
                    f"Required signatures: {self.REQUIRED_SIGNATURES}"
                )
                return None
        
        # Proceed with normal execution
        return super().main()
    
    def validate_output(self, output: Dict[str, Any]) -> bool:
        """
        Extended validation for DRAFT agents.
        
        Ensures outputs include proper citations and disclaimers.
        """
        # First run base validation
        if not super().validate_output(output):
            return False
        
        # Add draft-specific metadata
        output["_draft_metadata"] = {
            "agent_type": "DRAFT",
            "requires_human_review": True,
            "professional_guidance_checked": True,
            "disclaimer": (
                "This content is AI-generated and requires human review. "
                "It should not be used without professional validation."
            ),
        }
        
        return True
