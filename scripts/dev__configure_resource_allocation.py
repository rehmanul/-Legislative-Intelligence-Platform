"""
Script: dev__configure_resource_allocation.py
Intent:
- temporal

Reads:
- agent-orchestrator/app/config.py

Writes:
- agent-orchestrator/config/development_config.json (optional)

Schema:
- Development resource allocation configuration
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any

# Path setup
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Constants
BASE_DIR = PROJECT_ROOT
CONFIG_DIR = BASE_DIR / "config"
CONFIG_DIR.mkdir(exist_ok=True)
DEV_CONFIG_PATH = CONFIG_DIR / "development_config.json"


def create_development_config() -> Dict[str, Any]:
    """
    Create development resource allocation configuration.
    
    Returns:
        Configuration dictionary
    """
    config = {
        "_meta": {
            "config_type": "DEVELOPMENT_RESOURCE_ALLOCATION",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "purpose": "Development-specific agent resource allocation settings",
            "read_only": False,
            "authoritative": False
        },
        "execution_limits": {
            "max_concurrent_agents": 4,
            "development_workers": 4,
            "production_workers": 2,
            "note": "Reserve 4 workers for development, 2 for production"
        },
        "agent_type_allocation": {
            "intelligence_workers": 4,
            "drafting_workers": 2,
            "execution_workers": 1,
            "learning_workers": 1,
            "note": "Allocate more resources to Intelligence agents (read-only, safe for development)"
        },
        "priority_levels": {
            "development_priority": 10,
            "production_priority": 1,
            "testing_priority": 5,
            "note": "Higher priority = executed first. Development agents get highest priority."
        },
        "timeouts": {
            "development_agent_timeout": 600.0,
            "production_agent_timeout": 300.0,
            "note": "Development agents get longer timeout for testing/iteration"
        },
        "retry_config": {
            "development_max_retries": 3,
            "production_max_retries": 5,
            "note": "Fewer retries for development (faster iteration)"
        },
        "resource_strategy": {
            "strategy": "RESERVE_50_PERCENT",
            "total_workers": 8,
            "development_allocation": 4,
            "production_allocation": 4,
            "note": "Reserve 50% of resources for development work"
        },
        "environment_variables": {
            "MAX_CONCURRENT_AGENTS": "4",
            "AGENT_TIMEOUT": "600.0",
            "AGENT_MAX_RETRIES": "3",
            "note": "Set these environment variables to apply development limits"
        },
        "usage_instructions": {
            "step_1": "Set environment variables: export MAX_CONCURRENT_AGENTS=4",
            "step_2": "Use AgentSpawner with agent_types=['Intelligence'] filter",
            "step_3": "Set priority=10 for development agents",
            "step_4": "Monitor resource usage via executor.get_execution_statistics()"
        }
    }
    
    return config


def save_development_config(config: Dict[str, Any]) -> Path:
    """
    Save development configuration to file.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Path to saved configuration file
    """
    with open(DEV_CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    return DEV_CONFIG_PATH


def apply_environment_variables(config: Dict[str, Any]) -> None:
    """
    Apply configuration as environment variables (optional).
    
    Args:
        config: Configuration dictionary
    """
    env_vars = config.get("environment_variables", {})
    
    print("To apply development resource limits, set these environment variables:")
    print()
    for key, value in env_vars.items():
        if key != "note":
            print(f"export {key}={value}")
    print()


def main():
    """Main execution."""
    print("=" * 60)
    print("Development Resource Allocation Configuration")
    print("=" * 60)
    print()
    
    try:
        # Create development configuration
        config = create_development_config()
        
        # Save to file
        config_path = save_development_config(config)
        print(f"[OK] Created development configuration: {config_path}")
        print()
        
        # Display configuration
        print("Development Resource Allocation Settings:")
        print("-" * 60)
        print(f"Max Concurrent Agents: {config['execution_limits']['max_concurrent_agents']}")
        print(f"Development Workers: {config['execution_limits']['development_workers']}")
        print(f"Production Workers: {config['execution_limits']['production_workers']}")
        print()
        print(f"Development Priority: {config['priority_levels']['development_priority']}")
        print(f"Production Priority: {config['priority_levels']['production_priority']}")
        print()
        print(f"Development Timeout: {config['timeouts']['development_agent_timeout']}s")
        print(f"Production Timeout: {config['timeouts']['production_agent_timeout']}s")
        print()
        
        # Show environment variables
        apply_environment_variables(config)
        
        print("=" * 60)
        print("Configuration complete")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Set environment variables (see above)")
        print("2. Use dev__spawn_intelligence_agents.py to spawn development agents")
        print("3. Monitor resource usage via API or executor statistics")
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
