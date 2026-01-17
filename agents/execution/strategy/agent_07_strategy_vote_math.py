"""
AGENT-07: Strategy Agent — Vote Math

MODE: AGENT
ENTRY: workflow.context.target_members
OUTPUT: workflow.strategy.vote_math
RESPONSIBILITY: Calculate vote counts
STOP_CONDITION: vote counts exist
"""

from pathlib import Path
from typing import Any, Dict
from datetime import datetime
from agents.base.execution_agent_base import ExecutionAgentBase

AGENT_ID = "agent_07_strategy_vote_math"
ENTRY_PATH = "context.target_members"
OUTPUT_PATH = "strategy.vote_math"
RESPONSIBILITY = "Calculate vote counts"
FORBIDDEN = []


class Agent07StrategyVoteMath(ExecutionAgentBase):
    """Strategy Agent — Vote Math - Calculates vote counts"""
    
    AGENT_ID = AGENT_ID
    ENTRY_PATH = ENTRY_PATH
    OUTPUT_PATH = OUTPUT_PATH
    RESPONSIBILITY = RESPONSIBILITY
    FORBIDDEN = FORBIDDEN
    
    def _is_stop_condition_met(self, output_value: Any) -> bool:
        """Check if vote counts exist"""
        if not isinstance(output_value, dict):
            return False
        return "total_votes" in output_value or "yes_votes" in output_value
    
    def execute(self) -> Dict[str, Any]:
        """Execute vote math calculation"""
        entry_data = self.read_entry()
        
        # Extract target members
        target_members = entry_data.get("context.target_members", []) if isinstance(entry_data, dict) else entry_data
        if not isinstance(target_members, list):
            target_members = []
        
        # Calculate vote math
        vote_math = {
            "total_members": len(target_members),
            "total_votes": len(target_members),
            "yes_votes": 0,
            "no_votes": 0,
            "undecided": len(target_members),
            "needed": (len(target_members) // 2) + 1 if len(target_members) > 0 else 0,
            "confidence": "speculative",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "notes": "Vote math requires member stance analysis"
        }
        
        return vote_math


def main(workflow_id: str) -> Path:
    """Main entry point for AGENT-07 Strategy Vote Math"""
    agent = Agent07StrategyVoteMath(workflow_id)
    return agent.main()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: agent_07_strategy_vote_math.py <workflow_id>")
        sys.exit(1)
    
    workflow_id = sys.argv[1]
    result = main(workflow_id)
    if result:
        print(f"✅ Agent completed. Output: {result}")
    else:
        print("❌ Agent failed")
        sys.exit(1)