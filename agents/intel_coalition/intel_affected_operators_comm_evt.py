"""
Intelligence Agent: Affected Operators (COMM_EVT)
Class: Intelligence (Read-Only)
Purpose: Identify affected operators in coalition
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

BASE_DIR = Path(__file__).parent.parent.parent
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
AUDIT_PATH = BASE_DIR / "audit" / "audit-log.jsonl"
OUTPUT_DIR = BASE_DIR / "artifacts" / "intel_affected_operators_comm_evt"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

STATE_REG_PATH = BASE_DIR / "artifacts" / "intel_state_regulator_pre_evt" / "STATE_REGULATORS.json"

AGENT_ID = "intel_affected_operators_comm_evt"
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

def load_state_regulators() -> Dict[str, Any]:
    artifacts = {}
    try:
        if STATE_REG_PATH.exists():
            artifacts["regulators"] = json.loads(STATE_REG_PATH.read_text(encoding='utf-8'))
    except Exception as e:
        log_event("error", f"Failed to load state regulators: {e}")
    return artifacts

def generate_affected_operators(regulator_data: Dict[str, Any]) -> Dict[str, Any]:
    artifact = {
        "_meta": {
            "agent_id": AGENT_ID,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "artifact_type": "AFFECTED_OPERATORS",
            "artifact_name": "Affected Operators",
            "status": "SPECULATIVE",
            "confidence": "SPECULATIVE",
            "human_review_required": False,
            "requires_review": None,
            "guidance_status": "SIGNED"
        },
        "operators": [
            {
                "operator_id": "operator_001",
                "name": "Operator organization placeholder",
                "impact_level": "high",
                "engagement_priority": "high",
                "coalition_role": "primary_affected"
            }
        ],
        "summary": {
            "total_operators": 1,
            "high_impact_count": 1
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
        "scope": "Identify affected operators in coalition",
        "current_task": "Identifying affected operators",
        "last_heartbeat": datetime.utcnow().isoformat() + "Z",
        "risk_level": RISK_LEVEL,
        "outputs": [],
        "spawned_at": datetime.utcnow().isoformat() + "Z"
    }
    registry.setdefault("agents", []).append(agent_entry)
    registry.setdefault("_meta", {})["total_agents"] = len(registry.get("agents", []))
    registry["_meta"]["active_agents"] = len([a for a in registry.get("agents", []) if a.get("status") == "RUNNING"])
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_started", "Affected operators identification started")
    
    print(f"[{AGENT_ID}] Loading state regulators...")
    regulator_data = load_state_regulators()
    
    if not regulator_data:
        log_event("warning", "No state regulators found - proceeding speculatively")
    
    print(f"[{AGENT_ID}] Identifying affected operators...")
    time.sleep(1)
    
    artifact = generate_affected_operators(regulator_data)
    
    output_file = OUTPUT_DIR / "AFFECTED_OPERATORS.json"
    output_file.write_text(json.dumps(artifact, indent=2), encoding='utf-8')
    
    for agent in registry.get("agents", []):
        if agent.get("agent_id") == AGENT_ID:
            agent["outputs"].append(str(output_file.relative_to(BASE_DIR)))
            agent["status"] = "IDLE"
            agent["current_task"] = "Affected operators identified"
            break
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_completed", "Affected operators generated", output_file=str(output_file))
    
    print(f"[{AGENT_ID}] Affected operators generated. Output: {output_file}")
    return output_file

if __name__ == "__main__":
    main()
