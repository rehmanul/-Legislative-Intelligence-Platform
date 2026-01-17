# Artifact Viewer Enhancement

## Summary

Enhanced the dashboard integration example with comprehensive artifact viewing, copying, and routing capabilities.

## Features Added

### 1. Pending Reviews Section
- Displays all pending reviews from the system state
- Shows artifact metadata (gate ID, artifact ID, submitted by, submitted at)
- Quick action buttons for approve/reject
- "View Artifact" button to open artifact in modal

### 2. Artifact Viewer Modal
- Full-screen modal displaying complete artifact JSON
- Copy buttons:
  - **Copy All**: Copies entire artifact JSON
  - **Copy Summary**: Copies executive summary section
  - **Copy Key Findings**: Copies key findings array
- Formatted JSON display with syntax highlighting (monospace font)

### 3. Enhanced Command Forms
- **Artifact Selection Dropdown**: Select artifacts directly from pending reviews
- **Auto-population**: Selecting an artifact auto-fills Gate ID and Artifact ID
- **Routing Dropdown**: Route artifacts to:
  - External Human
  - Internal Human
  - Back to Agent
- **Rationale Input**: Enhanced textarea with copy-paste support
- **Copy from Artifact Button**: Copies content from viewed artifact into rationale field

### 4. Routing System
- Dropdown menu for routing decisions (not file picker)
- Automatically prefixes rationale with routing decision
- Options:
  - `Route to External Human` → "ROUTED TO EXTERNAL HUMAN: ..."
  - `Route to Internal Human` → "ROUTED TO INTERNAL HUMAN: ..."
  - `Back to Agent` → "RETURNED TO AGENT FOR REVISION: ..."

### 5. Backend API Endpoint
- **GET `/api/v1/dashboard/artifacts/{artifact_path}`**
- Supports multiple path formats:
  - Full paths: `artifacts/draft_concept_memo_pre_evt/PRE_CONCEPT.json`
  - Relative paths: `draft_concept_memo_pre_evt/PRE_CONCEPT.json`
  - Filenames: `PRE_CONCEPT.json` (searches in artifacts directory)
- Security: Validates paths are within artifacts directory
- Error handling: Returns appropriate HTTP status codes

## Usage

### Viewing Artifacts
1. Click "👁️ View Artifact" button on any pending review
2. Modal opens with full artifact content
3. Use copy buttons to copy specific sections

### Copying Content to Rationale
1. View an artifact (opens modal)
2. Click "📋 Copy from Artifact" button in the command form
3. Content is automatically appended to rationale field
4. Visual feedback confirms copy operation

### Routing Artifacts
1. Select artifact from dropdown in command form
2. Choose routing option from "Route To" dropdown
3. Rationale is automatically prefixed with routing decision
4. Complete rationale and submit approve/reject

### Quick Actions
- Click "✅ Approve" or "❌ Reject" on pending review item
- Form auto-populates and scrolls to command section
- Complete routing and rationale, then submit

## Technical Details

### Frontend
- Modal system with click-outside-to-close
- Clipboard API for copying content
- Dynamic form population based on selections
- Real-time state updates from WebSocket/SSE

### Backend
- New artifact endpoint in `dashboard_routes.py`
- Path normalization and security validation
- Flexible path resolution (direct, search, with/without extension)

## Files Modified

1. `agent-orchestrator/dashboards/js/dashboard-integration-example.html`
   - Added pending reviews section
   - Added artifact viewer modal
   - Enhanced command forms with routing
   - Added copy functionality

2. `agent-orchestrator/app/dashboard_routes.py`
   - Added `GET /api/v1/dashboard/artifacts/{artifact_path}` endpoint
   - Path resolution and security validation

## Next Steps

- [ ] Add artifact search/filter functionality
- [ ] Add artifact comparison view
- [ ] Add artifact history/versioning
- [ ] Add export functionality for artifacts
- [ ] Add annotation/commenting on artifacts
