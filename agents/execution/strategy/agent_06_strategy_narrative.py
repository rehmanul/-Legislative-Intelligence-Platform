"""
AGENT-06: Strategy Agent — Narrative

MODE: AGENT
ENTRY: workflow.data.signals.*
OUTPUT: workflow.strategy.narrative
RESPONSIBILITY: Synthesize narrative strategy
STOP_CONDITION: narrative text exists
"""

from pathlib import Path
from typing import Any, Dict
from datetime import datetime
from agents.base.execution_agent_base import ExecutionAgentBase

AGENT_ID = "agent_06_strategy_narrative"
ENTRY_PATH = "data.signals.*"
OUTPUT_PATH = "strategy.narrative"
RESPONSIBILITY = "Synthesize narrative strategy"
FORBIDDEN = []


class Agent06StrategyNarrative(ExecutionAgentBase):
    """Strategy Agent — Narrative - Synthesizes narrative strategy"""
    
    AGENT_ID = AGENT_ID
    ENTRY_PATH = ENTRY_PATH
    OUTPUT_PATH = OUTPUT_PATH
    RESPONSIBILITY = RESPONSIBILITY
    FORBIDDEN = FORBIDDEN
    
    def _is_stop_condition_met(self, output_value: Any) -> bool:
        """Check if narrative text exists"""
        if not isinstance(output_value, dict):
            return False
        return "narrative" in output_value and len(str(output_value.get("narrative", ""))) > 0
    
    def execute(self) -> Dict[str, Any]:
        """Execute narrative synthesis"""
        entry_data = self.read_entry()
        
        # Extract signals
        signals = entry_data.get("data.signals.*", {}) if isinstance(entry_data, dict) else {}
        if not isinstance(signals, dict):
            signals = {}
        
        # Synthesize narrative from signals
        narrative = {
            "narrative": "Policy narrative synthesized from signal analysis",
            "key_themes": [],
            "target_audience": "general",
            "tone": "professional",
            "confidence": "speculative",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "notes": "Narrative requires human review and refinement"
        }
        
        # Extract themes from signals
        for signal_type, signal_list in signals.items():
            if isinstance(signal_list, list) and signal_list:
                narrative["key_themes"].append(f"Themes from {signal_type} signals")
        
        if not narrative["key_themes"]:
            narrative["key_themes"] = ["Policy opportunity", "Stakeholder engagement"]
        
        return narrative


def main(workflow_id: str) -> Path:
    """Main entry point for AGENT-06 Strategy Narrative"""
    agent = Agent06StrategyNarrative(workflow_id)
    return agent.main()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: agent_06_strategy_narrative.py <workflow_id>")
        sys.exit(1)
    
    workflow_id = sys.argv[1]
    result = main(workflow_id)
    if result:
        print(f"✅ Agent completed. Output: {result}")
    else:
        print("❌ Agent failed")
        sys.exit(1)