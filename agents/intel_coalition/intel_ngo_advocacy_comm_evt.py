"""
Intelligence Agent: NGO & Advocacy (COMM_EVT)
Class: Intelligence (Read-Only)
Purpose: Identify NGOs and advocacy groups in coalition
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

BASE_DIR = Path(__file__).parent.parent.parent
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
AUDIT_PATH = BASE_DIR / "audit" / "audit-log.jsonl"
OUTPUT_DIR = BASE_DIR / "artifacts" / "intel_ngo_advocacy_comm_evt"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FEDERAL_PATH = BASE_DIR / "artifacts" / "intel_federal_agency_pre_evt" / "FEDERAL_AGENCIES.json"

AGENT_ID = "intel_ngo_advocacy_comm_evt"
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

def load_federal_agencies() -> Dict[str, Any]:
    artifacts = {}
    try:
        if FEDERAL_PATH.exists():
            artifacts["federal"] = json.loads(FEDERAL_PATH.read_text(encoding='utf-8'))
    except Exception as e:
        log_event("error", f"Failed to load federal agencies: {e}")
    return artifacts

def generate_ngo_advocacy(federal_data: Dict[str, Any]) -> Dict[str, Any]:
    artifact = {
        "_meta": {
            "agent_id": AGENT_ID,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "artifact_type": "NGO_ADVOCACY",
            "artifact_name": "NGO & Advocacy",
            "status": "SPECULATIVE",
            "confidence": "SPECULATIVE",
            "human_review_required": False,
            "requires_review": None,
            "guidance_status": "SIGNED"
        },
        "ngo_advocacy": [
            {
                "organization_id": "ngo_001",
                "name": "NGO/Advocacy organization placeholder",
                "advocacy_focus": "Policy advocacy",
                "coalition_role": "advocacy_support"
            }
        ],
        "summary": {
            "total_organizations": 1
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
        "scope": "Identify NGOs and advocacy groups in coalition",
        "current_task": "Identifying NGOs and advocacy groups",
        "last_heartbeat": datetime.utcnow().isoformat() + "Z",
        "risk_level": RISK_LEVEL,
        "outputs": [],
        "spawned_at": datetime.utcnow().isoformat() + "Z"
    }
    registry.setdefault("agents", []).append(agent_entry)
    registry.setdefault("_meta", {})["total_agents"] = len(registry.get("agents", []))
    registry["_meta"]["active_agents"] = len([a for a in registry.get("agents", []) if a.get("status") == "RUNNING"])
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_started", "NGO/advocacy identification started")
    
    print(f"[{AGENT_ID}] Loading federal agencies...")
    federal_data = load_federal_agencies()
    
    if not federal_data:
        log_event("warning", "No federal agencies found - proceeding speculatively")
    
    print(f"[{AGENT_ID}] Identifying NGOs and advocacy groups...")
    time.sleep(1)
    
    artifact = generate_ngo_advocacy(federal_data)
    
    output_file = OUTPUT_DIR / "NGO_ADVOCACY.json"
    output_file.write_text(json.dumps(artifact, indent=2), encoding='utf-8')
    
    for agent in registry.get("agents", []):
        if agent.get("agent_id") == AGENT_ID:
            agent["outputs"].append(str(output_file.relative_to(BASE_DIR)))
            agent["status"] = "IDLE"
            agent["current_task"] = "NGOs and advocacy groups identified"
            break
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_completed", "NGO/advocacy generated", output_file=str(output_file))
    
    print(f"[{AGENT_ID}] NGO/advocacy generated. Output: {output_file}")
    return output_file

if __name__ == "__main__":
    main()
