# HTML-Only Cockpit Template

This directory contains a ready-to-use HTML-only cockpit template that follows the [HTML-Only, Local-First Development Rules](../../.cursor/rules/html_only_local_first_rules.mdc).

## Files

- **`cockpit_template.html`** - Complete single-file cockpit template
- **`cockpit_state.out.json`** - Generated state snapshot (created by `scripts/cockpit__generate__state_snapshot.py`)
- **`HTML_ONLY_COCKPIT_GUIDE.md`** - Complete guide to the HTML-only cockpit system
- **`html_only_cockpit_context.mmd`** - Mermaid diagram showing system scope and constraints

## Usage

### Quick Start

1. **Generate state snapshot:**
   ```bash
   python scripts/cockpit__generate__state_snapshot.py
   ```
   This creates `dashboards/cockpit_state.out.json`

2. **Open cockpit template:**
   - Open `cockpit_template.html` directly in your browser (double-click)
   - **No server required** - works with `file://` protocol

3. **Load state file:**
   - Click "Load State File" button
   - Select `cockpit_state.out.json`
   - View system status, agents, reviews, and alerts

**For detailed usage, see [HTML_ONLY_COCKPIT_GUIDE.md](./HTML_ONLY_COCKPIT_GUIDE.md)**

### Customization

The template includes:

- **Progressive enhancement** - Works without JavaScript
- **File picker** - Load JSON state files dynamically
- **Status cards** - System status, agents, review checkpoints
- **Alerts section** - Displays alerts when present
- **Review section** - Shows pending reviews

### How Agents Write State Files

Agents write state files through the agent orchestrator system:

1. **Legislative State** - Written by `StateManager.sync_state_file()`:
   - Location: `agent-orchestrator/state/legislative-state.json`
   - Written when workflow state changes
   - Contains current legislative state, history, and advancement rules

2. **Agent Registry** - Updated by agents on spawn/heartbeat:
   - Location: `agent-orchestrator/registry/agent-registry.json`
   - Updated when agents register, update status, or retire
   - Contains agent list with status, tasks, and heartbeat timestamps

3. **Review Gates** - Managed by workflow state:
   - Part of workflow state or separate review state files
   - Contains gate status, required/approved artifacts

The HTML cockpit reads these files (via file picker) and displays them in a read-only interface.

### State File Format

The cockpit expects a combined state structure that can be constructed from multiple sources:

```json
{
  "legislative": {
    "_meta": {
      "state_version": "1.0",
      "last_updated": "2026-01-20T12:00:00Z",
      "authority": "api_synced",
      "workflow_id": "workflow-uuid"
    },
    "current_state": "PRE_EVT",
    "state_definition": "Pre-Event Intelligence",
    "state_lock": false,
    "state_history": [
      {
        "state": "PRE_EVT",
        "entered_at": "2026-01-20T12:00:00Z",
        "entered_by": "system",
        "reason": "Workflow created"
      }
    ],
    "next_allowed_states": ["INTRO_EVT"],
    "state_advancement_rule": "Requires HR_PRE approval"
  },
  "agents": {
    "_meta": {
      "registry_version": "1.0",
      "last_updated": "2026-01-20T12:00:00Z",
      "total_agents": 5,
      "active_agents": 2,
      "idle_agents": 1,
      "waiting_review_agents": 1,
      "blocked_agents": 0
    },
    "agents": [
      {
        "agent_id": "intel_signal_scan_pre_evt",
        "agent_type": "Intelligence",
        "status": "RUNNING",
        "scope": "Signal scanning only (read-only)",
        "current_task": "Scanning industry signals",
        "last_heartbeat": "2026-01-20T12:00:00Z",
        "risk_level": "LOW"
      }
    ]
  },
  "review_gates": [
    {
      "gate_id": "HR_PRE",
      "status": "PENDING",
      "required_artifacts": ["PRE_CONCEPT"],
      "approved_artifacts": [],
      "created_at": "2026-01-20T12:00:00Z"
    }
  ],
  "alerts": [
    {
      "level": "info",
      "message": "System operating normally",
      "timestamp": "2026-01-20T12:00:00Z"
    }
  ]
}
```

**Note:** You can load separate files (legislative-state.json, agent-registry.json) individually, or create a combined state file that merges data from multiple sources.

### Key Features

- ✅ **Zero dependencies** - Pure HTML/CSS/JS
- ✅ **No build step** - Open directly in browser
- ✅ **Local-first** - File picker for state loading
- ✅ **Progressive enhancement** - Works without JS
- ✅ **Responsive** - CSS Grid for layout

## Compliance

This template fully complies with `.cursor/rules/html_only_local_first_rules.mdc`:

### ✅ Technology Compliance
- ✅ Plain HTML5, CSS3, vanilla JavaScript only
- ✅ No frameworks (React, Vue, Next.js, etc.)
- ✅ No backend services
- ✅ No databases
- ✅ No authentication
- ✅ No cloud services or usage-based AI
- ✅ No build tools or bundlers
- ✅ No hosting assumptions

### ✅ Architecture Compliance
- ✅ **Read-only by default** - HTML only reads files, never writes
- ✅ **No coupling** - Agents write files independently; HTML observes passively
- ✅ **File-based state** - State loaded via file picker (no API calls)
- ✅ **Local-first** - Works with `file://` protocol (no server required)
- ✅ **Progressive enhancement** - Core content visible without JavaScript

### ✅ Execution Model Compliance
- ✅ Opens directly in browser (no build step)
- ✅ No compilation or installation required
- ✅ Human review model (display → review → decide → act outside cockpit)
- ✅ Zero infrastructure cost
- ✅ Zero background execution

### 🚫 Explicitly Forbidden (Not Present)
- ❌ Backend services or API endpoints
- ❌ WebSocket or push mechanisms
- ❌ UI-triggered execution
- ❌ Hosting or deployment instructions
- ❌ Framework imports
- ❌ Real-time updates
- ❌ Authentication systems

## See Also

- **[HTML_ONLY_COCKPIT_GUIDE.md](./HTML_ONLY_COCKPIT_GUIDE.md)** - Complete guide to the HTML-only cockpit system
- [HTML-Only Rules](../../.cursor/rules/html_only_local_first_rules.mdc)
- [System Context Diagram](./html_only_cockpit_context.mmd)
- [State Snapshot Generator](../../scripts/cockpit__generate__state_snapshot.py)