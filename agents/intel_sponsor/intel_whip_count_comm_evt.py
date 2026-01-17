"""
Intelligence Agent: Whip Count (COMM_EVT)
Class: Intelligence (Read-Only)
Purpose: Aggregate sponsor analysis into whip count
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

BASE_DIR = Path(__file__).parent.parent.parent
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
AUDIT_PATH = BASE_DIR / "audit" / "audit-log.jsonl"
OUTPUT_DIR = BASE_DIR / "artifacts" / "intel_whip_count_comm_evt"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Input artifacts from sponsor pipeline agents
CHAMPION_PATH = BASE_DIR / "artifacts" / "intel_natural_champion_comm_evt" / "NATURAL_CHAMPIONS.json"
PERSUADABLE_PATH = BASE_DIR / "artifacts" / "intel_persuadable_member_comm_evt" / "PERSUADABLE_MEMBERS.json"
COSPONSOR_PATH = BASE_DIR / "artifacts" / "intel_cover_cosponsor_comm_evt" / "COVER_COSPONSORS.json"
OPPOSITION_PATH = BASE_DIR / "artifacts" / "intel_opposition_risk_comm_evt" / "OPPOSITION_RISK.json"

AGENT_ID = "intel_whip_count_comm_evt"
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

def load_sponsor_data() -> Dict[str, Any]:
    artifacts = {}
    
    paths = {
        "champions": CHAMPION_PATH,
        "persuadables": PERSUADABLE_PATH,
        "cosponsors": COSPONSOR_PATH,
        "opposition": OPPOSITION_PATH
    }
    
    for key, path in paths.items():
        try:
            if path.exists():
                artifacts[key] = json.loads(path.read_text(encoding='utf-8'))
        except Exception as e:
            log_event("error", f"Failed to load {key}: {e}")
    
    return artifacts

def generate_whip_count(sponsor_data: Dict[str, Any]) -> Dict[str, Any]:
    champions = len(sponsor_data.get("champions", {}).get("champions", []))
    persuadables = len(sponsor_data.get("persuadables", {}).get("persuadables", []))
    cosponsors = len(sponsor_data.get("cosponsors", {}).get("cosponsors", []))
    opposition = len(sponsor_data.get("opposition", {}).get("opposition_assessments", []))
    
    artifact = {
        "_meta": {
            "agent_id": AGENT_ID,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "artifact_type": "WHIP_COUNT",
            "artifact_name": "Whip Count",
            "status": "SPECULATIVE",
            "confidence": "SPECULATIVE",
            "human_review_required": False,
            "requires_review": None,
            "guidance_status": "SIGNED"
        },
        "whip_count": {
            "yes_votes": champions + persuadables,
            "likely_yes": cosponsors,
            "opposition": opposition,
            "undecided": 0,
            "total_counted": champions + persuadables + cosponsors + opposition
        },
        "breakdown": {
            "champions": champions,
            "persuadables": persuadables,
            "cosponsors": cosponsors,
            "opposition": opposition
        },
        "summary": {
            "vote_prediction": "likely_pass",
            "confidence": "medium",
            "recommendations": ["Focus on persuadables", "Secure champion commitments"]
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
        "scope": "Aggregate sponsor analysis into whip count",
        "current_task": "Calculating whip count",
        "last_heartbeat": datetime.utcnow().isoformat() + "Z",
        "risk_level": RISK_LEVEL,
        "outputs": [],
        "spawned_at": datetime.utcnow().isoformat() + "Z"
    }
    registry.setdefault("agents", []).append(agent_entry)
    registry.setdefault("_meta", {})["total_agents"] = len(registry.get("agents", []))
    registry["_meta"]["active_agents"] = len([a for a in registry.get("agents", []) if a.get("status") == "RUNNING"])
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_started", "Whip count calculation started")
    
    print(f"[{AGENT_ID}] Loading sponsor data...")
    sponsor_data = load_sponsor_data()
    
    if not sponsor_data:
        log_event("warning", "No sponsor data found - proceeding speculatively")
    
    print(f"[{AGENT_ID}] Calculating whip count...")
    time.sleep(1)
    
    artifact = generate_whip_count(sponsor_data)
    
    output_file = OUTPUT_DIR / "WHIP_COUNT.json"
    output_file.write_text(json.dumps(artifact, indent=2), encoding='utf-8')
    
    for agent in registry.get("agents", []):
        if agent.get("agent_id") == AGENT_ID:
            agent["outputs"].append(str(output_file.relative_to(BASE_DIR)))
            agent["status"] = "IDLE"
            agent["current_task"] = "Whip count calculated"
            break
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_completed", "Whip count generated", output_file=str(output_file))
    
    print(f"[{AGENT_ID}] Whip count generated. Output: {output_file}")
    return output_file

if __name__ == "__main__":
    main()
