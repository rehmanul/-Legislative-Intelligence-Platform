# Agent Integration Guide: Policy Artifacts

**Purpose:** Guide for agents to properly reference READ-ONLY POLICY CONTEXT artifacts

---

## 🎯 Quick Reference

```python
# ✅ CORRECT: Reading policy artifacts
POLICY_DIR = BASE_DIR / "artifacts" / "policy"

def load_policy_context():
    """Load policy artifacts as READ-ONLY context"""
    key_findings = (POLICY_DIR / "key_findings.md").read_text()
    stakeholder_map = (POLICY_DIR / "stakeholder_map.md").read_text()
    return {
        "key_findings": key_findings,
        "stakeholder_map": stakeholder_map,
        "source": "artifacts/policy/ (READ-ONLY POLICY CONTEXT)"
    }

# ❌ WRONG: Treating policy as executable
# DO NOT create agents from policy content
# DO NOT execute actions based on policy documents
```

---

## 📋 Agent Requirements

### When Referencing Policy Artifacts

**1. Declare READ-ONLY Usage**
```python
"""
Agent: example_agent
Uses READ-ONLY POLICY CONTEXT from artifacts/policy/
References: key_findings.md, stakeholder_map.md
Purpose: Background context only, not executable instructions
"""
```

**2. Identify Specific Sections**
```python
# ✅ Good: Specific reference
policy_context = {
    "source": "artifacts/policy/key_findings.md",
    "section": "Policy Opportunities → Opportunity 1: Defense Facility Infrastructure",
    "usage": "Background context for stakeholder identification"
}

# ❌ Bad: Vague reference
policy_context = {
    "source": "policy stuff",  # Too vague
    "usage": "general reference"  # Not specific
}
```

**3. Require Human Approval for Actionable Outputs**
```python
def generate_output(policy_context):
    """Generate output that references policy"""
    output = {
        "content": "...",
        "policy_references": [
            {
                "document": "artifacts/policy/stakeholder_map.md",
                "section": "Path 1: Defense Facility Infrastructure",
                "usage": "Stakeholder identification"
            }
        ],
        "requires_human_approval": True,  # ← REQUIRED
        "approval_reason": "Output references policy context and may require validation"
    }
    return output
```

---

## 🔍 Finding Policy Information

### By Use Case

**Need Stakeholders?**
```python
POLICY_DIR = BASE_DIR / "artifacts" / "policy"
stakeholder_map = (POLICY_DIR / "stakeholder_map.md").read_text()
# Search for execution path or section
```

**Need Talking Points?**
```python
talking_points = (POLICY_DIR / "talking_points.md").read_text()
# Format: Authority → Action → Outcome
```

**Need Section Mapping?**
```python
section_table = (POLICY_DIR / "section_priority_table.md").read_text()
# Maps sections to execution paths and priorities
```

**Need Quick Overview?**
```python
quick_ref = (POLICY_DIR / "QUICK_REFERENCE.md").read_text()
key_findings = (POLICY_DIR / "key_findings.md").read_text()
```

---

## ✅ Allowed Agent Patterns

### Pattern 1: Intelligence Agent Reading Policy
```python
"""
Intelligence Agent: Reads policy for context
"""
def analyze_opportunity():
    # Read policy as background
    policy = load_policy_context()
    
    # Use for analysis (read-only)
    analysis = {
        "findings": "...",
        "policy_context": "Derived from artifacts/policy/key_findings.md",
        "status": "READ_ONLY_CONTEXT"
    }
    return analysis
```

### Pattern 2: Drafting Agent Referencing Policy
```python
"""
Drafting Agent: References policy in draft
"""
def draft_document():
    # Reference policy in draft
    policy_refs = load_policy_context()
    
    draft = {
        "content": "...",
        "references": [
            {
                "type": "READ_ONLY_POLICY_CONTEXT",
                "source": "artifacts/policy/stakeholder_map.md",
                "section": "Path 1 stakeholders",
                "usage": "Stakeholder identification"
            }
        ],
        "human_review_required": True
    }
    return draft
```

### Pattern 3: Validation Against Policy
```python
"""
Validation: Check consistency with policy intent
"""
def validate_against_policy(proposed_action):
    policy = load_policy_context()
    
    # Check if proposed action aligns with policy
    # DO NOT execute, only validate
    validation = {
        "aligned": True/False,
        "policy_reference": "artifacts/policy/action_plan.md",
        "recommendation": "Human review required"
    }
    return validation
```

---

## 🚫 Prohibited Patterns

### ❌ DO NOT: Execute Based on Policy
```python
# ❌ WRONG
def execute_from_policy():
    policy = load_policy_context()
    # DO NOT execute actions from policy
    # DO NOT create execution agents from policy
    # DO NOT trigger workflows from policy
    pass
```

### ❌ DO NOT: Modify Policy Files
```python
# ❌ WRONG
def update_policy():
    policy_file = POLICY_DIR / "key_findings.md"
    policy_file.write_text("...")  # FORBIDDEN
    pass
```

### ❌ DO NOT: Treat Policy as Instructions
```python
# ❌ WRONG
def follow_policy_plan():
    policy = load_policy_context()
    # DO NOT treat "Action Plan" as executable
    # DO NOT treat "Next Steps" as commands
    # DO NOT treat "Engagement Strategy" as permissions
    pass
```

---

## 📊 Policy Artifact Reference Table

| Agent Need | Policy Document | Section/Use |
|------------|----------------|-------------|
| **Stakeholder List** | `stakeholder_map.md` | Execution path sections |
| **Talking Points** | `talking_points.md` | Path A/B/C sections |
| **Section Mapping** | `section_priority_table.md` | Priority tables |
| **Executive Summary** | `key_findings.md` | Executive summary |
| **90-Day Plan** | `action_plan.md` | Execution paths |
| **Clear Asks** | `clear_ask_matrix_p1.md` | Matrix table |
| **One-Pager** | `staff_one_pager_p1.md` | Full document |
| **Quick Navigation** | `QUICK_REFERENCE.md` | Use case guides |
| **Complete Index** | `INDEX.md` | Document relationships |

---

## 🔗 Integration Examples

### Example 1: Intelligence Agent
```python
"""
Intelligence Agent: Signal Scan
Uses: artifacts/policy/key_findings.md (background context)
"""
AGENT_ID = "intel_signal_scan_pre_evt"
POLICY_DIR = BASE_DIR / "artifacts" / "policy"

def main():
    # Load policy context (read-only)
    key_findings = (POLICY_DIR / "key_findings.md").read_text()
    
    # Use for context, not execution
    log_event("policy_context_loaded", {
        "source": "artifacts/policy/key_findings.md",
        "usage": "Background context for signal analysis",
        "status": "READ_ONLY"
    })
    
    # Agent logic...
    return output
```

### Example 2: Drafting Agent
```python
"""
Drafting Agent: Concept Memo
References: artifacts/policy/stakeholder_map.md
"""
AGENT_ID = "draft_concept_memo_pre_evt"
POLICY_DIR = BASE_DIR / "artifacts" / "policy"

def main():
    # Reference policy in artifact
    stakeholder_map = (POLICY_DIR / "stakeholder_map.md").read_text()
    
    artifact = {
        "_meta": {
            "agent_id": AGENT_ID,
            "policy_references": [
                {
                    "document": "artifacts/policy/stakeholder_map.md",
                    "section": "Path 1: Defense Facility Infrastructure",
                    "usage": "Stakeholder identification",
                    "status": "READ_ONLY_CONTEXT"
                }
            ],
            "human_review_required": True
        },
        "content": "..."
    }
    return artifact
```

---

## 🛡️ Safety Checklist

Before using policy artifacts, verify:

- [ ] Agent declares READ-ONLY POLICY CONTEXT usage
- [ ] Specific documents/sections are identified
- [ ] Usage is clearly labeled as "background context"
- [ ] No execution actions are derived from policy
- [ ] Human approval required for actionable outputs
- [ ] Policy references are documented in artifact `_meta`

---

## 📚 Related Documentation

- **Contract:** See `README.md` → SYSTEM CONTRACT
- **Quick Reference:** See `QUICK_REFERENCE.md`
- **Complete Index:** See `INDEX.md`
- **Validation:** Run `scripts/validate_policy_contract.py`

---

**End of Agent Integration Guide**

*For questions, see README.md or review existing agent implementations*
