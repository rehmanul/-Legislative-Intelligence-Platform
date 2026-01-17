"""
Timeline Dashboard - Time-Horizon Focused Views
Provides urgent, weekly, and monthly work views aligned with legislative timeline
"""

import json
import sys
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Import functions from main dashboard
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / "app"))
sys.path.insert(0, str(BASE_DIR / "monitoring"))

# Import from dashboard-terminal module using importlib
import importlib.util
dashboard_path = BASE_DIR / "monitoring" / "dashboard-terminal.py"
spec = importlib.util.spec_from_file_location("dashboard_terminal_module", dashboard_path)
dashboard_terminal_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dashboard_terminal_module)

# Import needed functions
load_dashboard_data = dashboard_terminal_module.load_dashboard_data
load_goal = dashboard_terminal_module.load_goal
load_pending_reviews = dashboard_terminal_module.load_pending_reviews
load_execution_status = dashboard_terminal_module.load_execution_status
categorize_by_time_horizon = dashboard_terminal_module.categorize_by_time_horizon
translate_state_to_meaning = dashboard_terminal_module.translate_state_to_meaning
format_duration = dashboard_terminal_module.format_duration
parse_timestamp = dashboard_terminal_module.parse_timestamp
compute_goal_progress = dashboard_terminal_module.compute_goal_progress

def render_urgent_dashboard(data, time_horizons, goal_progress=None):
    """Render urgent items dashboard (next 48 hours)"""
    print("=" * 80)
    print("[URGENT] DASHBOARD - Next 48 Hours")
    print("=" * 80)
    print(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print()
    
    urgent_items = time_horizons.get("urgent", [])
    
    if not urgent_items:
        print("[OK] No urgent items requiring immediate attention.")
        print()
        print("System is operating normally. All items are within acceptable timeframes.")
        return
    
    print(f"Found {len(urgent_items)} urgent item(s) requiring action within 48 hours:\n")
    
    # Group by type
    reviews = [i for i in urgent_items if i.get("type") == "review"]
    artifacts = [i for i in urgent_items if i.get("type") == "artifact"]
    executions = [i for i in urgent_items if i.get("type") == "execution"]
    agents = [i for i in urgent_items if i.get("type") == "agent"]
    state_adv = [i for i in urgent_items if i.get("type") == "state_advancement"]
    
    # Reviews
    if reviews:
        print("[REVIEWS] PENDING REVIEWS (Blocking State Advancement)")
        print("-" * 80)
        for item in reviews:
            review = item.get("item", {})
            age_hours = item.get("age_hours", 0)
            print(f"\n  • {review.get('artifact_name', 'Unknown Artifact')}")
            print(f"    Gate: {review.get('gate_name', 'Unknown')} ({review.get('gate_id', 'UNKNOWN')})")
            print(f"    Age: {age_hours:.1f} hours")
            print(f"    File: {review.get('artifact_path', 'Path not available')}")
            if review.get("risk_level"):
                print(f"    Risk: {review.get('risk_level')}")
    
    # Missing Artifacts
    if artifacts:
        print("\n[ARTIFACTS] MISSING ARTIFACTS (Blocking Progress)")
        print("-" * 80)
        for item in artifacts:
            artifact = item.get("item", "Unknown")
            print(f"  • {artifact}")
            print(f"    Status: Required for state advancement")
    
    # Execution Failures
    if executions:
        print("\n⚙️ EXECUTION ISSUES (Requiring Attention)")
        print("-" * 80)
        for item in executions:
            exec_item = item.get("item", {})
            agent_id = exec_item.get("agent_id", "unknown")
            status = exec_item.get("status", "unknown")
            attempt = exec_item.get("attempt", 0)
            max_retries = exec_item.get("max_retries", 5)
            error = item.get("error", "Unknown error")
            
            print(f"\n  • {agent_id}")
            print(f"    Status: {status}")
            print(f"    Attempt: {attempt}/{max_retries}")
            if error:
                print(f"    Error: {error}")
    
    # Blocked Agents
    if agents:
        print("\n[AGENTS] BLOCKED AGENTS (Waiting on Human)")
        print("-" * 80)
        for item in agents:
            agent = item.get("item", {})
            agent_id = agent.get("agent_id", "unknown")
            status = agent.get("status", "unknown")
            task = agent.get("current_task", "N/A")
            age_hours = item.get("age_hours", 0)
            
            print(f"\n  • {agent_id}")
            print(f"    Status: {status}")
            print(f"    Task: {task}")
            print(f"    Waiting: {age_hours:.1f} hours")
    
    # State Advancement
    if state_adv:
        print("\n🧭 STATE ADVANCEMENT (Critical Path)")
        print("-" * 80)
        for item in state_adv:
            state_info = item.get("item", {})
            current = state_info.get("current", "UNKNOWN")
            target = state_info.get("target", "UNKNOWN")
            print(f"  • {current} → {target}")
            print(f"    Current: {translate_state_to_meaning(current)}")
            print(f"    Target: {translate_state_to_meaning(target)}")
    
    print("\n" + "=" * 80)
    print("ACTION REQUIRED: Address these items to unblock workflow progress")
    print("=" * 80)

def render_weekly_dashboard(data, time_horizons, goal_progress=None):
    """Render weekly work dashboard (this week)"""
    print("=" * 80)
    print("[WEEKLY] DASHBOARD - This Week's Focus")
    print("=" * 80)
    print(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print()
    
    weekly_items = time_horizons.get("weekly", [])
    urgent_items = time_horizons.get("urgent", [])
    
    # Include urgent items in weekly view
    all_weekly = urgent_items + weekly_items
    
    if not all_weekly:
        print("[OK] No items scheduled for this week.")
        print()
        print("Focus on strategic planning and long-term preparation.")
        return
    
    print(f"This week's work: {len(all_weekly)} item(s)\n")
    
    # Group by priority
    high_priority = [i for i in all_weekly if i.get("priority") == "HIGH"]
    medium_priority = [i for i in all_weekly if i.get("priority") == "MEDIUM"]
    
    if high_priority:
        print("[HIGH] HIGH PRIORITY (This Week)")
        print("-" * 80)
        for item in high_priority[:10]:
            print(f"  • {item.get('description', 'Unknown item')}")
            if item.get("age_hours"):
                print(f"    Age: {item['age_hours']:.1f} hours")
    
    if medium_priority:
        print("\n[MEDIUM] MEDIUM PRIORITY (This Week)")
        print("-" * 80)
        for item in medium_priority[:10]:
            print(f"  • {item.get('description', 'Unknown item')}")
            if item.get("estimated_weeks"):
                print(f"    Estimated: {item['estimated_weeks']} weeks")
    
    print("\n" + "=" * 80)
    print("WEEKLY FOCUS: Complete high-priority items to maintain momentum")
    print("=" * 80)

def render_monthly_dashboard(data, time_horizons, goal_progress=None):
    """Render monthly strategic dashboard"""
    print("=" * 80)
    print("[MONTHLY] DASHBOARD - Strategic Planning")
    print("=" * 80)
    print(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print()
    
    monthly_items = time_horizons.get("monthly", [])
    weekly_items = time_horizons.get("weekly", [])
    urgent_items = time_horizons.get("urgent", [])
    
    # Include all items in monthly view
    all_monthly = urgent_items + weekly_items + monthly_items
    
    if not all_monthly:
        print("[OK] No items planned for this month.")
        return
    
    print(f"Monthly overview: {len(all_monthly)} total item(s)")
    print(f"  - Urgent: {len(urgent_items)}")
    print(f"  - Weekly: {len(weekly_items)}")
    print(f"  - Monthly: {len(monthly_items)}")
    print()
    
    # Group by type for strategic view
    by_type = {}
    for item in all_monthly:
        item_type = item.get("type", "unknown")
        if item_type not in by_type:
            by_type[item_type] = []
        by_type[item_type].append(item)
    
    for item_type, items in sorted(by_type.items()):
        type_names = {
            "review": "[REVIEWS] Reviews",
            "artifact": "[ARTIFACTS] Artifacts",
            "execution": "[EXECUTION] Executions",
            "agent": "[AGENTS] Agents",
            "state_advancement": "[STATE] State Advancement"
        }
        print(f"{type_names.get(item_type, item_type.upper())} ({len(items)})")
        print("-" * 80)
        for item in items[:5]:
            print(f"  • {item.get('description', 'Unknown item')}")
        if len(items) > 5:
            print(f"  ... and {len(items) - 5} more")
        print()
    
    # State progression timeline
    if goal_progress:
        current_state = goal_progress.get("current_state", "UNKNOWN")
        target_state = goal_progress.get("target_state", "UNKNOWN")
        
        print("[TIMELINE] STRATEGIC TIMELINE")
        print("-" * 80)
        state_sequence = ["PRE_EVT", "INTRO_EVT", "COMM_EVT", "FLOOR_EVT", "FINAL_EVT", "IMPL_EVT"]
        try:
            current_idx = state_sequence.index(current_state)
            target_idx = state_sequence.index(target_state)
            
            print(f"Current State: {current_state}")
            print(f"Target State: {target_state}")
            print(f"States Remaining: {target_idx - current_idx}")
            print()
            
            for i, s in enumerate(state_sequence):
                if i == current_idx:
                    marker = "→"
                    status = "CURRENT"
                elif i < current_idx:
                    marker = "✓"
                    status = "COMPLETE"
                elif i == target_idx:
                    marker = "[TARGET]"
                    status = "TARGET"
                else:
                    marker = " "
                    status = "FUTURE"
                
                print(f"  {marker} {s} ({status})")
                if i == current_idx:
                    print(f"     {translate_state_to_meaning(s)}")
        except ValueError:
            pass
    
    print("\n" + "=" * 80)
    print("STRATEGIC FOCUS: Plan for multi-week initiatives and dependencies")
    print("=" * 80)

def generate_timeline_mermaid(time_horizons, goal_progress=None):
    """Generate Mermaid timeline chart"""
    lines = []
    lines.append("---")
    lines.append("config:")
    lines.append("  layout: dagre")
    lines.append("  theme: default")
    lines.append("---")
    lines.append("gantt")
    lines.append("    title Legislative Timeline - Work Items by Horizon")
    lines.append("    dateFormat YYYY-MM-DD")
    lines.append("    section Urgent")
    
    urgent_items = time_horizons.get("urgent", [])
    for i, item in enumerate(urgent_items[:5]):
        desc = item.get("description", "Item")[:30]
        lines.append(f"    {desc} :urgent{i}, 2026-01-07, 2d")
    
    lines.append("    section Weekly")
    weekly_items = time_horizons.get("weekly", [])
    for i, item in enumerate(weekly_items[:5]):
        desc = item.get("description", "Item")[:30]
        lines.append(f"    {desc} :weekly{i}, 2026-01-07, 7d")
    
    lines.append("    section Monthly")
    monthly_items = time_horizons.get("monthly", [])
    for i, item in enumerate(monthly_items[:5]):
        desc = item.get("description", "Item")[:30]
        estimated_weeks = item.get("estimated_weeks", 4)
        lines.append(f"    {desc} :monthly{i}, 2026-01-07, {estimated_weeks * 7}d")
    
    return "\n".join(lines)

def main():
    """Main timeline dashboard entry point"""
    parser = argparse.ArgumentParser(description="Timeline Dashboard - Time-horizon focused views")
    parser.add_argument("--horizon", choices=["urgent", "weekly", "monthly", "all"], 
                       default="all", help="Time horizon to display")
    parser.add_argument("--mermaid", action="store_true", help="Generate Mermaid timeline chart")
    args = parser.parse_args()
    
    # Load data
    print("Loading dashboard data...", end="", flush=True)
    data = load_dashboard_data()
    goal = load_goal()
    pending_reviews = load_pending_reviews()
    execution_status = data.get("execution_status")
    
    print(" [OK]")
    
    # Compute goal progress
    goal_progress = None
    if goal and "state" in data and "dashboard" in data:
        goal_progress = compute_goal_progress(
            state=data["state"],
            dashboard=data["dashboard"],
            goal=goal
        )
    
    # Categorize by time horizon
    time_horizons = categorize_by_time_horizon(
        data, goal_progress, pending_reviews, execution_status
    )
    
    # Generate Mermaid if requested
    if args.mermaid:
        chart = generate_timeline_mermaid(time_horizons, goal_progress)
        output_path = BASE_DIR / "monitoring" / "timeline-chart.mmd"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(chart)
        print(f"\n[SUCCESS] Mermaid timeline chart saved to: {output_path}")
        return
    
    # Render based on horizon
    if args.horizon == "urgent" or args.horizon == "all":
        render_urgent_dashboard(data, time_horizons, goal_progress)
        if args.horizon != "all":
            return
        print("\n\n")
    
    if args.horizon == "weekly" or args.horizon == "all":
        render_weekly_dashboard(data, time_horizons, goal_progress)
        if args.horizon != "all":
            return
        print("\n\n")
    
    if args.horizon == "monthly" or args.horizon == "all":
        render_monthly_dashboard(data, time_horizons, goal_progress)

if __name__ == "__main__":
    main()
