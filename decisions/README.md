# System Decisions Registry

This directory contains binding human decisions that govern system behavior.

## Active Decisions

### Dependency Failure Policy
**Decision ID:** `dependency_failure_policy__HUMAN_DECISION__APPROVED.json`  
**Status:** APPROVED  
**Date:** 2026-01-20  
**Selected Option:** C (Hybrid Mode)

**Policy:** System operates in two modes:
- **PRODUCTION:** Fail-fast for all missing dependencies
- **DEVELOPMENT:** Graceful degradation with explicit placeholder marking

All agents must respect this policy. See decision artifact for full implementation requirements.

---

**Last Updated:** 2026-01-20
