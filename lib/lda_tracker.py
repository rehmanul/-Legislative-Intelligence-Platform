"""
LDA Contact Tracker - Tracks lobbying contacts for LDA reporting.
"""

import json
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional, Any
from uuid import uuid4

from app.lda_models import LobbyingContact, ContactType, ContactStatus


class LDAContactTracker:
    """Tracks lobbying contacts for LDA compliance reporting."""
    
    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize LDA contact tracker.
        
        Args:
            base_dir: Base directory for storing contact records (defaults to agent-orchestrator root)
        """
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        
        self.base_dir = Path(base_dir)
        self.contacts_dir = self.base_dir / "data" / "lda_contacts"
        self.contacts_dir.mkdir(parents=True, exist_ok=True)
        
        # Per-workflow contact files
        self.workflow_contacts_file = self.contacts_dir / "workflow_contacts.json"
        self._load_workflow_contacts()
    
    def _load_workflow_contacts(self) -> Dict[str, List[str]]:
        """Load workflow-to-contacts mapping."""
        if self.workflow_contacts_file.exists():
            try:
                return json.loads(self.workflow_contacts_file.read_text(encoding="utf-8"))
            except:
                return {}
        return {}
    
    def _save_workflow_contacts(self, mapping: Dict[str, List[str]]):
        """Save workflow-to-contacts mapping."""
        self.workflow_contacts_file.write_text(
            json.dumps(mapping, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8"
        )
    
    def record_contact(
        self,
        workflow_id: str,
        contact_date: date,
        contact_type: ContactType,
        contacted_entity: str,
        contact_topic: str,
        lobbyist_name: str,
        contacted_name: Optional[str] = None,
        contacted_office: Optional[str] = None,
        covered_official: bool = False,
        issues_codes: Optional[List[str]] = None,
        house_id: Optional[str] = None,
        senate_id: Optional[str] = None,
        agency: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> LobbyingContact:
        """
        Record a lobbying contact for LDA reporting.
        
        Args:
            workflow_id: Workflow identifier
            contact_date: Date of contact
            contact_type: Type of contact
            contacted_entity: Entity contacted
            contact_topic: Subject matter
            lobbyist_name: Name of registered lobbyist
            contacted_name: Specific person name if known
            contacted_office: Office or committee
            covered_official: Is this a covered official?
            issues_codes: LDA issue codes
            house_id: House ID if applicable
            senate_id: Senate ID if applicable
            agency: Agency if applicable
            metadata: Additional metadata
            
        Returns:
            LobbyingContact record
        """
        contact = LobbyingContact(
            contact_id=str(uuid4()),
            workflow_id=workflow_id,
            contact_date=contact_date,
            contact_type=contact_type,
            contacted_entity=contacted_entity,
            contacted_name=contacted_name,
            contacted_office=contacted_office,
            contact_topic=contact_topic,
            covered_official=covered_official,
            issues_codes=issues_codes or [],
            house_id=house_id,
            senate_id=senate_id,
            agency=agency,
            lobbyist_name=lobbyist_name,
            status=ContactStatus.NOT_REPORTED,
            metadata=metadata or {}
        )
        
        # Save contact to file
        contact_file = self.contacts_dir / f"contact_{contact.contact_id}.json"
        contact_file.write_text(
            json.dumps(contact.model_dump(mode="json"), indent=2, default=str),
            encoding="utf-8"
        )
        
        # Update workflow mapping
        mapping = self._load_workflow_contacts()
        if workflow_id not in mapping:
            mapping[workflow_id] = []
        if contact.contact_id not in mapping[workflow_id]:
            mapping[workflow_id].append(contact.contact_id)
        self._save_workflow_contacts(mapping)
        
        return contact
    
    def get_contacts_for_workflow(
        self,
        workflow_id: str,
        status: Optional[ContactStatus] = None
    ) -> List[LobbyingContact]:
        """Get all contacts for a workflow."""
        mapping = self._load_workflow_contacts()
        contact_ids = mapping.get(workflow_id, [])
        
        contacts = []
        for contact_id in contact_ids:
            contact_file = self.contacts_dir / f"contact_{contact_id}.json"
            if contact_file.exists():
                try:
                    contact_data = json.loads(contact_file.read_text(encoding="utf-8"))
                    contact = LobbyingContact(**contact_data)
                    if status is None or contact.status == status:
                        contacts.append(contact)
                except Exception as e:
                    # Skip invalid contacts
                    continue
        
        return contacts
    
    def get_contacts_for_quarter(
        self,
        year: int,
        quarter: int
    ) -> List[LobbyingContact]:
        """Get all contacts for a reporting quarter."""
        quarter_str = f"{year}-Q{quarter}"
        
        # Load all contacts
        mapping = self._load_workflow_contacts()
        all_contact_ids = []
        for contact_ids in mapping.values():
            all_contact_ids.extend(contact_ids)
        
        contacts = []
        for contact_id in set(all_contact_ids):  # Deduplicate
            contact_file = self.contacts_dir / f"contact_{contact_id}.json"
            if contact_file.exists():
                try:
                    contact_data = json.loads(contact_file.read_text(encoding="utf-8"))
                    contact = LobbyingContact(**contact_data)
                    if contact.reported_quarter == quarter_str:
                        contacts.append(contact)
                except:
                    continue
        
        return contacts
    
    def update_contact_status(
        self,
        contact_id: str,
        status: ContactStatus,
        reported_quarter: Optional[str] = None,
        reported_date: Optional[date] = None
    ) -> bool:
        """Update contact reporting status."""
        contact_file = self.contacts_dir / f"contact_{contact_id}.json"
        if not contact_file.exists():
            return False
        
        try:
            contact_data = json.loads(contact_file.read_text(encoding="utf-8"))
            contact = LobbyingContact(**contact_data)
            
            contact.status = status
            if reported_quarter:
                contact.reported_quarter = reported_quarter
            if reported_date:
                contact.reported_date = reported_date
            contact.updated_at = datetime.utcnow()
            
            contact_file.write_text(
                json.dumps(contact.model_dump(mode="json"), indent=2, default=str),
                encoding="utf-8"
            )
            return True
        except:
            return False
