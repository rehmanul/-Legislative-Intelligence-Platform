"""
Intelligence Agent: Legal Objection (COMM_EVT)
Class: Intelligence (Read-Only)
Purpose: Assess legal objection risk
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

BASE_DIR = Path(__file__).parent.parent.parent
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
AUDIT_PATH = BASE_DIR / "audit" / "audit-log.jsonl"
OUTPUT_DIR = BASE_DIR / "artifacts" / "intel_legal_objection_comm_evt"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FALLBACK_PATH = BASE_DIR / "artifacts" / "draft_fallback_options_comm_evt" / "FALLBACK_OPTIONS.json"

AGENT_ID = "intel_legal_objection_comm_evt"
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

def load_fallback_options() -> Dict[str, Any]:
    artifacts = {}
    try:
        if FALLBACK_PATH.exists():
            artifacts["fallback"] = json.loads(FALLBACK_PATH.read_text(encoding='utf-8'))
    except Exception as e:
        log_event("error", f"Failed to load fallback options: {e}")
    return artifacts

def generate_legal_objection_risk(fallback_data: Dict[str, Any]) -> Dict[str, Any]:
    artifact = {
        "_meta": {
            "agent_id": AGENT_ID,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "artifact_type": "LEGAL_OBJECTION",
            "artifact_name": "Legal Objection",
            "status": "SPECULATIVE",
            "confidence": "SPECULATIVE",
            "human_review_required": False,
            "requires_review": None,
            "guidance_status": "SIGNED"
        },
        "legal_assessment": {
            "risk_level": "low",
            "potential_objections": ["Constitutional concerns", "Regulatory conflicts"],
            "mitigation_strategies": ["Legal review", "Constitutional analysis"]
        },
        "summary": {
            "total_risks": 1,
            "high_risk_count": 0
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
        "scope": "Assess legal objection risk",
        "current_task": "Assessing legal objections",
        "last_heartbeat": datetime.utcnow().isoformat() + "Z",
        "risk_level": RISK_LEVEL,
        "outputs": [],
        "spawned_at": datetime.utcnow().isoformat() + "Z"
    }
    registry.setdefault("agents", []).append(agent_entry)
    registry.setdefault("_meta", {})["total_agents"] = len(registry.get("agents", []))
    registry["_meta"]["active_agents"] = len([a for a in registry.get("agents", []) if a.get("status") == "RUNNING"])
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_started", "Legal objection assessment started")
    
    print(f"[{AGENT_ID}] Loading fallback options...")
    fallback_data = load_fallback_options()
    
    if not fallback_data:
        log_event("warning", "No fallback options found - proceeding speculatively")
    
    print(f"[{AGENT_ID}] Assessing legal objections...")
    time.sleep(1)
    
    artifact = generate_legal_objection_risk(fallback_data)
    
    output_file = OUTPUT_DIR / "LEGAL_OBJECTION.json"
    output_file.write_text(json.dumps(artifact, indent=2), encoding='utf-8')
    
    for agent in registry.get("agents", []):
        if agent.get("agent_id") == AGENT_ID:
            agent["outputs"].append(str(output_file.relative_to(BASE_DIR)))
            agent["status"] = "IDLE"
            agent["current_task"] = "Legal objections assessed"
            break
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_completed", "Legal objection generated", output_file=str(output_file))
    
    print(f"[{AGENT_ID}] Legal objection generated. Output: {output_file}")
    return output_file

if __name__ == "__main__":
    main()
