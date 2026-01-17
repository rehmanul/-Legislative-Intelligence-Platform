# Master Dashboard Standardization Prompt

**Purpose:** Copy-pasteable prompt to standardize any dashboard according to the Dashboard Architecture Contract.

**Usage:** Copy this entire prompt and paste it when asking an agent to standardize a dashboard.

---

## PROMPT: Standardize Dashboard According to Architecture Contract

You are a dashboard standardization agent. Your task is to audit and standardize the dashboard file: `[DASHBOARD_FILE_PATH]`

### Context

This dashboard is part of a system with 10-11 HTML dashboards that need consistent architecture. The system uses:
- **HTML-first, progressive enhancement** approach
- **Vanilla JavaScript** (no frameworks)
- **Mermaid diagrams** for visualizations
- **Hybrid data loading** (backend API → file picker → embedded data)
- **Backend integration** via `js/dashboard-api-client.js` (optional, graceful degradation)

### Reference Documents

Before proceeding, read these documents (they define the architecture contract):
1. `agent-orchestrator/dashboards/DASHBOARD_ARCHITECTURE.md` - Canonical architecture (HTML/JS/state/backend responsibilities)
2. `agent-orchestrator/dashboards/DASHBOARD_LANGUAGE_MAP.md` - Standardized terminology
3. `agent-orchestrator/dASHBOARD_DECISION_RUBRIC.md` - Decision rules (when to use what)
4. `agent-orchestrator/dashboards/DASHBOARD_AUDIT_CHECKLIST.md` - Step-by-step audit checklist

### Your Task

Apply the audit checklist (`DASHBOARD_AUDIT_CHECKLIST.md`) to `[DASHBOARD_FILE_PATH]` and fix any items that don't meet the standard.

### Key Requirements

#### 1. HTML Structure
- ✅ Use semantic HTML (`<section>`, `<article>`, `<header>`, `<main>`)
- ✅ Add meaningful `id` attributes for JavaScript targeting
- ✅ Ensure progressive enhancement (content visible without JavaScript)
- ✅ Link to shared CSS (`shared/dashboard-common.css`) if it exists
- ✅ Keep dashboard-specific styles minimal (only unique styles)

#### 2. JavaScript Patterns
- ✅ Configuration object at top: `const DASHBOARD_CONFIG = { ... }`
- ✅ State object: `let dashboardState = { ... }`
- ✅ Initialization pattern: `document.addEventListener('DOMContentLoaded', async () => { ... })`
- ✅ Data loading with fallback: Backend → File Picker → Embedded → Error
- ✅ Error handling function: `handleError(error, context)` with fix steps
- ✅ Rendering functions: Separate from data loading

#### 3. Data Loading (Hybrid Pattern)
- ✅ Try backend first (if `backendEnabled: true`)
- ✅ Show connection alert if backend unavailable (don't break dashboard)
- ✅ Fall back to file picker (always works offline)
- ✅ Fall back to embedded data (if provided)
- ✅ If all fail, show error with fix steps

**Pattern to use:**
```javascript
async function loadDashboardData() {
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
    
    if (DASHBOARD_CONFIG.filePickerEnabled) {
        setupFilePicker();
        return; // User will select file
    }
    
    if (DASHBOARD_CONFIG.embeddedData) {
        updateState(DASHBOARD_CONFIG.embeddedData);
        return;
    }
    
    handleError(new Error('No data source available'), {
        location: 'data-loading',
        fixSteps: [
            '1. Start backend server (python -m http.server 8000)',
            '2. Use file picker to load JSON manually',
            '3. Check if dashboard has embedded data'
        ]
    });
}
```

#### 4. Error Handling
- ✅ Function: `handleError(error, context)` that shows user-friendly error card
- ✅ Connection errors: Show alert banner (not blocking)
- ✅ Data errors: Show error card with fix steps
- ✅ All errors: Log to console AND show in UI

**Pattern to use:**
```javascript
function handleError(error, context = {}) {
    const errorCard = document.createElement('div');
    errorCard.className = 'error-boundary';
    errorCard.innerHTML = `
        <div class="error-header">
            <span class="error-icon">⚠️</span>
            <strong>Error: ${error.message}</strong>
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
    document.body.insertBefore(errorCard, document.body.firstChild);
    console.error('Dashboard Error:', error, context);
}
```

#### 5. Mermaid Integration (If Applicable)
- ✅ Load Mermaid from CDN: `<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>`
- ✅ Initialize once: `mermaid.initialize({ startOnLoad: false, theme: 'default' })`
- ✅ Container: `<div class="mermaid" id="diagram-container"></div>`
- ✅ Load from multiple paths (`.userInput/mermaid/`, `diagrams/`, `../diagrams/`)
- ✅ File picker fallback for Mermaid diagrams

**Pattern to use:**
```javascript
async function loadMermaidDiagram(diagramName) {
    const searchPaths = [
        '.userInput/mermaid/',
        'diagrams/',
        '../diagrams/',
        'artifacts/*/diagrams/'
    ];
    
    for (const path of searchPaths) {
        try {
            const content = await fetch(`${path}${diagramName}.mmd`).then(r => r.text());
            return content;
        } catch (e) {
            // Continue to next path
        }
    }
    
    handleError(new Error(`Mermaid diagram not found: ${diagramName}`), {
        location: 'mermaid-loading',
        fixSteps: [
            `1. Create .userInput/mermaid/${diagramName}.mmd`,
            `2. Or place in diagrams/${diagramName}.mmd`,
            `3. Or use file picker to load manually`
        ]
    });
}
```

#### 6. Backend Integration (If Applicable)
- ✅ Use `js/dashboard-api-client.js` for backend calls
- ✅ Check connection status (show indicator)
- ✅ Graceful degradation (works without backend)
- ✅ Connection errors show alert (don't break dashboard)

**Pattern to use:**
```javascript
// At top of script
const dashboardAPI = new DashboardAPIClient();

// Update connection status
dashboardAPI.onConnectionChange((connected) => {
    updateConnectionStatus(connected ? 'connected' : 'disconnected');
});

function updateConnectionStatus(status) {
    const indicator = document.getElementById('status-indicator');
    const text = document.getElementById('status-text');
    if (status === 'connected') {
        indicator.className = 'status-indicator connected';
        text.textContent = 'Connected';
    } else {
        indicator.className = 'status-indicator disconnected';
        text.textContent = 'Disconnected - Using file picker';
    }
}
```

#### 7. Auto-Save (If Dashboard Has Forms)
- ✅ Auto-save form state to localStorage (debounced)
- ✅ Restore form state on page load
- ✅ Handle localStorage errors gracefully

**Pattern to use:**
```javascript
function setupAutoSave(formId, debounceMs = 500) {
    const form = document.getElementById(formId);
    let saveTimeout;
    
    form.addEventListener('input', (e) => {
        clearTimeout(saveTimeout);
        saveTimeout = setTimeout(() => {
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);
            try {
                localStorage.setItem(`dashboard_${formId}`, JSON.stringify(data));
            } catch (error) {
                console.warn('Auto-save failed:', error);
            }
        }, debounceMs);
    });
    
    // Restore on load
    const saved = localStorage.getItem(`dashboard_${formId}`);
    if (saved) {
        try {
            const data = JSON.parse(saved);
            Object.entries(data).forEach(([key, value]) => {
                const input = form.querySelector(`[name="${key}"]`);
                if (input) input.value = value;
            });
        } catch (error) {
            console.warn('Auto-save restore failed:', error);
        }
    }
}
```

#### 8. Multi-Tab Sync (If State Changes Affect Other Tabs)
- ✅ Use BroadcastChannel API for lightweight sync
- ✅ Listen for state changes from other tabs
- ✅ Notify other tabs when state changes
- ✅ Handle BroadcastChannel errors gracefully

**Pattern to use:**
```javascript
const syncChannel = new BroadcastChannel('dashboard-sync');

syncChannel.onmessage = (event) => {
    if (event.data.type === 'state-updated') {
        refreshState(); // Reload from backend or re-fetch
    }
};

function notifyStateChange(newState) {
    try {
        syncChannel.postMessage({
            type: 'state-updated',
            state: newState,
            timestamp: Date.now()
        });
    } catch (error) {
        console.warn('Multi-tab sync failed:', error);
    }
}
```

### Terminology

Use standardized terms from `DASHBOARD_LANGUAGE_MAP.md`:
- ✅ "Container" or "Element" (not "Component")
- ✅ "Event Handler" (not "Hook")
- ✅ "State" or "Data" (not "Store")
- ✅ "Backend" (not "Server")
- ✅ "Diagram" (not "Chart")
- ✅ "Load" (not "Upload")

### What NOT to Do

- ❌ Don't use framework terminology ("component", "hook", "store")
- ❌ Don't assume backend always available (graceful degradation)
- ❌ Don't put business logic in frontend (call backend API)
- ❌ Don't mix data loading patterns without fallback
- ❌ Don't use inline styles where CSS classes work
- ❌ Don't skip error handling
- ❌ Don't hardcode paths (use search paths for files)

### Output Format

After standardizing the dashboard, provide:

1. **Summary of Changes**
   - List items from audit checklist that were fixed
   - List items that were already correct
   - List items that require backend changes (if any)

2. **Modified Code**
   - Show key changes (HTML structure, JavaScript patterns, error handling)
   - Keep existing functionality intact
   - Add comments explaining why patterns were used

3. **Testing Checklist**
   - [ ] Test with backend enabled
   - [ ] Test with backend disabled (file picker fallback)
   - [ ] Test error scenarios (invalid JSON, missing files)
   - [ ] Test multi-tab sync (if applicable)
   - [ ] Test auto-save (if applicable)

4. **Flag Backend Integration Points**
   - List where backend integration would eventually be needed
   - Note which features require backend (vs. which are frontend-only)
   - Suggest API endpoints that would be useful

### Success Criteria

Dashboard is standardized when:
- ✅ All items from audit checklist pass
- ✅ Uses consistent patterns (configuration, state, error handling)
- ✅ Works without backend (graceful degradation)
- ✅ Shows user-friendly errors with fix steps
- ✅ Uses standardized terminology

---

## END OF PROMPT

**To use this prompt:**
1. Copy entire prompt above
2. Replace `[DASHBOARD_FILE_PATH]` with actual file path (e.g., `agent-orchestrator/dashboards/next_steps_checklist.html`)
3. Paste into agent conversation
4. Agent will audit and standardize according to architecture contract

**Example usage:**
```
You are a dashboard standardization agent. Your task is to audit and standardize the dashboard file: `agent-orchestrator/dashboards/next_steps_checklist.html`

[... rest of prompt ...]
```
