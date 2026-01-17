# Phase 2 Execution Flow - Mermaid Diagram

```mermaid
flowchart TB
    Start([Agent Started]) --> LoadArtifacts[Load Artifacts]
    
    LoadArtifacts --> StakeholderMap[Load Stakeholder Map]
    LoadArtifacts --> BriefingPacket[Load Committee Briefing]
    
    StakeholderMap --> IdentifyTargets[Identify Outreach Targets]
    BriefingPacket --> IdentifyTargets
    
    IdentifyTargets --> Target1[Target 1: Senator Johnson's Office<br/>Priority: High]
    IdentifyTargets --> Target2[Target 2: Rep Martinez's Office<br/>Priority: High]
    IdentifyTargets --> Target3[Target 3: Energy Innovation Alliance<br/>Priority: High]
    IdentifyTargets --> Target4[Target 4: Clean Energy Coalition<br/>Priority: Medium]
    
    Target1 --> CreateContact1[Create Contact in Contact Manager]
    Target2 --> CreateContact2[Create Contact in Contact Manager]
    Target3 --> CreateContact3[Create Contact in Contact Manager]
    Target4 --> CreateContact4[Create Contact in Contact Manager]
    
    CreateContact1 --> GenerateEmail1[Generate Email Content<br/>from Briefing Packet]
    CreateContact2 --> GenerateEmail2[Generate Email Content<br/>from Briefing Packet]
    CreateContact3 --> GenerateEmail3[Generate Email Content<br/>from Briefing Packet]
    CreateContact4 --> GenerateEmail4[Generate Email Content<br/>from Briefing Packet]
    
    GenerateEmail1 --> CreateRequest1[Create Execution Request 1]
    GenerateEmail2 --> CreateRequest2[Create Execution Request 2]
    GenerateEmail3 --> CreateRequest3[Create Execution Request 3]
    GenerateEmail4 --> CreateRequest4[Create Execution Request 4]
    
    CreateRequest1 --> LogActivity1[Log: execution_requested]
    CreateRequest2 --> LogActivity2[Log: execution_requested]
    CreateRequest3 --> LogActivity3[Log: execution_requested]
    CreateRequest4 --> LogActivity4[Log: execution_requested]
    
    LogActivity1 --> SubmitApproval1[Submit to Approval Manager<br/>HR_LANG Gate]
    LogActivity2 --> SubmitApproval2[Submit to Approval Manager<br/>HR_LANG Gate]
    LogActivity3 --> SubmitApproval3[Submit to Approval Manager<br/>HR_LANG Gate]
    LogActivity4 --> SubmitApproval4[Submit to Approval Manager<br/>HR_LANG Gate]
    
    SubmitApproval1 --> ApprovalQueue[Approval Queue<br/>Status: PENDING]
    SubmitApproval2 --> ApprovalQueue
    SubmitApproval3 --> ApprovalQueue
    SubmitApproval4 --> ApprovalQueue
    
    ApprovalQueue --> CheckApproval{Check Approval Status}
    
    CheckApproval -->|Not Approved| PendingState[Status: PENDING_APPROVAL<br/>4 requests waiting]
    CheckApproval -->|Approved| ExecuteApproved[Execute Approved Requests]
    
    ExecuteApproved --> ValidateEmail[Validate Email Content]
    ValidateEmail --> DryRunCheck{DRY_RUN_MODE?}
    
    DryRunCheck -->|True| LogDryRun[Log to dry-run-log.jsonl<br/>No actual email sent]
    DryRunCheck -->|False| SendEmail[Send via SMTP<br/>Phase 2: Blocked]
    
    LogDryRun --> LogExecuted[Log: execution_executed]
    SendEmail --> LogExecuted
    
    LogExecuted --> UpdateContacts[Mark Contacts as Contacted]
    UpdateContacts --> GeneratePlan[Generate Execution Plan Artifact]
    
    GeneratePlan --> End([Execution Complete])
    PendingState --> End
    
    style Start fill:#e1f5ff
    style End fill:#d4edda
    style ApprovalQueue fill:#fff3cd
    style PendingState fill:#fff3cd
    style LogDryRun fill:#d1ecf1
    style ExecuteApproved fill:#d4edda
```

## Execution Flow Summary

### Phase 1: Artifact Loading
- Loaded stakeholder map (4 stakeholders)
- Loaded committee briefing packet

### Phase 2: Target Identification
- Identified 4 outreach targets
- Prioritized by alignment (allies first)
- Created contacts in contact manager

### Phase 3: Email Generation
- Generated personalized email content for each target
- Used briefing packet data for email body
- Included key points, agenda items, and asks

### Phase 4: Execution Request Creation
- Created 4 ExecutionRequest objects
- Set review gate: HR_LANG
- Set dry_run: True
- Set requires_approval: True

### Phase 5: Approval Submission
- Submitted all 4 requests to approval manager
- Logged execution_requested events
- Added to approval queue (status: PENDING)

### Phase 6: Approval Check
- Checked approval status (0 approved, 4 pending)
- No executions yet (awaiting human approval)

### Phase 7: Output Generation
- Generated execution plan artifact
- Documented all requests and status
- Ready for human review

## Current State

**Status:** PENDING_APPROVAL  
**Pending Requests:** 4  
**Approved Requests:** 0  
**Executed Requests:** 0  
**Dry-Run Mode:** Active (no emails sent)
