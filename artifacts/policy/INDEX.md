# Policy Artifacts Index

**Complete index of all policy artifacts and their relationships**

---

## 📚 Document Index

### Primary Documents (Read These First)

1. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** ⭐ START HERE
   - Quick navigation guide
   - Common use cases
   - File reference

2. **[key_findings.md](key_findings.md)**
   - Executive summary
   - Policy opportunities
   - Risks & uncertainties
   - Metrics summary

3. **[action_plan.md](action_plan.md)**
   - 90-day execution roadmap
   - Three execution paths
   - Section deep dives
   - Engagement strategies

### Engagement Documents

4. **[stakeholder_map.md](stakeholder_map.md)**
   - Institutional stakeholders
   - Three execution paths
   - Engagement priority tiers
   - Stakeholder engagement matrix

5. **[talking_points.md](talking_points.md)**
   - Structured talking points
   - Authority → Action → Outcome
   - P1 sections only
   - Cross-cutting points

6. **[clear_ask_matrix_p1.md](clear_ask_matrix_p1.md)**
   - Structured asks
   - Target offices
   - Authority levers
   - Proof requirements

### Reference Documents

7. **[section_priority_table.md](section_priority_table.md)**
   - Section mapping table
   - Priority rankings
   - Authority type definitions
   - Engagement type definitions

8. **[staff_one_pager_p1.md](staff_one_pager_p1.md)**
   - One-page brief
   - Problem statement
   - Existing authority
   - FY26 execution opportunities

### Supporting Documents

9. **[README.md](README.md)**
   - System contract
   - Usage rules
   - Prohibitions
   - Future agent safety rules

10. **[REVIEW_CHECKLIST.md](REVIEW_CHECKLIST.md)**
    - Validation checklist
    - Review process
    - Sign-off template

11. **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)**
    - Implementation details
    - Files created
    - Validation results

12. **[INDEX.md](INDEX.md)** (this file)
    - Complete index
    - Document relationships
    - Navigation guide

---

## 🗺️ Visual Diagrams Index

### Merged/Comprehensive Diagrams

1. **[comprehensive_overview.mmd](diagrams/comprehensive_overview.mmd)** ⭐ RECOMMENDED
   - Complete policy plan
   - All paths + timelines + stakeholders
   - Best starting point

2. **[master_dashboard.mmd](diagrams/master_dashboard.mmd)**
   - Executive dashboard
   - High-level overview
   - Quick reference

3. **[section_to_ask_flow.mmd](diagrams/section_to_ask_flow.mmd)**
   - Complete engagement flow
   - Sections → Paths → Asks → Targets

### Detailed Diagrams

4. **[stakeholder_hierarchy.mmd](diagrams/stakeholder_hierarchy.mmd)**
   - Stakeholder structure
   - Organizational hierarchy

5. **[90_day_timeline.mmd](diagrams/90_day_timeline.mmd)**
   - Gantt chart timeline
   - All three paths parallel

6. **[execution_paths_flowchart.mmd](diagrams/execution_paths_flowchart.mmd)**
   - Path selection
   - Phase progression

7. **[section_priority_map.mmd](diagrams/section_priority_map.mmd)**
   - Section priorities
   - Actionability scores

8. **[clear_ask_decision_tree.mmd](diagrams/clear_ask_decision_tree.mmd)**
   - Ask decision tree
   - Path → Ask → Target

**See:** [diagrams/README.md](diagrams/README.md) for usage guide

---

## 🔗 Document Relationships

### Reading Order

**For First-Time Review:**
```
QUICK_REFERENCE.md
  ↓
key_findings.md
  ↓
diagrams/master_dashboard.mmd
  ↓
action_plan.md (skim)
  ↓
stakeholder_map.md
```

**For Engagement Planning:**
```
stakeholder_map.md
  ↓
clear_ask_matrix_p1.md
  ↓
talking_points.md
  ↓
diagrams/section_to_ask_flow.mmd
```

**For Detailed Analysis:**
```
action_plan.md
  ↓
section_priority_table.md
  ↓
diagrams/comprehensive_overview.mmd
```

### Cross-References

**key_findings.md** references:
- → `action_plan.md` (execution paths)
- → `stakeholder_map.md` (stakeholders)

**action_plan.md** references:
- → `stakeholder_map.md` (stakeholder sections)
- → `section_priority_table.md` (section mapping)

**clear_ask_matrix_p1.md** references:
- → `action_plan.md` (execution paths)
- → `stakeholder_map.md` (target offices)

**talking_points.md** references:
- → `action_plan.md` (sections)
- → `section_priority_table.md` (authority types)

---

## 📊 Content Matrix

| Document | Path 1 | Path 2 | Path 3 | Sections | Stakeholders | Timeline |
|----------|--------|--------|--------|----------|--------------|----------|
| key_findings.md | ✅ | ✅ | ✅ | ✅ | ⚠️ | ⚠️ |
| action_plan.md | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| stakeholder_map.md | ✅ | ✅ | ✅ | ⚠️ | ✅ | ❌ |
| talking_points.md | ✅ | ✅ | ✅ | ✅ | ⚠️ | ❌ |
| clear_ask_matrix_p1.md | ✅ | ✅ | ✅ | ⚠️ | ✅ | ❌ |
| section_priority_table.md | ✅ | ✅ | ✅ | ✅ | ⚠️ | ⚠️ |
| staff_one_pager_p1.md | ✅ | ✅ | ✅ | ✅ | ⚠️ | ⚠️ |

**Legend:** ✅ Full coverage | ⚠️ Partial coverage | ❌ Not covered

---

## 🎯 Use Case Matrix

| Use Case | Primary Document | Supporting Documents | Diagram |
|----------|-----------------|---------------------|---------|
| Executive Briefing | key_findings.md | staff_one_pager_p1.md | master_dashboard.mmd |
| Engagement Planning | stakeholder_map.md | clear_ask_matrix_p1.md, talking_points.md | section_to_ask_flow.mmd |
| Execution Planning | action_plan.md | section_priority_table.md | comprehensive_overview.mmd |
| Section Analysis | section_priority_table.md | action_plan.md | section_priority_map.mmd |
| Timeline Planning | action_plan.md | (none) | 90_day_timeline.mmd |
| Stakeholder Analysis | stakeholder_map.md | (none) | stakeholder_hierarchy.mmd |

---

## 📁 File Structure

```
artifacts/policy/
├── README.md                    # Contract documentation
├── QUICK_REFERENCE.md          # ⭐ Start here
├── INDEX.md                    # This file
├── key_findings.md             # Executive summary
├── stakeholder_map.md           # Stakeholders
├── talking_points.md           # Talking points
├── action_plan.md              # 90-day roadmap
├── section_priority_table.md   # Section mapping
├── staff_one_pager_p1.md       # One-page brief
├── clear_ask_matrix_p1.md      # Ask matrix
├── REVIEW_CHECKLIST.md         # Validation checklist
├── IMPLEMENTATION_SUMMARY.md   # Implementation details
└── diagrams/
    ├── README.md               # Diagram guide
    ├── comprehensive_overview.mmd    # ⭐ Complete view
    ├── master_dashboard.mmd          # Executive view
    ├── section_to_ask_flow.mmd       # Engagement flow
    ├── stakeholder_hierarchy.mmd     # Stakeholder structure
    ├── 90_day_timeline.mmd           # Timeline
    ├── execution_paths_flowchart.mmd # Path flow
    ├── section_priority_map.mmd     # Section priorities
    └── clear_ask_decision_tree.mmd   # Ask tree
```

---

## 🔍 Search Guide

### Find by Topic

**Bill Sections:**
- `section_priority_table.md` - Complete mapping
- `action_plan.md` - Section deep dives
- `talking_points.md` - Section-specific talking points

**Stakeholders:**
- `stakeholder_map.md` - Complete stakeholder list
- `clear_ask_matrix_p1.md` - Target offices
- `action_plan.md` - Engagement strategies

**Timeline:**
- `action_plan.md` - 90-day phases
- `diagrams/90_day_timeline.mmd` - Visual timeline
- `section_priority_table.md` - Priority timeframes

**Engagement:**
- `clear_ask_matrix_p1.md` - What to ask
- `talking_points.md` - How to frame
- `stakeholder_map.md` - Who to engage

---

## ✅ Validation Status

All policy artifacts are:
- ✅ Contract headers validated
- ✅ No executable content
- ✅ READ-ONLY POLICY CONTEXT compliant
- ✅ Diagrams created
- ✅ Documentation complete

**Last Validation:** January 7, 2026

---

**End of Index**

*For quick navigation, start with [QUICK_REFERENCE.md](QUICK_REFERENCE.md)*
