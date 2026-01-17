"""
Power Classification Engine
Automated power classification (PRIMARY/SECONDARY/SHADOW) with conflict resolution
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

# Power hierarchy: PRIMARY > SECONDARY > SHADOW
POWER_HIERARCHY = {"PRIMARY": 3, "SECONDARY": 2, "SHADOW": 1}

def classify_member_power(
    member_id: str,
    committee_role: Optional[str] = None,
    leadership_position: Optional[str] = None,
    legislative_state: Optional[str] = None
) -> str:
    """
    Classify member power based on formal roles
    
    Rules:
    - Chair/Ranking Member in COMM_EVT = PRIMARY
    - Leadership positions (Speaker, Majority Leader) = PRIMARY
    - Committee member = SECONDARY
    - Otherwise = SHADOW
    """
    if leadership_position in ["Speaker", "Majority Leader", "Minority Leader", "Whip"]:
        return "PRIMARY"
    
    if legislative_state == "COMM_EVT":
        if committee_role in ["chair", "ranking_member"]:
            return "PRIMARY"
        elif committee_role == "member":
            return "SECONDARY"
    
    if legislative_state == "FLOOR_EVT":
        if leadership_position:
            return "PRIMARY"
        else:
            return "SECONDARY"
    
    if committee_role == "member":
        return "SECONDARY"
    
    return "SHADOW"

def classify_staff_power(
    staff_id: str,
    entity_class: str,
    continuity_score: float = 0.0,
    network_span: int = 0,
    legislative_state: Optional[str] = None
) -> str:
    """
    Classify staff power based on role and power indicators
    
    Rules:
    - Leadership staff in COMM_EVT/FLOOR_EVT = SECONDARY
    - Committee staff with high continuity = SECONDARY
    - High network span = SECONDARY
    - Otherwise = SHADOW
    """
    if entity_class == "leadership_staff":
        if legislative_state in ["COMM_EVT", "FLOOR_EVT"]:
            return "SECONDARY"
    
    if entity_class in ["committee_staff", "subcommittee_staff"]:
        if legislative_state == "COMM_EVT":
            if continuity_score > 0.7 or network_span > 5:
                return "SECONDARY"
            else:
                return "SHADOW"
    
    if continuity_score > 0.8 or network_span > 10:
        return "SECONDARY"
    
    return "SHADOW"

def classify_industry_org_power(
    entity_id: str,
    resource_capacity_score: float = 0.0,
    network_reach: int = 0,
    legislative_state: Optional[str] = None
) -> str:
    """
    Classify industry organization power
    
    Rules:
    - High resource capacity + high network = SECONDARY
    - Otherwise = SHADOW
    """
    if resource_capacity_score > 0.7 and network_reach > 10:
        return "SECONDARY"
    
    return "SHADOW"

def classify_nonprofit_org_power(
    entity_id: str,
    credibility_score: float = 0.0,
    research_influence: float = 0.0,
    mobilization_capacity: float = 0.0,
    legislative_state: Optional[str] = None
) -> str:
    """
    Classify nonprofit organization power
    
    Rules:
    - High credibility + high research = SECONDARY (in COMM_EVT, INTRO_EVT)
    - High mobilization = SECONDARY (in FLOOR_EVT, FINAL_EVT)
    - Otherwise = SHADOW
    """
    if legislative_state in ["INTRO_EVT", "COMM_EVT"]:
        if credibility_score > 0.7 and research_influence > 0.7:
            return "SECONDARY"
    
    if legislative_state in ["FLOOR_EVT", "FINAL_EVT"]:
        if mobilization_capacity > 0.7:
            return "SECONDARY"
    
    return "SHADOW"

def classify_coalition_power(
    entity_id: str,
    aggregate_member_power: float = 0.0,
    coordination_efficiency: float = 0.0,
    legislative_state: Optional[str] = None
) -> str:
    """
    Classify coalition power
    
    Rules:
    - High aggregate power + high coordination = SECONDARY
    - Otherwise = SHADOW
    """
    if aggregate_member_power > 5.0 and coordination_efficiency > 0.7:
        return "SECONDARY"
    
    return "SHADOW"

def resolve_power_conflicts(
    classifications: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Resolve conflicts when multiple power classifications apply
    
    Rules:
    1. PRIMARY > SECONDARY > SHADOW (hierarchy)
    2. Most specific context wins (bill-specific > committee-specific > policy-area > state-only)
    3. Most recent classification wins (if same specificity)
    """
    if not classifications:
        return None
    
    if len(classifications) == 1:
        return classifications[0]
    
    # Sort by specificity (more specific = higher priority)
    def specificity_score(cls: Dict[str, Any]) -> int:
        context = cls.get("context", {})
        score = 0
        if context.get("bill_id"):
            score += 100
        if context.get("committee_id"):
            score += 10
        if context.get("policy_area"):
            score += 5
        if context.get("legislative_state"):
            score += 1
        return score
    
    # Sort by specificity (descending), then by power hierarchy, then by timestamp
    sorted_classifications = sorted(
        classifications,
        key=lambda c: (
            -specificity_score(c),
            -POWER_HIERARCHY.get(c.get("control_type", "SHADOW"), 0),
            c.get("temporal_validity", {}).get("effective_from", "")
        ),
        reverse=True
    )
    
    winner = sorted_classifications[0]
    
    # Mark overrides
    if len(sorted_classifications) > 1:
        winner["overrides_classification_ids"] = [
            c.get("classification_id") for c in sorted_classifications[1:]
            if c.get("classification_id")
        ]
    
    return winner

def create_power_classification(
    entity_id: str,
    control_type: str,
    context: Dict[str, Any],
    evidence: List[str],
    rationale: str,
    base_dir: Path
) -> Dict[str, Any]:
    """
    Create a power classification record compatible with control_classification.schema.json
    """
    now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    classification = {
        "_meta": {
            "schema_version": "1.0.0",
            "doctrine_version": "Congressional Network Mapping v1.0",
            "last_updated": now
        },
        "classification_id": str(uuid.uuid4()),
        "entity_id": entity_id,
        "control_type": control_type,
        "context": {
            "bill_id": context.get("bill_id"),
            "policy_area": context.get("policy_area"),
            "legislative_state": context.get("legislative_state"),
            "committee_id": context.get("committee_id")
        },
        "evidence": evidence,
        "rationale": rationale,
        "overrides_classification_id": context.get("overrides_classification_id"),
        "temporal_validity": {
            "effective_from": context.get("effective_from", now),
            "effective_until": context.get("effective_until")
        }
    }
    
    return classification

def classify_entity_power(
    entity: Dict[str, Any],
    context: Dict[str, Any],
    base_dir: Path
) -> Dict[str, Any]:
    """
    Automatically classify entity power based on entity type and context
    
    Returns a power classification record
    """
    entity_type = entity.get("entity_type")
    entity_id = entity.get("entity_id")
    legislative_state = context.get("legislative_state")
    
    control_type = "SHADOW"  # Default
    evidence = []
    rationale = ""
    
    if entity_type == "member":
        committee_role = entity.get("committee_role")
        leadership_position = entity.get("leadership_position")
        control_type = classify_member_power(
            entity_id, committee_role, leadership_position, legislative_state
        )
        evidence = []
        if committee_role:
            evidence.append(f"Committee role: {committee_role}")
        if leadership_position:
            evidence.append(f"Leadership position: {leadership_position}")
        rationale = f"Member power classified as {control_type} based on role and legislative state {legislative_state}"
    
    elif entity_type == "staff":
        entity_class = entity.get("entity_class")
        continuity_score = entity.get("continuity_score", 0.0)
        network_span = entity.get("network_span", 0)
        control_type = classify_staff_power(
            entity_id, entity_class, continuity_score, network_span, legislative_state
        )
        evidence = [
            f"Staff class: {entity_class}",
            f"Continuity score: {continuity_score:.2f}",
            f"Network span: {network_span}"
        ]
        rationale = f"Staff power classified as {control_type} based on role, continuity, and network"
    
    elif entity_type == "industry_org":
        power_indicators = entity.get("power_indicators", {})
        resource_capacity_score = power_indicators.get("resource_capacity_score", 0.0)
        network_reach = power_indicators.get("network_reach", 0)
        control_type = classify_industry_org_power(
            entity_id, resource_capacity_score, network_reach, legislative_state
        )
        evidence = [
            f"Resource capacity score: {resource_capacity_score:.2f}",
            f"Network reach: {network_reach}"
        ]
        rationale = f"Industry org power classified as {control_type} based on resources and network"
    
    elif entity_type == "nonprofit_org":
        power_indicators = entity.get("power_indicators", {})
        credibility_score = power_indicators.get("credibility_score", 0.0)
        research_influence = power_indicators.get("research_influence", 0.0)
        mobilization_capacity = power_indicators.get("mobilization_capacity_score", 0.0)
        control_type = classify_nonprofit_org_power(
            entity_id, credibility_score, research_influence, mobilization_capacity, legislative_state
        )
        evidence = [
            f"Credibility score: {credibility_score:.2f}",
            f"Research influence: {research_influence:.2f}",
            f"Mobilization capacity: {mobilization_capacity:.2f}"
        ]
        rationale = f"Nonprofit org power classified as {control_type} based on credibility, research, and mobilization"
    
    elif entity_type == "coalition":
        power_indicators = entity.get("power_indicators", {})
        aggregate_member_power = power_indicators.get("aggregate_member_power", 0.0)
        coordination_efficiency = power_indicators.get("coordination_efficiency", 0.0)
        control_type = classify_coalition_power(
            entity_id, aggregate_member_power, coordination_efficiency, legislative_state
        )
        evidence = [
            f"Aggregate member power: {aggregate_member_power:.2f}",
            f"Coordination efficiency: {coordination_efficiency:.2f}"
        ]
        rationale = f"Coalition power classified as {control_type} based on aggregate power and coordination"
    
    # Create classification record
    classification = create_power_classification(
        entity_id=entity_id,
        control_type=control_type,
        context=context,
        evidence=evidence,
        rationale=rationale,
        base_dir=base_dir
    )
    
    return classification
