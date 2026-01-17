"""
Script: operator__mode_selector.py
Intent:
- temporal

Reads:
- None (interactive mode selection)

Writes:
- None (routes to appropriate mode script)

Schema:
Interactive mode selector that routes to Heat Map, Cockpit, or Velocity modes.
"""

import sys
import subprocess
from pathlib import Path

# Path setup
BASE_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"


def show_menu():
    """Display mode selection menu."""
    print("\n" + "=" * 80)
    print("OPERATOR MODES")
    print("=" * 80)
    print()
    print("Select a mode:")
    print()
    print("  1. Heat Map Mode")
    print("     - System health snapshot")
    print("     - Agent status distribution")
    print("     - Review gate status")
    print("     - State advancement readiness")
    print()
    print("  2. Cockpit Mode")
    print("     - Pending approvals")
    print("     - State advancement")
    print("     - Execution authorizations")
    print()
    print("  3. Velocity Mode")
    print("     - Throughput metrics")
    print("     - Review cycle times")
    print("     - Bottleneck identification")
    print()
    print("  4. Unified Dashboard (all modes)")
    print()
    print("  0. Exit")
    print()


def run_heat_map():
    """Run heat map mode."""
    script = SCRIPTS_DIR / "snapshot__generate__heat_map.py"
    if script.exists():
        subprocess.run([sys.executable, str(script)])
    else:
        print(f"[ERROR] Script not found: {script}")


def run_cockpit():
    """Run cockpit mode."""
    script = SCRIPTS_DIR / "cockpit__list__pending_approvals.py"
    if script.exists():
        subprocess.run([sys.executable, str(script)])
    else:
        print(f"[ERROR] Script not found: {script}")


def run_velocity():
    """Run velocity mode."""
    script = SCRIPTS_DIR / "velocity__calculate__metrics.py"
    if script.exists():
        subprocess.run([sys.executable, str(script)])
    else:
        print(f"[ERROR] Script not found: {script}")


def run_unified():
    """Run unified dashboard (all modes)."""
    print("\n" + "=" * 80)
    print("UNIFIED DASHBOARD")
    print("=" * 80)
    print()
    
    # Heat Map
    print("\n[HEAT MAP MODE]")
    print("-" * 80)
    run_heat_map()
    
    # Cockpit
    print("\n[COCKPIT MODE]")
    print("-" * 80)
    run_cockpit()
    
    # Velocity
    print("\n[VELOCITY MODE]")
    print("-" * 80)
    run_velocity()
    
    print("\n" + "=" * 80)
    print("Unified dashboard complete")
    print("=" * 80)


def main():
    """Main execution."""
    while True:
        show_menu()
        
        try:
            choice = input("Enter choice (0-4): ").strip()
            
            if choice == "0":
                print("Exiting...")
                break
            elif choice == "1":
                run_heat_map()
            elif choice == "2":
                run_cockpit()
            elif choice == "3":
                run_velocity()
            elif choice == "4":
                run_unified()
            else:
                print(f"[ERROR] Invalid choice: {choice}")
                continue
            
            # Ask if user wants to continue
            print()
            continue_choice = input("Press Enter to return to menu, or 'q' to quit: ").strip().lower()
            if continue_choice == 'q':
                break
                
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"[ERROR] {e}")
            continue


if __name__ == "__main__":
    main()
