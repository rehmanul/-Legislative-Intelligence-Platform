"""
Compliance Integration Helper - Provides automatic compliance checking for agents.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import sys

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from lib.compliance_checker import ComplianceChecker, ComplianceViolation


def check_artifact_compliance(
    artifact: Dict[str, Any],
    artifact_type: str,
    block_on_violation: bool = False
) -> Tuple[bool, List[str]]:
    """
    Check artifact compliance against GUIDANCE boundaries.
    
    Agents should call this before writing artifacts to ensure compliance.
    
    Args:
        artifact: Artifact data dictionary
        artifact_type: Type of artifact (e.g., "PRE_CONCEPT", "COMM_LANG")
        block_on_violation: If True, raise exception on violation
        
    Returns:
        (is_compliant, violations)
        
    Raises:
        ComplianceViolation: If block_on_violation=True and violations found
        
    Example:
        ```python
        from lib.compliance_integration import check_artifact_compliance
        
        artifact = generate_concept_memo()
        is_compliant, violations = check_artifact_compliance(
            artifact, "PRE_CONCEPT", block_on_violation=False
        )
        
        if not is_compliant:
            log_event("compliance_warning", f"Compliance violations: {violations}")
            # Optionally update artifact metadata
            artifact["_meta"]["compliance_warnings"] = violations
        ```
    """
    checker = ComplianceChecker()
    
    if block_on_violation:
        return checker.enforce_compliance(artifact, artifact_type, block_on_violation=True)
    else:
        return checker.check_artifact_compliance(artifact, artifact_type)


def get_compliance_warnings(
    artifact: Dict[str, Any],
    artifact_type: str
) -> List[str]:
    """
    Get compliance warnings without blocking.
    
    Use this for non-blocking compliance checking during artifact generation.
    
    Args:
        artifact: Artifact data dictionary
        artifact_type: Type of artifact
        
    Returns:
        List of warning messages (empty if compliant)
    """
    checker = ComplianceChecker()
    return checker.get_compliance_warnings(artifact, artifact_type)


def check_execution_action_compliance(
    action_type: str,
    action_data: Dict[str, Any],
    block_on_violation: bool = True
) -> Tuple[bool, List[str]]:
    """
    Check execution action compliance before execution.
    
    Execution agents should call this before executing external actions.
    
    Args:
        action_type: Type of action (email, phone_call, meeting, etc.)
        action_data: Action data dictionary
        block_on_violation: If True, raise exception on violation
        
    Returns:
        (is_compliant, violations)
        
    Raises:
        ComplianceViolation: If block_on_violation=True and violations found
        
    Example:
        ```python
        from lib.compliance_integration import check_execution_action_compliance
        
        is_compliant, violations = check_execution_action_compliance(
            "email",
            {
                "to": "staff@house.gov",
                "subject": "Policy briefing request",
                "contacted_entity": "Congressional Staff"
            },
            block_on_violation=True
        )
        ```
    """
    checker = ComplianceChecker()
    return checker.check_execution_action_compliance(action_type, action_data)


def is_guidance_signed() -> bool:
    """
    Check if GUIDANCE artifact is signed.
    
    Returns:
        True if at least one signature is present, False otherwise
    """
    checker = ComplianceChecker()
    return checker._get_guidance_signed()
