"""
Script: temporal__inspect__revolving_door.py
Intent: aggregate (read-only analysis, generates report)
Purpose: Inspect revolving-door events and their status

Reads:
- agent-orchestrator/data/temporal/crisis_events.jsonl

Writes:
- agent-orchestrator/data/temporal/revolving_door_inspection__{timestamp}.json

Schema: N/A (inspection report)
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add parent directory to path for imports
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from lib.revolving_door_observability import (
    get_revolving_door_events,
    get_revolving_door_kpis,
    get_revolving_door_timeline,
    get_revolving_door_status
)


def main():
    """Main execution."""
    print("=" * 60)
    print("Revolving-Door Event Inspection")
    print("=" * 60)
    print()
    
    current_time = datetime.utcnow()
    
    # Get all events (active and expired)
    all_events = get_revolving_door_events(current_time, include_expired=True)
    active_events = get_revolving_door_events(current_time, include_expired=False)
    
    print(f"📊 Event Summary:")
    print(f"  Total events: {len(all_events)}")
    print(f"  Active events: {len(active_events)}")
    print(f"  Expired events: {len(all_events) - len(active_events)}")
    print()
    
    # Get KPIs
    kpis = get_revolving_door_kpis(current_time)
    print(f"📈 KPIs:")
    print(f"  Active count: {kpis['active_count']}")
    if kpis.get('average_remaining_days'):
        print(f"  Average remaining days: {kpis['average_remaining_days']}")
    print(f"  Expiration compliance: {kpis['expiration_compliance']['compliance_rate']}%")
    print(f"  Health status: {kpis['health_status']}")
    print()
    
    # Get timeline
    timeline = get_revolving_door_timeline(limit=20)
    
    # Generate report
    report = {
        "_meta": {
            "generated_at": current_time.isoformat() + "Z",
            "total_events": len(all_events),
            "active_events": len(active_events),
            "schema_version": "1.0.0"
        },
        "kpis": kpis,
        "timeline": timeline,
        "active_events": [
            get_revolving_door_status(event, current_time)
            for event in active_events
        ],
        "recommendations": []
    }
    
    # Generate recommendations
    if kpis["expiration_compliance"]["compliance_rate"] < 100.0:
        report["recommendations"].append({
            "priority": "HIGH",
            "action": "REVIEW_EXPIRATION",
            "description": f"{kpis['expiration_compliance']['non_compliant']} events exceed 180-day maximum",
            "affected_count": kpis["expiration_compliance"]["non_compliant"]
        })
    
    if len(active_events) > 50:
        report["recommendations"].append({
            "priority": "MEDIUM",
            "action": "REVIEW_ACTIVE_EVENTS",
            "description": f"High number of active revolving-door events ({len(active_events)})",
            "affected_count": len(active_events)
        })
    
    # Events expiring soon
    expiring_soon = [
        event for event in active_events
        if get_revolving_door_status(event, current_time).get("remaining_days", 999) < 30
    ]
    if expiring_soon:
        report["recommendations"].append({
            "priority": "LOW",
            "action": "MONITOR_EXPIRATION",
            "description": f"{len(expiring_soon)} events expiring within 30 days",
            "affected_count": len(expiring_soon)
        })
    
    # Save report
    timestamp = current_time.strftime("%Y%m%d_%H%M%S")
    output_file = BASE_DIR / "data" / "temporal" / f"revolving_door_inspection__{timestamp}.json"
    
    # Ensure directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        output_file.write_text(json.dumps(report, indent=2, default=str))
        print(f"✅ Report saved to: {output_file}")
    except Exception as e:
        print(f"❌ Failed to save report: {e}")
        sys.exit(1)
    
    # Print recommendations
    if report["recommendations"]:
        print()
        print("💡 Recommendations:")
        for rec in report["recommendations"]:
            print(f"  [{rec['priority']}] {rec['action']}: {rec['description']}")
    
    print()
    print("=" * 60)
    print("✅ Inspection complete")
    print("=" * 60)
    
    return output_file


if __name__ == "__main__":
    output_path = main()
    if output_path:
        print(f"\n📁 Output file: {output_path}")
