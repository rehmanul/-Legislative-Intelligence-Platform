"""
Drafting Agent: Insurance Lens (COMM_EVT)
Class: Drafting (Human-Gated)
Purpose: Generate loss reduction perspective narrative
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
OUTPUT_DIR = BASE_DIR / "artifacts" / "draft_insurance_lens_comm_evt"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OPERATIONAL_PATH = BASE_DIR / "artifacts" / "draft_operational_impact_comm_evt" / "OPERATIONAL_IMPACT.json"

AGENT_ID = "draft_insurance_lens_comm_evt"
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

def load_operational_impact() -> Dict[str, Any]:
    artifacts = {}
    try:
        if OPERATIONAL_PATH.exists():
            artifacts["operational"] = json.loads(OPERATIONAL_PATH.read_text(encoding='utf-8'))
    except Exception as e:
        log_event("error", f"Failed to load operational impact: {e}")
    return artifacts

def generate_insurance_lens(operational_data: Dict[str, Any]) -> Dict[str, Any]:
    artifact = {
        "_meta": {
            "agent_id": AGENT_ID,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "artifact_type": "INSURANCE_LENS",
            "artifact_name": "Insurance Lens",
            "status": "SPECULATIVE",
            "confidence": "SPECULATIVE",
            "human_review_required": True,
            "requires_review": "HR_LANG",
            "guidance_status": "SIGNED" if check_guidance_signed() else "TEST_MODE"
        },
        "narrative": {
            "insurance_perspective": "Loss reduction and risk mitigation from insurance perspective",
            "loss_reduction": "Quantified loss reduction potential",
            "risk_mitigation": "Risk mitigation benefits"
        },
        "summary": {
            "perspective_elements": ["Loss reduction", "Risk mitigation", "Insurance benefits"]
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
        "scope": "Generate loss reduction perspective narrative",
        "current_task": "Drafting insurance lens narrative",
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
    
    log_event("task_started", "Insurance lens narrative drafting started")
    
    print(f"[{AGENT_ID}] Loading operational impact...")
    operational_data = load_operational_impact()
    
    if not operational_data:
        log_event("warning", "No operational impact found - proceeding speculatively")
    
    print(f"[{AGENT_ID}] Drafting insurance lens narrative...")
    time.sleep(2)
    
    artifact = generate_insurance_lens(operational_data)
    
    output_file = OUTPUT_DIR / "INSURANCE_LENS.json"
    output_file.write_text(json.dumps(artifact, indent=2), encoding='utf-8')
    
    for agent in registry.get("agents", []):
        if agent.get("agent_id") == AGENT_ID:
            agent["outputs"].append(str(output_file.relative_to(BASE_DIR)))
            agent["status"] = "WAITING_REVIEW"
            agent["current_task"] = "Insurance lens narrative drafted - awaiting HR_LANG review"
            break
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_completed", "Insurance lens narrative generated", output_file=str(output_file), review_gate="HR_LANG")
    log_event("human_review_required", "INSURANCE_LENS artifact requires HR_LANG approval", artifact=str(output_file))
    
    print(f"[{AGENT_ID}] Insurance lens narrative generated. Output: {output_file}")
    print(f"[{AGENT_ID}] STATUS: WAITING_REVIEW - Route to HR_LANG gate")
    return output_file

if __name__ == "__main__":
    main()
