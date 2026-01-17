# Dashboard Quick Start Guide

## Quick Commands

### Main Dashboard
```bash
cd agent-orchestrator
python monitoring/dashboard-terminal.py
```

### Timeline Dashboards
```bash
# Urgent items (next 48h)
python monitoring/dashboard-timeline.py --horizon urgent

# Weekly view
python monitoring/dashboard-timeline.py --horizon weekly

# Monthly strategic view
python monitoring/dashboard-timeline.py --horizon monthly

# All horizons
python monitoring/dashboard-timeline.py --horizon all
```

### Generate Charts
```bash
# Main dashboard chart
python monitoring/dashboard-terminal.py --mermaid

# Timeline chart
python monitoring/dashboard-timeline.py --mermaid
```

### Cleanup
```bash
# Clean agent registry (removes duplicates, marks stale agents)
python scripts/cleanup__agent_registry.py
```

## File Locations

### Dashboards
- Main: `monitoring/dashboard-terminal.py`
- Timeline: `monitoring/dashboard-timeline.py`

### Generated Charts
- Main: `monitoring/dashboard-status.mmd`
- Timeline: `monitoring/timeline-chart.mmd`

### Documentation
- User Guide: `monitoring/TIMELINE_DASHBOARD_README.md`
- Implementation: `monitoring/DASHBOARD_IMPLEMENTATION_SUMMARY.md`
- Quick Start: `monitoring/QUICK_START.md` (this file)

## What Each Dashboard Shows

### Main Dashboard
- System health summary
- Human decisions required
- State progression map
- Artifact completeness
- Execution status
- Agent lifecycle
- Recent events
- Time horizon priorities

### Timeline Dashboard - Urgent
- Pending reviews (>24h or critical gates)
- Missing artifacts (blocking progress)
- Execution failures/retries
- Blocked agents (>24h waiting)

### Timeline Dashboard - Weekly
- All urgent items
- Weekly planning items
- Grouped by priority (HIGH/MEDIUM)

### Timeline Dashboard - Monthly
- Strategic overview
- State progression timeline
- Multi-week initiatives
- Resource planning

## Viewing Mermaid Charts

1. **Mermaid Live Editor**: https://mermaid.live
   - Copy contents of `.mmd` file
   - Paste into editor
   - View rendered chart

2. **VS Code**: Install "Markdown Preview Mermaid Support" extension
   - Open `.mmd` file
   - Preview with extension

3. **GitHub**: Commit `.mmd` files
   - GitHub renders Mermaid automatically
   - View in repository

## Common Workflows

### Daily Check
```bash
# Check urgent items
python monitoring/dashboard-timeline.py --horizon urgent
```

### Weekly Planning
```bash
# Review weekly work
python monitoring/dashboard-timeline.py --horizon weekly
```

### Strategic Review
```bash
# Monthly strategic view
python monitoring/dashboard-timeline.py --horizon monthly
```

### Full Status
```bash
# Complete dashboard
python monitoring/dashboard-terminal.py
```

### Generate Visualizations
```bash
# Generate all charts
python monitoring/dashboard-terminal.py --mermaid
python monitoring/dashboard-timeline.py --mermaid
```
