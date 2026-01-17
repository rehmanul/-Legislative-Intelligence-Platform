"""
Drafting Agent: Sense of Congress (COMM_EVT)
Class: Drafting (Human-Gated)
Purpose: Draft sense of Congress resolution as legislative vehicle
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
OUTPUT_DIR = BASE_DIR / "artifacts" / "draft_sense_of_congress_comm_evt"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

POLICY_RADAR_PATH = BASE_DIR / "artifacts" / "intel_policy_radar_comm_evt" / "POLICY_RADAR_SUMMARY.json"

AGENT_ID = "draft_sense_of_congress_comm_evt"
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

def load_policy_radar() -> Dict[str, Any]:
    artifacts = {}
    try:
        if POLICY_RADAR_PATH.exists():
            artifacts["policy_radar"] = json.loads(POLICY_RADAR_PATH.read_text(encoding='utf-8'))
    except Exception as e:
        log_event("error", f"Failed to load policy radar: {e}")
    return artifacts

def generate_sense_of_congress(policy_data: Dict[str, Any]) -> Dict[str, Any]:
    artifact = {
        "_meta": {
            "agent_id": AGENT_ID,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "artifact_type": "SENSE_OF_CONGRESS",
            "artifact_name": "Sense of Congress",
            "status": "SPECULATIVE",
            "confidence": "SPECULATIVE",
            "human_review_required": True,
            "requires_review": "HR_LANG",
            "guidance_status": "SIGNED" if check_guidance_signed() else "TEST_MODE"
        },
        "vehicle": {
            "type": "sense_of_congress",
            "language": "Draft sense of Congress resolution expressing policy position",
            "placement": "Standalone resolution",
            "rationale": "Sense of Congress provides policy direction without binding authority"
        },
        "summary": {
            "vehicle_characteristics": ["Non-binding", "Policy statement", "Resolution format"]
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
        "scope": "Draft sense of Congress resolution as legislative vehicle",
        "current_task": "Drafting sense of Congress",
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
    
    log_event("task_started", "Sense of Congress drafting started")
    
    print(f"[{AGENT_ID}] Loading policy radar...")
    policy_data = load_policy_radar()
    
    if not policy_data:
        log_event("warning", "No policy radar found - proceeding speculatively")
    
    print(f"[{AGENT_ID}] Drafting sense of Congress...")
    time.sleep(2)
    
    artifact = generate_sense_of_congress(policy_data)
    
    output_file = OUTPUT_DIR / "SENSE_OF_CONGRESS.json"
    output_file.write_text(json.dumps(artifact, indent=2), encoding='utf-8')
    
    for agent in registry.get("agents", []):
        if agent.get("agent_id") == AGENT_ID:
            agent["outputs"].append(str(output_file.relative_to(BASE_DIR)))
            agent["status"] = "WAITING_REVIEW"
            agent["current_task"] = "Sense of Congress drafted - awaiting HR_LANG review"
            break
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_completed", "Sense of Congress generated", output_file=str(output_file), review_gate="HR_LANG")
    log_event("human_review_required", "SENSE_OF_CONGRESS artifact requires HR_LANG approval", artifact=str(output_file))
    
    print(f"[{AGENT_ID}] Sense of Congress generated. Output: {output_file}")
    print(f"[{AGENT_ID}] STATUS: WAITING_REVIEW - Route to HR_LANG gate")
    return output_file

if __name__ == "__main__":
    main()
