# Diagram Index

**Master Diagram:** `.userInput/agent orchestrator 1.6.mmd` (939 lines, authoritative source)

This document catalogs all diagrams in the agent-orchestrator system and their relationship to the master diagram.

---

## Master Diagram

- **Location:** `.userInput/agent orchestrator 1.6.mmd`
- **Version:** 1.6
- **Status:** Active & Authoritative
- **Description:** Complete system architecture showing legislative spine, AI services, agents, review gates, memory systems, and execution loops
- **Last Verified:** 2026-01-07

---

## Derived Diagrams

All diagrams below are specialized views derived from the master diagram.

### System Context Diagrams

| Diagram | Location | Focus Area | Last Updated |
|---------|----------|------------|--------------|
| Dashboard System Context | `monitoring/DASHBOARD_SYSTEM_CONTEXT.mmd` | Dashboard layer, data flow, legislative timeline | 2026-01-20 |
| Phase 3 System Context | `execution/PHASE3_SYSTEM_CONTEXT.mmd` | Execution layer, API routes, execution agents | 2026-01-20 |
| System Context | `execution/SYSTEM_CONTEXT.mmd` | Core orchestrator, intelligence, drafting, execution layers | 2026-01-20 |
| Policy System Context | `artifacts/policy/diagrams/system_context.mmd` | Policy artifacts integration, READ-ONLY context | 2026-01-20 |

### Execution Diagrams

| Diagram | Location | Focus Area | Last Updated |
|---------|----------|------------|--------------|
| Execution Flow | `execution/EXECUTION_FLOW.mmd` | Execution workflow and state transitions | 2026-01-20 |
| Phase 3 Execution Verified | `execution/PHASE3_EXECUTION_VERIFIED.mmd` | Verified execution components | 2026-01-20 |
| Phase 3 Complete | `execution/PHASE3_COMPLETE.mmd` | Phase 3 completion status | 2026-01-20 |
| Execution Complete | `execution/EXECUTION_COMPLETE.mmd` | Execution completion overview | 2026-01-20 |
| Next Steps | `execution/NEXT_STEPS.mmd` | Future execution enhancements | 2026-01-20 |

### Monitoring & Dashboard Diagrams

| Diagram | Location | Focus Area | Last Updated |
|---------|----------|------------|--------------|
| Dashboard Status | `monitoring/dashboard-status.mmd` | System status visualization | 2026-01-20 |
| Timeline Chart | `monitoring/timeline-chart.mmd` | Gantt-style timeline view | 2026-01-20 |

### Policy Artifact Diagrams

| Diagram | Location | Focus Area | Last Updated |
|---------|----------|------------|--------------|
| Stakeholder Hierarchy | `artifacts/policy/diagrams/stakeholder_hierarchy.mmd` | Stakeholder relationships and influence | 2026-01-20 |
| 90 Day Timeline | `artifacts/policy/diagrams/90_day_timeline.mmd` | 90-day execution timeline | 2026-01-20 |
| Execution Paths Flowchart | `artifacts/policy/diagrams/execution_paths_flowchart.mmd` | Three execution paths visualization | 2026-01-20 |
| Section Priority Map | `artifacts/policy/diagrams/section_priority_map.mmd` | Bill section priority mapping | 2026-01-20 |
| Clear Ask Decision Tree | `artifacts/policy/diagrams/clear_ask_decision_tree.mmd` | Decision tree for clear asks | 2026-01-20 |
| Comprehensive Overview | `artifacts/policy/diagrams/comprehensive_overview.mmd` | Comprehensive policy overview | 2026-01-20 |
| Section to Ask Flow | `artifacts/policy/diagrams/section_to_ask_flow.mmd` | Flow from bill sections to asks | 2026-01-20 |
| Master Dashboard | `artifacts/policy/diagrams/master_dashboard.mmd` | Master policy dashboard | 2026-01-20 |
| Agent Integration Flow | `artifacts/policy/diagrams/agent_integration_flow.mmd` | How agents reference policy artifacts | 2026-01-20 |
| Completion Status | `artifacts/policy/diagrams/completion_status.mmd` | Policy artifact completion status | 2026-01-20 |

### Drafting Diagrams

| Diagram | Location | Focus Area | Last Updated |
|---------|----------|------------|--------------|
| Intro Frame | `diagrams/INTRO_FRAME.mmd` | INTRO_EVT framing visualization | 2026-01-20 |
| Intro Frame Mermaid | `diagrams/INTRO_FRAME_mermaid.mmd` | INTRO_EVT frame (Mermaid format) | 2026-01-20 |
| Intro Whitepaper | `diagrams/INTRO_WHITEPAPER.mmd` | INTRO_EVT whitepaper structure | 2026-01-20 |

---

## Diagram to Master Diagram Mapping

### Legislative Spine Components

All diagrams that show legislative states map to:
- **Master Section:** Legislative Process Spine (PRE_EVT → IMPL_EVT)
- **Master Elements:** State transitions, artifacts per state, review gates

### Agent Layer Components

Diagrams showing agents map to:
- **Master Section:** Agent Orchestration Model
- **Master Elements:** Agent types (Intelligence, Drafting, Execution, Learning), agent lifecycle, spawn/retire rules

### Review Gates

Diagrams showing review gates map to:
- **Master Section:** Human Review Gates
- **Master Elements:** HR_PRE, HR_LANG, HR_MSG, HR_RELEASE

### Execution Components

Diagrams showing execution map to:
- **Master Section:** Execution Loop
- **Master Elements:** Strategy decomposition, tactical planning, tactic execution, live monitoring, tactical retuning

### Memory & Learning

Diagrams showing learning/memory map to:
- **Master Section:** Memory & Learning Systems
- **Master Elements:** Evidence store, tactic performance history, narrative effectiveness log, legislative outcomes, causal attribution engine

---

## Diagram Maintenance

When updating diagrams:

1. **Reference Master:** All diagrams must reference `.userInput/agent orchestrator 1.6.mmd`
2. **Stay Aligned:** Diagrams should not contradict master diagram
3. **Update Index:** Update this index when adding new diagrams
4. **Version Control:** Track diagram changes in git

---

## Validation

Run validation to ensure all diagrams reference master:

```bash
python scripts/validate_diagram_references.py
```

---

**Last Updated:** 2026-01-20  
**Total Diagrams:** 24  
**Master Diagram References:** All diagrams updated
