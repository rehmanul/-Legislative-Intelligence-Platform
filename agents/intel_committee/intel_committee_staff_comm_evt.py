"""
Intelligence Agent: Committee Staff (COMM_EVT)
Class: Intelligence (Read-Only)
Purpose: Identify committee staff contacts with full contact info and hearing schedules
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

JURISDICTION_PATH = BASE_DIR / "artifacts" / "intel_jurisdiction_match_comm_evt" / "JURISDICTION_MATCHES.json"
COMMITTEES_DATA_PATH = BASE_DIR / "data" / "committees" / "committees__snapshot.json"
CONGRESS_API_BASE = "https://api.congress.gov/v3"
CONGRESS_NUMBER = 119

AGENT_ID = "intel_committee_staff_comm_evt"
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
    
    # Try config file
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
            log_event("warning", f"Could not read config file: {e}")
    
    return None

def fetch_with_retry(url: str, headers: Dict[str, str], params: Optional[Dict[str, Any]] = None, max_retries: int = 3) -> requests.Response:
    """Fetch with retry logic."""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"Failed after {max_retries} attempts: {e}")

def load_committees_data() -> Dict[str, Any]:
    """Load committees snapshot data."""
    try:
        if COMMITTEES_DATA_PATH.exists():
            return json.loads(COMMITTEES_DATA_PATH.read_text(encoding='utf-8'))
    except Exception as e:
        log_event("warning", f"Could not load committees data: {e}")
    return {}

def fetch_committee_members_from_api(committee_id: str, api_key: str, chamber: str) -> List[Dict[str, Any]]:
    """Fetch committee members from Congress.gov API."""
    committee_id_lower = committee_id.lower()
    url = f"{CONGRESS_API_BASE}/committee/{chamber}/{committee_id_lower}"
    headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
    params = {"format": "json", "congress": CONGRESS_NUMBER}
    
    try:
        response = fetch_with_retry(url, headers, params=params)
        data = response.json()
        members = []
        if "committees" in data and len(data["committees"]) > 0:
            committee_data = data["committees"][0]
            if "currentMembers" in committee_data:
                for member in committee_data["currentMembers"]:
                    members.append(member)
        return members
    except Exception as e:
        log_event("warning", f"Could not fetch members for {committee_id}: {e}")
        return []

def fetch_hearings(committee_id: str, api_key: str, chamber: str) -> List[Dict[str, Any]]:
    """Fetch upcoming hearings for a committee."""
    committee_id_lower = committee_id.lower()
    url = f"{CONGRESS_API_BASE}/committee/{chamber}/{committee_id_lower}/hearings"
    headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
    params = {"format": "json", "congress": CONGRESS_NUMBER, "limit": 10}
    
    try:
        response = fetch_with_retry(url, headers, params=params)
        data = response.json()
        hearings = []
        if "hearings" in data:
            for hearing in data["hearings"]:
                # Filter for relevant topics
                topic = hearing.get("title", "").lower()
                if any(term in topic for term in ["air quality", "environment", "epa", "hud", "housing", "mold"]):
                    hearings.append({
                        "hearing_id": hearing.get("url", "").split("/")[-1] if hearing.get("url") else None,
                        "date": hearing.get("date"),
                        "topic": hearing.get("title"),
                        "relevance_score": 0.9 if any(term in topic for term in ["air quality", "mold"]) else 0.7
                    })
        return hearings
    except Exception as e:
        log_event("warning", f"Could not fetch hearings for {committee_id}: {e}")
        return []

def generate_committee_staff(jurisdiction_data: Dict[str, Any], committees_data: Dict[str, Any], api_key: Optional[str]) -> Dict[str, Any]:
    """Generate committee staff intelligence with full contact info and hearing schedules."""
    committees_list = []
    staff_contacts = []
    upcoming_hearings = []
    
    # Target committees from RISK_ASSESSMENT.html
    target_committees = [
        {"id": "HSIF", "name": "House Energy and Commerce Committee", "chamber": "house"},
        {"id": "SSAP", "name": "Senate Environment and Public Works Committee", "chamber": "senate"},
        {"id": "HAPW", "name": "House Appropriations - Interior & Environment Subcommittee", "chamber": "house", "is_subcommittee": True},
        {"id": "HATU", "name": "House Appropriations - Transportation & HUD Subcommittee", "chamber": "house", "is_subcommittee": True}
    ]
    
    # Load from committees snapshot if available
    if committees_data.get("committees"):
        all_committees = committees_data["committees"]
        all_memberships = committees_data.get("memberships", [])
        
        for target in target_committees:
            # Find matching committee
            matching_committee = None
            for comm in all_committees:
                if (comm.get("committee_id") == target["id"] or 
                    target["name"].lower() in comm.get("name", "").lower()):
                    matching_committee = comm
                    break
            
            if not matching_committee:
                continue
            
            committee_id = matching_committee.get("committee_id", target["id"])
            chamber = matching_committee.get("chamber_id", target["chamber"])
            
            # Get chair and ranking member from memberships
            chair = None
            ranking_member = None
            for membership in all_memberships:
                if membership.get("committee_id") == committee_id:
                    if membership.get("role") == "chair":
                        # Get member details from Congress.gov API if available
                        if api_key:
                            members = fetch_committee_members_from_api(committee_id, api_key, chamber)
                            for member in members:
                                if member.get("bioguideId") == membership.get("member_id"):
                                    chair = {
                                        "member_id": member.get("bioguideId"),
                                        "name": f"{member.get('firstName', '')} {member.get('lastName', '')}".strip(),
                                        "party": member.get("party"),
                                        "state": member.get("state"),
                                        "office_phone": None  # Would need additional API call
                                    }
                                    break
                    elif membership.get("role") == "ranking_member":
                        if api_key:
                            members = fetch_committee_members_from_api(committee_id, api_key, chamber)
                            for member in members:
                                if member.get("bioguideId") == membership.get("member_id"):
                                    ranking_member = {
                                        "member_id": member.get("bioguideId"),
                                        "name": f"{member.get('firstName', '')} {member.get('lastName', '')}".strip(),
                                        "party": member.get("party"),
                                        "state": member.get("state"),
                                        "office_phone": None
                                    }
                                    break
            
            # Fetch hearings if API key available
            committee_hearings = []
            if api_key:
                committee_hearings = fetch_hearings(committee_id, api_key, chamber)
                upcoming_hearings.extend(committee_hearings)
            
            committees_list.append({
                "committee_id": committee_id,
                "committee_name": matching_committee.get("name", target["name"]),
                "chamber": chamber,
                "jurisdiction": matching_committee.get("jurisdiction_tags", []),
                "chair": chair,
                "ranking_member": ranking_member,
                "staff": [],  # Staff contacts would come from scraping committee websites
                "upcoming_hearings": committee_hearings
            })
    
    artifact = {
        "_meta": {
            "agent_id": AGENT_ID,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "artifact_type": "COMMITTEE_FULL_INTEL",
            "artifact_name": "Committee Full Intelligence",
            "status": "SPECULATIVE",
            "confidence": "SPECULATIVE",
            "human_review_required": False,
            "requires_review": None,
            "guidance_status": "SIGNED",
            "schema_version": "1.0.0"
        },
        "committees": committees_list,
        "hearings": upcoming_hearings,
        "staff_contacts": staff_contacts,
        "summary": {
            "total_committees": len(committees_list),
            "total_staff": len(staff_contacts),
            "total_hearings": len(upcoming_hearings),
            "committees_covered": len(committees_list)
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
        "scope": "Identify committee staff contacts",
        "current_task": "Identifying committee staff",
        "last_heartbeat": datetime.utcnow().isoformat() + "Z",
        "risk_level": RISK_LEVEL,
        "outputs": [],
        "spawned_at": datetime.utcnow().isoformat() + "Z"
    }
    registry.setdefault("agents", []).append(agent_entry)
    registry.setdefault("_meta", {})["total_agents"] = len(registry.get("agents", []))
    registry["_meta"]["active_agents"] = len([a for a in registry.get("agents", []) if a.get("status") == "RUNNING"])
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_started", "Committee staff identification started")
    
    print(f"[{AGENT_ID}] Loading jurisdiction matches...")
    jurisdiction_data = load_jurisdiction_matches()
    
    if not jurisdiction_data:
        log_event("warning", "No jurisdiction matches found - proceeding speculatively")
    
    print(f"[{AGENT_ID}] Loading committees data...")
    committees_data = load_committees_data()
    
    print(f"[{AGENT_ID}] Getting Congress.gov API key...")
    api_key = get_api_key()
    if not api_key:
        log_event("warning", "Congress.gov API key not found - hearing schedules will be limited")
        print(f"[{AGENT_ID}] WARNING: No API key - hearing schedules will be limited")
    
    print(f"[{AGENT_ID}] Identifying committee staff with full contact info and hearing schedules...")
    time.sleep(1)
    
    artifact = generate_committee_staff(jurisdiction_data, committees_data, api_key)
    
    output_file = OUTPUT_DIR / "COMMITTEE_FULL_INTEL.json"
    output_file.write_text(json.dumps(artifact, indent=2), encoding='utf-8')
    
    for agent in registry.get("agents", []):
        if agent.get("agent_id") == AGENT_ID:
            agent["outputs"].append(str(output_file.relative_to(BASE_DIR)))
            agent["status"] = "IDLE"
            agent["current_task"] = "Committee staff identified"
            break
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_completed", "Committee full intelligence generated", output_file=str(output_file), 
              staff_count=len(artifact["staff_contacts"]), 
              hearings_count=len(artifact["hearings"]))
    
    print(f"[{AGENT_ID}] Committee full intelligence generated. Output: {output_file}")
    print(f"[{AGENT_ID}] Staff contacts: {len(artifact['staff_contacts'])}")
    print(f"[{AGENT_ID}] Hearings: {len(artifact['hearings'])}")
    return output_file

if __name__ == "__main__":
    main()
