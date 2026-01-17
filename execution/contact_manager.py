"""
Contact Manager - Contact Storage and Retrieval.

Provides JSON-backed contact storage.
Schema exactly as specified in plan.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from uuid import uuid4

from .config import CONTACTS_FILE

logger = logging.getLogger(__name__)


class ContactManager:
    """
    Manages contact storage and retrieval.
    
    JSON-backed storage (upgradeable to CRM in Phase 2).
    Schema exactly as specified in plan.
    """
    
    def __init__(self):
        """Initialize contact manager."""
        self._contacts: Dict[str, dict] = {}
        self._load_contacts()
    
    def _load_contacts(self) -> None:
        """Load contacts from file."""
        if CONTACTS_FILE.exists():
            try:
                with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for contact in data.get("contacts", []):
                        contact_id = contact.get("contact_id")
                        if contact_id:
                            self._contacts[contact_id] = contact
                logger.info(f"Loaded {len(self._contacts)} contacts")
            except Exception as e:
                logger.error(f"Failed to load contacts: {e}")
                self._contacts = {}
    
    def _save_contacts(self) -> None:
        """Save contacts to file."""
        try:
            CONTACTS_FILE.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "_meta": {
                    "version": "1.0",
                    "updated_at": datetime.utcnow().isoformat(),
                    "count": len(self._contacts)
                },
                "contacts": list(self._contacts.values())
            }
            with open(CONTACTS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save contacts: {e}")
    
    def create_contact(
        self,
        name: str,
        email: str,
        workflow_id: str,
        role: Optional[str] = None,
        organization: Optional[str] = None,
        stakeholder_type: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> dict:
        """
        Create a new contact.
        
        Args:
            name: Contact name
            email: Email address
            workflow_id: Associated workflow
            role: Role/title (optional)
            organization: Organization (optional)
            stakeholder_type: Type (ally, opponent, neutral, etc.)
            metadata: Additional metadata (optional)
            
        Returns:
            Contact dictionary
        """
        contact_id = str(uuid4())
        
        contact = {
            "contact_id": contact_id,
            "name": name,
            "email": email,
            "role": role,
            "organization": organization,
            "workflow_id": workflow_id,
            "stakeholder_type": stakeholder_type,
            "created_at": datetime.utcnow().isoformat(),
            "last_contacted": None,
            "metadata": metadata or {}
        }
        
        self._contacts[contact_id] = contact
        self._save_contacts()
        
        logger.info(f"Created contact: {contact_id} ({name})")
        
        return contact
    
    def get_contact(self, contact_id: str) -> Optional[dict]:
        """
        Get contact by ID.
        
        Args:
            contact_id: Contact identifier
            
        Returns:
            Contact dictionary or None
        """
        return self._contacts.get(contact_id)
    
    def get_contacts_by_workflow(
        self,
        workflow_id: str
    ) -> List[dict]:
        """
        Get all contacts for a workflow.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            List of contact dictionaries
        """
        return [
            contact for contact in self._contacts.values()
            if contact.get("workflow_id") == workflow_id
        ]
    
    def get_contacts_by_stakeholder_type(
        self,
        stakeholder_type: str,
        workflow_id: Optional[str] = None
    ) -> List[dict]:
        """
        Get contacts by stakeholder type.
        
        Args:
            stakeholder_type: Type (ally, opponent, neutral, etc.)
            workflow_id: Filter by workflow (optional)
            
        Returns:
            List of contact dictionaries
        """
        contacts = [
            contact for contact in self._contacts.values()
            if contact.get("stakeholder_type") == stakeholder_type
        ]
        
        if workflow_id:
            contacts = [
                c for c in contacts
                if c.get("workflow_id") == workflow_id
            ]
        
        return contacts
    
    def update_contact(
        self,
        contact_id: str,
        **updates
    ) -> Optional[dict]:
        """
        Update contact information.
        
        Args:
            contact_id: Contact identifier
            **updates: Fields to update
            
        Returns:
            Updated contact dictionary or None if not found
        """
        contact = self._contacts.get(contact_id)
        if not contact:
            return None
        
        # Update fields
        for key, value in updates.items():
            if key in contact:
                contact[key] = value
        
        self._save_contacts()
        
        logger.info(f"Updated contact: {contact_id}")
        
        return contact
    
    def mark_contacted(
        self,
        contact_id: str,
        timestamp: Optional[datetime] = None
    ) -> Optional[dict]:
        """
        Mark contact as contacted.
        
        Args:
            contact_id: Contact identifier
            timestamp: Contact timestamp (defaults to now)
            
        Returns:
            Updated contact dictionary or None if not found
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        return self.update_contact(
            contact_id,
            last_contacted=timestamp.isoformat()
        )
    
    def delete_contact(self, contact_id: str) -> bool:
        """
        Delete a contact.
        
        Args:
            contact_id: Contact identifier
            
        Returns:
            True if deleted, False if not found
        """
        if contact_id not in self._contacts:
            return False
        
        del self._contacts[contact_id]
        self._save_contacts()
        
        logger.info(f"Deleted contact: {contact_id}")
        
        return True
    
    def search_contacts(
        self,
        query: str,
        workflow_id: Optional[str] = None
    ) -> List[dict]:
        """
        Search contacts by name, email, or organization.
        
        Args:
            query: Search query
            workflow_id: Filter by workflow (optional)
            
        Returns:
            List of matching contact dictionaries
        """
        query_lower = query.lower()
        matches = []
        
        for contact in self._contacts.values():
            if workflow_id and contact.get("workflow_id") != workflow_id:
                continue
            
            # Search in name, email, organization
            name = contact.get("name", "") or ""
            email = contact.get("email", "") or ""
            organization = contact.get("organization", "") or ""
            
            if (query_lower in name.lower() or
                query_lower in email.lower() or
                query_lower in organization.lower()):
                matches.append(contact)
        
        return matches
    
    def get_all_contacts(self) -> List[dict]:
        """
        Get all contacts.
        
        Returns:
            List of all contact dictionaries
        """
        return list(self._contacts.values())


# Global contact manager instance
_contact_manager: Optional[ContactManager] = None


def get_contact_manager() -> ContactManager:
    """
    Get global contact manager instance.
    
    Returns:
        ContactManager instance
    """
    global _contact_manager
    if _contact_manager is None:
        _contact_manager = ContactManager()
    return _contact_manager
