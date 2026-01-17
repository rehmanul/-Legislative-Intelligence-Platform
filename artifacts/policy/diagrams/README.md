# Policy Artifacts Mermaid Diagrams

**Location:** `agent-orchestrator/artifacts/policy/diagrams/`  
**Purpose:** Visual representations of policy analysis artifacts

---

## Available Diagrams

### Overview Diagrams (Merged/Comprehensive)

#### **comprehensive_overview.mmd** ⭐ RECOMMENDED
**Visualizes:** Complete policy action plan in one view

**Combines:**
- Execution path selection
- All three paths with timelines
- Bill sections per path
- Stakeholder relationships
- Success metrics

**Use Case:** Best starting point - shows everything at once

---

#### **section_to_ask_flow.mmd**
**Visualizes:** Complete flow from bill sections to clear asks

**Shows:**
- Bill sections (Priority 1)
- Execution path mapping
- Engagement types
- Clear asks
- Target offices

**Use Case:** Understanding the complete engagement flow

---

#### **master_dashboard.mmd**
**Visualizes:** High-level dashboard view

**Shows:**
- All three paths side-by-side
- Stakeholder hierarchy
- Priority sections
- Success metrics

**Use Case:** Executive overview and quick reference

---

### Detailed Diagrams (Separate Views)

#### **stakeholder_hierarchy.mmd**
**Visualizes:** Stakeholder organizational structure and relationships

**Shows:**
- Congressional stakeholders (House/Senate committees)
- Department of Defense structure
- Service components (Army, Navy, Air Force)
- Implementing offices
- Three execution paths

**Use Case:** Understanding stakeholder relationships and engagement hierarchy

---

### 2. **90_day_timeline.mmd**
**Visualizes:** 90-day action plan timeline (Gantt chart)

**Shows:**
- Three execution paths in parallel
- Phase 1: Foundation/Program ID/Analysis (Days 1-30)
- Phase 2: Engagement/Proposal Development (Days 31-60)
- Phase 3: Implementation/Submission (Days 61-90)

**Use Case:** Planning and tracking progress across all three paths

---

### 3. **execution_paths_flowchart.mmd**
**Visualizes:** Decision tree and workflow for execution paths

**Shows:**
- Path selection decision point
- Three execution paths with phases
- Bill sections mapped to each path
- Success metrics

**Use Case:** Understanding path selection and phase progression

---

### 4. **section_priority_map.mmd**
**Visualizes:** Bill sections mapped to priorities and engagement types

**Shows:**
- Priority 1 sections (Days 1-30)
- Priority 2 sections (Days 31-60)
- Actionability scores (⭐⭐⭐⭐⭐)
- Engagement types (MILCON, ERCIP, SBIR/STTR, etc.)

**Use Case:** Prioritizing bill sections and identifying engagement opportunities

---

### 5. **clear_ask_decision_tree.mmd**
**Visualizes:** Decision tree for clear asks by execution path

**Shows:**
- Path selection
- Specific asks for each path
- Target offices
- Required proof/documentation

**Use Case:** Preparing for stakeholder engagement and identifying ask requirements

---

## Diagram Organization

### Recommended Usage

1. **Start with merged diagrams:**
   - `comprehensive_overview.mmd` - Full policy plan
   - `master_dashboard.mmd` - Executive summary
   - `section_to_ask_flow.mmd` - Engagement flow

2. **Use separate diagrams for:**
   - Detailed stakeholder analysis
   - Specific timeline planning
   - Focused decision trees

### When to Merge vs Separate

**Merge when:**
- You need to see relationships between elements
- Presenting to stakeholders (comprehensive view)
- Planning across multiple paths simultaneously

**Keep separate when:**
- Focusing on one specific aspect
- Detailed analysis of one component
- Creating focused presentations

---

## How to Use

### Viewing Diagrams

1. **In Markdown:** Diagrams can be embedded in markdown files using:
   ```markdown
   ```mermaid
   [diagram content]
   ```
   ```

2. **Standalone:** Open `.mmd` files in:
   - Mermaid Live Editor: https://mermaid.live
   - VS Code with Mermaid extension
   - Any Mermaid-compatible viewer

3. **Export:** Convert to PNG/SVG using:
   - Mermaid CLI: `mmdc -i diagram.mmd -o diagram.png`
   - Online tools: https://mermaid.live

### Updating Diagrams

- Edit `.mmd` files directly
- Follow existing patterns for consistency
- Test in Mermaid Live Editor before committing

---

## Diagram Conventions

### Color Coding
- **Green:** Start/End points, Success metrics
- **Blue:** Paths, Sections, Engagement types
- **Yellow:** Phases, Asks, Warnings
- **Gray:** Decision points, Neutral elements

### Layout
- **TB (Top-Bottom):** Hierarchical structures
- **LR (Left-Right):** Sequential flows
- **Dagre:** Automatic layout for complex graphs

---

## Source Data

All diagrams are derived from:
- `stakeholder_map.md` - Stakeholder hierarchy
- `action_plan.md` - Timeline and execution paths
- `section_priority_table.md` - Section mapping
- `clear_ask_matrix_p1.md` - Ask decision tree

---

**Note:** These diagrams are READ-ONLY POLICY CONTEXT per the system contract. They provide visual representations of strategic context only.

---

**End of Diagrams README**

*Generated: January 7, 2026*
