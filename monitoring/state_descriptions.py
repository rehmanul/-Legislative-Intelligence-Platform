"""
State Description Utilities (Enhanced)

Provides descriptive subtitles and full descriptions for legislative lifecycle stages.
Implements the enhanced clarity recommendations from Agent Context Clarity Review.
"""

from typing import Dict, Any, Optional


def get_state_description(state_code: str) -> Dict[str, Any]:
    """
    Get full state description with subtitle and details.
    
    Args:
        state_code: Legislative state code (e.g., "PRE_EVT")
        
    Returns:
        Dictionary with abbreviated, subtitle, description, activities, and agent_types
    """
    state_descriptions = {
        "PRE_EVT": {
            "abbreviated": "PRE_EVT",
            "subtitle": "Policy Opportunity Phase",
            "description": "Preparing concept and initial intelligence gathering. Identifying policy opportunities, scanning signals, mapping stakeholders, and developing initial concept memos.",
            "activities": [
                "Signal scanning",
                "Stakeholder mapping",
                "Opposition detection",
                "Concept memo drafting"
            ],
            "agent_types": ["Intelligence", "Drafting"]
        },
        "INTRO_EVT": {
            "abbreviated": "INTRO_EVT",
            "subtitle": "Bill Vehicle Phase",
            "description": "Shaping legitimacy and framing. No outreach or execution has begun. Identifying bill vehicles, securing sponsors, developing framing and whitepapers.",
            "activities": [
                "Sponsor targeting",
                "Legitimacy & policy framing",
                "Academic validation",
                "Policy whitepaper development"
            ],
            "agent_types": ["Intelligence", "Drafting"]
        },
        "COMM_EVT": {
            "abbreviated": "COMM_EVT",
            "subtitle": "Committee Phase",
            "description": "Committee engagement phase. Drafting language and building support. Developing legislative language, committee briefings, and amendment strategies.",
            "activities": [
                "Legislative language drafting",
                "Committee briefing preparation",
                "Amendment strategy development",
                "Coalition building"
            ],
            "agent_types": ["Intelligence", "Drafting", "Execution"]
        },
        "FLOOR_EVT": {
            "abbreviated": "FLOOR_EVT",
            "subtitle": "Floor Activity Phase",
            "description": "Floor action phase. Messaging and vote coordination. Developing floor messaging, talking points, and vote whip strategies.",
            "activities": [
                "Floor messaging development",
                "Vote coordination",
                "Whip count management",
                "Media narrative development"
            ],
            "agent_types": ["Drafting", "Execution"]
        },
        "FINAL_EVT": {
            "abbreviated": "FINAL_EVT",
            "subtitle": "Vote Phase",
            "description": "Final passage phase. Final vote coordination, constituent narrative development, and release authorization.",
            "activities": [
                "Final vote coordination",
                "Constituent narrative development",
                "Release authorization",
                "Success metrics definition"
            ],
            "agent_types": ["Drafting", "Execution"]
        },
        "IMPL_EVT": {
            "abbreviated": "IMPL_EVT",
            "subtitle": "Implementation Phase",
            "description": "Implementation and oversight phase. Monitoring implementation, tracking outcomes, and learning from execution.",
            "activities": [
                "Implementation monitoring",
                "Outcome tracking",
                "Learning and feedback",
                "Post-execution analysis"
            ],
            "agent_types": ["Intelligence", "Learning"]
        }
    }
    
    return state_descriptions.get(state_code, {
        "abbreviated": state_code,
        "subtitle": "Unknown Phase",
        "description": f"State: {state_code}",
        "activities": [],
        "agent_types": []
    })


def translate_state_to_meaning(state_code: str) -> str:
    """
    Translate state code to human-readable meaning (backward compatible).
    
    Args:
        state_code: Legislative state code
        
    Returns:
        Human-readable description string
    """
    desc = get_state_description(state_code)
    return desc["description"]


def format_state_display(state_code: str, format: str = "short") -> str:
    """
    Format state code for display.
    
    Args:
        state_code: Legislative state code
        format: "short" (PRE_EVT (Policy Opportunity Phase)) or "full" (full description)
        
    Returns:
        Formatted string
    """
    desc = get_state_description(state_code)
    
    if format == "short":
        return f"{desc['abbreviated']} ({desc['subtitle']})"
    elif format == "full":
        return f"{desc['abbreviated']} - {desc['subtitle']}\n{desc['description']}"
    else:
        return desc["subtitle"]


def get_review_gate_description(gate_id: str) -> Dict[str, Any]:
    """
    Get review gate description with purpose and criteria.
    
    Args:
        gate_id: Review gate ID (e.g., "HR_PRE")
        
    Returns:
        Dictionary with gate information
    """
    gate_descriptions = {
        "HR_PRE": {
            "gate_id": "HR_PRE",
            "full_name": "Concept & Direction Review",
            "purpose": "Review concept direction, policy opportunity clarity, stakeholder alignment, and evidence citations before proceeding to bill vehicle phase.",
            "checks": [
                "Policy opportunity clarity",
                "Stakeholder alignment",
                "Evidence citations",
                "Concept direction alignment with goals",
                "Risk assessment completeness"
            ],
            "artifact_types": ["PRE_CONCEPT", "PRE_STAKEHOLDER_MAP", "PRE_SIGNAL_SCAN"],
            "state": "PRE_EVT",
            "blocks": "Transition to INTRO_EVT"
        },
        "HR_LANG": {
            "gate_id": "HR_LANG",
            "full_name": "Language & Legislative Review",
            "purpose": "Review legal accuracy, compliance, messaging consistency, and legislative language before committee engagement.",
            "checks": [
                "Legal accuracy",
                "Compliance with regulations",
                "Messaging consistency",
                "Legislative language quality",
                "Committee briefing accuracy"
            ],
            "artifact_types": ["COMM_LANGUAGE", "COMM_BRIEFING", "COMM_AMENDMENT_STRATEGY"],
            "state": "COMM_EVT",
            "blocks": "Committee engagement and external communication"
        },
        "HR_MSG": {
            "gate_id": "HR_MSG",
            "full_name": "Messaging & Narrative Review",
            "purpose": "Review messaging alignment, narrative consistency, and audience appropriateness before floor activity.",
            "checks": [
                "Messaging alignment with goals",
                "Narrative consistency",
                "Audience appropriateness",
                "Floor talking points quality",
                "Vote coordination strategy"
            ],
            "artifact_types": ["FLOOR_MESSAGING", "FLOOR_MEDIA_NARRATIVE", "FLOOR_VOTE_WHIP_STRATEGY"],
            "state": "FLOOR_EVT",
            "blocks": "Floor activity and external communication"
        },
        "HR_RELEASE": {
            "gate_id": "HR_RELEASE",
            "full_name": "Final Release Authorization",
            "purpose": "Final approval, compliance check, release timing, and authorization chain verification before final release.",
            "checks": [
                "Final approval",
                "Compliance verification",
                "Release timing appropriateness",
                "Authorization chain completeness",
                "Success metrics definition"
            ],
            "artifact_types": ["FINAL_CONSTITUENT_NARRATIVE", "FINAL_IMPLEMENTATION_GUIDANCE", "FINAL_SUCCESS_METRICS"],
            "state": "FINAL_EVT",
            "blocks": "Final release and external publication"
        }
    }
    
    return gate_descriptions.get(gate_id, {
        "gate_id": gate_id,
        "full_name": "Unknown Review Gate",
        "purpose": f"Review gate: {gate_id}",
        "checks": [],
        "artifact_types": [],
        "state": "UNKNOWN",
        "blocks": "Unknown"
    })


def format_review_gate_display(gate_id: str, format: str = "short") -> str:
    """
    Format review gate for display.
    
    Args:
        gate_id: Review gate ID
        format: "short" (HR_PRE (Concept & Direction Review)) or "full" (full description)
        
    Returns:
        Formatted string
    """
    gate = get_review_gate_description(gate_id)
    
    if format == "short":
        return f"{gate['gate_id']} ({gate['full_name']})"
    elif format == "full":
        checks = "\n".join(f"  - {check}" for check in gate['checks'])
        return f"{gate['gate_id']} - {gate['full_name']}\nPurpose: {gate['purpose']}\n\nChecks:\n{checks}"
    else:
        return gate["full_name"]
