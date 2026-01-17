# Policy Artifacts Implementation Review Checklist

**Review Date:** _______________  
**Reviewer:** _______________  
**Status:** ⬜ Pending | ✅ Complete | ⚠️ Issues Found

---

## 1. Directory Structure Verification

- [ ] **Directory exists:** `agent-orchestrator/artifacts/policy/`
- [ ] **All 8 files present:**
  - [ ] `README.md`
  - [ ] `key_findings.md`
  - [ ] `stakeholder_map.md`
  - [ ] `talking_points.md`
  - [ ] `action_plan.md`
  - [ ] `section_priority_table.md`
  - [ ] `staff_one_pager_p1.md`
  - [ ] `clear_ask_matrix_p1.md`

---

## 2. Contract Header Verification

**Check that ALL policy files (except README.md) have the contract header:**

- [ ] `key_findings.md` - Has HTML comment header with "READ-ONLY POLICY CONTEXT - DO NOT EXECUTE"
- [ ] `stakeholder_map.md` - Has HTML comment header
- [ ] `talking_points.md` - Has HTML comment header
- [ ] `action_plan.md` - Has HTML comment header
- [ ] `section_priority_table.md` - Has HTML comment header
- [ ] `staff_one_pager_p1.md` - Has HTML comment header
- [ ] `clear_ask_matrix_p1.md` - Has HTML comment header

**Header should include:**
- [ ] "READ-ONLY POLICY CONTEXT - DO NOT EXECUTE" statement
- [ ] Reference to system contract
- [ ] "What this document represents" section
- [ ] "What this document is NOT" section
- [ ] Violation warning

---

## 3. README.md Verification

- [ ] **Location statement** - Correctly identifies directory location
- [ ] **Contract section** - Explains READ-ONLY POLICY CONTEXT
- [ ] **Canonical artifacts list** - All 7 policy files documented
- [ ] **Source location** - Correctly references `wi_charge_scenario/`
- [ ] **Usage rules** - ✅ ALLOWED USES section present
- [ ] **Usage rules** - 🚫 STRICT PROHIBITIONS section present
- [ ] **Interpretation rules** - Explains how to interpret action language
- [ ] **Future agent safety rule** - Documents requirements for agents
- [ ] **Default behavior** - DO NOTHING / ASK / ASSUME READ-ONLY

---

## 4. File Content Verification

### key_findings.md
- [ ] Contains executive summary
- [ ] Contains policy opportunities
- [ ] Contains risks & uncertainties
- [ ] Source location noted at bottom
- [ ] No executable instructions

### stakeholder_map.md
- [ ] Three execution paths documented
- [ ] Institutional stakeholders only (no individual names)
- [ ] Engagement priority tiers
- [ ] Source location noted at bottom
- [ ] No executable instructions

### talking_points.md
- [ ] Authority → Action → Outcome format
- [ ] P1 sections only
- [ ] Source location noted at bottom
- [ ] No executable instructions

### action_plan.md
- [ ] 90-day execution roadmap
- [ ] Three execution paths detailed
- [ ] Section deep dives
- [ ] Source location noted at bottom
- [ ] No executable instructions

### section_priority_table.md
- [ ] Section mapping table
- [ ] Authority type definitions
- [ ] Engagement type definitions
- [ ] Source location noted at bottom
- [ ] No executable instructions

### staff_one_pager_p1.md
- [ ] Problem statement
- [ ] Existing authority (P1 sections)
- [ ] FY26 execution opportunities
- [ ] Source location noted at bottom
- [ ] No executable instructions

### clear_ask_matrix_p1.md
- [ ] Ask matrix table
- [ ] Authority lever definitions
- [ ] Proof requirements
- [ ] Source location noted at bottom
- [ ] No executable instructions

---

## 5. Original Files Preservation

- [ ] **Original files still exist** in `artifacts/wi_charge_scenario/`:
  - [ ] `KEY_FINDINGS_REPORT.md`
  - [ ] `STAKEHOLDER_MAP.md`
  - [ ] `TALKING_POINTS_BY_PATH.md`
  - [ ] `POLICY_ACTION_PLAN.md`
  - [ ] `SECTION_PRIORITY_TABLE.md`
  - [ ] `STAFF_ONE_PAGER_P1.md`
  - [ ] `CLEAR_ASK_MATRIX_P1.md`

**Note:** Files were copied, not moved. Originals should be preserved.

---

## 6. Naming Convention Verification

- [ ] All filenames use lowercase with underscores
- [ ] No spaces in filenames
- [ ] No special characters (except underscores and dots)
- [ ] File extensions are `.md`

**Canonical naming pattern:** `{descriptive_name}.md`

---

## 7. Contract Compliance Check

**Verify that policy files do NOT contain:**
- [ ] Executable code blocks
- [ ] Agent task definitions
- [ ] Automated workflow triggers
- [ ] Direct execution instructions
- [ ] State advancement commands

**Verify that policy files DO contain:**
- [ ] Strategic context
- [ ] Human-facing guidance
- [ ] Analysis and recommendations
- [ ] Non-operational planning

---

## 8. Integration Points

**Check if any other files reference policy artifacts:**

- [ ] Search for references to `artifacts/policy/` in codebase
- [ ] Check if agents need updates to respect contract
- [ ] Verify no hardcoded paths to old `wi_charge_scenario/` location
- [ ] Check if documentation needs updates

---

## 9. Testing Recommendations

**After review, test that:**

- [ ] Agents can READ policy files without errors
- [ ] Agents do NOT attempt to MODIFY policy files
- [ ] Agents do NOT treat policy files as executable
- [ ] Contract headers are visible in rendered markdown
- [ ] README is accessible and clear

---

## 10. Issues Found

**Document any issues discovered:**

1. _________________________________________________
2. _________________________________________________
3. _________________________________________________

---

## Review Sign-Off

**Review Status:** ⬜ Approved | ⬜ Needs Revision | ⬜ Rejected

**Reviewer Notes:**

_________________________________________________
_________________________________________________
_________________________________________________

**Date:** _______________  
**Signature:** _______________

---

**End of Review Checklist**

*Generated: January 7, 2026*
