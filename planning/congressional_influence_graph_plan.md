# Congressional Influence Graph & Power Modeling — Planning Document

**Planning Agent:** Congressional Graph & Power Modeling  
**Date:** 2026-01-20  
**Status:** Planning Phase (No Implementation)  
**Authority:** Planning Document — Authorizes Implementation

---

## Executive Summary

This document defines the design for modeling Congress, staff, industry, nonprofits, and trade associations as a **living influence graph** within the existing Agent Orchestrator system. The graph will enable machine-readable power analysis, relationship querying, and contextual influence modeling that adapts to legislative state transitions.

**Key Design Principles:**
- **First-class staff nodes** (already implemented)
- **Contextual power** (varies by legislative state)
- **Temporal edges** (power decays, transfers, activates)
- **Multi-axis power semantics** (procedural, temporal, informational, memory, retaliation)
- **Compatibility** with existing artifact schemas, review gates, and audit logging

---

## 1. Node Taxonomy

### 1.1 Core Congressional Nodes

#### Member (Existing)
- **Entity Type:** `member`
- **Entity ID Format:** `bioguide_id` (e.g., `S000123`)
- **Power Characteristics:**
  - Formal voting authority
  - Committee membership roles (chair, ranking member, member)
  - Leadership positions (Speaker, Majority Leader, etc.)
  - Term-limited (2 or 6 years)
- **Existing Schema:** `data/committees/COMMITTEE_DATA_SCHEMA.md`
- **Power Indicators:**
  - Committee role (chair > ranking > member)
  - Leadership position
  - Seniority (years in office)
  - Party alignment with majority

#### Staff (First-Class — Already Implemented)
- **Entity Type:** `staff`
- **Entity ID Format:** `uuid` (e.g., `550e8400-e29b-41d4-a716-446655440000`)
- **Entity Classes:**
  - `committee_staff` — Committee professional staff
  - `subcommittee_staff` — Subcommittee professional staff
  - `leadership_staff` — Leadership office staff (Speaker, Majority Leader, etc.)
  - `personal_office_staff` — Member personal office staff
  - `agency_liaison` — Executive branch liaison staff
- **Power Characteristics:**
  - **Continuity** (persists across election cycles)
  - **Network span** (cross-committee, cross-chamber connections)
  - **Institutional memory** (years of experience, precedent knowledge)
  - **Assignment history** (tracks movement between offices/committees)
- **Existing Schema:** `schemas/entities/staff.schema.json`
- **Power Indicators:**
  - `continuity_score` (0.0-1.0)
  - `network_span` (integer count)
  - `institutional_memory_depth` (years)
  - `cross_chamber_connections` (array)

#### Committee (Existing)
- **Entity Type:** `committee`
- **Entity ID Format:** Official code (e.g., `HASC`, `SASC`, `HAC-DEF`)
- **Power Characteristics:**
  - Jurisdictional authority
  - Agenda control
  - Report-writing authority
  - Referral routing
- **Existing Schema:** `data/committees/COMMITTEE_DATA_SCHEMA.md`
- **Power Indicators:**
  - Committee type (standing > select > joint > special)
  - Jurisdiction breadth (number of policy areas)
  - Membership size
  - Party control (majority vs. minority)

#### Subcommittee (Existing)
- **Entity Type:** `subcommittee`
- **Entity ID Format:** Composite (e.g., `HASC-MPIF`)
- **Power Characteristics:**
  - Specialized jurisdiction
  - First-mover advantage on specific policy areas
  - Report language influence
- **Existing Schema:** `data/committees/COMMITTEE_DATA_SCHEMA.md`

### 1.2 External Actor Nodes

#### Industry Organization
- **Entity Type:** `industry_org`
- **Entity ID Format:** `industry_org:{slug}` (e.g., `industry_org:defense-contractors-assoc`)
- **Entity Classes:**
  - `trade_association` — Industry trade associations
  - `corporation` — Individual corporations
  - `industry_coalition` — Ad-hoc industry coalitions
- **Power Characteristics:**
  - Resource capacity (lobbying budget, staff size)
  - Member base size
  - Geographic scope
  - Policy expertise depth
- **Required Fields:**
  - `name` (string)
  - `entity_class` (enum: trade_association, corporation, industry_coalition)
  - `industry_tags` (array of strings)
  - `geographic_scope` (array: "national" | state codes | district codes)
  - `resource_capacity` (object: `lobbying_budget_estimate`, `staff_size_estimate`)
  - `member_base_size` (integer, null for corporations)
- **Power Indicators:**
  - Resource capacity score (0.0-1.0)
  - Network reach (number of connected members/staff)
  - Historical success rate (if available)

#### Nonprofit Organization
- **Entity Type:** `nonprofit_org`
- **Entity ID Format:** `nonprofit_org:{slug}` (e.g., `nonprofit_org:environmental-policy-institute`)
- **Entity Classes:**
  - `advocacy_org` — Policy advocacy organizations
  - `research_org` — Research and think tanks
  - `grassroots_org` — Grassroots mobilization organizations
  - `professional_association` — Professional associations (non-industry)
- **Power Characteristics:**
  - Credibility and legitimacy
  - Research capacity
  - Grassroots mobilization capacity
  - Media access
- **Required Fields:**
  - `name` (string)
  - `entity_class` (enum: advocacy_org, research_org, grassroots_org, professional_association)
  - `policy_focus_tags` (array of strings)
  - `geographic_scope` (array)
  - `credibility_indicators` (object: `expert_testimony_count`, `media_mentions`, `research_publications`)
  - `mobilization_capacity` (object: `member_base_size`, `grassroots_reach_estimate`)
- **Power Indicators:**
  - Credibility score (0.0-1.0)
  - Research influence (0.0-1.0)
  - Mobilization capacity (0.0-1.0)

#### Trade Association
- **Entity Type:** `trade_association` (subset of industry_org, but distinct for querying)
- **Entity ID Format:** `trade_assoc:{slug}` (e.g., `trade_assoc:renewable-energy-coalition`)
- **Power Characteristics:**
  - Member organization aggregation
  - Unified messaging capacity
  - Industry-wide coordination
- **Note:** Can be modeled as `industry_org` with `entity_class: trade_association`, or as separate entity type for specialized queries.

### 1.3 Boundary & Meta Nodes

#### Coalition
- **Entity Type:** `coalition`
- **Entity ID Format:** `coalition:{uuid}` (e.g., `coalition:550e8400-e29b-41d4-a716-446655440000`)
- **Power Characteristics:**
  - Aggregated member power
  - Coordinated messaging
  - Shared resources
- **Required Fields:**
  - `name` (string)
  - `member_entity_ids` (array of entity IDs)
  - `formation_date` (ISO-8601)
  - `dissolution_date` (ISO-8601, null if active)
  - `coalition_type` (enum: `ad_hoc`, `formal`, `caucus`, `working_group`)
  - `policy_focus_tags` (array)
- **Power Indicators:**
  - Aggregate member power (sum of member power scores)
  - Coordination efficiency (0.0-1.0)
  - Resource pooling capacity

#### Narrative
- **Entity Type:** `narrative`
- **Entity ID Format:** `narrative:{slug}` (e.g., `narrative:energy-independence`)
- **Power Characteristics:**
  - Shapes discourse
  - Influences framing
  - Mobilizes support/opposition
- **Required Fields:**
  - `narrative_id` (string, slug)
  - `name` (string)
  - `framing_tags` (array: e.g., ["economic", "security", "environmental"])
  - `proponent_entity_ids` (array: entities promoting this narrative)
  - `opponent_entity_ids` (array: entities opposing this narrative)
  - `media_amplification_score` (0.0-1.0)
- **Power Indicators:**
  - Media amplification (0.0-1.0)
  - Proponent power aggregate
  - Opponent power aggregate
  - Net narrative power (proponent - opponent)

#### Boundary Actor
- **Entity Type:** `boundary_actor`
- **Entity ID Format:** `boundary:{slug}` (e.g., `boundary:media-energy-desk`)
- **Entity Classes:**
  - `media` — Media organizations/desks
  - `academic` — Academic institutions/researchers
  - `executive_agency` — Executive branch agencies
  - `state_local` — State/local government entities
  - `international` — International organizations
- **Power Characteristics:**
  - Information gatekeeping
  - Legitimacy conferral
  - Cross-boundary translation
- **Required Fields:**
  - `name` (string)
  - `entity_class` (enum: media, academic, executive_agency, state_local, international)
  - `influence_mechanism` (enum: `information_gatekeeping`, `legitimacy_conferral`, `translation`, `coordination`)
  - `reach_scope` (array: geographic/policy scope)

---

## 2. Edge Taxonomy

### 2.1 Authority Edges (Formal Power)

#### has_formal_authority_over
- **Edge Type:** `has_formal_authority_over`
- **Direction:** Directed (A → B means A has authority over B)
- **Examples:**
  - Committee Chair → Committee Members
  - Speaker → House Floor
  - Subcommittee Chair → Subcommittee Members
- **Weight Semantics:**
  - `procedural_power`: HIGH (can set rules)
  - `temporal_leverage`: HIGH (controls timing)
  - `retaliation_capacity`: MEDIUM-HIGH (can punish deviation)
- **Temporal Characteristics:**
  - Effective during term/assignment
  - Expires on role change
  - State-independent (applies across all legislative states)

#### controls_agenda_of
- **Edge Type:** `controls_agenda_of`
- **Direction:** Directed
- **Examples:**
  - Committee Chair → Committee Agenda
  - Leadership Staff → Floor Schedule
- **Weight Semantics:**
  - `procedural_power`: HIGH
  - `temporal_leverage`: VERY HIGH
  - `informational_advantage`: MEDIUM (knows what's coming)
- **Temporal Characteristics:**
  - Can be state-dependent (stronger in COMM_EVT, FLOOR_EVT)
  - Can decay if agenda control is challenged

### 2.2 Influence Edges (Informal Power)

#### influences_drafting
- **Edge Type:** `influences_drafting`
- **Direction:** Directed
- **Examples:**
  - Staff → Bill Language
  - Industry Org → Committee Staff
  - Research Org → Policy Language
- **Weight Semantics:**
  - `informational_advantage`: HIGH (expertise)
  - `institutional_memory`: MEDIUM-HIGH (knows precedent)
  - `procedural_power`: LOW (no formal authority)
- **Temporal Characteristics:**
  - Strongest in INTRO_EVT, COMM_EVT
  - Weakens in FLOOR_EVT, FINAL_EVT
  - Can activate/deactivate based on bill relevance

#### writes_report_language
- **Edge Type:** `writes_report_language`
- **Direction:** Directed
- **Examples:**
  - Committee Staff → Committee Report
  - Subcommittee Staff → Subcommittee Report
- **Weight Semantics:**
  - `informational_advantage`: HIGH
  - `institutional_memory`: HIGH
  - `procedural_power`: MEDIUM (language shapes interpretation)
- **Temporal Characteristics:**
  - Active in COMM_EVT
  - Expires after report publication

#### signals_pre_clearance
- **Edge Type:** `signals_pre_clearance`
- **Direction:** Directed
- **Examples:**
  - Leadership Staff → Committee Chairs
  - Industry Org → Member Offices
- **Weight Semantics:**
  - `informational_advantage`: HIGH (knows what leadership wants)
  - `retaliation_capacity`: MEDIUM (can signal disapproval)
- **Temporal Characteristics:**
  - State-dependent (stronger in COMM_EVT, FLOOR_EVT)
  - Can be implicit (inferred from patterns)

### 2.3 Blocking & Delay Edges

#### can_delay
- **Edge Type:** `can_delay`
- **Direction:** Directed
- **Examples:**
  - Committee Chair → Bill Advancement
  - Subcommittee Chair → Full Committee Consideration
- **Weight Semantics:**
  - `temporal_leverage`: VERY HIGH
  - `procedural_power`: MEDIUM-HIGH
- **Temporal Characteristics:**
  - State-dependent (relevant in COMM_EVT, FLOOR_EVT)
  - Can expire if delay window closes

#### can_block
- **Edge Type:** `can_block`
- **Direction:** Directed
- **Examples:**
  - Committee Chair → Bill (refuses to schedule)
  - Leadership → Floor Consideration
- **Weight Semantics:**
  - `procedural_power`: VERY HIGH
  - `retaliation_capacity`: HIGH
- **Temporal Characteristics:**
  - State-dependent
  - Can be overridden (creates conflict edge)

### 2.4 Routing & Translation Edges

#### routes_around
- **Edge Type:** `routes_around`
- **Direction:** Directed
- **Examples:**
  - Staff → Alternative Committee Path
  - Industry Org → Friendly Member Office
- **Weight Semantics:**
  - `informational_advantage`: HIGH (knows alternative paths)
  - `institutional_memory`: HIGH (knows precedent)
- **Temporal Characteristics:**
  - Activates when primary path is blocked
  - Can be state-dependent

#### translates_for
- **Edge Type:** `translates_for`
- **Direction:** Directed
- **Examples:**
  - Staff → Member (translates technical language)
  - Industry Org → Committee Staff (translates industry needs)
  - Research Org → Policy Language (translates research to policy)
- **Weight Semantics:**
  - `informational_advantage`: HIGH
  - `institutional_memory`: MEDIUM
- **Temporal Characteristics:**
  - Ongoing (persistent relationship)
  - Can strengthen during relevant policy debates

### 2.5 Legitimacy & Reputation Edges

#### confers_legitimacy_to
- **Edge Type:** `confers_legitimacy_to`
- **Direction:** Directed
- **Examples:**
  - Research Org → Policy Position
  - Academic → Expert Testimony
  - Media → Narrative
- **Weight Semantics:**
  - `informational_advantage`: MEDIUM (credibility)
  - `retaliation_capacity`: LOW (no direct punishment)
- **Temporal Characteristics:**
  - Can decay if credibility is challenged
  - Can transfer (legitimacy can move between entities)

#### applies_reputational_pressure_to
- **Edge Type:** `applies_reputational_pressure_to`
- **Direction:** Directed
- **Examples:**
  - Media → Member (negative coverage)
  - Coalition → Industry Org (public pressure)
  - Nonprofit → Policy Position (advocacy campaign)
- **Weight Semantics:**
  - `retaliation_capacity`: MEDIUM-HIGH (reputational harm)
  - `informational_advantage`: LOW
- **Temporal Characteristics:**
  - Activates during public campaigns
  - Can be state-dependent (stronger when public attention is high)

### 2.6 Memory Transfer Edges

#### transfers_memory_to
- **Edge Type:** `transfers_memory_to`
- **Direction:** Directed
- **Examples:**
  - Former Staff → New Office (staff movement)
  - Former Member → Lobbying Firm (revolving door)
  - Committee Staff → Industry Org (expertise transfer)
- **Weight Semantics:**
  - `institutional_memory`: HIGH (transfers knowledge)
  - `informational_advantage`: MEDIUM (knows internal processes)
- **Temporal Characteristics:**
  - Activates on staff/member movement
  - Can decay over time (memory fades)
  - Can be bidirectional (ongoing relationship)

#### shares_precedent_with
- **Edge Type:** `shares_precedent_with`
- **Direction:** Undirected (or bidirectional)
- **Examples:**
  - Staff ↔ Staff (shared committee experience)
  - Committee ↔ Committee (similar jurisdiction)
- **Weight Semantics:**
  - `institutional_memory`: HIGH
  - `informational_advantage`: MEDIUM
- **Temporal Characteristics:**
  - Persistent (ongoing relationship)
  - Strengthens with shared experience

### 2.7 Pre-Negotiation Edges

#### pre_negotiates_with
- **Edge Type:** `pre_negotiates_with`
- **Direction:** Bidirectional (or undirected)
- **Examples:**
  - Industry Org ↔ Committee Staff (pre-markup negotiations)
  - Member ↔ Member (whip counts, vote trading)
  - Coalition ↔ Coalition (alliance building)
- **Weight Semantics:**
  - `informational_advantage`: HIGH (knows positions before public)
  - `temporal_leverage`: MEDIUM (shapes timing)
- **Temporal Characteristics:**
  - Activates before public events (markups, votes)
  - Can be inferred from patterns (repeated interactions)
  - State-dependent (stronger in COMM_EVT, FLOOR_EVT)

### 2.8 Edge Status Lifecycle

All edges support the following lifecycle states (from `influence_edge.schema.json`):
- **ACTIVE** — Currently effective
- **DORMANT** — Temporarily inactive but may reactivate
- **DECAYING** — Losing strength over time
- **ARCHIVED** — Permanently inactive

---

## 3. Power Classification System

### 3.1 Power Types: PRIMARY / SECONDARY / SHADOW

#### PRIMARY Power
- **Definition:** Direct, formal authority to make decisions or block advancement
- **Examples:**
  - Committee Chair (can schedule, block, set agenda)
  - Speaker (controls floor)
  - Member with decisive vote
- **Characteristics:**
  - Formal authority (conferred by rules/position)
  - Visible (publicly known)
  - State-dependent (varies by legislative state)
- **Conflict Resolution:** PRIMARY overrides SECONDARY and SHADOW

#### SECONDARY Power
- **Definition:** Significant influence but no formal blocking authority
- **Examples:**
  - Ranking Member (can influence but not block)
  - Senior Staff (shapes language, timing)
  - Large Industry Org (resource capacity, relationships)
- **Characteristics:**
  - Informal influence (relationships, expertise, resources)
  - Can be highly effective but not decisive
  - Often works through PRIMARY power holders
- **Conflict Resolution:** SECONDARY overrides SHADOW, defers to PRIMARY

#### SHADOW Power
- **Definition:** Indirect influence through information, legitimacy, or translation
- **Examples:**
  - Research Org (credibility, expertise)
  - Media (narrative shaping)
  - Former Staff (memory transfer, relationships)
- **Characteristics:**
  - Indirect mechanisms
  - Often invisible or underappreciated
  - Can be highly effective in aggregate
- **Conflict Resolution:** SHADOW defers to PRIMARY and SECONDARY

### 3.2 Contextual Power Classification

Power classification is **contextual** and must be specified for:
- **Legislative State** (PRE_EVT, INTRO_EVT, COMM_EVT, FLOOR_EVT, FINAL_EVT, IMPL_EVT)
- **Policy Area** (optional, e.g., "defense", "energy")
- **Bill ID** (optional, for bill-specific power)
- **Committee ID** (optional, for committee-specific power)

**Example:**
- Staff member may be PRIMARY in COMM_EVT (drafts language) but SHADOW in FLOOR_EVT (no formal role)
- Industry org may be SECONDARY in COMM_EVT (influences staff) but SHADOW in FLOOR_EVT (no direct access)

### 3.3 Conflict Resolution Rules

When multiple power classifications apply to the same entity in the same context:

1. **PRIMARY > SECONDARY > SHADOW** (hierarchy)
2. **Most specific context wins** (bill-specific > committee-specific > policy-area > state-only)
3. **Most recent classification wins** (if same specificity)
4. **Override tracking** (record which classification overrides which, for audit)

**Implementation:**
- Use `control_classification.schema.json` (already exists)
- `overrides_classification_id` field tracks overrides
- Temporal validity ensures classifications expire appropriately

### 3.4 Power Calculation

Power is not a single number but a **multi-axis vector**:

1. **Procedural Power** (0.0-1.0) — Can change rules/timing
2. **Temporal Leverage** (0.0-1.0) — Controls when things happen
3. **Informational Advantage** (0.0-1.0) — Has access to non-public information
4. **Institutional Memory** (0.0-1.0) — Knows precedent/history
5. **Retaliation Capacity** (0.0-1.0) — Can punish deviation

**Aggregate Power Score** (optional, for ranking):
- Weighted sum of axes (weights configurable by use case)
- Default: Equal weights
- Can be context-specific (e.g., COMM_EVT weights procedural_power higher)

---

## 4. Compatibility with Existing Systems

### 4.1 Artifact Schema Compatibility

All graph entities and edges must include `_meta` header compatible with `artifact.schema.json`:

```json
{
  "_meta": {
    "agent_id": "graph_builder_agent",
    "generated_at": "2026-01-20T12:00:00Z",
    "artifact_type": "graph_node" | "graph_edge" | "power_classification",
    "artifact_name": "Human-readable name",
    "requires_review": "HR_PRE" | null,
    "guidance_status": "SIGNED" | "TEST_MODE",
    "status": "SPECULATIVE" | "NON-AUTHORITATIVE" | "ACTIONABLE",
    "confidence": "SPECULATIVE" | "HIGH" | "MEDIUM" | "LOW"
  }
}
```

**Key Compatibility Points:**
- Graph data can be stored as artifacts
- Review gates apply to graph updates (especially power classifications)
- Confidence levels track uncertainty in relationships
- Status tracks authority (SPECULATIVE relationships vs. ACTIONABLE)

### 4.2 Phase State Integration

Graph edges and power classifications are **state-aware**:

- Edges can have `legislative_state` field (null if state-independent)
- Power classifications include `context.legislative_state`
- Graph queries can filter by legislative state
- State transitions can trigger edge activation/decay

**Example Query:**
"Who has PRIMARY power in COMM_EVT for defense policy?"
→ Returns entities with `control_type: PRIMARY`, `context.legislative_state: COMM_EVT`, `context.policy_area: defense`

### 4.3 Review Gate Integration

Power classifications and high-stakes edges should require human review:

- **HR_PRE** gate: Review PRIMARY power classifications
- **HR_LANG** gate: Review edges that affect drafting (influences_drafting, writes_report_language)
- **HR_MSG** gate: Review narrative edges and legitimacy conferral
- **HR_RELEASE** gate: Review before making graph data public

**Decision Log Integration:**
- Human decisions on power classifications logged via `decision_log.schema.json`
- Override decisions tracked (why PRIMARY was assigned, why edge was created/modified)

### 4.4 Audit Logging

All graph modifications must be auditable:

- **Entity creation/modification:** Logged with agent_id, timestamp, rationale
- **Edge creation/modification:** Logged with weight changes, activation events
- **Power classification:** Logged with evidence, rationale, override tracking
- **State transitions:** Can trigger graph updates (edge activation/decay)

**Integration Points:**
- Use existing diagnostic/audit systems
- Graph updates appear in workflow state history
- Power transfers logged via `power_transfer.schema.json`
- Power decay tracked via `power_decay.schema.json`

### 4.5 Dashboard Compatibility

Graph data must support existing dashboard assumptions:

- **Queryable:** Support common queries (who influences X, what is Y's power, etc.)
- **Visualizable:** Graph structure can be rendered (nodes, edges, weights)
- **Filterable:** By legislative state, policy area, entity type, power type
- **Temporal:** Support time-series queries (how did power change over time?)

---

## 5. Open Questions & Risks

### 5.1 Data Sources

**Question:** How do we populate the graph initially?

**Options:**
1. **Manual entry** (human-curated, high quality, slow)
2. **Automated extraction** (from public records, lobbying disclosures, faster but lower quality)
3. **Hybrid** (automated extraction + human review gates)

**Recommendation:** Start with hybrid — automated extraction with HR_PRE review gates for PRIMARY power classifications.

**Risk:** Low-quality data leads to incorrect power assessments.

**Mitigation:** Confidence levels, review gates, and audit logging.

### 5.2 Edge Inference

**Question:** How do we infer edges that aren't explicitly documented?

**Examples:**
- Pre-negotiation edges (inferred from timing patterns)
- Memory transfer edges (inferred from staff movement)
- Translation edges (inferred from repeated interactions)

**Options:**
1. **Explicit only** (only create edges from direct evidence)
2. **Inferred with confidence scores** (create edges with LOW confidence, require review)
3. **Machine learning** (train models to predict edges)

**Recommendation:** Start with explicit only, add inferred edges with LOW confidence and HR_PRE review.

**Risk:** False positives in edge inference create misleading graph.

**Mitigation:** Confidence levels, review gates, and ability to archive false edges.

### 5.3 Power Classification Automation

**Question:** Can power classifications be automated, or must they be human-assigned?

**Options:**
1. **Fully automated** (rules-based: chair = PRIMARY, staff = SECONDARY, etc.)
2. **Human-assigned only** (all classifications require review)
3. **Hybrid** (automated defaults, human override)

**Recommendation:** Hybrid — automated defaults based on formal roles, human review for PRIMARY classifications and edge cases.

**Risk:** Automated classification misses nuance (e.g., weak chair vs. strong chair).

**Mitigation:** Confidence scores, review gates, and override tracking.

### 5.4 Graph Scale

**Question:** How do we handle graph scale as entities and edges grow?

**Considerations:**
- Thousands of members, staff, organizations
- Millions of potential edges
- Temporal history (edges change over time)
- State-dependent queries (filter by legislative state)

**Options:**
1. **Full graph** (store all edges, query with filters)
2. **Subgraph extraction** (extract relevant subgraphs for specific queries)
3. **Graph database** (use specialized DB like Neo4j, ArangoDB)

**Recommendation:** Start with full graph in JSON/document store, migrate to graph database if scale becomes issue.

**Risk:** Performance degradation as graph grows.

**Mitigation:** Indexing, query optimization, subgraph extraction for common queries.

### 5.5 Temporal Complexity

**Question:** How do we handle temporal evolution of the graph?

**Considerations:**
- Edges activate/decay over time
- Power classifications change with state transitions
- Staff movement creates new edges, archives old ones
- Historical queries (what was power structure in COMM_EVT 6 months ago?)

**Options:**
1. **Snapshot-based** (store graph snapshots at key times)
2. **Event-based** (store events that modify graph, reconstruct at query time)
3. **Hybrid** (snapshots + event log)

**Recommendation:** Hybrid — event-based with periodic snapshots for performance.

**Risk:** Temporal queries become slow as event log grows.

**Mitigation:** Periodic snapshots, event log pruning, efficient reconstruction algorithms.

### 5.6 Privacy & Ethics

**Question:** How do we handle privacy and ethical concerns?

**Considerations:**
- Staff relationships may be sensitive
- Industry influence may be controversial
- Power classifications could be weaponized
- Graph data could leak strategic information

**Options:**
1. **Public data only** (only use publicly available information)
2. **Access controls** (restrict graph access to authorized users)
3. **Anonymization** (anonymize sensitive relationships)

**Recommendation:** Public data only, with access controls for internal use. No anonymization (defeats purpose of graph).

**Risk:** Privacy violations, ethical concerns, legal issues.

**Mitigation:** Public data only, clear access controls, audit logging, human review for sensitive classifications.

---

## 6. Implementation Phases

### Phase 1: Core Node & Edge Schemas
- **Deliverables:**
  - Node schemas for all entity types (extend existing, add new)
  - Edge schema extensions (add missing edge types to `influence_edge.schema.json`)
  - Power classification schema (already exists: `control_classification.schema.json`)
- **Dependencies:** None
- **Risk:** Low (schema definition only)

### Phase 2: Graph Builder Agent
- **Deliverables:**
  - Agent that creates/updates graph entities and edges
  - Integration with artifact system (`_meta` headers)
  - Integration with review gates (HR_PRE for PRIMARY power)
- **Dependencies:** Phase 1
- **Risk:** Medium (complexity of graph operations)

### Phase 3: Power Classification Engine
- **Deliverables:**
  - Automated power classification (rules-based defaults)
  - Conflict resolution logic
  - Integration with state transitions
- **Dependencies:** Phase 1, Phase 2
- **Risk:** Medium (classification logic complexity)

### Phase 4: Graph Query Interface
- **Deliverables:**
  - Query API (who influences X, what is Y's power, etc.)
  - Filtering by state, policy area, entity type
  - Temporal queries (power over time)
- **Dependencies:** Phase 1, Phase 2, Phase 3
- **Risk:** Medium (query performance at scale)

### Phase 5: Dashboard Integration
- **Deliverables:**
  - Graph visualization in dashboard
  - Power heatmaps
  - Influence pathway visualization
- **Dependencies:** Phase 4
- **Risk:** Low (visualization only)

### Phase 6: Temporal & Decay Modeling
- **Deliverables:**
  - Edge activation/decay on state transitions
  - Power transfer tracking (staff movement, etc.)
  - Historical graph reconstruction
- **Dependencies:** Phase 2, Phase 3
- **Risk:** High (temporal complexity)

---

## 7. Success Criteria

### Functional Requirements
- ✅ Graph supports all node types (Members, Staff, Industry, Nonprofits, Trade Associations, Coalitions, Narratives, Boundary Actors)
- ✅ Graph supports all edge types (authority, influence, blocking, routing, legitimacy, memory, pre-negotiation)
- ✅ Power classifications are contextual (state-dependent, policy-area-dependent)
- ✅ Conflict resolution works (PRIMARY > SECONDARY > SHADOW, specificity wins)
- ✅ Graph queries are performant (< 1 second for common queries)
- ✅ Graph integrates with artifact system, review gates, audit logging

### Quality Requirements
- ✅ Graph data is auditable (all modifications logged)
- ✅ Graph data is reviewable (high-stakes edges/classifications require human review)
- ✅ Graph data supports confidence levels (uncertainty is explicit)
- ✅ Graph data is compatible with existing schemas (`_meta` headers, etc.)

### Performance Requirements
- ✅ Graph supports 10,000+ entities
- ✅ Graph supports 100,000+ edges
- ✅ Common queries complete in < 1 second
- ✅ Temporal queries (6-month history) complete in < 5 seconds

---

## 8. Decision Handoff

**Recommended Approach:** Hybrid automation with human review gates

**Key Assumptions:**
- Public data only (no private/internal information)
- Automated defaults with human override
- Event-based temporal model with periodic snapshots
- Start with explicit edges only, add inference later

**Execution Handoff:**
- **Inputs:** Existing schemas, committee data, staff data, stakeholder maps
- **Outputs:** Graph node/edge schemas, graph builder agent, power classification engine, query interface
- **Constraints:** Must integrate with artifact system, review gates, audit logging
- **Success Criteria:** See Section 7

**Open Questions Requiring Human Input:**
1. Data source strategy (manual vs. automated vs. hybrid) — **Recommendation: Hybrid**
2. Edge inference strategy (explicit only vs. inferred) — **Recommendation: Explicit only initially**
3. Graph database choice (document store vs. graph DB) — **Recommendation: Document store initially, migrate if needed**
4. Privacy/ethics boundaries — **Recommendation: Public data only, access controls**

---

## Appendix A: Edge Type Reference

| Edge Type | Direction | Primary Weight Axes | State Dependency | Example |
|-----------|-----------|---------------------|------------------|---------|
| `has_formal_authority_over` | Directed | procedural_power, temporal_leverage | State-independent | Chair → Members |
| `controls_agenda_of` | Directed | procedural_power, temporal_leverage | COMM_EVT, FLOOR_EVT | Chair → Agenda |
| `influences_drafting` | Directed | informational_advantage, institutional_memory | INTRO_EVT, COMM_EVT | Staff → Language |
| `writes_report_language` | Directed | informational_advantage, institutional_memory | COMM_EVT | Staff → Report |
| `signals_pre_clearance` | Directed | informational_advantage | COMM_EVT, FLOOR_EVT | Leadership → Chairs |
| `can_delay` | Directed | temporal_leverage, procedural_power | COMM_EVT, FLOOR_EVT | Chair → Bill |
| `can_block` | Directed | procedural_power, retaliation_capacity | COMM_EVT, FLOOR_EVT | Chair → Bill |
| `routes_around` | Directed | informational_advantage, institutional_memory | COMM_EVT | Staff → Alternative Path |
| `translates_for` | Directed | informational_advantage | State-independent | Staff → Member |
| `confers_legitimacy_to` | Directed | (low weights, credibility-based) | State-independent | Research → Policy |
| `applies_reputational_pressure_to` | Directed | retaliation_capacity | FLOOR_EVT, FINAL_EVT | Media → Member |
| `transfers_memory_to` | Directed | institutional_memory, informational_advantage | State-independent | Former Staff → New Office |
| `shares_precedent_with` | Bidirectional | institutional_memory | State-independent | Staff ↔ Staff |
| `pre_negotiates_with` | Bidirectional | informational_advantage, temporal_leverage | COMM_EVT, FLOOR_EVT | Industry ↔ Staff |

---

## Appendix B: Node Type Reference

| Entity Type | Entity Class Options | Power Characteristics | Primary Power Indicators |
|-------------|---------------------|----------------------|-------------------------|
| `member` | (none) | Formal voting, committee roles | Committee role, leadership, seniority |
| `staff` | committee_staff, subcommittee_staff, leadership_staff, personal_office_staff, agency_liaison | Continuity, network span, memory | continuity_score, network_span, institutional_memory_depth |
| `committee` | (none) | Jurisdictional authority, agenda control | Committee type, jurisdiction breadth, party control |
| `subcommittee` | (none) | Specialized jurisdiction | Jurisdiction specificity, first-mover advantage |
| `industry_org` | trade_association, corporation, industry_coalition | Resource capacity, member base | Resource capacity, network reach, historical success |
| `nonprofit_org` | advocacy_org, research_org, grassroots_org, professional_association | Credibility, research, mobilization | Credibility score, research influence, mobilization capacity |
| `trade_association` | (subset of industry_org) | Member aggregation, unified messaging | Member base size, coordination efficiency |
| `coalition` | ad_hoc, formal, caucus, working_group | Aggregated power, coordination | Aggregate member power, coordination efficiency |
| `narrative` | (none) | Discourse shaping, framing | Media amplification, proponent power aggregate |
| `boundary_actor` | media, academic, executive_agency, state_local, international | Gatekeeping, legitimacy, translation | Reach scope, influence mechanism |

---

**END OF PLANNING DOCUMENT**
