# Dashboard Audit Checklist

**Purpose:** Step-by-step checklist to audit and standardize existing dashboards.

**Last Updated:** 2026-01-20  
**Version:** 1.0.0

---

## Pre-Audit Setup

- [ ] Read `DASHBOARD_ARCHITECTURE.md` (understand responsibilities)
- [ ] Read `DASHBOARD_LANGUAGE_MAP.md` (use consistent terminology)
- [ ] Read `DASHBOARD_DECISION_RUBRIC.md` (know when to use what)
- [ ] Open dashboard file in editor
- [ ] Open dashboard in browser (test current behavior)

---

## 1. HTML Structure Audit

### Semantic HTML
- [ ] Uses semantic elements (`<section>`, `<article>`, `<header>`, `<main>`)
- [ ] Has proper heading hierarchy (`<h1>`, `<h2>`, `<h3>`)
- [ ] Has meaningful `id` attributes for JavaScript targeting
- [ ] Has ARIA labels for accessibility (if needed)
- [ ] Has progressive enhancement (content visible without JavaScript)

### HTML Structure Pattern
- [ ] Has `<head>` with charset, viewport, title
- [ ] Links to shared CSS (`shared/dashboard-common.css`) if exists
- [ ] Has dashboard-specific `<style>` block (if needed)
- [ ] Has `<body>` with semantic structure
- [ ] Scripts loaded at end of `<body>`

**Checklist Items:**
```html
<!-- ✅ GOOD: Semantic structure with IDs -->
<section id="stats-section">
    <h2>Statistics</h2>
    <div id="stats-container">
        <!-- Content -->
    </div>
</section>

<!-- ❌ BAD: Generic divs, no IDs -->
<div>
    <div>
        <!-- Content -->
    </div>
</div>
```

---

## 2. CSS Audit

### Shared CSS
- [ ] Uses shared CSS file (`shared/dashboard-common.css`) if available
- [ ] Dashboard-specific styles are minimal (only what's unique)
- [ ] No duplicate styles already in shared CSS

### CSS Organization
- [ ] Styles are in `<style>` block or external file (not inline where possible)
- [ ] CSS classes follow consistent naming (`.card`, `.btn`, `.stat-card`)
- [ ] Uses CSS variables for colors/themes (if applicable)
- [ ] Responsive design considerations (if needed)

**Checklist Items:**
```css
/* ✅ GOOD: Uses shared classes, minimal custom CSS */
.card {
    /* Shared styles from dashboard-common.css */
}

.dashboard-specific-section {
    /* Only unique styles here */
}

/* ❌ BAD: Duplicates shared styles */
.card {
    background: white;
    padding: 20px;
    /* ... duplicates shared CSS ... */
}
```

---

## 3. JavaScript Audit

### JavaScript Structure
- [ ] JavaScript is in `<script>` block at end of `<body>`
- [ ] Uses shared utilities (`shared/dashboard-utils.js`) if available
- [ ] Uses API client (`js/dashboard-api-client.js`) if backend integration needed
- [ ] Has clear initialization pattern (`DOMContentLoaded` event)

### JavaScript Patterns
- [ ] Configuration object at top (`const DASHBOARD_CONFIG = {}`)
- [ ] State object defined (`let dashboardState = {}`)
- [ ] Data loading function with fallback (backend → file picker → embedded)
- [ ] Error handling function (`handleError()` or similar)
- [ ] Rendering functions (separate from data loading)

**Checklist Items:**
```javascript
// ✅ GOOD: Clear structure, error handling, fallback
const DASHBOARD_CONFIG = {
    name: 'Dashboard Name',
    backendEnabled: true,
    autoSave: true
};

let dashboardState = {};

document.addEventListener('DOMContentLoaded', async () => {
    try {
        await loadData();
        renderDashboard(dashboardState);
    } catch (error) {
        handleError(error, { location: 'initialization' });
    }
});

// ❌ BAD: No structure, no error handling, assumes backend
loadData();
renderDashboard();
```

---

## 4. Data Loading Audit

### Data Loading Pattern
- [ ] Tries backend first (if enabled)
- [ ] Falls back to file picker if backend unavailable
- [ ] Shows connection alert if backend fails (doesn't break dashboard)
- [ ] Has embedded data fallback (if applicable)
- [ ] Error handling shows fix steps

**Checklist Items:**
```javascript
// ✅ GOOD: Backend → File Picker → Embedded (with error handling)
async function loadData() {
    if (DASHBOARD_CONFIG.backendEnabled) {
        try {
            return await dashboardAPI.getState();
        } catch (error) {
            showConnectionAlert(error);
            // Fall through to file picker
        }
    }
    
    if (DASHBOARD_CONFIG.filePickerEnabled) {
        return await loadViaFilePicker();
    }
    
    if (DASHBOARD_CONFIG.embeddedData) {
        return DASHBOARD_CONFIG.embeddedData;
    }
    
    handleError(new Error('No data source'), {
        fixSteps: ['Start backend', 'Use file picker', 'Check embedded data']
    });
}

// ❌ BAD: Assumes backend, no fallback
const data = await dashboardAPI.getState();
```

---

## 5. State Management Audit

### State Storage
- [ ] In-memory state for current session (`let dashboardState = {}`)
- [ ] localStorage for preferences/auto-save (if needed)
- [ ] Backend state for authoritative data (if needed)
- [ ] Multi-tab sync via BroadcastChannel (if needed)

### State Updates
- [ ] State updates trigger re-render
- [ ] State updates notify other tabs (if multi-tab)
- [ ] State updates save to localStorage (if applicable)

**Checklist Items:**
```javascript
// ✅ GOOD: Clear state management
let dashboardState = {
    data: null,
    lastUpdated: null
};

function updateState(newData) {
    dashboardState.data = newData;
    dashboardState.lastUpdated = new Date().toISOString();
    
    // Save to localStorage if needed
    if (DASHBOARD_CONFIG.autoSave) {
        localStorage.setItem('dashboard_state', JSON.stringify(dashboardState));
    }
    
    // Notify other tabs
    notifyStateChange(dashboardState);
    
    // Re-render
    renderDashboard(dashboardState);
}

// ❌ BAD: No clear state management
// Data scattered across variables, no update flow
```

---

## 6. Error Handling Audit

### Error Handling
- [ ] Has `handleError()` function or equivalent
- [ ] Errors show user-friendly messages (not just console)
- [ ] Errors show fix steps (actionable)
- [ ] Connection errors show alert (don't break dashboard)
- [ ] Data errors show error card with recovery steps

**Checklist Items:**
```javascript
// ✅ GOOD: Comprehensive error handling
function handleError(error, context = {}) {
    const errorCard = document.createElement('div');
    errorCard.className = 'error-boundary';
    errorCard.innerHTML = `
        <div class="error-header">⚠️ ${error.message}</div>
        <div class="error-context">Where: ${context.location}</div>
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

// ❌ BAD: No error handling or silent failures
try {
    await loadData();
} catch (error) {
    console.error(error); // Only console, no user feedback
}
```

---

## 7. Mermaid Integration Audit

### Mermaid Setup
- [ ] Loads Mermaid from CDN (`<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>`)
- [ ] Initializes Mermaid once (`mermaid.initialize()`)
- [ ] Has diagram container (`<div class="mermaid">`)

### Mermaid Loading
- [ ] Checks multiple paths for `.mmd` files (`.userInput/mermaid/`, `diagrams/`, etc.)
- [ ] Has file picker fallback for Mermaid diagrams
- [ ] Handles Mermaid rendering errors gracefully

**Checklist Items:**
```javascript
// ✅ GOOD: Multiple sources, error handling
async function loadMermaidDiagram(diagramName) {
    const searchPaths = [
        '.userInput/mermaid/',
        'diagrams/',
        '../diagrams/'
    ];
    
    for (const path of searchPaths) {
        try {
            const content = await fetch(`${path}${diagramName}.mmd`).then(r => r.text());
            return content;
        } catch (e) {
            // Continue to next path
        }
    }
    
    handleError(new Error(`Diagram not found: ${diagramName}`), {
        fixSteps: [
            `Create .userInput/mermaid/${diagramName}.mmd`,
            `Or use file picker to load manually`
        ]
    });
}

// ❌ BAD: Hardcoded path, no error handling
const diagramCode = await fetch('diagrams/my-diagram.mmd').then(r => r.text());
```

---

## 8. Backend Integration Audit

### Backend Connection
- [ ] Uses `dashboard-api-client.js` if backend integration needed
- [ ] Checks connection status (shows indicator)
- [ ] Graceful degradation (works without backend)
- [ ] Connection errors show alert (don't break dashboard)

### Backend API Calls
- [ ] State transitions (approve/reject) call backend API
- [ ] Error handling for API calls
- [ ] Success feedback after API calls

**Checklist Items:**
```javascript
// ✅ GOOD: Backend integration with fallback
const dashboardAPI = new DashboardAPIClient();

async function approveArtifact(artifactId) {
    try {
        await dashboardAPI.approveArtifact(gateId, artifactId, rationale);
        showSuccessMessage('Artifact approved');
        await refreshState(); // Reload from backend
    } catch (error) {
        handleError(error, {
            location: 'approval',
            fixSteps: [
                '1. Check backend is running',
                '2. Verify artifact ID is correct',
                '3. Check network connection'
            ]
        });
    }
}

// ❌ BAD: No error handling, assumes backend always works
await dashboardAPI.approveArtifact(gateId, artifactId, rationale);
```

---

## 9. Auto-Save Audit (If Applicable)

### Auto-Save Setup
- [ ] Form inputs auto-save to localStorage (if dashboard has forms)
- [ ] Auto-save debounced (not on every keystroke)
- [ ] Auto-save restores on page load
- [ ] Auto-save handles localStorage errors gracefully

**Checklist Items:**
```javascript
// ✅ GOOD: Auto-save with debouncing
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

// ❌ BAD: No auto-save or saves on every keystroke
form.addEventListener('input', (e) => {
    localStorage.setItem('form', JSON.stringify(formData)); // No debouncing
});
```

---

## 10. Multi-Tab Sync Audit (If Applicable)

### Multi-Tab Sync
- [ ] Uses BroadcastChannel API for multi-tab sync (if needed)
- [ ] Listens for state changes from other tabs
- [ ] Notifies other tabs when state changes
- [ ] Handles BroadcastChannel errors gracefully

**Checklist Items:**
```javascript
// ✅ GOOD: Multi-tab sync with error handling
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
        // Dashboard continues to work
    }
}

// ❌ BAD: No multi-tab sync or assumes it works
// Tabs can be out of sync
```

---

## Post-Audit Actions

After completing audit:

- [ ] **Document Issues Found**
  - List items that don't meet checklist
  - Prioritize fixes (critical → nice-to-have)
  - Note which fixes require backend changes

- [ ] **Create Fix Plan**
  - Start with critical issues (error handling, data loading fallback)
  - Then move to consistency (HTML structure, CSS classes)
  - Finally polish (auto-save, multi-tab sync)

- [ ] **Test After Changes**
  - Test with backend enabled
  - Test with backend disabled (file picker fallback)
  - Test with multiple tabs open (if multi-tab sync implemented)
  - Test error scenarios (invalid JSON, missing files, network errors)

---

## Quick Reference: Must-Have Items

Every dashboard MUST have:
- ✅ Semantic HTML structure
- ✅ JavaScript initialization pattern
- ✅ Error handling function
- ✅ Data loading with fallback (backend → file picker)
- ✅ Graceful degradation (works without backend)

Every dashboard SHOULD have:
- ⚠️ Connection status indicator (if backend enabled)
- ⚠️ Auto-save for forms (if dashboard has forms)
- ⚠️ Multi-tab sync (if state changes affect other tabs)

Every dashboard MAY have:
- 💡 Mermaid diagrams (if visualization needed)
- 💡 Backend integration (if state transitions needed)
- 💡 localStorage persistence (if preferences needed)

---

**Usage:**
- Run this checklist for each dashboard
- Mark items that pass ✅
- Mark items that need fixing ❌
- Prioritize fixes based on Must-Have → Should-Have → May-Have
