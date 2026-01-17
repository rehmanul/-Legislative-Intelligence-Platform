"""
Script: setup__windows_scheduled_task.py
Intent: snapshot (creates Windows scheduled task)
Reads: None
Writes: Windows scheduled task (via schtasks command)
Purpose: Set up Windows scheduled task to run agent execution periodically
"""

import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
SPAWN_SCRIPT = BASE_DIR / "scripts" / "execution__spawn_agents.py"
MONITOR_SCRIPT = BASE_DIR / "scripts" / "monitor__check_agent_status.py"
PYTHON_EXE = sys.executable

def create_scheduled_task(task_name: str, script_path: Path, interval_minutes: int = 60) -> bool:
    """Create Windows scheduled task to run script periodically"""
    
    if not script_path.exists():
        print(f"❌ Script not found: {script_path}")
        return False
    
    # Build command to run
    command = f'"{PYTHON_EXE}" "{script_path}"'
    
    # Build schtasks command
    schtasks_cmd = [
        'schtasks',
        '/Create',
        '/TN', task_name,  # Task name
        '/TR', command,    # Task to run
        '/SC', 'MINUTE',   # Schedule type (MINUTE)
        '/MO', str(interval_minutes),  # Interval in minutes
        '/F',              # Force (overwrite if exists)
        '/RL', 'HIGHEST',  # Run level (highest privileges if needed)
    ]
    
    try:
        result = subprocess.run(
            schtasks_cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"✅ Scheduled task '{task_name}' created successfully")
            print(f"   Script: {script_path.name}")
            print(f"   Interval: Every {interval_minutes} minutes")
            return True
        else:
            print(f"❌ Failed to create scheduled task")
            print(f"   Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error creating scheduled task: {e}")
        return False

def delete_scheduled_task(task_name: str) -> bool:
    """Delete Windows scheduled task"""
    try:
        result = subprocess.run(
            ['schtasks', '/Delete', '/TN', task_name, '/F'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"✅ Scheduled task '{task_name}' deleted successfully")
            return True
        else:
            if "does not exist" in result.stderr.lower():
                print(f"ℹ️  Scheduled task '{task_name}' does not exist")
                return True
            print(f"❌ Failed to delete scheduled task: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error deleting scheduled task: {e}")
        return False

def list_scheduled_tasks(prefix: str = "AgentOrchestrator") -> bool:
    """List scheduled tasks matching prefix"""
    try:
        result = subprocess.run(
            ['schtasks', '/Query', '/FO', 'LIST', '/V'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            found_tasks = []
            current_task = {}
            
            for line in lines:
                line = line.strip()
                if line.startswith('TaskName:'):
                    task_name = line.split(':', 1)[1].strip()
                    if prefix in task_name:
                        if current_task:
                            found_tasks.append(current_task)
                        current_task = {'name': task_name}
                elif current_task and ':' in line:
                    key, value = line.split(':', 1)
                    current_task[key.strip()] = value.strip()
            
            if current_task:
                found_tasks.append(current_task)
            
            if found_tasks:
                print(f"\n📋 Found {len(found_tasks)} scheduled task(s) matching '{prefix}':")
                for task in found_tasks:
                    print(f"  • {task.get('name', 'Unknown')}")
                    print(f"    Status: {task.get('Status', 'Unknown')}")
                    print(f"    Next Run: {task.get('Next Run Time', 'Unknown')}")
                    print()
                return True
            else:
                print(f"ℹ️  No scheduled tasks found matching '{prefix}'")
                return False
        else:
            print(f"❌ Failed to query scheduled tasks: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error querying scheduled tasks: {e}")
        return False

def main():
    """Main function to set up scheduled tasks"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Set up Windows scheduled tasks for agent execution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create task to spawn agents every hour
  python setup__windows_scheduled_task.py --create --spawn-agents --interval 60
  
  # Create task to check status every 30 minutes
  python setup__windows_scheduled_task.py --create --check-status --interval 30
  
  # List all agent orchestrator tasks
  python setup__windows_scheduled_task.py --list
  
  # Delete a task
  python setup__windows_scheduled_task.py --delete --task-name AgentOrchestrator_SpawnAgents
        """
    )
    
    parser.add_argument("--create", action="store_true", help="Create scheduled task")
    parser.add_argument("--delete", action="store_true", help="Delete scheduled task")
    parser.add_argument("--list", action="store_true", help="List scheduled tasks")
    parser.add_argument("--spawn-agents", action="store_true", help="Create task to spawn agents")
    parser.add_argument("--check-status", action="store_true", help="Create task to check status")
    parser.add_argument("--task-name", type=str, help="Task name (required for delete)")
    parser.add_argument("--interval", type=int, default=60, help="Interval in minutes (default: 60)")
    
    args = parser.parse_args()
    
    if sys.platform != 'win32':
        print("❌ This script only works on Windows")
        print("   For Linux/Mac, use cron instead")
        sys.exit(1)
    
    if args.list:
        list_scheduled_tasks("AgentOrchestrator")
        return
    
    if args.delete:
        if not args.task_name:
            print("❌ --task-name is required when using --delete")
            sys.exit(1)
        delete_scheduled_task(args.task_name)
        return
    
    if args.create:
        if args.spawn_agents:
            task_name = "AgentOrchestrator_SpawnAgents"
            print(f"\n📅 Creating scheduled task: {task_name}")
            print(f"   This will spawn IDLE agents every {args.interval} minutes")
            print(f"   Script: {SPAWN_SCRIPT.name}\n")
            
            create_scheduled_task(task_name, SPAWN_SCRIPT, args.interval)
        
        if args.check_status:
            task_name = "AgentOrchestrator_CheckStatus"
            print(f"\n📅 Creating scheduled task: {task_name}")
            print(f"   This will check agent status every {args.interval} minutes")
            print(f"   Script: {MONITOR_SCRIPT.name}\n")
            
            create_scheduled_task(task_name, MONITOR_SCRIPT, args.interval)
        
        if not args.spawn_agents and not args.check_status:
            print("❌ Must specify --spawn-agents or --check-status when using --create")
            sys.exit(1)
        
        print(f"\n💡 Next steps:")
        print(f"  1. View scheduled tasks: python {Path(__file__).name} --list")
        print(f"  2. Manually test task: schtasks /Run /TN <task_name>")
        print(f"  3. Check task history in Windows Task Scheduler GUI")
        return
    
    # Default: show usage
    parser.print_help()

if __name__ == "__main__":
    main()
