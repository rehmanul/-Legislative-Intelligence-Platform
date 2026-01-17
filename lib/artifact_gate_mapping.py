"""
Artifact to Review Gate Mapping
Maps artifact types and names to correct review gates per AUTHORITATIVE_INVARIANTS.md
"""

from typing import Optional, Dict, Any, Tuple

# Mapping from artifact names to review gates
ARTIFACT_NAME_TO_GATE: Dict[str, str] = {
    # HR_PRE artifacts
    "Concept Memo": "HR_PRE",
    "Legitimacy & Policy Framing": "HR_PRE",
    "Policy Framing": "HR_PRE",
    "Policy Whitepaper": "HR_PRE",
    "Whitepaper": "HR_PRE",
    
    # HR_LANG artifacts
    "Draft Legislative Language": "HR_LANG",
    "Legislative Language": "HR_LANG",
    "Amendment Strategy": "HR_LANG",
    "Committee Briefing": "HR_LANG",
    "Briefing Packets": "HR_LANG",
    
    # HR_MSG artifacts
    "Floor Messaging & Talking Points": "HR_MSG",
    "Floor Messaging": "HR_MSG",
    "Media Narrative": "HR_MSG",
    
    # HR_RELEASE artifacts
    "Final Narrative": "HR_RELEASE",
    "Coalition Plan": "HR_RELEASE",
}

# Mapping from artifact types (prefixes) to review gates
ARTIFACT_TYPE_TO_GATE: Dict[str, str] = {
    "PRE_CONCEPT": "HR_PRE",
    "INTRO_FRAME": "HR_PRE",
    "INTRO_WHITEPAPER": "HR_PRE",
    "COMM_LANGUAGE": "HR_LANG",
    "COMM_AMENDMENT": "HR_LANG",
    "COMM_BRIEFING": "HR_LANG",
    "FLOOR_MESSAGING": "HR_MSG",
    "FINAL_NARRATIVE": "HR_RELEASE",
    "FINAL_COALITION": "HR_RELEASE",
}


def get_review_gate_for_artifact(artifact_name: Optional[str] = None, artifact_type: Optional[str] = None) -> Optional[str]:
    """
    Get review gate for artifact based on name or type.
    
    Args:
        artifact_name: Human-readable artifact name
        artifact_type: Artifact type identifier (e.g., PRE_CONCEPT)
    
    Returns:
        Review gate ID (e.g., HR_PRE) or None if not found
    """
    # Try artifact name first
    if artifact_name:
        gate = ARTIFACT_NAME_TO_GATE.get(artifact_name)
        if gate:
            return gate
        
        # Try partial match (case-insensitive)
        artifact_name_lower = artifact_name.lower()
        for name, gate in ARTIFACT_NAME_TO_GATE.items():
            if name.lower() in artifact_name_lower or artifact_name_lower in name.lower():
                return gate
    
    # Try artifact type
    if artifact_type:
        gate = ARTIFACT_TYPE_TO_GATE.get(artifact_type)
        if gate:
            return gate
        
        # Try prefix match
        for type_prefix, gate in ARTIFACT_TYPE_TO_GATE.items():
            if artifact_type.startswith(type_prefix) or type_prefix in artifact_type:
                return gate
    
    return None


def validate_artifact_gate_mapping(artifact_name: Optional[str], artifact_type: Optional[str], requires_review: Optional[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate that artifact is mapped to correct review gate.
    
    Args:
        artifact_name: Human-readable artifact name
        artifact_type: Artifact type identifier
        requires_review: Review gate ID from artifact _meta
    
    Returns:
        (is_valid, error_message)
    """
    if not requires_review:
        # No review required, validation passes
        return True, None
    
    expected_gate = get_review_gate_for_artifact(artifact_name, artifact_type)
    
    if not expected_gate:
        # Cannot determine expected gate, validation passes (may be new artifact type)
        return True, None
    
    if expected_gate != requires_review:
        return False, f"Artifact '{artifact_name}' (type: {artifact_type}) should route to {expected_gate}, but requires_review is {requires_review}"
    
    return True, None
