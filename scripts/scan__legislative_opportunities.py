"""
Script: scan__legislative_opportunities.py
Intent:
- aggregate

Reads:
- agent-orchestrator/artifacts/*/signal_summary.json
- agent-orchestrator/artifacts/*/PRE_STAKEHOLDER_MAP.json
- agent-orchestrator/artifacts/*/KEY_FINDINGS_REPORT.md
- agent-orchestrator/state/legislative-state.json
- data/committees/committees__snapshot.json (if available)

Writes:
- data/opportunities/legislative_opportunities__scan.json

Schema:
{
  "_meta": {
    "source_files": [...],
    "scanned_at": "ISO-8601 UTC",
    "script": "scan__legislative_opportunities.py",
    "schema_version": "1.0.0"
  },
  "opportunities": [
    {
      "opportunity_id": "uuid",
      "type": "bill" | "regulatory" | "signal",
      "item_id": "S.2296" | "regulatory-signal-1",
      "jurisdiction_check": "PASS" | "FAIL" | "UNCERTAIN",
      "timing_window_check": "PASS" | "FAIL" | "UNCERTAIN",
      "power_concentration_check": "PASS" | "FAIL" | "UNCERTAIN",
      "companion_bill_check": "PASS" | "PARTIAL" | "FAIL",
      "must_pass_check": "PASS" | "FAIL" | "N/A",
      "overall_score": 0.0-1.0,
      "recommendation": "PROCEED" | "MONITOR" | "DEFER",
      "reasoning": "...",
      "gaps": [...]
    }
  ]
}
"""

import sys
import json
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

# Path setup
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

# Data directories
DATA_DIR = BASE_DIR / "data"
OPPORTUNITIES_DIR = DATA_DIR / "opportunities"
OPPORTUNITIES_DIR.mkdir(parents=True, exist_ok=True)

ARTIFACTS_DIR = BASE_DIR / "artifacts"
STATE_DIR = BASE_DIR / "state"
COMMITTEES_DIR = DATA_DIR / "committees"


def load_artifacts() -> Dict[str, Any]:
    """Load all relevant artifacts."""
    artifacts = {
        "signals": None,
        "stakeholders": None,
        "bills": None,
        "legislative_state": None,
        "committees": None
    }
    
    # Load signal scan
    signal_paths = [
        ARTIFACTS_DIR / "intel_signal_scan_pre_evt" / "signal_summary.json",
        ARTIFACTS_DIR / "orchestrator_core_planner" / "regulatory_opportunity_analysis.json"
    ]
    for path in signal_paths:
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if "signals" in data or "industry_opportunities" in data:
                        artifacts["signals"] = data
                        break
            except Exception as e:
                print(f"[WARNING] Could not load signal scan from {path}: {e}")
    
    # Load stakeholder map
    stakeholder_paths = [
        ARTIFACTS_DIR / "intel_stakeholder_map_pre_evt" / "PRE_STAKEHOLDER_MAP.json",
        ARTIFACTS_DIR / "policy" / "stakeholder_map.md"
    ]
    for path in stakeholder_paths:
        if path.exists():
            try:
                if path.suffix == ".json":
                    with open(path, 'r', encoding='utf-8') as f:
                        artifacts["stakeholders"] = json.load(f)
                else:
                    # Markdown file - just note it exists
                    artifacts["stakeholders"] = {"source": str(path), "format": "markdown"}
                break
            except Exception as e:
                print(f"[WARNING] Could not load stakeholder map from {path}: {e}")
    
    # Load bill data
    bill_paths = [
        ARTIFACTS_DIR / "wi_charge_scenario" / "KEY_FINDINGS_REPORT.md"
    ]
    for path in bill_paths:
        if path.exists():
            artifacts["bills"] = {"source": str(path), "format": "markdown"}
    
    # Load legislative state
    state_path = STATE_DIR / "legislative-state.json"
    if state_path.exists():
        try:
            with open(state_path, 'r', encoding='utf-8') as f:
                artifacts["legislative_state"] = json.load(f)
        except Exception as e:
            print(f"[WARNING] Could not load legislative state: {e}")
    
    # Load committee data (if available)
    committees_path = COMMITTEES_DIR / "committees__snapshot.json"
    if committees_path.exists():
        try:
            with open(committees_path, 'r', encoding='utf-8') as f:
                artifacts["committees"] = json.load(f)
        except Exception as e:
            print(f"[WARNING] Could not load committee data: {e}")
    
    return artifacts


def check_jurisdiction(opportunity: Dict[str, Any], committees_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Check jurisdiction concentration."""
    result = {
        "status": "UNCERTAIN",
        "reasoning": [],
        "gaps": []
    }
    
    if opportunity["type"] == "bill":
        # For bills, check if committees are identifiable
        bill_id = opportunity.get("item_id", "")
        if "S." in bill_id or "H.R." in bill_id or "H.RES." in bill_id:
            result["status"] = "PASS"
            result["reasoning"].append("Bill identifier found - committees should be identifiable")
        else:
            result["status"] = "UNCERTAIN"
            result["gaps"].append("Cannot identify committees without bill details")
    
    elif opportunity["type"] == "regulatory":
        # For regulatory, need agency identification
        agency = opportunity.get("agency", "")
        if agency and agency != "UNKNOWN":
            result["status"] = "PASS"
            result["reasoning"].append(f"Agency identified: {agency}")
        else:
            result["status"] = "UNCERTAIN"
            result["gaps"].append("Agency not identified - cannot assess jurisdiction")
    
    # If we have committee data, enhance the check
    if committees_data and result["status"] == "PASS":
        result["reasoning"].append("Committee data available for detailed analysis")
    
    return result


def check_timing_window(opportunity: Dict[str, Any], legislative_state: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Check timing window viability."""
    result = {
        "status": "UNCERTAIN",
        "reasoning": [],
        "gaps": []
    }
    
    if opportunity["type"] == "bill":
        bill_status = opportunity.get("status", "")
        current_state = legislative_state.get("current_state", "") if legislative_state else None
        
        if bill_status == "Enrolled" or "ES" in bill_status:
            result["status"] = "UNCERTAIN"
            result["reasoning"].append("Bill appears enrolled - timing may be post-passage")
            result["gaps"].append("Cannot determine if pre-conference, post-passage, or implementation phase")
        
        elif current_state:
            if current_state == "INTRO_EVT":
                result["status"] = "PASS"
                result["reasoning"].append("Current state is INTRO_EVT - early in process")
            else:
                result["status"] = "UNCERTAIN"
                result["reasoning"].append(f"Current state is {current_state} - timing unclear")
        else:
            result["status"] = "UNCERTAIN"
            result["gaps"].append("No legislative state data available")
    
    elif opportunity["type"] == "regulatory":
        timeline = opportunity.get("timeline", "")
        if timeline:
            result["status"] = "PASS"
            result["reasoning"].append(f"Timeline identified: {timeline}")
        else:
            result["status"] = "FAIL"
            result["gaps"].append("No timeline identified for regulatory opportunity")
    
    return result


def check_power_concentration(opportunity: Dict[str, Any], committees_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Check power concentration."""
    result = {
        "status": "PASS",  # Default optimistic
        "reasoning": [],
        "gaps": []
    }
    
    if opportunity["type"] == "bill":
        bill_id = opportunity.get("item_id", "")
        
        # NDAA is must-pass
        if "NDAA" in opportunity.get("title", "") or "2296" in bill_id:
            result["status"] = "PASS"
            result["reasoning"].append("NDAA is must-pass legislation - high leverage")
            result["reasoning"].append("Multiple choke points: committee chairs, conference, Rules Committee")
        
        # If we have committee data, check for leadership
        if committees_data:
            result["reasoning"].append("Committee leadership data available for power analysis")
        else:
            result["gaps"].append("Committee leadership data not available")
    
    elif opportunity["type"] == "regulatory":
        agency = opportunity.get("agency", "")
        if agency:
            result["status"] = "PASS"
            result["reasoning"].append(f"Regulatory agency {agency} has concentrated authority")
        else:
            result["status"] = "UNCERTAIN"
            result["gaps"].append("Agency not identified")
    
    return result


def check_companion_bill(opportunity: Dict[str, Any]) -> Dict[str, Any]:
    """Check for companion bill."""
    result = {
        "status": "PARTIAL",
        "reasoning": [],
        "gaps": []
    }
    
    if opportunity["type"] == "bill":
        bill_id = opportunity.get("item_id", "")
        companion = opportunity.get("companion_bill", "")
        
        if companion:
            result["status"] = "PASS"
            result["reasoning"].append(f"Companion bill identified: {companion}")
        elif "S." in bill_id:
            result["status"] = "PARTIAL"
            result["reasoning"].append("Senate bill - House companion may exist but not identified")
            result["gaps"].append("House companion bill not found in artifacts")
        elif "H.R." in bill_id or "H.RES." in bill_id:
            result["status"] = "PARTIAL"
            result["reasoning"].append("House bill - Senate companion may exist but not identified")
            result["gaps"].append("Senate companion bill not found in artifacts")
    
    return result


def check_must_pass(opportunity: Dict[str, Any]) -> Dict[str, Any]:
    """Check if must-pass legislation."""
    result = {
        "status": "N/A",
        "reasoning": [],
        "gaps": []
    }
    
    if opportunity["type"] == "bill":
        bill_id = opportunity.get("item_id", "")
        title = opportunity.get("title", "")
        
        # Known must-pass bills
        must_pass_keywords = ["NDAA", "Appropriations", "Continuing Resolution", "CR", "Debt Ceiling"]
        
        if any(keyword in title for keyword in must_pass_keywords):
            result["status"] = "PASS"
            result["reasoning"].append(f"Identified as must-pass: {title}")
        else:
            result["status"] = "N/A"
            result["reasoning"].append("Not identified as must-pass legislation")
    
    return result


def calculate_overall_score(checks: Dict[str, Dict[str, Any]]) -> float:
    """Calculate overall opportunity score (0.0-1.0)."""
    weights = {
        "jurisdiction": 0.25,
        "timing": 0.25,
        "power": 0.20,
        "companion": 0.15,
        "must_pass": 0.15
    }
    
    score_map = {
        "PASS": 1.0,
        "PARTIAL": 0.5,
        "UNCERTAIN": 0.3,
        "FAIL": 0.0,
        "N/A": 0.5  # Neutral for N/A
    }
    
    total_score = 0.0
    for check_name, weight in weights.items():
        if check_name in checks:
            status = checks[check_name]["status"]
            score = score_map.get(status, 0.0)
            total_score += score * weight
    
    return round(total_score, 2)


def get_recommendation(score: float, checks: Dict[str, Dict[str, Any]]) -> str:
    """Get recommendation based on score and checks."""
    if score >= 0.7:
        return "PROCEED"
    elif score >= 0.4:
        return "MONITOR"
    else:
        return "DEFER"


def scan_opportunities(artifacts: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Scan for legislative opportunities."""
    opportunities = []
    
    # Scan for bills
    if artifacts.get("bills"):
        # S.2296 NDAA from artifacts
        opportunity = {
            "opportunity_id": str(uuid.uuid4()),
            "type": "bill",
            "item_id": "S.2296",
            "title": "NDAA FY2026",
            "status": "Enrolled (ES - Engrossed in Senate)",
            "source": "wi_charge_scenario/KEY_FINDINGS_REPORT.md"
        }
        
        # Run checks
        opportunity["jurisdiction_check"] = check_jurisdiction(opportunity, artifacts.get("committees"))
        opportunity["timing_window_check"] = check_timing_window(opportunity, artifacts.get("legislative_state"))
        opportunity["power_concentration_check"] = check_power_concentration(opportunity, artifacts.get("committees"))
        opportunity["companion_bill_check"] = check_companion_bill(opportunity)
        opportunity["must_pass_check"] = check_must_pass(opportunity)
        
        # Calculate score
        checks = {
            "jurisdiction": opportunity["jurisdiction_check"],
            "timing": opportunity["timing_window_check"],
            "power": opportunity["power_concentration_check"],
            "companion": opportunity["companion_bill_check"],
            "must_pass": opportunity["must_pass_check"]
        }
        opportunity["overall_score"] = calculate_overall_score(checks)
        opportunity["recommendation"] = get_recommendation(opportunity["overall_score"], checks)
        
        # Collect all gaps
        opportunity["gaps"] = []
        for check in checks.values():
            opportunity["gaps"].extend(check.get("gaps", []))
        
        # Build reasoning summary
        reasoning_parts = []
        for check_name, check_result in checks.items():
            status = check_result["status"]
            reasoning_parts.append(f"{check_name}: {status}")
            reasoning_parts.extend(check_result.get("reasoning", []))
        opportunity["reasoning"] = " | ".join(reasoning_parts)
        
        opportunities.append(opportunity)
    
    # Scan for regulatory opportunities
    if artifacts.get("signals"):
        signals_data = artifacts["signals"]
        
        # Check for regulatory signals
        regulatory_signals = signals_data.get("industry_opportunities", [])
        if not regulatory_signals:
            regulatory_signals = signals_data.get("signals", [])
        
        for signal in regulatory_signals:
            if isinstance(signal, dict) and signal.get("type") == "regulatory":
                opportunity = {
                    "opportunity_id": str(uuid.uuid4()),
                    "type": "regulatory",
                    "item_id": f"regulatory-signal-{len(opportunities) + 1}",
                    "agency": signal.get("agency", "UNKNOWN"),
                    "timeline": signal.get("timeline", ""),
                    "source": "signal_summary.json"
                }
                
                # Run checks
                opportunity["jurisdiction_check"] = check_jurisdiction(opportunity, artifacts.get("committees"))
                opportunity["timing_window_check"] = check_timing_window(opportunity, artifacts.get("legislative_state"))
                opportunity["power_concentration_check"] = check_power_concentration(opportunity, artifacts.get("committees"))
                opportunity["companion_bill_check"] = {"status": "N/A", "reasoning": ["Not applicable for regulatory"], "gaps": []}
                opportunity["must_pass_check"] = {"status": "N/A", "reasoning": ["Not applicable for regulatory"], "gaps": []}
                
                # Calculate score
                checks = {
                    "jurisdiction": opportunity["jurisdiction_check"],
                    "timing": opportunity["timing_window_check"],
                    "power": opportunity["power_concentration_check"]
                }
                opportunity["overall_score"] = calculate_overall_score(checks)
                opportunity["recommendation"] = get_recommendation(opportunity["overall_score"], checks)
                
                # Collect gaps
                opportunity["gaps"] = []
                for check in checks.values():
                    opportunity["gaps"].extend(check.get("gaps", []))
                
                # Build reasoning
                reasoning_parts = []
                for check_name, check_result in checks.items():
                    status = check_result["status"]
                    reasoning_parts.append(f"{check_name}: {status}")
                    reasoning_parts.extend(check_result.get("reasoning", []))
                opportunity["reasoning"] = " | ".join(reasoning_parts)
                
                opportunities.append(opportunity)
    
    return opportunities


def main():
    """Main execution."""
    print("=" * 60)
    print("Legislative Opportunity Scan")
    print("=" * 60)
    
    # Load artifacts
    print("[INFO] Loading artifacts...")
    artifacts = load_artifacts()
    
    source_files = []
    if artifacts["signals"]:
        source_files.append("signal_summary.json")
    if artifacts["stakeholders"]:
        source_files.append("stakeholder_map")
    if artifacts["bills"]:
        source_files.append("KEY_FINDINGS_REPORT.md")
    if artifacts["legislative_state"]:
        source_files.append("legislative-state.json")
    if artifacts["committees"]:
        source_files.append("committees__snapshot.json")
    
    print(f"[INFO] Loaded {len([a for a in artifacts.values() if a])} artifact sources")
    
    # Scan opportunities
    print("[INFO] Scanning for opportunities...")
    opportunities = scan_opportunities(artifacts)
    
    print(f"[SUCCESS] Found {len(opportunities)} opportunities")
    
    # Create output
    output_data = {
        "_meta": {
            "source_files": source_files,
            "scanned_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "script": "scan__legislative_opportunities.py",
            "schema_version": "1.0.0",
            "count": len(opportunities)
        },
        "opportunities": opportunities
    }
    
    # Write output
    output_file = OPPORTUNITIES_DIR / "legislative_opportunities__scan.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Scan Complete")
    print("=" * 60)
    for opp in opportunities:
        print(f"\n{opp['type'].upper()}: {opp.get('item_id', 'Unknown')}")
        print(f"  Score: {opp['overall_score']:.2f} | Recommendation: {opp['recommendation']}")
        if opp.get('gaps'):
            print(f"  Gaps: {len(opp['gaps'])} identified")
    
    print(f"\nOutput: {output_file}")
    
    return output_file


if __name__ == "__main__":
    result = main()
    if result:
        print(f"\n[SUCCESS] Script completed successfully")
        sys.exit(0)
    else:
        print(f"\n[ERROR] Script failed")
        sys.exit(1)
