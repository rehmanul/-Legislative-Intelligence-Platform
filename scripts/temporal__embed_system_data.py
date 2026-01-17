"""
Script: scripts/temporal__embed_system_data.py
Intent: temporal (generates embedded data)

Reads:
- registry/agent-registry.json
- execution/execution-status.json
- artifacts/ directory
- audit/audit-log.jsonl

Writes:
- dashboards/system_health_dashboard.html (with embedded data)
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

BASE_DIR = Path(__file__).parent.parent
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
EXECUTION_STATUS_PATH = BASE_DIR / "execution" / "execution-status.json"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
AUDIT_LOG_PATH = BASE_DIR / "audit" / "audit-log.jsonl"
DASHBOARD_TEMPLATE_PATH = BASE_DIR / "dashboards" / "system_health_dashboard.html"
OUTPUT_PATH = BASE_DIR / "dashboards" / "system_health_dashboard.html"


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    """Load JSON file."""
    try:
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"[WARNING] Failed to load {path}: {e}")
    return None


def load_artifacts() -> Dict[str, Dict[str, Any]]:
    """Load all JSON artifacts from artifacts directory."""
    artifacts = {}
    
    if not ARTIFACTS_DIR.exists():
        return artifacts
    
    # Load artifact index if it exists
    index_path = ARTIFACTS_DIR / "ARTIFACT_INDEX.json"
    if index_path.exists():
        artifacts["_index"] = load_json(index_path)
    
    # Load all JSON files from artifacts directory
    for json_file in ARTIFACTS_DIR.rglob("*.json"):
        if json_file.name == "ARTIFACT_INDEX.json":
            continue  # Already loaded
        
        relative_path = json_file.relative_to(BASE_DIR)
        data = load_json(json_file)
        if data:
            artifacts[str(relative_path).replace("\\", "/")] = data
    
    return artifacts


def load_audit_log() -> list:
    """Load audit log entries."""
    entries = []
    
    if not AUDIT_LOG_PATH.exists():
        return entries
    
    try:
        with open(AUDIT_LOG_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        print(f"[WARNING] Failed to load audit log: {e}")
    
    return entries


def embed_data_into_dashboard():
    """Embed system data into dashboard HTML."""
    print("[INFO] Loading system data...")
    
    # Load all data
    agent_registry = load_json(REGISTRY_PATH) or {}
    execution_status = load_json(EXECUTION_STATUS_PATH) or {}
    artifacts = load_artifacts()
    audit_log = load_audit_log()
    
    # Combine into system data object
    system_data = {
        "agentRegistry": agent_registry,
        "executionStatus": execution_status,
        "artifactIndex": artifacts.get("_index"),
        "artifacts": {k: v for k, v in artifacts.items() if k != "_index"},
        "auditLog": audit_log,
        "_meta": {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "source": "embedded"
        }
    }
    
    print(f"[INFO] Loaded {len(agent_registry.get('agents', []))} agents")
    print(f"[INFO] Loaded {len(system_data['artifacts'])} artifacts")
    print(f"[INFO] Loaded {len(audit_log)} audit log entries")
    
    # Read dashboard template
    print("[INFO] Reading dashboard template...")
    with open(DASHBOARD_TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Find the script section and replace/insert embedded data
    # Look for the systemData initialization or insert before closing script tag
    embedded_data_script = f"""
        // Embedded system data (generated at {datetime.utcnow().isoformat()})
        const EMBEDDED_SYSTEM_DATA = {json.dumps(system_data, indent=8)};
        
        // Auto-load embedded data on page load
        document.addEventListener('DOMContentLoaded', function() {{
            if (typeof EMBEDDED_SYSTEM_DATA !== 'undefined') {{
                systemData = EMBEDDED_SYSTEM_DATA;
                aggregateData();
                renderDashboard();
                document.getElementById('dashboardContent').style.display = 'block';
                document.getElementById('emptyState').style.display = 'none';
                document.getElementById('errorContainer').innerHTML = 
                    '<div class="info-message">✅ Loaded embedded system data automatically</div>';
                document.getElementById('lastUpdated').textContent = 
                    'Last updated: ' + new Date().toLocaleString();
            }}
        }});
    """
    
    # Insert embedded data before the closing script tag
    # Find the last </script> tag and insert before it
    script_end = html_content.rfind('</script>')
    if script_end != -1:
        html_content = (
            html_content[:script_end] + 
            embedded_data_script + 
            '\n    ' + 
            html_content[script_end:]
        )
    else:
        # If no script tag found, append before closing body
        body_end = html_content.rfind('</body>')
        if body_end != -1:
            html_content = (
                html_content[:body_end] +
                f'    <script>{embedded_data_script}</script>\n' +
                html_content[body_end:]
            )
    
    # Write updated dashboard
    print(f"[INFO] Writing dashboard to {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"[SUCCESS] Dashboard updated with embedded data!")
    print(f"[INFO] File size: {OUTPUT_PATH.stat().st_size / 1024:.1f} KB")
    print(f"[INFO] Open {OUTPUT_PATH} in your browser to view the dashboard")


if __name__ == "__main__":
    embed_data_into_dashboard()
