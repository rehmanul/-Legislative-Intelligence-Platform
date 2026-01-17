"""
Compliance Checker - Validates agent outputs against GUIDANCE boundaries.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import sys

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))


class ComplianceViolation(Exception):
    """Compliance violation error."""
    pass


class ComplianceChecker:
    """Validates agent outputs against GUIDANCE boundaries."""
    
    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize compliance checker.
        
        Args:
            base_dir: Base directory (defaults to agent-orchestrator root)
        """
        if base_dir is None:
            base_dir = BASE_DIR
        
        self.base_dir = Path(base_dir)
        self.guidance_path = base_dir / "guidance" / "PROFESSIONAL_GUIDANCE.json"
        self._load_guidance()
    
    def _load_guidance(self) -> Dict[str, Any]:
        """Load GUIDANCE artifact."""
        if self.guidance_path.exists():
            try:
                return json.loads(self.guidance_path.read_text(encoding="utf-8"))
            except:
                return {}
        return {}
    
    def _get_guidance_signed(self) -> bool:
        """Check if GUIDANCE is signed."""
        guidance = self._load_guidance()
        signatures = guidance.get("_meta", {}).get("signatures", {})
        
        # Check if at least one signature is present
        for role, sig_data in signatures.items():
            if sig_data.get("signed", False):
                return True
        
        return False
    
    def _get_guidance_fully_signed(self) -> bool:
        """Check if GUIDANCE is fully signed (all required roles)."""
        guidance = self._load_guidance()
        signatures = guidance.get("_meta", {}).get("signatures", {})
        
        required_roles = ["legal_counsel", "compliance_officer", "policy_director", "academic_validator"]
        signed_roles = [r for r in required_roles if signatures.get(r, {}).get("signed", False)]
        
        return len(signed_roles) == len(required_roles)
    
    def _get_prohibited_actions(self) -> List[str]:
        """Get all prohibited actions from GUIDANCE."""
        guidance = self._load_guidance()
        constraints = guidance.get("constraints", {})
        
        prohibited = []
        for category in ["legal", "compliance", "policy"]:
            category_constraints = constraints.get(category, {})
            prohibited.extend(category_constraints.get("prohibited_actions", []))
        
        return prohibited
    
    def _get_required_review_triggers(self) -> List[str]:
        """Get all required review triggers from GUIDANCE."""
        guidance = self._load_guidance()
        constraints = guidance.get("constraints", {})
        
        triggers = []
        for category in ["legal", "compliance", "policy"]:
            category_constraints = constraints.get(category, {})
            triggers.extend(category_constraints.get("required_review", []))
        
        return triggers
    
    def check_artifact_compliance(
        self,
        artifact: Dict[str, Any],
        artifact_type: str,
        require_signature: bool = True
    ) -> Tuple[bool, List[str]]:
        """
        Check artifact compliance against GUIDANCE boundaries.
        
        Args:
            artifact: Artifact data dictionary
            artifact_type: Artifact type identifier (e.g., "PRE_CONCEPT", "COMM_LANG")
            require_signature: If True, require GUIDANCE to be signed before checking (default: True)
            
        Returns:
            (is_compliant, violations)
        """
        violations = []
        
        # Check if GUIDANCE is signed
        if not self._get_guidance_signed():
            violations.append("GUIDANCE artifact not signed - compliance checks disabled")
            return False, violations
        
        # Get prohibited actions
        prohibited_actions = self._get_prohibited_actions()
        
        # Check artifact content against prohibited actions
        artifact_text = json.dumps(artifact, default=str).lower()
        
        # Check for prohibited content patterns
        for prohibited in prohibited_actions:
            prohibited_lower = prohibited.lower()
            # Simple keyword check - should be enhanced with NLP
            if prohibited_lower in artifact_text:
                violations.append(f"Artifact may contain prohibited content: {prohibited}")
        
        # Check for required fields based on artifact type
        if artifact_type in ["COMM_LANG", "LEGISLATIVE_LANGUAGE"]:
            # Legislative language requires legal review
            meta = artifact.get("_meta", {})
            if meta.get("requires_review") != "HR_LANG":
                violations.append("Legislative language artifacts require HR_LANG review")
        
        # Check for LDA compliance if applicable
        if artifact_type == "LDA_COMPLIANCE":
            # LDA compliance artifacts require legal review
            meta = artifact.get("_meta", {})
            if meta.get("requires_review") != "HR_LANG":
                violations.append("LDA compliance artifacts require HR_LANG review")
        
        return len(violations) == 0, violations
    
    def check_execution_action_compliance(
        self,
        action_type: str,
        action_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Check execution action compliance before execution.
        
        Args:
            action_type: Type of action (email, phone_call, meeting, etc.)
            action_data: Action data dictionary
            
        Returns:
            (is_compliant, violations)
        """
        violations = []
        
        # Check if GUIDANCE is signed
        if not self._get_guidance_signed():
            violations.append("GUIDANCE artifact not signed - compliance checks disabled")
            return False, violations
        
        # Check for prohibited actions
        prohibited_actions = self._get_prohibited_actions()
        
        # Check action content
        action_text = json.dumps(action_data, default=str).lower()
        
        for prohibited in prohibited_actions:
            prohibited_lower = prohibited.lower()
            if prohibited_lower in action_text:
                violations.append(f"Action may violate prohibition: {prohibited}")
        
        # Check for required LDA contact recording
        if action_type in ["email", "phone_call", "meeting", "letter"]:
            # Check if this is contact with covered official
            contacted_entity = action_data.get("contacted_entity", "").lower()
            if any(indicator in contacted_entity for indicator in [
                "member of congress", "congressional staff", "senator", "representative"
            ]):
                # Should be recorded for LDA reporting
                if not action_data.get("lda_contact_id"):
                    violations.append(
                        "Contact with covered official must be recorded for LDA reporting"
                    )
        
        return len(violations) == 0, violations
    
    def enforce_compliance(
        self,
        artifact: Dict[str, Any],
        artifact_type: str,
        block_on_violation: bool = True
    ) -> Tuple[bool, List[str]]:
        """
        Enforce compliance by blocking non-compliant artifacts.
        
        Args:
            artifact: Artifact data dictionary
            artifact_type: Type of artifact
            block_on_violation: If True, raise exception on violation
            
        Returns:
            (is_compliant, violations)
            
        Raises:
            ComplianceViolation: If block_on_violation=True and violations found
        """
        is_compliant, violations = self.check_artifact_compliance(artifact, artifact_type)
        
        if not is_compliant and block_on_violation:
            raise ComplianceViolation(
                f"Artifact compliance check failed: {', '.join(violations)}"
            )
        
        return is_compliant, violations
    
    def get_compliance_warnings(
        self,
        artifact: Dict[str, Any],
        artifact_type: str
    ) -> List[str]:
        """
        Get compliance warnings without blocking.
        
        Args:
            artifact: Artifact data dictionary
            artifact_type: Type of artifact
            
        Returns:
            List of warning messages
        """
        _, violations = self.check_artifact_compliance(artifact, artifact_type)
        return violations
