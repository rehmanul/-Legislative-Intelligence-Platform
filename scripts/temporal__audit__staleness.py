"""
Script: temporal__audit__staleness.py
Intent: aggregate (read-only analysis, generates report)
Purpose: Audit all influence edges for staleness and generate report

Reads:
- agent-orchestrator/data/edges/influence_edges__derived.json
- agent-orchestrator/data/temporal/decay_config__default.json

Writes:
- agent-orchestrator/data/temporal/staleness_audit__{timestamp}.json

Schema: N/A (audit report)
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add parent directory to path for imports
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from lib.staleness_detector import (
    check_edge_staleness,
    get_stale_edges,
    generate_staleness_summary
)
from lib.edge_decay import classify_edge_decay_type, load_decay_config

logger = None  # Will use print for standalone script


def load_edges() -> List[Dict[str, Any]]:
    """Load all influence edges."""
    edges_file = BASE_DIR / "data" / "edges" / "influence_edges__derived.json"
    
    if not edges_file.exists():
        print(f"⚠️  Edges file not found at {edges_file}")
        return []
    
    try:
        edges_data = json.loads(edges_file.read_text())
        return edges_data.get("edges", [])
    except Exception as e:
        print(f"❌ Failed to load edges: {e}")
        return []


def generate_audit_report() -> Dict[str, Any]:
    """Generate staleness audit report."""
    print("🔍 Loading edges...")
    edges = load_edges()
    
    if not edges:
        print("⚠️  No edges found to audit")
        return {
            "_meta": {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "total_edges": 0,
                "audit_status": "NO_EDGES"
            },
            "summary": {},
            "stale_edges": []
        }
    
    print(f"📊 Auditing {len(edges)} edges...")
    
    current_time = datetime.utcnow()
    
    # Generate summary
    summary = generate_staleness_summary(edges, current_time)
    
    # Get stale edges
    stale_edges_data = get_stale_edges(edges, current_time)
    
    # Detailed analysis
    detailed_analysis = {
        "by_edge_type": {},
        "by_decay_type": {
            "PERSON_DEPENDENT": {"fresh": 0, "stale": 0, "very_stale": 0},
            "INSTITUTION_DEPENDENT": {"fresh": 0, "stale": 0, "very_stale": 0},
            "HYBRID": {"fresh": 0, "stale": 0, "very_stale": 0}
        },
        "requiring_revalidation": []
    }
    
    for edge_info in stale_edges_data:
        edge = edge_info["edge"]
        staleness = edge_info["staleness"]
        
        # Track by edge type
        edge_type = edge.get("edge_type", "unknown")
        if edge_type not in detailed_analysis["by_edge_type"]:
            detailed_analysis["by_edge_type"][edge_type] = {"fresh": 0, "stale": 0, "very_stale": 0}
        
        status = staleness["status"]
        detailed_analysis["by_edge_type"][edge_type][status.lower()] += 1
        
        # Track by decay type
        decay_type = classify_edge_decay_type(edge)
        if decay_type in detailed_analysis["by_decay_type"]:
            detailed_analysis["by_decay_type"][decay_type][status.lower()] += 1
        
        # Track edges requiring revalidation
        if staleness.get("requires_revalidation"):
            detailed_analysis["requiring_revalidation"].append({
                "edge_id": edge.get("edge_id"),
                "edge_type": edge_type,
                "from_entity_id": edge.get("from_entity_id"),
                "to_entity_id": edge.get("to_entity_id"),
                "staleness_status": status,
                "days_since_confirmation": staleness.get("days_since_confirmation"),
                "last_confirmed_at": edge.get("last_confirmed_at")
            })
    
    # Prepare report
    report = {
        "_meta": {
            "generated_at": current_time.isoformat() + "Z",
            "total_edges": len(edges),
            "audit_status": "COMPLETE",
            "schema_version": "1.0.0"
        },
        "summary": summary,
        "detailed_analysis": detailed_analysis,
        "stale_edges": [
            {
                "edge_id": edge_info["edge"].get("edge_id"),
                "edge_type": edge_info["edge"].get("edge_type"),
                "from_entity_id": edge_info["edge"].get("from_entity_id"),
                "to_entity_id": edge_info["edge"].get("to_entity_id"),
                "staleness": edge_info["staleness"]
            }
            for edge_info in stale_edges_data
        ],
        "recommendations": []
    }
    
    # Generate recommendations
    if summary["never_confirmed"] > 0:
        report["recommendations"].append({
            "priority": "HIGH",
            "action": "REVALIDATE",
            "description": f"{summary['never_confirmed']} edges have never been confirmed and require initial validation",
            "affected_count": summary["never_confirmed"]
        })
    
    if summary["very_stale"] > 0:
        report["recommendations"].append({
            "priority": "HIGH",
            "action": "REVALIDATE",
            "description": f"{summary['very_stale']} edges are VERY_STALE and may need to be deprecated",
            "affected_count": summary["very_stale"]
        })
    
    if summary["stale"] > 0:
        report["recommendations"].append({
            "priority": "MEDIUM",
            "action": "REVALIDATE",
            "description": f"{summary['stale']} edges are STALE and should be revalidated soon",
            "affected_count": summary["stale"]
        })
    
    if summary["requires_revalidation"] > 0:
        report["recommendations"].append({
            "priority": "MEDIUM",
            "action": "SCHEDULE_REVIEW",
            "description": f"{summary['requires_revalidation']} edges require human revalidation",
            "affected_count": summary["requires_revalidation"]
        })
    
    return report


def main():
    """Main execution."""
    print("=" * 60)
    print("Staleness Audit Script")
    print("=" * 60)
    print()
    
    # Generate report
    report = generate_audit_report()
    
    # Save report
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_file = BASE_DIR / "data" / "temporal" / f"staleness_audit__{timestamp}.json"
    
    # Ensure directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        output_file.write_text(json.dumps(report, indent=2))
        print(f"✅ Report saved to: {output_file}")
    except Exception as e:
        print(f"❌ Failed to save report: {e}")
        sys.exit(1)
    
    # Print summary
    print()
    print("📊 Audit Summary:")
    print(f"  Total edges: {report['_meta']['total_edges']}")
    print(f"  Fresh: {report['summary'].get('fresh', 0)}")
    print(f"  Stale: {report['summary'].get('stale', 0)}")
    print(f"  Very Stale: {report['summary'].get('very_stale', 0)}")
    print(f"  Never Confirmed: {report['summary'].get('never_confirmed', 0)}")
    print(f"  Requires Revalidation: {report['summary'].get('requires_revalidation', 0)}")
    
    # Print recommendations
    if report["recommendations"]:
        print()
        print("💡 Recommendations:")
        for rec in report["recommendations"]:
            print(f"  [{rec['priority']}] {rec['action']}: {rec['description']}")
    
    print()
    print("=" * 60)
    print("✅ Audit complete")
    print("=" * 60)
    
    return output_file


if __name__ == "__main__":
    output_path = main()
    if output_path:
        print(f"\n📁 Output file: {output_path}")
