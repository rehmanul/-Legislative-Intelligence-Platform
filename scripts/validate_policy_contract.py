"""
Script: validate_policy_contract.py
Intent: aggregate (validation only, no writes)
Purpose: Validate that policy artifacts comply with READ-ONLY POLICY CONTEXT contract

Reads:
- agent-orchestrator/artifacts/policy/*.md files

Writes:
- None (validation only, outputs to stdout)

Schema: N/A (validation script)
"""

import json
from pathlib import Path
from typing import List, Dict, Tuple
import re

BASE_DIR = Path(__file__).parent.parent
POLICY_DIR = BASE_DIR / "artifacts" / "policy"
REQUIRED_HEADER_PATTERN = r"READ-ONLY POLICY CONTEXT - DO NOT EXECUTE"
REQUIRED_FILES = [
    "key_findings.md",
    "stakeholder_map.md",
    "talking_points.md",
    "action_plan.md",
    "section_priority_table.md",
    "staff_one_pager_p1.md",
    "clear_ask_matrix_p1.md",
    "README.md",
]

FORBIDDEN_PATTERNS = [
    r"def\s+\w+\s*\(",
    r"async\s+def\s+\w+\s*\(",
    r"class\s+\w+",
    r"import\s+\w+",
    r"from\s+\w+\s+import",
    r"@app\.(get|post|put|patch|delete)",
    r"agent\.(spawn|execute|run)",
    r"workflow\.(advance|execute)",
    r"EXEC_RUN",
    r"COMM_EVT",
    r"state\.advance",
]

def check_file_exists(file_path: Path) -> Tuple[bool, str]:
    """Check if file exists"""
    if file_path.exists():
        return True, "File exists"
    return False, f"File missing: {file_path.name}"

def check_contract_header(file_path: Path) -> Tuple[bool, str]:
    """Check if file has required contract header"""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # README.md doesn't need the header
        if file_path.name == "README.md":
            return True, "README.md (header not required)"
        
        # Check for required header pattern
        if re.search(REQUIRED_HEADER_PATTERN, content, re.IGNORECASE):
            # Check for HTML comment format
            if "<!--" in content and "-->" in content:
                return True, "Contract header present"
            return False, "Header pattern found but not in HTML comment format"
        
        return False, "Contract header missing"
    except Exception as e:
        return False, f"Error reading file: {str(e)}"

def check_for_executable_content(file_path: Path) -> Tuple[bool, List[str]]:
    """Check for forbidden executable patterns"""
    try:
        content = file_path.read_text(encoding='utf-8')
        violations = []
        
        # README.md is allowed to mention these patterns in explanatory context
        is_readme = file_path.name == "README.md"
        
        for pattern in FORBIDDEN_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                # For README, check if it's in a "DO NOT" or prohibition context
                if is_readme:
                    # Check if pattern appears in prohibition/explanation context
                    pattern_context = re.findall(
                        rf"(?i)(?:must\s+not|prohibited|do\s+not|forbidden|violation).*?{pattern}",
                        content,
                        re.IGNORECASE | re.DOTALL
                    )
                    if not pattern_context:
                        # Also check if it's in a code block or example
                        code_block_context = re.findall(
                            rf"```.*?{pattern}.*?```",
                            content,
                            re.IGNORECASE | re.DOTALL
                        )
                        if not code_block_context:
                            violations.append(f"Found forbidden pattern '{pattern}': {len(matches)} matches (may be in explanatory context)")
                else:
                    violations.append(f"Found forbidden pattern '{pattern}': {len(matches)} matches")
        
        if violations:
            return False, violations
        return True, []
    except Exception as e:
        return False, [f"Error checking file: {str(e)}"]

def validate_policy_directory() -> Dict:
    """Validate all policy files"""
    results = {
        "directory_exists": POLICY_DIR.exists(),
        "files_checked": [],
        "summary": {
            "total_files": 0,
            "files_exist": 0,
            "headers_valid": 0,
            "no_executable_content": 0,
            "errors": []
        }
    }
    
    if not POLICY_DIR.exists():
        results["summary"]["errors"].append(f"Policy directory not found: {POLICY_DIR}")
        return results
    
    for filename in REQUIRED_FILES:
        file_path = POLICY_DIR / filename
        file_result = {
            "filename": filename,
            "exists": False,
            "header_valid": False,
            "no_executable": False,
            "errors": []
        }
        
        results["summary"]["total_files"] += 1
        
        # Check existence
        exists, msg = check_file_exists(file_path)
        file_result["exists"] = exists
        if exists:
            results["summary"]["files_exist"] += 1
        else:
            file_result["errors"].append(msg)
        
        # Check header (if file exists)
        if exists:
            header_valid, msg = check_contract_header(file_path)
            file_result["header_valid"] = header_valid
            if header_valid:
                results["summary"]["headers_valid"] += 1
            else:
                file_result["errors"].append(f"Header: {msg}")
        
        # Check for executable content (if file exists)
        if exists:
            no_executable, violations = check_for_executable_content(file_path)
            file_result["no_executable"] = no_executable
            if no_executable:
                results["summary"]["no_executable_content"] += 1
            else:
                file_result["errors"].extend(violations)
        
        results["files_checked"].append(file_result)
    
    return results

def print_results(results: Dict):
    """Print validation results"""
    print("=" * 70)
    print("POLICY CONTRACT VALIDATION")
    print("=" * 70)
    print()
    
    if not results["directory_exists"]:
        print("[ERROR] Policy directory not found!")
        print(f"   Expected: {POLICY_DIR}")
        return
    
    print(f"Directory: {POLICY_DIR}")
    print(f"Files Checked: {results['summary']['total_files']}")
    print()
    
    # Summary
    print("SUMMARY:")
    print(f"  [OK] Files Exist: {results['summary']['files_exist']}/{results['summary']['total_files']}")
    print(f"  [OK] Headers Valid: {results['summary']['headers_valid']}/{results['summary']['total_files']}")
    print(f"  [OK] No Executable Content: {results['summary']['no_executable_content']}/{results['summary']['total_files']}")
    print()
    
    # Detailed results
    print("DETAILED RESULTS:")
    print("-" * 70)
    
    all_valid = True
    for file_result in results["files_checked"]:
        filename = file_result["filename"]
        status_icons = []
        
        if file_result["exists"]:
            status_icons.append("[OK]")
        else:
            status_icons.append("[MISSING]")
            all_valid = False
        
        if file_result["filename"] == "README.md":
            status_icons.append("[SKIP]")  # Skip header check for README
        elif file_result["header_valid"]:
            status_icons.append("[OK]")
        else:
            status_icons.append("[INVALID]")
            all_valid = False
        
        if file_result["no_executable"]:
            status_icons.append("[OK]")
        else:
            status_icons.append("[EXEC]")
            all_valid = False
        
        status = " ".join(status_icons)
        print(f"{status} {filename}")
        
        if file_result["errors"]:
            for error in file_result["errors"]:
                print(f"     [WARN] {error}")
    
    print("-" * 70)
    print()
    
    # Overall status
    if all_valid and results["summary"]["files_exist"] == results["summary"]["total_files"]:
        print("[PASS] VALIDATION PASSED: All policy files comply with contract")
    else:
        print("[FAIL] VALIDATION FAILED: Issues found (see details above)")
        if results["summary"]["errors"]:
            print("\nErrors:")
            for error in results["summary"]["errors"]:
                print(f"  - {error}")
    
    print("=" * 70)

def main():
    """Main validation function"""
    results = validate_policy_directory()
    print_results(results)
    
    # Return exit code
    if (results["summary"]["files_exist"] == results["summary"]["total_files"] and
        results["summary"]["headers_valid"] >= results["summary"]["total_files"] - 1 and  # README doesn't need header
        results["summary"]["no_executable_content"] == results["summary"]["total_files"]):
        return 0
    return 1

if __name__ == "__main__":
    exit(main())
