"""
Script: migrate__staff__first_class.py
Intent:
- normalize

Reads:
- data/committees/committees__snapshot.json (if exists)
- Artifact outputs from staff agents (if exist)

Writes:
- data/entities/staff__snapshot.json (first-class staff entities)

Schema:
- See schemas/entities/staff.schema.json
"""

import sys
import json
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

# Path setup
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

# Data directories
DATA_DIR = BASE_DIR / "data"
COMMITTEES_DIR = DATA_DIR / "committees"
ENTITIES_DIR = DATA_DIR / "entities"
ENTITIES_DIR.mkdir(parents=True, exist_ok=True)

# Schema path
SCHEMA_PATH = BASE_DIR / "schemas" / "entities" / "staff.schema.json"

# Artifacts directory
ARTIFACTS_DIR = BASE_DIR / "artifacts"


def load_committees_data() -> Optional[Dict[str, Any]]:
    """Load committees snapshot data."""
    committees_file = COMMITTEES_DIR / "committees__snapshot.json"
    if not committees_file.exists():
        return None
    
    try:
        with open(committees_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load committees data: {e}")
        return None


def load_staff_artifacts() -> List[Dict[str, Any]]:
    """Load staff data from agent artifacts."""
    staff_artifacts = []
    
    # Look for staff-related artifacts
    staff_patterns = [
        "**/COMMITTEE_STAFF.json",
        "**/PERSONAL_OFFICE_STAFF.json",
        "**/STAFF_INCENTIVE_MAP.json"
    ]
    
    for pattern in staff_patterns:
        for artifact_file in ARTIFACTS_DIR.glob(pattern):
            try:
                with open(artifact_file, 'r', encoding='utf-8') as f:
                    artifact = json.load(f)
                    staff_artifacts.append(artifact)
            except Exception as e:
                print(f"Warning: Failed to load artifact {artifact_file}: {e}")
    
    return staff_artifacts


def create_staff_entity_from_artifact(
    artifact_data: Dict[str, Any],
    committees_data: Optional[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """Create staff entity from artifact data."""
    # Extract staff information from artifact structure
    # This is a placeholder - actual structure depends on artifact format
    
    staff_id = str(uuid.uuid4())
    
    # Try to extract from artifact structure
    staff_contacts = artifact_data.get("staff_contacts", [])
    if not staff_contacts:
        return None
    
    # Create staff entities from contacts
    staff_entities = []
    for contact in staff_contacts:
        staff_name = contact.get("staff_name", "Unknown")
        name_parts = staff_name.split(maxsplit=1)
        first_name = name_parts[0] if name_parts else "Unknown"
        last_name = name_parts[1] if len(name_parts) > 1 else "Unknown"
        
        role = contact.get("role", "Staff")
        committee = contact.get("committee", "")
        
        # Determine entity_class based on context
        entity_class = "committee_staff"
        if "office" in role.lower() or "personal" in committee.lower():
            entity_class = "personal_office_staff"
        elif "leadership" in role.lower():
            entity_class = "leadership_staff"
        
        staff_entity = {
            "staff_id": str(uuid.uuid4()),
            "entity_type": "staff",
            "entity_class": entity_class,
            "first_name": first_name,
            "last_name": last_name,
            "active": True,
            "continuity_score": 0.5,  # Default conservative score
            "network_span": 1,
            "institutional_memory_depth": 0.0,
            "cross_chamber_connections": [],
            "current_assignments": [
                {
                    "assignment_type": "committee",
                    "entity_id": committee,
                    "role": role,
                    "assigned_at": datetime.now(timezone.utc).isoformat()
                }
            ],
            "historical_assignments": [],
            "assignment_timeline": [
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "event_type": "assignment_started",
                    "assignment_data": {
                        "committee": committee,
                        "role": role
                    }
                }
            ],
            "linked_to_member_id": None,
            "linked_to_committee_ids": [committee] if committee else [],
            "linked_to_subcommittee_ids": [],
            "email": contact.get("contact_info", {}).get("email") if isinstance(contact.get("contact_info"), dict) else None,
            "phone": contact.get("contact_info", {}).get("phone") if isinstance(contact.get("contact_info"), dict) else None
        }
        
        staff_entities.append(staff_entity)
    
    return staff_entities if staff_entities else None


def migrate_staff_data() -> Dict[str, Any]:
    """Migrate staff data to first-class entities."""
    print("[migrate__staff__first_class] Starting staff migration...")
    
    # Load source data
    committees_data = load_committees_data()
    staff_artifacts = load_staff_artifacts()
    
    # Create backup of existing data if it exists
    existing_staff_file = ENTITIES_DIR / "staff__snapshot.json"
    if existing_staff_file.exists():
        backup_file = ENTITIES_DIR / f"staff__snapshot__backup_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        print(f"[migrate__staff__first_class] Creating backup: {backup_file.name}")
        with open(existing_staff_file, 'r', encoding='utf-8') as src:
            with open(backup_file, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
    
    # Migrate staff entities
    all_staff_entities = []
    
    # Process artifacts
    for artifact in staff_artifacts:
        staff_entities = create_staff_entity_from_artifact(artifact, committees_data)
        if staff_entities:
            if isinstance(staff_entities, list):
                all_staff_entities.extend(staff_entities)
            else:
                all_staff_entities.append(staff_entities)
    
    # If no staff data found, create empty structure
    if not all_staff_entities:
        print("[migrate__staff__first_class] No existing staff data found. Creating empty structure.")
        all_staff_entities = []
    
    # Create output structure
    output_data = {
        "_meta": {
            "source_files": [
                str(COMMITTEES_DIR / "committees__snapshot.json") if committees_data else None,
                "artifacts/**/COMMITTEE_STAFF.json",
                "artifacts/**/PERSONAL_OFFICE_STAFF.json"
            ],
            "migrated_at": datetime.now(timezone.utc).isoformat(),
            "script": "migrate__staff__first_class.py",
            "schema_version": "1.0.0",
            "doctrine_version": "Congressional Network Mapping v1.0",
            "count": {
                "total_staff": len(all_staff_entities),
                "committee_staff": len([s for s in all_staff_entities if s.get("entity_class") == "committee_staff"]),
                "personal_office_staff": len([s for s in all_staff_entities if s.get("entity_class") == "personal_office_staff"]),
                "leadership_staff": len([s for s in all_staff_entities if s.get("entity_class") == "leadership_staff"])
            }
        },
        "staff": all_staff_entities
    }
    
    return output_data


def main():
    """Main migration function."""
    try:
        output_data = migrate_staff_data()
        
        # Write output
        output_file = ENTITIES_DIR / "staff__snapshot.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"[migrate__staff__first_class] Migration complete: {output_file}")
        print(f"[migrate__staff__first_class] Migrated {output_data['_meta']['count']['total_staff']} staff entities")
        return output_file
        
    except Exception as e:
        print(f"[migrate__staff__first_class] ERROR: Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)
