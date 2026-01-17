"""
Script: monitor__unified_status.py
Intent: temporal (read-only status check)
Reads: agent-registry.json, system processes, API health, audit log
Writes: None (stdout only)
Purpose: Unified monitoring that combines dashboard + process checking + activity analysis
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from typing import Dict, List, Optional

# Add parent to path for imports
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

# Import monitoring functions from dashboard using importlib (dashboard-terminal.py has hyphen)
import importlib.util
dashboard_path = BASE_DIR / "monitoring" / "dashboard-terminal.py"

if dashboard_path.exists():
    try:
        spec = importlib.util.spec_from_file_location("dashboard_terminal", dashboard_path)
        if spec and spec.loader:
            dashboard_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(dashboard_module)
            load_json = dashboard_module.load_json
            parse_timestamp = dashboard_module.parse_timestamp
            format_age = dashboard_module.format_duration  # Use format_duration as format_age
            deduplicate_agents = dashboard_module.deduplicate_agents
            check_agent_health = dashboard_module.check_agent_health
            analyze_recent_activity = dashboard_module.analyze_recent_activity
        else:
            raise ImportError("Could not create module spec")
    except Exception as e:
        print(f"⚠️  Warning: Could not load dashboard module: {e}")
        print(f"   Using fallback functions")
        # Fall to fallback functions below
        dashboard_module = None
else:
    dashboard_module = None

if not dashboard_module or not dashboard_path.exists():
    # Fallback functions if dashboard not found
    def load_json(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def parse_timestamp(ts_str):
        try:
            ts_str = ts_str.replace('Z', '+00:00')
            return datetime.fromisoformat(ts_str)
        except:
            return None
    
    def format_age(seconds):
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds // 60)}m"
        else:
            hours = int(seconds // 3600)
            mins = int((seconds % 3600) // 60)
            return f"{hours}h {mins}m"
    
    def deduplicate_agents(agents):
        seen = {}
        for agent in agents:
            agent_id = agent.get("agent_id", "unknown")
            if agent_id not in seen:
                seen[agent_id] = agent
            else:
                current_ts = parse_timestamp(agent.get("last_heartbeat", ""))
                existing_ts = parse_timestamp(seen[agent_id].get("last_heartbeat", ""))
                if current_ts and existing_ts and current_ts > existing_ts:
                    seen[agent_id] = agent
        return list(seen.values())
    
    def check_agent_health(agent, now):
        status = agent.get("status", "")
        heartbeat_str = agent.get("last_heartbeat", "")
        heartbeat_dt = parse_timestamp(heartbeat_str)
        
        if not heartbeat_dt:
            if status == "RUNNING":
                return (False, "NO_HEARTBEAT", 0)
            return (True, None, 0)
        
        age_seconds = (now - heartbeat_dt).total_seconds()
        if status == "RUNNING" and age_seconds > 15 * 60:  # 15 minutes
            return (False, "STALE_HEARTBEAT", age_seconds)
        if status == "RUNNING":
            spawned_dt = parse_timestamp(agent.get("spawned_at", ""))
            if spawned_dt:
                running_duration = (now - spawned_dt).total_seconds()
                if running_duration > 30 * 60:  # 30 minutes
                    return (False, "STUCK", running_duration)
        return (True, None, age_seconds)
    
    def analyze_recent_activity(hours=24):
        return {}

REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
AUDIT_LOG_PATH = BASE_DIR / "audit" / "audit-log.jsonl"
API_BASE_URL = "http://localhost:8000"

# Try to import requests
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

def check_api_health() -> tuple[bool, Optional[Dict]]:
    """Check if orchestrator API is running"""
    if not REQUESTS_AVAILABLE:
        return False, None
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            return True, response.json()
        return False, None
    except:
        return False, None

def get_unified_status(refresh: bool = True):
    """Get unified status combining all monitoring sources"""
    now = datetime.now(timezone.utc)
    
    print(f"\n{'='*80}")
    print(f"Unified Agent Status Report")
    print(f"Generated: {now.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"{'='*80}\n")
    
    # 1. API Health
    print("🔍 System Health:")
    api_running, api_data = check_api_health()
    if api_running:
        print(f"  ✅ Orchestrator API: RUNNING")
        if api_data:
            print(f"     Active workflows: {api_data.get('active_workflows', 0)}")
            print(f"     Workflows in error: {api_data.get('workflows_in_error', 0)}")
    else:
        print(f"  ❌ Orchestrator API: NOT RUNNING")
    print()
    
    # 2. Registry Status
    if not REGISTRY_PATH.exists():
        print(f"❌ Registry not found: {REGISTRY_PATH}\n")
        return
    
    registry = load_json(REGISTRY_PATH)
    agents = deduplicate_agents(registry.get("agents", []))
    
    # Group by status
    by_status = defaultdict(list)
    by_type = defaultdict(list)
    healthy_count = 0
    unhealthy_count = 0
    
    for agent in agents:
        status = agent.get("status", "UNKNOWN")
        agent_type = agent.get("agent_type", "unknown")
        by_status[status].append(agent)
        by_type[agent_type].append(agent)
        
        is_healthy, issue, _ = check_agent_health(agent, now)
        if is_healthy:
            healthy_count += 1
        else:
            unhealthy_count += 1
    
    # Display status summary
    print("📊 Agent Status Summary:")
    status_order = ["RUNNING", "WAITING_REVIEW", "IDLE", "BLOCKED", "RETIRED"]
    status_emoji = {
        "RUNNING": "🟢",
        "WAITING_REVIEW": "🟡",
        "IDLE": "⚪",
        "BLOCKED": "🔴",
        "RETIRED": "⚫"
    }
    
    for status in status_order:
        count = len(by_status.get(status, []))
        emoji = status_emoji.get(status, "⚪")
        print(f"  {emoji} {status}: {count}")
    print(f"  ✅ Healthy: {healthy_count}")
    print(f"  ❌ Unhealthy: {unhealthy_count}")
    print()
    
    # 3. Activity Analysis
    print("📈 Recent Activity (last 24 hours):")
    activity = analyze_recent_activity(hours=24)
    if activity:
        print(f"  Task completions: {activity.get('task_completions', 0)}")
        print(f"  Errors: {activity.get('errors', 0)}")
        most_active = activity.get('most_active_agents', {})
        if most_active:
            print(f"  Most active agents:")
            for agent_id, count in list(most_active.items())[:5]:
                print(f"    • {agent_id}: {count} events")
    else:
        print(f"  ⚠️  Could not analyze activity (audit log may be empty)")
    print()
    
    # 4. RUNNING Agents Detail
    running = by_status.get("RUNNING", [])
    if running:
        print(f"🟢 RUNNING Agents ({len(running)}):")
        print("-" * 80)
        for agent in running:
            agent_id = agent.get("agent_id", "unknown")
            agent_type = agent.get("agent_type", "unknown")
            task = agent.get("current_task", "No task")
            heartbeat_str = agent.get("last_heartbeat", "")
            heartbeat_dt = parse_timestamp(heartbeat_str)
            
            is_healthy, issue, age_seconds = check_agent_health(agent, now)
            health_indicator = "✅" if is_healthy else f"❌ {issue}"
            
            if age_seconds:
                age_str = format_age(age_seconds)
            else:
                age_str = "unknown"
            
            print(f"  • {agent_id}")
            print(f"    Type: {agent_type} | Health: {health_indicator}")
            print(f"    Task: {task}")
            print(f"    Last heartbeat: {age_str} ago")
            
            if not is_healthy and issue:
                print(f"    ⚠️  Issue: {issue}")
            print()
    else:
        print("⚠️  No agents currently RUNNING")
        print()
    
    # 5. Recommendations
    print("💡 Recommendations:")
    recommendations = []
    
    if not api_running:
        recommendations.append("Start orchestrator API: cd agent-orchestrator && python -m uvicorn app.main:app --reload --port 8000")
    
    if unhealthy_count > 0:
        recommendations.append(f"Investigate {unhealthy_count} unhealthy agent(s)")
    
    if len(running) == 0:
        recommendations.append("No agents running - spawn agents: python scripts/execution__spawn_agents.py")
    
    idle_count = len(by_status.get("IDLE", []))
    if idle_count > 0:
        recommendations.append(f"Spawn {idle_count} IDLE agents to generate reports: python scripts/execution__spawn_agents.py --max 5")
    
    if not recommendations:
        recommendations.append("✅ System is healthy - no actions needed")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
    
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Unified agent status monitoring")
    parser.add_argument("--watch", action="store_true", help="Watch mode (refresh every 30 seconds)")
    parser.add_argument("--interval", type=int, default=30, help="Refresh interval in seconds (default: 30)")
    
    args = parser.parse_args()
    
    if args.watch:
        print("Starting watch mode (Ctrl+C to stop)...")
        try:
            while True:
                get_unified_status()
                print(f"Refreshing in {args.interval} seconds... (Ctrl+C to stop)\n")
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n\nWatch mode stopped by user")
    else:
        get_unified_status()
