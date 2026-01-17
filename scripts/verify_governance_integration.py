"""
Script: Verify Governance Integration
Intent: aggregate
Reads: agents/*.py, control_plane/gate_enforcer.py
Writes: artifacts/governance_verification_report.json
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

BASE_DIR = Path(__file__).parent.parent
AGENTS_DIR = BASE_DIR / "agents"
GATE_ENFORCER_PATH = BASE_DIR / "control_plane" / "gate_enforcer.py"
OUTPUT_FILE = BASE_DIR / "artifacts" / "governance_verification_report.json"

def check_agent_governance(agent_file: Path) -> Dict[str, Any]:
    """Check if agent properly integrates governance"""
    content = agent_file.read_text(encoding='utf-8')
    agent_id = agent_file.stem
    
    checks = {
        "agent_id": agent_id,
        "has_guidance_check": "check_guidance_signed" in content,
        "has_audit_logging": "log_event" in content,
        "has_review_gate_check": False,
        "has_dependency_handling": False,
        "issues": []
    }
    
    # Check for review gate checks (HR_LANG, HR_MSG, etc.)
    if "HR_LANG" in content or "HR_MSG" in content or "HR_PRE" in content:
        checks["has_review_gate_check"] = True
    
    # Check for dependency handling
    if "exists()" in content or "load" in content.lower():
        checks["has_dependency_handling"] = True
    
    # Check for issues
    if "Execution" in content and not checks["has_review_gate_check"]:
        # Execution agents that do external actions should check review gates
        if "outreach" in content.lower() or "external" in content.lower():
            checks["issues"].append("Execution agent may perform external actions but doesn't check review gates")
    
    if "Drafting" in content:
        if "requires_review" not in content and "HR_" not in content:
            checks["issues"].append("Drafting agent doesn't declare review gate requirement")
    
    return checks

def main():
    """Verify governance integration across all agents"""
    report = {
        "_meta": {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "verification_type": "governance_integration",
            "status": "NON_AUTHORITATIVE"
        },
        "summary": {
            "total_agents_checked": 0,
            "agents_with_guidance_check": 0,
            "agents_with_audit_logging": 0,
            "agents_with_review_gates": 0,
            "agents_with_dependency_handling": 0,
            "agents_with_issues": 0
        },
        "agent_checks": [],
        "issues": []
    }
    
    # Check all agent files
    agent_files = list(AGENTS_DIR.glob("*.py"))
    agent_files.extend(list((AGENTS_DIR / "learning").glob("*.py")))
    
    for agent_file in agent_files:
        if agent_file.name.startswith("__"):
            continue
        
        checks = check_agent_governance(agent_file)
        report["agent_checks"].append(checks)
        report["summary"]["total_agents_checked"] += 1
        
        if checks["has_guidance_check"]:
            report["summary"]["agents_with_guidance_check"] += 1
        if checks["has_audit_logging"]:
            report["summary"]["agents_with_audit_logging"] += 1
        if checks["has_review_gate_check"]:
            report["summary"]["agents_with_review_gates"] += 1
        if checks["has_dependency_handling"]:
            report["summary"]["agents_with_dependency_handling"] += 1
        if checks["issues"]:
            report["summary"]["agents_with_issues"] += 1
            report["issues"].extend([f"{checks['agent_id']}: {issue}" for issue in checks["issues"]])
    
    # Check gate enforcer exists
    if GATE_ENFORCER_PATH.exists():
        report["gate_enforcer"] = {
            "exists": True,
            "path": str(GATE_ENFORCER_PATH.relative_to(BASE_DIR))
        }
    else:
        report["gate_enforcer"] = {
            "exists": False,
            "issue": "Gate enforcer not found"
        }
        report["issues"].append("Gate enforcer not found at expected path")
    
    # Write report
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(report, indent=2), encoding='utf-8')
    
    print(f"Governance verification complete")
    print(f"   Agents checked: {report['summary']['total_agents_checked']}")
    print(f"   Agents with issues: {report['summary']['agents_with_issues']}")
    if report["issues"]:
        print(f"   Issues found: {len(report['issues'])}")
        for issue in report["issues"][:5]:
            print(f"     - {issue}")
    
    return report

if __name__ == "__main__":
    main()
