"""
IntelAgentBase - Base class for INTEL-mode agents.

INTEL agents are responsible for:
- Calendar tracking (congressional calendar)
- Coalition intelligence (operators, economic clusters, insurers, NGOs, etc.)
- Committee intelligence (staff, agenda, power maps)
- Escalation intelligence (state/federal agency contacts)
- Risk intelligence (bill risk, media risk, legal objections)
- Rulemaking timeline tracking
- Sponsor intelligence (whip counts, persuadable members, champions)
- Stakeholder contacts

These agents are READ-ONLY and gather information without producing strategy.
They do NOT require professional guidance signatures to execute.
"""

from typing import Any, Dict, List
from agents.base.agent_base import AgentBase


class IntelAgentBase(AgentBase):
    """
    Base class for INTEL-mode agents.
    
    INTEL agents are read-only information gatherers. They:
    - Scan external sources for intelligence
    - Compile stakeholder information
    - Track calendars and timelines
    - Assess risk factors
    
    INTEL agents do NOT require professional guidance to execute.
    """
    
    # Intel agents should not output strategy
    FORBIDDEN: List[str] = ["strategy", "action_plan", "recommendation"]
    
    # Intel agents don't require human review to gather information
    REQUIRES_HUMAN_REVIEW: bool = False
    
    # Intel agents are read-only - they don't modify workflow state
    READ_ONLY: bool = True
    
    def validate_output(self, output: Dict[str, Any]) -> bool:
        """
        Extended validation for INTEL agents.
        
        Ensures outputs are informational, not strategic.
        """
        # First run base validation
        if not super().validate_output(output):
            return False
        
        # Ensure output includes source attribution
        if "sources" not in output and "source" not in output:
            output["sources"] = ["internal_analysis"]
        
        # Mark as intelligence product
        output["_intel_metadata"] = {
            "agent_type": "INTEL",
            "read_only": self.READ_ONLY,
            "requires_guidance": False,
        }
        
        return True
    
    def update_workflow_state(self, data: Dict[str, Any]) -> None:
        """
        Intel agents write to a separate intel store, not main workflow state.
        """
        import json
        from datetime import datetime
        
        try:
            intel_file = self.data_dir / "intel_store.json"
            
            # Load existing intel or create new
            if intel_file.exists():
                with open(intel_file, "r", encoding="utf-8") as f:
                    intel_store = json.load(f)
            else:
                intel_store = {"intel": {}}
            
            # Add this agent's intel
            intel_store["intel"][self.AGENT_ID] = {
                "data": data,
                "collected_at": datetime.utcnow().isoformat() + "Z",
                "workflow_id": self.workflow_id,
            }
            
            # Write updated intel store
            with open(intel_file, "w", encoding="utf-8") as f:
                json.dump(intel_store, f, indent=2, default=str)
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"[{self.AGENT_ID}] Error updating intel store: {e}")
