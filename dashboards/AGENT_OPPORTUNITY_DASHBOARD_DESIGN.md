# Agent & Opportunity Dashboard - Design Exploration

**Generated:** 2026-01-20  
**Purpose:** Design exploration document for HTML dashboard displaying 8 agents and 8 opportunities

---

## Design Concepts Explored

### Concept 1: Grid Card Layout

**Approach:** 2-column responsive grid with agent cards and opportunity cards side-by-side

**Pros:**
- Clean, modern card-based design
- Easy to scan and compare
- Familiar pattern from existing dashboards
- Responsive to different screen sizes

**Cons:**
- May require scrolling on smaller screens
- Less efficient use of vertical space

**Visual Structure:**
```
[Header: Title + Stats]
[Agent Grid: 4x2 cards]
[Opportunity Grid: 4x2 cards]
[Footer: Meta info]
```

---

### Concept 2: Split-Panel Layout

**Approach:** Two panels (Agents | Opportunities) side-by-side with list-based display

**Pros:**
- Clear separation between agents and opportunities
- Efficient use of horizontal space
- Good for wide screens
- Easy to compare within each category

**Cons:**
- Less responsive on mobile (stacks vertically)
- May feel cramped on smaller screens
- Less visual hierarchy compared to cards

**Visual Structure:**
```
[Header: Title + Stats]
[Agents Panel] | [Opportunities Panel]
[Footer: Meta info]
```

---

### Concept 3: Tabbed Interface

**Approach:** Tabs for Agents/Opportunities with unified card design

**Pros:**
- Focuses attention on one category at a time
- Clean, organized presentation
- Good for detailed views
- Allows for additional tabs in future

**Cons:**
- Requires interaction to see both categories
- Less immediate overview of all information
- One extra click to see full picture

**Visual Structure:**
```
[Header: Title + Stats]
[Tabs: Agents | Opportunities]
[Active Tab Content: Grid of cards]
[Footer: Meta info]
```

---

### Concept 4: Hybrid Dashboard (Selected)

**Approach:** Header with summary stats, 4x2 grid for agents, 4x2 grid for opportunities

**Pros:**
- Combines visual appeal with information density
- Matches existing dashboard patterns in workspace
- Clear visual hierarchy
- Responsive and accessible
- All information visible at once
- Good balance of density and clarity

**Cons:**
- Longer page (but acceptable for overview)
- Requires scrolling on smaller screens (mitigated by responsive design)

**Visual Structure:**
```
[Header: Title + Quick Stats]
[Section: Active Agents (8)]
  [Grid: 4x2 agent cards]
[Section: Legislative Opportunities (8)]
  [Grid: 4x2 opportunity cards]
[Footer: Data sources + Last updated]
```

---

## Selected Design: Hybrid Dashboard (Concept 4)

### Rationale

The Hybrid Dashboard approach was selected because:

1. **Matches Existing Patterns:** Aligns with design system used in `AIR_QUALITY_POLICY_REVIEW_DASHBOARD.html`
2. **Information Density:** Shows all 8 agents and 8 opportunities without requiring interaction
3. **Visual Hierarchy:** Clear separation between sections while maintaining visual consistency
4. **Responsive:** Grid layout adapts well to different screen sizes (4x2 → 2x4 → 1 column)
5. **Accessibility:** All content visible, clear structure, good contrast
6. **Scalability:** Easy to add more items or sections in the future

---

## Design System Elements

### Color System
- **Primary:** `#2563eb` (Blue) - Main actions, headers
- **Success:** `#059669` (Green) - RUNNING status, positive states
- **Warning:** `#d97706` (Yellow/Orange) - WAITING_REVIEW status
- **Error:** `#dc2626` (Red) - Error states
- **Neutral:** `#64748b` (Gray) - IDLE status, secondary text

### Status Badges
- **RUNNING:** Green background, checkmark icon
- **IDLE:** Gray background, neutral icon
- **WAITING_REVIEW:** Yellow/orange background, clock icon
- **BLOCKED:** Red background, stop icon

### Typography
- **Headings:** System font stack, bold weights
- **Body:** System font stack, regular weight
- **Small Text:** 0.875rem (14px) for metadata

### Spacing
- Base unit: 8px (0.5rem)
- Consistent spacing scale: 1, 2, 3, 4, 5, 6 units

### Cards
- White background
- Rounded corners (8px)
- Shadow elevation system
- Hover effects (translateY + enhanced shadow)
- Border-left accent for status/type

---

## Alternative Layouts Considered

1. **Timeline View:** Rejected - Too complex for simple overview
2. **Table View:** Rejected - Less visual appeal, harder to scan
3. **Kanban Board:** Rejected - Over-engineered for this use case
4. **Masonry Layout:** Rejected - Inconsistent card heights would be distracting

---

## Future Enhancement Ideas

1. **Filtering/Search:** Add filter controls to show agents/opportunities by type, status, or relevance
2. **Sorting:** Allow sorting by status, risk level, or relevance
3. **Details Modal:** Click card to see detailed information in modal/expanded view
4. **Data Refresh:** Add manual refresh button to reload data from sources
5. **Export:** Export current view as PDF or CSV
6. **Dark Mode:** Add dark mode toggle (optional)
7. **Live Updates:** WebSocket integration for real-time status updates (future, if backend available)

---

## Implementation Notes

- Single-file HTML for portability
- Embedded CSS in `<style>` tag
- Minimal JavaScript for interactivity (optional enhancements)
- Sample/embedded data (can be replaced with file loading later)
- Follows HTML-only cockpit rules (no frameworks, no build tools)
- Uses design system variables from existing dashboards

---

**End of Design Exploration Document**
