"""
Script: replit__integrate__approved.py
Intent: snapshot (moves approved files to final destinations)
Purpose: Integrate human-approved Replit files to final destinations with conflict checking

Reads:
- staging/replit/validated/* (validated files awaiting approval)
- staging/replit/integration_manifest.json (if exists, for tracking)

Writes:
- Final destination files (dashboards/replit_*, static/replit_*, scripts/replit_*)
- staging/replit/integration_manifest.json (integration tracking)
- staging/replit/integration_log.jsonl (audit trail)
- staging/replit/conflicts.json (if conflicts detected)

Schema: N/A (integration script)
"""

import json
import shutil
from pathlib import Path
from typing import List, Dict, Tuple, Any, Optional
from datetime import datetime, timezone

BASE_DIR = Path(__file__).parent.parent.parent
STAGING_DIR = BASE_DIR / "staging" / "replit"
VALIDATED_DIR = STAGING_DIR / "validated"
MANIFEST_PATH = STAGING_DIR / "integration_manifest.json"
LOG_PATH = STAGING_DIR / "integration_log.jsonl"
CONFLICTS_PATH = STAGING_DIR / "conflicts.json"

# Target directories based on file type
TARGET_DIRS = {
    "html_cockpit": BASE_DIR / "agent-orchestrator" / "dashboards",
    "static_assets": BASE_DIR / "agent-orchestrator" / "static",
    "data_analysis": BASE_DIR / "agent-orchestrator" / "data",
}

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


def ensure_target_directories():
    """Ensure all target directories exist"""
    for target_dir in TARGET_DIRS.values():
        target_dir.mkdir(parents=True, exist_ok=True)


def detect_file_type(filename: str) -> Optional[str]:
    """Detect file type from filename"""
    if filename.startswith("replit_html_cockpit_"):
        return "html_cockpit"
    elif filename.startswith("replit_static_assets_"):
        return "static_assets"
    elif filename.startswith("replit_data_analysis_"):
        return "data_analysis"
    return None


def check_conflicts(file_path: Path, target_path: Path) -> Tuple[bool, List[str]]:
    """
    Check for conflicts with existing files.
    Returns: (has_conflict, list_of_conflict_descriptions)
    """
    conflicts = []
    
    # Check if target file already exists
    if target_path.exists():
        conflicts.append(f"File already exists: {target_path}")
    
    # Check if target directory is forbidden
    target_path_str = str(target_path)
    for forbidden in FORBIDDEN_FILES + FORBIDDEN_DIRS:
        if forbidden in target_path_str:
            conflicts.append(f"Target path is in forbidden zone: {forbidden}")
    
    if conflicts:
        return True, conflicts
    return False, []


def load_manifest() -> Dict[str, Any]:
    """Load existing integration manifest"""
    if MANIFEST_PATH.exists():
        try:
            return json.loads(MANIFEST_PATH.read_text())
        except Exception:
            pass
    return {
        "_meta": {
            "created_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "version": "1.0.0"
        },
        "integrations": []
    }


def save_manifest(manifest: Dict[str, Any]):
    """Save integration manifest"""
    manifest["_meta"]["updated_at"] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding='utf-8')


def log_integration(log_entry: Dict[str, Any]):
    """Append to integration log"""
    log_entry["timestamp"] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry) + '\n')


def integrate_file(file_path: Path, file_type: str, dry_run: bool = False) -> Dict[str, Any]:
    """
    Integrate a single file to its destination.
    Returns: (success, result_dict)
    """
    result = {
        "filename": file_path.name,
        "file_type": file_type,
        "source_path": str(file_path),
        "target_path": None,
        "integrated": False,
        "conflicts": [],
        "errors": [],
        "dry_run": dry_run
    }
    
    # Determine target directory
    target_dir = TARGET_DIRS.get(file_type)
    if not target_dir:
        result["errors"].append(f"Unknown file type: {file_type}")
        return result
    
    # Ensure target directory exists
    if not dry_run:
        ensure_target_directories()
    
    # Determine target path
    target_path = target_dir / file_path.name
    result["target_path"] = str(target_path)
    
    # Check for conflicts
    has_conflict, conflicts = check_conflicts(file_path, target_path)
    result["conflicts"] = conflicts
    
    if has_conflict:
        result["errors"].extend(conflicts)
        log_integration({
            "action": "integration_blocked",
            "reason": "conflicts_detected",
            "result": result
        })
        return result
    
    # Integrate file (move or copy)
    if not dry_run:
        try:
            shutil.copy2(file_path, target_path)
            result["integrated"] = True
            log_integration({
                "action": "file_integrated",
                "result": result
            })
        except Exception as e:
            result["errors"].append(f"Failed to integrate file: {str(e)}")
            log_integration({
                "action": "integration_failed",
                "reason": str(e),
                "result": result
            })
    else:
        result["integrated"] = True  # Simulate success in dry run
        log_integration({
            "action": "integration_dry_run",
            "result": result
        })
    
    return result


def integrate_all_approved(dry_run: bool = False, file_list: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Integrate all approved files (or specific files if file_list provided).
    
    Args:
        dry_run: If True, simulate integration without moving files
        file_list: Optional list of specific filenames to integrate (if None, integrates all)
    
    Returns:
        Integration results dictionary
    """
    ensure_target_directories()
    
    if not VALIDATED_DIR.exists():
        return {
            "status": "error",
            "message": f"Validated directory does not exist: {VALIDATED_DIR}",
            "files_integrated": [],
            "summary": {
                "total": 0,
                "integrated": 0,
                "failed": 0,
                "conflicts": 0
            }
        }
    
    # Get files to integrate
    if file_list:
        files_to_integrate = [VALIDATED_DIR / f for f in file_list if (VALIDATED_DIR / f).exists()]
    else:
        files_to_integrate = [f for f in VALIDATED_DIR.iterdir() if f.is_file()]
    
    results = {
        "status": "complete",
        "integrated_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "dry_run": dry_run,
        "files_integrated": [],
        "summary": {
            "total": len(files_to_integrate),
            "integrated": 0,
            "failed": 0,
            "conflicts": 0
        }
    }
    
    conflicts_detected = []
    
    # Integrate each file
    for file_path in files_to_integrate:
        file_type = detect_file_type(file_path.name)
        if not file_type:
            result = {
                "filename": file_path.name,
                "file_type": "unknown",
                "integrated": False,
                "errors": [f"Could not determine file type from filename: {file_path.name}"]
            }
            results["files_integrated"].append(result)
            results["summary"]["failed"] += 1
            continue
        
        result = integrate_file(file_path, file_type, dry_run=dry_run)
        results["files_integrated"].append(result)
        
        if result["conflicts"]:
            conflicts_detected.append(result)
            results["summary"]["conflicts"] += 1
        elif result["integrated"]:
            results["summary"]["integrated"] += 1
        else:
            results["summary"]["failed"] += 1
    
    # Save conflicts if any
    if conflicts_detected:
        conflicts_data = {
            "detected_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "conflicts": conflicts_detected
        }
        CONFLICTS_PATH.write_text(json.dumps(conflicts_data, indent=2), encoding='utf-8')
        results["conflicts_file"] = str(CONFLICTS_PATH)
    
    # Update manifest
    if not dry_run:
        manifest = load_manifest()
        manifest["integrations"].append({
            "integrated_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "files_count": results["summary"]["integrated"],
            "dry_run": dry_run,
            "results": results["files_integrated"]
        })
        save_manifest(manifest)
    
    # Log summary
    log_integration({
        "action": "integration_complete",
        "summary": results["summary"],
        "dry_run": dry_run
    })
    
    return results


def print_results(results: Dict[str, Any]):
    """Print integration results"""
    print("=" * 70)
    print("REPLIT INTEGRATION")
    print("=" * 70)
    print()
    
    if results["status"] == "error":
        print(f"[ERROR] {results['message']}")
        return
    
    mode_str = "DRY RUN" if results["dry_run"] else "LIVE"
    print(f"Mode: {mode_str}")
    print(f"Integrated At: {results['integrated_at']}")
    print()
    
    summary = results["summary"]
    print("SUMMARY:")
    print(f"  Total Files: {summary['total']}")
    print(f"  [OK] Integrated: {summary['integrated']}")
    print(f"  [FAIL] Failed: {summary['failed']}")
    print(f"  [WARN] Conflicts: {summary['conflicts']}")
    print()
    
    if summary['total'] > 0:
        print("DETAILED RESULTS:")
        print("-" * 70)
        
        for file_result in results["files_integrated"]:
            filename = file_result["filename"]
            if file_result["integrated"]:
                status = "[INTEGRATED]"
                target = file_result.get("target_path", "unknown")
                print(f"{status} {filename}")
                print(f"     -> {target}")
            elif file_result["conflicts"]:
                status = "[CONFLICT]"
                print(f"{status} {filename}")
                for conflict in file_result["conflicts"]:
                    print(f"     [CONFLICT] {conflict}")
            else:
                status = "[FAILED]"
                print(f"{status} {filename}")
                for error in file_result.get("errors", []):
                    print(f"     [ERROR] {error}")
            
            print()
        
        print("-" * 70)
        print()
    
    # Overall status
    if summary['conflicts'] > 0:
        print(f"[WARNING] {summary['conflicts']} file(s) had conflicts")
        print(f"Conflicts saved to: {results.get('conflicts_file', CONFLICTS_PATH)}")
        print("Review conflicts.json and resolve before retrying integration")
    elif summary['failed'] > 0:
        print(f"[FAIL] {summary['failed']} file(s) failed to integrate")
    elif summary['integrated'] > 0:
        if results["dry_run"]:
            print("[INFO] DRY RUN complete - no files were actually moved")
            print("Run without --dry-run to perform actual integration")
        else:
            print(f"[SUCCESS] {summary['integrated']} file(s) integrated successfully")
            print(f"Integration manifest: {MANIFEST_PATH}")
            print(f"Integration log: {LOG_PATH}")
    else:
        print("[INFO] No files to integrate")
    
    print("=" * 70)


def main():
    """Main integration function"""
    import sys
    
    # Parse command line arguments
    dry_run = "--dry-run" in sys.argv or "-d" in sys.argv
    file_list = None
    
    # Check for specific file list
    if "--files" in sys.argv:
        idx = sys.argv.index("--files")
        if idx + 1 < len(sys.argv):
            file_list = sys.argv[idx + 1].split(",")
    
    # Show help
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: python replit__integrate__approved.py [OPTIONS]")
        print()
        print("Options:")
        print("  --dry-run, -d    Simulate integration without moving files")
        print("  --files FILE1,FILE2   Integrate specific files only")
        print("  --help, -h       Show this help message")
        print()
        print("Examples:")
        print("  python replit__integrate__approved.py")
        print("  python replit__integrate__approved.py --dry-run")
        print("  python replit__integrate__approved.py --files file1.html,file2.css")
        return 0
    
    # Perform integration
    results = integrate_all_approved(dry_run=dry_run, file_list=file_list)
    print_results(results)
    
    # Return exit code
    if results["status"] == "error":
        return 1
    if results["summary"]["failed"] > 0 or results["summary"]["conflicts"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    exit(main())
