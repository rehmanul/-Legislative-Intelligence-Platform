"""
Intelligence Agent: Staff Incentive Map (COMM_EVT)
Class: Intelligence (Read-Only)
Purpose: Map staff incentives and motivations
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

BASE_DIR = Path(__file__).parent.parent.parent
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
AUDIT_PATH = BASE_DIR / "audit" / "audit-log.jsonl"
OUTPUT_DIR = BASE_DIR / "artifacts" / "intel_staff_incentive_map_comm_evt"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OFFICE_STAFF_PATH = BASE_DIR / "artifacts" / "intel_personal_office_staff_comm_evt" / "PERSONAL_OFFICE_STAFF.json"

AGENT_ID = "intel_staff_incentive_map_comm_evt"
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

def load_office_staff() -> Dict[str, Any]:
    artifacts = {}
    try:
        if OFFICE_STAFF_PATH.exists():
            artifacts["office_staff"] = json.loads(OFFICE_STAFF_PATH.read_text(encoding='utf-8'))
    except Exception as e:
        log_event("error", f"Failed to load office staff: {e}")
    return artifacts

def generate_staff_incentive_map(staff_data: Dict[str, Any]) -> Dict[str, Any]:
    artifact = {
        "_meta": {
            "agent_id": AGENT_ID,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "artifact_type": "STAFF_INCENTIVE_MAP",
            "artifact_name": "Staff Incentive Map",
            "status": "SPECULATIVE",
            "confidence": "SPECULATIVE",
            "human_review_required": False,
            "requires_review": None,
            "guidance_status": "SIGNED"
        },
        "incentive_mappings": [
            {
                "staff_id": "staff_001",
                "primary_incentives": ["Policy impact", "Member priorities"],
                "engagement_approach": "Focus on alignment with member priorities",
                "motivation_factors": ["Policy relevance", "Stakeholder support"]
            }
        ],
        "summary": {
            "total_mapped": 1,
            "high_engagement_potential": 1
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
        "scope": "Map staff incentives and motivations",
        "current_task": "Mapping staff incentives",
        "last_heartbeat": datetime.utcnow().isoformat() + "Z",
        "risk_level": RISK_LEVEL,
        "outputs": [],
        "spawned_at": datetime.utcnow().isoformat() + "Z"
    }
    registry.setdefault("agents", []).append(agent_entry)
    registry.setdefault("_meta", {})["total_agents"] = len(registry.get("agents", []))
    registry["_meta"]["active_agents"] = len([a for a in registry.get("agents", []) if a.get("status") == "RUNNING"])
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_started", "Staff incentive mapping started")
    
    print(f"[{AGENT_ID}] Loading office staff...")
    staff_data = load_office_staff()
    
    if not staff_data:
        log_event("warning", "No office staff found - proceeding speculatively")
    
    print(f"[{AGENT_ID}] Mapping staff incentives...")
    time.sleep(1)
    
    artifact = generate_staff_incentive_map(staff_data)
    
    output_file = OUTPUT_DIR / "STAFF_INCENTIVE_MAP.json"
    output_file.write_text(json.dumps(artifact, indent=2), encoding='utf-8')
    
    for agent in registry.get("agents", []):
        if agent.get("agent_id") == AGENT_ID:
            agent["outputs"].append(str(output_file.relative_to(BASE_DIR)))
            agent["status"] = "IDLE"
            agent["current_task"] = "Staff incentive map completed"
            break
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_completed", "Staff incentive map generated", output_file=str(output_file))
    
    print(f"[{AGENT_ID}] Staff incentive map generated. Output: {output_file}")
    return output_file

if __name__ == "__main__":
    main()
