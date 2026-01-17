"""
Intelligence Agent: Hearing Schedule Monitor (COMM_EVT)
Class: Intelligence (Read-Only)
Purpose: Monitor Congress.gov hearings API for relevant hearings (EPA, HUD, air quality, housing, environmental)
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
OUTPUT_DIR = BASE_DIR / "artifacts" / "intel_committee"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CONGRESS_API_BASE = "https://api.congress.gov/v3"
CONGRESS_NUMBER = 119

AGENT_ID = "intel_hearing_schedule_monitor_comm_evt"
AGENT_TYPE = "Intelligence"
RISK_LEVEL = "LOW"

# Keywords for filtering relevant hearings
RELEVANT_KEYWORDS = [
    "epa", "environmental protection agency", "environment",
    "hud", "housing and urban development", "housing",
    "air quality", "mold", "indoor air",
    "environmental", "health", "public health"
]

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
    """Get Congress.gov API key from environment or config file."""
    api_key = os.getenv("CONGRESS_API_KEY")
    if api_key:
        return api_key
    
    config_path = BASE_DIR / "data-sources" / "data-sources-config.json"
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if "congressional_sources" in config:
                    sources = config["congressional_sources"].get("sources", [])
                    for source in sources:
                        if source.get("name") == "CONGRESS_GOV_API":
                            return source.get("credentials")
        except Exception as e:
            log_event("error", f"Could not read config file: {e}")
    
    return None

def calculate_relevance_score(hearing: Dict[str, Any]) -> float:
    """Calculate relevance score based on keyword matching"""
    title = hearing.get("title", "").lower()
    description = hearing.get("description", "").lower()
    text = f"{title} {description}"
    
    matches = sum(1 for keyword in RELEVANT_KEYWORDS if keyword in text)
    score = min(matches / len(RELEVANT_KEYWORDS), 1.0)  # Normalize to 0-1
    
    return score

def fetch_hearings(api_key: str, chamber: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Fetch hearings from Congress.gov API"""
    hearings = []
    
    if not api_key:
        log_event("warning", "No API key - cannot fetch hearings")
        return hearings
    
    try:
        url = f"{CONGRESS_API_BASE}/hearing/{chamber}"
        headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
        params = {
            "format": "json",
            "congress": CONGRESS_NUMBER,
            "limit": limit
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if "hearings" in data:
            for hearing in data["hearings"]:
                # Filter for relevant topics
                relevance_score = calculate_relevance_score(hearing)
                if relevance_score > 0.1:  # At least some relevance
                    hearings.append({
                        "hearing_id": hearing.get("hearingId"),
                        "title": hearing.get("title"),
                        "date": hearing.get("date"),
                        "time": hearing.get("time"),
                        "location": hearing.get("location"),
                        "committee": hearing.get("committee"),
                        "witnesses": hearing.get("witnesses", []),
                        "url": hearing.get("url"),
                        "relevance_score": relevance_score,
                        "relevance_level": "high" if relevance_score > 0.5 else "medium" if relevance_score > 0.2 else "low"
                    })
        
        log_event("info", f"Fetched {len(hearings)} relevant hearings for {chamber}")
        
    except Exception as e:
        log_event("error", f"Failed to fetch hearings for {chamber}: {e}")
    
    return hearings

def identify_witness_affiliation(witnesses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Identify opposition/allies from witness lists"""
    allies = []
    opponents = []
    neutral = []
    
    # Keywords for identifying affiliations
    ally_keywords = ["veteran", "health insurance", "epa", "hud", "public health"]
    opponent_keywords = ["property management", "real estate", "housing association", "nmhc", "naa"]
    
    for witness in witnesses:
        name = witness.get("name", "").lower()
        organization = witness.get("organization", "").lower()
        text = f"{name} {organization}"
        
        if any(keyword in text for keyword in opponent_keywords):
            opponents.append(witness)
        elif any(keyword in text for keyword in ally_keywords):
            allies.append(witness)
        else:
            neutral.append(witness)
    
    return {
        "allies": allies,
        "opponents": opponents,
        "neutral": neutral
    }

def generate_hearing_schedule(api_key: Optional[str]) -> Dict[str, Any]:
    """Generate hearing schedule artifact"""
    
    all_hearings = []
    
    if api_key:
        # Fetch from both chambers
        house_hearings = fetch_hearings(api_key, "house")
        time.sleep(0.5)  # Rate limiting
        senate_hearings = fetch_hearings(api_key, "senate")
        all_hearings = house_hearings + senate_hearings
        
        # Sort by relevance score (highest first)
        all_hearings.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        # Identify witness affiliations
        for hearing in all_hearings:
            if hearing.get("witnesses"):
                affiliations = identify_witness_affiliation(hearing["witnesses"])
                hearing["witness_affiliations"] = affiliations
    else:
        log_event("warning", "No API key - generating placeholder structure")
    
    artifact = {
        "_meta": {
            "agent_id": AGENT_ID,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "artifact_type": "HEARING_SCHEDULE",
            "artifact_name": "Hearing Schedule Monitor",
            "status": "SPECULATIVE",
            "confidence": "SPECULATIVE",
            "human_review_required": False,
            "requires_review": None,
            "review_gate_status": None,
            "guidance_status": "SIGNED",
            "schema_version": "1.0.0"
        },
        "hearings": all_hearings,
        "summary": {
            "total_hearings": len(all_hearings),
            "high_relevance": len([h for h in all_hearings if h.get("relevance_level") == "high"]),
            "medium_relevance": len([h for h in all_hearings if h.get("relevance_level") == "medium"]),
            "low_relevance": len([h for h in all_hearings if h.get("relevance_level") == "low"]),
            "upcoming_hearings": len([h for h in all_hearings if h.get("date")])  # Would filter by future dates
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
        "scope": "Monitor Congress.gov hearings API for relevant hearings",
        "current_task": "Monitoring hearing schedules",
        "last_heartbeat": datetime.utcnow().isoformat() + "Z",
        "risk_level": RISK_LEVEL,
        "outputs": [],
        "spawned_at": datetime.utcnow().isoformat() + "Z"
    }
    registry.setdefault("agents", []).append(agent_entry)
    registry.setdefault("_meta", {})["total_agents"] = len(registry.get("agents", []))
    registry["_meta"]["active_agents"] = len([a for a in registry.get("agents", []) if a.get("status") == "RUNNING"])
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_started", "Hearing schedule monitoring started")
    
    print(f"[{AGENT_ID}] Getting Congress.gov API key...")
    api_key = get_api_key()
    if not api_key:
        print(f"[{AGENT_ID}] WARNING: No API key - hearing schedules will be limited")
    
    print(f"[{AGENT_ID}] Monitoring hearing schedules...")
    
    artifact = generate_hearing_schedule(api_key)
    
    output_file = OUTPUT_DIR / "HEARING_SCHEDULE.json"
    output_file.write_text(json.dumps(artifact, indent=2, ensure_ascii=False), encoding='utf-8')
    
    for agent in registry.get("agents", []):
        if agent.get("agent_id") == AGENT_ID:
            agent["outputs"].append(str(output_file.relative_to(BASE_DIR)))
            agent["status"] = "IDLE"
            agent["current_task"] = "Hearing schedules monitored"
            break
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_completed", "Hearing schedule generated", output_file=str(output_file), hearing_count=len(artifact["hearings"]))
    
    print(f"[{AGENT_ID}] Hearing schedule generated. Output: {output_file}")
    print(f"[{AGENT_ID}] Total hearings: {len(artifact['hearings'])}")
    return output_file

if __name__ == "__main__":
    main()
