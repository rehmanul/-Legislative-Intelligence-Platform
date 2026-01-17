"""
AGENT-08: Strategy Agent — Timing

MODE: AGENT
ENTRY: workflow.context.calendar
OUTPUT: workflow.strategy.timing
RESPONSIBILITY: Calculate timing strategy
STOP_CONDITION: timeline exists
"""

from pathlib import Path
from typing import Any, Dict
from datetime import datetime, timedelta
from agents.base.execution_agent_base import ExecutionAgentBase

AGENT_ID = "agent_08_strategy_timing"
ENTRY_PATH = "context.calendar"
OUTPUT_PATH = "strategy.timing"
RESPONSIBILITY = "Calculate timing strategy"
FORBIDDEN = []


class Agent08StrategyTiming(ExecutionAgentBase):
    """Strategy Agent — Timing - Calculates timing strategy"""
    
    AGENT_ID = AGENT_ID
    ENTRY_PATH = ENTRY_PATH
    OUTPUT_PATH = OUTPUT_PATH
    RESPONSIBILITY = RESPONSIBILITY
    FORBIDDEN = FORBIDDEN
    
    def _is_stop_condition_met(self, output_value: Any) -> bool:
        """Check if timeline exists"""
        if not isinstance(output_value, dict):
            return False
        return "timeline" in output_value or "milestones" in output_value
    
    def execute(self) -> Dict[str, Any]:
        """Execute timing strategy calculation"""
        entry_data = self.read_entry()
        
        # Extract calendar
        calendar = entry_data.get("context.calendar", {}) if isinstance(entry_data, dict) else entry_data
        if not isinstance(calendar, dict):
            calendar = {}
        
        # Calculate timing strategy
        now = datetime.utcnow()
        timing = {
            "start_date": now.isoformat() + "Z",
            "target_date": (now + timedelta(days=90)).isoformat() + "Z",
            "timeline": [
                {"phase": "ASK", "start": now.isoformat() + "Z", "duration_days": 7},
                {"phase": "PLAN", "start": (now + timedelta(days=7)).isoformat() + "Z", "duration_days": 7},
                {"phase": "AGENT", "start": (now + timedelta(days=14)).isoformat() + "Z", "duration_days": 60}
            ],
            "milestones": [],
            "confidence": "speculative",
            "timestamp": now.isoformat() + "Z",
            "notes": "Timing requires calendar validation"
        }
        
        return timing


def main(workflow_id: str) -> Path:
    """Main entry point for AGENT-08 Strategy Timing"""
    agent = Agent08StrategyTiming(workflow_id)
    return agent.main()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: agent_08_strategy_timing.py <workflow_id>")
        sys.exit(1)
    
    workflow_id = sys.argv[1]
    result = main(workflow_id)
    if result:
        print(f"✅ Agent completed. Output: {result}")
    else:
        print("❌ Agent failed")
        sys.exit(1)