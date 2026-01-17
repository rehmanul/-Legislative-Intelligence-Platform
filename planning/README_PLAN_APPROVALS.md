# Plan Approvals Tracking

This directory contains the plan approvals tracking system for mode transitions.

## File: `plan_approvals.jsonl`

JSONL (JSON Lines) file tracking human approvals for plans before AGENT mode execution.

### Format

Each line is a JSON object with the following structure:

```json
{
  "timestamp": "2026-01-20T12:00:00Z",
  "approval_type": "plan_approval",
  "plan_id": "replit_integration_governance_plan",
  "approved_by": "human:user_id",
  "status": "approved",
  "plan_path": "planning/replit_integration_plan_20260120_120000.md",
  "checklist_items_verified": [
    "Plan document exists",
    "File locations specified",
    "Naming conventions defined",
    "Schema validation rules defined",
    "Forbidden zones identified"
  ],
  "note": "Optional note from approver"
}
```

### Approval Status Values

- `pending`: Plan created, awaiting human approval
- `approved`: Plan approved, ready for AGENT mode
- `rejected`: Plan rejected, requires modification
- `revoked`: Previously approved plan revoked

### Usage

**Agent MUST check this file before executing in AGENT mode:**

1. Read `plan_approvals.jsonl`
2. Find most recent approval entry for plan
3. Verify `status` is `approved`
4. Verify `approval_type` matches current plan
5. Verify all required checklist items are present
6. If approval not found or status not `approved`, refuse execution

### Adding an Approval

Human adds approval by appending a line to this file:

```json
{"timestamp":"2026-01-20T14:00:00Z","approval_type":"plan_approval","plan_id":"replit_integration_governance_plan","approved_by":"human:operator","status":"approved","plan_path":"planning/replit_integration_plan_20260120_120000.md","checklist_items_verified":["all"],"note":"Plan approved for AGENT mode execution"}
```

### Security

- Only human operators may add approvals
- Agents may only READ this file (never modify)
- Approvals are append-only (no deletions or modifications)
- Each approval includes timestamp for audit trail
