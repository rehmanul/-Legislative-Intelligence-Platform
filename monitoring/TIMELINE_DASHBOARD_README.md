# Timeline Dashboard - Time-Horizon Focused Views

## Overview

The Timeline Dashboard provides focused views of work items organized by time horizon, aligned with the legislative timeline. This helps prioritize work based on urgency and legislative deadlines.

## Features

### Time Horizons

1. **Urgent (Next 48 Hours)**
   - Items requiring immediate action
   - Pending reviews blocking state advancement
   - Execution failures/retries
   - Blocked agents waiting on human decisions
   - Missing artifacts blocking progress

2. **Weekly (This Week)**
   - Work items scheduled for this week
   - Includes urgent items plus weekly planning items
   - Grouped by priority (HIGH/MEDIUM)

3. **Monthly (Strategic Planning)**
   - Long-term strategic view
   - State progression timeline
   - Multi-week initiatives
   - Resource planning

## Usage

### Command-Line Options

```bash
# View urgent items only
python monitoring/dashboard-timeline.py --horizon urgent

# View weekly items only
python monitoring/dashboard-timeline.py --horizon weekly

# View monthly strategic view
python monitoring/dashboard-timeline.py --horizon monthly

# View all horizons
python monitoring/dashboard-timeline.py --horizon all

# Generate Mermaid timeline chart
python monitoring/dashboard-timeline.py --mermaid
```

### Integration with Main Dashboard

The main dashboard (`dashboard-terminal.py`) now includes:
- Time horizon summary in the health section
- Urgent items section (if any)
- Automatic categorization of all work items

## How It Works

### Categorization Logic

Items are categorized based on:

1. **Age**: How long an item has been waiting
   - Reviews > 24 hours old → Urgent
   - Reviews < 7 days old → Weekly

2. **Blocking Status**: Items that block state advancement
   - Missing artifacts → Urgent
   - Pending reviews for critical gates (HR_PRE, HR_LANG) → Urgent

3. **Execution Status**: Agent execution health
   - Failed executions → Urgent
   - Retrying executions → Urgent

4. **State Progression**: Estimated time to next milestone
   - < 1 week → Weekly
   - 1-4 weeks → Monthly

### Item Types Tracked

- **Reviews**: Pending human review gates
- **Artifacts**: Missing required artifacts
- **Executions**: Agent execution status (running/retrying/failed)
- **Agents**: Agent lifecycle status (waiting/blocked)
- **State Advancement**: Progress toward target state

## Output Files

- **Timeline Chart**: `monitoring/timeline-chart.mmd` (when using `--mermaid`)
  - Gantt chart showing work items by horizon
  - Viewable in Mermaid Live Editor or VS Code

## Examples

### Urgent Dashboard Output

```
[URGENT] DASHBOARD - Next 48 Hours
================================================================================
Found 3 urgent item(s) requiring action within 48 hours:

[REVIEWS] PENDING REVIEWS (Blocking State Advancement)
--------------------------------------------------------------------------------
  • Concept Memo
    Gate: HR_PRE (Approve Concept Direction)
    Age: 25.3 hours
    File: artifacts/draft_concept_memo_pre_evt/PRE_CONCEPT.json
    Risk: MEDIUM
```

### Weekly Dashboard Output

```
[WEEKLY] DASHBOARD - This Week's Focus
================================================================================
This week's work: 5 item(s)

[HIGH] HIGH PRIORITY (This Week)
--------------------------------------------------------------------------------
  • Review: Policy Framing (HR_PRE)
    Age: 12.5 hours
  • Missing artifact: Policy Whitepaper
```

### Monthly Dashboard Output

```
[MONTHLY] DASHBOARD - Strategic Planning
================================================================================
Monthly overview: 8 total item(s)
  - Urgent: 2
  - Weekly: 3
  - Monthly: 3

[TIMELINE] STRATEGIC TIMELINE
--------------------------------------------------------------------------------
Current State: INTRO_EVT
Target State: COMM_EVT
States Remaining: 1

  → INTRO_EVT (CURRENT)
     Shaping legitimacy and framing. No outreach or execution has begun.
  [TARGET] COMM_EVT (TARGET)
```

## Integration with Legislative Timeline

The dashboards align work items with legislative states:

- **PRE_EVT → INTRO_EVT**: Concept approval, framing preparation
- **INTRO_EVT → COMM_EVT**: Policy whitepaper, sponsor targeting
- **COMM_EVT → FLOOR_EVT**: Legislative language, committee briefings
- **FLOOR_EVT → FINAL_EVT**: Floor messaging, vote coordination

Each state transition has associated work items that are tracked and prioritized by time horizon.

## Best Practices

1. **Daily**: Check urgent dashboard for immediate action items
2. **Weekly**: Review weekly dashboard for planning
3. **Monthly**: Use monthly dashboard for strategic planning
4. **Before State Transitions**: Check all horizons to ensure readiness

## Future Enhancements

- Integration with external legislative calendar APIs
- Deadline tracking for committee hearings and votes
- Automated reminders for approaching deadlines
- Historical trend analysis
