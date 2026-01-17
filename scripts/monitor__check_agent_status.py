"""
Script: monitor__check_agent_status.py
Intent: temporal (read-only status check)
Reads: agent-registry.json, system processes, API health
Writes: None (stdout only)
Purpose: Comprehensive agent status check that verifies registry AND running processes
"""

import json
import sys
import subprocess
import io
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass  # Fallback to default encoding if this fails

BASE_DIR = Path(__file__).parent.parent
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
API_BASE_URL = "http://localhost:8000"

# Try to import requests
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️  Warning: requests library not available. API checks will be skipped.")

def parse_timestamp(ts_str: str) -> Optional[datetime]:
    """Parse ISO timestamp to datetime object"""
    try:
        ts_str = ts_str.replace('Z', '+00:00')
        return datetime.fromisoformat(ts_str)
    except:
        return None

def format_age(seconds: float) -> str:
    """Format age in human-readable format"""
    if seconds < 60:
        return f"{int(seconds)}s ago"
    elif seconds < 3600:
        return f"{int(seconds // 60)}m {int(seconds % 60)}s ago"
    else:
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        return f"{hours}h {mins}m ago"

def check_api_health() -> Tuple[bool, Optional[Dict]]:
    """Check if orchestrator API is running and healthy"""
    if not REQUESTS_AVAILABLE:
        return False, None
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            return True, response.json()
        return False, None
    except Exception as e:
        return False, {"error": str(e)}

def check_running_python_processes() -> List[Dict[str, str]]:
    """Check which Python processes are currently running with command lines
    
    Returns list of dicts with 'pid' and 'cmdline' keys for better matching
    """
    running_processes = []
    
    try:
        if sys.platform == 'win32':
            # Windows: Use wmic to get command lines (more reliable than tasklist)
            try:
                result = subprocess.run(
                    ['wmic', 'process', 'where', "name='python.exe'", 'get', 'ProcessId,CommandLine', '/format:csv'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                lines = result.stdout.strip().split('\n')
                for line in lines[2:]:  # Skip header lines
                    if not line.strip() or 'ProcessId' in line:
                        continue
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 3 and parts[-2] and parts[-1]:  # PID and CommandLine
                        running_processes.append({
                            'pid': parts[-2],
                            'cmdline': parts[-1].lower() if parts[-1] else ''
                        })
            except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
                # Fallback: Use PowerShell Get-Process if wmic unavailable
                try:
                    ps_cmd = "Get-Process python* | ForEach-Object { $_.Id.ToString() + '|' + (Get-CimInstance Win32_Process -Filter \"ProcessId = $($_.Id)\").CommandLine }"
                    result = subprocess.run(
                        ['powershell', '-Command', ps_cmd],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    for line in result.stdout.strip().split('\n'):
                        if '|' in line:
                            pid, cmdline = line.split('|', 1)
                            running_processes.append({
                                'pid': pid.strip(),
                                'cmdline': cmdline.strip().lower() if cmdline else ''
                            })
                except Exception:
                    # Final fallback: just check for python.exe (no command line)
                    result = subprocess.run(
                        ['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    lines = result.stdout.strip().split('\n')
                    for line in lines[1:]:
                        if 'python.exe' in line.lower():
                            running_processes.append({
                                'pid': 'unknown',
                                'cmdline': 'python.exe'  # Limited info
                            })
        else:
            # Linux/Mac: use ps with command line
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True,
                timeout=5
            )
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'python' in line.lower():
                    parts = line.split(None, 10)  # Split but keep last field intact (command)
                    if len(parts) >= 11:
                        running_processes.append({
                            'pid': parts[1] if len(parts) > 1 else 'unknown',
                            'cmdline': parts[10].lower() if len(parts) > 10 else line.lower()
                        })
    except Exception as e:
        print(f"⚠️  Error checking processes: {e}")
    
    return running_processes

def find_agent_processes(running_processes: List[Dict[str, str]], registry_agents: List[Dict]) -> Dict[str, bool]:
    """Match running processes to agent IDs using improved matching heuristics
    
    Uses multiple matching strategies:
    1. Direct agent_id in command line
    2. Normalized path matching (agent file path)
    3. Process name matching (fallback)
    """
    agent_running = {}
    
    # Extract agent IDs from registry
    agent_ids = [a.get("agent_id", "") for a in registry_agents]
    
    # Build agent file path patterns for matching
    agent_file_patterns = {}
    for agent_id in agent_ids:
        agent_file_patterns[agent_id] = [
            agent_id,  # Direct agent_id match
            f"{agent_id}.py",  # Agent file name
            f"agents/{agent_id}.py",  # Relative path
            f"agents\\{agent_id}.py",  # Windows path
        ]
    
    for agent_id in agent_ids:
        agent_running[agent_id] = False
        
        # Normalize agent_id for matching (handle underscores, case)
        agent_id_lower = agent_id.lower()
        agent_id_normalized = agent_id_lower.replace('_', '').replace('-', '')
        
        # Check each running process
        for proc in running_processes:
            cmdline = proc.get('cmdline', '')
            if not cmdline:
                continue
            
            # Strategy 1: Direct agent_id match in command line
            if agent_id in cmdline or agent_id_lower in cmdline:
                agent_running[agent_id] = True
                break
            
            # Strategy 2: File path pattern matching
            for pattern in agent_file_patterns[agent_id]:
                if pattern.lower() in cmdline:
                    agent_running[agent_id] = True
                    break
            
            if agent_running[agent_id]:
                break
            
            # Strategy 3: Normalized matching (handles path variations)
            # Extract filename from command line
            cmdline_normalized = cmdline.replace('\\', '/').replace('_', '').replace('-', '')
            if agent_id_normalized in cmdline_normalized:
                agent_running[agent_id] = True
                break
    
    return agent_running

def classify_agent_status(agent: Dict, now: datetime, agent_running_map: Dict[str, bool], stale_threshold_minutes: int = 30) -> str:
    """Classify agent status with STALE detection
    
    Returns: RUNNING, STALE, IDLE, WAITING_REVIEW, BLOCKED, RETIRED
    """
    registry_status = agent.get("status", "UNKNOWN")
    agent_id = agent.get("agent_id", "unknown")
    heartbeat_str = agent.get("last_heartbeat", "")
    heartbeat_dt = parse_timestamp(heartbeat_str)
    
    # Check if actually running
    is_actually_running = agent_running_map.get(agent_id, False)
    
    # STALE: Registry says RUNNING but no process AND old heartbeat
    if registry_status == "RUNNING":
        if not is_actually_running and heartbeat_dt:
            age_minutes = (now - heartbeat_dt).total_seconds() / 60
            if age_minutes > stale_threshold_minutes:
                return "STALE"
        # If process found, trust registry RUNNING
        if is_actually_running:
            return "RUNNING"
    
    # Return registry status for non-RUNNING states
    return registry_status

def check_running_agents(clean_stale: bool = False, stale_threshold_minutes: int = 30):
    """Check and display running agents"""
    print(f"\n{'='*80}")
    print(f"Agent Status Report - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"{'='*80}\n")
    
    # 1. Check API health
    print("🔍 Checking Orchestrator API...")
    api_running, api_data = check_api_health()
    if api_running:
        print(f"  ✅ Orchestrator API is RUNNING")
        if api_data:
            print(f"     Status: {api_data.get('status', 'unknown')}")
            print(f"     Active workflows: {api_data.get('active_workflows', 0)}")
            print(f"     Workflows in error: {api_data.get('workflows_in_error', 0)}")
    else:
        print(f"  ❌ Orchestrator API is NOT RUNNING")
        if api_data and 'error' in api_data:
            print(f"     Error: {api_data['error']}")
        print(f"     To start: cd agent-orchestrator && python -m uvicorn app.main:app --reload --port 8000")
    print()
    
    # 2. Check registry
    if not REGISTRY_PATH.exists():
        print(f"❌ Registry not found: {REGISTRY_PATH}")
        return
    
    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    agents = registry.get("agents", [])
    now = datetime.now(timezone.utc)
    
    # Deduplicate by agent_id (keep most recent)
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
    
    unique_agents = list(seen.values())
    
    # 3. Check running processes
    print("🔍 Checking running Python processes...")
    running_processes = check_running_python_processes()
    print(f"  Found {len(running_processes)} Python process(es) running")
    
    # Match processes to agents (improved matching)
    agent_running_map = find_agent_processes(running_processes, unique_agents)
    
    # 4. Classify agents with STALE detection
    classified_agents = []
    stale_count = 0
    for agent in unique_agents:
        classified_status = classify_agent_status(agent, now, agent_running_map, stale_threshold_minutes)
        if classified_status == "STALE":
            stale_count += 1
            # Create copy with updated status for display
            agent_copy = agent.copy()
            agent_copy["_classified_status"] = "STALE"
            agent_copy["_registry_status"] = agent.get("status", "UNKNOWN")
            classified_agents.append(agent_copy)
            
            # Clean stale if requested
            if clean_stale:
                agent["status"] = "STALE"
                heartbeat_age = "unknown"
                if agent.get('last_heartbeat'):
                    hb_dt = parse_timestamp(agent.get('last_heartbeat', ''))
                    if hb_dt:
                        heartbeat_age = format_age((now - hb_dt).total_seconds())
                agent["current_task"] = f"Marked STALE: registry showed RUNNING but no process found (heartbeat {heartbeat_age} ago)"
        else:
            agent_copy = agent.copy()
            agent_copy["_classified_status"] = classified_status
            classified_agents.append(agent_copy)
    
    # 5. Group by classified status
    by_status = defaultdict(list)
    for agent in classified_agents:
        status = agent.get("_classified_status", agent.get("status", "UNKNOWN"))
        by_status[status].append(agent)
    
    # 6. Save registry if cleaned
    if clean_stale and stale_count > 0:
        # Update ALL registry entries matching STALE agents (handle duplicates)
        # GOVERNANCE: Only update status, preserve audit trail (never delete)
        stale_agent_ids = {a.get("agent_id") for a in classified_agents if a.get("_classified_status") == "STALE"}
        updated_count = 0
        
        for i, agent in enumerate(agents):
            agent_id = agent.get("agent_id")
            if agent_id in stale_agent_ids:
                # Update all entries for this agent_id that are still RUNNING (handle duplicates)
                if agent.get("status") == "RUNNING":  # Only update if still RUNNING (avoid overwriting already-updated entries)
                    heartbeat_age = "unknown"
                    if agent.get('last_heartbeat'):
                        hb_dt = parse_timestamp(agent.get('last_heartbeat', ''))
                        if hb_dt:
                            heartbeat_age = format_age((now - hb_dt).total_seconds())
                    
                    agents[i]["status"] = "STALE"
                    agents[i]["current_task"] = f"Marked STALE: registry showed RUNNING but no process found (heartbeat {heartbeat_age} ago)"
                    # Preserve original heartbeat for audit trail
                    updated_count += 1
        
        if updated_count > 0:
            registry["agents"] = agents
            registry["_meta"]["last_updated"] = now.isoformat()
            with open(REGISTRY_PATH, 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=2)
            print(f"\n✅ Registry updated: {updated_count} agent entry/entries marked as STALE")
            print(f"   GOVERNANCE: Entries preserved for audit trail (no deletions)")
        else:
            print(f"\nℹ️  No registry entries needed updating (already marked as STALE or status changed)")
    
    # 7. Display summary
    print(f"\n📊 Status Summary (registry + process verification):")
    for status in ["RUNNING", "STALE", "IDLE", "WAITING_REVIEW", "BLOCKED", "RETIRED"]:
        count = len(by_status.get(status, []))
        emoji = {
            "RUNNING": "🟢",
            "STALE": "🟠",  # Orange for stale
            "IDLE": "⚪",
            "WAITING_REVIEW": "🟡",
            "BLOCKED": "🔴",
            "RETIRED": "⚫"
        }.get(status, "⚪")
        print(f"  {emoji} {status}: {count}")
    
    # 8. Display STALE agents (registry mismatch)
    stale = by_status.get("STALE", [])
    if stale:
        print(f"\n🟠 STALE Agents ({len(stale)}):")
        print("  (Registry shows RUNNING but no process found - likely crashed/exited)")
        print("-" * 80)
        for agent in stale:
            agent_id = agent.get("agent_id", "unknown")
            agent_type = agent.get("agent_type", "unknown")
            task = agent.get("current_task", "No task")
            heartbeat_str = agent.get("last_heartbeat", "")
            heartbeat_dt = parse_timestamp(heartbeat_str)
            
            age_str = "unknown"
            if heartbeat_dt:
                age_seconds = (now - heartbeat_dt).total_seconds()
                age_str = format_age(age_seconds)
            
            print(f"  • {agent_id}")
            print(f"    Type: {agent_type}")
            print(f"    Registry status: {agent.get('_registry_status', 'UNKNOWN')}")
            print(f"    Last heartbeat: {age_str}")
            print(f"    ⚠️  Agent likely crashed or exited without updating registry")
            print()
    
    # 9. Display RUNNING agents in detail (verified with processes)
    running = by_status.get("RUNNING", [])
    if running:
        print(f"\n🟢 RUNNING Agents ({len(running)}) - Verified with processes:")
        print("-" * 80)
        for agent in running:
            agent_id = agent.get("agent_id", "unknown")
            agent_type = agent.get("agent_type", "unknown")
            task = agent.get("current_task", "No task")
            heartbeat_str = agent.get("last_heartbeat", "")
            heartbeat_dt = parse_timestamp(heartbeat_str)
            
            age_str = "unknown"
            if heartbeat_dt:
                age_seconds = (now - heartbeat_dt).total_seconds()
                age_str = format_age(age_seconds)
            
            # Should be actually running if classified as RUNNING
            is_actually_running = agent_running_map.get(agent_id, False)
            process_indicator = "✅ Process verified" if is_actually_running else "⚠️  No process (classification may be wrong)"
            
            print(f"  • {agent_id}")
            print(f"    Type: {agent_type}")
            print(f"    Task: {task}")
            print(f"    Last heartbeat: {age_str}")
            print(f"    Process status: {process_indicator}")
            print()
    else:
        if not stale:
            print("\n⚠️  No agents currently RUNNING (according to registry + process verification)")
    
    # 10. Process Verification Summary
    print(f"\n🔍 Process Verification Summary:")
    registry_running = len([a for a in unique_agents if a.get("status") == "RUNNING"])
    actually_running = sum(1 for v in agent_running_map.values() if v)
    verified_running = len(by_status.get("RUNNING", []))
    
    print(f"  Registry reports: {registry_running} RUNNING agent(s)")
    print(f"  Processes found: {actually_running} agent process(es)")
    print(f"  Verified RUNNING: {verified_running} (registry + process match)")
    print(f"  STALE detected: {len(stale)} (registry says RUNNING, no process)")
    
    if stale:
        print(f"  ⚠️  {len(stale)} agent(s) marked as STALE (registry/process mismatch)")
        if not clean_stale:
            print(f"     Use --clean-stale flag to update registry")
    
    # 11. Display IDLE agents that should be running
    idle = by_status.get("IDLE", [])
    if idle:
        print(f"\n⚪ IDLE Agents ({len(idle)}):")
        print(f"  (Registered but not executing - these won't generate reports)")
        for agent in idle[:10]:  # Show first 10
            agent_id = agent.get("agent_id", "unknown")
            task = agent.get("current_task", "No task")
            print(f"  • {agent_id} - {task}")
        if len(idle) > 10:
            print(f"  ... and {len(idle) - 10} more")
    
    # 12. Recommendations
    print(f"\n💡 Recommendations:")
    recommendations = []
    if not api_running:
        recommendations.append("Start orchestrator API to enable agent spawning")
    if stale and not clean_stale:
        recommendations.append(f"Use --clean-stale flag to mark {len(stale)} STALE agent(s) in registry")
    if stale and clean_stale:
        recommendations.append(f"✅ {len(stale)} STALE agent(s) have been marked in registry")
    if idle:
        recommendations.append(f"{len(idle)} agents are IDLE - use execution__spawn_agents.py to activate them")
    if actually_running == 0 and verified_running == 0 and not idle:
        recommendations.append("No agents currently executing - use execution__spawn_agents.py to start")
    
    if not recommendations:
        recommendations.append("✅ System is healthy - no actions needed")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Check agent status with process verification")
    parser.add_argument("--clean-stale", action="store_true", 
                       help="Mark stale agents (RUNNING with no process) as STALE in registry")
    parser.add_argument("--stale-threshold", type=int, default=30,
                       help="Minutes since last heartbeat to consider stale (default: 30)")
    
    args = parser.parse_args()
    
    check_running_agents(
        clean_stale=args.clean_stale,
        stale_threshold_minutes=args.stale_threshold
    )
