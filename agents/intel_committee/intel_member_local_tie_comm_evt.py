"""
Intelligence Agent: Member Local Tie (COMM_EVT)
Class: Intelligence (Read-Only)
Purpose: Identify local connections for members
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

BASE_DIR = Path(__file__).parent.parent.parent
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
AUDIT_PATH = BASE_DIR / "audit" / "audit-log.jsonl"
OUTPUT_DIR = BASE_DIR / "artifacts" / "intel_member_local_tie_comm_evt"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

INCENTIVE_PATH = BASE_DIR / "artifacts" / "intel_staff_incentive_map_comm_evt" / "STAFF_INCENTIVE_MAP.json"

AGENT_ID = "intel_member_local_tie_comm_evt"
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

def load_incentive_map() -> Dict[str, Any]:
    artifacts = {}
    try:
        if INCENTIVE_PATH.exists():
            artifacts["incentive"] = json.loads(INCENTIVE_PATH.read_text(encoding='utf-8'))
    except Exception as e:
        log_event("error", f"Failed to load incentive map: {e}")
    return artifacts

def generate_member_local_ties(incentive_data: Dict[str, Any]) -> Dict[str, Any]:
    artifact = {
        "_meta": {
            "agent_id": AGENT_ID,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "artifact_type": "MEMBER_LOCAL_TIES",
            "artifact_name": "Member Local Ties",
            "status": "SPECULATIVE",
            "confidence": "SPECULATIVE",
            "human_review_required": False,
            "requires_review": None,
            "guidance_status": "SIGNED"
        },
        "local_ties": [
            {
                "member": "Member placeholder",
                "local_connections": ["Local organization 1", "Local organization 2"],
                "tie_strength": "strong",
                "relevance": "high"
            }
        ],
        "summary": {
            "total_members": 1,
            "strong_ties_count": 1
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
        "scope": "Identify local connections for members",
        "current_task": "Identifying member local ties",
        "last_heartbeat": datetime.utcnow().isoformat() + "Z",
        "risk_level": RISK_LEVEL,
        "outputs": [],
        "spawned_at": datetime.utcnow().isoformat() + "Z"
    }
    registry.setdefault("agents", []).append(agent_entry)
    registry.setdefault("_meta", {})["total_agents"] = len(registry.get("agents", []))
    registry["_meta"]["active_agents"] = len([a for a in registry.get("agents", []) if a.get("status") == "RUNNING"])
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_started", "Member local tie identification started")
    
    print(f"[{AGENT_ID}] Loading incentive map...")
    incentive_data = load_incentive_map()
    
    if not incentive_data:
        log_event("warning", "No incentive map found - proceeding speculatively")
    
    print(f"[{AGENT_ID}] Identifying member local ties...")
    time.sleep(1)
    
    artifact = generate_member_local_ties(incentive_data)
    
    output_file = OUTPUT_DIR / "MEMBER_LOCAL_TIES.json"
    output_file.write_text(json.dumps(artifact, indent=2), encoding='utf-8')
    
    for agent in registry.get("agents", []):
        if agent.get("agent_id") == AGENT_ID:
            agent["outputs"].append(str(output_file.relative_to(BASE_DIR)))
            agent["status"] = "IDLE"
            agent["current_task"] = "Member local ties identified"
            break
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_completed", "Member local ties generated", output_file=str(output_file))
    
    print(f"[{AGENT_ID}] Member local ties generated. Output: {output_file}")
    return output_file

if __name__ == "__main__":
    main()
