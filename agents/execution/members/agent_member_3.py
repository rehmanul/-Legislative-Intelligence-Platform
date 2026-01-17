"""AGENT-13: Member Agent — Member 3"""
from pathlib import Path
from agents.execution.members.agent_member_template import create_member_agent

AgentMember3 = create_member_agent(2)
AGENT_ID = AgentMember3.AGENT_ID

def main(workflow_id: str) -> Path:
    """Main entry point for AGENT-13 Member 3"""
    agent = AgentMember3(workflow_id)
    return agent.main()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: agent_member_3.py <workflow_id>")
        sys.exit(1)
    workflow_id = sys.argv[1]
    result = main(workflow_id)
    if result:
        print(f"✅ Agent completed. Output: {result}")
    else:
        print("❌ Agent failed")
        sys.exit(1)