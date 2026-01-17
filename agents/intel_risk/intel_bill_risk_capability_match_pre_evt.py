"""
Intelligence Agent: Bill Risk Capability Matching (PRE_EVT)
Class: Intelligence (Read-Only)
Purpose: Analyze legislative bills to extract risk-management signals and assess alignment 
         with wireless, low-power sensing capabilities
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

# Add lib to path
BASE_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from lib.bill_risk_analyzer import BillRiskAnalyzer

# Paths
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
AUDIT_PATH = BASE_DIR / "audit" / "audit-log.jsonl"
OUTPUT_DIR = BASE_DIR / "artifacts" / "intel_risk"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

AGENT_ID = "intel_bill_risk_capability_match_pre_evt"
AGENT_TYPE = "Intelligence"
RISK_LEVEL = "LOW"

def log_event(event_type: str, message: str, **kwargs):
    """Log event to audit log"""
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "event_type": event_type,
        "agent_id": AGENT_ID,
        "message": message,
        **kwargs
    }
    with open(AUDIT_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(event) + '\n')

def update_heartbeat():
    """Update agent heartbeat in registry"""
    try:
        registry = json.loads(REGISTRY_PATH.read_text(encoding='utf-8'))
        for agent in registry.get("agents", []):
            if agent.get("agent_id") == AGENT_ID:
                agent["last_heartbeat"] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                agent["status"] = "RUNNING"
                break
        REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    except Exception as e:
        log_event("error", f"Failed to update heartbeat: {e}")

def load_bill_metadata(metadata_path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """Load bill metadata from JSON file if provided"""
    if metadata_path and metadata_path.exists():
        try:
            return json.loads(metadata_path.read_text(encoding='utf-8'))
        except Exception as e:
            log_event("warning", f"Failed to load bill metadata: {e}")
    return None

def find_bill_file(input_path: str) -> Optional[Path]:
    """Find bill file from input path"""
    bill_path = Path(input_path)
    
    # If it's a file, return it
    if bill_path.is_file():
        return bill_path
    
    # If it's a directory, look for common bill file names
    if bill_path.is_dir():
        for pattern in ["*.pdf", "*.html", "*.txt", "*.md", "bill*.pdf", "bill*.html"]:
            matches = list(bill_path.glob(pattern))
            if matches:
                return matches[0]
    
    return None

def main() -> Optional[Path]:
    """
    Main agent execution
    
    Returns:
        Path to output file if successful, None if failed
    """
    log_event("agent_spawned", f"Agent {AGENT_ID} spawned", agent_type=AGENT_TYPE, risk_level=RISK_LEVEL)
    
    # Register agent
    try:
        registry = json.loads(REGISTRY_PATH.read_text(encoding='utf-8'))
        agent_entry = {
            "agent_id": AGENT_ID,
            "agent_type": AGENT_TYPE,
            "status": "RUNNING",
            "scope": "Bill risk-capability matching analysis (read-only)",
            "current_task": "Analyzing bill for risk signals and capability alignment",
            "last_heartbeat": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "risk_level": RISK_LEVEL,
            "outputs": [],
            "spawned_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }
        registry.setdefault("agents", []).append(agent_entry)
        registry["_meta"]["total_agents"] = len(registry.get("agents", []))
        registry["_meta"]["active_agents"] = len([a for a in registry.get("agents", []) if a.get("status") == "RUNNING"])
        REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    except Exception as e:
        log_event("error", f"Failed to register agent: {e}")
        print(f"[{AGENT_ID}] ERROR: Failed to register agent: {e}")
    
    log_event("task_started", "Bill risk analysis task started")
    
    # Get input (from command line or default)
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    else:
        # Try to find bill file in common locations
        input_path = None
        for search_path in [
            BASE_DIR / "data" / "bills",
            BASE_DIR / "uploads",
            Path.cwd()
        ]:
            if search_path.exists():
                bill_file = find_bill_file(str(search_path))
                if bill_file:
                    input_path = str(bill_file)
                    break
    
    if not input_path:
        log_event("error", "No bill file provided or found")
        print(f"[{AGENT_ID}] ERROR: No bill file provided. Usage: python {sys.argv[0]} <bill_file_path> [metadata_json_path]")
        return None
    
    bill_file = find_bill_file(input_path)
    if not bill_file:
        log_event("error", f"Bill file not found: {input_path}")
        print(f"[{AGENT_ID}] ERROR: Bill file not found: {input_path}")
        return None
    
    # Load metadata if provided
    metadata_path = None
    if len(sys.argv) > 2:
        metadata_path = Path(sys.argv[2])
    
    bill_metadata = load_bill_metadata(metadata_path)
    
    print(f"[{AGENT_ID}] Analyzing bill: {bill_file}")
    log_event("info", f"Analyzing bill: {bill_file}", bill_path=str(bill_file))
    
    try:
        # Initialize analyzer
        analyzer = BillRiskAnalyzer()
        
        # Perform analysis
        analysis_result = analyzer.analyze(bill_file, bill_metadata)
        
        # Build output artifact with _meta block
        output_data = {
            "_meta": {
                "agent_id": AGENT_ID,
                "generated_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                "artifact_type": "BILL_RISK_ANALYSIS",
                "artifact_name": "Bill Risk Capability Analysis",
                "status": "SPECULATIVE",
                "confidence": "MEDIUM",
                "human_review_required": False,
                "requires_review": None,
                "review_gate_status": None,
                "guidance_status": "SIGNED"
            },
            **analysis_result
        }
        
        # Write output
        output_file = OUTPUT_DIR / f"BILL_RISK_ANALYSIS_{analysis_result.get('bill_id', 'UNKNOWN').replace('.', '_').replace(' ', '_')}.json"
        output_file.write_text(json.dumps(output_data, indent=2), encoding='utf-8')
        
        # Update agent entry
        try:
            registry = json.loads(REGISTRY_PATH.read_text(encoding='utf-8'))
            for agent in registry.get("agents", []):
                if agent.get("agent_id") == AGENT_ID:
                    agent["outputs"].append(str(output_file.relative_to(BASE_DIR)))
                    agent["status"] = "IDLE"
                    agent["current_task"] = "Bill analysis complete"
                    break
            REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
        except Exception as e:
            log_event("warning", f"Failed to update registry: {e}")
        
        log_event("task_completed", "Bill risk analysis completed", 
                  output_file=str(output_file), 
                  bill_id=analysis_result.get("bill_id"),
                  risk_relevance=analysis_result.get("risk_relevance"),
                  alignment_level=analysis_result.get("wireless_risk_alignment", {}).get("alignment_level"))
        
        print(f"[{AGENT_ID}] Analysis complete. Output: {output_file}")
        print(f"[{AGENT_ID}] Risk relevance: {analysis_result.get('risk_relevance')}")
        print(f"[{AGENT_ID}] Alignment level: {analysis_result.get('wireless_risk_alignment', {}).get('alignment_level')}")
        
        return output_file
        
    except Exception as e:
        log_event("error", f"Bill analysis failed: {e}", error_type=type(e).__name__)
        print(f"[{AGENT_ID}] ERROR: Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = main()
    if result:
        print(f"[SUCCESS] Agent completed. Output: {result}")
        sys.exit(0)
    else:
        print("[FAILED] Agent failed")
        sys.exit(1)
