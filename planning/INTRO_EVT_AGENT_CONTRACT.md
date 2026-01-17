# 🧭 INTRO_EVT Agent Contract (Authoritative)

## Purpose

This document defines the **INTRO_EVT agent suite**, orchestration flow, governance constraints, and review requirements.

INTRO_EVT corresponds to:
> **Bill vehicle identified / legitimacy and framing phase**

All agents defined here operate **after PRE_EVT approval** and **before COMM_EVT**.

---

## Legislative State

**Current State:** INTRO_EVT  
**State Authority:** Human-controlled  
**State File:** state/legislative-state.json

No agent may advance state beyond INTRO_EVT.

---

## Agent Classes & Responsibilities

### 1. Intelligence Agents (Read-Only)

These agents operate observationally and may not generate strategy or world-facing actions.

#### intel_signal_scan_intro_evt.py
**Purpose**
- Scan industry, court, agency, and media signals relevant to the identified bill vehicle

**Outputs**
- Updated signal summary artifact

**Constraints**
- Read-only
- No execution
- No publishing

---

#### intel_stakeholder_map_intro_evt.py
**Purpose**
- Build or update stakeholder map
- Include sponsor alignment scores and relevance to bill vehicle

**Outputs**
- Stakeholder map artifact (INTRO_EVT scoped)

**Constraints**
- Observational only
- No outreach

---

#### intel_opposition_detect_intro_evt.py
**Purpose**
- Detect opposition signals and emerging counter-narratives

**Outputs**
- Opposition analysis artifact

**Constraints**
- Read-only
- Early warning only

---

### 2. Drafting Agents (Human-Gated)

Drafting agents generate **reviewable artifacts only** and are blocked by human approval gates.

#### draft_framing_intro_evt.py
**Purpose**
- Generate INTRO_FRAME artifact
- Articulate legitimacy, narrative framing, and policy justification

**Outputs**
- INTRO_FRAME artifact

**Review Gate**
- HR_PRE (mandatory)

---

#### draft_whitepaper_intro_evt.py
**Purpose**
- Generate INTRO_WHITEPAPER
- Intended for academic and technical validation

**Outputs**
- INTRO_WHITEPAPER artifact

**Review Gate**
- HR_PRE (mandatory)

---

## Orchestration & Execution Flow

### Orchestration Script
**File:** orchestrate_intro_evt.py

### Execution Order
1. Monitoring dashboard must be running
2. Intelligence agents spawn in parallel
3. Orchestrator waits for intelligence completion
4. Drafting agents spawn sequentially
5. Draft outputs routed to review/HR_PRE_queue.json
6. Execution pauses pending human review

---

## Monitoring & Audit

- All agents must register in registry/
- All actions logged to audit/
- Dashboard compatibility maintained
- Heartbeat signals required

---

## Compliance & Safety

- No agent may self-publish
- No agent may advance legislative state
- Drafting agents require HR_PRE approval
- All artifacts must be auditable
- All permissions are state-scoped

---

## Diagram Compatibility

All INTRO_EVT artifacts must be compatible with:
- SYSTEM_STATUS diagrams
- CONCEPT / FRAMING diagrams
- RISK / OPPOSITION diagrams

No artifact may bypass the diagram output layer.

---

## Final Principle

INTRO_EVT is about **legitimacy and framing**, not execution.

Humans approve direction.  
Agents prepare clarity.  
State advances only by authority.
