"""
Intelligence Agent: Congressional Calendar (COMM_EVT)
Class: Intelligence (Read-Only)
Purpose: Scrape official congressional calendars for specific markup dates, primaries, recess dates
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import requests
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).parent.parent.parent
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
AUDIT_PATH = BASE_DIR / "audit" / "audit-log.jsonl"
OUTPUT_DIR = BASE_DIR / "artifacts" / "intel_calendar"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CONGRESS_API_BASE = "https://api.congress.gov/v3"
CONGRESS_NUMBER = 119

AGENT_ID = "intel_congressional_calendar_comm_evt"
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

def scrape_congressional_calendar(chamber: str, api_key: Optional[str]) -> List[Dict[str, Any]]:
    """Scrape congressional calendar for specific dates"""
    events = []
    
    if api_key:
        try:
            url = f"{CONGRESS_API_BASE}/calendar/{chamber}"
            headers = {
                "X-API-Key": api_key,
                "Content-Type": "application/json"
            }
            params = {
                "format": "json",
                "congress": CONGRESS_NUMBER
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "calendar" in data:
                for event in data["calendar"]:
                    events.append({
                        "date": event.get("date"),
                        "type": event.get("type"),  # markup, hearing, vote, recess, etc.
                        "description": event.get("description"),
                        "committee": event.get("committee"),
                        "status": event.get("status")
                    })
            
            log_event("info", f"Fetched {len(events)} calendar events for {chamber}")
            
        except Exception as e:
            log_event("error", f"Failed to fetch calendar for {chamber}: {e}")
    else:
        # Fallback: Scrape House.gov/Senate.gov calendar pages
        try:
            if chamber == "house":
                url = "https://www.house.gov/legislative-activity"
            else:
                url = "https://www.senate.gov/legislative/calendar.htm"
            
            response = requests.get(url, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # This is a placeholder - actual scraping would parse calendar structure
            
            log_event("info", f"Scraped {chamber} calendar from {url}")
            
        except Exception as e:
            log_event("error", f"Failed to scrape {chamber} calendar: {e}")
    
    return events

def scrape_state_primary_dates() -> List[Dict[str, Any]]:
    """Scrape state election websites for primary dates"""
    primaries = []
    
    # Top 10 states by population
    states = ["CA", "TX", "FL", "NY", "PA", "IL", "OH", "GA", "NC", "MI"]
    
    for state in states:
        try:
            # This is a placeholder - actual URLs would need to be determined per state
            url = f"https://www.{state.lower()}.gov/elections"
            response = requests.get(url, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            
            # This is a placeholder - actual scraping would parse primary date information
            
            primaries.append({
                "state": state,
                "primary_date": None,  # Would extract from page
                "source_url": url,
                "scraped_at": datetime.utcnow().isoformat() + "Z"
            })
            
            time.sleep(0.5)  # Be respectful with requests
            
        except Exception as e:
            log_event("error", f"Failed to scrape {state} primary dates: {e}")
    
    return primaries

def generate_congressional_calendar(api_key: Optional[str]) -> Dict[str, Any]:
    """Generate congressional calendar artifact"""
    
    house_events = scrape_congressional_calendar("house", api_key)
    time.sleep(0.5)  # Rate limiting
    senate_events = scrape_congressional_calendar("senate", api_key)
    
    all_events = house_events + senate_events
    
    # Filter for relevant events (markups, hearings, etc.)
    relevant_events = [
        e for e in all_events 
        if e.get("type") in ["markup", "hearing", "vote"] or 
           any(keyword in e.get("description", "").lower() for keyword in ["epa", "hud", "environment", "housing"])
    ]
    
    # Scrape state primary dates
    primary_dates = scrape_state_primary_dates()
    
    artifact = {
        "_meta": {
            "agent_id": AGENT_ID,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "artifact_type": "CONGRESSIONAL_CALENDAR",
            "artifact_name": "Congressional Calendar",
            "status": "SPECULATIVE",
            "confidence": "SPECULATIVE",
            "human_review_required": False,
            "requires_review": None,
            "review_gate_status": None,
            "guidance_status": "SIGNED",
            "schema_version": "1.0.0"
        },
        "congressional_events": relevant_events,
        "primary_dates": primary_dates,
        "recess_dates": [],  # Would extract recess dates
        "session_dates": [],  # Would extract session dates
        "summary": {
            "total_events": len(relevant_events),
            "house_events": len([e for e in relevant_events if "house" in str(e.get("committee", "")).lower()]),
            "senate_events": len([e for e in relevant_events if "senate" in str(e.get("committee", "")).lower()]),
            "markup_events": len([e for e in relevant_events if e.get("type") == "markup"]),
            "primary_dates_found": len([p for p in primary_dates if p.get("primary_date")])
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
        "scope": "Scrape congressional calendars for specific markup dates and primaries",
        "current_task": "Scraping congressional calendar",
        "last_heartbeat": datetime.utcnow().isoformat() + "Z",
        "risk_level": RISK_LEVEL,
        "outputs": [],
        "spawned_at": datetime.utcnow().isoformat() + "Z"
    }
    registry.setdefault("agents", []).append(agent_entry)
    registry.setdefault("_meta", {})["total_agents"] = len(registry.get("agents", []))
    registry["_meta"]["active_agents"] = len([a for a in registry.get("agents", []) if a.get("status") == "RUNNING"])
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_started", "Congressional calendar scraping started")
    
    print(f"[{AGENT_ID}] Getting Congress.gov API key...")
    api_key = get_api_key()
    if not api_key:
        print(f"[{AGENT_ID}] WARNING: No API key - calendar data will be limited")
    
    print(f"[{AGENT_ID}] Scraping congressional calendar...")
    
    artifact = generate_congressional_calendar(api_key)
    
    output_file = OUTPUT_DIR / "CONGRESSIONAL_CALENDAR.json"
    output_file.write_text(json.dumps(artifact, indent=2, ensure_ascii=False), encoding='utf-8')
    
    for agent in registry.get("agents", []):
        if agent.get("agent_id") == AGENT_ID:
            agent["outputs"].append(str(output_file.relative_to(BASE_DIR)))
            agent["status"] = "IDLE"
            agent["current_task"] = "Congressional calendar scraped"
            break
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_completed", "Congressional calendar generated", output_file=str(output_file), event_count=len(artifact["congressional_events"]))
    
    print(f"[{AGENT_ID}] Congressional calendar generated. Output: {output_file}")
    print(f"[{AGENT_ID}] Total events: {len(artifact['congressional_events'])}")
    return output_file

if __name__ == "__main__":
    main()
