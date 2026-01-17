"""
AGENT-09: Strategy Agent — Coalition

MODE: AGENT
ENTRY: workflow.context.stakeholders
OUTPUT: workflow.strategy.coalition
RESPONSIBILITY: Build coalition strategy
STOP_CONDITION: coalition list exists
"""

from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime
from agents.base.execution_agent_base import ExecutionAgentBase

AGENT_ID = "agent_09_strategy_coalition"
ENTRY_PATH = "context.stakeholders"
OUTPUT_PATH = "strategy.coalition"
RESPONSIBILITY = "Build coalition strategy"
FORBIDDEN = []


class Agent09StrategyCoalition(ExecutionAgentBase):
    """Strategy Agent — Coalition - Builds coalition strategy"""
    
    AGENT_ID = AGENT_ID
    ENTRY_PATH = ENTRY_PATH
    OUTPUT_PATH = OUTPUT_PATH
    RESPONSIBILITY = RESPONSIBILITY
    FORBIDDEN = FORBIDDEN
    
    def _is_stop_condition_met(self, output_value: Any) -> bool:
        """Check if coalition list exists"""
        if not isinstance(output_value, dict):
            return False
        return "coalition_members" in output_value and len(output_value.get("coalition_members", [])) > 0
    
    def execute(self) -> Dict[str, Any]:
        """Execute coalition strategy building"""
        entry_data = self.read_entry()
        
        # Extract stakeholders
        stakeholders = entry_data.get("context.stakeholders", {}) if isinstance(entry_data, dict) else entry_data
        if not isinstance(stakeholders, dict):
            stakeholders = {}
        
        # Build coalition
        coalition = {
            "coalition_members": [],
            "allies": stakeholders.get("allies", []),
            "opponents": stakeholders.get("opponents", []),
            "neutrals": stakeholders.get("neutrals", []),
            "strategy": "Engage allies, neutralize opponents",
            "confidence": "speculative",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "notes": "Coalition requires stakeholder validation"
        }
        
        # Process allies into coalition
        allies = coalition.get("allies", [])
        for ally in allies:
            coalition["coalition_members"].append({
                "entity": ally if isinstance(ally, str) else ally.get("name", "unknown"),
                "role": "ally",
                "priority": "high"
            })
        
        # If no allies, create placeholder
        if not coalition["coalition_members"]:
            coalition["coalition_members"].append({
                "entity": "TBD",
                "role": "ally",
                "priority": "high",
                "notes": "Coalition members require stakeholder identification"
            })
        
        return coalition


def main(workflow_id: str) -> Path:
    """Main entry point for AGENT-09 Strategy Coalition"""
    agent = Agent09StrategyCoalition(workflow_id)
    return agent.main()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: agent_09_strategy_coalition.py <workflow_id>")
        sys.exit(1)
    
    workflow_id = sys.argv[1]
    result = main(workflow_id)
    if result:
        print(f"✅ Agent completed. Output: {result}")
    else:
        print("❌ Agent failed")
        sys.exit(1)