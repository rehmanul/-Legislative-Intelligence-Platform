# Agent Monitoring & Execution Scripts

This directory contains scripts to track agent status and ensure agents are running to generate reports.

## Quick Start

### Check Agent Status
```bash
# Windows (double-click or run from command line)
CHECK_AGENT_STATUS.bat

# Or from command line
python scripts/monitor__check_agent_status.py
```

### Spawn IDLE Agents
```bash
# Windows (double-click or run from command line)
SPAWN_AGENTS.bat

# Or from command line (spawn 5 agents)
python scripts/execution__spawn_agents.py --max 5

# Spawn only Learning agents
python scripts/execution__spawn_agents.py --max 3 --type Learning
```

## Scripts Overview

### 1. `monitor__check_agent_status.py`
**Purpose:** Comprehensive status check that verifies registry AND running processes

**What it does:**
- Checks if orchestrator API is running
- Checks running Python processes
- Compares registry status with actual processes
- Identifies mismatches (registry says RUNNING but no process)
- Shows detailed agent status breakdown

**Usage:**
```bash
python scripts/monitor__check_agent_status.py
```

**Output includes:**
- API health status
- Process count verification
- RUNNING agents with heartbeat age
- Warnings for stale/crashed agents
- IDLE agents that should be running
- Specific recommendations

### 2. `execution__spawn_agents.py`
**Purpose:** Spawn/execute IDLE agents to generate reports

**What it does:**
- Finds IDLE agents in registry
- Prioritizes Learning agents (for report generation)
- Spawns agents via API (if available) or direct execution
- Reports success/failure for each agent

**Usage:**
```bash
# Spawn 5 agents (default)
python scripts/execution__spawn_agents.py

# Spawn 10 agents
python scripts/execution__spawn_agents.py --max 10

# Spawn only Learning agents
python scripts/execution__spawn_agents.py --type Learning

# Spawn only Intelligence agents
python scripts/execution__spawn_agents.py --type Intelligence

# Force direct execution (skip API)
python scripts/execution__spawn_agents.py --direct
```

**Options:**
- `--max N`: Maximum number of agents to spawn (default: 5)
- `--type TYPE`: Filter by agent type (can specify multiple times)
- `--direct`: Force direct execution, skip API

### 3. `monitor__unified_status.py`
**Purpose:** Unified monitoring combining dashboard + process checking + activity analysis

**What it does:**
- Combines registry status, process verification, and activity analysis
- Shows comprehensive system health
- Provides actionable recommendations
- Supports watch mode for continuous monitoring

**Usage:**
```bash
# Single status check
python scripts/monitor__unified_status.py

# Watch mode (refresh every 30 seconds)
python scripts/monitor__unified_status.py --watch

# Watch mode with custom interval (60 seconds)
python scripts/monitor__unified_status.py --watch --interval 60
```

### 4. `setup__windows_scheduled_task.py`
**Purpose:** Set up Windows scheduled tasks for automated agent execution

**What it does:**
- Creates Windows scheduled tasks to run scripts periodically
- Can schedule agent spawning or status checking
- Lists and manages existing tasks

**Usage:**
```bash
# Create task to spawn agents every hour
python scripts/setup__windows_scheduled_task.py --create --spawn-agents --interval 60

# Create task to check status every 30 minutes
python scripts/setup__windows_scheduled_task.py --create --check-status --interval 30

# List all agent orchestrator tasks
python scripts/setup__windows_scheduled_task.py --list

# Delete a task
python scripts/setup__windows_scheduled_task.py --delete --task-name AgentOrchestrator_SpawnAgents
```

## Common Workflows

### Daily Check
```bash
# 1. Check current status
python scripts/monitor__check_agent_status.py

# 2. If agents are IDLE, spawn them
python scripts/execution__spawn_agents.py --max 5

# 3. Verify they started
python scripts/monitor__check_agent_status.py
```

### Automated Execution (Windows)
```bash
# 1. Set up scheduled task to spawn agents every hour
python scripts/setup__windows_scheduled_task.py --create --spawn-agents --interval 60

# 2. Set up scheduled task to check status every 30 minutes
python scripts/setup__windows_scheduled_task.py --create --check-status --interval 30

# 3. Verify tasks were created
python scripts/setup__windows_scheduled_task.py --list
```

### Continuous Monitoring
```bash
# Watch mode - refreshes every 30 seconds
python scripts/monitor__unified_status.py --watch
```

## Troubleshooting

### Problem: Script says "Orchestrator API is NOT RUNNING"
**Solution:** Start the orchestrator API:
```bash
cd agent-orchestrator
python -m uvicorn app.main:app --reload --port 8000
```

### Problem: Registry shows RUNNING but no process found
**Solution:** Agents crashed or exited without updating registry. Spawn them again:
```bash
python scripts/execution__spawn_agents.py --max 5
```

### Problem: All agents are IDLE
**Solution:** Agents are registered but not executing. Spawn them:
```bash
# Spawn Learning agents (prioritized for reports)
python scripts/execution__spawn_agents.py --type Learning --max 5

# Or spawn all types
python scripts/execution__spawn_agents.py --max 10
```

### Problem: Scheduled task not working
**Solution:** Check task exists and is enabled:
```bash
# List tasks
python scripts/setup__windows_scheduled_task.py --list

# Check Windows Task Scheduler GUI
# Open: Task Scheduler (taskschd.msc)
# Look for: AgentOrchestrator_SpawnAgents or AgentOrchestrator_CheckStatus
```

## Understanding Status Indicators

### Agent Statuses
- 🟢 **RUNNING**: Agent is executing (should have matching Python process)
- ⚪ **IDLE**: Agent is registered but not executing (won't generate reports)
- 🟡 **WAITING_REVIEW**: Agent produced output, waiting for human review
- 🔴 **BLOCKED**: Agent is blocked (e.g., waiting for authorization)
- ⚫ **RETIRED**: Agent completed or was auto-retired

### Health Indicators
- ✅ **Healthy**: Agent has recent heartbeat and running normally
- ❌ **Unhealthy**: Agent has stale heartbeat or stuck
- ⚠️ **Warning**: Registry shows RUNNING but no process found (agent crashed)

## Best Practices

1. **Check status regularly** - Use `monitor__check_agent_status.py` to verify agents are actually running
2. **Spawn agents when IDLE** - Use `execution__spawn_agents.py` to activate IDLE agents for report generation
3. **Monitor for mismatches** - If registry shows RUNNING but no process, agents likely crashed
4. **Prioritize Learning agents** - Learning agents generate reports, prioritize them when spawning
5. **Set up automation** - Use scheduled tasks for hands-off operation

## File Locations

- **Registry:** `agent-orchestrator/registry/agent-registry.json`
- **Agents:** `agent-orchestrator/agents/`
- **Outputs:** `agent-orchestrator/artifacts/{agent_id}/`
- **Audit Log:** `agent-orchestrator/audit/audit-log.jsonl`

## Notes

- The dashboard script (`monitoring/dashboard-terminal.py`) runs continuously but must be started manually
- Registry only updates when agents execute - if agents don't run, registry won't update
- Process verification compares registry status with actual running processes - mismatches indicate stale registry entries
- Scheduled tasks require Windows Task Scheduler - for Linux/Mac, use cron instead
