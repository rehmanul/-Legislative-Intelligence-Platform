"""
KPI Calculation Scheduler

Schedules recurring KPI calculation:
- Daily: Operational KPIs
- Weekly: Strategic KPIs
- Monthly: System Health KPIs
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime, timezone

# Path setup
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

SCRIPTS_DIR = BASE_DIR / "scripts"
STRATEGIC_SCRIPT = SCRIPTS_DIR / "metrics__calculate__strategic_kpis.py"
OPERATIONAL_SCRIPT = SCRIPTS_DIR / "metrics__calculate__operational_kpis.py"
SYSTEM_HEALTH_SCRIPT = SCRIPTS_DIR / "metrics__calculate__system_health.py"
AGGREGATE_SCRIPT = SCRIPTS_DIR / "metrics__aggregate__dashboard.py"
INGESTION_SCRIPT = BASE_DIR / "lib" / "kpi_ingestion.py"


def run_script(script_path: Path) -> bool:
    """Run a Python script and return success status."""
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        if result.returncode == 0:
            print(f"[OK] {script_path.name}")
            return True
        else:
            print(f"[ERROR] {script_path.name}: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"[ERROR] {script_path.name}: Timeout")
        return False
    except Exception as e:
        print(f"[ERROR] {script_path.name}: {e}")
        return False


def calculate_all_kpis():
    """Calculate all KPI categories."""
    print(f"[scheduler__kpi_calculation] Calculating all KPIs...")
    print(f"   Timestamp: {datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')}")
    
    results = {
        "strategic": run_script(STRATEGIC_SCRIPT),
        "operational": run_script(OPERATIONAL_SCRIPT),
        "system_health": run_script(SYSTEM_HEALTH_SCRIPT),
    }
    
    # Aggregate dashboard
    if all(results.values()):
        results["aggregate"] = run_script(AGGREGATE_SCRIPT)
        results["ingestion"] = run_script(INGESTION_SCRIPT)
    else:
        print("[WARNING] Skipping aggregation due to calculation failures")
        results["aggregate"] = False
        results["ingestion"] = False
    
    success = all(results.values())
    
    print(f"[scheduler__kpi_calculation] KPI calculation complete")
    print(f"   Results: {results}")
    print(f"   Success: {success}")
    
    return success


def calculate_operational_kpis():
    """Calculate operational KPIs (daily)."""
    print(f"[scheduler__kpi_calculation] Calculating operational KPIs (daily)...")
    
    results = {
        "operational": run_script(OPERATIONAL_SCRIPT),
        "system_health": run_script(SYSTEM_HEALTH_SCRIPT),
    }
    
    if all(results.values()):
        results["aggregate"] = run_script(AGGREGATE_SCRIPT)
        results["ingestion"] = run_script(INGESTION_SCRIPT)
    
    return all(results.values())


def calculate_strategic_kpis():
    """Calculate strategic KPIs (weekly)."""
    print(f"[scheduler__kpi_calculation] Calculating strategic KPIs (weekly)...")
    
    results = {
        "strategic": run_script(STRATEGIC_SCRIPT),
        "operational": run_script(OPERATIONAL_SCRIPT),
        "system_health": run_script(SYSTEM_HEALTH_SCRIPT),
    }
    
    if all(results.values()):
        results["aggregate"] = run_script(AGGREGATE_SCRIPT)
        results["ingestion"] = run_script(INGESTION_SCRIPT)
    
    return all(results.values())


def calculate_system_health_kpis():
    """Calculate system health KPIs (monthly)."""
    print(f"[scheduler__kpi_calculation] Calculating system health KPIs (monthly)...")
    
    results = {
        "strategic": run_script(STRATEGIC_SCRIPT),
        "operational": run_script(OPERATIONAL_SCRIPT),
        "system_health": run_script(SYSTEM_HEALTH_SCRIPT),
    }
    
    if all(results.values()):
        results["aggregate"] = run_script(AGGREGATE_SCRIPT)
        results["ingestion"] = run_script(INGESTION_SCRIPT)
    
    return all(results.values())


def main():
    """Main scheduler execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="KPI Calculation Scheduler")
    parser.add_argument(
        "--frequency",
        choices=["all", "daily", "weekly", "monthly"],
        default="all",
        help="Calculation frequency"
    )
    
    args = parser.parse_args()
    
    if args.frequency == "all":
        success = calculate_all_kpis()
    elif args.frequency == "daily":
        success = calculate_operational_kpis()
    elif args.frequency == "weekly":
        success = calculate_strategic_kpis()
    elif args.frequency == "monthly":
        success = calculate_system_health_kpis()
    else:
        success = False
    
    if success:
        print("[OK] KPI calculation scheduler completed successfully")
        sys.exit(0)
    else:
        print("[ERROR] KPI calculation scheduler completed with errors")
        sys.exit(1)


if __name__ == "__main__":
    main()
