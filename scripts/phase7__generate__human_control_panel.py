"""
Script: phase7__generate__human_control_panel.py
Intent: snapshot
Generates human control panel specification for Phase 7
"""

import json
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_SPEC = DATA_DIR / "human_control_panel_spec.json"


def generate_control_panel_spec():
    """Generate human control panel specification"""
    spec = {
        "_meta": {
            "generated_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "phase": 7,
            "name": "Human Control Panel Design"
        },
        "control_panel_sections": {
            "items_awaiting_approval": {
                "description": "Items requiring human review and approval",
                "display_fields": [
                    "artifact_id",
                    "artifact_name",
                    "artifact_type",
                    "review_gate",
                    "submitted_at",
                    "agent_id",
                    "urgency_level",
                    "estimated_review_time"
                ],
                "grouping": [
                    "By review gate (HR_PRE, HR_LANG, HR_MSG, HR_RELEASE)",
                    "By urgency (high, medium, low)",
                    "By age (oldest first)"
                ],
                "actions": [
                    "Approve",
                    "Reject",
                    "Request modifications",
                    "View full artifact",
                    "Compare with previous versions"
                ]
            },
            "agents_currently_running": {
                "description": "Active agents and their status",
                "display_fields": [
                    "agent_id",
                    "agent_type",
                    "status",
                    "current_task",
                    "progress_percentage",
                    "started_at",
                    "last_heartbeat",
                    "estimated_completion"
                ],
                "grouping": [
                    "By status (RUNNING, WAITING_REVIEW, BLOCKED)",
                    "By agent type (Intelligence, Drafting, Execution, Learning)",
                    "By legislative state"
                ],
                "actions": [
                    "View agent logs",
                    "Terminate agent",
                    "View agent output",
                    "View agent dependencies"
                ]
            },
            "blocked_states": {
                "description": "States where workflow is blocked",
                "display_fields": [
                    "blocking_condition",
                    "blocked_state",
                    "blocking_agent_id",
                    "missing_dependency",
                    "blocked_since",
                    "resolution_options"
                ],
                "grouping": [
                    "By blocking condition type",
                    "By legislative state",
                    "By severity"
                ],
                "actions": [
                    "View blocking details",
                    "Override block (if authorized)",
                    "Provide missing dependency",
                    "Terminate blocking agent"
                ]
            },
            "system_status_overview": {
                "description": "High-level system status",
                "display_fields": [
                    "current_legislative_state",
                    "total_active_agents",
                    "total_pending_reviews",
                    "total_blocked_items",
                    "system_health",
                    "last_state_advancement"
                ],
                "indicators": [
                    "Green: System operating normally",
                    "Yellow: Some items need attention",
                    "Red: Critical issues requiring immediate action"
                ]
            }
        },
        "notification_rules": {
            "immediate_notification": {
                "triggers": [
                    "Critical blocking condition",
                    "High-risk artifact submitted",
                    "Agent execution failure",
                    "State advancement opportunity"
                ],
                "channels": [
                    "Dashboard alerts",
                    "Email (optional)",
                    "Desktop notification (optional)"
                ]
            },
            "batch_notification": {
                "triggers": [
                    "Daily summary",
                    "Weekly report",
                    "Multiple items pending review"
                ],
                "channels": [
                    "Dashboard summary",
                    "Email digest"
                ]
            },
            "notification_preferences": {
                "user_configurable": True,
                "default_urgency_threshold": "medium"
            }
        },
        "override_authority": {
            "human_can": [
                {
                    "action": "Force agent termination",
                    "use_case": "Agent stuck or behaving incorrectly",
                    "confirmation_required": True
                },
                {
                    "action": "Override blocking conditions",
                    "use_case": "Provide missing dependency or bypass non-critical block",
                    "confirmation_required": True,
                    "audit_logged": True
                },
                {
                    "action": "Advance legislative state",
                    "use_case": "State advancement after all gates approved",
                    "confirmation_required": True,
                    "audit_logged": True
                },
                {
                    "action": "Modify agent parameters",
                    "use_case": "Adjust agent behavior or configuration",
                    "confirmation_required": False,
                    "audit_logged": True
                }
            ],
            "human_cannot": [
                "Bypass safety constraints",
                "Skip required review gates (except override)",
                "Execute external actions without approval (for execution agents)"
            ]
        },
        "control_panel_layout": {
            "primary_view": "Dashboard with tabs for each section",
            "secondary_views": [
                "Agent detail view",
                "Artifact review view",
                "System health view",
                "Audit log view"
            ],
            "navigation": {
                "type": "Tab-based with breadcrumbs",
                "quick_access": [
                    "Pending reviews",
                    "Active agents",
                    "System status"
                ]
            }
        }
    }
    return spec


def main():
    """Generate Phase 7 output file"""
    spec = generate_control_panel_spec()
    OUTPUT_SPEC.write_text(json.dumps(spec, indent=2), encoding='utf-8')
    print(f"Generated {OUTPUT_SPEC.name}")
    print("Phase 7 output generated successfully")


if __name__ == "__main__":
    main()
