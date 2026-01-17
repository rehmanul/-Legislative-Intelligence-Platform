# Staffer Artifact Sophistication - Quick Start Guide

**Purpose:** Bridge gap from placeholder artifacts to staffer-ready documents  
**Timeline:** 6-8 weeks across 3 phases  
**Current:** 20% sophistication → **Target:** 90% sophistication

---

## 🎯 The Goal

Transform basic structural artifacts into sophisticated, actionable documents that staffers can use at key legislative moments.

**Key Capabilities Needed:**
- ✅ Deep bill text analysis with authority citations
- ✅ Member-specific intelligence and customization
- ✅ Temporal awareness (deadlines, timing windows)
- ✅ Policy precedent analysis
- ✅ Risk assessment and mitigation
- ✅ Multiple communication formats

---

## 📋 Implementation Phases

### Phase 1: Foundation (Weeks 1-2)
**Goal:** Upgrade from placeholders to basic staffer-ready

**Agents to Build:**
1. `intel_bill_parser_pre_evt.py` - Deep bill parsing
2. `intel_member_database_builder_pre_evt.py` - Member intelligence
3. `draft_staff_one_pager_comm_evt.py` - One-pager generator

**Enhancements:**
- `draft_committee_briefing_comm_evt.py` - Add authority citations

**Key Deliverables:**
- Bill structure with authority citations
- Member database with voting history
- Enhanced briefing packets
- Automated one-pagers

---

### Phase 2: Intelligence (Weeks 3-4)
**Goal:** Add temporal awareness and precedent analysis

**Agents to Build:**
1. `intel_legislative_calendar_comm_evt.py` - Calendar tracking
2. `intel_precedent_analyzer_comm_evt.py` - Similar provisions
3. `intel_risk_assessor_comm_evt.py` - Risk analysis

**Enhancements:**
- `intel_member_database_builder_pre_evt.py` - Deep analysis

**Key Deliverables:**
- Legislative calendar integration
- Precedent database
- Risk assessment framework
- Enhanced member intelligence

---

### Phase 3: Advanced (Weeks 5-6)
**Goal:** Deep policy analysis and member customization

**Agents to Build:**
1. `intel_policy_analyzer_comm_evt.py` - Policy mechanisms
2. `draft_member_specific_comms_comm_evt.py` - Customized comms
3. `intel_timing_predictor_comm_evt.py` - Timing predictions

**Libraries:**
- `lib/communication_templates.py` - Template system

**Key Deliverables:**
- Deep policy analysis
- Member-specific communications
- Timing predictions
- Advanced templates

---

## 🚀 Getting Started

### Step 1: Set Up Environment

```bash
# Add new dependencies to requirements.txt
pip install spacy nltk beautifulsoup4 python-dateutil pandas

# Set up data directories
mkdir -p agent-orchestrator/data/{bills,members,precedents,calendar}
```

### Step 2: Get API Access

- **Congress.gov API:** Free, rate-limited (no key needed)
- **ProPublica Congress API:** Free, requires API key (sign up at propublica.org)
- **Committee Websites:** Scraping or RSS feeds

### Step 3: Start with Phase 1

**First Agent to Build:** `intel_bill_parser_pre_evt.py`

**Why Start Here:**
- Foundation for all other agents
- Can test immediately with sample bill
- Provides structured data for downstream agents

**Key Functions:**
```python
parse_bill_structure(pdf_path) -> Dict[str, Any]
extract_authority_citations(text) -> List[Dict[str, Any]]
classify_provision_type(section_text) -> str
resolve_cross_references(section_text, bill_structure) -> List[Dict[str, Any]]
```

---

## 📊 Current vs. Target Comparison

| Capability | Current | Phase 1 | Phase 2 | Phase 3 |
|------------|---------|---------|---------|---------|
| **Bill Parsing** | Keyword matching | Section hierarchy + citations | Precedent integration | Deep analysis |
| **Member Data** | Schema only | Voting history | Deep patterns | Customization |
| **Temporal Awareness** | None | Basic | Calendar integration | Predictions |
| **Policy Analysis** | Basic | Authority citations | Precedents | Mechanisms |
| **Communication** | Generic | One-pagers | Risk-aware | Member-specific |
| **Sophistication** | 20% | 50% | 75% | 90% |

---

## 🎯 Success Criteria

### Phase 1 Complete When:
- [ ] Bill parser extracts 90%+ of sections correctly
- [ ] Member database has 100% of current Congress
- [ ] Briefing packets include authority citations
- [ ] One-pagers are under 1 page and actionable

### Phase 2 Complete When:
- [ ] Calendar identifies 80%+ of relevant deadlines
- [ ] Precedent analyzer finds 5+ similar provisions
- [ ] Risk assessor identifies top 3 risks
- [ ] Member intelligence includes voting patterns

### Phase 3 Complete When:
- [ ] Policy analyzer explains 90%+ of mechanisms
- [ ] Member-specific comms for 10+ members
- [ ] Timing predictor accuracy within 1 week (70%+)
- [ ] Staffer feedback: "Ready to use" (80%+)

---

## 📁 File Locations

### Planning Documents
- `planning/STAFFER_ARTIFACT_SOPHISTICATION_PLAN.md` - Full plan
- `planning/STAFFER_ARTIFACT_ARCHITECTURE.mmd` - Visual diagram
- `planning/STAFFER_ARTIFACT_QUICK_START.md` - This file

### Agents (to be created)
- `agents/intel_bill_parser_pre_evt.py`
- `agents/intel_member_database_builder_pre_evt.py`
- `agents/draft_staff_one_pager_comm_evt.py`
- `agents/intel_legislative_calendar_comm_evt.py`
- `agents/intel_precedent_analyzer_comm_evt.py`
- `agents/intel_risk_assessor_comm_evt.py`
- `agents/intel_policy_analyzer_comm_evt.py`
- `agents/draft_member_specific_comms_comm_evt.py`
- `agents/intel_timing_predictor_comm_evt.py`

### Data Directories
- `data/bills/` - Bill text and analysis
- `data/members/` - Member database
- `data/precedents/` - Precedent database
- `data/calendar/` - Legislative calendar

### Libraries
- `lib/communication_templates.py` - Template system

---

## 🔗 Key Dependencies

### Existing Systems
- Agent orchestrator framework
- Artifact schema system
- Review gate system (HR_LANG, HR_MSG, etc.)
- Audit logging

### New Dependencies
- `spacy` - NLP for text analysis
- `nltk` - Natural language processing
- `beautifulsoup4` - Web scraping
- `python-dateutil` - Date parsing
- `pandas` - Data analysis

### External APIs
- Congress.gov API
- ProPublica Congress API
- Committee websites

---

## ⚠️ Important Notes

1. **Human Review Gates Remain:** All drafting agents still require human approval (HR_LANG, HR_MSG)

2. **Speculative by Default:** All artifacts start as SPECULATIVE until human approval

3. **Data Quality:** Manual validation checkpoints required for accuracy

4. **Performance:** Optimize for large bills (1000+ pages)

5. **Maintenance:** Automated data refresh where possible

---

## 📞 Next Steps

1. **Review full plan:** `STAFFER_ARTIFACT_SOPHISTICATION_PLAN.md`
2. **View architecture:** `STAFFER_ARTIFACT_ARCHITECTURE.mmd`
3. **Set up environment:** Install dependencies, create directories
4. **Start Phase 1:** Build `intel_bill_parser_pre_evt.py`
5. **Test with sample:** Use S.2296 (NDAA FY2026) as test case

---

**Last Updated:** 2026-01-20  
**Version:** 1.0.0
