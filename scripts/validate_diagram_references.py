"""
Script: validate_diagram_references.py
Intent: aggregate (validation only, no writes)
Purpose: Ensure all derived diagrams reference the master diagram

Reads:
- agent-orchestrator/**/*.mmd files

Writes:
- None (validation only, outputs to stdout)

Schema: N/A (validation script)
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
MASTER_DIAGRAM_PATH = ".userInput/agent orchestrator 1.6.mmd"
MASTER_DIAGRAM_REF_PATTERNS = [
    r"agent orchestrator 1\.6\.mmd",
    r"agent orchestrator 1\.6",
    r"master diagram",
    r"MASTER_DIAGRAM",
    r"\.userInput/agent orchestrator"
]

def find_all_diagrams() -> List[Path]:
    """Find all .mmd files in agent-orchestrator"""
    diagrams = []
    for mmd_file in BASE_DIR.rglob("*.mmd"):
        # Skip if in .git or __pycache__
        if ".git" in str(mmd_file) or "__pycache__" in str(mmd_file):
            continue
        diagrams.append(mmd_file)
    return diagrams

def check_diagram_reference(diagram_path: Path) -> Dict[str, Any]:
    """Check if diagram references master diagram"""
    result = {
        "path": str(diagram_path.relative_to(BASE_DIR)),
        "has_reference": False,
        "reference_type": None,
        "issues": []
    }
    
    try:
        content = diagram_path.read_text(encoding="utf-8")
        
        # Check for reference patterns
        for pattern in MASTER_DIAGRAM_REF_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                result["has_reference"] = True
                result["reference_type"] = "pattern_match"
                break
        
        # Check for comment-style reference
        if "%%" in content or "<!--" in content:
            comment_patterns = [
                r"%%\s*[Mm]aster\s+[Dd]iagram",
                r"<!--\s*[Mm]aster\s+[Dd]iagram",
                r"%%\s*\.userInput",
                r"<!--\s*\.userInput"
            ]
            for pattern in comment_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    result["has_reference"] = True
                    result["reference_type"] = "comment"
                    break
        
        if not result["has_reference"]:
            result["issues"].append("No master diagram reference found")
    
    except Exception as e:
        result["issues"].append(f"Error reading file: {e}")
    
    return result

def validate_diagram_references() -> Dict[str, Any]:
    """Validate all diagrams have master diagram references"""
    report = {
        "_meta": {
            "validation_timestamp": datetime.utcnow().isoformat() + "Z",
            "master_diagram": MASTER_DIAGRAM_PATH,
            "validator_version": "1.0.0"
        },
        "diagrams": [],
        "summary": {
            "total_diagrams": 0,
            "with_reference": 0,
            "missing_reference": 0,
            "errors": 0
        }
    }
    
    diagrams = find_all_diagrams()
    report["summary"]["total_diagrams"] = len(diagrams)
    
    for diagram_path in diagrams:
        check_result = check_diagram_reference(diagram_path)
        report["diagrams"].append(check_result)
        
        if check_result["issues"]:
            if "Error" in str(check_result["issues"]):
                report["summary"]["errors"] += 1
            else:
                report["summary"]["missing_reference"] += 1
        else:
            report["summary"]["with_reference"] += 1
    
    return report

if __name__ == "__main__":
    report = validate_diagram_references()
    print(json.dumps(report, indent=2))
