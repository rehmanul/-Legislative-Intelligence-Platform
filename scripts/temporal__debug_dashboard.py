"""
Script: temporal__debug_dashboard.py
Intent: temporal (exploration)

Reads:
- Agent registry
- Audit logs
- Artifact files
- System state

Writes:
- Debug dashboard HTML (temporary, for viewing)

Schema:
- HTML dashboard with agent state, errors, dependencies
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from collections import defaultdict

# Path setup
BASE_DIR = Path(__file__).parent.parent
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
AUDIT_PATH = BASE_DIR / "audit" / "audit-log.jsonl"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
OUTPUT_DIR = BASE_DIR / "artifacts" / "debug_dashboard"


def load_registry() -> Dict[str, Any]:
    """Load agent registry."""
    try:
        if REGISTRY_PATH.exists():
            return json.loads(REGISTRY_PATH.read_text(encoding='utf-8'))
    except Exception as e:
        print(f"⚠️ Error loading registry: {e}")
    return {"agents": [], "_meta": {}}


def load_audit_log() -> List[Dict[str, Any]]:
    """Load audit log entries."""
    entries = []
    try:
        if AUDIT_PATH.exists():
            for line in AUDIT_PATH.read_text(encoding='utf-8').strip().split('\n'):
                if line.strip():
                    try:
                        entries.append(json.loads(line))
                    except:
                        pass
    except Exception as e:
        print(f"[WARNING] Error loading audit log: {e}")
    return entries


def scan_artifacts() -> Dict[str, Any]:
    """Scan artifacts directory for agent outputs."""
    artifacts = {
        "by_agent": defaultdict(list),
        "by_type": defaultdict(list),
        "by_status": defaultdict(list),
        "total": 0,
        "errors": []
    }
    
    try:
        for agent_dir in ARTIFACTS_DIR.iterdir():
            if not agent_dir.is_dir() or agent_dir.name.startswith('.'):
                continue
            
            agent_id = agent_dir.name
            for artifact_file in agent_dir.glob("*.json"):
                try:
                    artifact = json.loads(artifact_file.read_text(encoding='utf-8'))
                    meta = artifact.get("_meta", {})
                    
                    artifact_info = {
                        "path": str(artifact_file.relative_to(BASE_DIR)),
                        "name": artifact_file.name,
                        "agent_id": meta.get("agent_id", agent_id),
                        "artifact_type": meta.get("artifact_type", "unknown"),
                        "status": meta.get("status", "UNKNOWN"),
                        "generated_at": meta.get("generated_at", "unknown"),
                        "size": artifact_file.stat().st_size
                    }
                    
                    artifacts["by_agent"][agent_id].append(artifact_info)
                    artifacts["by_type"][artifact_info["artifact_type"]].append(artifact_info)
                    artifacts["by_status"][artifact_info["status"]].append(artifact_info)
                    artifacts["total"] += 1
                except Exception as e:
                    artifacts["errors"].append({
                        "file": str(artifact_file),
                        "error": str(e)
                    })
    except Exception as e:
        artifacts["errors"].append({"error": f"Scan error: {e}"})
    
    return artifacts


def analyze_agent_state(registry: Dict[str, Any], audit_log: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze agent execution state."""
    agents = registry.get("agents", [])
    
    state = {
        "total_agents": len(agents),
        "by_status": defaultdict(int),
        "by_type": defaultdict(int),
        "recent_activity": [],
        "errors": [],
        "blocked": [],
        "waiting_review": []
    }
    
    for agent in agents:
        status = agent.get("status", "UNKNOWN")
        agent_type = agent.get("agent_type", "UNKNOWN")
        
        state["by_status"][status] += 1
        state["by_type"][agent_type] += 1
        
        if status == "BLOCKED":
            state["blocked"].append({
                "agent_id": agent.get("agent_id"),
                "current_task": agent.get("current_task", "unknown")
            })
        
        if status == "WAITING_REVIEW":
            state["waiting_review"].append({
                "agent_id": agent.get("agent_id"),
                "outputs": agent.get("outputs", [])
            })
    
    # Analyze recent audit entries
    recent_entries = sorted(audit_log, key=lambda x: x.get("timestamp", ""), reverse=True)[:20]
    for entry in recent_entries:
        if entry.get("event_type") == "error":
            state["errors"].append({
                "agent_id": entry.get("agent_id", "unknown"),
                "message": entry.get("message", "unknown error"),
                "timestamp": entry.get("timestamp", "unknown")
            })
    
    return state


def generate_dashboard_html(
    agent_state: Dict[str, Any],
    artifacts: Dict[str, Any],
    audit_summary: Dict[str, Any]
) -> str:
    """Generate debug dashboard HTML."""
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent Orchestrator - Debug Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }}
        
        .header {{
            background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
            color: white;
            padding: 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }}
        
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .card {{
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .card h2 {{
            color: #1e40af;
            margin-bottom: 1rem;
            font-size: 1.25rem;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 0.5rem;
        }}
        
        .stat {{
            display: flex;
            justify-content: space-between;
            padding: 0.5rem 0;
            border-bottom: 1px solid #f3f4f6;
        }}
        
        .stat:last-child {{
            border-bottom: none;
        }}
        
        .stat-label {{
            color: #666;
        }}
        
        .stat-value {{
            font-weight: bold;
            color: #1e40af;
        }}
        
        .error-item {{
            background: #fee2e2;
            border-left: 4px solid #dc2626;
            padding: 0.75rem;
            margin-bottom: 0.5rem;
            border-radius: 4px;
        }}
        
        .error-item .agent {{
            font-weight: bold;
            color: #991b1b;
        }}
        
        .error-item .message {{
            color: #7f1d1d;
            font-size: 0.9em;
            margin-top: 0.25rem;
        }}
        
        .blocked-item {{
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 0.75rem;
            margin-bottom: 0.5rem;
            border-radius: 4px;
        }}
        
        .review-item {{
            background: #dbeafe;
            border-left: 4px solid #3b82f6;
            padding: 0.75rem;
            margin-bottom: 0.5rem;
            border-radius: 4px;
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 500;
            margin-right: 0.5rem;
        }}
        
        .status-RUNNING {{
            background: #d1fae5;
            color: #065f46;
        }}
        
        .status-WAITING_REVIEW {{
            background: #dbeafe;
            color: #1e40af;
        }}
        
        .status-BLOCKED {{
            background: #fee2e2;
            color: #991b1b;
        }}
        
        .status-FAILED {{
            background: #fee2e2;
            color: #dc2626;
        }}
        
        .status-IDLE {{
            background: #f3f4f6;
            color: #374151;
        }}
        
        .list-item {{
            padding: 0.5rem;
            margin-bottom: 0.25rem;
            background: #f9fafb;
            border-radius: 4px;
            font-size: 0.9em;
        }}
        
        .timestamp {{
            color: #666;
            font-size: 0.85em;
        }}
        
        .empty-state {{
            text-align: center;
            padding: 2rem;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 Agent Orchestrator - Debug Dashboard</h1>
        <div>System state, errors, and dependencies</div>
        <div style="margin-top: 0.5rem; font-size: 0.9em; opacity: 0.9;">
            Generated: {datetime.utcnow().isoformat()}Z
        </div>
    </div>
    
    <div class="container">
        <div class="grid">
            <!-- Agent State -->
            <div class="card">
                <h2>Agent State</h2>
                <div class="stat">
                    <span class="stat-label">Total Agents</span>
                    <span class="stat-value">{agent_state['total_agents']}</span>
                </div>
"""
    
    # Add status breakdown
    for status, count in agent_state['by_status'].items():
        html += f"""
                <div class="stat">
                    <span class="stat-label">
                        <span class="status-badge status-{status}">{status}</span>
                    </span>
                    <span class="stat-value">{count}</span>
                </div>
"""
    
    html += """
            </div>
            
            <!-- Artifacts -->
            <div class="card">
                <h2>Artifacts</h2>
                <div class="stat">
                    <span class="stat-label">Total Artifacts</span>
                    <span class="stat-value">""" + str(artifacts['total']) + """</span>
                </div>
"""
    
    # Add artifact type breakdown
    for artifact_type, items in list(artifacts['by_type'].items())[:10]:
        html += f"""
                <div class="stat">
                    <span class="stat-label">{artifact_type}</span>
                    <span class="stat-value">{len(items)}</span>
                </div>
"""
    
    html += """
            </div>
            
            <!-- Errors -->
            <div class="card">
                <h2>Recent Errors</h2>
"""
    
    if agent_state['errors']:
        for error in agent_state['errors'][:10]:
            html += f"""
                <div class="error-item">
                    <div class="agent">{error.get('agent_id', 'unknown')}</div>
                    <div class="message">{error.get('message', 'unknown error')}</div>
                    <div class="timestamp">{error.get('timestamp', 'unknown')}</div>
                </div>
"""
    else:
        html += """
                <div class="empty-state">No recent errors</div>
"""
    
    html += """
            </div>
            
            <!-- Blocked Agents -->
            <div class="card">
                <h2>Blocked Agents</h2>
"""
    
    if agent_state['blocked']:
        for blocked in agent_state['blocked']:
            html += f"""
                <div class="blocked-item">
                    <div class="agent">{blocked.get('agent_id', 'unknown')}</div>
                    <div class="message">{blocked.get('current_task', 'unknown task')}</div>
                </div>
"""
    else:
        html += """
                <div class="empty-state">No blocked agents</div>
"""
    
    html += """
            </div>
            
            <!-- Waiting Review -->
            <div class="card">
                <h2>Waiting Review</h2>
"""
    
    if agent_state['waiting_review']:
        for waiting in agent_state['waiting_review']:
            outputs = waiting.get('outputs', [])
            html += f"""
                <div class="review-item">
                    <div class="agent">{waiting.get('agent_id', 'unknown')}</div>
                    <div class="message">{len(outputs)} output(s) pending review</div>
                </div>
"""
    else:
        html += """
                <div class="empty-state">No agents waiting for review</div>
"""
    
    html += """
            </div>
            
            <!-- Artifact Errors -->
            <div class="card">
                <h2>Artifact Errors</h2>
"""
    
    if artifacts['errors']:
        for error in artifacts['errors'][:10]:
            html += f"""
                <div class="error-item">
                    <div class="agent">{error.get('file', 'unknown')}</div>
                    <div class="message">{error.get('error', 'unknown error')}</div>
                </div>
"""
    else:
        html += """
                <div class="empty-state">No artifact errors</div>
"""
    
    html += """
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html


def main():
    """Main execution."""
    print("[INFO] Generating debug dashboard...")
    
    # Load data
    print("  Loading registry...")
    registry = load_registry()
    
    print("  Loading audit log...")
    audit_log = load_audit_log()
    
    print("  Scanning artifacts...")
    artifacts = scan_artifacts()
    
    print("  Analyzing agent state...")
    agent_state = analyze_agent_state(registry, audit_log)
    
    # Generate dashboard
    print("  Generating HTML...")
    html = generate_dashboard_html(agent_state, artifacts, {})
    
    # Save
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    dashboard_path = OUTPUT_DIR / "debug_dashboard.html"
    dashboard_path.write_text(html, encoding='utf-8')
    
    print(f"\n[SUCCESS] Debug dashboard generated!")
    print(f"View at: {dashboard_path}")
    
    # Print summary
    print(f"\n[SUMMARY]")
    print(f"   Agents: {agent_state['total_agents']}")
    print(f"   Artifacts: {artifacts['total']}")
    print(f"   Errors: {len(agent_state['errors'])}")
    print(f"   Blocked: {len(agent_state['blocked'])}")
    print(f"   Waiting Review: {len(agent_state['waiting_review'])}")
    
    return dashboard_path


if __name__ == "__main__":
    result = main()
    if not result:
        sys.exit(1)
