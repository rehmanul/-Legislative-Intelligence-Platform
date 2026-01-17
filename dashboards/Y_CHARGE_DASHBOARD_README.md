# Y-Charge Workflow Dashboard

**File:** `y_charge_workflow_dashboard.html`  
**Location:** `agent-orchestrator/dashboards/`  
**Type:** HTML-only, local-first dashboard

---

## Quick Start

### Option 1: Open Directly in Browser

1. Navigate to the dashboard file:
   ```
   C:\Users\phi3t\12.20 dash\1.5.2026\agent-orchestrator\dashboards\y_charge_workflow_dashboard.html
   ```

2. Double-click the file or right-click → "Open with" → Your browser

### Option 2: Via Local Server (Recommended)

```powershell
cd "C:\Users\phi3t\12.20 dash\1.5.2026\agent-orchestrator\dashboards"
python -m http.server 9000
```

Then open: `http://localhost:9000/y_charge_workflow_dashboard.html`

---

## Features

### 1. Workflow Process Flow
- Interactive Mermaid diagram showing the complete workflow
- Visual representation of:
  - Intelligence agents scanning current events
  - Signal processing pipeline
  - Drafting agents
  - Human review gates
  - Legislative states

### 2. Legislative States Panel
- Shows all 6 legislative states (PRE_EVT → IMPL_EVT)
- Highlights current active state
- Visual indicators for pending/active states

### 3. Intelligence Agents Panel
- **Primary Signal Scanning:** 3 main agents
- **Grassroots Signal Intake:** 6 agents monitoring:
  - Field observations
  - Constituent narratives
  - FOIA/public records
  - Local metrics
  - Social media trends
  - Personal insights
- **Signal Processing Pipeline:** 6-stage processing flow

### 4. Quick Actions
- One-click commands to:
  - Create new workflow
  - Run signal scanning agents
  - Generate concept memos
  - Check policy radar
  - View artifacts

### 5. Statistics Dashboard
- Real-time stats (when workflow data loaded):
  - Intelligence agent count
  - Current legislative state
  - Signals scanned
  - Artifacts generated

---

## Loading Workflow Data

The dashboard can load workflow state from JSON files:

1. Click "📁 Load Workflow State (JSON)"
2. Select a workflow JSON file (e.g., from `agent-orchestrator/state/`)
3. Dashboard will update with:
   - Current legislative state
   - Active state highlighting
   - State badges

---

## Dashboard Sections

### Header
- Title and description
- Statistics cards showing key metrics

### Workflow Diagram
- Mermaid flowchart visualization
- Shows complete process from signal scanning to implementation
- Color-coded by agent type and state

### Legislative States
- 6 states with descriptions
- Active state highlighted in green
- Pending states in blue

### Intelligence Agents
- Organized by type and purpose
- Status indicators (active/idle/running)
- Agent metadata (type, state, risk level)

### Quick Actions
- 6 action cards with commands
- Copy-paste ready Python commands
- Direct links to artifact directories

---

## Agent Types Shown

### Intelligence Agents (Read-Only)
- **Primary Scanning:** `intel_signal_scan_pre_evt`, `intel_policy_radar_comm_evt`, `intel_signal_scan_intro_evt`
- **Grassroots Intake:** 6 agents for field data, narratives, records, metrics, social, insights
- **Processing:** Deduplication, credibility, severity, urgency, jurisdiction, archive

### Drafting Agents (Human-Gated)
- `draft_concept_memo_pre_evt` - Creates PRE_CONCEPT
- `draft_framing_intro_evt` - Policy framing
- `draft_language_comm_evt` - Legislative language

---

## Customization

The dashboard is self-contained HTML with:
- Embedded CSS styling
- Minimal vanilla JavaScript
- Mermaid.js for diagrams (CDN)

To customize:
1. Edit the HTML file directly
2. Modify CSS in `<style>` tag
3. Update JavaScript in `<script>` tag
4. Adjust Mermaid diagram syntax in `#mermaid-diagram` div

---

## Related Files

- `Y_CHARGE_WORKFLOW_GUIDE.md` - Complete workflow guide
- `agent-orchestrator/agents/` - Agent implementations
- `agent-orchestrator/artifacts/` - Generated artifacts
- `agent-orchestrator/state/` - Workflow state files

---

## Notes

- **No Backend Required:** Dashboard works standalone
- **No Build Step:** Open directly in browser
- **Local-First:** Designed for local file system access
- **Progressive Enhancement:** Works without JavaScript (diagram won't render)

---

**Last Updated:** 2026-01-20
