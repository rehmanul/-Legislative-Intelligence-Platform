"""
Script: Update Agent Registry with New Swarm Agents
Intent: snapshot
Reads: registry/agent-registry.json
Writes: registry/agent-registry.json (updated)
"""

import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
REGISTRY_PATH = BASE_DIR / "registry" / "agent-registry.json"

NEW_AGENTS = [
    # Execution Swarm - Grassroots (5 agents)
    {
        "agent_id": "execution_grassroots_mobilize_execute_pre_evt",
        "agent_type": "Execution",
        "legislative_state": "PRE_EVT",
        "scope": "Mobilize grassroots organizations and execute activation campaigns",
        "risk_level": "HIGH"
    },
    {
        "agent_id": "execution_grassroots_amplify_execute_pre_evt",
        "agent_type": "Execution",
        "legislative_state": "PRE_EVT",
        "scope": "Amplify grassroots signals to policymakers",
        "risk_level": "HIGH"
    },
    {
        "agent_id": "execution_grassroots_coordinate_execute_pre_evt",
        "agent_type": "Execution",
        "legislative_state": "PRE_EVT",
        "scope": "Coordinate grassroots efforts across regions",
        "risk_level": "HIGH"
    },
    {
        "agent_id": "execution_grassroots_narrative_execute_pre_evt",
        "agent_type": "Execution",
        "legislative_state": "PRE_EVT",
        "scope": "Execute grassroots narrative campaigns",
        "risk_level": "HIGH"
    },
    {
        "agent_id": "execution_grassroots_monitor_execute_pre_evt",
        "agent_type": "Execution",
        "legislative_state": "PRE_EVT",
        "scope": "Monitor grassroots engagement effectiveness",
        "risk_level": "HIGH"
    },
    # Execution Swarm - Cosponsorship (5 agents)
    {
        "agent_id": "execution_cosponsor_target_execute_comm_evt",
        "agent_type": "Execution",
        "legislative_state": "COMM_EVT",
        "scope": "Execute targeted cosponsor recruitment",
        "risk_level": "HIGH"
    },
    {
        "agent_id": "execution_cosponsor_outreach_execute_comm_evt",
        "agent_type": "Execution",
        "legislative_state": "COMM_EVT",
        "scope": "Execute outreach to potential cosponsors",
        "risk_level": "HIGH"
    },
    {
        "agent_id": "execution_cosponsor_pathway_execute_comm_evt",
        "agent_type": "Execution",
        "legislative_state": "COMM_EVT",
        "scope": "Execute influence pathway strategies",
        "risk_level": "HIGH"
    },
    {
        "agent_id": "execution_cosponsor_timing_execute_comm_evt",
        "agent_type": "Execution",
        "legislative_state": "COMM_EVT",
        "scope": "Execute cosponsor asks at optimal timing",
        "risk_level": "HIGH"
    },
    {
        "agent_id": "execution_cosponsor_track_execute_comm_evt",
        "agent_type": "Execution",
        "legislative_state": "COMM_EVT",
        "scope": "Track cosponsor commitments and update whip count",
        "risk_level": "HIGH"
    },
    # Origination Swarm - Drafting (9 agents)
    {
        "agent_id": "draft_coalition_strategy_originate_impl_evt",
        "agent_type": "Drafting",
        "legislative_state": "IMPL_EVT",
        "scope": "Draft coalition building strategies",
        "risk_level": "MEDIUM"
    },
    {
        "agent_id": "draft_coalition_structure_originate_impl_evt",
        "agent_type": "Drafting",
        "legislative_state": "IMPL_EVT",
        "scope": "Design optimal coalition structures",
        "risk_level": "MEDIUM"
    },
    {
        "agent_id": "draft_coalition_innovation_originate_impl_evt",
        "agent_type": "Drafting",
        "legislative_state": "IMPL_EVT",
        "scope": "Develop innovative coalition tactics",
        "risk_level": "MEDIUM"
    },
    {
        "agent_id": "draft_grassroots_strategy_originate_impl_evt",
        "agent_type": "Drafting",
        "legislative_state": "IMPL_EVT",
        "scope": "Draft grassroots mobilization strategies",
        "risk_level": "MEDIUM"
    },
    {
        "agent_id": "draft_grassroots_model_originate_impl_evt",
        "agent_type": "Drafting",
        "legislative_state": "IMPL_EVT",
        "scope": "Develop grassroots mobilization models",
        "risk_level": "MEDIUM"
    },
    {
        "agent_id": "draft_grassroots_narrative_originate_impl_evt",
        "agent_type": "Drafting",
        "legislative_state": "IMPL_EVT",
        "scope": "Develop grassroots narrative frameworks",
        "risk_level": "MEDIUM"
    },
    {
        "agent_id": "draft_cosponsorship_strategy_originate_comm_evt",
        "agent_type": "Drafting",
        "legislative_state": "COMM_EVT",
        "scope": "Draft cosponsorship recruitment strategies",
        "risk_level": "MEDIUM"
    },
    {
        "agent_id": "draft_cosponsorship_model_originate_comm_evt",
        "agent_type": "Drafting",
        "legislative_state": "COMM_EVT",
        "scope": "Develop cosponsorship recruitment models",
        "risk_level": "MEDIUM"
    },
    {
        "agent_id": "draft_unified_strategy_originate_impl_evt",
        "agent_type": "Drafting",
        "legislative_state": "IMPL_EVT",
        "scope": "Synthesize unified tactical playbook",
        "risk_level": "MEDIUM"
    },
    # Origination Swarm - Learning (1 agent)
    {
        "agent_id": "learning_coalition_lessons_originate_impl_evt",
        "agent_type": "Learning",
        "legislative_state": "IMPL_EVT",
        "scope": "Analyze coalition, grassroots, and cosponsorship lessons learned",
        "risk_level": "LOW"
    },
    # Coordination Agent (1 agent)
    {
        "agent_id": "execution_coalition_originate_impl_evt",
        "agent_type": "Execution",
        "legislative_state": "IMPL_EVT",
        "scope": "Orchestrate origination swarm and synthesize strategies",
        "risk_level": "HIGH"
    }
]

def main():
    # Load existing registry
    if REGISTRY_PATH.exists():
        registry = json.loads(REGISTRY_PATH.read_text(encoding='utf-8'))
    else:
        registry = {"agents": [], "_meta": {"total_agents": 0, "active_agents": 0}}
    
    existing_agent_ids = {agent.get("agent_id") for agent in registry.get("agents", [])}
    
    # Add new agents (skip if already exists)
    added_count = 0
    for agent_spec in NEW_AGENTS:
        if agent_spec["agent_id"] not in existing_agent_ids:
            agent_entry = {
                "agent_id": agent_spec["agent_id"],
                "agent_type": agent_spec["agent_type"],
                "status": "IDLE",
                "scope": agent_spec["scope"],
                "current_task": "Registered",
                "last_heartbeat": datetime.utcnow().isoformat() + "Z",
                "risk_level": agent_spec["risk_level"],
                "outputs": [],
                "spawned_at": datetime.utcnow().isoformat() + "Z",
                "legislative_state": agent_spec.get("legislative_state", "UNKNOWN")
            }
            registry.setdefault("agents", []).append(agent_entry)
            added_count += 1
    
    # Update metadata
    registry.setdefault("_meta", {})["total_agents"] = len(registry.get("agents", []))
    registry["_meta"]["last_updated"] = datetime.utcnow().isoformat() + "Z"
    registry["_meta"]["registry_version"] = "1.0"
    
    # Write updated registry
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    
    print(f"Registry updated: {added_count} new agents added")
    print(f"   Total agents in registry: {len(registry.get('agents', []))}")
    return added_count

if __name__ == "__main__":
    main()
