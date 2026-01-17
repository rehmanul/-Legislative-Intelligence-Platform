"""
LDA Integration Helper - Provides automatic LDA contact tracking for execution agents.
"""

from datetime import date
from pathlib import Path
from typing import Optional, Dict, Any
import sys

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from lib.lda_tracker import LDAContactTracker
from app.lda_models import ContactType, ContactStatus


def record_lda_contact(
    workflow_id: str,
    contact_date: date,
    contact_type: str,
    contacted_entity: str,
    contact_topic: str,
    lobbyist_name: str,
    contacted_name: Optional[str] = None,
    contacted_office: Optional[str] = None,
    covered_official: bool = False,
    metadata: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """
    Record a lobbying contact for LDA reporting.
    
    This function should be called by execution agents when they make contact
    with covered officials (Members of Congress, congressional staff, etc.).
    
    Args:
        workflow_id: Workflow identifier
        contact_date: Date of contact
        contact_type: Type of contact ("email", "phone_call", "meeting", "letter")
        contacted_entity: Entity contacted (e.g., "Member of Congress", "Congressional Staff")
        contact_topic: Subject matter of contact
        lobbyist_name: Name of registered lobbyist making contact
        contacted_name: Specific person name if known
        contacted_office: Office or committee
        covered_official: Is this a covered official under LDA?
        metadata: Additional metadata
        
    Returns:
        Contact ID if recorded, None if not recordable
    """
    try:
        # Determine if contact type is valid
        contact_type_enum = None
        if contact_type.lower() in ["email", "e-mail"]:
            contact_type_enum = ContactType.EMAIL
        elif contact_type.lower() in ["phone", "phone_call", "call"]:
            contact_type_enum = ContactType.PHONE_CALL
        elif contact_type.lower() in ["meeting", "in_person"]:
            contact_type_enum = ContactType.MEETING
        elif contact_type.lower() in ["letter", "mail"]:
            contact_type_enum = ContactType.LETTER
        else:
            contact_type_enum = ContactType.OTHER
        
        # Initialize tracker
        tracker = LDAContactTracker()
        
        # Record contact
        contact = tracker.record_contact(
            workflow_id=workflow_id,
            contact_date=contact_date,
            contact_type=contact_type_enum,
            contacted_entity=contacted_entity,
            contacted_name=contacted_name,
            contacted_office=contacted_office,
            contact_topic=contact_topic,
            lobbyist_name=lobbyist_name,
            covered_official=covered_official,
            metadata=metadata or {}
        )
        
        return contact.contact_id
        
    except Exception as e:
        # Log error but don't block execution
        print(f"[LDA Integration] Failed to record contact: {e}")
        return None


def is_covered_official(contacted_entity: str, contacted_office: Optional[str] = None) -> bool:
    """
    Determine if contacted entity is a covered official under LDA.
    
    Covered officials include:
    - Members of Congress
    - Congressional staff
    - Executive branch officials above certain levels
    - Senior White House staff
    
    Args:
        contacted_entity: Entity contacted
        contacted_office: Office or committee
        
    Returns:
        True if likely a covered official, False otherwise
    """
    entity_lower = contacted_entity.lower()
    office_lower = (contacted_office or "").lower()
    
    # Covered official indicators
    covered_indicators = [
        "member of congress",
        "representative",
        "senator",
        "congressional staff",
        "committee staff",
        "house staff",
        "senate staff",
        "personal office staff",
        "executive office",
        "white house",
        "cabinet",
        "deputy secretary",
        "assistant secretary",
        "under secretary"
    ]
    
    # Check entity and office
    for indicator in covered_indicators:
        if indicator in entity_lower or indicator in office_lower:
            return True
    
    return False
