"""
Execution Directive: Generate Remaining Execution Swarm Agents
Artifact Type: EXECUTION_DIRECTIVE
"""

import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent

AGENT_TEMPLATES = {
    "grassroots_base": """\"\"\"
Execution Agent: {name} ({state})
Class: Execution (Human-Gated)
Purpose: {purpose}
\"\"\"

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

BASE_DIR = Path(__file__).parent.parent
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
GUIDANCE_PATH = BASE_DIR / "guidance" / "PROFESSIONAL_GUIDANCE.json"
AUDIT_PATH = BASE_DIR / "audit" / "audit-log.jsonl"
OUTPUT_DIR = BASE_DIR / "artifacts" / "{agent_id}"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

{dependency_paths}

AGENT_ID = "{agent_id}"
AGENT_TYPE = "Execution"
RISK_LEVEL = "HIGH"

def log_event(event_type: str, message: str, **kwargs):
    event = {{"timestamp": datetime.utcnow().isoformat() + "Z", "event_type": event_type, "agent_id": AGENT_ID, "message": message, **kwargs}}
    with open(AUDIT_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(event) + '\\n')

def check_guidance_signed() -> bool:
    try:
        if GUIDANCE_PATH.exists():
            guidance = json.loads(GUIDANCE_PATH.read_text(encoding='utf-8'))
            signatures = guidance.get("_meta", {{}}).get("signatures", {{}})
            for role, sig_data in signatures.items():
                if sig_data.get("signed", False):
                    return True
        return False
    except:
        return False

{approval_check}

def load_input_artifacts() -> Dict[str, Any]:
    artifacts = {{}}
    {load_artifacts}
    return artifacts

def generate_execution_plan(input_data: Dict[str, Any]) -> Dict[str, Any]:
    return {{
        "_meta": {{
            "agent_id": AGENT_ID,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "artifact_type": "{artifact_type}",
            "artifact_name": "{artifact_name}",
            "status": "SPECULATIVE",
            "confidence": "SPECULATIVE",
            "human_review_required": False,
            "requires_review": None,
            "guidance_status": "SIGNED" if check_guidance_signed() else "TEST_MODE",
            "dependencies": {dependencies_json}
        }},
        "execution_plan": {{
            "status": "PLANNED",
            "planned_actions": [],
            "execution_status": {{"total_actions": 0, "completed": 0, "pending": 0}}
        }},
        "recommendations": ["Execute according to evaluation outputs", "Track execution effectiveness"]
    }}

def main() -> Optional[Path]:
    guidance_signed = check_guidance_signed()
    if not guidance_signed:
        log_event("warning", "GUIDANCE not signed - proceeding in TEST MODE")
    
    log_event("agent_spawned", f"Agent {{AGENT_ID}} spawned", agent_type=AGENT_TYPE, risk_level=RISK_LEVEL)
    
    try:
        registry = json.loads(REGISTRY_PATH.read_text(encoding='utf-8'))
    except:
        registry = {{"agents": [], "_meta": {{"total_agents": 0, "active_agents": 0}}}}
    
    agent_entry = {{
        "agent_id": AGENT_ID,
        "agent_type": AGENT_TYPE,
        "status": "RUNNING",
        "scope": "{purpose}",
        "current_task": "Planning execution",
        "last_heartbeat": datetime.utcnow().isoformat() + "Z",
        "risk_level": RISK_LEVEL,
        "outputs": [],
        "spawned_at": datetime.utcnow().isoformat() + "Z",
        "guidance_signed": guidance_signed
    }}
    registry.setdefault("agents", []).append(agent_entry)
    registry.setdefault("_meta", {{}})["total_agents"] = len(registry.get("agents", []))
    registry["_meta"]["active_agents"] = len([a for a in registry.get("agents", []) if a.get("status") == "RUNNING"])
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_started", "Execution planning started")
    
    input_data = load_input_artifacts()
    if not input_data:
        log_event("warning", "No input artifacts found - proceeding speculatively")
    
    print(f"[{{AGENT_ID}}] Generating execution plan...")
    execution_plan = generate_execution_plan(input_data)
    
    output_file = OUTPUT_DIR / "{artifact_type}.json"
    output_file.write_text(json.dumps(execution_plan, indent=2), encoding='utf-8')
    
    for agent in registry.get("agents", []):
        if agent.get("agent_id") == AGENT_ID:
            agent["outputs"].append(str(output_file.relative_to(BASE_DIR)))
            agent["status"] = "IDLE"
            agent["current_task"] = "Execution plan completed"
            break
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_completed", "Execution plan generated", output_file=str(output_file))
    print(f"[{{AGENT_ID}}] Execution plan generated. Output: {{output_file}}")
    return output_file

if __name__ == "__main__":
    main()
"""
}

AGENT_SPECS = [
    {
        "agent_id": "execution_grassroots_amplify_execute_pre_evt",
        "name": "Grassroots Amplification Executor",
        "state": "PRE_EVT",
        "purpose": "Amplifies grassroots signals to policymakers",
        "artifact_type": "GRASSROOTS_AMPLIFICATION",
        "artifact_name": "Grassroots Amplification",
        "dependencies": [("MOBILIZATION_PATH", "intel_grassroots_mobilization_evaluate_pre_evt/GRASSROOTS_MOBILIZATION_ASSESSMENT.json")],
        "requires_approval": None
    },
    {
        "agent_id": "execution_grassroots_coordinate_execute_pre_evt",
        "name": "Grassroots Coordination Executor",
        "state": "PRE_EVT",
        "purpose": "Coordinates grassroots efforts across regions",
        "artifact_type": "GRASSROOTS_COORDINATION",
        "artifact_name": "Grassroots Coordination",
        "dependencies": [("CAPACITY_PATH", "intel_grassroots_capacity_evaluate_pre_evt/GRASSROOTS_CAPACITY.json")],
        "requires_approval": None
    },
    {
        "agent_id": "execution_grassroots_narrative_execute_pre_evt",
        "name": "Grassroots Narrative Executor",
        "state": "PRE_EVT",
        "purpose": "Executes grassroots narrative campaigns",
        "artifact_type": "GRASSROOTS_NARRATIVE",
        "artifact_name": "Grassroots Narrative",
        "dependencies": [("SIGNAL_PATH", "intel_grassroots_signal_aggregator_evaluate_pre_evt/GRASSROOTS_SIGNAL_AGGREGATE.json")],
        "requires_approval": None
    },
    {
        "agent_id": "execution_grassroots_monitor_execute_pre_evt",
        "name": "Grassroots Monitoring Executor",
        "state": "PRE_EVT",
        "purpose": "Monitors grassroots engagement effectiveness",
        "artifact_type": "GRASSROOTS_MONITORING",
        "artifact_name": "Grassroots Monitoring",
        "dependencies": [("MOBILIZATION_LOG_PATH", "execution_grassroots_mobilize_execute_pre_evt/GRASSROOTS_MOBILIZATION_LOG.json")],
        "requires_approval": None
    },
    {
        "agent_id": "execution_cosponsor_target_execute_comm_evt",
        "name": "Cosponsor Targeting Executor",
        "state": "COMM_EVT",
        "purpose": "Executes targeted cosponsor recruitment",
        "artifact_type": "COSPONSOR_TARGETING_LOG",
        "artifact_name": "Cosponsor Targeting Log",
        "dependencies": [("TARGETS_PATH", "intel_cosponsorship_target_evaluate_comm_evt/COSPONSOR_TARGETS.json")],
        "requires_approval": None
    },
    {
        "agent_id": "execution_cosponsor_outreach_execute_comm_evt",
        "name": "Cosponsor Outreach Executor",
        "state": "COMM_EVT",
        "purpose": "Executes outreach to potential cosponsors",
        "artifact_type": "COSPONSOR_OUTREACH_LOG",
        "artifact_name": "Cosponsor Outreach Log",
        "dependencies": [
            ("TARGETS_PATH", "intel_cosponsorship_target_evaluate_comm_evt/COSPONSOR_TARGETS.json"),
            ("LANG_PATH", "draft_legislative_language_comm_evt/COMM_LANG.json")
        ],
        "requires_approval": "HR_LANG"
    },
    {
        "agent_id": "execution_cosponsor_pathway_execute_comm_evt",
        "name": "Cosponsor Pathway Executor",
        "state": "COMM_EVT",
        "purpose": "Executes influence pathway strategies",
        "artifact_type": "COSPONSOR_PATHWAY_LOG",
        "artifact_name": "Cosponsor Pathway Log",
        "dependencies": [("PATHWAYS_PATH", "intel_cosponsorship_pathway_evaluate_comm_evt/COSPONSOR_PATHWAYS.json")],
        "requires_approval": None
    },
    {
        "agent_id": "execution_cosponsor_timing_execute_comm_evt",
        "name": "Cosponsor Timing Executor",
        "state": "COMM_EVT",
        "purpose": "Executes cosponsor asks at optimal timing",
        "artifact_type": "COSPONSOR_TIMING_LOG",
        "artifact_name": "Cosponsor Timing Log",
        "dependencies": [("TIMING_PATH", "intel_cosponsorship_timing_evaluate_comm_evt/COSPONSOR_TIMING.json")],
        "requires_approval": None
    },
    {
        "agent_id": "execution_cosponsor_track_execute_comm_evt",
        "name": "Cosponsor Tracking Executor",
        "state": "COMM_EVT",
        "purpose": "Tracks cosponsor commitments and updates whip count",
        "artifact_type": "COSPONSOR_TRACKING",
        "artifact_name": "Cosponsor Tracking",
        "dependencies": [
            ("WHIP_COUNT_PATH", "intel_sponsor/intel_whip_count_comm_evt/WHIP_COUNT.json"),
            ("OUTREACH_LOG_PATH", "execution_cosponsor_outreach_execute_comm_evt/COSPONSOR_OUTREACH_LOG.json")
        ],
        "requires_approval": None
    }
]

def generate_agent_file(spec):
    dependency_paths = "\n".join([
        f'{var} = BASE_DIR / "artifacts" / "{path}"'
        for var, path in spec["dependencies"]
    ])
    
    load_artifacts = "\n".join([
        f'try:\n    if {var}.exists():\n        artifacts["{var.split("_PATH")[0].lower()}"] = json.loads({var}.read_text(encoding="utf-8"))\nexcept Exception as e:\n    log_event("error", f"Failed to load {var}: {{e}}")'
        for var, _ in spec["dependencies"]
    ])
    
    dependencies_json = json.dumps([path for _, path in spec["dependencies"]])
    
    approval_check = ""
    if spec.get("requires_approval"):
        approval_check = f'''def check_{spec["requires_approval"].lower()}_approved() -> bool:
    try:
        queue_file = BASE_DIR / "review" / "{spec["requires_approval"]}_queue.json"
        if not queue_file.exists():
            return False
        queue_data = json.loads(queue_file.read_text(encoding='utf-8'))
        approved_reviews = queue_data.get("approved_reviews", [])
        for review in approved_reviews:
            if review.get("decision") == "APPROVE" and review.get("status") == "APPROVED":
                return True
        return False
    except:
        return False
'''
    
    content = AGENT_TEMPLATES["grassroots_base"].format(
        agent_id=spec["agent_id"],
        name=spec["name"],
        state=spec["state"],
        purpose=spec["purpose"],
        artifact_type=spec["artifact_type"],
        artifact_name=spec["artifact_name"],
        dependency_paths=dependency_paths,
        load_artifacts=load_artifacts,
        dependencies_json=dependencies_json,
        approval_check=approval_check
    )
    
    output_file = BASE_DIR / "agents" / f'{spec["agent_id"]}.py'
    output_file.write_text(content, encoding='utf-8')
    print(f"Generated: {output_file}")

def main():
    for spec in AGENT_SPECS:
        generate_agent_file(spec)
    print(f"Generated {len(AGENT_SPECS)} execution agents")

if __name__ == "__main__":
    main()
