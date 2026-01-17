# Staffer Artifact Sophistication Implementation Plan

**Date:** 2026-01-20  
**Status:** Planning Document  
**Purpose:** Bridge gap from current placeholder artifacts to staffer-ready, actionable documents

---

## Executive Summary

**Current State:** ~20% sophistication  
**Target State:** 90% sophistication (staffer-ready)  
**Implementation:** 3 phases over 6-8 weeks

This plan outlines specific technical steps to transform basic structural artifacts into sophisticated, actionable documents that staffers can use at key legislative moments.

---

## Phase 1: Foundation Layer (Weeks 1-2)

**Goal:** Upgrade from placeholder content to basic staffer-ready artifacts

### 1.1 Enhanced Bill Text Parser

**Current State:**
- Basic keyword matching (`scripts/analyze_wi_charge_scenario.py`)
- Simple section extraction (regex-based)
- Limited context understanding

**Required Capabilities:**
- Deep section parsing with hierarchy (Division → Title → Section → Subsection)
- Authority citation extraction (statutes, regulations, prior bills)
- Provision type classification (authorization, appropriation, directive, etc.)
- Cross-reference resolution (internal bill references)

**Implementation:**

```python
# New agent: intel_bill_parser_pre_evt.py
# Location: agent-orchestrator/agents/intel_bill_parser_pre_evt.py

"""
Intelligence Agent: Bill Parser (PRE_EVT)
Class: Intelligence (Read-Only)
Purpose: Deep parse bill text into structured, queryable format
"""

# Key functions:
- parse_bill_structure(pdf_path) -> Dict[str, Any]
  # Returns: divisions, titles, sections, subsections with full hierarchy
  
- extract_authority_citations(text) -> List[Dict[str, Any]]
  # Returns: [{type: "statute", citation: "10 USC 1234", context: "..."}]
  
- classify_provision_type(section_text) -> str
  # Returns: "authorization" | "appropriation" | "directive" | "reporting" | etc.
  
- resolve_cross_references(section_text, bill_structure) -> List[Dict[str, Any]]
  # Returns: [{reference: "Section 2101", resolved_to: {...}, context: "..."}]
```

**Dependencies:**
- Existing: `pdfplumber`, `PyPDF2` (already in requirements.txt)
- New: `spacy` or `nltk` for NLP (add to requirements.txt)
- New: `regex` patterns for citation extraction

**Output Artifact:**
- `BILL_STRUCTURE.json` - Full bill hierarchy with metadata
- `AUTHORITY_CITATIONS.json` - Extracted statutory/regulatory references
- `PROVISION_CLASSIFICATION.json` - Type classification per section

---

### 1.2 Committee Member Intelligence Database

**Current State:**
- Basic committee schema exists (`data/committees/COMMITTEE_DATA_SCHEMA.md`)
- Member data structure defined but not populated
- No voting history integration

**Required Capabilities:**
- Populate member database from public sources (Congress.gov API, ProPublica)
- Committee assignment tracking
- Basic voting history (last 2-3 Congresses)
- District/state profile data

**Implementation:**

```python
# New agent: intel_member_database_builder_pre_evt.py
# Location: agent-orchestrator/agents/intel_member_database_builder_pre_evt.py

"""
Intelligence Agent: Member Database Builder (PRE_EVT)
Class: Intelligence (Read-Only)
Purpose: Build and maintain member intelligence database
"""

# Key functions:
- fetch_member_data(congress: int) -> List[Dict[str, Any]]
  # Source: Congress.gov API or ProPublica API
  # Returns: Member profiles with committee assignments
  
- fetch_voting_history(member_id: str, congress: int) -> List[Dict[str, Any]]
  # Source: ProPublica Congress API
  # Returns: Recent votes with bill topics
  
- build_member_profiles() -> Dict[str, Any]
  # Aggregates: Member data + voting history + committee assignments
```

**Data Sources:**
- Congress.gov API (free, rate-limited)
- ProPublica Congress API (free, requires API key)
- Manual data entry for staff contacts (if available)

**Output Artifact:**
- `MEMBER_DATABASE.json` - Complete member profiles
- `COMMITTEE_MEMBERSHIPS.json` - Current committee assignments
- `VOTING_HISTORY_SUMMARY.json` - Aggregated voting patterns

**Storage:**
- `agent-orchestrator/data/members/` directory
- Versioned snapshots: `members__snapshot__YYYYMMDD_HHMMSS.json`

---

### 1.3 Enhanced Committee Briefing Packet Agent

**Current State:**
- `draft_committee_briefing_comm_evt.py` generates placeholder content
- Basic structure but no deep integration

**Required Enhancements:**
- Integrate bill parser output
- Integrate member database
- Generate member-specific talking points
- Include authority citations

**Implementation:**

```python
# Enhance: agent-orchestrator/agents/draft_committee_briefing_comm_evt.py

# New inputs:
- bill_structure: Dict[str, Any]  # From intel_bill_parser
- member_profiles: Dict[str, Any]  # From intel_member_database_builder
- authority_citations: List[Dict[str, Any]]  # From intel_bill_parser

# Enhanced outputs:
{
  "executive_summary": {
    "policy_proposal": "...",
    "key_sections": [
      {
        "section": "Sec. 2101",
        "title": "Army Construction",
        "authority": "10 USC 2801",
        "relevance": "High - Direct alignment with wireless power infrastructure"
      }
    ],
    "authority_foundation": [
      {
        "citation": "10 USC 2801",
        "description": "Authorizes military construction projects",
        "relevance": "Primary authority for infrastructure modernization"
      }
    ]
  },
  "member_specific_talking_points": [
    {
      "member_id": "S000123",
      "member_name": "Sen. Smith",
      "committee_role": "Chair",
      "talking_points": [
        {
          "point": "Wireless power reduces maintenance costs",
          "rationale": "Sen. Smith's district includes major defense facilities",
          "local_impact": "Fort XYZ maintenance costs $2M/year on battery replacement"
        }
      ],
      "prior_votes": [
        {
          "bill": "HR-4567",
          "topic": "Energy efficiency",
          "vote": "Yea",
          "relevance": "Similar energy efficiency provision"
        }
      ]
    }
  ]
}
```

**Review Gate:** HR_LANG (unchanged)

---

### 1.4 Staff One-Pager Generator

**Current State:**
- Example exists: `artifacts/policy/staff_one_pager_p1.md`
- Manual creation, not agent-generated

**Required:**
- Automated generation from bill analysis
- Authority citation integration
- Problem statement extraction
- Actionable asks with rationale

**Implementation:**

```python
# New agent: draft_staff_one_pager_comm_evt.py
# Location: agent-orchestrator/agents/draft_staff_one_pager_comm_evt.py

"""
Drafting Agent: Staff One-Pager (COMM_EVT)
Class: Drafting (Human-Gated)
Purpose: Generate concise, actionable one-pager for staffers
"""

# Key functions:
- extract_problem_statement(bill_analysis, policy_context) -> str
  # Synthesizes: Policy problem from bill + context
  
- identify_authority_sections(bill_structure, policy_goals) -> List[Dict[str, Any]]
  # Returns: Relevant sections with authority citations
  
- generate_actionable_asks(authority_sections, policy_goals) -> List[Dict[str, Any]]
  # Returns: Specific asks with rationale and authority
  
- format_one_pager(content) -> str
  # Returns: Markdown-formatted one-pager (max 1 page)
```

**Output Artifact:**
- `STAFF_ONE_PAGER.md` - Formatted markdown
- `STAFF_ONE_PAGER.json` - Structured data version

**Review Gate:** HR_LANG

---

## Phase 2: Intelligence Layer (Weeks 3-4)

**Goal:** Add temporal awareness, precedent analysis, and risk assessment

### 2.1 Legislative Calendar Intelligence

**Current State:**
- No temporal awareness
- No deadline tracking

**Required Capabilities:**
- Legislative calendar integration
- Amendment deadline tracking
- Vote scheduling windows
- Urgency signal detection

**Implementation:**

```python
# New agent: intel_legislative_calendar_comm_evt.py
# Location: agent-orchestrator/agents/intel_legislative_calendar_comm_evt.py

"""
Intelligence Agent: Legislative Calendar (COMM_EVT)
Class: Intelligence (Read-Only)
Purpose: Track legislative calendar and identify timing windows
"""

# Key functions:
- fetch_committee_schedule(committee_id: str) -> Dict[str, Any]
  # Source: Committee websites or Congress.gov
  # Returns: Upcoming hearings, markups, votes
  
- identify_amendment_deadlines(bill_id: str) -> List[Dict[str, Any]]
  # Returns: Amendment submission deadlines with urgency signals
  
- detect_timing_windows(committee_schedule, bill_status) -> Dict[str, Any]
  # Returns: Optimal timing windows for action
  
- assess_urgency(bill_status, calendar) -> str
  # Returns: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"
```

**Data Sources:**
- Committee websites (scraping or RSS feeds)
- Congress.gov calendar API
- Manual calendar entry (if needed)

**Output Artifact:**
- `LEGISLATIVE_CALENDAR.json` - Committee schedules
- `TIMING_WINDOWS.json` - Optimal action windows
- `URGENCY_ASSESSMENT.json` - Urgency signals

---

### 2.2 Policy Precedent Database

**Current State:**
- No precedent tracking
- No similar provision analysis

**Required Capabilities:**
- Similar provision identification
- Implementation example tracking
- Opposition pattern recognition
- Success/failure analysis

**Implementation:**

```python
# New agent: intel_precedent_analyzer_comm_evt.py
# Location: agent-orchestrator/agents/intel_precedent_analyzer_comm_evt.py

"""
Intelligence Agent: Precedent Analyzer (COMM_EVT)
Class: Intelligence (Read-Only)
Purpose: Identify similar provisions and learn from past implementations
"""

# Key functions:
- find_similar_provisions(bill_section: Dict[str, Any]) -> List[Dict[str, Any]]
  # Searches: Past bills with similar language/purpose
  # Returns: Similar provisions with outcomes
  
- analyze_implementation_examples(provision_type: str) -> List[Dict[str, Any]]
  # Returns: How similar provisions were implemented
  
- identify_opposition_patterns(similar_provisions) -> Dict[str, Any]
  # Returns: Common opposition arguments and responses
  
- assess_success_indicators(provision_outcomes) -> Dict[str, Any]
  # Returns: What made similar provisions successful
```

**Data Sources:**
- Congress.gov bill text database
- CRS reports (Congressional Research Service)
- Manual precedent entry (curated examples)

**Output Artifact:**
- `PRECEDENT_ANALYSIS.json` - Similar provisions with outcomes
- `IMPLEMENTATION_EXAMPLES.json` - How similar provisions worked
- `OPPOSITION_PATTERNS.json` - Common objections and responses

---

### 2.3 Risk Assessment Framework

**Current State:**
- Basic risk lists in artifacts
- No structured risk analysis

**Required Capabilities:**
- Structured risk identification
- Opposition likelihood assessment
- Mitigation strategy generation
- Risk prioritization

**Implementation:**

```python
# New agent: intel_risk_assessor_comm_evt.py
# Location: agent-orchestrator/agents/intel_risk_assessor_comm_evt.py

"""
Intelligence Agent: Risk Assessor (COMM_EVT)
Class: Intelligence (Read-Only)
Purpose: Assess risks and opposition likelihood
"""

# Key functions:
- identify_risks(bill_analysis, stakeholder_map) -> List[Dict[str, Any]]
  # Returns: Structured risk list with likelihood
  
- assess_opposition_likelihood(member_profiles, bill_content) -> Dict[str, Any]
  # Returns: Opposition probability per member/group
  
- generate_mitigation_strategies(risks) -> List[Dict[str, Any]]
  # Returns: Mitigation strategies for each risk
  
- prioritize_risks(risks, mitigation_strategies) -> List[Dict[str, Any]]
  # Returns: Prioritized risk list
```

**Output Artifact:**
- `RISK_ASSESSMENT.json` - Structured risk analysis
- `OPPOSITION_LIKELIHOOD.json` - Member/group opposition probabilities
- `MITIGATION_STRATEGIES.json` - Risk mitigation plans

---

### 2.4 Enhanced Member Intelligence

**Current State:**
- Basic member profiles
- Limited voting history

**Required Enhancements:**
- Deep voting pattern analysis
- Issue area expertise identification
- Relationship mapping (allies, opponents)
- Communication preferences

**Implementation:**

```python
# Enhance: intel_member_database_builder_pre_evt.py

# New analysis functions:
- analyze_voting_patterns(member_id: str) -> Dict[str, Any]
  # Returns: Voting patterns by issue area, party alignment, etc.
  
- identify_issue_expertise(member_id: str, voting_history) -> List[str]
  # Returns: Issue areas where member is active/expert
  
- map_relationships(member_id: str, voting_history, cosponsorships) -> Dict[str, Any]
  # Returns: Frequent allies, opponents, swing relationships
  
- extract_communication_preferences(member_id: str, public_statements) -> Dict[str, Any]
  # Returns: Preferred messaging themes, framing approaches
```

**Output Artifact:**
- `MEMBER_INTELLIGENCE_DEEP.json` - Enhanced member profiles
- `VOTING_PATTERNS.json` - Detailed voting analysis
- `RELATIONSHIP_MAP.json` - Member relationship network

---

## Phase 3: Advanced Sophistication (Weeks 5-6)

**Goal:** Deep policy analysis, member-specific customization, predictive timing

### 3.1 Deep Policy Analysis Engine

**Current State:**
- Basic policy context extraction
- Limited impact analysis

**Required Capabilities:**
- Policy mechanism analysis
- Impact quantification (where possible)
- Implementation pathway mapping
- Regulatory coordination requirements

**Implementation:**

```python
# New agent: intel_policy_analyzer_comm_evt.py
# Location: agent-orchestrator/agents/intel_policy_analyzer_comm_evt.py

"""
Intelligence Agent: Policy Analyzer (COMM_EVT)
Class: Intelligence (Read-Only)
Purpose: Deep analysis of policy mechanisms and impacts
"""

# Key functions:
- analyze_policy_mechanisms(bill_sections) -> Dict[str, Any]
  # Returns: How policy would work (authorization, appropriation, directive)
  
- quantify_impacts(provisions, similar_precedents) -> Dict[str, Any]
  # Returns: Estimated impacts (costs, benefits, affected entities)
  
- map_implementation_pathway(provisions) -> Dict[str, Any]
  # Returns: Implementation steps, timelines, responsible agencies
  
- identify_regulatory_coordination(provisions) -> List[Dict[str, Any]]
  # Returns: Required agency coordination, rulemaking needs
```

**Output Artifact:**
- `POLICY_MECHANISM_ANALYSIS.json` - How policy works
- `IMPACT_QUANTIFICATION.json` - Estimated impacts
- `IMPLEMENTATION_PATHWAY.json` - How to implement
- `REGULATORY_COORDINATION.json` - Agency coordination needs

---

### 3.2 Member-Specific Customization Engine

**Current State:**
- Generic talking points
- Limited member customization

**Required Capabilities:**
- Member-specific talking point generation
- District/state impact customization
- Relationship-aware messaging
- Communication style adaptation

**Implementation:**

```python
# New agent: draft_member_specific_comms_comm_evt.py
# Location: agent-orchestrator/agents/draft_member_specific_comms_comm_evt.py

"""
Drafting Agent: Member-Specific Communications (COMM_EVT)
Class: Drafting (Human-Gated)
Purpose: Generate customized communications per member
"""

# Key functions:
- generate_member_talking_points(member_id: str, bill_analysis, member_intelligence) -> List[Dict[str, Any]]
  # Returns: Customized talking points based on member profile
  
- customize_district_impact(member_id: str, bill_analysis) -> Dict[str, Any]
  # Returns: Local impact analysis for member's district/state
  
- adapt_communication_style(member_id: str, message: str, member_intelligence) -> str
  # Returns: Message adapted to member's communication preferences
  
- generate_relationship_context(member_id: str, relationship_map) -> Dict[str, Any]
  # Returns: Context about member's relationships (allies, opponents)
```

**Output Artifact:**
- `MEMBER_SPECIFIC_COMMS.json` - Customized communications per member
- `DISTRICT_IMPACTS.json` - Local impact analysis
- `COMMUNICATION_STYLE_GUIDE.json` - Member-specific messaging guidance

**Review Gate:** HR_MSG

---

### 3.3 Predictive Timing Models

**Current State:**
- No predictive capabilities
- Reactive only

**Required Capabilities:**
- Vote timing prediction
- Amendment window prediction
- Committee action forecasting
- Optimal engagement timing

**Implementation:**

```python
# New agent: intel_timing_predictor_comm_evt.py
# Location: agent-orchestrator/agents/intel_timing_predictor_comm_evt.py

"""
Intelligence Agent: Timing Predictor (COMM_EVT)
Class: Intelligence (Read-Only)
Purpose: Predict optimal timing for actions
"""

# Key functions:
- predict_vote_timing(bill_status, committee_schedule, historical_patterns) -> Dict[str, Any]
  # Returns: Predicted vote dates with confidence intervals
  
- predict_amendment_windows(bill_status, committee_schedule) -> List[Dict[str, Any]]
  # Returns: Optimal amendment submission windows
  
- forecast_committee_actions(committee_id: str, bill_status) -> Dict[str, Any]
  # Returns: Predicted committee actions (hearings, markups, votes)
  
- identify_optimal_engagement_timing(member_id: str, bill_status, calendar) -> Dict[str, Any]
  # Returns: Best times to engage specific members
```

**Output Artifact:**
- `TIMING_PREDICTIONS.json` - Predicted timing windows
- `OPTIMAL_ENGAGEMENT_WINDOWS.json` - Best times to engage
- `FORECASTED_ACTIONS.json` - Predicted committee actions

---

### 3.4 Advanced Communication Templates

**Current State:**
- Basic templates
- Limited sophistication

**Required Enhancements:**
- Multiple template types (one-pager, briefing memo, email, talking points)
- Context-aware template selection
- Dynamic content insertion
- Format optimization (PDF, Markdown, HTML)

**Implementation:**

```python
# New library: agent-orchestrator/lib/communication_templates.py

# Template types:
- STAFF_ONE_PAGER
- BRIEFING_MEMO
- EMAIL_OUTREACH
- TALKING_POINTS
- AMENDMENT_EXPLANATION

# Key functions:
- select_template(context: Dict[str, Any]) -> str
  # Returns: Best template type for context
  
- populate_template(template_type: str, content: Dict[str, Any]) -> str
  # Returns: Populated template with content
  
- format_output(content: str, format_type: str) -> bytes
  # Returns: Formatted output (PDF, Markdown, HTML)
```

**Output Artifact:**
- Multiple formatted outputs per artifact type
- Template library with examples

---

## Implementation Roadmap

### Week 1-2: Phase 1 Foundation
- [ ] Build `intel_bill_parser_pre_evt.py`
- [ ] Build `intel_member_database_builder_pre_evt.py`
- [ ] Enhance `draft_committee_briefing_comm_evt.py`
- [ ] Build `draft_staff_one_pager_comm_evt.py`
- [ ] Test with sample bill (S.2296)

### Week 3-4: Phase 2 Intelligence
- [ ] Build `intel_legislative_calendar_comm_evt.py`
- [ ] Build `intel_precedent_analyzer_comm_evt.py`
- [ ] Build `intel_risk_assessor_comm_evt.py`
- [ ] Enhance `intel_member_database_builder_pre_evt.py` with deep analysis
- [ ] Integrate all intelligence into briefing packets

### Week 5-6: Phase 3 Advanced
- [ ] Build `intel_policy_analyzer_comm_evt.py`
- [ ] Build `draft_member_specific_comms_comm_evt.py`
- [ ] Build `intel_timing_predictor_comm_evt.py`
- [ ] Build `lib/communication_templates.py`
- [ ] End-to-end testing with full workflow

### Week 7-8: Integration & Refinement
- [ ] Integrate all agents into workflow
- [ ] Performance optimization
- [ ] Documentation
- [ ] User testing with real staffers
- [ ] Refinement based on feedback

---

## Dependencies & Requirements

### New Python Packages
```txt
# Add to requirements.txt:
spacy>=3.7.0
nltk>=3.8.0
requests>=2.31.0  # Already present
beautifulsoup4>=4.12.0  # For web scraping
python-dateutil>=2.8.0  # For date parsing
pandas>=2.0.0  # For data analysis
```

### External APIs
- Congress.gov API (free, rate-limited)
- ProPublica Congress API (free, requires API key)
- Committee websites (scraping or RSS)

### Data Storage
- `agent-orchestrator/data/bills/` - Bill text and analysis
- `agent-orchestrator/data/members/` - Member database
- `agent-orchestrator/data/precedents/` - Precedent database
- `agent-orchestrator/data/calendar/` - Legislative calendar

---

## Success Metrics

### Phase 1 Success Criteria
- [ ] Bill parser extracts 90%+ of sections correctly
- [ ] Member database has 100% of current Congress members
- [ ] Briefing packets include authority citations
- [ ] One-pagers are under 1 page and actionable

### Phase 2 Success Criteria
- [ ] Calendar intelligence identifies 80%+ of relevant deadlines
- [ ] Precedent analyzer finds 5+ similar provisions per section
- [ ] Risk assessor identifies top 3 risks per bill
- [ ] Member intelligence includes voting patterns

### Phase 3 Success Criteria
- [ ] Policy analyzer explains mechanisms for 90%+ of provisions
- [ ] Member-specific comms customized for 10+ members
- [ ] Timing predictor accuracy within 1 week for 70%+ of votes
- [ ] Staffer feedback: "Ready to use" on 80%+ of artifacts

---

## Risk Mitigation

### Technical Risks
- **API Rate Limits:** Implement caching and request throttling
- **Data Quality:** Manual validation checkpoints
- **Performance:** Optimize for large bills (1000+ pages)

### Operational Risks
- **Staffer Adoption:** Early user testing and feedback loops
- **Maintenance Burden:** Automated data refresh where possible
- **Accuracy:** Human review gates remain mandatory

---

## Next Steps

1. **Review this plan** with stakeholders
2. **Prioritize phases** based on immediate needs
3. **Set up development environment** (APIs, data directories)
4. **Begin Phase 1** with bill parser agent
5. **Establish feedback loop** with staffers early

---

**Last Updated:** 2026-01-20  
**Version:** 1.0.0  
**Status:** Ready for Implementation
