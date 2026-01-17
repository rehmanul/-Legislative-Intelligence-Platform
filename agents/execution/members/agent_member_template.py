"""
Member Agent Template

MODE: AGENT
ENTRY: workflow.strategy, workflow.context.target_members[index]
OUTPUT: workflow.members.member_{index}.profile
RESPONSIBILITY: Member-specific stance + leverage
STOP_CONDITION: profile exists
"""

from pathlib import Path
from typing import Any, Dict
from datetime import datetime
from agents.base.execution_agent_base import ExecutionAgentBase


class MemberAgentTemplate(ExecutionAgentBase):
    """Template for Member of Congress agents"""
    
    # These should be set by subclasses or factory
    AGENT_ID = ""
    MEMBER_INDEX = 0
    ENTRY_PATH = ["strategy.*", "context.target_members"]
    OUTPUT_PATH = ""  # e.g., "members.member_1.profile"
    RESPONSIBILITY = "Member-specific stance + leverage"
    FORBIDDEN = []
    
    def _is_stop_condition_met(self, output_value: Any) -> bool:
        """Check if profile exists"""
        if not isinstance(output_value, dict):
            return False
        return len(output_value) > 0
    
    def execute(self) -> Dict[str, Any]:
        """Execute member profile creation"""
        entry_data = self.read_entry()
        
        # Extract strategy and target members
        strategy = entry_data.get("strategy.*", {}) if isinstance(entry_data, dict) else {}
        target_members = entry_data.get("context.target_members", []) if isinstance(entry_data, dict) else entry_data.get("target_members", [])
        
        if not isinstance(target_members, list):
            target_members = []
        
        # Get member data for this index
        member_data = target_members[self.MEMBER_INDEX] if self.MEMBER_INDEX < len(target_members) else {}
        
        # Create member profile
        profile = {
            "member_id": member_data.get("member_id", f"member_{self.MEMBER_INDEX + 1}"),
            "chamber": member_data.get("chamber", "unknown"),
            "committee": member_data.get("committee", "unknown"),
            "role": member_data.get("role", "member"),
            "stance": "unknown",
            "leverage_points": [],
            "priority": member_data.get("priority", "medium"),
            "confidence": "speculative",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "notes": f"Member profile for member {self.MEMBER_INDEX + 1} - requires validation"
        }
        
        return profile


def create_member_agent(member_index: int) -> type:
    """Factory function to create member agent class for given index"""
    class_name = f"AgentMember{member_index + 1}"
    
    from agents.base.execution_agent_base import ExecutionAgentBase
    
    class AgentMember(ExecutionAgentBase):
        AGENT_ID = f"agent_member_{member_index + 1}"
        MEMBER_INDEX = member_index
        ENTRY_PATH = ["strategy.*", "context.target_members"]
        OUTPUT_PATH = f"members.member_{member_index + 1}.profile"
        RESPONSIBILITY = f"Member {member_index + 1} specific stance + leverage"
        FORBIDDEN = []
        
        def _is_stop_condition_met(self, output_value: Any) -> bool:
            if not isinstance(output_value, dict):
                return False
            return len(output_value) > 0
        
        def execute(self) -> Dict[str, Any]:
            entry_data = self.read_entry()
            
            strategy = entry_data.get("strategy.*", {}) if isinstance(entry_data, dict) else {}
            target_members = entry_data.get("context.target_members", []) if isinstance(entry_data, dict) else entry_data.get("target_members", [])
            
            if not isinstance(target_members, list):
                target_members = []
            
            member_data = target_members[member_index] if member_index < len(target_members) else {}
            
            profile = {
                "member_id": member_data.get("member_id", f"member_{member_index + 1}"),
                "chamber": member_data.get("chamber", "unknown"),
                "committee": member_data.get("committee", "unknown"),
                "role": member_data.get("role", "member"),
                "stance": "unknown",
                "leverage_points": [],
                "priority": member_data.get("priority", "medium"),
                "confidence": "speculative",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "notes": f"Member profile for member {member_index + 1} - requires validation"
            }
            
            return profile
    
    AgentMember.__name__ = class_name
    return AgentMember