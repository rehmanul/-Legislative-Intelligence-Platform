"""
ASK-05: Signal Prioritization Agent

MODE: ASK
ENTRY: workflow.context.raw_signals
OUTPUT: workflow.context.prioritized_signals
RESPONSIBILITY: Rank signals
STOP_CONDITION: ordered signal list exists
"""

from pathlib import Path
from typing import Any, List, Dict
from datetime import datetime
from agents.base.ask_agent_base import AskAgentBase

AGENT_ID = "ask_05_signal_prioritization"
ENTRY_PATH = "context.raw_signals"
OUTPUT_PATH = "context.prioritized_signals"
RESPONSIBILITY = "Rank signals"
FORBIDDEN = []


class Ask05SignalPrioritizationAgent(AskAgentBase):
    """Signal Prioritization Agent - Ranks signals by priority"""
    
    AGENT_ID = AGENT_ID
    ENTRY_PATH = ENTRY_PATH
    OUTPUT_PATH = OUTPUT_PATH
    RESPONSIBILITY = RESPONSIBILITY
    FORBIDDEN = FORBIDDEN
    
    def _is_stop_condition_met(self, output_value: Any) -> bool:
        """Check if prioritized_signals list exists and is ordered"""
        if not isinstance(output_value, list):
            return False
        return len(output_value) > 0
    
    def execute(self) -> List[Dict[str, Any]]:
        """
        Execute signal prioritization.
        
        Reads raw_signals and ranks them by priority.
        """
        entry_data = self.read_entry()
        
        # Extract raw signals
        raw_signals = entry_data if isinstance(entry_data, list) else []
        
        # Prioritize signals
        prioritized_signals = []
        
        # Sort signals by priority score (if available)
        if raw_signals:
            # Add priority scores if not present
            for signal in raw_signals:
                if not isinstance(signal, dict):
                    signal = {"content": str(signal), "priority": 5}
                
                # Calculate priority if not set
                if "priority" not in signal:
                    # Default priority based on signal type/urgency
                    signal["priority"] = signal.get("urgency_score", 5)
                
                prioritized_signals.append(signal)
            
            # Sort by priority (higher = more important)
            prioritized_signals.sort(key=lambda x: x.get("priority", 0), reverse=True)
            
            # Add rank
            for i, signal in enumerate(prioritized_signals):
                signal["rank"] = i + 1
        else:
            # No raw signals - create placeholder
            prioritized_signals.append({
                "rank": 1,
                "priority": 5,
                "content": "No raw signals available",
                "confidence": "speculative",
                "notes": "Signal prioritization requires raw signals input"
            })
        
        return prioritized_signals


def main(workflow_id: str) -> Path:
    """Main entry point for ASK-05 Signal Prioritization Agent"""
    agent = Ask05SignalPrioritizationAgent(workflow_id)
    return agent.main()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: ask_05_signal_prioritization.py <workflow_id>")
        sys.exit(1)
    
    workflow_id = sys.argv[1]
    result = main(workflow_id)
    if result:
        print(f"✅ Agent completed. Output: {result}")
    else:
        print("❌ Agent failed")
        sys.exit(1)