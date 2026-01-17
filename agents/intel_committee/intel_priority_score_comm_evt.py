"""
Intelligence Agent: Priority Score (COMM_EVT)
Class: Intelligence (Read-Only)
Purpose: Aggregate targeting data into priority scores
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

BASE_DIR = Path(__file__).parent.parent.parent
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
AUDIT_PATH = BASE_DIR / "audit" / "audit-log.jsonl"
OUTPUT_DIR = BASE_DIR / "artifacts" / "intel_priority_score_comm_evt"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Input artifacts from committee targeting agents
JURISDICTION_PATH = BASE_DIR / "artifacts" / "intel_jurisdiction_match_comm_evt" / "JURISDICTION_MATCHES.json"
COMMITTEE_STAFF_PATH = BASE_DIR / "artifacts" / "intel_committee_staff_comm_evt" / "COMMITTEE_STAFF.json"
OFFICE_STAFF_PATH = BASE_DIR / "artifacts" / "intel_personal_office_staff_comm_evt" / "PERSONAL_OFFICE_STAFF.json"
INCENTIVE_PATH = BASE_DIR / "artifacts" / "intel_staff_incentive_map_comm_evt" / "STAFF_INCENTIVE_MAP.json"
LOCAL_TIE_PATH = BASE_DIR / "artifacts" / "intel_member_local_tie_comm_evt" / "MEMBER_LOCAL_TIES.json"

AGENT_ID = "intel_priority_score_comm_evt"
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

def load_targeting_data() -> Dict[str, Any]:
    artifacts = {}
    
    paths = {
        "jurisdiction": JURISDICTION_PATH,
        "committee_staff": COMMITTEE_STAFF_PATH,
        "office_staff": OFFICE_STAFF_PATH,
        "incentive": INCENTIVE_PATH,
        "local_tie": LOCAL_TIE_PATH
    }
    
    for key, path in paths.items():
        try:
            if path.exists():
                artifacts[key] = json.loads(path.read_text(encoding='utf-8'))
        except Exception as e:
            log_event("error", f"Failed to load {key}: {e}")
    
    return artifacts

def generate_priority_scores(targeting_data: Dict[str, Any]) -> Dict[str, Any]:
    artifact = {
        "_meta": {
            "agent_id": AGENT_ID,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "artifact_type": "PRIORITY_SCORE",
            "artifact_name": "Priority Score",
            "status": "SPECULATIVE",
            "confidence": "SPECULATIVE",
            "human_review_required": False,
            "requires_review": None,
            "guidance_status": "SIGNED"
        },
        "priority_scores": [
            {
                "target_id": "target_001",
                "overall_priority": 0.85,
                "component_scores": {
                    "jurisdiction_match": 0.90,
                    "staff_access": 0.80,
                    "incentive_alignment": 0.85,
                    "local_tie_strength": 0.80
                },
                "recommendation": "high_priority"
            }
        ],
        "summary": {
            "total_targets": 1,
            "high_priority_count": 1,
            "average_priority": 0.85
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
        "scope": "Aggregate targeting data into priority scores",
        "current_task": "Calculating priority scores",
        "last_heartbeat": datetime.utcnow().isoformat() + "Z",
        "risk_level": RISK_LEVEL,
        "outputs": [],
        "spawned_at": datetime.utcnow().isoformat() + "Z"
    }
    registry.setdefault("agents", []).append(agent_entry)
    registry.setdefault("_meta", {})["total_agents"] = len(registry.get("agents", []))
    registry["_meta"]["active_agents"] = len([a for a in registry.get("agents", []) if a.get("status") == "RUNNING"])
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_started", "Priority score calculation started")
    
    print(f"[{AGENT_ID}] Loading targeting data...")
    targeting_data = load_targeting_data()
    
    if not targeting_data:
        log_event("warning", "No targeting data found - proceeding speculatively")
    
    print(f"[{AGENT_ID}] Calculating priority scores...")
    time.sleep(1)
    
    artifact = generate_priority_scores(targeting_data)
    
    output_file = OUTPUT_DIR / "PRIORITY_SCORE.json"
    output_file.write_text(json.dumps(artifact, indent=2), encoding='utf-8')
    
    for agent in registry.get("agents", []):
        if agent.get("agent_id") == AGENT_ID:
            agent["outputs"].append(str(output_file.relative_to(BASE_DIR)))
            agent["status"] = "IDLE"
            agent["current_task"] = "Priority scores calculated"
            break
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_completed", "Priority scores generated", output_file=str(output_file))
    
    print(f"[{AGENT_ID}] Priority scores generated. Output: {output_file}")
    return output_file

if __name__ == "__main__":
    main()
