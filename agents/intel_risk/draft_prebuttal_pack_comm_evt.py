"""
Drafting Agent: Pre-buttal Pack (COMM_EVT)
Class: Drafting (Human-Gated)
Purpose: Aggregate risk analysis into pre-buttal pack
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

BASE_DIR = Path(__file__).parent.parent.parent
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
GUIDANCE_PATH = BASE_DIR / "guidance" / "PROFESSIONAL_GUIDANCE.json"
AUDIT_PATH = BASE_DIR / "audit" / "audit-log.jsonl"
OUTPUT_DIR = BASE_DIR / "artifacts" / "draft_prebuttal_pack_comm_evt"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Input artifacts from risk agents
INDUSTRY_PATH = BASE_DIR / "artifacts" / "intel_industry_pushback_comm_evt" / "INDUSTRY_PUSHBACK.json"
LEGAL_PATH = BASE_DIR / "artifacts" / "intel_legal_objection_comm_evt" / "LEGAL_OBJECTION.json"
BUDGET_PATH = BASE_DIR / "artifacts" / "intel_budget_resistance_comm_evt" / "BUDGET_RESISTANCE.json"
MEDIA_PATH = BASE_DIR / "artifacts" / "intel_media_risk_comm_evt" / "MEDIA_RISK.json"

AGENT_ID = "draft_prebuttal_pack_comm_evt"
AGENT_TYPE = "Drafting"
RISK_LEVEL = "MEDIUM"

def log_event(event_type: str, message: str, **kwargs):
    event = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "agent_id": AGENT_ID,
        "message": message,
        **kwargs
    }
    with open(AUDIT_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(event) + '\n')

def check_guidance_signed() -> bool:
    try:
        guidance = json.loads(GUIDANCE_PATH.read_text(encoding='utf-8'))
        signatures = guidance.get("_meta", {}).get("signatures", {})
        for role, sig_data in signatures.items():
            if sig_data.get("signed", False):
                return True
        return False
    except:
        return False

def load_risk_assessments() -> Dict[str, Any]:
    artifacts = {}
    
    paths = {
        "industry": INDUSTRY_PATH,
        "legal": LEGAL_PATH,
        "budget": BUDGET_PATH,
        "media": MEDIA_PATH
    }
    
    for key, path in paths.items():
        try:
            if path.exists():
                artifacts[key] = json.loads(path.read_text(encoding='utf-8'))
        except Exception as e:
            log_event("error", f"Failed to load {key}: {e}")
    
    return artifacts

def generate_prebuttal_pack(risk_data: Dict[str, Any]) -> Dict[str, Any]:
    artifact = {
        "_meta": {
            "agent_id": AGENT_ID,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "artifact_type": "PREBUTTAL_PACK",
            "artifact_name": "Pre-buttal Pack",
            "status": "SPECULATIVE",
            "confidence": "SPECULATIVE",
            "human_review_required": True,
            "requires_review": "HR_LANG",
            "guidance_status": "SIGNED" if check_guidance_signed() else "TEST_MODE"
        },
        "prebuttal_materials": {
            "industry_pushback": risk_data.get("industry", {}).get("pushback_assessment", {}),
            "legal_objections": risk_data.get("legal", {}).get("legal_assessment", {}),
            "budget_resistance": risk_data.get("budget", {}).get("budget_assessment", {}),
            "media_risks": risk_data.get("media", {}).get("media_assessment", {})
        },
        "counter_arguments": [
            {
                "risk_type": "Industry pushback",
                "counter_argument": "Policy benefits outweigh industry concerns",
                "supporting_evidence": "Economic analysis and stakeholder support"
            }
        ],
        "summary": {
            "total_risks_addressed": len(risk_data),
            "prebuttal_readiness": "ready"
        }
    }
    return artifact

def main() -> Optional[Path]:
    guidance_signed = check_guidance_signed()
    if not guidance_signed:
        print(f"[{AGENT_ID}] WARNING: GUIDANCE artifact not signed. Proceeding in TEST MODE.")
        log_event("warning", "GUIDANCE not signed - proceeding in test mode")
    
    log_event("agent_spawned", f"Agent {AGENT_ID} spawned", agent_type=AGENT_TYPE, risk_level=RISK_LEVEL, guidance_signed=guidance_signed)
    
    try:
        registry = json.loads(REGISTRY_PATH.read_text(encoding='utf-8'))
    except:
        registry = {"agents": [], "_meta": {"total_agents": 0, "active_agents": 0}}
    
    agent_entry = {
        "agent_id": AGENT_ID,
        "agent_type": AGENT_TYPE,
        "status": "RUNNING",
        "scope": "Aggregate risk analysis into pre-buttal pack",
        "current_task": "Drafting pre-buttal pack",
        "last_heartbeat": datetime.utcnow().isoformat() + "Z",
        "risk_level": RISK_LEVEL,
        "outputs": [],
        "spawned_at": datetime.utcnow().isoformat() + "Z",
        "guidance_signed": guidance_signed
    }
    registry.setdefault("agents", []).append(agent_entry)
    registry.setdefault("_meta", {})["total_agents"] = len(registry.get("agents", []))
    registry["_meta"]["active_agents"] = len([a for a in registry.get("agents", []) if a.get("status") == "RUNNING"])
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_started", "Pre-buttal pack drafting started")
    
    print(f"[{AGENT_ID}] Loading risk assessments...")
    risk_data = load_risk_assessments()
    
    if not risk_data:
        log_event("warning", "No risk assessments found - proceeding speculatively")
    
    print(f"[{AGENT_ID}] Drafting pre-buttal pack...")
    time.sleep(2)
    
    artifact = generate_prebuttal_pack(risk_data)
    
    output_file = OUTPUT_DIR / "PREBUTTAL_PACK.json"
    output_file.write_text(json.dumps(artifact, indent=2), encoding='utf-8')
    
    for agent in registry.get("agents", []):
        if agent.get("agent_id") == AGENT_ID:
            agent["outputs"].append(str(output_file.relative_to(BASE_DIR)))
            agent["status"] = "WAITING_REVIEW"
            agent["current_task"] = "Pre-buttal pack drafted - awaiting HR_LANG review"
            break
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_completed", "Pre-buttal pack generated", output_file=str(output_file), review_gate="HR_LANG")
    log_event("human_review_required", "PREBUTTAL_PACK artifact requires HR_LANG approval", artifact=str(output_file))
    
    print(f"[{AGENT_ID}] Pre-buttal pack generated. Output: {output_file}")
    print(f"[{AGENT_ID}] STATUS: WAITING_REVIEW - Route to HR_LANG gate")
    return output_file

if __name__ == "__main__":
    main()
