# Viewable Files Index

This document lists all markdown (.md), mermaid (.mmd), and JSON files that should be easily viewable in HTML with approve/reject/yes/no buttons for human review workflows.

**Last Updated:** 2026-01-20

---

## JSON Artifacts Requiring Review

### Review Queue Files (4 files)

**Location:** `agent-orchestrator/review/`

1. ✅ **`HR_PRE_queue.json`**
   - **Purpose:** Pre-event review queue
   - **Contains:** Pending reviews for concept memos and policy framing
   - **Viewable In:** `unified_review_viewer.html`, `cockpit_review.html`
   - **Action Required:** Approve/Reject buttons available

2. ✅ **`HR_LANG_queue.json`**
   - **Purpose:** Legislative language review queue
   - **Contains:** Pending reviews for drafted legislative text
   - **Viewable In:** `unified_review_viewer.html`, `cockpit_review.html`
   - **Action Required:** Approve/Reject buttons available

3. ✅ **`HR_MSG_queue.json`**
   - **Purpose:** Messaging review queue
   - **Contains:** Pending reviews for floor messaging and talking points
   - **Viewable In:** `unified_review_viewer.html`, `cockpit_review.html`
   - **Action Required:** Approve/Reject buttons available

4. ✅ **`HR_RELEASE_queue.json`**
   - **Purpose:** Release review queue
   - **Contains:** Pending reviews for final release artifacts
   - **Viewable In:** `unified_review_viewer.html`, `cockpit_review.html`
   - **Action Required:** Approve/Reject buttons available

### JSON Artifact Files (79 files)

**Location:** `agent-orchestrator/artifacts/{agent_id}/*.json`

**Criteria:** Files with `_meta.status: "SPECULATIVE"` and `requires_review: not null`

**Examples:**
- ✅ `artifacts/draft_concept_memo_pre_evt/PRE_CONCEPT.json`
- ✅ `artifacts/draft_framing_intro_evt/INTRO_FRAME.json`
- ✅ `artifacts/draft_whitepaper_intro_evt/INTRO_WHITEPAPER.json`
- ✅ `artifacts/draft_legislative_language_comm_evt/COMM_LEGISLATIVE_LANGUAGE.json`
- ✅ `artifacts/draft_amendment_strategy_comm_evt/COMM_AMENDMENT_STRATEGY.json`
- ✅ `artifacts/floor_evt/FLOOR_MESSAGING.json`
- ✅ Plus 73 more JSON artifacts

**Viewable In:** `unified_review_viewer.html`, `cockpit_review.html` (via review queue files)

**Action Required:** Approve/Reject buttons available when loaded from review queue

---

## Markdown Review Documents (21 files)

**Location:** `agent-orchestrator/artifacts/review/*.md`

**All files viewable with interactive checkboxes for TODOs:**

1. ✅ **`learning__codebase_exploration__DRAFT_v1.md`**
   - **TODOs:** Yes (5 TODO items)
   - **Action Items:** Investigate timestamp generation, review registry deduplication, verify review gate mapping
   - **Viewable In:** `unified_review_viewer.html`, `markdown_review_viewer.html`

2. ✅ **`business_outcome_acceleration_brief__20260108_023219.md`**
   - **Status:** ACTION_REQUIRED ⚠️
   - **TODOs:** Priority actions for review queue routing
   - **Action Items:** Fix review queue routing, re-run diagnostic, backfill decision logs
   - **Viewable In:** `unified_review_viewer.html`, `markdown_review_viewer.html`

3. ✅ **`critical_blockers_fixed__DRAFT_v1.md`**
   - **TODOs:** Yes (14 checkbox TODOs: `- [ ]`)
   - **Action Items:** Integration test script, bounds checking, error recovery, performance optimization
   - **Viewable In:** `unified_review_viewer.html`, `markdown_review_viewer.html`

4. ✅ **`system_advancement_implementation__diagnostic_accuracy_operator_clarity__DRAFT_v1.md`**
   - **Purpose:** System advancement implementation status
   - **Viewable In:** `unified_review_viewer.html`, `markdown_review_viewer.html`

5. ✅ **`agent_contract_system_implementation__DRAFT_v1.md`**
   - **Purpose:** Agent contract system implementation
   - **Viewable In:** `unified_review_viewer.html`, `markdown_review_viewer.html`

6. ✅ **`orchestrator_core__coalition_grassroots_cosponsorship_swarms__DRAFT_v1.md`**
   - **Purpose:** Coalition and grassroots implementation
   - **Viewable In:** `unified_review_viewer.html`, `markdown_review_viewer.html`

7. ✅ **`kpi_feedback_loop__implementation_complete__DRAFT_v1.md`**
   - **Purpose:** KPI feedback loop implementation
   - **Viewable In:** `unified_review_viewer.html`, `markdown_review_viewer.html`

8. ✅ **`kpi_framework__implementation_complete__DRAFT_v1.md`**
   - **Purpose:** KPI framework implementation
   - **Viewable In:** `unified_review_viewer.html`, `markdown_review_viewer.html`

9. ✅ **`revolving_door_operator_brief__20260120.md`**
   - **Purpose:** Revolving door operator brief
   - **Viewable In:** `unified_review_viewer.html`, `markdown_review_viewer.html`

10. ✅ **`temporal_dynamics__implementation_complete__DRAFT_v1.md`**
    - **Purpose:** Temporal dynamics implementation
    - **Viewable In:** `unified_review_viewer.html`, `markdown_review_viewer.html`

11. ✅ **`api_exposure_guidance_signature__implementation_status__DRAFT_v1.md`**
    - **Purpose:** API exposure implementation status
    - **Viewable In:** `unified_review_viewer.html`, `markdown_review_viewer.html`

12. ✅ **`10k_reading_capability__implementation_complete__DRAFT_v1.md`**
    - **Purpose:** 10K reading capability implementation
    - **Viewable In:** `unified_review_viewer.html`, `markdown_review_viewer.html`

13. ✅ **`bill_risk_extraction__wi_charge_analysis__DRAFT_v1.md`**
    - **Purpose:** Bill risk extraction for Wi-Charge analysis
    - **Viewable In:** `unified_review_viewer.html`, `markdown_review_viewer.html`

14. ✅ **`control_plane_integration__implementation_complete__DRAFT_v1.md`**
    - **Purpose:** Control plane integration implementation
    - **Viewable In:** `unified_review_viewer.html`, `markdown_review_viewer.html`

15. ✅ **`artifact_viewer_integration__implementation_complete__DRAFT_v1.md`**
    - **Purpose:** Artifact viewer integration implementation
    - **Viewable In:** `unified_review_viewer.html`, `markdown_review_viewer.html`

16-21. ✅ Plus 6 more DRAFT markdown files in `artifacts/review/`

**Features:**
- Interactive checkboxes for `- [ ]` (unchecked) and `- [x]` (checked) TODO items
- Auto-save checkbox state to localStorage
- TODO statistics (total, completed, remaining)
- Action Required / Draft status detection

---

## Mermaid Diagrams (15 files)

**Location:** `agent-orchestrator/artifacts/**/*.mmd`

**All files viewable with Mermaid.js rendering:**

1. ✅ **`AGENT_DEPENDENCY_GRAPH.mmd`**
   - **Location:** `artifacts/AGENT_DEPENDENCY_GRAPH.mmd`
   - **Viewable In:** `unified_review_viewer.html`, `mermaid_viewer.html`

2. ✅ **`vibe_coding_workflow_with_agents.mmd`**
   - **Location:** `artifacts/vibe_coding_workflow_with_agents.mmd`
   - **Viewable In:** `unified_review_viewer.html`, `mermaid_viewer.html`

3. ✅ **`intro_evt/FUTURE_STATE_TRANSITIONS.mmd`**
   - **Location:** `artifacts/intro_evt/FUTURE_STATE_TRANSITIONS.mmd`
   - **Viewable In:** `unified_review_viewer.html`, `mermaid_viewer.html`

4. ✅ **`policy/diagrams/system_context.mmd`**
   - **Location:** `artifacts/policy/diagrams/system_context.mmd`
   - **Viewable In:** `unified_review_viewer.html`, `mermaid_viewer.html`, `artifacts/policy/viewer.html`

5. ✅ **`policy/diagrams/stakeholder_hierarchy.mmd`**
   - **Location:** `artifacts/policy/diagrams/stakeholder_hierarchy.mmd`
   - **Viewable In:** `unified_review_viewer.html`, `mermaid_viewer.html`, `artifacts/policy/viewer.html`

6. ✅ **`policy/diagrams/section_to_ask_flow.mmd`**
   - **Location:** `artifacts/policy/diagrams/section_to_ask_flow.mmd`
   - **Viewable In:** `unified_review_viewer.html`, `mermaid_viewer.html`, `artifacts/policy/viewer.html`

7. ✅ **`policy/diagrams/section_priority_map.mmd`**
   - **Location:** `artifacts/policy/diagrams/section_priority_map.mmd`
   - **Viewable In:** `unified_review_viewer.html`, `mermaid_viewer.html`, `artifacts/policy/viewer.html`

8. ✅ **`policy/diagrams/master_dashboard.mmd`**
   - **Location:** `artifacts/policy/diagrams/master_dashboard.mmd`
   - **Viewable In:** `unified_review_viewer.html`, `mermaid_viewer.html`, `artifacts/policy/viewer.html`

9. ✅ **`policy/diagrams/execution_paths_flowchart.mmd`**
   - **Location:** `artifacts/policy/diagrams/execution_paths_flowchart.mmd`
   - **Viewable In:** `unified_review_viewer.html`, `mermaid_viewer.html`, `artifacts/policy/viewer.html`

10. ✅ **`policy/diagrams/comprehensive_overview.mmd`**
    - **Location:** `artifacts/policy/diagrams/comprehensive_overview.mmd`
    - **Viewable In:** `unified_review_viewer.html`, `mermaid_viewer.html`, `artifacts/policy/viewer.html`

11. ✅ **`policy/diagrams/completion_status.mmd`**
    - **Location:** `artifacts/policy/diagrams/completion_status.mmd`
    - **Viewable In:** `unified_review_viewer.html`, `mermaid_viewer.html`, `artifacts/policy/viewer.html`

12. ✅ **`policy/diagrams/clear_ask_decision_tree.mmd`**
    - **Location:** `artifacts/policy/diagrams/clear_ask_decision_tree.mmd`
    - **Viewable In:** `unified_review_viewer.html`, `mermaid_viewer.html`, `artifacts/policy/viewer.html`

13. ✅ **`policy/diagrams/agent_integration_flow.mmd`**
    - **Location:** `artifacts/policy/diagrams/agent_integration_flow.mmd`
    - **Viewable In:** `unified_review_viewer.html`, `mermaid_viewer.html`, `artifacts/policy/viewer.html`

14. ✅ **`policy/diagrams/90_day_timeline.mmd`**
    - **Location:** `artifacts/policy/diagrams/90_day_timeline.mmd`
    - **Viewable In:** `unified_review_viewer.html`, `mermaid_viewer.html`, `artifacts/policy/viewer.html`

15. ✅ **`development/RESOURCE_ALLOCATION_SYSTEM.mmd`**
    - **Location:** `artifacts/development/RESOURCE_ALLOCATION_SYSTEM.mmd`
    - **Viewable In:** `unified_review_viewer.html`, `mermaid_viewer.html`

**Features:**
- Render diagrams using Mermaid.js
- Toggle source code view
- Error handling with source display
- List of known diagrams for reference

---

## Summary

### Total Files Viewable

- **JSON Review Queue Files:** 4 files
- **JSON Artifact Files:** 79 files (when loaded via review queues)
- **Markdown Review Documents:** 21 files
- **Mermaid Diagrams:** 15 files

**Total:** 119 files viewable in HTML with interactive review/approval features

---

## Recommended Viewers

### For JSON Artifacts
1. **Primary:** `unified_review_viewer.html` (Tab 1: JSON Artifacts)
2. **Alternative:** `cockpit_review.html` (dedicated JSON review)

### For Markdown Files
1. **Primary:** `unified_review_viewer.html` (Tab 2: Markdown Files)
2. **Alternative:** `markdown_review_viewer.html` (dedicated markdown viewer)

### For Mermaid Diagrams
1. **Primary:** `unified_review_viewer.html` (Tab 3: Mermaid Diagrams)
2. **Alternative:** `mermaid_viewer.html` (dedicated mermaid viewer)

### For Everything
- **Best Option:** `unified_review_viewer.html` (all-in-one interface)

---

## Quick Access

**Open any viewer by:**
1. Navigate to: `agent-orchestrator/dashboards/`
2. Open: `index.html` (main index with links to all viewers)
3. Or open directly:
   - `unified_review_viewer.html`
   - `cockpit_review.html`
   - `markdown_review_viewer.html`
   - `mermaid_viewer.html`

---

**Last Updated:** 2026-01-20  
**Status:** ✅ All files identified and viewable
