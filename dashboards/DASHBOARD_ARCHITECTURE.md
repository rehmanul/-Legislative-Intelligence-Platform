# Dashboard Architecture Contract

**Purpose:** Canonical definition of what HTML, JavaScript, State, and Backend are responsible for in dashboard system.

**Last Updated:** 2026-01-20  
**Version:** 1.0.0

---

## 1. HTML Responsibilities (Structure & Presentation)

### HTML IS Responsible For:
- ✅ **Semantic structure** — `<section>`, `<article>`, `<header>`, `<main>`, `<nav>`
- ✅ **Content hierarchy** — headings, paragraphs, lists
- ✅ **Progressive enhancement** — core content visible without JavaScript
- ✅ **Accessibility** — ARIA labels, semantic HTML
- ✅ **Static content** — labels, descriptions, help text
- ✅ **Mermaid diagram containers** — `<div class="mermaid">` with diagram code

### HTML IS NOT Responsible For:
- ❌ Dynamic data rendering (that's JavaScript)
- ❌ State management (that's JavaScript/localStorage/backend)
- ❌ API calls (that's JavaScript)
- ❌ Event handling (that's JavaScript)

### HTML Structure Pattern:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Name</title>
    <link rel="stylesheet" href="shared/dashboard-common.css">
    <style>
        /* Dashboard-specific styles only */
    </style>
</head>
<body>
    <!-- Header -->
    <header>
        <h1>Dashboard Title</h1>
        <p>Dashboard description</p>
    </header>
    
    <!-- Main Content -->
    <main>
        <!-- Semantic sections with IDs for JS targeting -->
        <section id="stats-section">
            <h2>Statistics</h2>
            <div id="stats-container">
                <!-- Placeholder content visible without JS -->
                <p>Loading statistics...</p>
            </div>
        </section>
        
        <section id="diagram-section">
            <h2>Visualization</h2>
            <div class="mermaid" id="diagram-container">
                <!-- Mermaid diagram code -->
            </div>
        </section>
    </main>
    
    <!-- Scripts -->
    <script src="shared/dashboard-utils.js"></script>
    <script src="js/dashboard-api-client.js"></script>
    <script>
        // Dashboard-specific JavaScript
    </script>
</body>
</html>
```

---

## 2. JavaScript Responsibilities (Behavior & Interactivity)

### JavaScript IS Responsible For:
- ✅ **Data loading** — fetch JSON, file picker, backend API calls
- ✅ **DOM manipulation** — update content, show/hide elements
- ✅ **Event handling** — button clicks, form submissions
- ✅ **State management** — localStorage, in-memory state
- ✅ **Mermaid initialization** — `mermaid.initialize()` and rendering
- ✅ **Error handling** — catch errors, display user-friendly messages
- ✅ **Multi-tab sync** — BroadcastChannel API for state sync

### JavaScript IS NOT Responsible For:
- ❌ Content structure (that's HTML)
- ❌ Visual styling (that's CSS)
- ❌ Data persistence beyond localStorage (that's backend)
- ❌ Business logic that should be server-side (that's backend)

### JavaScript Pattern:

```javascript
// 1. Configuration
const DASHBOARD_CONFIG = {
    name: 'Dashboard Name',
    backendEnabled: true,  // Try backend first, fallback to file picker
    autoSave: true,        // Auto-save form state
    mermaidTheme: 'default'
};

// 2. State
let dashboardState = {
    data: null,
    lastUpdated: null,
    connectionStatus: 'unknown'
};

// 3. Initialization
document.addEventListener('DOMContentLoaded', async () => {
    try {
        await initializeDashboard();
    } catch (error) {
        handleError(error, { location: 'initialization' });
    }
});

// 4. Data Loading (try backend, fallback to file picker)
async function loadData() {
    if (DASHBOARD_CONFIG.backendEnabled) {
        try {
            const data = await dashboardAPI.getState();
            updateState(data);
            return;
        } catch (error) {
            showConnectionAlert(error);
            // Fall through to file picker
        }
    }
    
    // Fallback: file picker
    setupFilePicker();
}

// 5. Rendering
function renderDashboard(state) {
    updateElement('stats-container', renderStats(state));
    updateElement('diagram-container', renderMermaid(state));
}

// 6. Error Handling
function handleError(error, context) {
    showErrorCard(error, context);
    console.error('Dashboard Error:', error, context);
}
```

---

## 3. State Responsibilities (Data & Persistence)

### State IS:
- **In-memory state** — JavaScript variables (`let dashboardState = {}`)
- **localStorage** — user preferences, form state, connection status
- **Backend state** — server-side data (artifacts, registry, reviews)
- **URL state** — query parameters, hash fragments (optional)

### State IS NOT:
- ❌ Visual appearance (that's CSS)
- ❌ DOM structure (that's HTML)
- ❌ Business rules (that's backend logic)

### State Management Pattern:

```javascript
// In-memory state (ephemeral, lost on refresh)
let currentState = {
    data: null,
    lastUpdated: null
};

// localStorage state (persistent across sessions)
function saveToLocalStorage(key, value) {
    try {
        localStorage.setItem(`dashboard_${key}`, JSON.stringify(value));
    } catch (error) {
        console.warn('localStorage save failed:', error);
    }
}

function loadFromLocalStorage(key, defaultValue = null) {
    try {
        const stored = localStorage.getItem(`dashboard_${key}`);
        return stored ? JSON.parse(stored) : defaultValue;
    } catch (error) {
        console.warn('localStorage load failed:', error);
        return defaultValue;
    }
}

// Backend state (authoritative, shared across users/tabs)
async function fetchBackendState() {
    const response = await fetch('/api/v1/dashboard/state');
    if (response.ok) {
        return await response.json();
    }
    throw new Error(`Backend unavailable: ${response.status}`);
}

// State update flow
function updateState(newData) {
    currentState.data = newData;
    currentState.lastUpdated = new Date().toISOString();
    
    // Sync to localStorage (for persistence)
    saveToLocalStorage('state', currentState);
    
    // Sync to other tabs (via BroadcastChannel)
    notifyStateChange(currentState);
    
    // Re-render UI
    renderDashboard(currentState);
}
```

---

## 4. Backend Responsibilities (Server-Side Logic)

### Backend IS Responsible For:
- ✅ **Authoritative data** — single source of truth (registry, artifacts, reviews)
- ✅ **State transitions** — approve/reject, state advancement (immutable history)
- ✅ **Business logic** — validation, routing, authorization
- ✅ **Real-time updates** — WebSocket broadcasts (optional, can use polling)
- ✅ **Data persistence** — file system writes, database (if used)
- ✅ **Security** — validation, rate limiting, access control

### Backend IS NOT Responsible For:
- ❌ HTML rendering (that's frontend)
- ❌ Client-side state management (that's JavaScript/localStorage)
- ❌ Visual styling (that's CSS)
- ❌ File picker fallback (that's frontend)

### Backend Integration Pattern:

```javascript
// Dashboard API client (js/dashboard-api-client.js)
class DashboardAPIClient {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
        this.isConnected = false;
    }
    
    async getState() {
        // Fetch authoritative state from backend
        const response = await fetch(`${this.baseURL}/api/v1/dashboard/state`);
        if (!response.ok) {
            throw new Error(`Backend unavailable: ${response.status}`);
        }
        return await response.json();
    }
    
    async approveArtifact(gateId, artifactId, rationale) {
        // State transition: approve artifact
        const response = await fetch(`${this.baseURL}/api/v1/dashboard/approve`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ gate_id: gateId, artifact_id: artifactId, rationale })
        });
        if (!response.ok) {
            throw new Error(`Approval failed: ${response.status}`);
        }
        return await response.json();
    }
}

// Dashboard should work WITHOUT backend (graceful degradation)
async function loadDataWithFallback() {
    if (DASHBOARD_CONFIG.backendEnabled) {
        try {
            return await dashboardAPI.getState();
        } catch (error) {
            showConnectionAlert(error); // Alert user, don't break
            // Fall through to file picker
        }
    }
    
    // Fallback: file picker (works offline)
    return await loadViaFilePicker();
}
```

---

## 5. Mermaid Integration Pattern

### Mermaid IS:
- ✅ **Diagram definition** — stored in HTML `<div class="mermaid">` or `.mmd` files
- ✅ **Rendering** — handled by Mermaid.js library (CDN)
- ✅ **Multiple sources** — can be embedded, loaded from file, or generated from JSON

### Mermaid IS NOT:
- ❌ State management (diagrams are rendered, not stored as state)
- ❌ Data source (diagrams are visualization of data, not data itself)

### Mermaid Loading Pattern:

```javascript
// 1. Initialize Mermaid once (globally)
mermaid.initialize({ 
    startOnLoad: false,  // Don't auto-render, we'll control it
    theme: DASHBOARD_CONFIG.mermaidTheme 
});

// 2. Load Mermaid diagram from multiple sources
async function loadMermaidDiagram(diagramName) {
    const searchPaths = [
        '.userInput/mermaid/',
        'diagrams/',
        '../diagrams/',
        'artifacts/*/diagrams/'
    ];
    
    // Try each path
    for (const path of searchPaths) {
        try {
            const content = await fetch(`${path}${diagramName}.mmd`).then(r => r.text());
            return content;
        } catch (e) {
            // Continue to next path
        }
    }
    
    // Fallback: file picker
    return await loadMermaidViaFilePicker();
}

// 3. Render Mermaid diagram
async function renderMermaidDiagram(containerId, diagramCode) {
    const container = document.getElementById(containerId);
    container.innerHTML = diagramCode;
    
    // Mermaid will auto-render on elements with class "mermaid"
    await mermaid.run({
        nodes: [container]
    });
}
```

---

## 6. Data Loading Strategy (Hybrid Pattern)

### Priority Order:

1. **Backend API** (if enabled and available)
   - Try: `dashboardAPI.getState()`
   - On failure: Show alert, fall through to file picker
   - Do NOT break dashboard

2. **File Picker** (always available, works offline)
   - User selects `.json` or `.mmd` file
   - Load via `FileReader` API
   - Update dashboard state

3. **Embedded Data** (fallback for static dashboards)
   - JSON in `<script>` tag
   - Hardcoded data structure
   - Last resort

### Implementation:

```javascript
async function loadDashboardData() {
    // Try backend first
    if (DASHBOARD_CONFIG.backendEnabled) {
        try {
            const data = await dashboardAPI.getState();
            dashboardState.data = data;
            dashboardState.source = 'backend';
            return data;
        } catch (error) {
            showConnectionAlert({
                message: 'Backend unavailable',
                error: error.message,
                fallback: 'Using file picker instead'
            });
            // Continue to file picker
        }
    }
    
    // Fallback: file picker
    setupFilePicker();
    return null; // User will select file
}

function setupFilePicker() {
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '.json,.mmd';
    fileInput.onchange = async (e) => {
        const file = e.target.files[0];
        if (file) {
            const content = await file.text();
            const data = JSON.parse(content);
            dashboardState.data = data;
            dashboardState.source = 'file-picker';
            renderDashboard(dashboardState);
        }
    };
    
    // Show file picker button
    const pickerButton = document.getElementById('file-picker-btn');
    pickerButton.onclick = () => fileInput.click();
}
```

---

## 7. Error Handling Pattern

### Error Levels:

1. **Connection Errors** (backend unavailable)
   - Show alert banner (not blocking)
   - Fall back to file picker
   - Dashboard continues to work

2. **Data Errors** (invalid JSON, missing fields)
   - Show error card with fix steps
   - Highlight which data is missing
   - Provide actionable recovery steps

3. **Rendering Errors** (Mermaid parse error, DOM error)
   - Show error in diagram container
   - Log to console
   - Allow user to reload/re-enter data

### Error Handling Implementation:

```javascript
function handleError(error, context = {}) {
    const errorCard = document.createElement('div');
    errorCard.className = 'error-boundary';
    errorCard.innerHTML = `
        <div class="error-header">
            <span class="error-icon">⚠️</span>
            <strong>${error.message}</strong>
        </div>
        <div class="error-context">
            <strong>Where:</strong> ${context.location || 'Unknown'}
        </div>
        <div class="error-fix">
            <strong>How to fix:</strong>
            <ol>
                ${(context.fixSteps || []).map(step => `<li>${step}</li>`).join('')}
            </ol>
        </div>
    `;
    
    // Show prominently
    document.body.insertBefore(errorCard, document.body.firstChild);
    
    console.error('Dashboard Error:', error, context);
}

function showConnectionAlert(error) {
    const alert = document.createElement('div');
    alert.className = 'connection-alert';
    alert.innerHTML = `
        🔔 <strong>Backend unavailable:</strong> ${error.message}
        <br>Dashboard will use file picker instead.
    `;
    document.body.insertBefore(alert, document.body.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => alert.remove(), 5000);
}
```

---

## Summary: Responsibility Boundaries

| Concern | HTML | JavaScript | State | Backend |
|---------|------|------------|-------|---------|
| **Structure** | ✅ Semantic HTML | ❌ | ❌ | ❌ |
| **Styling** | ✅ CSS (inline or external) | ❌ | ❌ | ❌ |
| **Content** | ✅ Static text/labels | ✅ Dynamic rendering | ❌ | ❌ |
| **Data Loading** | ❌ | ✅ Fetch API, FileReader | ❌ | ✅ Authoritative source |
| **Interactivity** | ❌ | ✅ Event handlers | ❌ | ❌ |
| **Persistence** | ❌ | ✅ localStorage | ✅ In-memory state | ✅ File system/DB |
| **Business Logic** | ❌ | ❌ | ❌ | ✅ Validation, routing |
| **Mermaid Diagrams** | ✅ Container `<div class="mermaid">` | ✅ Rendering, loading | ❌ | ❌ |

---

**Next Steps:**
1. Apply this architecture to existing dashboards
2. Use language map (DASHBOARD_LANGUAGE_MAP.md) for consistent terminology
3. Use decision rubric (DASHBOARD_DECISION_RUBRIC.md) for when to use what
4. Use audit checklist (DASHBOARD_AUDIT_CHECKLIST.md) for migration
