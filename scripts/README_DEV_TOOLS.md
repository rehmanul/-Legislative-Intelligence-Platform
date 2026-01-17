# Development Tools - README

**Purpose:** Collection of scripts for allocating agent resources to development work

---

## Quick Start

```powershell
# 1. Check current status
python scripts\dev__status_dashboard.py

# 2. Run integrated workflow (monitor + configure + spawn)
python scripts\dev__workflow.py

# 3. Or use individual tools:
python scripts\dev__monitor_resource_usage.py
python scripts\dev__configure_resource_allocation.py
python scripts\dev__spawn_intelligence_agents.py
```

---

## Available Tools

### 1. `dev__status_dashboard.py`
**Purpose:** Comprehensive development status dashboard

**Features:**
- System state overview
- Resource configuration display
- Agent statistics (total, active, development, production)
- Status and type breakdowns
- Active agents list with heartbeat timestamps
- Development agents tracking
- Recommendations based on resource usage

**Usage:**
```powershell
python scripts\dev__status_dashboard.py
```

**Output:** Read-only dashboard showing current system state

---

### 2. `dev__workflow.py`
**Purpose:** Integrated development workflow (all-in-one)

**Features:**
- Loads system state
- Analyzes resource usage
- Configures development environment
- Spawns development agents (if resources available)
- Provides next steps guidance

**Usage:**
```powershell
python scripts\dev__workflow.py
```

**Workflow Steps:**
1. Load system state
2. Analyze resources
3. Configure environment
4. Spawn development agents (if safe)

---

### 3. `dev__monitor_resource_usage.py`
**Purpose:** Monitor current agent resource usage

**Features:**
- Resource summary (total, active, utilization)
- Status breakdown
- Type breakdown
- Development vs production categorization
- Resource allocation recommendations

**Usage:**
```powershell
python scripts\dev__monitor_resource_usage.py
```

---

### 4. `dev__configure_resource_allocation.py`
**Purpose:** Configure development resource allocation settings

**Features:**
- Creates development configuration file
- Sets execution limits
- Configures priority levels
- Sets timeouts and retry configs
- Provides environment variable instructions

**Usage:**
```powershell
python scripts\dev__configure_resource_allocation.py
```

**Output:** `config/development_config.json`

---

### 5. `dev__spawn_intelligence_agents.py`
**Purpose:** Spawn Intelligence agents for development work

**Features:**
- Spawns only Intelligence agents (read-only, safe)
- Limits to 2 agents for development
- Assigns high priority (10)
- Tags with development metadata

**Usage:**
```powershell
python scripts\dev__spawn_intelligence_agents.py
```

---

### 6. `dev__batch_execute.py`
**Purpose:** Execute multiple development agents in batch

**Features:**
- Batch execution of Intelligence agents
- Configurable concurrent execution limit
- High priority assignment
- Development metadata tagging

**Usage:**
```powershell
python scripts\dev__batch_execute.py
```

**Note:** Executes all Intelligence agents for current legislative state

---

## Tool Comparison

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `dev__status_dashboard.py` | View comprehensive status | Check current state, get overview |
| `dev__workflow.py` | Integrated workflow | Quick start, all-in-one |
| `dev__monitor_resource_usage.py` | Monitor resources | Check if can spawn agents |
| `dev__configure_resource_allocation.py` | Configure limits | First-time setup |
| `dev__spawn_intelligence_agents.py` | Spawn agents | Spawn specific agents |
| `dev__batch_execute.py` | Batch execute | Execute multiple agents |

---

## Typical Workflows

### Workflow 1: Quick Development Start
```powershell
# One command does everything
python scripts\dev__workflow.py
```

### Workflow 2: Step-by-Step Development
```powershell
# 1. Check status
python scripts\dev__status_dashboard.py

# 2. Configure (if needed)
python scripts\dev__configure_resource_allocation.py

# 3. Spawn agents
python scripts\dev__spawn_intelligence_agents.py

# 4. Monitor progress
python scripts\dev__monitor_resource_usage.py
```

### Workflow 3: Batch Development
```powershell
# Execute all Intelligence agents for current state
python scripts\dev__batch_execute.py

# Monitor progress
python scripts\dev__status_dashboard.py
```

---

## Safety Features

All development tools:
- ✅ Spawn only Intelligence agents (read-only, safe)
- ✅ Limit concurrent execution
- ✅ Assign high priority to development
- ✅ Tag with development metadata
- ✅ Do not modify system state
- ✅ Do not advance workflows
- ✅ Respect review gates and blocking rules

---

## Configuration

Development tools read from:
- `state/legislative-state.json` - Current workflow state
- `registry/agent-registry.json` - Agent registry
- `config/development_config.json` - Development configuration (optional)

---

## Output Locations

- **Configuration:** `config/development_config.json`
- **Agent Outputs:** `artifacts/<agent_id>/`
- **Registry Updates:** `registry/agent-registry.json` (read-only from tools)

---

## Troubleshooting

### Issue: "No Intelligence agents found for state"
**Solution:** Check that current legislative state has Intelligence agents defined in `dev__batch_execute.py`

### Issue: "High resource usage"
**Solution:** Wait for current agents to complete or increase `MAX_CONCURRENT_AGENTS`

### Issue: "Failed to import modules"
**Solution:** Ensure you're running from `agent-orchestrator` directory and dependencies are installed

---

## Related Documentation

- `docs/AGENT_RESOURCE_ALLOCATION_GUIDE.md` - Complete guide
- `docs/DEVELOPMENT_QUICK_START.md` - Quick reference
- `artifacts/development/RESOURCE_ALLOCATION_SUMMARY.json` - Summary

---

**Last Updated:** 2026-01-20
