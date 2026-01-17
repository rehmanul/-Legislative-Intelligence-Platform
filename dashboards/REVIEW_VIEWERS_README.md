# Review Viewers Documentation

This document describes all HTML viewers available for reviewing artifacts, markdown files, and diagrams in the agent-orchestrator system.

---

## Available Viewers

### 1. Unified Review Viewer (`unified_review_viewer.html`)

**Purpose:** Single interface for reviewing JSON artifacts, markdown files, and mermaid diagrams.

**Location:** `agent-orchestrator/dashboards/unified_review_viewer.html`

**Features:**
- **Tab 1 - JSON Artifacts:** Review queue files with approve/reject buttons
  - Load review queue JSON files (HR_PRE_queue.json, HR_LANG_queue.json, etc.)
  - View artifact metadata (type, risk level, review requirements)
  - Approve/Reject buttons for each artifact
  - View artifact content inline
  - Export approval manifest
  
- **Tab 2 - Markdown Files:** View markdown with interactive checkboxes
  - Load markdown files (.md)
  - Interactive checkboxes for `- [ ]` and `- [x]` TODO items
  - Auto-save checkbox state to localStorage
  - Rendered markdown with proper formatting
  
- **Tab 3 - Mermaid Diagrams:** View and render mermaid diagrams
  - Load mermaid diagram files (.mmd)
  - Render diagrams using Mermaid.js
  - View source code

**Usage:**
1. Open `unified_review_viewer.html` in a web browser
2. Select the appropriate tab (JSON, Markdown, or Mermaid)
3. Use file picker to load files
4. For JSON: Review artifacts and click Approve/Reject
5. For Markdown: Check/uncheck TODO items (auto-saves)
6. For Mermaid: View rendered diagrams

---

### 2. Cockpit Review (`cockpit_review.html`)

**Purpose:** Specialized viewer for JSON artifact review queues with human-in-the-loop approval.

**Location:** `agent-orchestrator/dashboards/cockpit_review.html`

**Features:**
- Load review queue files (HR_PRE, HR_LANG, HR_MSG, HR_RELEASE)
- Display pending reviews with full metadata
- Approve/Reject buttons with rationale input
- High-risk artifact warnings
- View artifact JSON content inline
- Session decision tracking
- Export approval manifest

**Usage:**
1. Open `cockpit_review.html` in a web browser
2. Click "Load Review Queue File"
3. Select a review queue file from `agent-orchestrator/review/HR_*_queue.json`
4. Review each artifact's metadata and requirements
5. Optionally load artifact file to view content
6. Enter rationale (optional) and click Approve or Reject
7. Export manifest when done

**Review Queue Files:**
- `review/HR_PRE_queue.json` - Pre-event artifacts
- `review/HR_LANG_queue.json` - Legislative language artifacts
- `review/HR_MSG_queue.json` - Messaging artifacts
- `review/HR_RELEASE_queue.json` - Release artifacts

---

### 3. Markdown Review Viewer (`markdown_review_viewer.html`)

**Purpose:** Dedicated viewer for markdown files with interactive TODO checkboxes.

**Location:** `agent-orchestrator/dashboards/markdown_review_viewer.html`

**Features:**
- Load markdown files (.md) from artifacts/review/
- Convert `- [ ]` and `- [x]` checkboxes to interactive HTML checkboxes
- Auto-save checkbox state to localStorage
- Statistics: Total TODOs, Completed, Remaining
- Action Required / Draft status detection
- Proper markdown rendering (tables, code blocks, headers)

**Usage:**
1. Open `markdown_review_viewer.html` in a web browser
2. Click "Load Markdown File"
3. Select a markdown file from `artifacts/review/*.md`
4. Check/uncheck TODO items as you complete them
5. Checkbox state auto-saves
6. Click "Save Checkbox State" for manual save

**Supported Markdown Files:**
All files in `agent-orchestrator/artifacts/review/*.md`:
- `learning__codebase_exploration__DRAFT_v1.md`
- `business_outcome_acceleration_brief__20260108_023219.md` (ACTION_REQUIRED)
- `critical_blockers_fixed__DRAFT_v1.md` (has checkboxes)
- Plus 18 more DRAFT files

---

### 4. Mermaid Diagram Viewer (`mermaid_viewer.html`)

**Purpose:** Dedicated viewer for Mermaid diagram files (.mmd).

**Location:** `agent-orchestrator/dashboards/mermaid_viewer.html`

**Features:**
- Load mermaid diagram files (.mmd)
- Render diagrams using Mermaid.js
- Toggle source code view
- List of known diagrams for reference
- Error handling with source display

**Usage:**
1. Open `mermaid_viewer.html` in a web browser
2. Click "Load Mermaid Diagram File"
3. Select a .mmd file from `artifacts/**/*.mmd`
4. View rendered diagram
5. Toggle "Toggle Source Code" to see original mermaid syntax

**Known Diagram Files:**
- `artifacts/AGENT_DEPENDENCY_GRAPH.mmd`
- `artifacts/policy/diagrams/system_context.mmd`
- `artifacts/policy/diagrams/stakeholder_hierarchy.mmd`
- `artifacts/policy/diagrams/master_dashboard.mmd`
- Plus 12 more diagram files

---

### 5. Policy Artifacts Viewer (`artifacts/policy/viewer.html`)

**Purpose:** View policy artifacts and diagrams (read-only context).

**Location:** `agent-orchestrator/artifacts/policy/viewer.html`

**Features:**
- View policy documents
- View policy mermaid diagrams
- Navigation guides
- System context visualization

**Note:** This viewer is for read-only policy context, not for review/approval.

---

## File Locations

### Review Queue Files (JSON)
```
agent-orchestrator/review/
├── HR_PRE_queue.json      # Pre-event review queue
├── HR_LANG_queue.json     # Legislative language review queue
├── HR_MSG_queue.json      # Messaging review queue
└── HR_RELEASE_queue.json  # Release review queue
```

### Markdown Review Files
```
agent-orchestrator/artifacts/review/
├── learning__codebase_exploration__DRAFT_v1.md
├── business_outcome_acceleration_brief__20260108_023219.md
├── critical_blockers_fixed__DRAFT_v1.md
└── ... (21 total files)
```

### Mermaid Diagram Files
```
agent-orchestrator/artifacts/
├── AGENT_DEPENDENCY_GRAPH.mmd
├── vibe_coding_workflow_with_agents.mmd
├── policy/diagrams/
│   ├── system_context.mmd
│   ├── stakeholder_hierarchy.mmd
│   ├── master_dashboard.mmd
│   └── ... (9 more diagrams)
└── ... (15 total .mmd files)
```

### JSON Artifact Files
```
agent-orchestrator/artifacts/{agent_id}/
├── PRE_CONCEPT.json
├── INTRO_FRAME.json
├── COMM_LEGISLATIVE_LANGUAGE.json
└── ... (79 total JSON artifacts)
```

---

## Quick Start

### Review JSON Artifacts
1. Open `cockpit_review.html` or `unified_review_viewer.html`
2. Load `review/HR_PRE_queue.json` (or appropriate queue file)
3. Review artifacts and approve/reject
4. Export manifest when done

### Review Markdown with TODOs
1. Open `markdown_review_viewer.html` or `unified_review_viewer.html`
2. Load a markdown file from `artifacts/review/*.md`
3. Check/uncheck TODO items
4. State auto-saves

### View Mermaid Diagrams
1. Open `mermaid_viewer.html` or `unified_review_viewer.html`
2. Load a .mmd file from `artifacts/**/*.mmd`
3. View rendered diagram

---

## Browser Compatibility

All viewers work in modern browsers:
- Chrome/Edge (recommended)
- Firefox
- Safari
- Opera

**Requirements:**
- JavaScript enabled
- Local file access (for file picker)
- Internet connection (for CDN libraries: Mermaid.js, Marked.js)

---

## Data Persistence

### JSON Review Decisions
- Stored in browser localStorage as `reviewDecisions`
- Can be exported as JSON manifest
- Manifest can be saved to `approvals/manifest.json`

### Markdown Checkbox State
- Stored in browser localStorage as `md-checkboxes-{filename}`
- Persists across browser sessions
- Each file has separate state

---

## Exporting Approval Manifest

After reviewing artifacts in the JSON viewers:

1. Review all artifacts and make decisions
2. Click "Copy Manifest JSON" or "Download Manifest"
3. Save manifest to `agent-orchestrator/approvals/manifest.json`
4. Or run: `python scripts/cockpit__write_approval.py` with manifest data

**Manifest Format:**
```json
{
  "_meta": {
    "manifest_version": "1.0.0",
    "generated_at": "2026-01-20T12:00:00Z",
    "generated_by": "unified_review_viewer.html",
    "total_decisions": 2
  },
  "decisions": [
    {
      "review_id": "hr_pre_001",
      "gate_id": "HR_PRE",
      "artifact_path": "artifacts/...",
      "artifact_name": "Artifact Name",
      "decision": "APPROVE",
      "rationale": "Optional rationale",
      "decision_at": "2026-01-20T12:00:00Z",
      "decision_by": "human:reviewer",
      "risk_level": "Medium"
    }
  ]
}
```

---

## Troubleshooting

### Diagrams Don't Render
- Check browser console for errors
- Verify Mermaid.js CDN is loaded
- Check diagram syntax is valid Mermaid
- Try viewing source code to debug

### Checkboxes Don't Save
- Check browser localStorage is enabled
- Verify file name is consistent
- Check browser console for errors

### Artifacts Don't Load
- Verify JSON file is valid
- Check file path is correct
- Ensure file uses review queue format
- Check browser console for parsing errors

---

## Related Files

- `scripts/cockpit__approve_artifact.py` - Python script for approving artifacts
- `scripts/cockpit__write_approval.py` - Python script for writing approval manifest
- `review/HR_*_queue.json` - Review queue files
- `artifacts/review/*.md` - Markdown review documents

---

**Last Updated:** 2026-01-20  
**Version:** 1.0.0
