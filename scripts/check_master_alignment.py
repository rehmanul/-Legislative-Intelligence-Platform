"""
Script: check_master_alignment.py
Intent: aggregate (validation only, no writes)
Purpose: Single script to run all alignment checks

Reads:
- All files checked by validation scripts

Writes:
- alignment_report.json (optional, via --output flag)

Schema: N/A (validation script)
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

BASE_DIR = Path(__file__).parent.parent

# Import validation functions
sys.path.insert(0, str(Path(__file__).parent))
from validate_master_diagram_alignment import validate_master_diagram_alignment
from validate_diagram_references import validate_diagram_references
from validate_component_mapping import validate_component_mapping

def run_all_checks() -> Dict[str, Any]:
    """Run all alignment checks"""
    print("Running master diagram alignment checks...")
    print("=" * 60)
    
    # Run all validations
    alignment_check = validate_master_diagram_alignment()
    diagram_refs_check = validate_diagram_references()
    component_mapping_check = validate_component_mapping()
    
    # Combine results
    report = {
        "_meta": {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "master_diagram": ".userInput/agent orchestrator 1.6.mmd",
            "report_version": "1.0.0"
        },
        "alignment_check": alignment_check,
        "diagram_references": diagram_refs_check,
        "component_mapping": component_mapping_check,
        "overall_summary": {
            "status": "PASS",
            "total_checks": 0,
            "passed": 0,
            "warnings": 0,
            "failed": 0
        }
    }
    
    # Calculate overall summary
    # From alignment check
    report["overall_summary"]["total_checks"] += alignment_check["summary"]["total_checks"]
    report["overall_summary"]["passed"] += alignment_check["summary"]["passed"]
    report["overall_summary"]["warnings"] += alignment_check["summary"]["warnings"]
    report["overall_summary"]["failed"] += alignment_check["summary"]["failed"]
    
    # From diagram references
    if diagram_refs_check["summary"]["missing_reference"] > 0:
        report["overall_summary"]["warnings"] += diagram_refs_check["summary"]["missing_reference"]
        report["overall_summary"]["total_checks"] += diagram_refs_check["summary"]["missing_reference"]
    
    # From component mapping
    report["overall_summary"]["total_checks"] += component_mapping_check["summary"]["total_components"]
    report["overall_summary"]["passed"] += component_mapping_check["summary"]["mapped"]
    report["overall_summary"]["warnings"] += component_mapping_check["summary"]["warnings"]
    report["overall_summary"]["failed"] += component_mapping_check["summary"]["failures"]
    
    # Determine overall status
    if report["overall_summary"]["failed"] > 0:
        report["overall_summary"]["status"] = "FAIL"
    elif report["overall_summary"]["warnings"] > 0:
        report["overall_summary"]["status"] = "WARN"
    else:
        report["overall_summary"]["status"] = "PASS"
    
    return report

def print_summary(report: Dict[str, Any]):
    """Print human-readable summary"""
    summary = report["overall_summary"]
    
    print("\n" + "=" * 60)
    print("MASTER DIAGRAM ALIGNMENT REPORT")
    print("=" * 60)
    print(f"Overall Status: {summary['status']}")
    print(f"Total Checks: {summary['total_checks']}")
    print(f"  Passed: {summary['passed']}")
    print(f"  Warnings: {summary['warnings']}")
    print(f"  Failed: {summary['failed']}")
    print("=" * 60)
    
    # Alignment check summary
    align = report["alignment_check"]["summary"]
    print(f"\nAlignment Check: {align['passed']}/{align['total_checks']} passed")
    if align["warnings"] > 0 or align["failed"] > 0:
        print("  Issues found in:")
        for check in report["alignment_check"]["checks"]:
            if check["status"] != "PASS":
                print(f"    - {check['check']}: {check['status']}")
                for issue in check.get("issues", [])[:2]:  # Show first 2 issues
                    print(f"      * {issue}")
    
    # Diagram references summary
    diag = report["diagram_references"]["summary"]
    print(f"\nDiagram References: {diag['with_reference']}/{diag['total_diagrams']} have references")
    if diag["missing_reference"] > 0:
        print(f"  Missing references: {diag['missing_reference']} diagrams")
        missing = [d for d in report["diagram_references"]["diagrams"] if not d["has_reference"]]
        for d in missing[:5]:  # Show first 5
            print(f"    - {d['path']}")
    
    # Component mapping summary
    comp = report["component_mapping"]["summary"]
    print(f"\nComponent Mapping: {comp['mapped']}/{comp['total_components']} components mapped")
    if comp["warnings"] > 0 or comp["failures"] > 0:
        print("  Issues found in:")
        for mapping in report["component_mapping"]["mappings"]:
            if mapping["status"] != "PASS":
                print(f"    - {mapping['component']}: {mapping['status']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check master diagram alignment")
    parser.add_argument("--output", "-o", help="Output JSON report file", default=None)
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress summary output")
    
    args = parser.parse_args()
    
    report = run_all_checks()
    
    if not args.quiet:
        print_summary(report)
    
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(json.dumps(report, indent=2))
        print(f"\nReport saved to: {output_path}")
    else:
        # Print JSON to stdout if no output file specified
        print("\n" + "=" * 60)
        print("JSON Report:")
        print("=" * 60)
        print(json.dumps(report, indent=2))
