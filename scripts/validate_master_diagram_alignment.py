"""
Script: validate_master_diagram_alignment.py
Intent: aggregate (validation only, no writes)
Purpose: Validate that system components align with master diagram structure

Reads:
- agent-orchestrator/AUTHORITATIVE_INVARIANTS.md
- agent-orchestrator/state/legislative-state.json
- agent-orchestrator/agents/*.py
- agent-orchestrator/app/*.py
- agent-orchestrator/review/*.json

Writes:
- None (validation only, outputs JSON report to stdout)

Schema: N/A (validation script)
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent

# Expected values from master diagram
EXPECTED_LEGISLATIVE_STATES = ["PRE_EVT", "INTRO_EVT", "COMM_EVT", "FLOOR_EVT", "FINAL_EVT", "IMPL_EVT"]
EXPECTED_SYSTEM_STATES = ["ORCH_IDLE", "ORCH_ACTIVE", "ORCH_PAUSED", "ORCH_ERROR"]
EXPECTED_AGENT_LIFECYCLE_STATES = ["SPAWN", "RUNNING", "WAITING_REVIEW", "BLOCKED", "MONITORING", "TERMINATED", "FAILED"]
EXPECTED_REVIEW_GATES = ["HR_PRE", "HR_LANG", "HR_MSG", "HR_RELEASE"]
EXPECTED_AGENT_TYPES = ["Intelligence", "Drafting", "Execution", "Learning"]

def check_legislative_state_machine() -> Dict[str, Any]:
    """Check legislative state machine matches diagram"""
    results = {
        "check": "legislative_state_machine",
        "status": "PASS",
        "details": {},
        "issues": []
    }
    
    # Check AUTHORITATIVE_INVARIANTS.md
    invariants_path = BASE_DIR / "AUTHORITATIVE_INVARIANTS.md"
    if not invariants_path.exists():
        results["status"] = "FAIL"
        results["issues"].append("AUTHORITATIVE_INVARIANTS.md not found")
        return results
    
    content = invariants_path.read_text(encoding="utf-8")
    
    # Check for all expected states
    found_states = []
    for state in EXPECTED_LEGISLATIVE_STATES:
        if state in content:
            found_states.append(state)
        else:
            results["issues"].append(f"Legislative state {state} not found in invariants")
    
    results["details"]["expected_states"] = EXPECTED_LEGISLATIVE_STATES
    results["details"]["found_states"] = found_states
    results["details"]["missing_states"] = [s for s in EXPECTED_LEGISLATIVE_STATES if s not in found_states]
    
    # Check state file
    state_file = BASE_DIR / "state" / "legislative-state.json"
    if state_file.exists():
        try:
            state_data = json.loads(state_file.read_text())
            current_state = state_data.get("current_state", "")
            if current_state not in EXPECTED_LEGISLATIVE_STATES:
                results["issues"].append(f"Current state {current_state} not in expected states")
            results["details"]["current_state"] = current_state
        except Exception as e:
            results["issues"].append(f"Error reading state file: {e}")
    
    if results["issues"]:
        results["status"] = "FAIL"
    
    return results

def check_review_gates() -> Dict[str, Any]:
    """Check human review gates exist"""
    results = {
        "check": "review_gates",
        "status": "PASS",
        "details": {},
        "issues": []
    }
    
    review_dir = BASE_DIR / "review"
    if not review_dir.exists():
        results["status"] = "FAIL"
        results["issues"].append("Review directory not found")
        return results
    
    found_gates = []
    for gate in EXPECTED_REVIEW_GATES:
        queue_file = review_dir / f"{gate}_queue.json"
        if queue_file.exists():
            found_gates.append(gate)
        else:
            results["issues"].append(f"Review gate {gate} queue file not found")
    
    results["details"]["expected_gates"] = EXPECTED_REVIEW_GATES
    results["details"]["found_gates"] = found_gates
    results["details"]["missing_gates"] = [g for g in EXPECTED_REVIEW_GATES if g not in found_gates]
    
    # Check invariants document mentions gates
    invariants_path = BASE_DIR / "AUTHORITATIVE_INVARIANTS.md"
    if invariants_path.exists():
        content = invariants_path.read_text(encoding="utf-8")
        for gate in EXPECTED_REVIEW_GATES:
            if gate not in content:
                results["issues"].append(f"Review gate {gate} not mentioned in invariants")
    
    if results["issues"]:
        results["status"] = "FAIL"
    
    return results

def check_agent_types() -> Dict[str, Any]:
    """Check agent types match diagram"""
    results = {
        "check": "agent_types",
        "status": "PASS",
        "details": {},
        "issues": []
    }
    
    agents_dir = BASE_DIR / "agents"
    if not agents_dir.exists():
        results["status"] = "FAIL"
        results["issues"].append("Agents directory not found")
        return results
    
    # Check both root agents directory and subdirectories (e.g., learning/)
    agent_files = list(agents_dir.glob("*.py")) + list(agents_dir.rglob("learning/*.py"))
    found_types = set()
    agent_type_patterns = {
        "Intelligence": r"intel_",
        "Drafting": r"draft_",
        "Execution": r"execution_",
        "Learning": r"learning_"
    }
    
    for agent_file in agent_files:
        filename = agent_file.name
        for agent_type, pattern in agent_type_patterns.items():
            if re.search(pattern, filename):
                found_types.add(agent_type)
                break
    
    results["details"]["expected_types"] = EXPECTED_AGENT_TYPES
    results["details"]["found_types"] = list(found_types)
    results["details"]["missing_types"] = [t for t in EXPECTED_AGENT_TYPES if t not in found_types]
    results["details"]["agent_count"] = len(agent_files)
    
    # Check agent files for AGENT_TYPE constant
    for agent_file in agent_files[:5]:  # Sample first 5
        try:
            content = agent_file.read_text(encoding="utf-8")
            for agent_type in EXPECTED_AGENT_TYPES:
                if f'AGENT_TYPE = "{agent_type}"' in content or f"AGENT_TYPE = '{agent_type}'" in content:
                    break
        except Exception:
            pass
    
    if results["details"]["missing_types"]:
        results["status"] = "WARN"
        results["issues"].append(f"Missing agent types: {', '.join(results['details']['missing_types'])}")
    
    return results

def check_ai_service_layer() -> Dict[str, Any]:
    """Check AI service layer components exist"""
    results = {
        "check": "ai_service_layer",
        "status": "PASS",
        "details": {},
        "issues": []
    }
    
    # Check for app directory (API layer)
    app_dir = BASE_DIR / "app"
    if not app_dir.exists():
        results["status"] = "FAIL"
        results["issues"].append("App directory not found (API layer)")
        return results
    
    # Check for key API files
    expected_api_files = ["main.py", "routes.py"]
    found_files = []
    for filename in expected_api_files:
        if (app_dir / filename).exists():
            found_files.append(filename)
        else:
            results["issues"].append(f"API file {filename} not found")
    
    results["details"]["expected_files"] = expected_api_files
    results["details"]["found_files"] = found_files
    
    # Check for execution routes
    if (app_dir / "execution_routes.py").exists():
        results["details"]["execution_routes"] = True
    else:
        results["issues"].append("Execution routes not found")
    
    if results["issues"]:
        results["status"] = "WARN"
    
    return results

def check_memory_learning_systems() -> Dict[str, Any]:
    """Check memory & learning systems are present"""
    results = {
        "check": "memory_learning_systems",
        "status": "PASS",
        "details": {},
        "issues": []
    }
    
    # Check for audit log (evidence store)
    audit_path = BASE_DIR / "audit" / "audit-log.jsonl"
    if audit_path.exists():
        results["details"]["audit_log"] = True
    else:
        results["issues"].append("Audit log not found")
    
    # Check for registry (tactic performance)
    registry_path = BASE_DIR / "registry" / "agent-registry.json"
    if registry_path.exists():
        results["details"]["agent_registry"] = True
    else:
        results["issues"].append("Agent registry not found")
    
    # Check for learning agents (in root and subdirectories)
    agents_dir = BASE_DIR / "agents"
    learning_agents = list(agents_dir.glob("learning_*.py")) + list(agents_dir.rglob("learning/*.py"))
    results["details"]["learning_agent_count"] = len(learning_agents)
    
    if not learning_agents:
        results["issues"].append("No learning agents found")
    
    if results["issues"]:
        results["status"] = "WARN"
    
    return results

def check_execution_loop() -> Dict[str, Any]:
    """Check execution loop components exist"""
    results = {
        "check": "execution_loop",
        "status": "PASS",
        "details": {},
        "issues": []
    }
    
    # Check for execution directory
    execution_dir = BASE_DIR / "execution"
    if execution_dir.exists():
        results["details"]["execution_directory"] = True
        execution_files = list(execution_dir.glob("*.py"))
        results["details"]["execution_files"] = len(execution_files)
    else:
        results["issues"].append("Execution directory not found")
    
    # Check for execution agents
    agents_dir = BASE_DIR / "agents"
    execution_agents = list(agents_dir.glob("execution_*.py"))
    results["details"]["execution_agent_count"] = len(execution_agents)
    
    if not execution_agents:
        results["issues"].append("No execution agents found")
    
    if results["issues"]:
        results["status"] = "WARN"
    
    return results

def validate_master_diagram_alignment() -> Dict[str, Any]:
    """Run all alignment checks"""
    report = {
        "_meta": {
            "validation_timestamp": datetime.utcnow().isoformat() + "Z",
            "master_diagram": ".userInput/agent orchestrator 1.6.mmd",
            "validator_version": "1.0.0"
        },
        "checks": [],
        "summary": {
            "total_checks": 0,
            "passed": 0,
            "warnings": 0,
            "failed": 0
        }
    }
    
    checks = [
        check_legislative_state_machine(),
        check_review_gates(),
        check_agent_types(),
        check_ai_service_layer(),
        check_memory_learning_systems(),
        check_execution_loop()
    ]
    
    for check_result in checks:
        report["checks"].append(check_result)
        report["summary"]["total_checks"] += 1
        if check_result["status"] == "PASS":
            report["summary"]["passed"] += 1
        elif check_result["status"] == "WARN":
            report["summary"]["warnings"] += 1
        else:
            report["summary"]["failed"] += 1
    
    return report

if __name__ == "__main__":
    report = validate_master_diagram_alignment()
    print(json.dumps(report, indent=2))
