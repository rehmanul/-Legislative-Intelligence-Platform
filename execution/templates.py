"""
Email Template System - Phase 2

Basic email template generation from drafting artifacts.
Phase 2: Simple template system (Phase 3 will add Jinja2).
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def generate_email_from_briefing(
    briefing_data: Dict[str, Any],
    contact_name: Optional[str] = None,
    contact_role: Optional[str] = None,
    custom_message: Optional[str] = None
) -> Dict[str, str]:
    """
    Generate email content from committee briefing packet.
    
    Args:
        briefing_data: Committee briefing packet artifact data
        contact_name: Contact name for personalization
        contact_role: Contact role/title
        custom_message: Optional custom message to include
        
    Returns:
        Dictionary with 'subject', 'body', and optionally 'html_body'
    """
    # Extract briefing content
    summary = briefing_data.get("summary", "Committee briefing information")
    agenda_items = briefing_data.get("agenda", [])
    key_points = briefing_data.get("key_points", [])
    asks = briefing_data.get("asks", [])
    
    # Generate subject
    subject = f"Committee Briefing: {briefing_data.get('committee_name', 'Legislative Matter')}"
    
    # Generate body
    greeting = f"Dear {contact_name}," if contact_name else "Dear Colleague,"
    if contact_role:
        greeting = f"Dear {contact_name} ({contact_role})," if contact_name else f"Dear {contact_role},"
    
    body_parts = [greeting, ""]
    
    # Introduction
    body_parts.append("I wanted to share important information regarding an upcoming committee matter.")
    body_parts.append("")
    
    # Summary
    if summary:
        body_parts.append("Summary:")
        body_parts.append(summary)
        body_parts.append("")
    
    # Key points
    if key_points:
        body_parts.append("Key Points:")
        for point in key_points[:5]:  # Limit to top 5
            if isinstance(point, str):
                body_parts.append(f"  • {point}")
            elif isinstance(point, dict):
                body_parts.append(f"  • {point.get('point', str(point))}")
        body_parts.append("")
    
    # Agenda items
    if agenda_items:
        body_parts.append("Relevant Agenda Items:")
        for item in agenda_items[:3]:  # Limit to top 3
            if isinstance(item, str):
                body_parts.append(f"  • {item}")
            elif isinstance(item, dict):
                body_parts.append(f"  • {item.get('title', str(item))}")
        body_parts.append("")
    
    # Custom message
    if custom_message:
        body_parts.append(custom_message)
        body_parts.append("")
    
    # Asks/action items
    if asks:
        body_parts.append("Requested Actions:")
        for ask in asks[:3]:  # Limit to top 3
            if isinstance(ask, str):
                body_parts.append(f"  • {ask}")
            elif isinstance(ask, dict):
                body_parts.append(f"  • {ask.get('action', str(ask))}")
        body_parts.append("")
    
    # Closing
    body_parts.append("Please let me know if you have any questions or need additional information.")
    body_parts.append("")
    body_parts.append("Best regards,")
    body_parts.append("[Your Name]")
    
    body = "\n".join(body_parts)
    
    return {
        "subject": subject,
        "body": body
    }


def generate_email_from_stakeholder_map(
    stakeholder_data: Dict[str, Any],
    contact_name: Optional[str] = None
) -> Dict[str, str]:
    """
    Generate basic email from stakeholder map context.
    
    Args:
        stakeholder_data: Stakeholder map artifact data
        contact_name: Contact name for personalization
        
    Returns:
        Dictionary with 'subject' and 'body'
    """
    subject = "Legislative Update"
    
    greeting = f"Dear {contact_name}," if contact_name else "Dear Colleague,"
    
    body = f"""{greeting}

I wanted to reach out regarding an important legislative matter that may be of interest.

[Content would be generated from stakeholder map context]

Please let me know if you'd like to discuss further.

Best regards,
[Your Name]"""
    
    return {
        "subject": subject,
        "body": body
    }


def generate_simple_outreach_email(
    subject: str,
    message: str,
    contact_name: Optional[str] = None,
    contact_role: Optional[str] = None
) -> Dict[str, str]:
    """
    Generate simple outreach email.
    
    Args:
        subject: Email subject
        message: Email body message
        contact_name: Contact name for personalization
        contact_role: Contact role/title
        
    Returns:
        Dictionary with 'subject' and 'body'
    """
    greeting = f"Dear {contact_name}," if contact_name else "Dear Colleague,"
    if contact_role and contact_name:
        greeting = f"Dear {contact_name} ({contact_role}),"
    
    body = f"""{greeting}

{message}

Best regards,
[Your Name]"""
    
    return {
        "subject": subject,
        "body": body
    }
