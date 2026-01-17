# 📐 Diagram Output Contract (Authoritative)

## Purpose

This document defines how governed system artifacts are translated into
**human-reviewable diagrams** using **Mermaid Flowchart (OSS) syntax**.

Diagrams are:
- Read-only
- State-aware
- Auditable
- Suitable for dashboard embedding
- The primary interface for human review

Mermaid syntax reference:
https://docs.mermaidchart.com/mermaid-oss/syntax/flowchart.html

---

## Authorized Diagram Types (PRE_EVT)

### 1. SYSTEM_STATUS

**Sources**
- monitoring/INTERNAL_STATUS_UPDATE.json
- monitoring/dashboard-status.json
- registry/*

**Shows**
- Legislative state (PRE_EVT)
- Execution status (PAUSED)
- Pending gates (HR_PRE)
- Agent states (IDLE / WAITING_REVIEW)
- Monitoring health

---

### 2. CONCEPT_LANDSCAPE

**Sources**
- artifacts/draft_concept_memo_pre_evt/PRE_CONCEPT.json
- artifacts/draft_concept_memo_pre_evt/PRE_CONCEPT_REFINED.md
- artifacts/draft_concept_memo_pre_evt/PRE_CONCEPT_VARIANTS.json

**Shows**
- Core concept (center)
- Alternative framings (branches)
- Stakeholder alignment
- Opposition presence

Constraints:
- INTERNAL
- NON-AUTHORITATIVE
- No legislative language

---

### 3. RISK_MAP

**Sources**
- analysis/PRE_CONCEPT_RISK_ASSESSMENT.md
- artifacts/opposition_risk_assessment.json (if present)

**Shows**
- Risk categories
- Severity
- Ambiguities
- Human judgment points

---

## Shape Semantics (Binding)

| Shape | Meaning |
|-----|--------|
| `[ ]` | Concept / Artifact |
| `( )` | Status / Process |
| `{ }` | Human decision gate |
| `(( ))` | State |

---

## Rules

- Diagrams may not advance state
- Diagrams may not imply approval
- Ambiguity must be shown, not resolved
- All diagrams must be labeled:
  - INTERNAL
  - UNDER HUMAN REVIEW (HR_PRE)

---

## Final Principle

Diagrams are for **human judgment**, not automation.
