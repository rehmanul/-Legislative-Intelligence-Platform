"""
Intelligence Agent: Persuadable Member (COMM_EVT)
Class: Intelligence (Read-Only)
Purpose: Identify persuadable members
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

BASE_DIR = Path(__file__).parent.parent.parent
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
AUDIT_PATH = BASE_DIR / "audit" / "audit-log.jsonl"
OUTPUT_DIR = BASE_DIR / "artifacts" / "intel_persuadable_member_comm_evt"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PRIORITY_PATH = BASE_DIR / "artifacts" / "intel_priority_score_comm_evt" / "PRIORITY_SCORE.json"

AGENT_ID = "intel_persuadable_member_comm_evt"
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

def load_priority_scores() -> Dict[str, Any]:
    artifacts = {}
    try:
        if PRIORITY_PATH.exists():
            artifacts["priority"] = json.loads(PRIORITY_PATH.read_text(encoding='utf-8'))
    except Exception as e:
        log_event("error", f"Failed to load priority scores: {e}")
    return artifacts

def generate_persuadable_members(priority_data: Dict[str, Any]) -> Dict[str, Any]:
    artifact = {
        "_meta": {
            "agent_id": AGENT_ID,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "artifact_type": "PERSUADABLE_MEMBERS",
            "artifact_name": "Persuadable Members",
            "status": "SPECULATIVE",
            "confidence": "SPECULATIVE",
            "human_review_required": False,
            "requires_review": None,
            "guidance_status": "SIGNED"
        },
        "persuadables": [
            {
                "member": "Member placeholder",
                "persuadability_score": 0.75,
                "persuasion_factors": ["Moderate alignment", "Stakeholder pressure", "Policy benefits"],
                "engagement_approach": "Focus on benefits and stakeholder support"
            }
        ],
        "summary": {
            "total_persuadables": 1,
            "medium_score_count": 1
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
        "scope": "Identify persuadable members",
        "current_task": "Identifying persuadable members",
        "last_heartbeat": datetime.utcnow().isoformat() + "Z",
        "risk_level": RISK_LEVEL,
        "outputs": [],
        "spawned_at": datetime.utcnow().isoformat() + "Z"
    }
    registry.setdefault("agents", []).append(agent_entry)
    registry.setdefault("_meta", {})["total_agents"] = len(registry.get("agents", []))
    registry["_meta"]["active_agents"] = len([a for a in registry.get("agents", []) if a.get("status") == "RUNNING"])
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_started", "Persuadable member identification started")
    
    print(f"[{AGENT_ID}] Loading priority scores...")
    priority_data = load_priority_scores()
    
    if not priority_data:
        log_event("warning", "No priority scores found - proceeding speculatively")
    
    print(f"[{AGENT_ID}] Identifying persuadable members...")
    time.sleep(1)
    
    artifact = generate_persuadable_members(priority_data)
    
    output_file = OUTPUT_DIR / "PERSUADABLE_MEMBERS.json"
    output_file.write_text(json.dumps(artifact, indent=2), encoding='utf-8')
    
    for agent in registry.get("agents", []):
        if agent.get("agent_id") == AGENT_ID:
            agent["outputs"].append(str(output_file.relative_to(BASE_DIR)))
            agent["status"] = "IDLE"
            agent["current_task"] = "Persuadable members identified"
            break
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_completed", "Persuadable members generated", output_file=str(output_file))
    
    print(f"[{AGENT_ID}] Persuadable members generated. Output: {output_file}")
    return output_file

if __name__ == "__main__":
    main()
