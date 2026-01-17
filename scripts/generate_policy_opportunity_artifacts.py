"""
Script: generate_policy_opportunity_artifacts.py
Intent:
- aggregate

Reads:
- agent-orchestrator/artifacts/policy/WIRELESS_CHARGING_INSURABLE_RISK_POLICY_OPPORTUNITY.json
- agent-orchestrator/artifacts/policy/WIRELESS_CHARGING_INSURABLE_RISK_STRATEGIC_PLAN.md

Writes:
- agent-orchestrator/artifacts/policy/POLICY_OPPORTUNITY_ARTIFACTS_INDEX.json

Schema:
{
  "_meta": {...},
  "artifacts": [
    {
      "artifact_type": "POLICY_OPPORTUNITY" | "STRATEGIC_PLAN" | "SUMMARY",
      "file_path": "...",
      "status": "SPECULATIVE" | "ACTIONABLE",
      "description": "..."
    }
  ],
  "workflow_status": {
    "opportunity_identified": true,
    "analysis_complete": true,
    "strategic_plan_ready": true,
    "agents_available": true
  }
}
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Paths
BASE_DIR = Path(__file__).parent.parent
POLICY_DIR = BASE_DIR / "artifacts" / "policy"
OUTPUT_FILE = POLICY_DIR / "POLICY_OPPORTUNITY_ARTIFACTS_INDEX.json"

def load_artifact_metadata(file_path: Path) -> Dict[str, Any]:
    """Load metadata from artifact file"""
    try:
        if file_path.suffix == ".json":
            data = json.loads(file_path.read_text(encoding='utf-8'))
            meta = data.get("_meta", {})
            opp_summary = data.get("opportunity_summary", {})
            return {
                "artifact_type": meta.get("artifact_type", "UNKNOWN"),
                "status": meta.get("status", "UNKNOWN"),
                "review_gate_status": meta.get("review_gate_status"),
                "generated_at": meta.get("generated_at"),
                "description": opp_summary.get("title", "Policy Opportunity") if opp_summary else "Policy Opportunity"
            }
        elif file_path.suffix == ".md":
            # For markdown, extract basic info
            content = file_path.read_text(encoding='utf-8')
            return {
                "artifact_type": "STRATEGIC_PLAN" if "STRATEGIC_PLAN" in content else "MARKDOWN",
                "status": "ACTIONABLE" if "APPROVED" in content else "SPECULATIVE",
                "description": content.split('\n')[0].replace('#', '').strip() if content else "Document"
            }
        else:
            return {
                "artifact_type": "UNKNOWN",
                "status": "UNKNOWN",
                "description": f"Unknown file type: {file_path.suffix}"
            }
    except Exception as e:
        return {
            "artifact_type": "UNKNOWN",
            "status": "ERROR",
            "description": f"Error loading: {e}"
        }

def scan_policy_artifacts() -> List[Dict[str, Any]]:
    """Scan policy directory for artifacts"""
    artifacts = []
    
    # Known artifact files
    known_files = [
        "WIRELESS_CHARGING_INSURABLE_RISK_POLICY_OPPORTUNITY.json",
        "WIRELESS_CHARGING_INSURABLE_RISK_POLICY_OPPORTUNITY.md",
        "WIRELESS_CHARGING_INSURABLE_RISK_POLICY_OPPORTUNITY.mmd",
        "WIRELESS_CHARGING_INSURABLE_RISK_STRATEGIC_PLAN.md"
    ]
    
    for filename in known_files:
        file_path = POLICY_DIR / filename
        if file_path.exists():
            metadata = load_artifact_metadata(file_path)
            artifacts.append({
                "file_path": str(file_path.relative_to(BASE_DIR)),
                "file_name": filename,
                **metadata
            })
    
    return artifacts

def check_agent_availability() -> Dict[str, bool]:
    """Check if policy opportunity agents are available"""
    agents_dir = BASE_DIR / "agents"
    
    return {
        "intel_policy_opportunity_analyzer": (agents_dir / "intel_policy_opportunity_analyzer_pre_evt.py").exists(),
        "draft_policy_opportunity_document": (agents_dir / "draft_policy_opportunity_document_pre_evt.py").exists()
    }

def main():
    """Generate policy opportunity artifacts index"""
    
    print("Scanning policy opportunity artifacts...")
    artifacts = scan_policy_artifacts()
    
    print(f"Found {len(artifacts)} artifacts")
    
    # Check agent availability
    agents_available = check_agent_availability()
    
    # Determine workflow status
    opportunity_json = next((a for a in artifacts if "POLICY_OPPORTUNITY.json" in a.get("file_name", "")), None)
    strategic_plan = next((a for a in artifacts if "STRATEGIC_PLAN.md" in a.get("file_name", "")), None)
    
    workflow_status = {
        "opportunity_identified": opportunity_json is not None,
        "analysis_complete": opportunity_json is not None and opportunity_json.get("status") == "ACTIONABLE",
        "strategic_plan_ready": strategic_plan is not None,
        "agents_available": all(agents_available.values())
    }
    
    # Generate index
    index = {
        "_meta": {
            "generated_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "script": "generate_policy_opportunity_artifacts.py",
            "artifact_count": len(artifacts),
            "version": "1.0.0"
        },
        "artifacts": artifacts,
        "workflow_status": workflow_status,
        "agents_available": agents_available,
        "next_steps": [
            "Run intel_policy_opportunity_analyzer_pre_evt.py to generate summary",
            "Run draft_policy_opportunity_document_pre_evt.py to generate document",
            "Review artifacts in artifacts/policy/ directory"
        ]
    }
    
    # Write output
    OUTPUT_FILE.write_text(
        json.dumps(index, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )
    
    print(f"[SUCCESS] Artifacts index generated: {OUTPUT_FILE}")
    print(f"\nWorkflow Status:")
    print(f"  Opportunity Identified: {workflow_status['opportunity_identified']}")
    print(f"  Analysis Complete: {workflow_status['analysis_complete']}")
    print(f"  Strategic Plan Ready: {workflow_status['strategic_plan_ready']}")
    print(f"  Agents Available: {workflow_status['agents_available']}")
    
    return OUTPUT_FILE

if __name__ == "__main__":
    main()
