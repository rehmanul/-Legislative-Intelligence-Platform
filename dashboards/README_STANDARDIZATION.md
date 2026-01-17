# Dashboard Standardization System

**Status:** ✅ Complete  
**Created:** 2026-01-20  
**Purpose:** Master contract for standardizing 10-11 HTML dashboards

---

## What Was Created

### 📐 Phase 1: Architecture Contract (PLAN)

1. **`DASHBOARD_ARCHITECTURE.md`**
   - Defines what HTML, JavaScript, State, and Backend are responsible for
   - Includes code patterns for each responsibility
   - Defines boundaries and anti-patterns

2. **`DASHBOARD_LANGUAGE_MAP.md`**
   - Standardized terminology for discussions
   - What terms to use (and avoid)
   - Quick reference for term substitution

3. **`DASHBOARD_DECISION_RUBRIC.md`**
   - Decision tree for when to use static HTML, JS, state, or backend
   - Decision rules by feature type
   - Anti-patterns to avoid

4. **`DASHBOARD_AUDIT_CHECKLIST.md`**
   - Step-by-step checklist for auditing dashboards
   - 10 sections covering all aspects
   - Must-have, should-have, may-have items

### 🚀 Phase 2: Master Prompt (REUSABLE)

5. **`MASTER_DASHBOARD_PROMPT.md`**
   - Copy-pasteable prompt for agent standardization
   - Includes all patterns and requirements
   - Can be reused for every dashboard

6. **`DASHBOARD_STANDARDIZATION_GUIDE.md`**
   - Quick start guide
   - Document index
   - Common patterns and anti-patterns

---

## How to Use

### Step 1: Read the Contract

Read these in order:
1. `DASHBOARD_ARCHITECTURE.md` - Understand boundaries
2. `DASHBOARD_LANGUAGE_MAP.md` - Learn terminology
3. `DASHBOARD_DECISION_RUBRIC.md` - Know when to use what

### Step 2: Standardize a Dashboard

**Option A: Use Master Prompt (Recommended)**
1. Open `MASTER_DASHBOARD_PROMPT.md`
2. Copy entire prompt
3. Replace `[DASHBOARD_FILE_PATH]` with your dashboard (e.g., `agent-orchestrator/dashboards/next_steps_checklist.html`)
4. Paste into agent conversation
5. Agent will standardize according to architecture contract

**Option B: Manual Audit**
1. Open `DASHBOARD_AUDIT_CHECKLIST.md`
2. Go through each section
3. Mark items that pass ✅
4. Fix items that fail ❌
5. Use patterns from `DASHBOARD_ARCHITECTURE.md`

### Step 3: Verify Changes

After standardization:
- [ ] Test with backend enabled
- [ ] Test with backend disabled (file picker fallback)
- [ ] Test error scenarios
- [ ] Test multi-tab sync (if applicable)
- [ ] Test auto-save (if applicable)

---

## Example Usage

### Standardize `next_steps_checklist.html`:

```
You are a dashboard standardization agent. Your task is to audit and standardize the dashboard file: `agent-orchestrator/dashboards/next_steps_checklist.html`

[... copy rest of MASTER_DASHBOARD_PROMPT.md ...]
```

Agent will:
1. Read architecture contract documents
2. Audit dashboard against checklist
3. Apply standard patterns
4. Fix issues according to contract
5. Provide summary of changes

---

## Key Patterns Enforced

### 1. Data Loading (Hybrid Pattern)
```javascript
// Priority: Backend → File Picker → Embedded → Error
async function loadDashboardData() {
    if (DASHBOARD_CONFIG.backendEnabled) {
        try {
            return await dashboardAPI.getState();
        } catch (error) {
            showConnectionAlert(error);
            // Fall through to file picker
        }
    }
    // ... fallback logic
}
```

### 2. Error Handling
```javascript
function handleError(error, context = {}) {
    // Show user-friendly error with fix steps
    // Log to console
    // Don't break dashboard
}
```

### 3. Mermaid Loading
```javascript
// Check multiple paths: .userInput/mermaid/, diagrams/, etc.
// Fallback to file picker
// Show error with fix steps if not found
```

---

## Must-Have Items (Every Dashboard)

- ✅ Semantic HTML structure
- ✅ JavaScript initialization pattern
- ✅ Error handling function
- ✅ Data loading with fallback (backend → file picker)
- ✅ Graceful degradation (works without backend)

---

## File Structure

```
agent-orchestrator/dashboards/
├── DASHBOARD_ARCHITECTURE.md          # Canonical architecture
├── DASHBOARD_LANGUAGE_MAP.md          # Standardized terminology
├── DASHBOARD_DECISION_RUBRIC.md       # Decision rules
├── DASHBOARD_AUDIT_CHECKLIST.md       # Audit checklist
├── MASTER_DASHBOARD_PROMPT.md         # Reusable prompt
├── DASHBOARD_STANDARDIZATION_GUIDE.md # Quick start guide
├── README_STANDARDIZATION.md          # This file
├── js/
│   ├── dashboard-api-client.js        # Backend API client
│   ├── dashboard-state-manager.js     # State management
│   └── dashboard-realtime.js          # Real-time updates
└── [dashboard files...]
```

---

## Next Steps

1. **Start with one dashboard:**
   - Choose simplest (e.g., `mermaid_viewer.html`)
   - Use master prompt to standardize
   - Verify changes work

2. **Then standardize remaining:**
   - Apply same process to each dashboard
   - Consistency will emerge naturally

3. **Future: Shared Utilities**
   - Create `shared/dashboard-common.css` (shared styles)
   - Create `shared/dashboard-utils.js` (shared functions)
   - Reuse across all dashboards

---

## Questions?

- Check `DASHBOARD_ARCHITECTURE.md` for boundaries
- Check `DASHBOARD_LANGUAGE_MAP.md` for terminology
- Check `DASHBOARD_DECISION_RUBRIC.md` for decision rules
- Check `DASHBOARD_AUDIT_CHECKLIST.md` for audit items

---

**Status:** ✅ Ready for use  
**Last Updated:** 2026-01-20
