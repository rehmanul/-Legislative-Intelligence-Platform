"""
Intelligence Agent: Rulemaking Timeline Tracker (COMM_EVT)
Class: Intelligence (Read-Only)
Purpose: Monitor Regulations.gov API for EPA/HUD rulemaking milestones with specific dates
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import requests

BASE_DIR = Path(__file__).parent.parent.parent
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
AUDIT_PATH = BASE_DIR / "audit" / "audit-log.jsonl"
OUTPUT_DIR = BASE_DIR / "artifacts" / "intel_rulemaking"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

REGULATIONS_API_BASE = "https://api.regulations.gov/v4"
AGENCIES = ["EPA", "HUD"]

AGENT_ID = "intel_rulemaking_timeline_tracker_comm_evt"
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

def get_api_key() -> Optional[str]:
    """Get Regulations.gov API key from environment or config file."""
    api_key = os.getenv("REGULATIONS_API_KEY")
    if api_key:
        return api_key
    
    config_path = BASE_DIR / "data-sources" / "data-sources-config.json"
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Would check for regulations.gov API key in config
        except Exception as e:
            log_event("error", f"Could not read config file: {e}")
    
    return None

def fetch_agency_dockets(agency: str, api_key: Optional[str]) -> List[Dict[str, Any]]:
    """Fetch EPA or HUD dockets from Regulations.gov API"""
    dockets = []
    
    if not api_key:
        log_event("warning", f"No API key - cannot fetch {agency} dockets")
        return dockets
    
    try:
        url = f"{REGULATIONS_API_BASE}/dockets"
        headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
        params = {
            "filter[agencyId]": agency,
            "page[size]": 20,
            "sort": "-postedDate"
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if "data" in data:
            for docket in data["data"]:
                # Filter for relevant topics (air quality, housing, indoor air)
                title = docket.get("attributes", {}).get("title", "").lower()
                if any(keyword in title for keyword in ["air quality", "indoor air", "housing", "mold", "environment"]):
                    dockets.append({
                        "docket_id": docket.get("id"),
                        "title": docket.get("attributes", {}).get("title"),
                        "agency": agency,
                        "posted_date": docket.get("attributes", {}).get("postedDate"),
                        "document_count": docket.get("attributes", {}).get("documentCount", 0),
                        "url": docket.get("attributes", {}).get("docketUrl")
                    })
        
        log_event("info", f"Fetched {len(dockets)} relevant dockets for {agency}")
        
    except Exception as e:
        log_event("error", f"Failed to fetch {agency} dockets: {e}")
    
    return dockets

def track_rulemaking_milestones(docket: Dict[str, Any], api_key: Optional[str]) -> Dict[str, Any]:
    """Track milestone dates for a rulemaking docket"""
    milestones = {
        "docket_id": docket.get("docket_id"),
        "nprm_date": None,  # Notice of Proposed Rulemaking
        "comment_period_start": None,
        "comment_period_end": None,
        "final_rule_date": None,
        "target_dates": {},  # Would extract from docket
        "delays": []  # Would detect delays by comparing actual vs target dates
    }
    
    if api_key:
        try:
            # Fetch documents for this docket to identify milestones
            url = f"{REGULATIONS_API_BASE}/documents"
            headers = {
                "X-API-Key": api_key,
                "Content-Type": "application/json"
            }
            params = {
                "filter[docketId]": docket.get("docket_id"),
                "page[size]": 50
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "data" in data:
                for doc in data["data"]:
                    doc_type = doc.get("attributes", {}).get("documentType", "").lower()
                    posted_date = doc.get("attributes", {}).get("postedDate")
                    
                    if "nprm" in doc_type or "proposed rule" in doc_type:
                        milestones["nprm_date"] = posted_date
                    elif "final rule" in doc_type:
                        milestones["final_rule_date"] = posted_date
                    elif "comment" in doc_type:
                        if not milestones["comment_period_start"]:
                            milestones["comment_period_start"] = posted_date
                        milestones["comment_period_end"] = posted_date
            
        except Exception as e:
            log_event("error", f"Failed to track milestones for docket {docket.get('docket_id')}: {e}")
    
    return milestones

def generate_rulemaking_timelines(api_key: Optional[str]) -> Dict[str, Any]:
    """Generate rulemaking timeline artifact"""
    
    all_dockets = []
    all_milestones = []
    
    for agency in AGENCIES:
        dockets = fetch_agency_dockets(agency, api_key)
        all_dockets.extend(dockets)
        time.sleep(0.5)  # Rate limiting
        
        # Track milestones for each docket
        for docket in dockets[:5]:  # Limit to 5 dockets per agency
            milestones = track_rulemaking_milestones(docket, api_key)
            all_milestones.append(milestones)
            time.sleep(0.5)  # Rate limiting
    
    # Detect delays and alerts
    alerts = []
    for milestone in all_milestones:
        if milestone.get("target_dates"):
            # Would compare actual dates vs target dates to detect delays
            pass
    
    artifact = {
        "_meta": {
            "agent_id": AGENT_ID,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "artifact_type": "RULEMAKING_TIMELINES",
            "artifact_name": "Rulemaking Timeline Tracker",
            "status": "SPECULATIVE",
            "confidence": "SPECULATIVE",
            "human_review_required": False,
            "requires_review": None,
            "review_gate_status": None,
            "guidance_status": "SIGNED",
            "schema_version": "1.0.0"
        },
        "dockets": all_dockets,
        "milestones": all_milestones,
        "alerts": alerts,
        "summary": {
            "total_dockets": len(all_dockets),
            "epa_dockets": len([d for d in all_dockets if d.get("agency") == "EPA"]),
            "hud_dockets": len([d for d in all_dockets if d.get("agency") == "HUD"]),
            "milestones_tracked": len(all_milestones),
            "alerts_count": len(alerts)
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
        "scope": "Monitor Regulations.gov API for EPA/HUD rulemaking milestones",
        "current_task": "Tracking rulemaking timelines",
        "last_heartbeat": datetime.utcnow().isoformat() + "Z",
        "risk_level": RISK_LEVEL,
        "outputs": [],
        "spawned_at": datetime.utcnow().isoformat() + "Z"
    }
    registry.setdefault("agents", []).append(agent_entry)
    registry.setdefault("_meta", {})["total_agents"] = len(registry.get("agents", []))
    registry["_meta"]["active_agents"] = len([a for a in registry.get("agents", []) if a.get("status") == "RUNNING"])
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_started", "Rulemaking timeline tracking started")
    
    print(f"[{AGENT_ID}] Getting Regulations.gov API key...")
    api_key = get_api_key()
    if not api_key:
        print(f"[{AGENT_ID}] WARNING: No API key - rulemaking timelines will be limited")
    
    print(f"[{AGENT_ID}] Tracking rulemaking timelines...")
    
    artifact = generate_rulemaking_timelines(api_key)
    
    output_file = OUTPUT_DIR / "RULEMAKING_TIMELINES.json"
    output_file.write_text(json.dumps(artifact, indent=2, ensure_ascii=False), encoding='utf-8')
    
    for agent in registry.get("agents", []):
        if agent.get("agent_id") == AGENT_ID:
            agent["outputs"].append(str(output_file.relative_to(BASE_DIR)))
            agent["status"] = "IDLE"
            agent["current_task"] = "Rulemaking timelines tracked"
            break
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_completed", "Rulemaking timelines generated", output_file=str(output_file), docket_count=len(artifact["dockets"]))
    
    print(f"[{AGENT_ID}] Rulemaking timelines generated. Output: {output_file}")
    print(f"[{AGENT_ID}] Total dockets: {len(artifact['dockets'])}")
    return output_file

if __name__ == "__main__":
    main()
