"""
Script: phase4__generate__github_structure.py
Intent: snapshot
Generates GitHub structure plan JSON files for Phase 4
"""

import json
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Output files
OUTPUT_STRUCTURE = DATA_DIR / "github_structure.json"
OUTPUT_NAMING = DATA_DIR / "artifact_naming.json"
OUTPUT_ACCESS = DATA_DIR / "access_control.json"
OUTPUT_VERSION = DATA_DIR / "version_control_rules.json"


def generate_github_structure():
    """Generate GitHub repository structure definition"""
    structure = {
        "_meta": {
            "generated_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "phase": 4,
            "name": "GitHub Structure Plan"
        },
        "repository_layout": {
            "agent-orchestrator/": {
                "agents/": {
                    "description": "Agent Python scripts (Cursor-owned)",
                    "ownership": "cursor",
                    "permissions": ["read", "write", "version_control"]
                },
                "app/": {
                    "description": "FastAPI backend (Cursor-owned)",
                    "ownership": "cursor",
                    "permissions": ["read", "write", "version_control"]
                },
                "dashboards/": {
                    "description": "Dashboard HTML files (Cursor-owned)",
                    "ownership": "cursor",
                    "permissions": ["read", "write", "version_control"]
                },
                "artifacts/": {
                    "description": "Agent-generated artifacts (Agent-written)",
                    "ownership": "agent",
                    "permissions": ["write"],
                    "subdirectories": {
                        "{agent_id}/": "Per-agent artifact directories",
                        "review/": "Review queue artifacts"
                    }
                },
                "state/": {
                    "description": "Legislative state files (Agent-written, Human-reviewed)",
                    "ownership": "human_reviewed",
                    "permissions": ["read", "write", "approve"]
                },
                "registry/": {
                    "description": "Agent registry (Agent-written)",
                    "ownership": "agent",
                    "permissions": ["write"]
                },
                "data/": {
                    "description": "Workflow data (Phase 0-2 outputs)",
                    "ownership": "agent",
                    "permissions": ["read", "write"]
                },
                "schemas/": {
                    "description": "JSON schemas (Cursor-owned)",
                    "ownership": "cursor",
                    "permissions": ["read", "write", "version_control"]
                },
                "scripts/": {
                    "description": "Utility scripts (Cursor-owned)",
                    "ownership": "cursor",
                    "permissions": ["read", "write", "version_control"]
                }
            }
        }
    }
    return structure


def generate_artifact_naming():
    """Generate artifact naming conventions"""
    naming = {
        "_meta": {
            "generated_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "phase": 4
        },
        "conventions": {
            "agent_artifacts": {
                "pattern": "{ARTIFACT_TYPE}.json",
                "examples": [
                    "PRE_CONCEPT.json",
                    "INTRO_WHITEPAPER.json",
                    "COMM_LANG.json"
                ],
                "location": "artifacts/{agent_id}/"
            },
            "state_files": {
                "files": [
                    "legislative-state.json",
                    "agent-registry.json"
                ],
                "location": "state/ or registry/"
            },
            "dashboard_state": {
                "file": "cockpit_state.out.json",
                "location": "dashboards/"
            },
            "review_queues": {
                "pattern": "{GATE_ID}_queue.json",
                "examples": [
                    "HR_PRE_queue.json",
                    "HR_LANG_queue.json",
                    "HR_MSG_queue.json",
                    "HR_RELEASE_queue.json"
                ],
                "location": "artifacts/review/"
            },
            "workflow_data": {
                "pattern": "{data_type}.json",
                "examples": [
                    "workflow_nodes.json",
                    "dashboard_sections.json",
                    "agent_inventory.json"
                ],
                "location": "data/"
            }
        }
    }
    return naming


def generate_access_control():
    """Generate access control rules"""
    access = {
        "_meta": {
            "generated_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "phase": 4
        },
        "read_only_for_agents": {
            "directories": [
                "schemas/",
                "agents/"
            ],
            "description": "Agents can read but cannot modify",
            "rationale": "Prevent agents from modifying code or schemas"
        },
        "writable_by_agents": {
            "directories": [
                "artifacts/",
                "state/",
                "registry/",
                "data/"
            ],
            "description": "Agents can create and write files",
            "constraints": [
                "Agents write to their own artifact directories",
                "State files require backup before overwrite",
                "Registry updates are append-only where possible"
            ]
        },
        "human_only": {
            "activities": [
                "State advancement decisions",
                "Review approvals",
                "Artifact approval/rejection",
                "Code merges"
            ],
            "description": "Only humans can perform these actions",
            "rationale": "Maintain human oversight and control"
        }
    }
    return access


def generate_version_control_rules():
    """Generate version control rules"""
    version_control = {
        "_meta": {
            "generated_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "phase": 4
        },
        "committed": {
            "items": [
                "Agent scripts (*.py in agents/)",
                "Dashboard HTML files",
                "Schemas (*.json in schemas/)",
                "Documentation (*.md)",
                "Configuration files (requirements.txt, etc.)"
            ],
            "rationale": "Code and configuration should be version controlled"
        },
        "gitignored": {
            "items": [
                "Agent-generated artifacts (unless approved)",
                "State snapshots (unless canonical)",
                "Log files (*.log, *.jsonl)",
                "Temporary files",
                "__pycache__/ directories",
                "*.pyc files"
            ],
            "rationale": "Generated artifacts are temporary unless explicitly approved"
        },
        "backup_before_overwrite": {
            "files": [
                "state/legislative-state.json",
                "registry/agent-registry.json"
            ],
            "pattern": "{filename}.backup",
            "rationale": "Preserve state history before major updates"
        },
        "merge_rules": {
            "requires_approval": True,
            "approval_authority": "human",
            "conflict_resolution": "human_decision"
        }
    }
    return version_control


def main():
    """Generate all Phase 4 output files"""
    # GitHub structure
    structure = generate_github_structure()
    OUTPUT_STRUCTURE.write_text(json.dumps(structure, indent=2), encoding='utf-8')
    print(f"Generated {OUTPUT_STRUCTURE.name}")
    
    # Artifact naming
    naming = generate_artifact_naming()
    OUTPUT_NAMING.write_text(json.dumps(naming, indent=2), encoding='utf-8')
    print(f"Generated {OUTPUT_NAMING.name}")
    
    # Access control
    access = generate_access_control()
    OUTPUT_ACCESS.write_text(json.dumps(access, indent=2), encoding='utf-8')
    print(f"Generated {OUTPUT_ACCESS.name}")
    
    # Version control
    version_control = generate_version_control_rules()
    OUTPUT_VERSION.write_text(json.dumps(version_control, indent=2), encoding='utf-8')
    print(f"Generated {OUTPUT_VERSION.name}")
    
    print("Phase 4 outputs generated successfully")


if __name__ == "__main__":
    main()
