"""
Script: validate_component_mapping.py
Intent: aggregate (validation only, no writes)
Purpose: Verify code components map to master diagram elements

Reads:
- agent-orchestrator/agents/*.py
- agent-orchestrator/app/*.py
- agent-orchestrator/state/*.json
- agent-orchestrator/AUTHORITATIVE_INVARIANTS.md

Writes:
- None (validation only, outputs JSON report to stdout)

Schema: N/A (validation script)
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Set
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent

# Master diagram component mappings
MASTER_DIAGRAM_COMPONENTS = {
    "legislative_spine": {
        "states": ["PRE_EVT", "INTRO_EVT", "COMM_EVT", "FLOOR_EVT", "FINAL_EVT", "IMPL_EVT"],
        "expected_files": ["state/legislative-state.json", "AUTHORITATIVE_INVARIANTS.md"]
    },
    "ai_service_layer": {
        "components": ["multi-source ingestion", "contextual retrieval", "feature extraction", "draft generation", "strategy generation", "impact scoring", "risk scoring"],
        "expected_files": ["app/main.py", "app/routes.py"]
    },
    "human_review_gates": {
        "gates": ["HR_PRE", "HR_LANG", "HR_MSG", "HR_RELEASE"],
        "expected_files": ["review/HR_PRE_queue.json", "review/HR_LANG_queue.json", "review/HR_MSG_queue.json", "review/HR_RELEASE_queue.json"]
    },
    "agent_types": {
        "types": ["Intelligence", "Drafting", "Execution", "Learning"],
        "expected_patterns": {
            "Intelligence": r"intel_.*\.py",
            "Drafting": r"draft_.*\.py",
            "Execution": r"execution_.*\.py",
            "Learning": r"learning_.*\.py"
        }
    },
    "memory_learning": {
        "components": ["evidence store", "tactic performance", "narrative effectiveness", "legislative outcomes", "causal attribution"],
        "expected_files": ["audit/audit-log.jsonl", "registry/agent-registry.json"]
    },
    "execution_loop": {
        "components": ["strategy decomposition", "tactical planning", "tactic execution", "live monitoring", "tactical retuning"],
        "expected_files": ["execution/"]
    }
}

def map_legislative_spine() -> Dict[str, Any]:
    """Map legislative spine to state machine implementation"""
    result = {
        "component": "legislative_spine",
        "status": "PASS",
        "mappings": [],
        "issues": []
    }
    
    # Check state file
    state_file = BASE_DIR / "state" / "legislative-state.json"
    if state_file.exists():
        try:
            state_data = json.loads(state_file.read_text())
            current_state = state_data.get("current_state", "")
            result["mappings"].append({
                "diagram_element": "Legislative State Machine",
                "code_location": "state/legislative-state.json",
                "implementation": f"Current state: {current_state}",
                "status": "FOUND"
            })
        except Exception as e:
            result["issues"].append(f"Error reading state file: {e}")
            result["status"] = "FAIL"
    else:
        result["issues"].append("State file not found")
        result["status"] = "FAIL"
    
    # Check invariants
    invariants = BASE_DIR / "AUTHORITATIVE_INVARIANTS.md"
    if invariants.exists():
        result["mappings"].append({
            "diagram_element": "State Machine Definition",
            "code_location": "AUTHORITATIVE_INVARIANTS.md",
            "implementation": "State definitions and transitions",
            "status": "FOUND"
        })
    else:
        result["issues"].append("AUTHORITATIVE_INVARIANTS.md not found")
        result["status"] = "FAIL"
    
    return result

def map_agent_types() -> Dict[str, Any]:
    """Map agent types to agent files"""
    result = {
        "component": "agent_types",
        "status": "PASS",
        "mappings": [],
        "issues": []
    }
    
    agents_dir = BASE_DIR / "agents"
    if not agents_dir.exists():
        result["status"] = "FAIL"
        result["issues"].append("Agents directory not found")
        return result
    
    # Check both root agents directory and subdirectories (e.g., learning/)
    agent_files = list(agents_dir.glob("*.py")) + list(agents_dir.rglob("learning/*.py"))
    type_counts = {
        "Intelligence": 0,
        "Drafting": 0,
        "Execution": 0,
        "Learning": 0
    }
    
    for agent_file in agent_files:
        filename = agent_file.name
        if filename.startswith("intel_"):
            type_counts["Intelligence"] += 1
        elif filename.startswith("draft_"):
            type_counts["Drafting"] += 1
        elif filename.startswith("execution_"):
            type_counts["Execution"] += 1
        elif filename.startswith("learning_"):
            type_counts["Learning"] += 1
    
    for agent_type, count in type_counts.items():
        result["mappings"].append({
            "diagram_element": f"{agent_type} Agents",
            "code_location": f"agents/{agent_type.lower()}_*.py",
            "implementation": f"{count} agent files found",
            "status": "FOUND" if count > 0 else "MISSING"
        })
        if count == 0:
            result["issues"].append(f"No {agent_type} agents found")
            result["status"] = "WARN"
    
    return result

def map_review_gates() -> Dict[str, Any]:
    """Map human review gates to review system"""
    result = {
        "component": "human_review_gates",
        "status": "PASS",
        "mappings": [],
        "issues": []
    }
    
    review_dir = BASE_DIR / "review"
    if not review_dir.exists():
        result["status"] = "FAIL"
        result["issues"].append("Review directory not found")
        return result
    
    gates = ["HR_PRE", "HR_LANG", "HR_MSG", "HR_RELEASE"]
    for gate in gates:
        queue_file = review_dir / f"{gate}_queue.json"
        if queue_file.exists():
            result["mappings"].append({
                "diagram_element": f"{gate} Review Gate",
                "code_location": f"review/{gate}_queue.json",
                "implementation": "Review queue file",
                "status": "FOUND"
            })
        else:
            result["mappings"].append({
                "diagram_element": f"{gate} Review Gate",
                "code_location": f"review/{gate}_queue.json",
                "implementation": "Review queue file",
                "status": "MISSING"
            })
            result["issues"].append(f"{gate} queue file not found")
            result["status"] = "WARN"
    
    return result

def map_ai_service_layer() -> Dict[str, Any]:
    """Map AI service layer to code modules"""
    result = {
        "component": "ai_service_layer",
        "status": "PASS",
        "mappings": [],
        "issues": []
    }
    
    app_dir = BASE_DIR / "app"
    if not app_dir.exists():
        result["status"] = "FAIL"
        result["issues"].append("App directory not found")
        return result
    
    # Check for main API files
    api_files = {
        "main.py": "Main API application",
        "routes.py": "Core API routes",
        "execution_routes.py": "Execution API routes",
        "policy_routes.py": "Policy artifact routes"
    }
    
    for filename, description in api_files.items():
        file_path = app_dir / filename
        if file_path.exists():
            result["mappings"].append({
                "diagram_element": "AI Service Layer",
                "code_location": f"app/{filename}",
                "implementation": description,
                "status": "FOUND"
            })
        else:
            result["mappings"].append({
                "diagram_element": "AI Service Layer",
                "code_location": f"app/{filename}",
                "implementation": description,
                "status": "MISSING"
            })
            if filename in ["main.py", "routes.py"]:
                result["issues"].append(f"Required API file {filename} not found")
                result["status"] = "FAIL"
    
    return result

def map_memory_learning() -> Dict[str, Any]:
    """Map memory & learning systems to data storage"""
    result = {
        "component": "memory_learning",
        "status": "PASS",
        "mappings": [],
        "issues": []
    }
    
    # Check audit log (evidence store)
    audit_path = BASE_DIR / "audit" / "audit-log.jsonl"
    if audit_path.exists():
        result["mappings"].append({
            "diagram_element": "Evidence Store",
            "code_location": "audit/audit-log.jsonl",
            "implementation": "Audit log for evidence tracking",
            "status": "FOUND"
        })
    else:
        result["issues"].append("Audit log not found")
        result["status"] = "WARN"
    
    # Check registry (tactic performance)
    registry_path = BASE_DIR / "registry" / "agent-registry.json"
    if registry_path.exists():
        result["mappings"].append({
            "diagram_element": "Tactic Performance History",
            "code_location": "registry/agent-registry.json",
            "implementation": "Agent registry for performance tracking",
            "status": "FOUND"
        })
    else:
        result["issues"].append("Agent registry not found")
        result["status"] = "WARN"
    
    return result

def map_execution_loop() -> Dict[str, Any]:
    """Map execution loop to execution engine"""
    result = {
        "component": "execution_loop",
        "status": "PASS",
        "mappings": [],
        "issues": []
    }
    
    execution_dir = BASE_DIR / "execution"
    if execution_dir.exists():
        execution_files = list(execution_dir.glob("*.py"))
        result["mappings"].append({
            "diagram_element": "Execution Loop",
            "code_location": "execution/",
            "implementation": f"{len(execution_files)} execution files",
            "status": "FOUND"
        })
    else:
        result["issues"].append("Execution directory not found")
        result["status"] = "WARN"
    
    # Check execution agents (in root and subdirectories)
    agents_dir = BASE_DIR / "agents"
    execution_agents = list(agents_dir.glob("execution_*.py")) + list(agents_dir.rglob("execution/*.py"))
    result["mappings"].append({
        "diagram_element": "Tactic Execution Engine",
        "code_location": "agents/execution_*.py",
        "implementation": f"{len(execution_agents)} execution agents",
        "status": "FOUND" if execution_agents else "MISSING"
    })
    
    if not execution_agents:
        result["issues"].append("No execution agents found")
        result["status"] = "WARN"
    
    return result

def validate_component_mapping() -> Dict[str, Any]:
    """Run all component mapping validations"""
    report = {
        "_meta": {
            "validation_timestamp": datetime.utcnow().isoformat() + "Z",
            "master_diagram": ".userInput/agent orchestrator 1.6.mmd",
            "validator_version": "1.0.0"
        },
        "mappings": [],
        "summary": {
            "total_components": 0,
            "mapped": 0,
            "warnings": 0,
            "failures": 0
        }
    }
    
    mapping_functions = [
        map_legislative_spine,
        map_agent_types,
        map_review_gates,
        map_ai_service_layer,
        map_memory_learning,
        map_execution_loop
    ]
    
    for mapping_func in mapping_functions:
        mapping_result = mapping_func()
        report["mappings"].append(mapping_result)
        report["summary"]["total_components"] += 1
        
        if mapping_result["status"] == "PASS":
            report["summary"]["mapped"] += 1
        elif mapping_result["status"] == "WARN":
            report["summary"]["warnings"] += 1
        else:
            report["summary"]["failures"] += 1
    
    return report

if __name__ == "__main__":
    report = validate_component_mapping()
    print(json.dumps(report, indent=2))
