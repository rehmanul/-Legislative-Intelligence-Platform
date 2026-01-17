"""
Intelligence Agent: Industry Association Contacts (COMM_EVT)
Class: Intelligence (Read-Only)
Purpose: Scrape industry association websites (VFW, Legion, AHIP, BCBS, NMHC, NAAHQ) for legislative/government affairs contacts
"""

import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import requests
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).parent.parent.parent
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
AUDIT_PATH = BASE_DIR / "audit" / "audit-log.jsonl"
OUTPUT_DIR = BASE_DIR / "artifacts" / "intel_stakeholder_contacts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

AGENT_ID = "intel_industry_association_contacts_comm_evt"
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

def scrape_association_contacts(org_name: str, url: str, org_type: str) -> Dict[str, Any]:
    """Scrape a single association website for contact information"""
    contact = {
        "organization": org_name,
        "organization_type": org_type,
        "name": f"{org_name} Contact (Scraping)",
        "title": "Legislative Affairs Director or Government Affairs Contact",
        "email": None,
        "phone": None,
        "verified": False,
        "verification_method": "scraped",
        "verified_at": None,
        "verified_by": None,
        "source_url": url,
        "scraped_at": datetime.utcnow().isoformat() + "Z"
    }
    
    try:
        response = requests.get(url, timeout=30, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        page_text = soup.get_text()
        
        # Look for contact information patterns
        # Try to find legislative affairs or government relations pages
        links = soup.find_all('a', href=True)
        contact_pages = []
        for link in links:
            href = link.get('href', '').lower()
            text = link.get_text().lower()
            if any(term in href or term in text for term in ['legislative', 'government', 'policy', 'contact', 'staff', 'team']):
                full_url = url if href.startswith('http') else f"{url.rstrip('/')}/{href.lstrip('/')}"
                contact_pages.append(full_url)
        
        # Extract email patterns from main page
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, page_text)
        org_emails = [e for e in emails if org_name.lower().replace(' ', '') in e.lower() or any(domain in e.lower() for domain in ['vfw.org', 'legion.org', 'ahip.org', 'bcbs.com', 'nmhc.org', 'naahq.org'])]
        
        # Extract phone patterns
        phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, page_text)
        
        # Look for director or contact names
        director_patterns = [
            r'Director[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+),\s*Director',
            r'Legislative\s+Affairs[^.]*([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'Government\s+Affairs[^.]*([A-Z][a-z]+\s+[A-Z][a-z]+)'
        ]
        
        contact_name = None
        for pattern in director_patterns:
            match = re.search(pattern, page_text)
            if match:
                contact_name = match.group(1) if len(match.groups()) > 0 else None
                if contact_name and len(contact_name.split()) == 2:  # Valid name format
                    break
        
        # Update contact with found information
        if contact_name and contact_name != f"{org_name} Contact":
            contact["name"] = contact_name
        if org_emails:
            contact["email"] = org_emails[0]
        if phones:
            # Filter for DC area numbers (202) or organization-specific
            dc_phones = [p for p in phones if '(202)' in p or '202' in p.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')]
            contact["phone"] = dc_phones[0] if dc_phones else phones[0]
        
        # Try to scrape contact pages if found
        if contact_pages and (not contact["email"] or not contact_name):
            for contact_page_url in contact_pages[:2]:  # Limit to first 2 pages
                try:
                    time.sleep(1)  # Be respectful
                    contact_response = requests.get(contact_page_url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
                    if contact_response.ok:
                        contact_soup = BeautifulSoup(contact_response.content, 'html.parser')
                        contact_text = contact_soup.get_text()
                        
                        # Extract emails from contact page
                        if not contact["email"]:
                            page_emails = re.findall(email_pattern, contact_text)
                            org_page_emails = [e for e in page_emails if any(domain in e.lower() for domain in ['vfw.org', 'legion.org', 'ahip.org', 'bcbs.com', 'nmhc.org', 'naahq.org'])]
                            if org_page_emails:
                                contact["email"] = org_page_emails[0]
                        
                        # Extract names from contact page
                        if not contact_name or contact_name == f"{org_name} Contact":
                            for pattern in director_patterns:
                                match = re.search(pattern, contact_text)
                                if match:
                                    found_name = match.group(1) if len(match.groups()) > 0 else None
                                    if found_name and len(found_name.split()) == 2:
                                        contact["name"] = found_name
                                        contact_name = found_name
                                        break
                except:
                    pass  # Continue if contact page fails
        
        log_event("info", f"Scraped {org_name} contacts from {url}", name_found=bool(contact_name), email_found=bool(contact["email"]))
        
    except Exception as e:
        log_event("error", f"Failed to scrape {org_name} contacts: {e}")
        contact["name"] = f"{org_name} Contact (Scraping Failed)"
        contact["error"] = str(e)
    
    return contact

def generate_association_contacts() -> Dict[str, Any]:
    """Generate industry association contacts artifact"""
    
    # Target organizations from RISK_ASSESSMENT.json
    associations = [
        {"name": "VFW", "url": "https://www.vfw.org", "type": "ally"},
        {"name": "American Legion", "url": "https://www.legion.org", "type": "ally"},
        {"name": "AHIP", "url": "https://www.ahip.org", "type": "ally"},
        {"name": "Blue Cross Blue Shield", "url": "https://www.bcbs.com", "type": "ally"},
        {"name": "NMHC", "url": "https://www.nmhc.org", "type": "opponent"},
        {"name": "NAAHQ", "url": "https://www.naahq.org", "type": "opponent"}
    ]
    
    contacts = []
    for assoc in associations:
        contact = scrape_association_contacts(assoc["name"], assoc["url"], assoc["type"])
        contacts.append(contact)
        time.sleep(1)  # Be respectful with requests
    
    artifact = {
        "_meta": {
            "agent_id": AGENT_ID,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "artifact_type": "ASSOCIATION_CONTACTS",
            "artifact_name": "Industry Association Contacts",
            "status": "SPECULATIVE",
            "confidence": "SPECULATIVE",
            "human_review_required": False,
            "requires_review": None,
            "review_gate_status": None,
            "guidance_status": "SIGNED",
            "schema_version": "1.0.0"
        },
        "contacts": contacts,
        "summary": {
            "total_contacts": len(contacts),
            "ally_contacts": len([c for c in contacts if c.get("organization_type") == "ally"]),
            "opponent_contacts": len([c for c in contacts if c.get("organization_type") == "opponent"]),
            "verified_contacts": 0,
            "unverified_contacts": len(contacts)
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
        "scope": "Scrape industry association websites for legislative/government affairs contacts",
        "current_task": "Scraping industry association contacts",
        "last_heartbeat": datetime.utcnow().isoformat() + "Z",
        "risk_level": RISK_LEVEL,
        "outputs": [],
        "spawned_at": datetime.utcnow().isoformat() + "Z"
    }
    registry.setdefault("agents", []).append(agent_entry)
    registry.setdefault("_meta", {})["total_agents"] = len(registry.get("agents", []))
    registry["_meta"]["active_agents"] = len([a for a in registry.get("agents", []) if a.get("status") == "RUNNING"])
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_started", "Industry association contacts scraping started")
    
    print(f"[{AGENT_ID}] Scraping industry association contacts...")
    
    artifact = generate_association_contacts()
    
    output_file = OUTPUT_DIR / "ASSOCIATION_CONTACTS.json"
    output_file.write_text(json.dumps(artifact, indent=2, ensure_ascii=False), encoding='utf-8')
    
    for agent in registry.get("agents", []):
        if agent.get("agent_id") == AGENT_ID:
            agent["outputs"].append(str(output_file.relative_to(BASE_DIR)))
            agent["status"] = "IDLE"
            agent["current_task"] = "Industry association contacts scraped"
            break
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    log_event("task_completed", "Industry association contacts generated", output_file=str(output_file), contact_count=len(artifact["contacts"]))
    
    print(f"[{AGENT_ID}] Industry association contacts generated. Output: {output_file}")
    print(f"[{AGENT_ID}] Total contacts: {len(artifact['contacts'])}")
    return output_file

if __name__ == "__main__":
    main()
