# Batch Review Interface

## Overview

The **Batch Review Interface** (`cockpit_batch_review.html`) is an HTML-only, local-first dashboard for reviewing and processing artifacts across all human review gates in batch mode.

## Features

- **Load All Review Gates**: Automatically loads HR_PRE, HR_LANG, HR_MSG, and HR_RELEASE queue files
- **Unified View**: See all pending reviews across all gates in a single table
- **Filtering**: Filter by gate, risk level, or search by artifact name/type
- **Batch Selection**: Select multiple items using checkboxes or "Select All"
- **Batch Actions**: Approve or reject multiple items at once
- **Export Manifest**: Generate approval manifest JSON compatible with `cockpit__write_approval.py`
- **Statistics**: Real-time stats showing total pending, selected, and counts per gate

## Usage

### Opening the Interface

1. **Via Local Server (Recommended)**:
   ```bash
   # From agent-orchestrator directory
   python -m http.server 9000
   # Then open: http://localhost:9000/dashboards/cockpit_batch_review.html
   ```

2. **Direct File Open**:
   - Open `agent-orchestrator/dashboards/cockpit_batch_review.html` directly in your browser
   - Click "Load All Queue Files" and select the 4 queue files manually

3. **Load from Directory**:
   - If running via local server, click "Load from review/ directory" button
   - Automatically loads all `*_queue.json` files from `review/` directory

### Reviewing Artifacts

1. **Load Queue Files**: Click "Load All Queue Files" or "Load from review/ directory"
2. **Filter** (optional): Use filters to narrow down to specific gates, risk levels, or search
3. **Select Items**: 
   - Click checkboxes to select individual items
   - Use "Select All Visible" to select all filtered items
4. **Review Details**: Click on artifact names or paths to view details (if available)

### Batch Processing

1. **Select Multiple Items**: Use checkboxes or "Select All Visible"
2. **Choose Action**:
   - **Approve Selected**: Batch approve all selected items
   - **Reject Selected**: Batch reject all selected items
   - **Export Manifest**: Generate manifest for later processing
3. **Review Manifest**: The manifest JSON will be displayed below
4. **Export**: Copy or download the manifest JSON

### Applying Decisions

After generating the manifest:

1. **Download or Copy** the manifest JSON
2. **Save** to a file (e.g., `approval_manifest.json`)
3. **Run the approval script**:
   ```bash
   python scripts/cockpit__write_approval.py --manifest-file approval_manifest.json
   ```
   
   Or pipe from stdin:
   ```bash
   python scripts/cockpit__write_approval.py < approval_manifest.json
   ```

The script will:
- Write individual approval files to `approvals/{review_id}.json`
- Update review queue files (move from pending to history)
- Update artifact files (set status to ACTIONABLE if approved)
- Log decisions to audit log

## Manifest Format

The manifest JSON follows this structure:

```json
{
  "_meta": {
    "generated_at": "2026-01-20T12:00:00Z",
    "generated_by": "batch_review_interface",
    "total_decisions": 5
  },
  "decisions": [
    {
      "review_id": "hr_pre_001",
      "gate_id": "HR_PRE",
      "artifact_path": "artifacts/...",
      "artifact_name": "Artifact Name",
      "decision": "APPROVE",
      "rationale": "Batch approved via batch review interface",
      "decision_at": "2026-01-20T12:00:00Z",
      "decision_by": "human:reviewer"
    }
  ]
}
```

### Decision Values

- `"decision": "APPROVE"` - Approve the artifact
- `"decision": "REJECT"` - Reject the artifact

**Note**: The decision values must be `"APPROVE"` or `"REJECT"` (not "APPROVED" or "REJECTED").

## Review Gate Definitions

| Gate ID | Name | Description |
|---------|------|-------------|
| HR_PRE | Concept Direction Review | Human approval of concept memo and policy direction before bill introduction |
| HR_LANG | Legislative Language Review | Human approval of drafted legislative text before committee activity |
| HR_MSG | Messaging & Narrative Review | Human approval of policy messaging, framing, and talking points |
| HR_RELEASE | Public Release Approval | Final human authorization for public or external release |

## Statistics Bar

The statistics bar shows:
- **Total Pending**: Total number of pending reviews across all gates
- **Selected**: Number of currently selected items
- **HR_PRE / HR_LANG / HR_MSG / HR_RELEASE**: Count of pending reviews per gate

## Filtering

- **Filter by Gate**: Show only reviews from specific gates
- **Filter by Risk**: Filter by Low, Medium, or High risk levels
- **Search**: Search by artifact name or type (case-insensitive)

## Keyboard Shortcuts

- **Ctrl+A** (or Cmd+A on Mac): Select all visible items (when table is focused)

## File Locations

- **HTML Interface**: `agent-orchestrator/dashboards/cockpit_batch_review.html`
- **Queue Files**: `agent-orchestrator/review/HR_*_queue.json`
- **Approval Script**: `agent-orchestrator/scripts/cockpit__write_approval.py`
- **Approval Files**: `agent-orchestrator/approvals/{review_id}.json`

## Troubleshooting

### No Reviews Loaded

- Check that review queue files exist in `review/` directory
- Verify file names are correct: `HR_PRE_queue.json`, `HR_LANG_queue.json`, etc.
- Check browser console for errors when loading files

### Manifest Not Generated

- Ensure at least one item is selected
- Check that selected items are from the filtered view
- Verify browser console for JavaScript errors

### Approval Script Fails

- Verify manifest format matches expected structure
- Check that `review_id` and `gate_id` match entries in queue files
- Ensure decision values are "APPROVE" or "REJECT" (not "APPROVED"/"REJECTED")
- Check script output for specific error messages

### Files Not Found

- Ensure you're running from the correct directory
- Verify file paths in the manifest match actual artifact locations
- Check that review queue files are in the `review/` directory

## Design Principles

This interface follows the **HTML-Only, Local-First** rules:
- ✅ Pure HTML/CSS/JavaScript (no frameworks)
- ✅ No backend required (works via file:// or local server)
- ✅ No build step (open directly in browser)
- ✅ File-based data (reads JSON files directly)
- ✅ Manual refresh (regenerate queue files to see updates)

## Related Files

- `cockpit_review.html` - Single queue file review interface
- `cockpit__write_approval.py` - Script that processes approval manifests
- `cockpit__list__pending_approvals.py` - Script that generates text summary of pending reviews
