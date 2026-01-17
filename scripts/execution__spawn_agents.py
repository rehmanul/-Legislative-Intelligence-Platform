"""
Script: execution__spawn_agents.py
Intent: snapshot (spawns/executes agents)
Reads: agent-registry.json, orchestrator API
Writes: agent-registry.json (via agent execution)
Purpose: Spawn/execute agents that are currently IDLE to generate reports
"""

import json
import sys
import subprocess
import io
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

BASE_DIR = Path(__file__).parent.parent
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"
AGENTS_DIR = BASE_DIR / "agents"
API_BASE_URL = "http://localhost:8000"
WORKFLOW_ID = "default"  # Default workflow ID

# Try to import requests
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️  Warning: requests library not available. API spawning will be skipped.")
    print("   Will fall back to direct agent execution.")

def check_api_available() -> bool:
    """Check if orchestrator API is available"""
    if not REQUESTS_AVAILABLE:
        return False
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def spawn_agent_via_api(agent_id: str, agent_type: str, scope: str, risk_level: str) -> bool:
    """Spawn agent via orchestrator API"""
    if not REQUESTS_AVAILABLE:
        return False
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/workflows/{WORKFLOW_ID}/agents/spawn",
            json={
                "agent_id": agent_id,
                "agent_type": agent_type,
                "scope": scope,
                "risk_level": risk_level
            },
            timeout=10
        )
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"    ❌ API spawn failed: {e}")
        return False

def check_running_python_processes() -> List[Dict[str, str]]:
    """Check running Python processes (same as monitor script for consistency)"""
    running_processes = []
    
    try:
        if sys.platform == 'win32':
            try:
                result = subprocess.run(
                    ['wmic', 'process', 'where', "name='python.exe'", 'get', 'ProcessId,CommandLine', '/format:csv'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                lines = result.stdout.strip().split('\n')
                for line in lines[2:]:
                    if not line.strip() or 'ProcessId' in line:
                        continue
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 3 and parts[-2] and parts[-1]:
                        running_processes.append({
                            'pid': parts[-2],
                            'cmdline': parts[-1].lower() if parts[-1] else ''
                        })
            except Exception:
                # Fallback: PowerShell
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
                    pass
        else:
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True,
                timeout=5
            )
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'python' in line.lower():
                    parts = line.split(None, 10)
                    if len(parts) >= 11:
                        running_processes.append({
                            'pid': parts[1] if len(parts) > 1 else 'unknown',
                            'cmdline': parts[10].lower() if len(parts) > 10 else line.lower()
                        })
    except Exception:
        pass
    
    return running_processes

def check_agent_already_running(agent_id: str) -> Tuple[bool, str]:
    """Check if agent is already running (conflict detection)
    
    Returns: (is_running, reason)
    """
    # Check registry
    if not REGISTRY_PATH.exists():
        return False, "registry_not_found"
    
    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    agents = registry.get("agents", [])
    for agent in agents:
        if agent.get("agent_id") == agent_id:
            status = agent.get("status", "")
            if status == "RUNNING":
                return True, "registry_shows_running"
            if status == "BLOCKED":
                return True, "agent_is_blocked"
            break
    
    # Check running processes
    running_processes = check_running_python_processes()
    agent_id_lower = agent_id.lower()
    agent_file_pattern = f"{agent_id}.py"
    
    for proc in running_processes:
        cmdline = proc.get('cmdline', '')
        if agent_id in cmdline or agent_id_lower in cmdline:
            return True, "process_found"
        if agent_file_pattern in cmdline:
            return True, "process_found"
    
    return False, "not_running"

def execute_agent_directly(agent_id: str) -> bool:
    """Execute agent Python script directly"""
    agent_file = AGENTS_DIR / f"{agent_id}.py"
    
    if not agent_file.exists():
        print(f"    ⚠️  Agent file not found: {agent_file}")
        return False
    
    try:
        # Execute agent script
        result = subprocess.run(
            [sys.executable, str(agent_file)],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            return True
        else:
            print(f"    ❌ Agent execution failed (exit code {result.returncode})")
            if result.stderr:
                print(f"    Error: {result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"    ⚠️  Agent execution timed out (may still be running)")
        return True  # Consider timeout as success (agent is running)
    except Exception as e:
        print(f"    ❌ Failed to execute agent: {e}")
        return False

def spawn_idle_agents(max_agents: int = 5, agent_types: Optional[List[str]] = None, use_api: bool = True, allow_execution_agents: bool = False):
    """Spawn IDLE agents that should be running
    
    GOVERNANCE GUARDRAILS:
    - EXECUTION agents require explicit --allow-execution flag (never auto-spawn)
    - BLOCKED agents are never spawned (human-gated, requires explicit approval)
    - Conflict detection prevents double-spawning (checks registry + processes)
    """
    print(f"\n{'='*80}")
    print(f"Agent Execution Script")
    print(f"{'='*80}\n")
    
    # Check API availability
    api_available = check_api_available()
    if use_api and api_available:
        print(f"✅ Orchestrator API is available - will use API to spawn agents")
    elif use_api:
        print(f"⚠️  Orchestrator API is not available - will execute agents directly")
        use_api = False
    else:
        print(f"ℹ️  Using direct agent execution (API mode disabled)")
    
    # Load registry to find IDLE agents
    if not REGISTRY_PATH.exists():
        print(f"❌ Registry not found: {REGISTRY_PATH}")
        return
    
    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    agents = registry.get("agents", [])
    
    # Filter for IDLE agents
    idle_agents = [
        a for a in agents 
        if a.get("status") == "IDLE" and a.get("current_task") != "Registered"
    ]
    
    # Also consider agents with status "Registered" as potential candidates
    registered_agents = [
        a for a in agents
        if a.get("status") == "IDLE" and a.get("current_task") == "Registered"
    ]
    
    # GOVERNANCE GUARDRAIL: Filter out EXECUTION agents unless explicitly allowed
    execution_agents_filtered = []
    if not allow_execution_agents:
        execution_agents_filtered = [a for a in idle_agents + registered_agents if a.get("agent_type") == "Execution"]
        idle_agents = [a for a in idle_agents if a.get("agent_type") != "Execution"]
        registered_agents = [a for a in registered_agents if a.get("agent_type") != "Execution"]
        if execution_agents_filtered:
            print(f"🔒 GOVERNANCE: {len(execution_agents_filtered)} EXECUTION agent(s) filtered (require --allow-execution flag)")
            print(f"   EXECUTION agents require explicit human approval and cannot be auto-spawned\n")
    
    # GOVERNANCE GUARDRAIL: Filter out BLOCKED agents (never spawn)
    blocked_agents = [a for a in agents if a.get("status") == "BLOCKED"]
    if blocked_agents:
        print(f"🔒 GOVERNANCE: {len(blocked_agents)} BLOCKED agent(s) skipped (human-gated, requires explicit approval)")
        print(f"   BLOCKED agents cannot be spawned automatically - they require human intervention\n")
    
    # Filter by agent type if specified
    if agent_types:
        idle_agents = [a for a in idle_agents if a.get("agent_type") in agent_types]
        registered_agents = [a for a in registered_agents if a.get("agent_type") in agent_types]
    
    # Prioritize learning agents for report generation
    learning_agents = [a for a in idle_agents if a.get("agent_type") == "Learning"]
    other_agents = [a for a in idle_agents if a.get("agent_type") != "Learning"]
    
    # Combine: learning agents first, then others
    agents_to_spawn = (learning_agents + other_agents + registered_agents)[:max_agents]
    
    if not agents_to_spawn:
        print(f"ℹ️  No IDLE agents found to spawn")
        print(f"   Current registry shows {len(agents)} total agents")
        print(f"   Filtered: {len(idle_agents)} IDLE (non-Registered), {len(registered_agents)} Registered")
        if execution_agents_filtered:
            print(f"   Blocked: {len(execution_agents_filtered)} EXECUTION agents (use --allow-execution to include)")
        return
    
    print(f"Found {len(agents_to_spawn)} agent(s) to spawn (showing first {max_agents})")
    print(f"  - {len(learning_agents)} Learning agents (prioritized for reports)")
    print(f"  - {len(other_agents)} Other agents")
    print(f"  - {len(registered_agents)} Registered agents\n")
    
    success_count = 0
    failed_count = 0
    skipped_conflicts = 0
    
    for i, agent in enumerate(agents_to_spawn, 1):
        agent_id = agent.get("agent_id", "unknown")
        agent_type = agent.get("agent_type", "unknown")
        scope = agent.get("scope", "")
        risk_level = agent.get("risk_level", "MEDIUM")
        
        print(f"[{i}/{len(agents_to_spawn)}] Spawning {agent_id}")
        print(f"  Type: {agent_type}, Risk: {risk_level}")
        print(f"  Scope: {scope[:60]}...")
        
        # CONFLICT DETECTION: Check if agent already running
        is_running, reason = check_agent_already_running(agent_id)
        if is_running:
            print(f"  ⚠️  SKIPPED: Agent appears already running (reason: {reason})")
            print(f"     Conflict detection prevents double-spawning")
            skipped_conflicts += 1
            print()
            continue
        
        success = False
        if use_api and api_available:
            print(f"  Attempting via API...")
            success = spawn_agent_via_api(agent_id, agent_type, scope, risk_level)
            if not success:
                print(f"  Falling back to direct execution...")
                success = execute_agent_directly(agent_id)
        else:
            print(f"  Executing directly...")
            success = execute_agent_directly(agent_id)
        
        if success:
            print(f"  ✅ Successfully spawned {agent_id}\n")
            success_count += 1
        else:
            print(f"  ❌ Failed to spawn {agent_id}\n")
            failed_count += 1
    
    # Summary
    print(f"{'='*80}")
    print(f"Execution Summary:")
    print(f"  ✅ Successfully spawned: {success_count}")
    print(f"  ❌ Failed: {failed_count}")
    if skipped_conflicts > 0:
        print(f"  ⚠️  Skipped (conflicts): {skipped_conflicts}")
    print(f"{'='*80}\n")
    
    if success_count > 0:
        print(f"💡 Next steps:")
        print(f"  1. Check agent status: python scripts/monitor__check_agent_status.py")
        print(f"  2. Monitor dashboard: python monitoring/dashboard-terminal.py")
        print(f"  3. Check agent outputs in: {BASE_DIR / 'artifacts'}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Spawn/execute IDLE agents to generate reports",
        epilog="""
GOVERNANCE GUARDRAILS:
  - EXECUTION agents require --allow-execution flag (never auto-spawned)
  - BLOCKED agents are never spawned (human-gated)
  - Conflict detection prevents double-spawning (checks registry + processes)

Examples:
  # Spawn 5 Learning agents (safe, for reports)
  python execution__spawn_agents.py --type Learning --max 5
  
  # Spawn EXECUTION agents (requires explicit flag)
  python execution__spawn_agents.py --type Execution --allow-execution --max 1
        """
    )
    parser.add_argument("--max", type=int, default=5, help="Maximum number of agents to spawn (default: 5)")
    parser.add_argument("--type", action="append", help="Filter by agent type (can specify multiple times)")
    parser.add_argument("--direct", action="store_true", help="Force direct execution (skip API)")
    parser.add_argument("--allow-execution", action="store_true", 
                       help="Allow spawning EXECUTION agents (requires explicit flag - never auto-spawned)")
    
    args = parser.parse_args()
    
    spawn_idle_agents(
        max_agents=args.max,
        agent_types=args.type,
        use_api=not args.direct,
        allow_execution_agents=args.allow_execution
    )
