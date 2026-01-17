#!/usr/bin/env python3
"""Quick script to verify agent counts after deduplication"""

import json
from pathlib import Path

registry_path = Path(__file__).parent.parent / "registry" / "agent-registry.json"

with open(registry_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Deduplicate by agent_id (keep most recent by last_heartbeat)
agent_map = {}
for agent in data['agents']:
    agent_id = agent.get('agent_id')
    if not agent_id:
        continue
    
    existing = agent_map.get(agent_id)
    if not existing:
        agent_map[agent_id] = agent
    else:
        # Keep the one with the more recent heartbeat
        existing_heartbeat = existing.get('last_heartbeat', '')
        new_heartbeat = agent.get('last_heartbeat', '')
        if new_heartbeat and new_heartbeat > existing_heartbeat:
            agent_map[agent_id] = agent

unique_agents = list(agent_map.values())

# Count by status
counts = {
    'RUNNING': 0,
    'IDLE': 0,
    'WAITING_REVIEW': 0,
    'BLOCKED': 0,
    'RETIRED': 0,
    'OTHER': 0
}

for agent in unique_agents:
    status = agent.get('status', 'OTHER')
    if status in counts:
        counts[status] += 1
    else:
        counts['OTHER'] += 1

print("=" * 50)
print("AGENT COUNT VERIFICATION")
print("=" * 50)
print(f"\nTotal agents in array: {len(data['agents'])}")
print(f"Unique agents (after deduplication): {len(unique_agents)}")
print(f"\nCounts from metadata (_meta):")
print(f"  active_agents: {data['_meta'].get('active_agents', 'N/A')}")
print(f"  idle_agents: {data['_meta'].get('idle_agents', 'N/A')}")
print(f"  waiting_review_agents: {data['_meta'].get('waiting_review_agents', 'N/A')}")
print(f"  blocked_agents: {data['_meta'].get('blocked_agents', 'N/A')}")
print(f"\nActual counts (from unique agents):")
for status, count in counts.items():
    if count > 0 or status == 'OTHER':
        print(f"  {status}: {count}")

print(f"\nUnique agent IDs:")
for agent in sorted(unique_agents, key=lambda x: (x.get('status', ''), x.get('agent_id', ''))):
    status = agent.get('status', 'UNKNOWN')
    agent_id = agent.get('agent_id', 'UNKNOWN')
    heartbeat = agent.get('last_heartbeat', 'N/A')
    print(f"  [{status:15}] {agent_id:50} (heartbeat: {heartbeat[:19] if heartbeat != 'N/A' else 'N/A'})")
