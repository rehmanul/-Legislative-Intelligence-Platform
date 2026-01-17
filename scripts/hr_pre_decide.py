---
config:
  layout: dagre
  elk:
    nodePlacementStrategy: NETWORK_SIMPLEX
    mergeEdges: true
    padding: 16
---
flowchart TB
AVAQ(["👥 AVAQ Strategic Team"]):::human
AI_CORE(["🤖 AI Policy Execution Agent"]):::ai
subgraph LEGISLATIVE["📜 Legislative Process Spine (Authoritative Timeline)"]
direction TB
PRE_EVT((Policy Opportunity Detected)):::system
PRE_SIGNAL_SCAN("Signal Scanning<br/>Industry · Courts · Agencies"):::human
PRE_STAKEHOLDER_MAP["Stakeholder Landscape Map"]:::artifact
PRE_EDU("Staff & Member Education"):::human
PRE_CONCEPT["Concept Memo"]:::artifact
INTRO_EVT((Bill Vehicle Identified)):::system
INTRO_SPONSOR("Sponsor Targeting"):::human
INTRO_FRAME["Legitimacy & Policy Framing"]:::artifact
INTRO_ACAD("Academic Validation"):::human
INTRO_WHITEPAPER["Policy Whitepaper"]:::artifact
COMM_EVT((Committee Referral)):::system
COMM_AGENDA("Agenda & Member Analysis"):::human
COMM_BRIEFS["Committee Briefing Packets"]:::artifact
COMM_LANG["Draft Legislative Language"]:::artifact
COMM_AMEND["Amendment Strategy"]:::artifact
FLOOR_EVT((Floor Scheduled)):::system
FLOOR_MSG["Floor Messaging & Talking Points"]:::artifact
FLOOR_TIMING("Timing & Vote Whip Strategy"):::human
FLOOR_MEDIA["Press & Media Narrative"]:::artifact
FINAL_EVT((Vote Imminent)):::decision
FINAL_COAL("Coalition Activation"):::human
FINAL_NARR["Final Constituent Narrative"]:::artifact
IMPL_EVT((Law Enacted)):::system
IMPL_GUIDE["Implementation Guidance"]:::artifact
IMPL_OVERSIGHT("Oversight & Compliance Prep"):::human
IMPL_OUTCOME["Outcome & Impact Report"]:::artifact

end
PRE_EVT --> PRE_SIGNAL_SCAN --> PRE_STAKEHOLDER_MAP --> PRE_EDU --> PRE_CONCEPT --> INTRO_EVT
INTRO_EVT --> INTRO_SPONSOR --> INTRO_FRAME --> INTRO_ACAD --> INTRO_WHITEPAPER --> COMM_EVT
COMM_EVT --> COMM_AGENDA --> COMM_BRIEFS --> COMM_LANG --> COMM_AMEND --> FLOOR_EVT
FLOOR_EVT --> FLOOR_MSG --> FLOOR_TIMING --> FLOOR_MEDIA --> FINAL_EVT
FINAL_EVT --> FINAL_COAL --> FINAL_NARR --> IMPL_EVT
IMPL_EVT --> IMPL_GUIDE --> IMPL_OVERSIGHT --> IMPL_OUTCOME

AVAQ --> PRE_EDU
AVAQ --> INTRO_SPONSOR
AVAQ --> COMM_AGENDA
AVAQ --> FLOOR_TIMING
AVAQ --> FINAL_COAL
AVAQ --> IMPL_OVERSIGHT
subgraph AI_SERVICES["🤖 AI Service Execution Layer"]
direction TB

AI_INGEST("🔍 Multi-Source Ingestion<br/>Public · Academic · Internal"):::ai
AI_RETRIEVE("🔎 Contextual Retrieval"):::ai
AI_FEATURES("📐 Feature Extraction<br/>Signals · Frames · Votes"):::ai
AI_GENERATE("🧠 Draft & Strategy Generation"):::ai
AI_SCORE("📊 Impact & Risk Scoring"):::ai

end

AI_INGEST --> AI_RETRIEVE --> AI_FEATURES --> AI_GENERATE --> AI_SCORE
AI_GENERATE -.-> PRE_STAKEHOLDER_MAP
AI_GENERATE -.-> PRE_CONCEPT
AI_GENERATE -.-> INTRO_FRAME
AI_GENERATE -.-> INTRO_WHITEPAPER
AI_GENERATE -.-> COMM_BRIEFS
AI_GENERATE -.-> COMM_LANG
AI_GENERATE -.-> COMM_AMEND
AI_GENERATE -.-> FLOOR_MSG
AI_GENERATE -.-> FLOOR_MEDIA
AI_GENERATE -.-> FINAL_NARR
AI_GENERATE -.-> IMPL_GUIDE
subgraph HUMAN_REVIEW["👤 Human Judgment & Approval"]
direction TB

HR_PRE{Approve Concept Direction?}:::decision
HR_LANG{Approve Legislative Language?}:::decision
HR_MSG{Approve Messaging & Narrative?}:::decision
HR_RELEASE{Authorize Public Release?}:::decision

end

PRE_CONCEPT --> HR_PRE --o INTRO_EVT
COMM_LANG --> HR_LANG --o FLOOR_EVT
FLOOR_MEDIA --> HR_MSG --o FINAL_EVT
FINAL_NARR --> HR_RELEASE --o IMPL_EVT

AVAQ --> HR_PRE
AVAQ --> HR_LANG
AVAQ --> HR_MSG
AVAQ --> HR_RELEASE
subgraph MEMORY["🗄️ Evidence, Memory & Learning"]
direction TB

MEM_EVIDENCE[(🗄️ Evidence Store)]:::data
MEM_TACTICS[(📊 Tactic Performance History)]:::data
MEM_NARRATIVE[(🗣️ Narrative Effectiveness Log)]:::data
MEM_OUTCOMES[(📈 Legislative Outcomes)]:::data

LEARN_CAUSAL("📐 Causal Attribution Engine"):::ai
LEARN_UPDATE("🔁 Strategy Reweighting"):::ai

end

AI_SCORE --> MEM_EVIDENCE
FINAL_EVT --> MEM_OUTCOMES
IMPL_OUTCOME --> MEM_OUTCOMES
FLOOR_MEDIA --> MEM_NARRATIVE
COMM_AMEND --> MEM_TACTICS

MEM_EVIDENCE --> LEARN_CAUSAL
MEM_OUTCOMES --> LEARN_CAUSAL
MEM_TACTICS --> LEARN_CAUSAL
MEM_NARRATIVE --> LEARN_CAUSAL

LEARN_CAUSAL --> LEARN_UPDATE --> AI_FEATURES
subgraph MARKETING["📣 Messaging & Marketing Intelligence"]
direction TB

MSG_TEST("🧪 Message Variant Testing"):::ai
MSG_SIGNAL("📡 Media & Public Signal Capture"):::system
MSG_SCORE("📊 Persuasion Effectiveness Scoring"):::ai

end

FLOOR_MEDIA --> MSG_TEST
MSG_TEST --> MSG_SIGNAL --> MSG_SCORE
MSG_SCORE --> MEM_NARRATIVE
MSG_SCORE -.-> AI_GENERATE
subgraph GOVERNANCE["⚖️ Professional Governance & Bounds"]
direction TB

LEGAL(["⚖️ Legislative Counsel"]):::human
COMPLIANCE(["🛡️ Compliance Officer"]):::human
POLICY(["🧠 Policy Director"]):::human
ACADEMIC(["🎓 Academic Validator"]):::human

GUIDANCE["📑 Signed Guidance & Constraints"]:::artifact
AUDIT[(🧾 Audit & Rationale Log)]:::data

end

LEGAL --> GUIDANCE
COMPLIANCE --> GUIDANCE
POLICY --> GUIDANCE
ACADEMIC --> GUIDANCE

GUIDANCE ==> AI_GENERATE
GUIDANCE ==> AI_SCORE
AI_GENERATE --> AUDIT
AI_SCORE --> AUDIT
subgraph REALITY["🌍 External Reality"]
direction TB
REAL_ELECT((🗳️ Elections)):::system
REAL_COURT((⚖️ Court Rulings)):::system
REAL_AGENCY((🏛️ Agency Actions)):::system
REAL_MARKET((🏭 Industry Behavior)):::system
end

REAL_ELECT -.-> PRE_EVT
REAL_COURT -.-> PRE_EVT
REAL_AGENCY -.-> PRE_EVT
REAL_MARKET -.-> PRE_EVT
classDef human fill:#E0F2FE,stroke:#0369A1,stroke-width:2px
classDef ai fill:#F3E8FF,stroke:#7C3AED,stroke-width:2px
classDef system fill:#ECFDF5,stroke:#047857,stroke-width:2px
classDef artifact fill:#DBEAFE,stroke:#1E40AF,stroke-width:2px
classDef data fill:#FEF9C3,stroke:#CA8A04,stroke-width:2px
classDef decision fill:#FEE2E2,stroke:#991B1B,stroke-width:2px

subgraph EXECUTION_LOOP["🔄 Post-Decision Execution & Adaptive Momentum"]
direction TB
EXEC_STRATEGY("🧠 Strategy Decomposition<br/>Goals → Plays → Tasks"):::ai
EXEC_TACTICS("🎯 Tactical Planning<br/>Outreach · Messaging · Timing"):::ai
EXEC_RUN("⚙️ Tactic Execution Engine<br/>Briefings · Outreach · Narrative Push"):::system
EXEC_MONITOR("📡 Live Monitoring<br/>Staff Signals · Media · Votes"):::system
EXEC_ALERT((⚠️ Deviation / Opportunity Detected)):::ai
EXEC_RETUNE("🔁 Tactical Retuning<br/>Adjust Frames · Targets · Timing"):::ai

end
IMPL_OUTCOME --> EXEC_STRATEGY
EXEC_STRATEGY --> EXEC_TACTICS --> EXEC_RUN --> EXEC_MONITOR --> EXEC_ALERT --> EXEC_RETUNE
EXEC_RETUNE --> AI_FEATURES
EXEC_ALERT --> MEM_TACTICS
EXEC_MONITOR --> MEM_NARRATIVE
EXEC_ALERT -.-> AVAQ

%% =====================================================
%% 🧭 HUMAN REVIEW — COST, EFFORT & RISK SIGNALING (ADDITIVE)
%% Purpose: make “approve” actions legible in effort, time, and risk
%% Does NOT replace existing Human Review decisions
%% =====================================================

subgraph HUMAN_COSTS["👤 Human Review Effort & Cost Signals"]
direction TB

%% --- Concept Approval Effort ---
COST_PRE_TIME["⏱️ ~10–15 min<br/>Skim & Sanity Check"]:::artifact
COST_PRE_RISK["⚠️ Low–Medium Risk<br/>Directional Alignment"]:::artifact

%% --- Legislative Language Approval Effort ---
COST_LANG_TIME["⏱️ ~45–90 min<br/>Deep Review"]:::artifact
COST_LANG_RISK["⚠️ High Risk<br/>Statutory / Legal Exposure"]:::artifact

%% --- Messaging Approval Effort ---
COST_MSG_TIME["⏱️ ~15–30 min<br/>Content & Tone Review"]:::artifact
COST_MSG_RISK["⚠️ Medium Risk<br/>Reputational / Narrative"]:::artifact

%% --- Public Release Approval Effort ---
COST_REL_TIME["⏱️ ~5–10 min<br/>Final Go / No-Go"]:::artifact
COST_REL_RISK["⚠️ High Visibility<br/>Irreversible Action"]:::artifact

end

%% Map cost signals to existing decision gates (non-blocking, informational)
HR_PRE -.-> COST_PRE_TIME
HR_PRE -.-> COST_PRE_RISK

HR_LANG -.-> COST_LANG_TIME
HR_LANG -.-> COST_LANG_RISK

HR_MSG -.-> COST_MSG_TIME
HR_MSG -.-> COST_MSG_RISK

HR_RELEASE -.-> COST_REL_TIME
HR_RELEASE -.-> COST_REL_RISK


%% =====================================================
%% ⏱️ EXECUTION LOOP — TEMPORAL CLARIFICATION (ADDITIVE)
%% Purpose: clarify WHEN the execution loop operates
%% =====================================================

subgraph EXECUTION_SCOPE["🕒 Execution Scope & Timing"]
direction TB

SCOPE_ACTIVE["📍 Operates While Bill Is Active<br/>Pre-Vote · Committee · Floor"]:::artifact
SCOPE_NOT_POST["🚫 Not Post-Mortem<br/>Not Historical Analysis"]:::artifact
SCOPE_NOT_ONLY_LAW["🚫 Not Only Post-Enactment<br/>Runs Before Law Is Passed"]:::artifact

end

%% Anchor scope clarification to execution loop
EXEC_STRATEGY -.-> SCOPE_ACTIVE
EXEC_STRATEGY -.-> SCOPE_NOT_POST
EXEC_STRATEGY -.-> SCOPE_NOT_ONLY_LAW


%% =====================================================
%% 🧩 RIGHT-HAND COLUMN CONTINUITY (CAUSE → EXECUTION → SPECIALIZATION)
%% Purpose: visually explain why Governance, AI Services,
%% and Marketing sit next to each other
%% =====================================================

subgraph CONTINUITY["➡️ Constraint → Execution → Specialization"]
direction TB

CONT_GOV["⚖️ Constraints & Bounds<br/>What AI Is Allowed To Do"]:::artifact
CONT_EXEC["🤖 Execution Engine<br/>How Work Is Performed"]:::artifact
CONT_SPEC["📣 Domain Intelligence<br/>Messaging & Persuasion"]:::artifact

end

%% Causal continuity (informational, not control flow)
GUIDANCE -.-> CONT_GOV
CONT_GOV -.-> AI_SERVICES
AI_SERVICES -.-> CONT_EXEC
CONT_EXEC -.-> MARKETING
MARKETING -.-> CONT_SPEC


%% =====================================================
%% 👀 OPTIONAL USER ORIENTATION CALLOUTS (LOW NOISE)
%% Purpose: give readers novelty and orientation as they scroll
%% =====================================================

subgraph ORIENTATION["🧭 How To Read This Diagram"]
direction TB

READ_SPINE["⬇️ Read Down = Legislative Time"]:::artifact
READ_RIGHT["➡️ Read Right = Automation & Services"]:::artifact
READ_DECISIONS["🔴 Diamonds = Rare Human Decisions"]:::artifact

end

READ_SPINE -.-> LEGISLATIVE
READ_RIGHT -.-> AI_SERVICES
READ_DECISIONS -.-> HUMAN_REVIEW
%% =====================================================
%% 🚦 ACTIVE CAMPAIGN OPERATIONS (NOVEL, PARALLEL MOTION)
%% Purpose: show real lobbying work happening right now
%% Audience: business devs, industry pros, lobbyists
%% =====================================================

subgraph CAMPAIGN_OPS["🔥 Active Campaign Operations (While Bill Is Live)"]
direction TB

%% ======================
%% PARALLEL CAMPAIGN THREADS
%% ======================

THREAD_COMMITTEE("🧵 Committee Outreach Wave<br/>Targeted Staff Touchpoints"):::system
THREAD_NARRATIVE("🧵 Narrative Reframing Push<br/>Message Alignment & Media Prep"):::system
THREAD_COALITION("🧵 Coalition Expansion Sprint<br/>Partner Activation"):::system
THREAD_OPPOSITION("🧵 Opposition Neutralization Track<br/>Counter-Framing"):::system

end

%% Threads originate from active execution
EXEC_RUN --> THREAD_COMMITTEE
EXEC_RUN --> THREAD_NARRATIVE
EXEC_RUN --> THREAD_COALITION
EXEC_RUN --> THREAD_OPPOSITION


%% =====================================================
%% ⏳ OPPORTUNITY WINDOWS (TIME-SENSITIVE ADVANTAGE)
%% =====================================================

subgraph OPPORTUNITIES["⏰ Live Opportunity Windows"]
direction TB

WIN_MSG((🪟 48-Hour Messaging Window)):::decision
WIN_MEMBER((🪟 Undecided Member Window)):::decision
WIN_AMEND((🪟 Amendment Timing Window)):::decision
WIN_MEDIA((🪟 Media Cycle Alignment Window)):::decision

end

%% Monitoring opens windows
EXEC_MONITOR --> WIN_MSG
EXEC_MONITOR --> WIN_MEMBER
EXEC_MONITOR --> WIN_AMEND
EXEC_MONITOR --> WIN_MEDIA

%% Windows feed back into tactical planning
WIN_MSG -.-> EXEC_TACTICS
WIN_MEMBER -.-> EXEC_TACTICS
WIN_AMEND -.-> EXEC_TACTICS
WIN_MEDIA -.-> EXEC_TACTICS


%% =====================================================
%% 📤 OUTBOUND INFLUENCE (REAL-WORLD ACTION)
%% =====================================================

subgraph OUTBOUND["📤 Outbound Influence Actions"]
direction TB

OUT_BRIEF["📨 Staff Briefing Delivered"]:::artifact
OUT_POINTS["🗣️ Talking Points Distributed"]:::artifact
OUT_PARTNER["🤝 Coalition Partner Activated"]:::artifact
OUT_MEDIA["📰 Narrative Seeded to Media"]:::artifact

end

%% Each thread produces outward pressure
THREAD_COMMITTEE --> OUT_BRIEF
THREAD_COMMITTEE --> OUT_POINTS
THREAD_COALITION --> OUT_PARTNER
THREAD_NARRATIVE --> OUT_MEDIA

%% Outbound actions generate signals
OUT_MEDIA --> EXEC_MONITOR
OUT_BRIEF --> EXEC_MONITOR
OUT_PARTNER --> EXEC_MONITOR


%% =====================================================
%% 📈 CAMPAIGN MOMENTUM (WHAT OPERATORS CARE ABOUT)
%% =====================================================

subgraph MOMENTUM["📈 Campaign Momentum Signals"]
direction TB

MOM_UP((⬆️ Momentum Building)):::system
MOM_FLAT((➡️ Momentum Stalling)):::system
MOM_DOWN((⬇️ Resistance Increasing)):::system

end

%% Signals derived from monitoring + scoring
EXEC_ALERT --> MOM_UP
EXEC_ALERT --> MOM_FLAT
EXEC_ALERT --> MOM_DOWN

%% Momentum informs retuning decisions
MOM_UP -.-> EXEC_RETUNE
MOM_FLAT -.-> EXEC_RETUNE
MOM_DOWN -.-> EXEC_RETUNE


%% =====================================================
%% 🚨 RARE HUMAN ESCALATION (STRATEGIC, NOT CLERICAL)
%% =====================================================

subgraph ESCALATION["🚨 Strategic Human Escalation (Rare)"]
direction TB

ESC_RISK{⚠️ High-Risk Political Sensitivity}:::decision
ESC_OVERRIDE{🎛️ Strategic Override Requested}:::decision

end

%% Only triggered under pressure
MOM_DOWN --> ESC_RISK
ESC_RISK --o ESC_OVERRIDE
ESC_OVERRIDE -.-> AVAQ
%% =====================================================
%% 💼 BUSINESS DEVELOPMENT LANE
%% Purpose: make value creation, partnerships, and ROI visible
%% Audience: business devs, industry stakeholders, execs
%% =====================================================

subgraph BIZDEV["💼 Business Development & Industry Value"]
direction TB

BD_SIGNAL("📡 Industry Demand Signal<br/>Market Pull Detected"):::system
BD_PARTNER("🤝 Strategic Partner Identified"):::human
BD_VALUE_MAP["💰 Value Proposition Mapping<br/>Jobs · Benefits · Risk Reduction"]:::artifact
BD_COMMIT["📝 Partner Commitment Secured"]:::artifact
BD_PIPELINE["📊 Opportunity Pipeline Impact"]:::data

end

%% Business development hooks into early + mid legislative stages
PRE_STAKEHOLDER_MAP -.-> BD_SIGNAL
BD_SIGNAL --> BD_PARTNER --> BD_VALUE_MAP --> BD_COMMIT --> BD_PIPELINE
BD_PIPELINE -.-> IMPL_OUTCOME


%% =====================================================
%% 📣 ADVOCACY & PRESSURE LANE
%% Purpose: show real-world lobbying force, friction, and counterforce
%% Audience: lobbyists, advocates, political operators
%% =====================================================

subgraph ADVOCACY["📣 Advocacy & Political Pressure Field"]
direction TB

ADV_BASE("👥 Constituent Base Activation"):::system
ADV_STAFF("🏛️ Staff-Level Advocacy<br/>Meetings · Briefings"):::system
ADV_MEMBER("🧑‍⚖️ Member-Level Persuasion<br/>Direct Influence"):::system
ADV_OPPOSE("🛑 Opposition Pressure Detected"):::system
ADV_COUNTER("🧯 Counter-Pressure Deployed"):::ai

end

%% Pressure attaches to spine without altering it
COMM_EVT -.-> ADV_STAFF
FLOOR_EVT -.-> ADV_MEMBER
ADV_BASE -.-> ADV_STAFF
ADV_STAFF --> ADV_MEMBER
ADV_MEMBER --> ADV_OPPOSE --> ADV_COUNTER
ADV_COUNTER -.-> EXEC_RETUNE


%% =====================================================
%% 🧑‍💻 SOFTWARE & SYSTEMS LANE
%% Purpose: make backend automation, reliability, and observability explicit
%% Audience: developers, architects, technical evaluators
%% =====================================================

subgraph SYSTEMS["🧑‍💻 Software Systems & Automation"]
direction TB

SYS_JOBS("⏱️ Background Jobs<br/>Schedulers · Workers"):::ai
SYS_EVENTS("📨 Event Bus<br/>Signals & Triggers"):::system
SYS_APIS("🔌 External APIs<br/>Data Providers · Media Feeds"):::system
SYS_OBS("📈 Observability<br/>Logs · Metrics · Traces"):::data
SYS_FAIL("🚨 Failure / Drift Detection"):::decision

end

%% Systems support AI services and execution loop
AI_INGEST --> SYS_APIS
SYS_APIS --> SYS_EVENTS --> SYS_JOBS --> AI_FEATURES
EXEC_RUN -.-> SYS_EVENTS
SYS_EVENTS --> SYS_OBS
SYS_OBS --> SYS_FAIL
SYS_FAIL --o EXEC_ALERT


%% =====================================================
%% 🧠 OPERATOR INTELLIGENCE LANE
%% Purpose: give users something to *study* when zoomed in
%% Audience: power users, strategists, analysts
%% =====================================================

subgraph OP_INTEL["🧠 Operator Intelligence & Signals"]
direction TB

INTEL_HEAT["🌡️ Influence Heatmap<br/>Where Effort Matters Most"]:::artifact
INTEL_VOL["📉 Volatility Index<br/>Position Drift · Risk"]:::artifact
INTEL_LEV["🪜 Leverage Score<br/>Effort → Impact Ratio"]:::artifact

end

EXEC_MONITOR --> INTEL_HEAT
EXEC_MONITOR --> INTEL_VOL
AI_SCORE --> INTEL_LEV
INTEL_LEV -.-> EXEC_TACTICS


%% =====================================================
%% 🔄 FEEDBACK INTO EXECUTION (LIGHT, CONTINUOUS MOTION)
%% =====================================================

INTEL_HEAT -.-> EXEC_RETUNE
INTEL_VOL -.-> EXEC_RETUNE
BD_PIPELINE -.-> EXEC_STRATEGY
ADV_OPPOSE -.-> EXEC_ALERT

%% =====================================================
%% 🧠 AI POLICY EXECUTION AGENT — PROFESSIONAL SERVICE FIELD
%% Purpose: make clear WHAT expertise the AI operationalizes
%% Audience: industry, regulators, academics, customers
%% =====================================================

subgraph AI_PROFESSIONALS["🧠 AI Policy Execution Agent — Professional Service Field"]
direction TB

%% =========================
%% POLICY & REGULATORY EXPERTISE
%% =========================
PRO_REG("⚖️ Regulatory Affairs Specialist"):::human
PRO_LEG("📜 Legislative Policy Analyst"):::human
PRO_COMPLY("🛡️ Compliance & Ethics Advisor"):::human
PRO_GOVREL("🏛️ Government Relations Lead"):::human

%% =========================
%% INDUSTRY & DOMAIN EXPERTISE
%% =========================
PRO_INDUSTRY("🏭 Industry Subject-Matter Expert"):::human
PRO_MARKET("📊 Market & Competitive Analyst"):::human
PRO_RISK("⚠️ Risk & Impact Assessor"):::human

%% =========================
%% COMMUNICATION & ADVOCACY
%% =========================
PRO_COMMS("🗣️ Strategic Communications Lead"):::human
PRO_MEDIA("📰 Media & Narrative Strategist"):::human
PRO_GRASS("👥 Grassroots Mobilization Lead"):::human

%% =========================
%% RESEARCH & VALIDATION
%% =========================
PRO_ACAD("🎓 Academic / Research Validator"):::human
PRO_DATA("📐 Policy Data Scientist"):::human

%% =========================
%% SYNTHESIZED EXECUTION CONTEXT
%% =========================
PRO_CONTEXT["📦 Professional Context Packets<br/>Precedent · Norms · Constraints · Best Practice"]:::artifact

end

%% Professionals inform context packets (standing guidance, not commands)
PRO_REG --> PRO_CONTEXT
PRO_LEG --> PRO_CONTEXT
PRO_COMPLY --> PRO_CONTEXT
PRO_GOVREL --> PRO_CONTEXT
PRO_INDUSTRY --> PRO_CONTEXT
PRO_MARKET --> PRO_CONTEXT
PRO_RISK --> PRO_CONTEXT
PRO_COMMS --> PRO_CONTEXT
PRO_MEDIA --> PRO_CONTEXT
PRO_GRASS --> PRO_CONTEXT
PRO_ACAD --> PRO_CONTEXT
PRO_DATA --> PRO_CONTEXT

%% Context packets inform the AI Policy Execution Agent
PRO_CONTEXT -.-> AI_CORE

%% Explicit linkage to early legislative cognition
PRO_CONTEXT -.-> PRE_SIGNAL_SCAN
PRO_CONTEXT -.-> PRE_STAKEHOLDER_MAP
PRO_CONTEXT -.-> PRE_CONCEPT


%% =====================================================
%% 🧭 CLARIFYING CALLOUT — WHAT THIS IS / IS NOT
%% Purpose: prevent misinterpretation by regulators & professionals
%% =====================================================

subgraph AI_CLARITY["🧭 Role Clarity (Non-Operational)"]
direction TB

CLARIFY_1["✅ AI Executes Within<br/>Professionally Defined Bounds"]:::artifact
CLARIFY_2["🚫 AI Does NOT Replace<br/>Licensed or Regulated Judgment"]:::artifact
CLARIFY_3["🔁 Human Expertise Is<br/>Upstream, Continuous, Auditable"]:::artifact

end

AI_CORE -.-> CLARIFY_1
AI_CORE -.-> CLARIFY_2
AI_CORE -.-> CLARIFY_3


%% =====================================================
%% 🔗 CONTINUITY INTO EXISTING GOVERNANCE
%% Purpose: visually tie professionals to formal governance
%% =====================================================

PRO_CONTEXT -.-> GUIDANCE
PRO_CONTEXT -.-> AUDIT

%% =====================================================
%% 🧠 AI POLICY EXECUTION AGENT — AGENT ORCHESTRATION MODEL (ADDITIVE)
%% Purpose:
%% - Make explicit that the Legislative Spine is the STATE MACHINE
%% - AI_CORE is the ORCHESTRATOR (not a worker)
%% - All other agents are SPAWNED, SCOPED, and RETIRED relative to state
%% Audience: Cursor agents, agent developers, advanced operators
%% =====================================================

%% -----------------------------------------------------
%% 🎛️ ORCHESTRATOR ROLE (CENTER OF GRAVITY)
%% -----------------------------------------------------

subgraph ORCHESTRATION["🎛️ Orchestrator Logic (Implicit, Always-On)"]
direction TB

ORCH_STATE["📍 Legislative State Cursor<br/>PRE · INTRO · COMM · FLOOR · FINAL · IMPL"]:::artifact
ORCH_PERMS["🔐 Action Permissions<br/>What Is Allowed *Now*"]:::artifact
ORCH_SPAWN["🧩 Agent Spawn Rules<br/>Who Can Be Instantiated"]:::artifact
ORCH_RETIRE["♻️ Agent Retirement Rules<br/>When Agents Terminate"]:::artifact

end

AI_CORE -.-> ORCH_STATE
AI_CORE -.-> ORCH_PERMS
AI_CORE -.-> ORCH_SPAWN
AI_CORE -.-> ORCH_RETIRE

%% State is driven ONLY by legislative spine
PRE_EVT --> ORCH_STATE
INTRO_EVT --> ORCH_STATE
COMM_EVT --> ORCH_STATE
FLOOR_EVT --> ORCH_STATE
FINAL_EVT --> ORCH_STATE
IMPL_EVT --> ORCH_STATE


%% -----------------------------------------------------
%% 🧩 AGENT SPAWN CATEGORIES (WHAT GETS CREATED)
%% -----------------------------------------------------

subgraph AGENT_TYPES["🧩 Spawned Agent Classes (Ephemeral)"]
direction TB

AG_INTEL["🔍 Intelligence Agents<br/>Observe · Summarize · Detect"]:::ai
AG_DRAFT["🧠 Drafting Agents<br/>Generate Artifacts"]:::ai
AG_EXEC["⚙️ Execution Agents<br/>World-Facing Actions"]:::ai
AG_LEARN["📐 Learning Agents<br/>Post-Hoc Attribution"]:::ai

end

ORCH_SPAWN -.-> AG_INTEL
ORCH_SPAWN -.-> AG_DRAFT
ORCH_SPAWN -.-> AG_EXEC
ORCH_SPAWN -.-> AG_LEARN


%% -----------------------------------------------------
%% 🔍 INTELLIGENCE AGENTS (READ-ONLY)
%% -----------------------------------------------------

subgraph INTEL_AGENTS["🔍 Intelligence Agents (Read-Only)"]
direction TB

INT_SIGNAL("📡 Signal Scan Agent"):::ai
INT_OPPOSE("🛑 Opposition Detection Agent"):::ai
INT_STAKE("🗺️ Stakeholder Mapping Agent"):::ai
INT_MEDIA("📰 Media Signal Monitor"):::ai

end

AG_INTEL --> INT_SIGNAL
AG_INTEL --> INT_OPPOSE
AG_INTEL --> INT_STAKE
AG_INTEL --> INT_MEDIA

INT_SIGNAL -.-> AI_INGEST
INT_OPPOSE -.-> EXEC_ALERT
INT_STAKE -.-> PRE_STAKEHOLDER_MAP
INT_MEDIA -.-> EXEC_MONITOR


%% -----------------------------------------------------
%% 🧠 DRAFTING AGENTS (PRODUCTIVE, GATED)
%% -----------------------------------------------------

subgraph DRAFT_AGENTS["🧠 Drafting Agents (Human-Gated)"]
direction TB

DR_MEMO("📄 Concept Memo Agent"):::ai
DR_LANG("📜 Legislative Language Agent"):::ai
DR_MSG("🗣️ Messaging Draft Agent"):::ai
DR_AMEND("✏️ Amendment Strategy Agent"):::ai

end

AG_DRAFT --> DR_MEMO
AG_DRAFT --> DR_LANG
AG_DRAFT --> DR_MSG
AG_DRAFT --> DR_AMEND

DR_MEMO --> PRE_CONCEPT
DR_LANG --> COMM_LANG
DR_MSG --> FLOOR_MEDIA
DR_AMEND --> COMM_AMEND

%% All drafting outputs route to human review
DR_MEMO -.-> HR_PRE
DR_LANG -.-> HR_LANG
DR_MSG -.-> HR_MSG
DR_AMEND -.-> HR_LANG


%% -----------------------------------------------------
%% ⚙️ EXECUTION AGENTS (WORLD-FACING, HIGH RISK)
%% -----------------------------------------------------

subgraph EXEC_AGENTS["⚙️ Execution Agents (Scoped & Timed)"]
direction TB

EX_OUTREACH("📨 Outreach Execution Agent"):::ai
EX_COAL("🤝 Coalition Activation Agent"):::ai
EX_MEDIA("📰 Media Seeding Agent"):::ai
EX_COUNTER("🧯 Counter-Pressure Agent"):::ai

end

AG_EXEC --> EX_OUTREACH
AG_EXEC --> EX_COAL
AG_EXEC --> EX_MEDIA
AG_EXEC --> EX_COUNTER

%% Execution agents operate ONLY via EXEC_RUN
EX_OUTREACH --> EXEC_RUN
EX_COAL --> EXEC_RUN
EX_MEDIA --> EXEC_RUN
EX_COUNTER --> EXEC_RUN

%% Execution agents are continuously monitored
EXEC_MONITOR --> EX_OUTREACH
EXEC_MONITOR --> EX_COAL
EXEC_MONITOR --> EX_MEDIA
EXEC_MONITOR --> EX_COUNTER


%% -----------------------------------------------------
%% 📐 LEARNING AGENTS (NON-INTERFERING)
%% -----------------------------------------------------

subgraph LEARN_AGENTS["📐 Learning Agents (Post-Hoc Only)"]
direction TB

LR_TACTIC("📊 Tactic Performance Learner"):::ai
LR_NARR("🗣️ Narrative Effectiveness Learner"):::ai
LR_ATTRIB("📈 Outcome Attribution Agent"):::ai

end

AG_LEARN --> LR_TACTIC
AG_LEARN --> LR_NARR
AG_LEARN --> LR_ATTRIB

LR_TACTIC --> MEM_TACTICS
LR_NARR --> MEM_NARRATIVE
LR_ATTRIB --> MEM_OUTCOMES

%% Learning never blocks execution
LR_TACTIC -.-> LEARN_UPDATE
LR_NARR -.-> LEARN_UPDATE
LR_ATTRIB -.-> LEARN_UPDATE


%% -----------------------------------------------------
%% ⛔ HARD SAFETY CONSTRAINTS (AGENT-LEVEL)
%% -----------------------------------------------------

subgraph AGENT_RULES["⛔ Non-Negotiable Agent Rules"]
direction TB

RULE_1["🚫 No Agent May Advance<br/>Legislative State"]:::artifact
RULE_2["🚫 No Agent May Self-Release<br/>Public Outputs"]:::artifact
RULE_3["🚫 No Agent Persists<br/>Beyond Its Scope"]:::artifact

end

AG_INTEL -.-> RULE_1
AG_DRAFT -.-> RULE_2
AG_EXEC -.-> RULE_2
AG_LEARN -.-> RULE_3


%% -----------------------------------------------------
%% ♻️ AGENT LIFECYCLE (VISUAL FEELING ANCHOR)
%% -----------------------------------------------------

subgraph AGENT_LIFECYCLE["♻️ Agent Lifecycle (Implicit Motion)"]
direction LR

LC_SPAWN((Spawn)):::system --> LC_WORK("Execute Task"):::ai --> LC_MON("Monitor"):::system --> LC_END((Terminate)):::system

end

ORCH_SPAWN -.-> LC_SPAWN
LC_END -.-> ORCH_RETIRE
%% =====================================================
%% 🤖 CURSOR AGENT INTERPRETATION & SPAWNING LAYER (ADDITIVE)
%% Purpose:
%% - Explain how a Cursor-style agent reads THIS diagram
%% - Show that the Legislative Spine is the backbone
%% - Show how AI_CORE spawns, scopes, and retires agents
%% This is a CONTROL PLANE, not execution logic
%% =====================================================

subgraph CURSOR_META["🧭 Cursor Agent — Diagram Interpretation Layer"]
direction TB

META_READ["👁️ Read System Topology<br/>Parse Subgraphs · States · Gates"]:::ai
META_BIND["🧩 Bind Legislative Spine<br/>as State Machine"]:::ai
META_ROLE["🎭 Identify Agent Roles<br/>Intel · Draft · Exec · Learn"]:::ai
META_PLAN["🗺️ Build Parallel Work Plan<br/>Based on Current State"]:::ai

end

%% Cursor agent reads the system
META_READ --> META_BIND --> META_ROLE --> META_PLAN

%% Cursor agent anchors on the spine
LEGISLATIVE -.-> META_BIND
META_BIND -.-> ORCH_STATE

%% =====================================================
%% 🧠 AI_CORE AS ORCHESTRATOR (INTERPRETED, NOT MANUAL)
%% =====================================================

subgraph CURSOR_ORCH["🎛️ Cursor-Controlled Orchestration"]
direction TB

CURSOR_DELEGATE["📤 Delegate Tasks<br/>to AI_CORE"]:::ai
CURSOR_MONITOR["👀 Observe Outcomes<br/>Without Direct Execution"]:::ai

end

META_PLAN --> CURSOR_DELEGATE --> AI_CORE
AI_CORE -.-> CURSOR_MONITOR

%% Cursor never bypasses AI_CORE
CURSOR_MONITOR -.-> ORCH_RETIRE

%% =====================================================
%% 🧩 AGENT TEMPLATE RESOLUTION (STATIC → DYNAMIC)
%% =====================================================

subgraph AGENT_TEMPLATES["📦 Agent Templates (From Diagram)"]
direction TB

TPL_INTEL["🔍 Intelligence Template"]:::artifact
TPL_DRAFT["🧠 Drafting Template"]:::artifact
TPL_EXEC["⚙️ Execution Template"]:::artifact
TPL_LEARN["📐 Learning Template"]:::artifact

end

META_ROLE --> TPL_INTEL
META_ROLE --> TPL_DRAFT
META_ROLE --> TPL_EXEC
META_ROLE --> TPL_LEARN

%% Templates resolve into live agents via AI_CORE
TPL_INTEL -.-> ORCH_SPAWN
TPL_DRAFT -.-> ORCH_SPAWN
TPL_EXEC -.-> ORCH_SPAWN
TPL_LEARN -.-> ORCH_SPAWN

%% =====================================================
%% 🕒 STATE-DRIVEN SPAWN LOGIC (NO HALLUCINATION)
%% =====================================================

subgraph STATE_RULES["📍 State → Agent Eligibility"]
direction TB

RULE_PRE["PRE_EVT → Intel + Draft"]:::artifact
RULE_COMM["COMM_EVT → Draft + Exec"]:::artifact
RULE_FLOOR["FLOOR_EVT → Exec + Monitor"]:::artifact
RULE_FINAL["FINAL_EVT → Exec + Learn"]:::artifact
RULE_IMPL["IMPL_EVT → Learn Only"]:::artifact

end

ORCH_STATE -.-> RULE_PRE
ORCH_STATE -.-> RULE_COMM
ORCH_STATE -.-> RULE_FLOOR
ORCH_STATE -.-> RULE_FINAL
ORCH_STATE -.-> RULE_IMPL

%% =====================================================
%% ⛔ CURSOR HARD LIMITS (IMPORTANT FOR SAFETY)
%% =====================================================

subgraph CURSOR_LIMITS["⛔ Cursor Agent Constraints"]
direction TB

CURSOR_NO_STATE["🚫 Cursor Cannot Advance<br/>Legislative State"]:::artifact
CURSOR_NO_EXEC["🚫 Cursor Cannot Execute<br/>World Actions"]:::artifact
CURSOR_NO_PUBLISH["🚫 Cursor Cannot Publish<br/>Externally"]:::artifact

end

META_READ -.-> CURSOR_NO_STATE
META_READ -.-> CURSOR_NO_EXEC
META_READ -.-> CURSOR_NO_PUBLISH

%% =====================================================
%% ♻️ FEEDBACK LOOP (DIAGRAM AS LIVING SPEC)
%% =====================================================

subgraph DIAGRAM_FEEDBACK["♻️ Diagram → Agent → Diagram"]
direction LR

FB_OBSERVE["👀 Observe Bottlenecks"]:::ai
FB_SUGGEST["💡 Suggest Diagram Changes"]:::ai
FB_HUMAN["👤 Human Accepts / Rejects"]:::decision

end

CURSOR_MONITOR --> FB_OBSERVE --> FB_SUGGEST --> FB_HUMAN
FB_HUMAN --o AVAQ
