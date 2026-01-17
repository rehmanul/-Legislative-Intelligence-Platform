# Dashboard Integration Guide

**How to integrate the bidirectional API into your existing dashboards.**

---

## Quick Integration (3 Steps)

### Step 1: Add Scripts to Your HTML

Add these three script tags before your closing `</body>` tag:

```html
<!-- Dashboard API Client -->
<script src="js/dashboard-api-client.js"></script>
<script src="js/dashboard-state-manager.js"></script>
<script src="js/dashboard-realtime.js"></script>
```

**Note:** Adjust paths if your dashboard is in a different location.

### Step 2: Initialize Components

Add this JavaScript to your dashboard:

```javascript
// Initialize dashboard components
const stateManager = new DashboardStateManager(dashboardAPI);
const realtimeUpdater = new DashboardRealtimeUpdater(dashboardAPI);

// Initialize
stateManager.initialize();
realtimeUpdater.initialize();

// Listen for state changes
stateManager.onStateChange((newState) => {
    // Update your UI with newState
    updateDashboardUI(newState);
});
```

### Step 3: Replace File Picker with API

**Before (file picker):**
```javascript
// Old: Manual file picker
const fileInput = document.getElementById('fileInput');
fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    const reader = new FileReader();
    reader.onload = (event) => {
        const data = JSON.parse(event.target.result);
        updateDashboard(data);
    };
    reader.readAsText(file);
});
```

**After (API):**
```javascript
// New: Automatic API updates
// State updates automatically via WebSocket/SSE
// No file picker needed!
```

---

## Adding Command Buttons

### Approve/Reject Artifacts

```html
<button onclick="approveArtifact('HR_PRE', 'artifact_id', 'Looks good!')">
    Approve
</button>

<button onclick="rejectArtifact('HR_PRE', 'artifact_id', 'Needs revision')">
    Reject
</button>
```

```javascript
async function approveArtifact(gateId, artifactId, rationale) {
    try {
        await dashboardAPI.approveArtifact(gateId, artifactId, rationale);
        alert('Artifact approved!');
    } catch (error) {
        alert('Failed to approve: ' + error.message);
    }
}

async function rejectArtifact(gateId, artifactId, rationale) {
    try {
        await dashboardAPI.rejectArtifact(gateId, artifactId, rationale);
        alert('Artifact rejected!');
    } catch (error) {
        alert('Failed to reject: ' + error.message);
    }
}
```

### Trigger Agents

```html
<button onclick="triggerAgent('intel_signal_scan_pre_evt')">
    Run Signal Scanner
</button>
```

```javascript
async function triggerAgent(agentId) {
    try {
        await dashboardAPI.triggerAgent(agentId);
        alert('Agent triggered!');
    } catch (error) {
        alert('Failed to trigger agent: ' + error.message);
    }
}
```

### Advance State

```html
<button onclick="advanceState('INTRO_EVT', 'Committee referral confirmed')">
    Advance to Introduction
</button>
```

```javascript
async function advanceState(nextState, confirmation) {
    try {
        await dashboardAPI.advanceState(nextState, confirmation);
        alert('State advanced!');
    } catch (error) {
        alert('Failed to advance state: ' + error.message);
    }
}
```

---

## Updating Existing Dashboards

### Example: Update `live.html`

**Add scripts:**
```html
<script src="js/dashboard-api-client.js"></script>
<script src="js/dashboard-state-manager.js"></script>
<script src="js/dashboard-realtime.js"></script>
```

**Replace polling with state manager:**
```javascript
// Old: Manual polling
setInterval(async () => {
    const response = await fetch('/api/v1/dashboard/state');
    const state = await response.json();
    updateDashboard(state);
}, 10000);

// New: Automatic updates
const stateManager = new DashboardStateManager(dashboardAPI);
stateManager.initialize();
stateManager.onStateChange((state) => {
    updateDashboard(state);
});
```

**Add command buttons:**
```html
<!-- Add approve/reject buttons to review items -->
<button onclick="approveReview(review.gate_id, review.artifact_id)">
    Approve
</button>
```

---

## Connection Status Indicator

Add a connection status indicator to your dashboard:

```html
<div id="connectionStatus">
    <span class="status-dot"></span>
    <span id="statusText">Connecting...</span>
</div>
```

```javascript
dashboardAPI.onConnectionChange((connected) => {
    const dot = document.querySelector('.status-dot');
    const text = document.getElementById('statusText');
    
    if (connected) {
        dot.style.background = '#28a745';
        text.textContent = 'Connected';
    } else {
        dot.style.background = '#dc3545';
        text.textContent = 'Disconnected';
    }
});
```

---

## Real-Time Event Listeners

Listen for specific events:

```javascript
// Artifact approved
realtimeUpdater.onArtifactApproved((data) => {
    console.log('Artifact approved:', data);
    showNotification('Artifact approved!');
});

// Artifact rejected
realtimeUpdater.onArtifactRejected((data) => {
    console.log('Artifact rejected:', data);
    showNotification('Artifact rejected');
});

// State advanced
realtimeUpdater.onStateAdvanced((data) => {
    console.log('State advanced:', data);
    showNotification(`State advanced to ${data.next_state}`);
});

// File changed
realtimeUpdater.onFileChanged((data) => {
    console.log('File changed:', data);
    // Optionally refresh specific section
});
```

---

## Error Handling

```javascript
try {
    await dashboardAPI.approveArtifact(gateId, artifactId, rationale);
} catch (error) {
    if (error.message.includes('HTTP 404')) {
        alert('Artifact not found');
    } else if (error.message.includes('HTTP 500')) {
        alert('Server error - please try again');
    } else {
        alert('Error: ' + error.message);
    }
}
```

---

## Testing

1. **Start backend:**
   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```

2. **Open dashboard** in browser

3. **Check connection:** Status indicator should show "Connected"

4. **Test commands:** Click approve/reject buttons

5. **Test real-time:** Have an agent write a file, dashboard should update automatically

---

## Troubleshooting

### Scripts Not Loading

**Check:**
- Script paths are correct relative to your HTML file
- Files exist in `dashboards/js/` directory
- Browser console for 404 errors

### API Calls Failing

**Check:**
- Backend is running on port 8000
- CORS is enabled (already configured)
- Browser console for error messages

### No Real-Time Updates

**Check:**
- WebSocket connection is active (check status indicator)
- File watcher is running (check backend logs)
- Files are being written to watched directories

---

**See `dashboard-integration-example.html` for a complete working example.**
