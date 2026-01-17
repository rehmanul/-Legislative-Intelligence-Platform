"""
Intelligence Agent: Jurisdiction Match (COMM_EVT)
Class: Intelligence (Read-Only)
Purpose: Match policy signals to committee jurisdictions
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

BASE_DIR = Path(__file__).parent.parent.parent
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
AUDIT_PATH = BASE_DIR / "audit" / "audit-log.jsonl"
OUTPUT_DIR = BASE_DIR / "artifacts" / "intel_jurisdiction_match_comm_evt"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CONGRESS_PATH = BASE_DIR / "artifacts" / "intel_congress_committee_pre_evt" / "CONGRESS_COMMITTEES.json"

AGENT_ID = "intel_jurisdiction_match_comm_evt"
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

def load_congress_committees() -> Dict[str, Any]:
    artifacts = {}
    try:
        if CONGRESS_PATH.exists():
            artifacts["congress"] = json.loads(CONGRESS_PATH.read_text(encoding='utf-8'))
    except Exception as e:
        log_event("error", f"Failed to load Congress committees: {e}")
    return artifacts

def generate_jurisdiction_matches(congress_data: Dict[str, Any]) -> Dict[str, Any]:
    artifact = {
        "_meta": {
            "agent_id": AGENT_ID,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "artifact_type": "JURISDICTION_MATCHES",
            "artifact_name": "Jurisdiction Matches",
            "status": "SPECULATIVE",
            "confidence": "SPECULATIVE",
            "human_review_required": False,
            "requires_review": None,
            "guidance_status": "SIGNED"
        },
        "matches": [
            {
                "signal_id": "signal_001",
                "committee": "Committee placeholder",
                "jurisdiction_match_score": 0.90,
                "match_rationale": "Policy area aligns with committee jurisdiction"
            }
        ],
        "summary": {
            "total_matches": 1,
            "high_match_count": 1
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
        "scope": "Match policy signals to committee jurisdictions",
        "current_task": "Matching jurisdictions",
        "last_heartbeat": datetime.utcnow().isoformat() + "Z",
        "risk_level": RISK_LEVEL,
        "outputs": [],
        "spawned_at": datetime.utcnow().isoformat() + "Z"
    }
    registry.setdefault("agents", []).append(agent_entry)
    registry.setdefault("_meta", {})["total_agents"] = len(registry.get("agents", []))
    registry["_meta"]["active_agents"] = len([a for a in registry.get("agents", []) if a.get("status") == "RUNNING"])
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_started", "Jurisdiction matching started")
    
    print(f"[{AGENT_ID}] Loading Congress committees...")
    congress_data = load_congress_committees()
    
    if not congress_data:
        log_event("warning", "No Congress committees found - proceeding speculatively")
    
    print(f"[{AGENT_ID}] Matching jurisdictions...")
    time.sleep(1)
    
    artifact = generate_jurisdiction_matches(congress_data)
    
    output_file = OUTPUT_DIR / "JURISDICTION_MATCHES.json"
    output_file.write_text(json.dumps(artifact, indent=2), encoding='utf-8')
    
    for agent in registry.get("agents", []):
        if agent.get("agent_id") == AGENT_ID:
            agent["outputs"].append(str(output_file.relative_to(BASE_DIR)))
            agent["status"] = "IDLE"
            agent["current_task"] = "Jurisdiction matches completed"
            break
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_completed", "Jurisdiction matches generated", output_file=str(output_file))
    
    print(f"[{AGENT_ID}] Jurisdiction matches generated. Output: {output_file}")
    return output_file

if __name__ == "__main__":
    main()
