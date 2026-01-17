# Policy Artifacts Quick Reference Guide

**Last Updated:** January 7, 2026  
**Purpose:** Quick navigation guide for policy artifacts

---

## 🚀 Start Here

### For Executive Overview
1. **`key_findings.md`** - Executive summary (5 min read)
2. **`diagrams/master_dashboard.mmd`** - Visual overview
3. **`action_plan.md`** - 90-day roadmap (skim sections)

### For Engagement Planning
1. **`stakeholder_map.md`** - Who to engage
2. **`clear_ask_matrix_p1.md`** - What to ask
3. **`talking_points.md`** - How to frame it
4. **`diagrams/section_to_ask_flow.mmd`** - Complete flow visualization

### For Detailed Analysis
1. **`section_priority_table.md`** - Section mapping
2. **`action_plan.md`** - Full execution details
3. **`diagrams/comprehensive_overview.mmd`** - Complete visual

---

## 📊 Visual Diagrams Quick Guide

| Need | Use This Diagram |
|------|------------------|
| **Complete overview** | `comprehensive_overview.mmd` |
| **Executive summary** | `master_dashboard.mmd` |
| **Engagement flow** | `section_to_ask_flow.mmd` |
| **Stakeholder structure** | `stakeholder_hierarchy.mmd` |
| **Timeline planning** | `90_day_timeline.mmd` |
| **Path selection** | `execution_paths_flowchart.mmd` |
| **Section priorities** | `section_priority_map.mmd` |
| **Ask decision tree** | `clear_ask_decision_tree.mmd` |

**View diagrams:** Open `.mmd` files in [Mermaid Live Editor](https://mermaid.live)

---

## 📁 File Reference

### Core Policy Documents
- **`key_findings.md`** (12.8 KB) - Policy analysis summary
- **`stakeholder_map.md`** (14.7 KB) - Institutional stakeholders
- **`talking_points.md`** (4.3 KB) - Structured talking points
- **`action_plan.md`** (23.6 KB) - 90-day execution roadmap
- **`section_priority_table.md`** (10.6 KB) - Section mapping
- **`staff_one_pager_p1.md`** (4.7 KB) - One-page brief
- **`clear_ask_matrix_p1.md`** (4.0 KB) - Ask matrix

### Supporting Documents
- **`README.md`** - Contract documentation
- **`REVIEW_CHECKLIST.md`** - Validation checklist
- **`IMPLEMENTATION_SUMMARY.md`** - Implementation details
- **`QUICK_REFERENCE.md`** - This file

### Diagrams
- **`diagrams/`** - 8 mermaid diagrams (3 merged, 5 detailed)

---

## 🎯 Common Use Cases

### "I need to brief leadership"
1. Read: `key_findings.md` (executive summary)
2. View: `diagrams/master_dashboard.mmd`
3. Reference: `staff_one_pager_p1.md`

### "I need to plan engagement"
1. Read: `stakeholder_map.md` (who)
2. Read: `clear_ask_matrix_p1.md` (what)
3. Read: `talking_points.md` (how)
4. View: `diagrams/section_to_ask_flow.mmd`

### "I need to understand the plan"
1. Read: `action_plan.md` (full details)
2. View: `diagrams/comprehensive_overview.mmd`
3. Reference: `section_priority_table.md`

### "I need to prioritize sections"
1. Read: `section_priority_table.md`
2. View: `diagrams/section_priority_map.mmd`
3. Reference: `action_plan.md` (section deep dives)

---

## 🔍 Finding Information

### By Execution Path

**Path 1: Infrastructure**
- Sections: 2101, 2201, 2301, 2402
- Stakeholders: `stakeholder_map.md` → Path 1 section
- Timeline: `action_plan.md` → Execution Path 1
- Asks: `clear_ask_matrix_p1.md` → Infrastructure rows

**Path 2: R&D**
- Sections: 220A, 220
- Stakeholders: `stakeholder_map.md` → Path 2 section
- Timeline: `action_plan.md` → Execution Path 2
- Asks: `clear_ask_matrix_p1.md` → R&D rows

**Path 3: Energy**
- Sections: 2402, 314
- Stakeholders: `stakeholder_map.md` → Path 3 section
- Timeline: `action_plan.md` → Execution Path 3
- Asks: `clear_ask_matrix_p1.md` → Energy rows

### By Bill Section

**Priority 1 Sections (Days 1-30):**
- Sec. 2101, 2201, 2301, 2402, 314, 220A, 220
- See: `section_priority_table.md` → Priority 1
- See: `action_plan.md` → Section Deep Dives

**Priority 2 Sections (Days 31-60):**
- Sec. 1060, 227, 212, 322, Division C
- See: `section_priority_table.md` → Priority 2

---

## ⚡ Quick Actions

### Validate Policy Files
```bash
python scripts/validate_policy_contract.py
```

### View Diagrams
1. Open `.mmd` file
2. Copy content
3. Paste into [Mermaid Live Editor](https://mermaid.live)

### Find Stakeholders
1. Open `stakeholder_map.md`
2. Navigate to relevant execution path
3. See engagement priority tiers

### Find Talking Points
1. Open `talking_points.md`
2. Find execution path (A, B, or C)
3. Use Authority → Action → Outcome format

---

## 📋 Document Status

| Document | Status | Last Updated |
|----------|--------|--------------|
| Policy Artifacts | ✅ Complete | Jan 7, 2026 |
| Contract Headers | ✅ Validated | Jan 7, 2026 |
| Diagrams | ✅ Complete | Jan 7, 2026 |
| Validation Script | ✅ Working | Jan 7, 2026 |

---

## 🔗 Related Resources

- **Source Files:** `agent-orchestrator/artifacts/wi_charge_scenario/`
- **Validation Script:** `agent-orchestrator/scripts/validate_policy_contract.py`
- **System Contract:** See `README.md` → SYSTEM CONTRACT section

---

## ❓ Need Help?

1. **Contract Questions:** See `README.md`
2. **Review Process:** See `REVIEW_CHECKLIST.md`
3. **Implementation Details:** See `IMPLEMENTATION_SUMMARY.md`
4. **Diagram Usage:** See `diagrams/README.md`

---

**End of Quick Reference Guide**

*For detailed information, see individual document files.*
