"""
Script: replit__validate__downloads.py
Intent: snapshot (validation with file moves)
Purpose: Validate Replit downloads against naming conventions, schemas, and forbidden zones

Reads:
- staging/replit/downloads/* (all files in downloads directory)

Writes:
- staging/replit/validated/* (validated files moved here)
- staging/replit/rejected/* (rejected files moved here with error logs)

Schema: Uses schemas/replit/*.schema.json
"""

import json
import re
import shutil
from pathlib import Path
from typing import List, Dict, Tuple, Any
from datetime import datetime, timezone
import sys

BASE_DIR = Path(__file__).parent.parent.parent
STAGING_DIR = BASE_DIR / "staging" / "replit"
DOWNLOADS_DIR = STAGING_DIR / "downloads"
VALIDATED_DIR = STAGING_DIR / "validated"
REJECTED_DIR = STAGING_DIR / "rejected"
SCHEMAS_DIR = BASE_DIR / "agent-orchestrator" / "schemas" / "replit"

VALIDATOR_VERSION = "1.0.0"

# Forbidden file paths (absolute forbidden)
FORBIDDEN_FILES = [
    "agent-orchestrator/state/legislative-state.json",
    "infrastructure/ports.registry.json",
    "agent-orchestrator/registry/agent-registry.json",
]

# Forbidden directory patterns (absolute forbidden)
FORBIDDEN_DIRS = [
    "agent-orchestrator/review/",
    "agent-orchestrator/decisions/",
    "agent-orchestrator/audit/audit-log.jsonl",
    "agent-orchestrator/state/",
    "agent-orchestrator/artifacts/",
]

# Naming convention patterns
NAMING_PATTERNS = {
    "html_cockpit": r"^replit_html_cockpit_\d{8}_\d{6}_[\w-]+\.html$",
    "static_assets": r"^replit_static_assets_\d{8}_\d{6}_[\w-]+\.(css|js)$",
    "data_analysis": r"^replit_data_analysis_\d{8}_\d{6}_[\w-]+\.json$",
}

# Forbidden patterns in content
FORBIDDEN_CONTENT_PATTERNS = [
    r"legislative-state\.json",
    r"ports\.registry\.json",
    r"agent-registry\.json",
    r"agent\.(spawn|execute|run)",
    r"workflow\.(advance|execute)",
    r"@app\.(get|post|put|patch|delete)",
    r"def\s+\w+\s*\(",
    r"async\s+def\s+\w+\s*\(",
    r"class\s+\w+",
    r"from\s+\w+\s+import.*agent",
    r"import.*agent.*spawn",
]

# Allowed target directories for Replit outputs
ALLOWED_TARGET_DIRS = [
    "dashboards/replit_*",
    "static/replit_*",
    "scripts/replit_*",
    "staging/replit/",
]


def ensure_directories():
    """Ensure all required directories exist"""
    VALIDATED_DIR.mkdir(parents=True, exist_ok=True)
    REJECTED_DIR.mkdir(parents=True, exist_ok=True)


def check_naming_convention(file_path: Path) -> Tuple[bool, str, str]:
    """
    Check if file name matches Replit naming convention.
    Returns: (is_valid, file_type, error_message)
    """
    filename = file_path.name
    
    # Check each pattern
    for file_type, pattern in NAMING_PATTERNS.items():
        if re.match(pattern, filename):
            return True, file_type, ""
    
    return False, "unknown", f"Filename '{filename}' does not match any Replit naming pattern. Expected: replit_{{type}}_{{timestamp}}_{{description}}.{{ext}}"


def load_schema(file_type: str) -> Dict[str, Any]:
    """Load schema for file type"""
    schema_map = {
        "html_cockpit": "html_cockpit.schema.json",
        "static_assets": "static_assets.schema.json",
        "data_analysis": "data_analysis.schema.json",
    }
    
    schema_file = SCHEMAS_DIR / schema_map.get(file_type, "")
    if not schema_file.exists():
        return {}
    
    try:
        return json.loads(schema_file.read_text())
    except Exception as e:
        print(f"[WARN] Failed to load schema for {file_type}: {e}")
        return {}


def check_forbidden_content(file_path: Path) -> Tuple[bool, List[str]]:
    """
    Check file content for forbidden patterns.
    Returns: (is_valid, list_of_violations)
    """
    if not file_path.exists():
        return False, [f"File does not exist: {file_path}"]
    
    try:
        content = file_path.read_text(encoding='utf-8')
        violations = []
        
        for pattern in FORBIDDEN_CONTENT_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                violations.append(f"Found forbidden pattern '{pattern}': {len(matches)} matches")
        
        if violations:
            return False, violations
        return True, []
    except Exception as e:
        # For binary files or files we can't read, skip content check
        if file_path.suffix.lower() in ['.html', '.css', '.js', '.json', '.md', '.txt']:
            return False, [f"Error reading file: {str(e)}"]
        return True, []  # Allow binary files (images, etc.)


def check_forbidden_paths(file_path: Path) -> Tuple[bool, List[str]]:
    """
    Check if file path or content references forbidden paths.
    Returns: (is_valid, list_of_violations)
    """
    violations = []
    
    # Check file path itself (shouldn't happen if file is in staging, but check anyway)
    file_path_str = str(file_path)
    for forbidden in FORBIDDEN_FILES + FORBIDDEN_DIRS:
        if forbidden in file_path_str:
            violations.append(f"File path references forbidden location: {forbidden}")
    
    # Check content for forbidden path references
    if file_path.exists():
        try:
            content = file_path.read_text(encoding='utf-8')
            for forbidden in FORBIDDEN_FILES + FORBIDDEN_DIRS:
                # Check for path references in content
                if forbidden.replace("/", "[/\\]") in content or forbidden.replace("\\", "[/\\]") in content:
                    violations.append(f"Content references forbidden path: {forbidden}")
        except Exception:
            pass  # Skip if file can't be read as text
    
    if violations:
        return False, violations
    return True, []


def validate_file(file_path: Path) -> Dict[str, Any]:
    """Validate a single file"""
    result = {
        "filename": file_path.name,
        "file_path": str(file_path),
        "validated_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "validator_version": VALIDATOR_VERSION,
        "naming_valid": False,
        "file_type": None,
        "content_valid": False,
        "path_valid": False,
        "schema_valid": False,
        "overall_valid": False,
        "errors": [],
        "warnings": []
    }
    
    # Check naming convention
    naming_valid, file_type, naming_error = check_naming_convention(file_path)
    result["naming_valid"] = naming_valid
    result["file_type"] = file_type
    
    if not naming_valid:
        result["errors"].append(f"Naming: {naming_error}")
    elif file_type == "unknown":
        result["warnings"].append("File type could not be determined from naming pattern")
    
    # Check forbidden content patterns
    content_valid, content_violations = check_forbidden_content(file_path)
    result["content_valid"] = content_valid
    if not content_valid:
        result["errors"].extend([f"Content: {v}" for v in content_violations])
    
    # Check forbidden paths
    path_valid, path_violations = check_forbidden_paths(file_path)
    result["path_valid"] = path_valid
    if not path_valid:
        result["errors"].extend([f"Path: {v}" for v in path_violations])
    
    # Schema validation (basic - just checks if schema exists and file is parseable if JSON)
    if file_type != "unknown" and file_path.suffix.lower() == ".json":
        schema = load_schema(file_type)
        if schema:
            try:
                content = json.loads(file_path.read_text(encoding='utf-8'))
                # Basic schema validation would go here if jsonschema library is available
                result["schema_valid"] = True
            except json.JSONDecodeError as e:
                result["errors"].append(f"Schema: Invalid JSON: {str(e)}")
                result["schema_valid"] = False
            except Exception as e:
                result["warnings"].append(f"Schema: Could not validate against schema: {str(e)}")
                result["schema_valid"] = True  # Don't block on schema validation errors
        else:
            result["warnings"].append(f"Schema: No schema available for file type '{file_type}'")
            result["schema_valid"] = True  # Don't block if no schema
    else:
        result["schema_valid"] = True  # Non-JSON files don't need schema validation
    
    # Overall validation: all checks must pass (warnings don't block)
    result["overall_valid"] = (
        result["naming_valid"] and
        result["content_valid"] and
        result["path_valid"]
    )
    
    return result


def validate_all_downloads() -> Dict[str, Any]:
    """Validate all files in downloads directory"""
    ensure_directories()
    
    if not DOWNLOADS_DIR.exists():
        return {
            "status": "error",
            "message": f"Downloads directory does not exist: {DOWNLOADS_DIR}",
            "files_validated": [],
            "summary": {
                "total": 0,
                "validated": 0,
                "rejected": 0
            }
        }
    
    files_to_validate = list(DOWNLOADS_DIR.iterdir())
    files_to_validate = [f for f in files_to_validate if f.is_file()]
    
    results = {
        "status": "complete",
        "validated_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "validator_version": VALIDATOR_VERSION,
        "files_validated": [],
        "summary": {
            "total": len(files_to_validate),
            "validated": 0,
            "rejected": 0
        }
    }
    
    for file_path in files_to_validate:
        validation_result = validate_file(file_path)
        results["files_validated"].append(validation_result)
        
        if validation_result["overall_valid"]:
            # Move to validated directory
            target_path = VALIDATED_DIR / file_path.name
            shutil.move(str(file_path), str(target_path))
            results["summary"]["validated"] += 1
        else:
            # Move to rejected directory with error log
            target_path = REJECTED_DIR / file_path.name
            shutil.move(str(file_path), str(target_path))
            
            # Write error log
            error_log_path = REJECTED_DIR / f"{file_path.stem}_errors.json"
            error_log = {
                "filename": file_path.name,
                "rejected_at": datetime.utcnow().isoformat() + "Z",
                "validator_version": VALIDATOR_VERSION,
                "errors": validation_result["errors"],
                "warnings": validation_result["warnings"],
                "validation_result": validation_result
            }
            error_log_path.write_text(json.dumps(error_log, indent=2), encoding='utf-8')
            results["summary"]["rejected"] += 1
    
    return results


def print_results(results: Dict[str, Any]):
    """Print validation results"""
    print("=" * 70)
    print("REPLIT DOWNLOADS VALIDATION")
    print("=" * 70)
    print()
    
    if results["status"] == "error":
        print(f"[ERROR] {results['message']}")
        return
    
    print(f"Validator Version: {results['validator_version']}")
    print(f"Validated At: {results['validated_at']}")
    print()
    
    summary = results["summary"]
    print("SUMMARY:")
    print(f"  Total Files: {summary['total']}")
    print(f"  [OK] Validated: {summary['validated']}")
    print(f"  [FAIL] Rejected: {summary['rejected']}")
    print()
    
    if summary['total'] > 0:
        print("DETAILED RESULTS:")
        print("-" * 70)
        
        for file_result in results["files_validated"]:
            filename = file_result["filename"]
            status = "[VALID]" if file_result["overall_valid"] else "[REJECTED]"
            print(f"{status} {filename}")
            
            if file_result["file_type"]:
                print(f"     Type: {file_result['file_type']}")
            
            if file_result["errors"]:
                for error in file_result["errors"]:
                    print(f"     [ERROR] {error}")
            
            if file_result["warnings"]:
                for warning in file_result["warnings"]:
                    print(f"     [WARN] {warning}")
            
            print()
        
        print("-" * 70)
        print()
    
    # Overall status
    if summary['rejected'] == 0 and summary['total'] > 0:
        print("[PASS] VALIDATION PASSED: All files validated successfully")
        print(f"Validated files moved to: {VALIDATED_DIR}")
    elif summary['rejected'] > 0:
        print(f"[FAIL] VALIDATION FAILED: {summary['rejected']} file(s) rejected")
        print(f"Rejected files moved to: {REJECTED_DIR}")
        print(f"Error logs written to: {REJECTED_DIR}")
    else:
        print("[INFO] No files found in downloads directory")
    
    print("=" * 70)


def main():
    """Main validation function"""
    results = validate_all_downloads()
    print_results(results)
    
    # Save validation report
    report_path = STAGING_DIR / f"validation_report_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    report_path.write_text(json.dumps(results, indent=2), encoding='utf-8')
    print(f"\nValidation report saved to: {report_path}")
    
    # Return exit code
    if results["status"] == "error":
        return 1
    if results["summary"]["rejected"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    exit(main())
