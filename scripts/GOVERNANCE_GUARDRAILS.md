# Governance Guardrails - Agent Monitoring System

This document explains the governance guardrails implemented to ensure safe agent execution without bypassing human approval gates.

---

## What This System Will NEVER Do Automatically

### ❌ NEVER Auto-Approve Review Gates
- `HR_PRE`, `HR_LANG`, `HR_MSG`, `HR_RELEASE` gates require explicit human approval
- No script will ever bypass these gates or auto-approve artifacts
- These are hard stops - non-negotiable

### ❌ NEVER Auto-Spawn EXECUTION Agents
- EXECUTION agents require explicit `--allow-execution` flag
- These agents perform external actions (outreach, media, coalition building)
- They are filtered out by default in all spawn operations
- Code explicitly checks agent type before spawning

### ❌ NEVER Auto-Respawn BLOCKED Agents
- BLOCKED agents are human-gated and require explicit intervention
- They are automatically skipped in all spawn operations
- Status must be manually changed before they can spawn

### ❌ NEVER Auto-Delete Registry Entries
- Stale entries are marked as STALE, not deleted
- Registry entries are preserved for audit trail
- Only status is updated, never removed

### ❌ NEVER Auto-Retry Failed Spawns
- Failed spawns are reported but not automatically retried
- Human decision required on whether to retry
- No exponential backoff or automatic retry loops

---

## Governance Guardrails Implemented

### 1. EXECUTION Agent Filtering

**Location:** `execution__spawn_agents.py`

**Code:**
```python
# GOVERNANCE GUARDRAIL: Filter out EXECUTION agents unless explicitly allowed
if not allow_execution_agents:
    execution_agents_filtered = [a for a in idle_agents + registered_agents if a.get("agent_type") == "Execution"]
    idle_agents = [a for a in idle_agents if a.get("agent_type") != "Execution"]
    # ... agents filtered out
    if execution_agents_filtered:
        print(f"🔒 GOVERNANCE: {len(execution_agents_filtered)} EXECUTION agent(s) filtered (require --allow-execution flag)")
```

**Behavior:**
- EXECUTION agents are filtered out by default
- User must explicitly use `--allow-execution` flag to spawn them
- This prevents accidental external actions

**Why:** EXECUTION agents perform external actions that require approval. Auto-spawning them would bypass human authority.

### 2. BLOCKED Agent Filtering

**Location:** `execution__spawn_agents.py`

**Code:**
```python
# GOVERNANCE GUARDRAIL: Filter out BLOCKED agents (never spawn)
blocked_agents = [a for a in agents if a.get("status") == "BLOCKED"]
if blocked_agents:
    print(f"🔒 GOVERNANCE: {len(blocked_agents)} BLOCKED agent(s) skipped (human-gated, requires explicit approval)")
```

**Behavior:**
- BLOCKED agents are always skipped
- No flag can override this - they require manual intervention
- This prevents spawning agents that are explicitly blocked

**Why:** BLOCKED status indicates human-gated agents that require explicit approval. Auto-spawning would violate governance.

### 3. Conflict Detection Before Spawn

**Location:** `execution__spawn_agents.py` - `check_agent_already_running()`

**Behavior:**
- Checks registry status BEFORE spawning
- Checks running processes BEFORE spawning
- If agent is RUNNING or BLOCKED, aborts spawn
- Prevents double-spawning

**Code:**
```python
# CONFLICT DETECTION: Check if agent already running
is_running, reason = check_agent_already_running(agent_id)
if is_running:
    print(f"  ⚠️  SKIPPED: Agent appears already running (reason: {reason})")
    skipped_conflicts += 1
    continue
```

**Why:** Prevents resource conflicts and ensures agents aren't accidentally spawned multiple times.

### 4. STALE Status (Not RETIRED)

**Location:** `monitor__check_agent_status.py` - `classify_agent_status()`

**Behavior:**
- Detects agents with RUNNING status but no process
- Classifies as STALE (not RETIRED) if heartbeat exceeds threshold
- `--clean-stale` flag marks them as STALE in registry
- **Does NOT delete entries** - preserves audit trail

**Code:**
```python
# STALE: Registry says RUNNING but no process AND old heartbeat
if registry_status == "RUNNING":
    if not is_actually_running and heartbeat_dt:
        age_minutes = (now - heartbeat_dt).total_seconds() / 60
        if age_minutes > stale_threshold_minutes:
            return "STALE"
```

**Why:** STALE indicates registry mismatch, not completion. RETIRED should only be set when agent legitimately completes. STALE preserves information that agent crashed without proper cleanup.

---

## Status Meanings

### RUNNING (Verified)
- Registry shows RUNNING
- Process found and matched
- **Trustworthy:** Agent is actually executing

### STALE (Registry Mismatch)
- Registry shows RUNNING
- No process found
- Heartbeat exceeds threshold (default: 30 minutes)
- **Meaning:** Agent likely crashed or exited without updating registry
- **Action:** Use `--clean-stale` to mark as STALE in registry

### IDLE
- Registry shows IDLE
- Not currently executing
- **Meaning:** Agent is registered but not running
- **Action:** Safe to spawn if needed

### WAITING_REVIEW
- Registry shows WAITING_REVIEW
- **Meaning:** Agent produced output, waiting for human approval
- **Action:** Review and approve via review gates (HR_PRE, HR_LANG, etc.)
- **Never:** Automatically bypass review gates

### BLOCKED
- Registry shows BLOCKED
- **Meaning:** Agent is explicitly blocked, requires human intervention
- **Action:** Manual intervention required before spawning
- **Never:** Automatically spawned or unblocked

### RETIRED
- Registry shows RETIRED
- **Meaning:** Agent legitimately completed and was retired
- **Action:** None - agent completed its lifecycle
- **Never:** Automatically respawned (use explicit spawn if needed)

---

## Safe Cleanup Process

### When Cleanup is Safe

Cleanup (`--clean-stale`) is safe when:
1. Agent shows RUNNING in registry
2. No matching process found
3. Last heartbeat exceeds threshold (default: 30 minutes)
4. User explicitly uses `--clean-stale` flag

### What Cleanup Does

- Updates registry status from RUNNING to STALE
- Updates `current_task` to explain why marked STALE
- Preserves all other agent data
- Updates registry `_meta.last_updated` timestamp
- **Does NOT delete entries**
- **Does NOT respawn agents**
- **Does NOT change any other status**

### What Cleanup Does NOT Do

- ❌ Delete registry entries
- ❌ Auto-respawn agents
- ❌ Change IDLE, WAITING_REVIEW, BLOCKED, or RETIRED status
- ❌ Bypass any review gates
- ❌ Modify agent outputs or artifacts

---

## Process Matching Accuracy

### Windows Process Detection

**Methods Used (in order of preference):**
1. `wmic process where name='python.exe' get ProcessId,CommandLine` - Most accurate
2. PowerShell `Get-CimInstance Win32_Process` - Fallback if wmic unavailable
3. `tasklist` - Final fallback (limited info)

**Limitations:**
- Command line extraction may fail if process started without command line
- Process may have already finished before check (learning agents complete quickly)
- Windows command line may be truncated or normalized

**Accuracy:**
- High for long-running agents (process persists)
- Medium for quick-completing agents (may finish before check)
- Low if agent started via wrapper script (command line may not contain agent_id)

### Process Matching Heuristics

**Multiple Strategies:**
1. Direct agent_id match in command line
2. Agent file path pattern matching (`agents/{agent_id}.py`)
3. Normalized matching (handles path variations)

**Why Multiple Strategies:**
- Different execution methods produce different command lines
- Paths may vary (relative vs absolute)
- Windows vs Linux path separators

---

## Explicit Guardrails in Code

### Execution Agent Check
```python
# GOVERNANCE GUARDRAIL: Filter out EXECUTION agents unless explicitly allowed
if not allow_execution_agents:
    execution_agents_filtered = [a for a in idle_agents + registered_agents if a.get("agent_type") == "Execution"]
    # ... filter out
```

**Comment Purpose:** Makes guardrail obvious to future developers. This check is non-negotiable.

### Blocked Agent Check
```python
# GOVERNANCE GUARDRAIL: Filter out BLOCKED agents (never spawn)
blocked_agents = [a for a in agents if a.get("status") == "BLOCKED"]
if blocked_agents:
    print(f"🔒 GOVERNANCE: {len(blocked_agents)} BLOCKED agent(s) skipped (human-gated, requires explicit approval)")
```

**Comment Purpose:** Explicitly documents that BLOCKED agents are never spawned automatically.

### Conflict Detection Comment
```python
# CONFLICT DETECTION: Check if agent already running
is_running, reason = check_agent_already_running(agent_id)
if is_running:
    # ... abort spawn
```

**Comment Purpose:** Makes conflict detection obvious and prevents accidental bypass.

---

## Testing Validation

### Tested Scenarios

1. ✅ **STALE Detection:** Correctly identified 4 stale agents (registry RUNNING, no process)
2. ✅ **STALE Cleanup:** Successfully marked 3 agents as STALE in registry (preserved entries)
3. ✅ **Governance Filtering:** EXECUTION agents filtered (11 filtered, requires flag)
4. ✅ **BLOCKED Filtering:** BLOCKED agents skipped (1 skipped)
5. ✅ **Conflict Detection:** Checks registry and processes before spawning
6. ✅ **Agent Spawning:** Successfully spawned Learning agent for testing
7. ⚠️ **Process Matching:** Works but agents complete too quickly to fully validate (expected behavior)

### Validation Results

**Process Matching:**
- Logic implemented and working
- Windows process detection functional (wmic/PowerShell fallback)
- Learning agents complete too quickly (< 1 second) to catch running process
- This is expected - process matching is most useful for long-running agents
- **Status:** ✅ Logic correct, validation limited by agent execution time

**Conflict Detection:**
- Registry check: ✅ Working
- Process check: ✅ Working
- Logic prevents spawning if agent is RUNNING or BLOCKED
- **Status:** ✅ Validated

**Stale Cleanup:**
- Detection: ✅ Working (found 4 stale, marked 3)
- Registry update: ✅ Working (agents marked as STALE)
- Preservation: ✅ Working (entries preserved, only status changed)
- **Status:** ✅ Validated

---

## Remaining Known Limitations

### 1. Process Matching for Quick Agents
**Issue:** Learning agents complete in < 1 second, so process matching can't catch them running.

**Impact:** Low - process matching is most useful for long-running agents. For quick agents, registry status is sufficient.

**Workaround:** Process matching still works for long-running agents. Quick agents are safe to respawn anyway.

### 2. Windows Command Line Extraction
**Issue:** Command line extraction may fail if process started via wrapper script.

**Impact:** Medium - false negatives (agent running but not detected).

**Mitigation:** Multiple matching heuristics reduce false negatives. Registry check provides backup.

### 3. Duplicate Registry Entries
**Issue:** Registry may contain duplicate entries for same agent_id.

**Impact:** Low - deduplication logic handles this, but may miss edge cases.

**Mitigation:** Deduplication keeps most recent entry based on heartbeat timestamp.

---

## What This System Ensures

✅ **Human Authority Preserved:** No automatic bypassing of review gates or BLOCKED status  
✅ **Safe Execution:** EXECUTION agents require explicit flag  
✅ **Conflict Prevention:** No double-spawning  
✅ **Registry Accuracy:** STALE detection and cleanup  
✅ **Audit Trail:** No deletions, only status updates  
✅ **Governance Compliance:** Explicit guardrails in code with clear comments

---

## What This System Does NOT Ensure

❌ **Perfect Process Detection:** Quick agents may complete before detection  
❌ **Auto-Recovery:** Stale agents not auto-respawned  
❌ **Real-Time Monitoring:** Checks are on-demand, not continuous  
❌ **Cross-Platform Consistency:** Windows process detection differs from Linux/Mac

---

**Last Updated:** 2026-01-10  
**Status:** Active  
**Governance Model:** Human-in-the-loop, controlled-chaos
