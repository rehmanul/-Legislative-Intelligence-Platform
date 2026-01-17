# Bidirectional Dashboard-Agent Communication System

**Status:** ✅ Implemented  
**Version:** 1.0.0  
**Date:** 2026-01-20

---

## Overview

This system enables **bidirectional communication** between HTML dashboards and Python agents:

- **Agents → Dashboards:** Real-time updates when agents process files
- **Dashboards → Agents:** Commands from dashboards (approve, reject, trigger, advance state)
- **Multi-Dashboard Support:** Multiple dashboards stay in sync automatically

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    AGENTS (Python)                        │
│  - Write files: artifacts/, registry/, state/             │
│  - Read commands: commands/                               │
│  - Independent operation                                   │
└──────────────────────┬───────────────────────────────────┘
                       │
                       │ File changes detected
                       │
┌──────────────────────▼───────────────────────────────────┐
│              FASTAPI BACKEND (Python)                      │
│  ┌────────────────────────────────────────────────────┐  │
│  │ File Watcher Service                               │  │
│  │  - Watches: artifacts/, registry/, state/, review/  │  │
│  │  - Detects: new files, modified files             │  │
│  │  - Broadcasts: Updates to all dashboards          │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Command Handler API                                │  │
│  │  POST /api/v1/dashboard/commands/approve          │  │
│  │  POST /api/v1/dashboard/commands/reject          │  │
│  │  POST /api/v1/dashboard/commands/trigger-agent    │  │
│  │  POST /api/v1/dashboard/commands/advance-state    │  │
│  │  → Writes to files (agents read)                 │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐  │
│  │ State Aggregator                                  │  │
│  │  GET /api/v1/dashboard/state                     │  │
│  │  → Aggregates all file-based state                │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐  │
│  │ WebSocket/SSE Server                               │  │
│  │  WS /api/v1/dashboard/ws                          │  │
│  │  SSE /api/v1/dashboard/state/stream               │  │
│  │  → Broadcasts updates to all dashboards           │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────┬───────────────────────────────────┘
                       │
                       │ WebSocket/SSE + REST API
                       │
┌──────────────────────▼───────────────────────────────────┐
│              DASHBOARDS (HTML + JavaScript)               │
│  ┌────────────────────────────────────────────────────┐  │
│  │ dashboard-api-client.js                          │  │
│  │  - Sends commands to backend                     │  │
│  │  - Receives real-time updates                    │  │
│  │  - Auto-reconnects on disconnect                 │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐  │
│  │ dashboard-state-manager.js                        │  │
│  │  - Manages local state cache                      │  │
│  │  - Provides reactive state updates                │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐  │
│  │ dashboard-realtime.js                              │  │
│  │  - Event-driven updates                            │  │
│  │  - Listens for specific events                     │  │
│  └────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────┘
```

---

## Quick Start

### 1. Install Dependencies

```bash
cd agent-orchestrator
pip install -r requirements.txt
```

**New dependency:** `watchdog>=3.0.0` (for file watching)

### 2. Start Backend

```bash
cd agent-orchestrator/app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will:
- Start file watcher (watches for agent file changes)
- Start WebSocket server (for real-time updates)
- Expose REST API (for commands and state)

### 3. Include JavaScript in Your Dashboard

Add these scripts to your HTML dashboard:

```html
<!-- Include dashboard API client -->
<script src="js/dashboard-api-client.js"></script>
<script src="js/dashboard-state-manager.js"></script>
<script src="js/dashboard-realtime.js"></script>

<script>
    // Initialize dashboard components
    const stateManager = new DashboardStateManager(dashboardAPI);
    const realtimeUpdater = new DashboardRealtimeUpdater(dashboardAPI);
    
    // Initialize
    stateManager.initialize();
    realtimeUpdater.initialize();
    
    // Listen for state changes
    stateManager.onStateChange((newState) => {
        console.log('State updated:', newState);
        // Update your UI here
    });
    
    // Listen for real-time events
    realtimeUpdater.onArtifactApproved((data) => {
        console.log('Artifact approved:', data);
    });
</script>
```

### 4. Send Commands from Dashboard

```javascript
// Approve an artifact
await dashboardAPI.approveArtifact('HR_PRE', 'artifact_id', 'Rationale here');

// Reject an artifact
await dashboardAPI.rejectArtifact('HR_PRE', 'artifact_id', 'Reason here');

// Trigger an agent
await dashboardAPI.triggerAgent('intel_signal_scan_pre_evt', { param: 'value' });

// Advance state
await dashboardAPI.advanceState('INTRO_EVT', 'External confirmation text', 'source');
```

---

## API Endpoints

### State Endpoints

**GET `/api/v1/dashboard/state`**
- Returns aggregated state snapshot
- Includes: agents, artifacts, reviews, legislative state, system status

**WebSocket `/api/v1/dashboard/ws`**
- Real-time updates via WebSocket
- Sends: state updates, file changes, command results

**SSE `/api/v1/dashboard/state/stream`**
- Server-Sent Events stream
- Alternative to WebSocket (works with HTTP/2)

### Command Endpoints

**POST `/api/v1/dashboard/commands/approve`**
```json
{
  "gate_id": "HR_PRE",
  "artifact_id": "artifact_id_or_path",
  "rationale": "Approval rationale",
  "approved_by": "dashboard"
}
```

**POST `/api/v1/dashboard/commands/reject`**
```json
{
  "gate_id": "HR_PRE",
  "artifact_id": "artifact_id_or_path",
  "rationale": "Rejection reason",
  "rejected_by": "dashboard"
}
```

**POST `/api/v1/dashboard/commands/trigger-agent`**
```json
{
  "agent_id": "intel_signal_scan_pre_evt",
  "params": {}
}
```

**POST `/api/v1/dashboard/commands/advance-state`**
```json
{
  "next_state": "INTRO_EVT",
  "external_confirmation": "Description of external event",
  "source": "Optional source reference",
  "confirmed_by": "dashboard"
}
```

---

## JavaScript API Reference

### DashboardAPIClient

**Methods:**
- `connect()` - Connect to backend (auto-called on page load)
- `disconnect()` - Disconnect from backend
- `getState()` - Fetch current state snapshot
- `approveArtifact(gateId, artifactId, rationale)` - Approve artifact
- `rejectArtifact(gateId, artifactId, rationale)` - Reject artifact
- `triggerAgent(agentId, params)` - Trigger agent
- `advanceState(nextState, confirmation, source)` - Advance state

**Events:**
- `onStateChange(callback)` - State changed
- `onConnectionChange(callback)` - Connection status changed

### DashboardStateManager

**Methods:**
- `initialize()` - Initialize and subscribe to updates
- `getState()` - Get current state (synchronous)
- `getAgents()` - Get agent statistics
- `getArtifacts()` - Get artifact statistics
- `getReviews()` - Get review statistics
- `getLegislativeState()` - Get legislative state
- `formatStateAge(ageSeconds)` - Format age as human-readable

**Events:**
- `onStateChange(callback)` - State changed

### DashboardRealtimeUpdater

**Methods:**
- `initialize()` - Initialize real-time updater
- `onArtifactApproved(callback)` - Artifact approved event
- `onArtifactRejected(callback)` - Artifact rejected event
- `onAgentTriggered(callback)` - Agent triggered event
- `onStateAdvanced(callback)` - State advanced event
- `onFileChanged(callback)` - File changed event
- `onStateUpdate(callback)` - State update event

---

## Command Queue System

Commands from dashboards are written to `commands/` directory:

```
commands/
├── approve_{uuid}.json      # Approval commands
├── reject_{uuid}.json       # Rejection commands
├── trigger_{uuid}.json      # Agent trigger commands
├── advance_state_{uuid}.json # State advancement commands
├── processed/               # Processed commands (moved here)
└── failed/                  # Failed commands (moved here)
```

**Agents can check for commands:**
```python
from lib.command_reader import get_pending_commands, mark_command_processed

# Check for pending commands
commands = get_pending_commands(BASE_DIR, command_type="approve")

for command in commands:
    # Process command
    result = process_approval(command)
    
    # Mark as processed
    mark_command_processed(BASE_DIR, command["_file_path"], result)
```

---

## File Watcher

The file watcher automatically detects changes in:
- `registry/agent-registry.json` - Agent status changes
- `state/legislative-state.json` - State changes
- `review/*_queue.json` - Review queue updates
- `artifacts/**/*.json` - New/modified artifacts
- `commands/*.json` - New commands

When changes are detected:
1. File watcher triggers `broadcast_file_change()`
2. Backend broadcasts update to all connected dashboards
3. Dashboards receive update and refresh state

---

## Multi-Dashboard Support

**All dashboards stay in sync automatically:**

1. Dashboard 1 approves artifact → Backend updates file
2. Backend broadcasts update → All dashboards receive it
3. Dashboard 2 and 3 update their UI automatically

**No manual refresh needed!**

---

## Example Integration

See `dashboards/js/dashboard-integration-example.html` for a complete example showing:
- Connection status indicator
- Real-time statistics display
- Command buttons (approve, reject, trigger, advance)
- Event log

---

## Troubleshooting

### Backend Not Starting

**Check:**
- Port 8000 is available
- `watchdog` is installed: `pip install watchdog`
- Dependencies installed: `pip install -r requirements.txt`

### WebSocket Connection Fails

**Fallback:** API client automatically falls back to polling (every 5 seconds)

**Check:**
- Backend is running on port 8000
- CORS is configured (already set to allow all origins)
- Firewall allows WebSocket connections

### Commands Not Working

**Check:**
- Backend is running
- Command files are created in `commands/` directory
- Agents are checking for commands (if using command queue)

### State Not Updating

**Check:**
- File watcher is running (check backend logs)
- Files are being written to watched directories
- WebSocket/SSE connection is active

---

## Migration from File-Only Dashboards

**Existing dashboards can be updated incrementally:**

1. **Add scripts** to HTML:
   ```html
   <script src="js/dashboard-api-client.js"></script>
   ```

2. **Replace file picker** with API call:
   ```javascript
   // Old: File picker
   // New: API call
   const state = await dashboardAPI.getState();
   ```

3. **Add command buttons**:
   ```javascript
   // Replace CLI scripts with API calls
   await dashboardAPI.approveArtifact(gateId, artifactId, rationale);
   ```

4. **Remove manual refresh** - updates are automatic!

---

## Files Created

### Backend
- `app/dashboard_routes.py` - Dashboard API routes
- `app/file_watcher.py` - File watching service
- `lib/command_reader.py` - Command queue utilities

### Frontend
- `dashboards/js/dashboard-api-client.js` - API client
- `dashboards/js/dashboard-state-manager.js` - State manager
- `dashboards/js/dashboard-realtime.js` - Real-time updater
- `dashboards/js/dashboard-integration-example.html` - Example dashboard

### Configuration
- `requirements.txt` - Updated with `watchdog>=3.0.0`
- `app/main.py` - Integrated dashboard routes and file watcher

---

## Next Steps

1. **Update existing dashboards** to use new API client
2. **Add command buttons** to dashboards (approve, reject, trigger)
3. **Test multi-dashboard sync** (open multiple dashboards)
4. **Add agents** that check command queue (optional)

---

**Last Updated:** 2026-01-20  
**Version:** 1.0.0
