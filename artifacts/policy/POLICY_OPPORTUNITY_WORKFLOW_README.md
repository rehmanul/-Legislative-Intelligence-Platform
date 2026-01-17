# Policy Opportunity Workflow - Implementation Guide

**Status:** ✅ IMPLEMENTED  
**Date:** 2026-01-20  
**Purpose:** Automated workflow for policy opportunity analysis and artifact generation

---

## 🎯 Overview

This workflow automates the analysis and documentation of policy opportunities connecting wireless charging technology, risk mitigation, and insurable risks.

---

## 📋 Workflow Components

### 1. Intelligence Agent

**Agent:** `intel_policy_opportunity_analyzer_pre_evt.py`  
**Type:** Intelligence (Read-Only)  
**Purpose:** Analyzes policy opportunities from existing artifacts

**Inputs:**
- `artifacts/policy/WIRELESS_CHARGING_INSURABLE_RISK_POLICY_OPPORTUNITY.json`
- `artifacts/intel_risk/BILL_RISK_ANALYSIS_S_1071.json`

**Outputs:**
- `artifacts/intel_policy_opportunity_analyzer_pre_evt/POLICY_OPPORTUNITY_SUMMARY.json`

**Usage:**
```bash
python agents/intel_policy_opportunity_analyzer_pre_evt.py
```

---

### 2. Drafting Agent

**Agent:** `draft_policy_opportunity_document_pre_evt.py`  
**Type:** Drafting (Human-Gated)  
**Purpose:** Generates policy opportunity documents for human review

**Inputs:**
- `artifacts/intel_policy_opportunity_analyzer_pre_evt/POLICY_OPPORTUNITY_SUMMARY.json`
- `artifacts/policy/WIRELESS_CHARGING_INSURABLE_RISK_POLICY_OPPORTUNITY.json`

**Outputs:**
- `artifacts/draft_policy_opportunity_document_pre_evt/POLICY_OPPORTUNITY_DOCUMENT.json`
- Status: `WAITING_REVIEW` (HR_PRE)

**Usage:**
```bash
python agents/draft_policy_opportunity_document_pre_evt.py
```

---

### 3. Artifacts Index Generator

**Script:** `scripts/generate_policy_opportunity_artifacts.py`  
**Purpose:** Generates index of all policy opportunity artifacts

**Outputs:**
- `artifacts/policy/POLICY_OPPORTUNITY_ARTIFACTS_INDEX.json`

**Usage:**
```bash
python scripts/generate_policy_opportunity_artifacts.py
```

---

### 4. Workflow Automation

**Script:** `scripts/workflow_policy_opportunity_automation.py`  
**Purpose:** Automates the complete workflow execution

**Executes:**
1. Prerequisites check
2. Intelligence agent
3. Drafting agent
4. Artifacts index generation

**Usage:**
```bash
python scripts/workflow_policy_opportunity_automation.py
```

---

## 🚀 Quick Start

### Option 1: Run Complete Workflow

```bash
cd agent-orchestrator
python scripts/workflow_policy_opportunity_automation.py
```

### Option 2: Run Individual Components

```bash
# Step 1: Intelligence analysis
python agents/intel_policy_opportunity_analyzer_pre_evt.py

# Step 2: Document generation
python agents/draft_policy_opportunity_document_pre_evt.py

# Step 3: Generate index
python scripts/generate_policy_opportunity_artifacts.py
```

---

## 📁 Artifact Structure

### Input Artifacts (READ-ONLY)

- `artifacts/policy/WIRELESS_CHARGING_INSURABLE_RISK_POLICY_OPPORTUNITY.json`
- `artifacts/policy/WIRELESS_CHARGING_INSURABLE_RISK_POLICY_OPPORTUNITY.md`
- `artifacts/policy/WIRELESS_CHARGING_INSURABLE_RISK_STRATEGIC_PLAN.md`
- `artifacts/intel_risk/BILL_RISK_ANALYSIS_S_1071.json`

### Generated Artifacts

- `artifacts/intel_policy_opportunity_analyzer_pre_evt/POLICY_OPPORTUNITY_SUMMARY.json`
- `artifacts/draft_policy_opportunity_document_pre_evt/POLICY_OPPORTUNITY_DOCUMENT.json`
- `artifacts/policy/POLICY_OPPORTUNITY_ARTIFACTS_INDEX.json`

---

## 🔄 Workflow Status Tracking

The artifacts index tracks workflow status:

```json
{
  "workflow_status": {
    "opportunity_identified": true,
    "analysis_complete": true,
    "strategic_plan_ready": true,
    "agents_available": true
  }
}
```

---

## ✅ Success Criteria

- [ ] Intelligence agent generates summary successfully
- [ ] Drafting agent generates document successfully
- [ ] Artifacts index includes all artifacts
- [ ] Workflow automation completes without errors
- [ ] Generated artifacts follow schema requirements

---

## 📊 Integration with Strategic Plan

This workflow supports **Phase 1: Foundation & Coalition Building** of the strategic plan:

- **Legislative Drafting:** Agents can analyze and document policy opportunities
- **Stakeholder Mapping:** Artifacts provide stakeholder analysis
- **Actuarial Analysis:** Risk mitigation metrics included in artifacts
- **Documentation:** Automated document generation for review

---

## 🔗 Related Artifacts

- **Strategic Plan:** `WIRELESS_CHARGING_INSURABLE_RISK_STRATEGIC_PLAN.md`
- **Policy Opportunity:** `WIRELESS_CHARGING_INSURABLE_RISK_POLICY_OPPORTUNITY.md`
- **NDAA Analysis:** `artifacts/intel_risk/NDAA_ANALYSIS_INDEX.md`

---

**Last Updated:** 2026-01-20  
**Status:** ✅ IMPLEMENTED - Ready for Use
