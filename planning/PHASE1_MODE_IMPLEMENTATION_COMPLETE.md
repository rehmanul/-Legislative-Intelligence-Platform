# Phase 1 Mode Policy Implementation - Complete

**Date:** 2026-01-20  
**Status:** ✅ Implementation Complete  
**Decision Reference:** `agent-orchestrator/decisions/dependency_failure_policy__HUMAN_DECISION__APPROVED.json`

---

## Summary

All Phase 1 agents have been updated to enforce the hybrid mode dependency failure policy:
- **PRODUCTION mode:** Fail-fast when dependencies are missing
- **DEVELOPMENT mode:** Graceful degradation with explicit placeholder marking

---

## Implementation Details

### 1. Mode Configuration System

**File:** `agent-orchestrator/lib/mode_config.py`

**Functions:**
- `get_system_mode()` - Get mode from `SYSTEM_MODE` environment variable
- `is_production_mode()` - Check if in PRODUCTION mode
- `is_development_mode()` - Check if in DEVELOPMENT mode
- `validate_mode()` - Validate mode is set (required at agent startup)

**Usage:**
```bash
# Set mode before running agents
export SYSTEM_MODE=DEVELOPMENT  # or PRODUCTION
```

---

### 2. Bill Parser Agent (`intel_bill_parser_pre_evt.py`)

**Updates:**
- Mode validation at startup
- PRODUCTION: Raises exception if bill PDF not found
- DEVELOPMENT: Generates placeholder structure with explicit `PLACEHOLDER` status
- Artifact `_meta` includes:
  - `system_mode`: Current mode
  - `is_placeholder`: Whether data is placeholder
  - `dependency_status`: Bill PDF and text extraction status

**Behavior:**
- PRODUCTION: Fails immediately if PDF not found or extraction fails
- DEVELOPMENT: Generates placeholder bill structure, marks as `PLACEHOLDER`

---

### 3. Member Database Builder (`intel_member_database_builder_pre_evt.py`)

**Updates:**
- Mode validation at startup
- Checks for cached member data before failing
- PRODUCTION: Raises exception if API unavailable and no cached data
- DEVELOPMENT: Generates placeholder member with explicit `PLACEHOLDER` status
- Artifact `_meta` includes dependency status

**Behavior:**
- PRODUCTION: Fails if no API key and no cached data
- DEVELOPMENT: Generates placeholder member structure, marks as `PLACEHOLDER`

---

### 4. Committee Briefing Agent (`draft_committee_briefing_comm_evt.py`)

**Updates:**
- Mode validation at startup
- Dependency validation function: `validate_dependencies()`
- PRODUCTION: Fails if any required dependency missing
- DEVELOPMENT: Continues with placeholders, marks artifact as `SPECULATIVE` with missing dependencies list
- Artifact `_meta` includes:
  - `missing_dependencies`: List of missing dependencies
  - `is_placeholder`: Whether any dependencies are placeholders

**Required Dependencies:**
- Bill structure (BILL_STRUCTURE.json)
- Authority citations (AUTHORITY_CITATIONS.json)
- Member database (MEMBER_DATABASE.json)

**Behavior:**
- PRODUCTION: Validates all dependencies exist and are non-empty, fails if any missing
- DEVELOPMENT: Processes available dependencies, marks missing ones in artifact metadata

---

### 5. Staff One-Pager Agent (`draft_staff_one_pager_comm_evt.py`)

**Updates:**
- Mode validation at startup
- Dependency validation function: `validate_dependencies()`
- PRODUCTION: Fails if policy context missing
- DEVELOPMENT: Uses generic content, marks as `INCOMPLETE` with missing dependency list
- Artifact `_meta` includes missing dependencies

**Required Dependencies:**
- Bill structure (BILL_STRUCTURE.json)
- Authority citations (AUTHORITY_CITATIONS.json)
- Policy context (PRE_CONCEPT.json)

**Behavior:**
- PRODUCTION: Validates policy context exists, fails if missing
- DEVELOPMENT: Generates one-pager with generic problem statement if context missing, marks as `INCOMPLETE`

---

## Artifact Status Marking

### Status Values

- **PLACEHOLDER:** Data is placeholder (DEVELOPMENT mode only)
- **INCOMPLETE:** Artifact generated but missing dependencies (DEVELOPMENT mode only)
- **SPECULATIVE:** Normal speculative status (default for all artifacts until human approval)
- **ACTIONABLE:** After human approval (not set by agents)

### Artifact Metadata Fields

All artifacts now include:
```json
{
  "_meta": {
    "system_mode": "PRODUCTION" | "DEVELOPMENT",
    "is_placeholder": true | false,
    "missing_dependencies": ["dependency1", "dependency2"],
    "dependency_status": {
      "bill_pdf_found": true | false,
      "api_available": true | false,
      "mode": "PRODUCTION" | "DEVELOPMENT"
    }
  }
}
```

---

## Testing Instructions

### Development Mode Testing

```bash
# Set development mode
export SYSTEM_MODE=DEVELOPMENT

# Run agents (will generate placeholders if dependencies missing)
python agent-orchestrator/agents/intel_bill_parser_pre_evt.py
python agent-orchestrator/agents/intel_member_database_builder_pre_evt.py
python agent-orchestrator/agents/draft_committee_briefing_comm_evt.py
python agent-orchestrator/agents/draft_staff_one_pager_comm_evt.py
```

**Expected:** Agents complete with placeholder data, artifacts marked as `PLACEHOLDER` or `INCOMPLETE`

### Production Mode Testing

```bash
# Set production mode
export SYSTEM_MODE=PRODUCTION

# Run agents (will fail if dependencies missing)
python agent-orchestrator/agents/intel_bill_parser_pre_evt.py
python agent-orchestrator/agents/intel_member_database_builder_pre_evt.py
python agent-orchestrator/agents/draft_committee_briefing_comm_evt.py
python agent-orchestrator/agents/draft_staff_one_pager_comm_evt.py
```

**Expected:** Agents fail with clear error messages if dependencies missing

---

## Next Steps

1. **End-to-End Testing**
   - Test in DEVELOPMENT mode with missing dependencies
   - Test in PRODUCTION mode with all dependencies present
   - Test in PRODUCTION mode with missing dependencies (should fail)

2. **Phase 2 Implementation**
   - Begin Phase 2 agents with mode policy in place
   - All Phase 2 agents must respect mode policy
   - Document mode requirements in Phase 2 agent contracts

3. **Documentation**
   - Update agent rules to include mode policy
   - Add mode configuration to quick start guide
   - Document mode behavior in agent README

---

## Files Modified

- `agent-orchestrator/lib/mode_config.py` (NEW)
- `agent-orchestrator/agents/intel_bill_parser_pre_evt.py` (UPDATED)
- `agent-orchestrator/agents/intel_member_database_builder_pre_evt.py` (UPDATED)
- `agent-orchestrator/agents/draft_committee_briefing_comm_evt.py` (UPDATED)
- `agent-orchestrator/agents/draft_staff_one_pager_comm_evt.py` (UPDATED)

---

**Last Updated:** 2026-01-20  
**Status:** ✅ Ready for Testing
