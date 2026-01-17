"""
Script: snapshot__fetch__committees.py
Intent:
- snapshot

Reads:
- Congress.gov API v3 (https://api.congress.gov/v3)
- API key from environment variable CONGRESS_API_KEY or config

Writes:
- data/committees/committees__snapshot.json

Schema:
{
  "_meta": {
    "source": "congress.gov API v3",
    "fetched_at": "ISO-8601 UTC timestamp",
    "congress": 119,
    "script": "snapshot__fetch__committees.py",
    "schema_version": "1.0.0",
    "count": {
      "chambers": 2,
      "committees": N,
      "subcommittees": M,
      "memberships": K
    }
  },
  "chambers": [
    {
      "chamber_id": "house" | "senate",
      "name": "House of Representatives" | "United States Senate",
      "abbreviation": "H" | "S"
    }
  ],
  "committees": [
    {
      "committee_id": "HASC" | "SASC" | ...,
      "chamber_id": "house" | "senate",
      "name": "Full Committee Name",
      "abbreviation": "HASC",
      "type": "standing" | "select" | "joint" | "special",
      "jurisdiction_tags": ["defense", "military"],
      "parent_committee_id": null,
      "congress": 119,
      "established_at": "ISO-8601 UTC",
      "disbanded_at": null | "ISO-8601 UTC"
    }
  ],
  "subcommittees": [
    {
      "subcommittee_id": "HASC-MPIF",
      "committee_id": "HASC",
      "chamber_id": "house",
      "name": "Subcommittee Name",
      "abbreviation": "MPIF",
      "jurisdiction_tags": ["military-construction"],
      "congress": 119
    }
  ],
  "memberships": [
    {
      "membership_id": "uuid",
      "member_id": "bioguide_id",
      "committee_id": "HASC" | null,
      "subcommittee_id": "HASC-MPIF" | null,
      "role": "member" | "chair" | "ranking_member" | "vice_chair",
      "party": "R" | "D" | "I",
      "congress": 119,
      "appointed_at": "ISO-8601 UTC",
      "removed_at": null
    }
  ]
}
"""

import sys
import json
import os
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import requests
from urllib.parse import urljoin

# Path setup
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

# Data directory
DATA_DIR = BASE_DIR / "data"
COMMITTEES_DIR = DATA_DIR / "committees"
COMMITTEES_DIR.mkdir(parents=True, exist_ok=True)

# Congress.gov API configuration
CONGRESS_API_BASE = "https://api.congress.gov/v3"
CONGRESS_NUMBER = 119  # Current Congress (2025-2026)

# Rate limiting
RATE_LIMIT_DELAY = 0.5  # Seconds between API calls to avoid rate limits
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"  # Set TEST_MODE=true to limit to 3 committees per chamber

# Get API key from environment or config
def get_api_key() -> Optional[str]:
    """Get Congress.gov API key from environment or config file."""
    # Try environment variable first
    api_key = os.getenv("CONGRESS_API_KEY")
    if api_key:
        return api_key
    
    # Try config file
    config_path = BASE_DIR / "data-sources" / "data-sources-config.json"
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Check for congressional_sources section
                if "congressional_sources" in config:
                    sources = config["congressional_sources"].get("sources", [])
                    for source in sources:
                        if source.get("name") == "CONGRESS_GOV_API":
                            return source.get("credentials")
        except Exception as e:
            print(f"[WARNING] Could not read config file: {e}")
    
    return None


def fetch_with_retry(url: str, headers: Dict[str, str], params: Optional[Dict[str, Any]] = None, max_retries: int = 3) -> requests.Response:
    """Fetch with exponential backoff retry and rate limiting."""
    import time
    
    # Rate limiting delay
    time.sleep(RATE_LIMIT_DELAY)
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            return response
        except requests.HTTPError as e:
            # Check for rate limit errors
            if response.status_code == 429:
                wait_time = 60  # Wait 60 seconds for rate limit
                print(f"[RATE_LIMIT] Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            elif attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 1s, 2s, 4s
                print(f"[RETRY] Attempt {attempt + 1}/{max_retries} failed (HTTP {response.status_code}), waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            else:
                print(f"[ERROR] HTTP {response.status_code}: {response.text[:200]}")
                raise RuntimeError(
                    f"Failed to fetch {url} after {max_retries} attempts: HTTP {response.status_code}"
                ) from e
        except (requests.RequestException, requests.Timeout) as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 1s, 2s, 4s
                print(f"[RETRY] Attempt {attempt + 1}/{max_retries} failed, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            else:
                raise RuntimeError(
                    f"Failed to fetch {url} after {max_retries} attempts: {e}"
                ) from e


def fetch_committees(chamber: str, api_key: str, congress: int) -> List[Dict[str, Any]]:
    """Fetch committees for a chamber."""
    url = f"{CONGRESS_API_BASE}/committee/{chamber}"
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
    params = {
        "format": "json",
        "limit": 250,  # Max per page
        "congress": congress  # Add congress parameter
    }
    
    print(f"[INFO] Fetching {chamber} committees (Congress {congress})...")
    try:
        response = fetch_with_retry(url, headers, params=params)
        data = response.json()
        
        committees = []
        if "committees" in data:
            for committee in data["committees"]:
                committees.append(committee)
        else:
            print(f"[WARNING] No 'committees' key in response. Response keys: {list(data.keys())}")
            if "message" in data:
                print(f"[WARNING] API message: {data['message']}")
        
        # Debug: Print first committee structure
        if len(committees) > 0:
            print(f"[DEBUG] First committee keys: {list(committees[0].keys())}")
            print(f"[DEBUG] First committee systemCode: {committees[0].get('systemCode', 'N/A')}")
        
        print(f"[SUCCESS] Fetched {len(committees)} {chamber} committees")
        return committees
    except Exception as e:
        print(f"[ERROR] Failed to fetch {chamber} committees: {e}")
        import traceback
        print(f"[DEBUG] Error details:\n{traceback.format_exc()}")
        return []


def fetch_subcommittees(committee_id: str, api_key: str, congress: int, chamber: str) -> List[Dict[str, Any]]:
    """Fetch subcommittees for a committee."""
    # Congress.gov API structure: /committee/{chamber}/{committeeId}/subcommittees
    # Use lowercase committee_id for API
    committee_id_lower = committee_id.lower()
    
    url = f"{CONGRESS_API_BASE}/committee/{chamber}/{committee_id_lower}/subcommittees"
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
    params = {
        "format": "json",
        "congress": congress  # Add congress parameter
    }
    
    try:
        response = fetch_with_retry(url, headers, params=params)
        data = response.json()
        
        subcommittees = []
        if "subcommittees" in data:
            for subcommittee in data["subcommittees"]:
                subcommittees.append(subcommittee)
        
        return subcommittees
    except RuntimeError as e:
        # 404 errors are normal for committees without subcommittees
        if "404" in str(e):
            return []  # No subcommittees - this is normal
        raise  # Re-raise other errors
    except Exception as e:
        # Other errors - log but don't fail
        return []


def fetch_committee_members(committee_id: str, api_key: str, congress: int, chamber: str) -> List[Dict[str, Any]]:
    """Fetch members for a committee."""
    # Use lowercase committee_id for API
    committee_id_lower = committee_id.lower()
    
    url = f"{CONGRESS_API_BASE}/committee/{chamber}/{committee_id_lower}"
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
    params = {
        "format": "json",
        "congress": congress  # Add congress parameter
    }
    
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
    except RuntimeError as e:
        # 404 errors are normal for some committees
        if "404" in str(e):
            return []  # Committee not found or no members - this is normal
        raise  # Re-raise other errors
    except Exception as e:
        print(f"[WARNING] Could not fetch members for {committee_id}: {e}")
        return []


def normalize_committee(committee: Dict[str, Any], chamber: str) -> Dict[str, Any]:
    """Normalize committee data to schema."""
    # Get committee ID from systemCode (API returns lowercase)
    system_code = committee.get("systemCode", "")
    committee_id = system_code.upper() if system_code else "UNKNOWN"
    name = committee.get("name", "")
    abbreviation = committee_id
    
    # Check if this is a subcommittee - check parent field
    parent_data = committee.get("parent")
    is_subcommittee = "subcommittee" in name.lower() or parent_data is not None
    parent_committee_id = None
    
    if parent_data:
        # Parent can be a dict or a string
        if isinstance(parent_data, dict):
            parent_committee_id = parent_data.get("systemCode", "").upper()
        elif isinstance(parent_data, str):
            parent_committee_id = parent_data.upper()
    
    # Determine type from committeeTypeCode if available
    committee_type = "standing"  # Default
    type_code = committee.get("committeeTypeCode", "").lower()
    if "select" in type_code or "select" in name.lower():
        committee_type = "select"
    elif "joint" in type_code or "joint" in name.lower():
        committee_type = "joint"
    elif "special" in type_code or "special" in name.lower():
        committee_type = "special"
    
    return {
        "committee_id": committee_id,
        "chamber_id": chamber,
        "name": name,
        "abbreviation": abbreviation,
        "type": committee_type,
        "jurisdiction_tags": [],  # Would need additional data source
        "parent_committee_id": parent_committee_id,
        "is_subcommittee": is_subcommittee,
        "congress": CONGRESS_NUMBER,
        "established_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "disbanded_at": None
    }


def normalize_membership(member: Dict[str, Any], committee_id: str, subcommittee_id: Optional[str] = None) -> Dict[str, Any]:
    """Normalize membership data to schema."""
    bioguide_id = member.get("bioguideId", "")
    role = member.get("title", "member").lower()
    
    # Normalize role
    if "chair" in role:
        normalized_role = "chair"
    elif "ranking" in role:
        normalized_role = "ranking_member"
    elif "vice" in role:
        normalized_role = "vice_chair"
    else:
        normalized_role = "member"
    
    party = member.get("party", "").upper()
    if party not in ["R", "D", "I"]:
        party = "I"  # Default to Independent if unknown
    
    return {
        "membership_id": str(uuid.uuid4()),
        "member_id": bioguide_id,
        "committee_id": committee_id if not subcommittee_id else None,
        "subcommittee_id": subcommittee_id,
        "role": normalized_role,
        "party": party,
        "congress": CONGRESS_NUMBER,
        "appointed_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "removed_at": None
    }


def main():
    """Main execution."""
    print("=" * 60)
    print("Congressional Committee Roster Fetch")
    print("=" * 60)
    
    # Get API key
    api_key = get_api_key()
    if not api_key:
        print("[ERROR] Congress.gov API key not found.")
        print("[INFO] Set CONGRESS_API_KEY environment variable or configure in data-sources-config.json")
        print("[INFO] Get API key from: https://api.congress.gov/sign-up")
        return None
    
    print(f"[INFO] Using Congress.gov API (Congress {CONGRESS_NUMBER})")
    if TEST_MODE:
        print(f"[INFO] TEST_MODE enabled - limiting to 3 committees per chamber")
    print(f"[INFO] Rate limit delay: {RATE_LIMIT_DELAY}s between calls")
    
    # Initialize data structures
    chambers = [
        {
            "chamber_id": "house",
            "name": "House of Representatives",
            "abbreviation": "H"
        },
        {
            "chamber_id": "senate",
            "name": "United States Senate",
            "abbreviation": "S"
        }
    ]
    
    all_committees = []
    all_subcommittees = []
    all_memberships = []
    
    # Fetch committees for each chamber
    for chamber in ["house", "senate"]:
        committees = fetch_committees(chamber, api_key, CONGRESS_NUMBER)
        
        # Test mode: limit to first 3 committees
        if TEST_MODE and len(committees) > 3:
            print(f"[TEST_MODE] Limiting to first 3 committees (found {len(committees)} total)")
            committees = committees[:3]
        
        # Filter out subcommittees from main list (they'll be fetched separately)
        main_committees = []
        subcommittees_from_list = []
        
        for committee_raw in committees:
            normalized = normalize_committee(committee_raw, chamber)
            if normalized.get("is_subcommittee"):
                subcommittees_from_list.append(normalized)
            else:
                main_committees.append(normalized)
        
        print(f"[INFO] Found {len(main_committees)} main committees and {len(subcommittees_from_list)} subcommittees in list")
        
        # Add subcommittees found in main list
        for subcommittee in subcommittees_from_list:
            all_subcommittees.append({
                "subcommittee_id": subcommittee["committee_id"],
                "committee_id": subcommittee.get("parent_committee_id") or "UNKNOWN",
                "chamber_id": chamber,
                "name": subcommittee["name"],
                "abbreviation": subcommittee["abbreviation"],
                "jurisdiction_tags": [],
                "congress": CONGRESS_NUMBER
            })
        
        # Test mode: limit to first 3 main committees
        if TEST_MODE and len(main_committees) > 3:
            print(f"[TEST_MODE] Limiting to first 3 main committees (found {len(main_committees)} total)")
            main_committees = main_committees[:3]
        
        total_committees = len(main_committees)
        for idx, committee in enumerate(main_committees, 1):
            # Progress indicator
            print(f"[PROGRESS] Processing {chamber} committee {idx}/{total_committees}: {committee.get('name', 'Unknown')[:50]}")
            
            try:
                all_committees.append(committee)
                committee_id = committee["committee_id"]
                
                # Skip if committee_id is invalid
                if committee_id == "UNKNOWN" or not committee_id:
                    print(f"  [WARNING] Skipping committee with invalid ID: {committee.get('name')}")
                    continue
                
                # Fetch subcommittees (only for main committees)
                # Note: Many committees don't have subcommittees - 404 is normal
                subcommittees_raw = fetch_subcommittees(committee_id, api_key, CONGRESS_NUMBER, chamber)
                if subcommittees_raw:
                    print(f"  [INFO] Found {len(subcommittees_raw)} subcommittees for {committee_id}")
                for subcommittee_raw in subcommittees_raw:
                    subcommittee_system_code = subcommittee_raw.get('systemCode', '').upper()
                    subcommittee_id = f"{committee_id}-{subcommittee_system_code}" if subcommittee_system_code else f"{committee_id}-SUB"
                    subcommittee = {
                        "subcommittee_id": subcommittee_id,
                        "committee_id": committee_id,
                        "chamber_id": chamber,
                        "name": subcommittee_raw.get("name", ""),
                        "abbreviation": subcommittee_system_code,
                        "jurisdiction_tags": [],
                        "congress": CONGRESS_NUMBER
                    }
                    all_subcommittees.append(subcommittee)
                
                # Fetch members
                members = fetch_committee_members(committee_id, api_key, CONGRESS_NUMBER, chamber)
                if members:
                    print(f"  [INFO] Found {len(members)} members for {committee_id}")
                else:
                    print(f"  [INFO] No members found for {committee_id} (may be inactive or API limitation)")
                for member in members:
                    membership = normalize_membership(member, committee_id)
                    all_memberships.append(membership)
                    
                    # Also add subcommittee memberships if applicable
                    # (This would require additional API calls per subcommittee)
            except Exception as e:
                print(f"[ERROR] Failed to process committee {committee.get('name', 'Unknown')}: {e}")
                import traceback
                print(f"[DEBUG] Error details:\n{traceback.format_exc()}")
                continue  # Continue with next committee
    
    # Sort for deterministic output
    all_committees = sorted(all_committees, key=lambda x: (x["chamber_id"], x["committee_id"]))
    all_subcommittees = sorted(all_subcommittees, key=lambda x: (x["committee_id"], x["subcommittee_id"]))
    all_memberships = sorted(all_memberships, key=lambda x: (x["committee_id"] or "", x["subcommittee_id"] or "", x["member_id"]))
    
    # Create output structure
    output_data = {
        "_meta": {
            "source": "congress.gov API v3",
            "fetched_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "congress": CONGRESS_NUMBER,
            "script": "snapshot__fetch__committees.py",
            "schema_version": "1.0.0",
            "count": {
                "chambers": len(chambers),
                "committees": len(all_committees),
                "subcommittees": len(all_subcommittees),
                "memberships": len(all_memberships)
            }
        },
        "chambers": chambers,
        "committees": all_committees,
        "subcommittees": all_subcommittees,
        "memberships": all_memberships
    }
    
    # Write output
    output_file = COMMITTEES_DIR / "committees__snapshot.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Fetch Complete")
    print("=" * 60)
    print(f"Chambers: {len(chambers)}")
    print(f"Committees: {len(all_committees)}")
    print(f"Subcommittees: {len(all_subcommittees)}")
    print(f"Memberships: {len(all_memberships)}")
    print(f"\nOutput: {output_file}")
    
    return output_file


if __name__ == "__main__":
    result = main()
    if result:
        print(f"\n[SUCCESS] Script completed successfully")
        sys.exit(0)
    else:
        print(f"\n[ERROR] Script failed")
        sys.exit(1)
