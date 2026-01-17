# 🧭 COMM_EVT Agent Contract (Authoritative)

## Purpose

This document defines the **COMM_EVT agent system**, including agent types, orchestration rules, human review gates, and safety constraints.

COMM_EVT corresponds to:
> **Committee phase — drafting, amendment strategy, and controlled execution**

This is a **high-risk phase**. Governance, monitoring, and human authority are mandatory.

---

## Legislative State

**Current State:** COMM_EVT  
**State Authority:** Human-controlled  
**State Manager:** Legislative State Manager

No agent may advance legislative state.

---

## Agent Type Extensions

The system defines the following agent types:

- **Intelligence** — Read-only, observational
- **Drafting** — Human-gated, high accountability
- **Execution** — World-facing, high risk
- **Learning** — Post-hoc only (not active in COMM_EVT)

All agents are state-scoped and ephemeral.

---

## Intelligence Agents (Read-Only)

### Committee Signal Monitor
**Purpose**
- Monitor committee member positions
- Track media signals and emerging opposition
- Detect shifts in committee dynamics

**Outputs**
- Committee signal summary artifact

**Constraints**
- Read-only
- No strategy generation
- No execution

---

### Stakeholder Mapping Agent
**Purpose**
- Map stakeholders, coalition partners, and opposition
- Update influence and alignment assessments

**Outputs**
- Updated stakeholder map (committee-scoped)

**Constraints**
- Observational only
- No outreach

---

## Drafting Agents (Human-Gated)

### Committee Briefing Packet Agent
**Purpose**
- Generate briefing packets for committee context

**Outputs**
- Committee briefing packet artifact

**Human Review Gate**
- HR_LANG (mandatory)

---

### Legislative Language Drafting Agent
**Purpose**
- Draft legislative language

**Risk Level**
- HIGH

**Review Expectations**
- Estimated review time: 45–90 minutes

**Outputs**
- Legislative language draft artifact

**Human Review Gate**
- HR_LANG (mandatory)

---

### Amendment Strategy Agent
**Purpose**
- Generate amendment strategy options

**Outputs**
- Amendment strategy artifact

**Human Review Gate**
- HR_PRE (mandatory)

---

## Execution Agents (World-Facing — High Risk)

### Committee Outreach Execution Agent
**Purpose**
- Execute staff outreach activities

**Requirements**
- Monitoring dashboard active
- Explicit human authorization

**Constraints**
- Immediate termination capability
- Continuous monitoring required

---

### Coalition Activation Agent
**Purpose**
- Activate coalition partners

**Requirements**
- Monitoring dashboard active
- Explicit human authorization

**Constraints**
- Immediate termination capability
- World-facing execution

---

## State & Review Management

### Legislative State Manager
**Responsibilities**
- Validate legislative state
- Enforce state-scoped permissions
- Prevent unauthorized transitions

---

### Human Review Gate Manager
**Managed Gates**
- HR_LANG — Legislative language
- HR_PRE — Strategic framing / amendments
- HR_MSG — Messaging
- HR_RELEASE — Public release

All drafting outputs must route through the appropriate gate.

---

## Orchestration

### COMM_EVT Orchestrator
**Responsibilities**
- Spawn agents in correct order
- Manage agent lifecycle
- Route artifacts to review queues
- Enforce safety constraints
- Maintain registry and audit logs

---

## Monitoring & Safety

Mandatory safeguards:

- Monitoring required for all execution agents
- Immediate termination capability
- State-aware permission checks
- No self-publication
- No agent-initiated state advancement

Violation → immediate termination.

---

## Documentation

- COMM_EVT_IMPLEMENTATION.md — architecture & usage
- Index file — import convenience

All code must pass linting and comply with this contract.

---

## Final Principle

COMM_EVT is where **power exists**.

Humans decide.  
Agents assist.  
Monitoring never stops.
