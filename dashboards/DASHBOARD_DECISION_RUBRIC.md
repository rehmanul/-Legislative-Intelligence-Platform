# Dashboard Decision Rubric

**Purpose:** Decision-making guide for when to use static HTML, JavaScript, State, or Backend.

**Last Updated:** 2026-01-20  
**Version:** 1.0.0

---

## Decision Tree: What Goes Where?

### Question 1: Does it change based on user input or data?

- **NO** → **Static HTML**
  - Labels, descriptions, help text
  - Static headings, paragraphs
  - Fixed structure (tabs, sections)
  
- **YES** → Continue to Question 2

---

### Question 2: Does it change based on backend data or user actions?

- **NO** (only changes on page reload or file selection) → **JavaScript + Embedded Data**
  - Data comes from file picker
  - Data comes from embedded JSON
  - Rendering happens once on load
  
- **YES** (changes in real-time or across tabs) → Continue to Question 3

---

### Question 3: Does it need to persist across sessions or be shared?

- **NO** (only needed during current session) → **JavaScript + In-Memory State**
  - Current dashboard view
  - Temporary user selections
  - UI state (expanded/collapsed sections)
  
- **YES** (persists or shared) → Continue to Question 4

---

### Question 4: Is it user preferences or session state?

- **User preferences** → **JavaScript + localStorage**
  - Theme selection
  - Column visibility
  - Auto-save form state
  
- **Shared state or authoritative data** → **Backend**
  - Artifacts, registry, reviews
  - State transitions (approve/reject)
  - Multi-user consistency

---

## Decision Rules by Feature Type

### Feature: Displaying Statistics

**Decision: JavaScript + Data Loading (Backend or File Picker)**

**Why:**
- Statistics come from backend data
- Statistics change over time
- Can fallback to file picker if backend unavailable

**Implementation:**
```javascript
async function loadStatistics() {
    try {
        const state = await dashboardAPI.getState();
        renderStatistics(state.stats);
    } catch (error) {
        showConnectionAlert(error);
        setupFilePickerForStats();
    }
}
```

---

### Feature: Mermaid Diagram

**Decision: HTML Container + JavaScript Rendering**

**Why:**
- Diagram code is static (embedded or from file)
- Rendering happens via JavaScript (Mermaid library)
- Not state-dependent (diagrams are visualization, not state)

**Implementation:**
```html
<div class="mermaid" id="diagram-container">
    <!-- Diagram code loaded here -->
</div>
```

```javascript
async function renderMermaid(diagramCode) {
    const container = document.getElementById('diagram-container');
    container.innerHTML = diagramCode;
    await mermaid.run({ nodes: [container] });
}
```

---

### Feature: Form Input (User Entry)

**Decision: HTML Form + JavaScript Event Handler + localStorage Auto-Save**

**Why:**
- Form structure is static HTML
- User input triggers JavaScript validation/handling
- Auto-save to localStorage for persistence
- Submit may call backend (but form itself is frontend)

**Implementation:**
```html
<form id="approval-form">
    <input type="text" name="rationale" id="rationale-input">
    <button type="submit">Approve</button>
</form>
```

```javascript
// Auto-save to localStorage
setupAutoSave('approval-form');

// Submit handler
document.getElementById('approval-form').onsubmit = async (e) => {
    e.preventDefault();
    const data = new FormData(e.target);
    await dashboardAPI.approveArtifact(data.get('rationale'));
};
```

---

### Feature: Connection Status Indicator

**Decision: HTML Container + JavaScript State + Backend Health Check**

**Why:**
- Status changes based on backend availability
- Status needs to update without page reload
- Backend health check is authoritative

**Implementation:**
```html
<div id="connection-status">
    <span class="status-indicator" id="status-indicator"></span>
    <span id="status-text">Checking...</span>
</div>
```

```javascript
async function checkConnectionStatus() {
    try {
        await dashboardAPI.getState();
        updateConnectionStatus('connected');
    } catch (error) {
        updateConnectionStatus('disconnected');
    }
}

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

---

### Feature: Multi-Tab Synchronization

**Decision: JavaScript + BroadcastChannel API**

**Why:**
- State changes in one tab should reflect in other tabs
- Not backend concern (client-side synchronization)
- localStorage alone doesn't sync across tabs in real-time

**Implementation:**
```javascript
const syncChannel = new BroadcastChannel('dashboard-sync');

// Listen for state changes from other tabs
syncChannel.onmessage = (event) => {
    if (event.data.type === 'state-updated') {
        refreshState();
    }
};

// Notify other tabs when state changes
function notifyStateChange(newState) {
    syncChannel.postMessage({
        type: 'state-updated',
        state: newState
    });
}
```

---

### Feature: Approve/Reject Artifacts

**Decision: HTML Button + JavaScript Handler + Backend API**

**Why:**
- Button is static HTML
- Click handler is JavaScript
- State transition (approve/reject) must be backend (authoritative, creates audit log)

**Implementation:**
```html
<button class="btn btn-success" onclick="handleApprove(artifactId)">
    ✅ Approve
</button>
```

```javascript
async function handleApprove(artifactId) {
    try {
        await dashboardAPI.approveArtifact(gateId, artifactId, rationale);
        showSuccessMessage('Artifact approved');
        refreshState(); // Reload from backend
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
```

---

## Decision Checklist

Use this checklist for each feature:

- [ ] **Is it content that never changes?**
  - ✅ Yes → Static HTML
  - ❌ No → Continue
  
- [ ] **Does it change only on page load/file selection?**
  - ✅ Yes → JavaScript + Embedded Data or File Picker
  - ❌ No → Continue
  
- [ ] **Does it change during user session?**
  - ✅ Yes → JavaScript + In-Memory State
  - ❌ No → Continue
  
- [ ] **Does it need to persist across sessions?**
  - ✅ Yes → JavaScript + localStorage (preferences) OR Backend (shared data)
  - ❌ No → Continue
  
- [ ] **Is it authoritative data or state transition?**
  - ✅ Yes → Backend API
  - ❌ No → JavaScript + localStorage or In-Memory State

---

## Anti-Patterns (What NOT to Do)

### ❌ Don't: Store Authoritative Data in localStorage

**Wrong:**
```javascript
// BAD: localStorage should not be authoritative source
localStorage.setItem('artifacts', JSON.stringify(artifacts));
```

**Right:**
```javascript
// GOOD: Backend is authoritative, localStorage is cache/preferences
const artifacts = await dashboardAPI.getArtifacts();
localStorage.setItem('artifacts_cache', JSON.stringify(artifacts)); // Cache only
```

---

### ❌ Don't: Put Dynamic Content in Static HTML

**Wrong:**
```html
<!-- BAD: Statistics are hardcoded -->
<div class="stat">42</div>
```

**Right:**
```html
<!-- GOOD: Statistics container, JavaScript populates -->
<div class="stat" id="stat-total-agents">0</div>
```

```javascript
// JavaScript updates
document.getElementById('stat-total-agents').textContent = state.totalAgents;
```

---

### ❌ Don't: Do Business Logic in Frontend

**Wrong:**
```javascript
// BAD: Business logic (validation) in frontend only
function approveArtifact(artifactId) {
    if (artifactId.startsWith('PRE_')) {
        // Approval logic...
    }
}
```

**Right:**
```javascript
// GOOD: Frontend calls backend, backend does validation
async function approveArtifact(artifactId) {
    await dashboardAPI.approveArtifact(gateId, artifactId, rationale);
    // Backend validates and creates audit log
}
```

---

### ❌ Don't: Mix Data Loading Patterns Without Fallback

**Wrong:**
```javascript
// BAD: Assumes backend always available
const state = await dashboardAPI.getState();
renderDashboard(state);
```

**Right:**
```javascript
// GOOD: Try backend, fallback to file picker
async function loadData() {
    try {
        return await dashboardAPI.getState();
    } catch (error) {
        showConnectionAlert(error);
        return await loadViaFilePicker();
    }
}
```

---

## Summary: Decision Matrix

| Feature Type | HTML | JavaScript | State | Backend |
|-------------|------|------------|-------|---------|
| **Static Labels** | ✅ | ❌ | ❌ | ❌ |
| **Dynamic Content** | ✅ Container | ✅ Rendering | ✅ Data | ❌ |
| **User Input** | ✅ Form | ✅ Handler | ✅ localStorage | ❌ |
| **File Loading** | ❌ | ✅ FileReader | ✅ In-Memory | ❌ |
| **State Transitions** | ✅ Button | ✅ Handler | ❌ | ✅ API |
| **Preferences** | ❌ | ✅ Save/Load | ✅ localStorage | ❌ |
| **Authoritative Data** | ✅ Display | ✅ Fetch | ✅ Cache | ✅ Source |
| **Multi-Tab Sync** | ❌ | ✅ BroadcastChannel | ✅ In-Memory | ❌ |
| **Mermaid Diagrams** | ✅ Container | ✅ Rendering | ❌ | ❌ |

---

**Usage:**
- When adding new feature, run through decision tree
- When reviewing dashboard, check against anti-patterns
- When refactoring, apply decision matrix
