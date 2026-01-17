"""
Script: cleanup__agent_registry.py
Intent:
- temporal

Reads:
- agent-orchestrator/registry/agent-registry.json

Writes:
- agent-orchestrator/registry/agent-registry.json (cleaned)

Schema:
- Same as input (agent registry format)
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

REGISTRY_PATH = PROJECT_ROOT / "registry" / "agent-registry.json"

# Thresholds
STALE_HEARTBEAT_THRESHOLD_HOURS = 1  # Mark as RETIRED if RUNNING > 1 hour with stale heartbeat
STALE_HEARTBEAT_THRESHOLD_SECONDS = STALE_HEARTBEAT_THRESHOLD_HOURS * 3600

def parse_timestamp(ts_str):
    """Parse ISO timestamp to datetime object"""
    if not ts_str:
        return None
    try:
        # Handle both Z and +00:00 formats
        ts_str = ts_str.replace('Z', '+00:00')
        if '+' not in ts_str and 'Z' not in ts_str:
            # Assume UTC if no timezone
            ts_str = ts_str + '+00:00'
        return datetime.fromisoformat(ts_str)
    except Exception:
        return None

def cleanup_registry():
    """Clean up agent registry: deduplicate and mark stale agents as RETIRED"""
    
    if not REGISTRY_PATH.exists():
        print(f"[ERROR] Registry file not found: {REGISTRY_PATH}")
        return False
    
    # Load registry
    print(f"[INFO] Loading registry from {REGISTRY_PATH}")
    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    agents = registry.get("agents", [])
    print(f"[INFO] Found {len(agents)} agent entries")
    
    # Step 1: Deduplicate agents (keep most recent heartbeat per agent_id)
    print("\n[STEP 1] Deduplicating agents...")
    seen = {}
    duplicates_removed = 0
    
    for agent in agents:
        agent_id = agent.get("agent_id", "unknown")
        heartbeat_str = agent.get("last_heartbeat", "")
        heartbeat_dt = parse_timestamp(heartbeat_str)
        
        if agent_id not in seen:
            seen[agent_id] = agent
        else:
            # Compare timestamps to keep most recent
            existing_heartbeat_str = seen[agent_id].get("last_heartbeat", "")
            existing_heartbeat_dt = parse_timestamp(existing_heartbeat_str)
            
            if heartbeat_dt and existing_heartbeat_dt:
                if heartbeat_dt > existing_heartbeat_dt:
                    seen[agent_id] = agent
                    duplicates_removed += 1
                else:
                    duplicates_removed += 1
            elif heartbeat_dt:
                seen[agent_id] = agent
                duplicates_removed += 1
            else:
                duplicates_removed += 1
    
    print(f"   [OK] Removed {duplicates_removed} duplicate entries")
    print(f"   [OK] Kept {len(seen)} unique agents")
    
    # Step 2: Mark stale RUNNING agents as RETIRED
    print("\n[STEP 2] Checking for stale agents...")
    now = datetime.now(timezone.utc)
    stale_marked = 0
    
    for agent_id, agent in seen.items():
        status = agent.get("status", "")
        heartbeat_str = agent.get("last_heartbeat", "")
        heartbeat_dt = parse_timestamp(heartbeat_str)
        
        # Only check RUNNING agents
        if status == "RUNNING" and heartbeat_dt:
            age_seconds = (now - heartbeat_dt).total_seconds()
            
            if age_seconds > STALE_HEARTBEAT_THRESHOLD_SECONDS:
                print(f"   [WARN] Marking {agent_id} as RETIRED (stale for {age_seconds/3600:.1f}h)")
                agent["status"] = "RETIRED"
                agent["current_task"] = f"Auto-retired: stale heartbeat ({age_seconds/3600:.1f}h old)"
                stale_marked += 1
    
    print(f"   [OK] Marked {stale_marked} stale agents as RETIRED")
    
    # Step 3: Update metadata
    print("\n[STEP 3] Updating registry metadata...")
    cleaned_agents = list(seen.values())
    
    # Count by status
    status_counts = {}
    for agent in cleaned_agents:
        status = agent.get("status", "UNKNOWN")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    registry["_meta"] = {
        "registry_version": "1.0",
        "last_updated": now.isoformat() + "Z",
        "total_agents": len(cleaned_agents),
        "active_agents": status_counts.get("RUNNING", 0),
        "idle_agents": status_counts.get("IDLE", 0),
        "waiting_review_agents": status_counts.get("WAITING_REVIEW", 0),
        "blocked_agents": status_counts.get("BLOCKED", 0),
        "retired_agents": status_counts.get("RETIRED", 0),
        "cleaned_at": now.isoformat() + "Z",
        "duplicates_removed": duplicates_removed,
        "stale_agents_retired": stale_marked
    }
    
    registry["agents"] = cleaned_agents
    
    # Step 4: Save cleaned registry
    print("\n[STEP 4] Saving cleaned registry...")
    
    # Create backup
    backup_path = REGISTRY_PATH.with_suffix('.json.backup')
    print(f"   [INFO] Creating backup: {backup_path}")
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2)
    
    # Save cleaned version
    with open(REGISTRY_PATH, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2)
    
    print(f"   [OK] Saved cleaned registry to {REGISTRY_PATH}")
    
    # Summary
    print("\n" + "=" * 80)
    print("[SUCCESS] CLEANUP COMPLETE")
    print("=" * 80)
    print(f"Total agents: {len(cleaned_agents)}")
    print(f"Duplicates removed: {duplicates_removed}")
    print(f"Stale agents retired: {stale_marked}")
    print(f"\nStatus breakdown:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")
    print(f"\nBackup saved to: {backup_path}")
    
    return True

if __name__ == "__main__":
    try:
        success = cleanup_registry()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
