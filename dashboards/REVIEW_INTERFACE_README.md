# Artifact Review Interface - Usage Guide

## Overview

The Artifact Review Interface is a local HTML-based human-in-the-loop approval system for reviewing and approving agent-generated artifacts. It provides a visual interface for reviewing artifacts and recording approval decisions that agents can read.

## Architecture

The system uses a two-part architecture:

1. **HTML Interface** (`cockpit_review.html`) - Visual review and decision interface
2. **Python Bridge Script** (`cockpit__write_approval.py`) - Writes approval decisions to filesystem

## Workflow

```
1. Agent generates artifact → status: SPECULATIVE
2. Artifact added to review queue (HR_*_queue.json)
3. Human opens cockpit_review.html in browser (file://)
4. Human loads review queue file
5. Human reviews artifacts and clicks APPROVE/REJECT
6. Decisions stored in localStorage (session persistence)
7. Human exports manifest JSON
8. Human runs: python scripts/cockpit__write_approval.py
9. Script updates:
   - Review queue (moves to history)
   - Artifact files (_meta.status: ACTIONABLE)
   - Audit log
10. Agent checks artifact status → sees ACTIONABLE → executes
```

## Usage

### Step 1: Open the HTML Interface

1. Open `agent-orchestrator/dashboards/cockpit_review.html` in your browser
   - You can double-click the file or use `file://` protocol
   - No server required - works completely offline

### Step 2: Load Review Queue

1. Click "📁 Load Review Queue File"
2. Navigate to `agent-orchestrator/review/`
3. Select a queue file (e.g., `HR_PRE_queue.json`, `HR_LANG_queue.json`)
4. The interface will display all pending reviews

### Step 3: Review Artifacts

For each artifact, you'll see:
- Artifact name and type
- Review gate (HR_PRE, HR_LANG, etc.)
- Risk level
- Review requirements
- Artifact path
- Submission metadata

### Step 4: Make Decisions

For each pending artifact:
1. Review the artifact content (click to view full artifact file if needed)
2. Optionally add a rationale
3. Click **✅ APPROVE** or **❌ REJECT**

Decisions are:
- Stored in localStorage (persists during browser session)
- Shown in "Session Decisions" summary
- Can be undone with "↺ Undo" button

### Step 5: Export Approval Manifest

1. After making all decisions, scroll to "Export Approval Manifest"
2. Review the generated JSON
3. Either:
   - **Copy Manifest JSON** - Copy to clipboard, then save manually
   - **Download Manifest** - Downloads manifest.json file

### Step 6: Process Approvals

Run the bridge script to write decisions to filesystem:

```bash
# Option 1: Process manifest from file (recommended)
python agent-orchestrator/scripts/cockpit__write_approval.py --manifest-file approvals/manifest.json

# Option 2: Process from default location (if you saved to approvals/manifest.json)
python agent-orchestrator/scripts/cockpit__write_approval.py

# Option 3: Pipe manifest JSON from stdin
cat manifest.json | python agent-orchestrator/scripts/cockpit__write_approval.py
```

The script will:
- Write individual approval files to `approvals/{review_id}.json`
- Update review queue files (move from pending to history)
- Update artifact files (`_meta.status: ACTIONABLE` for approved)
- Log decisions to audit log

## Alternative: Command-Line Approvals

You can also approve artifacts directly from command line:

```bash
# Approve a single artifact
python agent-orchestrator/scripts/cockpit__approve_artifact.py HR_PRE hr_pre_001 APPROVE --rationale "Policy goals aligned"

# Reject an artifact
python agent-orchestrator/scripts/cockpit__approve_artifact.py HR_LANG "Concept Memo" REJECT "Needs revision"

# Process manifest file
python agent-orchestrator/scripts/cockpit__approve_artifact.py --manifest approvals/manifest.json
```

## Approval Manifest Schema

The approval manifest is a JSON file with this structure:

```json
{
  "_meta": {
    "manifest_version": "1.0.0",
    "generated_at": "2026-01-20T12:00:00Z",
    "generated_by": "cockpit_review.html",
    "total_decisions": 2
  },
  "decisions": [
    {
      "review_id": "hr_pre_001",
      "gate_id": "HR_PRE",
      "artifact_path": "artifacts/concept.json",
      "artifact_name": "Concept Memo",
      "decision": "APPROVE",
      "rationale": "Policy goals aligned",
      "decision_at": "2026-01-20T12:00:00Z",
      "decision_by": "human:reviewer",
      "risk_level": "Medium"
    }
  ]
}
```

## File Locations

- **HTML Interface**: `agent-orchestrator/dashboards/cockpit_review.html`
- **Review Queues**: `agent-orchestrator/review/HR_*_queue.json`
- **Artifacts**: `agent-orchestrator/artifacts/{agent_id}/*.json`
- **Approval Manifests**: `agent-orchestrator/approvals/manifest.json`
- **Individual Approvals**: `agent-orchestrator/approvals/{review_id}.json`
- **Bridge Script**: `agent-orchestrator/scripts/cockpit__write_approval.py`
- **Approval Script**: `agent-orchestrator/scripts/cockpit__approve_artifact.py`
- **Audit Log**: `agent-orchestrator/audit/audit-log.jsonl`

## Safety Features

1. **High-Risk Warnings**: HIGH risk artifacts show a warning and require confirmation
2. **Undo Decisions**: Decisions can be undone before exporting manifest
3. **Session Persistence**: Decisions persist in localStorage (survives page refresh)
4. **Audit Trail**: All decisions are logged to audit log
5. **Validation**: Scripts validate decision data before processing

## Limitations

1. **No Direct Filesystem Write**: HTML interface cannot directly write files (browser security). You must use the bridge script.
2. **Manual Export Step**: Must manually export manifest and run bridge script
3. **Local Only**: HTML interface works locally only (file:// protocol)

## Troubleshooting

### Manifest not processing
- Check JSON syntax is valid
- Verify all required fields are present (review_id, gate_id, decision)
- Check that review_id exists in the queue file

### Artifact not updating
- Verify artifact_path is correct relative to BASE_DIR
- Check artifact file exists and has `_meta` block
- Review script output for warnings

### Decisions not persisting
- Check browser localStorage is enabled
- Some browsers disable localStorage for file:// protocol in private mode

## Integration with Agents

Agents check artifact status before execution:

```python
artifact_data = load_json(artifact_file)
status = artifact_data.get("_meta", {}).get("status", "SPECULATIVE")

if status == "ACTIONABLE":
    # Proceed with execution
else:
    # Wait for approval
```

## Future Enhancements

Potential improvements:
- Direct filesystem write via browser FileSystem API (requires user permission)
- Real-time queue updates (would require server or file watcher)
- Batch approval of multiple artifacts
- Approval templates/presets
- Integration with Cursor execution context for seamless workflow
