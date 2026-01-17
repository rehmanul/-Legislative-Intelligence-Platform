"""
Execution Dashboard - Real-time execution status view.

Displays:
- Pending approvals
- Execution history
- Contact management
- Channel status
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

BASE_DIR = Path(__file__).parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from execution.approval_manager import get_approval_manager
from execution.monitor import get_monitor
from execution.contact_manager import get_contact_manager
from execution.channel import get_channel_registry
from execution.models import ExecutionStatus, ChannelType


def get_dashboard_data(workflow_id: Optional[str] = None) -> Dict:
    """
    Get dashboard data for execution system.
    
    Args:
        workflow_id: Optional workflow ID filter
        
    Returns:
        Dictionary with dashboard data
    """
    approval_manager = get_approval_manager()
    monitor = get_monitor()
    contact_manager = get_contact_manager()
    channel_registry = get_channel_registry()
    
    # Get pending approvals
    pending = approval_manager.get_pending_approvals(workflow_id=workflow_id)
    
    # Get recent activity
    recent_activities = monitor.get_activity_log(workflow_id=workflow_id, limit=50)
    
    # Get contacts
    if workflow_id:
        contacts = contact_manager.get_contacts_by_workflow(workflow_id)
    else:
        contacts = list(contact_manager._contacts.values())
    
    # Count executions by status
    status_counts = {
        "pending": len([a for a in recent_activities if a.status == ExecutionStatus.PENDING]),
        "approved": len([a for a in recent_activities if a.status == ExecutionStatus.APPROVED]),
        "executed": len([a for a in recent_activities if a.status == ExecutionStatus.EXECUTED]),
        "failed": len([a for a in recent_activities if a.status == ExecutionStatus.FAILED]),
        "rejected": len([a for a in recent_activities if a.status == ExecutionStatus.REJECTED])
    }
    
    # Count by channel type
    channel_counts = {}
    for channel_type in ChannelType:
        channel_counts[channel_type.value] = channel_registry.has_channel(channel_type)
    
    return {
        "timestamp": datetime.now().isoformat(),
        "workflow_id": workflow_id,
        "pending_approvals": {
            "total": len(pending),
            "approvals": [
                {
                    "execution_id": a.execution_id,
                    "action_type": a.action_type.value,
                    "target": a.target,
                    "review_gate": a.review_gate,
                    "created_at": a.created_at.isoformat() if isinstance(a.created_at, datetime) else str(a.created_at),
                    "content_preview": a.content_preview[:100] + "..." if len(a.content_preview) > 100 else a.content_preview
                }
                for a in pending
            ]
        },
        "execution_status": {
            "counts": status_counts,
            "recent_activities": [
                {
                    "activity_id": a.activity_id,
                    "execution_id": a.execution_id,
                    "event_type": a.event_type,
                    "timestamp": a.timestamp.isoformat() if isinstance(a.timestamp, datetime) else str(a.timestamp),
                    "status": a.status.value,
                    "message": a.message
                }
                for a in recent_activities[:20]
            ]
        },
        "contacts": {
            "total": len(contacts),
            "recent": [
                {
                    "contact_id": c.get("contact_id"),
                    "name": c.get("name"),
                    "email": c.get("email"),
                    "last_contacted": c.get("last_contacted"),
                    "stakeholder_type": c.get("stakeholder_type")
                }
                for c in contacts[-10:]
            ]
        },
        "channels": {
            "available": channel_counts,
            "registered": sum(1 for v in channel_counts.values() if v)
        }
    }


def print_dashboard(workflow_id: Optional[str] = None):
    """
    Print execution dashboard to console.
    
    Args:
        workflow_id: Optional workflow ID filter
    """
    data = get_dashboard_data(workflow_id)
    
    print("=" * 80)
    print("EXECUTION DASHBOARD")
    print("=" * 80)
    print(f"Timestamp: {data['timestamp']}")
    if workflow_id:
        print(f"Workflow: {workflow_id}")
    print()
    
    # Pending Approvals
    print("PENDING APPROVALS")
    print("-" * 80)
    pending = data["pending_approvals"]
    print(f"Total: {pending['total']}")
    if pending['total'] > 0:
        for approval in pending['approvals']:
            print(f"  - {approval['execution_id'][:8]}... | {approval['action_type']} -> {approval['target']}")
            print(f"    Gate: {approval['review_gate']} | Created: {approval['created_at']}")
    print()
    
    # Execution Status
    print("EXECUTION STATUS")
    print("-" * 80)
    status = data["execution_status"]
    counts = status["counts"]
    print(f"Pending: {counts['pending']} | Approved: {counts['approved']} | Executed: {counts['executed']} | Failed: {counts['failed']} | Rejected: {counts['rejected']}")
    print()
    
    # Recent Activities
    print("RECENT ACTIVITIES")
    print("-" * 80)
    for activity in status["recent_activities"][:10]:
        print(f"  - {activity['event_type']} | {activity['status']} | {activity['message'][:60]}")
    print()
    
    # Contacts
    print("CONTACTS")
    print("-" * 80)
    contacts = data["contacts"]
    print(f"Total: {contacts['total']}")
    for contact in contacts["recent"]:
        last_contacted = contact.get("last_contacted") or "Never"
        print(f"  - {contact.get('name', 'Unknown')} ({contact.get('email', 'No email')}) | Last: {last_contacted}")
    print()
    
    # Channels
    print("AVAILABLE CHANNELS")
    print("-" * 80)
    channels = data["channels"]
    print(f"Registered: {channels['registered']}")
    for channel_type, available in channels["available"].items():
        status_icon = "[OK]" if available else "[X]"
        print(f"  {status_icon} {channel_type}")
    print()
    
    print("=" * 80)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Execution Dashboard")
    parser.add_argument("--workflow-id", type=str, help="Filter by workflow ID")
    args = parser.parse_args()
    
    print_dashboard(workflow_id=args.workflow_id)
