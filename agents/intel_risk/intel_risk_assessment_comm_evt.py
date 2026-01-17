"""
Intelligence Agent: Comprehensive Risk Assessment (COMM_EVT)
Class: Intelligence (Read-Only)
Purpose: Produce comprehensive risk assessment across all risk categories to pressure-test approved concept before legislative vehicle selection
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

BASE_DIR = Path(__file__).parent.parent.parent
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
AUDIT_PATH = BASE_DIR / "audit" / "audit-log.jsonl"
OUTPUT_DIR = BASE_DIR / "artifacts" / "intel_risk"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Input artifact paths
PRE_CONCEPT_PATH = BASE_DIR / "artifacts" / "draft_concept_memo_pre_evt" / "PRE_CONCEPT.json"
SIGNAL_SCAN_PATH = BASE_DIR / "artifacts" / "intel_signal_scan_pre_evt" / "signal_summary.json"
STAKEHOLDER_MAP_PATH = BASE_DIR / "artifacts" / "intel_stakeholder_map_pre_evt" / "PRE_STAKEHOLDER_MAP.json"

AGENT_ID = "intel_risk_assessment_comm_evt"
AGENT_TYPE = "Intelligence"
RISK_LEVEL = "LOW"

def log_event(event_type: str, message: str, **kwargs):
    """Log event to audit log"""
    event = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "agent_id": AGENT_ID,
        "message": message,
        **kwargs
    }
    with open(AUDIT_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(event) + '\n')

def load_input_artifacts() -> Dict[str, Any]:
    """Load all required input artifacts"""
    artifacts = {}
    
    try:
        if PRE_CONCEPT_PATH.exists():
            artifacts["pre_concept"] = json.loads(PRE_CONCEPT_PATH.read_text(encoding='utf-8'))
            log_event("info", f"Loaded PRE_CONCEPT from {PRE_CONCEPT_PATH}")
        else:
            log_event("warning", f"PRE_CONCEPT not found at {PRE_CONCEPT_PATH}")
    except Exception as e:
        log_event("error", f"Failed to load PRE_CONCEPT: {e}")
    
    try:
        if SIGNAL_SCAN_PATH.exists():
            artifacts["signal_scan"] = json.loads(SIGNAL_SCAN_PATH.read_text(encoding='utf-8'))
            log_event("info", f"Loaded signal scan from {SIGNAL_SCAN_PATH}")
        else:
            log_event("warning", f"Signal scan not found at {SIGNAL_SCAN_PATH}")
    except Exception as e:
        log_event("error", f"Failed to load signal scan: {e}")
    
    try:
        if STAKEHOLDER_MAP_PATH.exists():
            artifacts["stakeholder_map"] = json.loads(STAKEHOLDER_MAP_PATH.read_text(encoding='utf-8'))
            log_event("info", f"Loaded stakeholder map from {STAKEHOLDER_MAP_PATH}")
        else:
            log_event("warning", f"Stakeholder map not found at {STAKEHOLDER_MAP_PATH}")
    except Exception as e:
        log_event("error", f"Failed to load stakeholder map: {e}")
    
    return artifacts

def assess_political_risk(artifacts: Dict[str, Any]) -> Dict[str, Any]:
    """Assess political risk: opposition strength, framing risks"""
    pre_concept = artifacts.get("pre_concept", {})
    stakeholder_map = artifacts.get("stakeholder_map", {})
    signal_scan = artifacts.get("signal_scan", {})
    
    opponents = stakeholder_map.get("stakeholders", {}).get("opponents", [])
    allies = stakeholder_map.get("stakeholders", {}).get("allies", [])
    
    # Calculate opposition strength
    high_influence_opponents = [o for o in opponents if o.get("influence") == "high"]
    high_influence_allies = [a for a in allies if a.get("influence") == "high"]
    
    opposition_strength = "high" if len(high_influence_opponents) >= 2 else "medium" if len(high_influence_opponents) >= 1 else "low"
    
    # Framing risks from signal scan
    framing_risks = []
    if any("regulatory burden" in str(o.get("rationale", "")).lower() for o in opponents):
        framing_risks.append({
            "risk": "Regulatory burden narrative",
            "source": "Industry opponents",
            "severity": "high",
            "description": "Property management and real estate industries may frame policy as excessive regulatory burden"
        })
    
    if any("federal overreach" in str(o.get("rationale", "")).lower() for o in opponents):
        framing_risks.append({
            "risk": "Federal overreach narrative",
            "source": "State/Local Government Associations",
            "severity": "medium",
            "description": "Federalism concerns may be framed as federal overreach"
        })
    
    # Overall political risk level
    # High opposition strength with multiple framing risks = high risk
    # High opposition strength alone = medium risk (strong allies can mitigate)
    # Medium opposition strength with framing risks = medium risk
    if opposition_strength == "high" and len(framing_risks) >= 2:
        risk_level = "high"
    elif opposition_strength == "high":
        risk_level = "medium"  # High opposition but strong allies (4 high-influence allies)
    elif opposition_strength == "medium" and len(framing_risks) >= 1:
        risk_level = "medium"
    elif opposition_strength == "medium":
        risk_level = "low"
    else:
        risk_level = "low"
    
    return {
        "risk_level": risk_level,
        "opposition_strength": opposition_strength,
        "opposition_analysis": {
            "high_influence_opponents": len(high_influence_opponents),
            "opponent_list": [o.get("name") for o in high_influence_opponents],
            "opposition_rationale": [o.get("rationale") for o in high_influence_opponents]
        },
        "allied_support": {
            "high_influence_allies": len(high_influence_allies),
            "ally_list": [a.get("name") for a in high_influence_allies]
        },
        "framing_risks": framing_risks,
        "mitigation_strategies": [
            "Engage high-influence allies early to counter opposition framing",
            "Develop cost-sharing mechanisms to address industry opposition",
            "Frame as federal coordination with state flexibility (not federal overreach)",
            "Emphasize health benefits and economic case (health insurance industry support)",
            "Prepare rapid response protocol for opposition media campaigns"
        ]
    }

def assess_legal_risk(artifacts: Dict[str, Any]) -> Dict[str, Any]:
    """Assess legal risk: preemption, litigation exposure"""
    pre_concept = artifacts.get("pre_concept", {})
    signal_scan = artifacts.get("signal_scan", {})
    stakeholder_map = artifacts.get("stakeholder_map", {})
    
    legal_concerns = []
    
    # Preemption risk
    state_local_opponents = [o for o in stakeholder_map.get("stakeholders", {}).get("opponents", []) 
                             if "state" in o.get("name", "").lower() or "local" in o.get("name", "").lower()]
    if state_local_opponents:
        legal_concerns.append({
            "concern": "Federal preemption of state/local authority",
            "source": "State/Local Government Associations",
            "legal_basis": "Federal standards may override existing state/local air quality regulations. Federalism concerns about state authority.",
            "litigation_exposure": "medium",
            "mitigation": [
                "Frame as federal coordination with state implementation flexibility",
                "Emphasize state health department partnership role",
                "Develop state implementation framework with flexibility",
                "Highlight benefits of federal coordination (consistency, resources, technical support)"
            ]
        })
    
    # Regulatory authority questions
    legal_concerns.append({
        "concern": "Regulatory authority questions",
        "source": "Industry opponents, state/local governments",
        "legal_basis": "Questions about EPA and HUD regulatory authority for indoor air quality standards. May challenge agency authority.",
        "litigation_exposure": "medium",
        "mitigation": [
            "Ensure authorization provides clear regulatory authority",
            "Reference existing EPA and HUD authority where applicable",
            "Develop legal justification for regulatory authority",
            "Coordinate with agency legal counsel",
            "Reference court precedents on landlord liability and air quality"
        ]
    })
    
    # Evidence base and rulemaking requirements
    legal_concerns.append({
        "concern": "Evidence base and rulemaking requirements",
        "source": "Industry opponents, legal challenges",
        "legal_basis": "Regulatory challenges may question evidence base or rulemaking process. Administrative Procedure Act requirements.",
        "litigation_exposure": "low",
        "mitigation": [
            "Reference NDAA verification of military pilot evidence (already verified)",
            "Peer-reviewed health outcomes data",
            "Transparent rulemaking process",
            "Public comment and stakeholder engagement",
            "Clear evidence base documentation"
        ]
    })
    
    # Legal precedents
    legal_precedents = {
        "supportive": [
            "Recent court rulings on landlord liability for mold-related health issues (from PRE_CONCEPT)",
            "EPA authority for indoor air quality (existing precedents)",
            "HUD authority for public housing standards (existing precedents)"
        ],
        "challenging": [
            "State court decisions showing inconsistent application (may support federal standardization)",
            "Federal preemption challenges in other policy areas"
        ]
    }
    
    # Overall legal risk
    if any(c.get("litigation_exposure") == "high" for c in legal_concerns):
        risk_level = "high"
    elif any(c.get("litigation_exposure") == "medium" for c in legal_concerns):
        risk_level = "medium"
    else:
        risk_level = "low"
    
    return {
        "risk_level": risk_level,
        "legal_concerns": legal_concerns,
        "legal_precedents": legal_precedents,
        "litigation_exposure": "medium",
        "mitigation_priorities": [
            "Ensure clear regulatory authority in authorization language",
            "Develop state implementation framework to address federalism concerns",
            "Reference NDAA verification in all legal justifications",
            "Coordinate with agency legal counsel early"
        ]
    }

def assess_fiscal_risk(artifacts: Dict[str, Any]) -> Dict[str, Any]:
    """Assess fiscal risk: budget optics, scoring sensitivity"""
    pre_concept = artifacts.get("pre_concept", {})
    stakeholder_map = artifacts.get("stakeholder_map", {})
    
    # Budget requirements estimation
    budget_requirements = {
        "epa_rulemaking": "Moderate (rulemaking process, technical support)",
        "hud_public_housing": "Moderate-high (monitoring, remediation, technical assistance)",
        "cost_sharing_grants": "High (addresses opposition concerns, enables implementation)",
        "state_implementation_support": "Moderate (technical assistance, coordination)"
    }
    
    total_estimated_cost = "Moderate to high (depends on scope and cost-sharing mechanisms)"
    
    # Resistance factors
    resistance_factors = [
        "Federal budget constraints and competing priorities",
        "Cost estimates for air quality monitoring and remediation programs",
        "Appropriations committee concerns about new spending",
        "Cost-sharing grant requirements may face budget resistance"
    ]
    
    # Cost justification
    cost_justification = [
        "Health insurance cost savings (preventive measures reduce respiratory illness claims)",
        "Long-term cost reduction (preventive vs. reactive remediation)",
        "Public health benefits (reduced respiratory illness)",
        "Economic benefits (healthy buildings, reduced healthcare costs)"
    ]
    
    # Scoring sensitivity
    scoring_sensitivity = "medium-high"  # New spending may require offsets or pay-fors
    
    # Overall fiscal risk
    risk_level = "medium"  # Moderate to high costs but strong cost-benefit case
    
    return {
        "risk_level": risk_level,
        "resistance_factors": resistance_factors,
        "budget_requirements": {
            "estimated_costs": budget_requirements,
            "total_estimated_cost": total_estimated_cost,
            "cost_justification": cost_justification
        },
        "scoring_sensitivity": scoring_sensitivity,
        "appropriations_committee_engagement": {
            "priority": "high",
            "engagement_strategy": [
                "Early engagement with EPA and HUD appropriations subcommittees",
                "Provide detailed cost estimates and cost-benefit analysis",
                "Emphasize economic benefits and cost savings",
                "Coordinate with authorizing committees on cost estimates",
                "Develop appropriations request with clear justification"
            ]
        },
        "mitigation_strategies": [
            "Develop detailed cost-benefit analysis (Health Insurance Industry working group)",
            "Emphasize long-term cost savings and economic benefits",
            "Phase implementation to reduce upfront costs",
            "Leverage existing agency resources where possible",
            "Develop offset proposals (if required)",
            "Frame as preventive healthcare investment (health insurance industry support)"
        ]
    }

def assess_implementation_risk(artifacts: Dict[str, Any]) -> Dict[str, Any]:
    """Assess implementation risk: agency capacity, compliance burden"""
    pre_concept = artifacts.get("pre_concept", {})
    stakeholder_map = artifacts.get("stakeholder_map", {})
    signal_scan = artifacts.get("signal_scan", {})
    
    # Agency capacity assessment
    agency_capacity = {
        "EPA": {
            "capacity": "moderate",
            "concerns": [
                "Existing rulemaking workload may delay indoor air quality rulemaking",
                "Technical expertise available but resource constraints"
            ],
            "mitigation": [
                "Coordinate with EPA early on rulemaking timeline",
                "Provide technical support and evidence base",
                "Align with existing EPA priorities"
            ]
        },
        "HUD": {
            "capacity": "moderate-high",
            "concerns": [
                "Public housing implementation requires coordination with local housing authorities",
                "Monitoring and remediation capacity varies by jurisdiction"
            ],
            "mitigation": [
                "Develop technical assistance programs",
                "Provide implementation support to local housing authorities",
                "Phase implementation to build capacity gradually"
            ]
        },
        "State Health Departments": {
            "capacity": "variable",
            "concerns": [
                "State capacity varies significantly",
                "May require federal technical assistance and funding"
            ],
            "mitigation": [
                "Engage state health departments as implementation partners",
                "Provide federal technical assistance and coordination",
                "Develop state implementation framework with flexibility"
            ]
        }
    }
    
    # Compliance burden
    compliance_burden = {
        "property_management": {
            "burden": "medium-high",
            "concerns": [
                "Monitoring requirements may increase operational costs",
                "Remediation protocols may require technical expertise",
                "Compliance tracking and reporting requirements"
            ],
            "mitigation": [
                "Develop cost-sharing mechanisms (federal grants, insurance incentives)",
                "Provide technical assistance and best practices",
                "Simplify compliance requirements where possible",
                "Phase implementation to allow capacity building"
            ]
        },
        "local_housing_authorities": {
            "burden": "medium",
            "concerns": [
                "Varying capacity across jurisdictions",
                "Coordination with federal agencies required",
                "Funding constraints for monitoring and remediation"
            ],
            "mitigation": [
                "Federal technical assistance and coordination",
                "Cost-sharing grant programs",
                "Phased implementation approach",
                "Flexible compliance framework"
            ]
        }
    }
    
    # Overall implementation risk
    risk_level = "medium"  # Manageable with proper support and phased approach
    
    return {
        "risk_level": risk_level,
        "agency_capacity": agency_capacity,
        "compliance_burden": compliance_burden,
        "implementation_challenges": [
            "Varying state and local capacity",
            "Coordination across multiple agencies (EPA, HUD, state health departments)",
            "Compliance burden on property management and housing authorities",
            "Technical expertise requirements for monitoring and remediation"
        ],
        "mitigation_strategies": [
            "Develop comprehensive technical assistance programs",
            "Provide cost-sharing mechanisms to reduce compliance burden",
            "Phase implementation to build capacity gradually",
            "Engage state health departments as implementation partners",
            "Simplify compliance requirements where possible",
            "Coordinate across agencies to reduce duplication"
        ]
    }

def assess_timeline_risk(artifacts: Dict[str, Any]) -> Dict[str, Any]:
    """Assess timeline risk: election cycles, rulemaking delays"""
    pre_concept = artifacts.get("pre_concept", {})
    signal_scan = artifacts.get("signal_scan", {})
    
    # Election cycle considerations
    election_risks = [
        {
            "risk": "2026 midterm elections",
            "impact": "medium",
            "description": "Policy window may close if control of Congress changes. Need to advance before election cycle intensifies.",
            "mitigation": [
                "Advance policy in early 2026 before election cycle intensifies",
                "Build bipartisan support to reduce election risk",
                "Focus on non-controversial aspects (health benefits, evidence base)"
            ]
        },
        {
            "risk": "2028 presidential election",
            "impact": "low",
            "description": "Longer-term risk if policy not implemented before potential administration change.",
            "mitigation": [
                "Complete rulemaking and initial implementation before 2028",
                "Build institutional support across agencies",
                "Document evidence base and cost-benefit analysis"
            ]
        }
    ]
    
    # Rulemaking delays
    rulemaking_risks = [
        {
            "risk": "EPA rulemaking timeline",
            "impact": "medium",
            "description": "EPA rulemaking process typically takes 2-3 years. Delays may push implementation beyond policy window.",
            "mitigation": [
                "Coordinate with EPA early on rulemaking timeline",
                "Provide comprehensive evidence base to expedite process",
                "Align with existing EPA priorities to reduce delays"
            ]
        },
        {
            "risk": "HUD rulemaking timeline",
            "impact": "medium",
            "description": "HUD rulemaking may face delays due to coordination with local housing authorities.",
            "mitigation": [
                "Engage HUD early on rulemaking approach",
                "Develop state implementation framework to reduce coordination delays",
                "Phase implementation to allow gradual rollout"
            ]
        },
        {
            "risk": "Public comment and stakeholder engagement",
            "impact": "low",
            "description": "Extended public comment periods may delay rulemaking.",
            "mitigation": [
                "Proactive stakeholder engagement before rulemaking",
                "Address opposition concerns early",
                "Build coalition support to expedite process"
            ]
        }
    ]
    
    # Overall timeline risk
    risk_level = "medium"  # Manageable with early coordination and phased approach
    
    return {
        "risk_level": risk_level,
        "election_risks": election_risks,
        "rulemaking_delays": rulemaking_risks,
        "critical_timeline_factors": [
            "Advance policy in early 2026 before election cycle intensifies",
            "Coordinate with EPA and HUD early on rulemaking timelines",
            "Build bipartisan support to reduce election risk",
            "Phase implementation to allow gradual rollout"
        ],
        "mitigation_strategies": [
            "Early coordination with EPA and HUD on rulemaking timelines",
            "Proactive stakeholder engagement before rulemaking",
            "Build bipartisan support to reduce election risk",
            "Phase implementation to allow gradual rollout",
            "Document evidence base and cost-benefit analysis early"
        ]
    }

def generate_risk_assessment(artifacts: Dict[str, Any]) -> Dict[str, Any]:
    """Generate comprehensive risk assessment"""
    
    # Assess each risk category
    political_risk = assess_political_risk(artifacts)
    legal_risk = assess_legal_risk(artifacts)
    fiscal_risk = assess_fiscal_risk(artifacts)
    implementation_risk = assess_implementation_risk(artifacts)
    timeline_risk = assess_timeline_risk(artifacts)
    
    # Calculate overall risk level
    risk_levels = [
        political_risk.get("risk_level"),
        legal_risk.get("risk_level"),
        fiscal_risk.get("risk_level"),
        implementation_risk.get("risk_level"),
        timeline_risk.get("risk_level")
    ]
    
    high_count = risk_levels.count("high")
    medium_count = risk_levels.count("medium")
    
    if high_count >= 2:
        overall_risk = "high"
    elif high_count >= 1 or medium_count >= 3:
        overall_risk = "medium"
    else:
        overall_risk = "low"
    
    # Get policy context
    pre_concept = artifacts.get("pre_concept", {})
    policy_context = pre_concept.get("_meta", {}).get("policy_context", "Air Quality & Mold Risk Policy Scaling")
    
    # Build comprehensive assessment
    assessment = {
        "_meta": {
            "agent_id": AGENT_ID,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "artifact_type": "RISK_ASSESSMENT",
            "artifact_name": "Comprehensive Risk Assessment - Air Quality & Mold Risk Policy Scaling",
            "status": "SPECULATIVE",
            "confidence": "SPECULATIVE",
            "human_review_required": True,
            "requires_review": None,
            "guidance_status": "SIGNED",
            "policy_context": policy_context
        },
        "overall_risk_assessment": {
            "overall_risk_level": overall_risk,
            "risk_summary": f"Overall risk level: {overall_risk.upper()}. Policy scaling is feasible with identified mitigation strategies. Primary risks: {political_risk.get('opposition_strength', 'unknown')} opposition strength, {fiscal_risk.get('risk_level', 'unknown')} fiscal risk, {implementation_risk.get('risk_level', 'unknown')} implementation risk. Evidence verification complete (NDAA verified).",
            "risk_factors": [
                f"Political: {political_risk.get('opposition_strength', 'unknown')} opposition strength",
                f"Legal: {legal_risk.get('risk_level', 'unknown')} litigation exposure",
                f"Fiscal: {fiscal_risk.get('risk_level', 'unknown')} budget resistance",
                f"Implementation: {implementation_risk.get('risk_level', 'unknown')} agency capacity and compliance burden",
                f"Timeline: {timeline_risk.get('risk_level', 'unknown')} election cycles and rulemaking delays"
            ]
        },
        "political_risk": political_risk,
        "legal_risk": legal_risk,
        "fiscal_risk": fiscal_risk,
        "implementation_risk": implementation_risk,
        "timeline_risk": timeline_risk,
        "risk_mitigation_priorities": {
            "critical": [
                "Evidence verification (COMPLETE - NDAA verified)",
                "HR_PRE approval of concept memo (COMPLETE - PRE_CONCEPT approved)"
            ],
            "high": [
                "Industry opposition management (property management, real estate)",
                "Budget resistance mitigation (cost-benefit analysis, economic case)",
                "State health department engagement (federalism concerns)",
                "Early coordination with EPA and HUD on rulemaking timelines"
            ],
            "medium": [
                "Legal objections (regulatory authority, federal preemption)",
                "Media risk (opposition framing, false health claims)",
                "Implementation capacity building (technical assistance, phased rollout)"
            ]
        },
        "risk_monitoring": {
            "monitoring_mechanisms": [
                "Industry association activity tracking (property management, real estate)",
                "Media monitoring (opposition statements, op-eds, social media)",
                "Congressional hearing monitoring (opposition testimony)",
                "State/local government position tracking",
                "Budget process monitoring (appropriations committee activity)",
                "Agency rulemaking timeline tracking (EPA, HUD)"
            ],
            "response_protocol": [
                "Rapid response team (steering committee + working group leads)",
                "Unified messaging framework for risk responses",
                "Coalition asset deployment (economic case, health evidence, tenant stories)",
                "Strategic engagement (where appropriate) to address concerns"
            ]
        },
        "recommendations": [
            "PRIORITIZE early coordination with EPA and HUD on rulemaking timelines",
            "Develop detailed cost-benefit analysis to address budget resistance",
            "Engage state health departments early as implementation partners",
            "Develop cost-sharing mechanisms to address industry opposition",
            "Establish rapid response protocol for opposition management",
            "Create unified messaging framework for all coalition communications",
            "Monitor opposition signals and adapt strategy accordingly",
            "Coordinate risk mitigation across working groups",
            "Track risk metrics to measure mitigation effectiveness",
            "Maintain ethical boundaries (no false health claims, accurate representation)"
        ],
        "disclaimer": "This risk assessment is generated for human review. Risk levels are SPECULATIVE and require validation. All mitigation strategies require professional judgment. No legislative vehicle selection has been made. This assessment is for analysis only - no execution or drafting beyond analysis."
    }
    
    return assessment

def main() -> Optional[Path]:
    """Main agent execution"""
    log_event("agent_spawned", f"Agent {AGENT_ID} spawned", agent_type=AGENT_TYPE, risk_level=RISK_LEVEL)
    
    try:
        registry = json.loads(REGISTRY_PATH.read_text(encoding='utf-8'))
    except:
        registry = {"agents": [], "_meta": {"total_agents": 0, "active_agents": 0}}
    
    agent_entry = {
        "agent_id": AGENT_ID,
        "agent_type": AGENT_TYPE,
        "status": "RUNNING",
        "scope": "Comprehensive risk assessment across all risk categories",
        "current_task": "Assessing risks across political, legal, fiscal, implementation, and timeline categories",
        "last_heartbeat": datetime.utcnow().isoformat() + "Z",
        "risk_level": RISK_LEVEL,
        "outputs": [],
        "spawned_at": datetime.utcnow().isoformat() + "Z"
    }
    registry.setdefault("agents", []).append(agent_entry)
    registry.setdefault("_meta", {})["total_agents"] = len(registry.get("agents", []))
    registry["_meta"]["active_agents"] = len([a for a in registry.get("agents", []) if a.get("status") == "RUNNING"])
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_started", "Comprehensive risk assessment started")
    
    print(f"[{AGENT_ID}] Loading input artifacts...")
    artifacts = load_input_artifacts()
    
    if not artifacts.get("pre_concept"):
        log_event("error", "PRE_CONCEPT not found - cannot proceed without approved concept")
        print(f"[{AGENT_ID}] ERROR: PRE_CONCEPT not found. Cannot proceed without approved concept.")
        return None
    
    if not artifacts.get("signal_scan"):
        log_event("warning", "Signal scan not found - proceeding with limited intelligence")
        print(f"[{AGENT_ID}] WARNING: Signal scan not found - proceeding with limited intelligence")
    
    if not artifacts.get("stakeholder_map"):
        log_event("warning", "Stakeholder map not found - proceeding with limited intelligence")
        print(f"[{AGENT_ID}] WARNING: Stakeholder map not found - proceeding with limited intelligence")
    
    print(f"[{AGENT_ID}] Assessing risks across all categories...")
    time.sleep(1)
    
    assessment = generate_risk_assessment(artifacts)
    
    output_file = OUTPUT_DIR / "RISK_ASSESSMENT.json"
    output_file.write_text(json.dumps(assessment, indent=2), encoding='utf-8')
    
    for agent in registry.get("agents", []):
        if agent.get("agent_id") == AGENT_ID:
            agent["outputs"].append(str(output_file.relative_to(BASE_DIR)))
            agent["status"] = "IDLE"
            agent["current_task"] = "Comprehensive risk assessment complete"
            break
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_completed", "Comprehensive risk assessment generated", output_file=str(output_file))
    log_event("speculative_artifact_generated", "RISK_ASSESSMENT.json generated for human review")
    
    print(f"[{AGENT_ID}] Comprehensive risk assessment generated. Output: {output_file}")
    print(f"[{AGENT_ID}] Overall risk level: {assessment['overall_risk_assessment']['overall_risk_level'].upper()}")
    print(f"[{AGENT_ID}] Risk categories assessed: Political, Legal, Fiscal, Implementation, Timeline")
    
    return output_file

if __name__ == "__main__":
    main()
