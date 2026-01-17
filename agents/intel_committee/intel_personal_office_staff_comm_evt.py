"""
Intelligence Agent: Personal Office Staff (COMM_EVT)
Class: Intelligence (Read-Only)
Purpose: Identify personal office staff contacts
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

BASE_DIR = Path(__file__).parent.parent.parent
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
AUDIT_PATH = BASE_DIR / "audit" / "audit-log.jsonl"
OUTPUT_DIR = BASE_DIR / "artifacts" / "intel_personal_office_staff_comm_evt"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

COMMITTEE_STAFF_PATH = BASE_DIR / "artifacts" / "intel_committee_staff_comm_evt" / "COMMITTEE_STAFF.json"

AGENT_ID = "intel_personal_office_staff_comm_evt"
AGENT_TYPE = "Intelligence"
RISK_LEVEL = "LOW"

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

def load_committee_staff() -> Dict[str, Any]:
    artifacts = {}
    try:
        if COMMITTEE_STAFF_PATH.exists():
            artifacts["committee_staff"] = json.loads(COMMITTEE_STAFF_PATH.read_text(encoding='utf-8'))
    except Exception as e:
        log_event("error", f"Failed to load committee staff: {e}")
    return artifacts

def generate_personal_office_staff(committee_data: Dict[str, Any]) -> Dict[str, Any]:
    artifact = {
        "_meta": {
            "agent_id": AGENT_ID,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "artifact_type": "PERSONAL_OFFICE_STAFF",
            "artifact_name": "Personal Office Staff",
            "status": "SPECULATIVE",
            "confidence": "SPECULATIVE",
            "human_review_required": False,
            "requires_review": None,
            "guidance_status": "SIGNED"
        },
        "office_staff": [
            {
                "member": "Member placeholder",
                "staff_name": "Staff member placeholder",
                "role": "Staff role placeholder",
                "contact_info": "Contact placeholder",
                "relevance": "high"
            }
        ],
        "summary": {
            "total_staff": 1,
            "offices_covered": 1
        }
    }
    return artifact

def main() -> Optional[Path]:
    log_event("agent_spawned", f"Agent {AGENT_ID} spawned", agent_type=AGENT_TYPE, risk_level=RISK_LEVEL)
    
    try:
        registry = json.loads(REGISTRY_PATH.read_text(encoding='utf-8'))
    except:
        registry = {"agents": [], "_meta": {"total_agents": 0, "active_agents": 0}}
    
    agent_entry = {
        "agent_id": AGENT_ID,
        "agent_type": AGENT_TYPE,
        "status": "RUNNING",
        "scope": "Identify personal office staff contacts",
        "current_task": "Identifying personal office staff",
        "last_heartbeat": datetime.utcnow().isoformat() + "Z",
        "risk_level": RISK_LEVEL,
        "outputs": [],
        "spawned_at": datetime.utcnow().isoformat() + "Z"
    }
    registry.setdefault("agents", []).append(agent_entry)
    registry.setdefault("_meta", {})["total_agents"] = len(registry.get("agents", []))
    registry["_meta"]["active_agents"] = len([a for a in registry.get("agents", []) if a.get("status") == "RUNNING"])
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_started", "Personal office staff identification started")
    
    print(f"[{AGENT_ID}] Loading committee staff...")
    committee_data = load_committee_staff()
    
    if not committee_data:
        log_event("warning", "No committee staff found - proceeding speculatively")
    
    print(f"[{AGENT_ID}] Identifying personal office staff...")
    time.sleep(1)
    
    artifact = generate_personal_office_staff(committee_data)
    
    output_file = OUTPUT_DIR / "PERSONAL_OFFICE_STAFF.json"
    output_file.write_text(json.dumps(artifact, indent=2), encoding='utf-8')
    
    for agent in registry.get("agents", []):
        if agent.get("agent_id") == AGENT_ID:
            agent["outputs"].append(str(output_file.relative_to(BASE_DIR)))
            agent["status"] = "IDLE"
            agent["current_task"] = "Personal office staff identified"
            break
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_completed", "Personal office staff generated", output_file=str(output_file))
    
    print(f"[{AGENT_ID}] Personal office staff generated. Output: {output_file}")
    return output_file

if __name__ == "__main__":
    main()
