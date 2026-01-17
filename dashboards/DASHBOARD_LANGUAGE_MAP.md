# Dashboard Language Map

**Purpose:** Standardized terminology for discussing dashboard architecture across HTML, JavaScript, State, and Backend.

**Last Updated:** 2026-01-20  
**Version:** 1.0.0

---

## When Discussing Structure (HTML/CSS)

### Use These Terms:

| Term | Meaning | Example |
|------|---------|---------|
| **Semantic HTML** | HTML elements that convey meaning (`<section>`, `<article>`) | "Use semantic HTML for accessibility" |
| **Container** | `<div>` or `<section>` that groups related content | "The stats container holds all statistics" |
| **Target element** | Element with `id` attribute for JavaScript targeting | "Target element `#stats-container` for updates" |
| **Progressive enhancement** | Content visible without JavaScript | "Dashboard uses progressive enhancement" |
| **CSS class** | Reusable style identifier | "Apply CSS class `.card` to all sections" |
| **Inline styles** | Styles in `style=""` attribute (avoid when possible) | "Move inline styles to CSS class" |

### Avoid These Terms:
- ❌ "Component" (implies framework, use "element" or "container")
- ❌ "Template" (implies templating engine, use "structure" or "pattern")
- ❌ "View" (ambiguous, use "section" or "container")

---

## When Discussing Behavior (JavaScript)

### Use These Terms:

| Term | Meaning | Example |
|------|---------|---------|
| **Event handler** | Function called on user interaction | "Add event handler for button click" |
| **Data loading** | Fetching JSON/API/file content | "Data loading happens in `loadDashboardData()`" |
| **State update** | Changing in-memory data structure | "State update triggers re-render" |
| **DOM manipulation** | Changing HTML content dynamically | "DOM manipulation updates `#stats-container`" |
| **Error handling** | Catching and displaying errors gracefully | "Error handling shows user-friendly messages" |
| **Initialization** | Setup code that runs on page load | "Initialization happens in `DOMContentLoaded`" |
| **Rendering** | Converting data to HTML display | "Rendering updates all visible sections" |

### Avoid These Terms:
- ❌ "Component" (use "function" or "module")
- ❌ "Hook" (implies React, use "event handler")
- ❌ "Mixin" (implies framework, use "utility function")

---

## When Discussing Data/State

### Use These Terms:

| Term | Meaning | Example |
|------|---------|---------|
| **In-memory state** | JavaScript variables that hold current data | "In-memory state is lost on page refresh" |
| **localStorage state** | Data persisted in browser storage | "localStorage state survives page refresh" |
| **Backend state** | Authoritative data from server | "Backend state is the source of truth" |
| **State snapshot** | Point-in-time copy of current state | "Take state snapshot before mutation" |
| **State update** | Changing state values | "State update triggers re-render" |
| **Data loading** | Fetching state from source | "Data loading populates in-memory state" |
| **State sync** | Keeping multiple tabs/windows in sync | "State sync uses BroadcastChannel API" |

### Avoid These Terms:
- ❌ "Store" (implies Redux/Vuex, use "state" or "data")
- ❌ "Action" (implies Redux, use "function" or "handler")
- ❌ "Mutation" (implies Vuex, use "state update")

---

## When Discussing Backend

### Use These Terms:

| Term | Meaning | Example |
|------|---------|---------|
| **API endpoint** | URL that returns data or accepts commands | "API endpoint `/api/v1/dashboard/state` returns state" |
| **Backend unavailable** | Server is offline or unreachable | "If backend unavailable, use file picker fallback" |
| **Authoritative source** | Server-side data that is the single source of truth | "Backend is authoritative source for artifacts" |
| **State transition** | Immutable change to backend state (approve/reject) | "State transition creates audit log entry" |
| **Connection status** | Whether dashboard can reach backend | "Connection status shown in header" |
| **Graceful degradation** | Dashboard works without backend | "Dashboard uses graceful degradation pattern" |

### Avoid These Terms:
- ❌ "Server" (ambiguous, use "backend")
- ❌ "API" alone (use "backend API" or "API endpoint")
- ❌ "Request" (ambiguous, use "API call" or "fetch")

---

## When Discussing Mermaid

### Use These Terms:

| Term | Meaning | Example |
|------|---------|---------|
| **Diagram code** | Mermaid syntax (`.mmd` file content) | "Load diagram code from `.mmd` file" |
| **Diagram container** | HTML `<div class="mermaid">` that holds diagram | "Mermaid renders in diagram container" |
| **Diagram rendering** | Converting Mermaid code to SVG visualization | "Diagram rendering happens after data loads" |
| **Mermaid initialization** | Setting up Mermaid.js library | "Mermaid initialization configures theme" |
| **Diagram source** | Where diagram code comes from (file, embedded, generated) | "Diagram source can be file picker or backend" |

### Avoid These Terms:
- ❌ "Chart" (ambiguous, use "diagram")
- ❌ "Visualization" (too generic, use "Mermaid diagram")
- ❌ "Graph" (implies data structure, use "diagram")

---

## When Discussing Errors

### Use These Terms:

| Term | Meaning | Example |
|------|---------|---------|
| **Error boundary** | UI element that displays errors gracefully | "Error boundary shows user-friendly error message" |
| **Connection alert** | Warning when backend is unavailable | "Connection alert appears in header" |
| **Fix steps** | Actionable instructions to resolve error | "Error shows fix steps: 1) Start backend, 2) Reload page" |
| **Error handling** | Code that catches and displays errors | "Error handling prevents dashboard crash" |
| **Graceful failure** | Dashboard continues working despite error | "Dashboard uses graceful failure pattern" |

### Avoid These Terms:
- ❌ "Exception" (technical, use "error")
- ❌ "Throw" (technical, use "show error" or "display error")
- ❌ "Catch" (technical, use "handle error")

---

## When Discussing File Loading

### Use These Terms:

| Term | Meaning | Example |
|------|---------|---------|
| **File picker** | User selects file via `<input type="file">` | "File picker allows offline data loading" |
| **File reader** | JavaScript `FileReader` API for reading file content | "File reader parses JSON from selected file" |
| **Embedded data** | JSON hardcoded in HTML `<script>` tag | "Embedded data provides fallback snapshot" |
| **Data source priority** | Order of fallback (backend → file picker → embedded) | "Data source priority: backend first, file picker second" |

### Avoid These Terms:
- ❌ "Upload" (implies sending to server, use "load" or "select")
- ❌ "Import" (implies module system, use "load" or "load data")

---

## Quick Reference: Term Substitution

| ❌ Don't Say | ✅ Say Instead |
|-------------|---------------|
| "Component" | "Element", "Container", "Function" |
| "Store" | "State", "Data" |
| "Action" | "Handler", "Function" |
| "Hook" | "Event Handler" |
| "Template" | "Structure", "Pattern" |
| "View" | "Section", "Container" |
| "Server" | "Backend" |
| "Chart" | "Diagram" |
| "Upload" | "Load", "Select" |
| "Exception" | "Error" |

---

**Usage:**
- When discussing dashboard architecture, use terms from this map
- When writing code, use terms consistently
- When documenting, use terms from this map
- When asking questions, use terms from this map
