#!/usr/bin/env python3
"""
heartbeat_integrations.py - Rotate through integration checks on heartbeats

Implements the rotation schedule from HEARTBEAT.md:
- Every heartbeat: position checks, activity logging
- Every 2nd: self-evaluation, preference scanning
- Every 3rd: memory consolidation, pattern analysis
- Every 5th: full memory review, skill usage audit

Usage:
    python3 tools/heartbeat_integrations.py next     # Get next scheduled task
    python3 tools/heartbeat_integrations.py run      # Run next task and mark complete
    python3 tools/heartbeat_integrations.py status   # Show rotation status
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

WORKSPACE = Path("/data/.openclaw/workspace")
STATE_FILE = WORKSPACE / "memory" / "heartbeat-state.json"
WORK_LOG = WORKSPACE / "memory" / "work-log.md"

# Rotation schedule (task_id, frequency, description)
ROTATION_TASKS = [
    # Every heartbeat
    ("position_check", 1, "Check trading positions (if applicable)"),
    ("activity_log", 1, "Log current activity state"),
    
    # Every 2nd heartbeat
    ("self_eval", 2, "Run self-evaluation on recent work"),
    ("preference_scan", 2, "Scan for new user preferences"),
    
    # Every 3rd heartbeat
    ("memory_consolidation", 3, "Check if daily logs need consolidation"),
    ("pattern_analysis", 3, "Analyze patterns in recent interactions"),
    
    # Every 5th heartbeat
    ("full_memory_review", 5, "Full MEMORY.md review and update"),
    ("skill_audit", 5, "Audit tool and skill usage patterns"),
]

def load_state():
    """Load heartbeat state"""
    if not STATE_FILE.exists():
        return {
            "heartbeatCount": 0,
            "lastChecks": {},
            "rotationStatus": {}
        }
    
    with open(STATE_FILE, "r") as f:
        return json.load(f)

def save_state(state):
    """Save heartbeat state"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def get_next_tasks(heartbeat_count):
    """Get tasks scheduled for this heartbeat"""
    tasks = []
    for task_id, frequency, description in ROTATION_TASKS:
        if heartbeat_count % frequency == 0:
            tasks.append({
                "id": task_id,
                "frequency": frequency,
                "description": description
            })
    return tasks

def mark_task_complete(task_id):
    """Mark a task as complete in rotation status"""
    state = load_state()
    
    if "rotationStatus" not in state:
        state["rotationStatus"] = {}
    
    state["rotationStatus"][task_id] = {
        "lastRun": datetime.now(timezone.utc).isoformat(),
        "heartbeat": state["heartbeatCount"]
    }
    
    save_state(state)

def get_status():
    """Get rotation status report"""
    state = load_state()
    heartbeat_count = state.get("heartbeatCount", 0)
    rotation = state.get("rotationStatus", {})
    
    status = {
        "heartbeatCount": heartbeat_count,
        "nextHeartbeat": heartbeat_count + 1,
        "upcomingTasks": get_next_tasks(heartbeat_count + 1),
        "recentRuns": []
    }
    
    # Sort by last run time
    for task_id, info in sorted(
        rotation.items(),
        key=lambda x: x[1].get("lastRun", ""),
        reverse=True
    )[:10]:
        task_desc = next(
            (desc for tid, _, desc in ROTATION_TASKS if tid == task_id),
            task_id
        )
        status["recentRuns"].append({
            "task": task_id,
            "description": task_desc,
            "lastRun": info.get("lastRun"),
            "heartbeat": info.get("heartbeat")
        })
    
    return status

def main():
    if len(sys.argv) < 2:
        print("Usage: heartbeat_integrations.py next|run|status")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "next":
        state = load_state()
        heartbeat_count = state.get("heartbeatCount", 0)
        tasks = get_next_tasks(heartbeat_count + 1)
        
        if tasks:
            print(f"📋 Next heartbeat ({heartbeat_count + 1}) tasks:")
            for task in tasks:
                print(f"  • {task['description']} (every {task['frequency']})")
        else:
            print(f"⏭️  No rotation tasks for heartbeat {heartbeat_count + 1}")
        
    elif command == "run":
        state = load_state()
        heartbeat_count = state.get("heartbeatCount", 0)
        tasks = get_next_tasks(heartbeat_count + 1)
        
        if not tasks:
            print("⏭️  No tasks scheduled - skipping rotation")
            sys.exit(0)
        
        print(f"🔄 Running rotation tasks for heartbeat {heartbeat_count + 1}:")
        for task in tasks:
            print(f"  ✓ {task['description']}")
            mark_task_complete(task['id'])
        
        print(f"\n✅ Marked {len(tasks)} task(s) complete")
        
    elif command == "status":
        status = get_status()
        print(f"📊 Heartbeat Rotation Status")
        print(f"{'=' * 60}")
        print(f"Current heartbeat: {status['heartbeatCount']}")
        print(f"Next heartbeat: {status['nextHeartbeat']}")
        
        print(f"\n📋 Upcoming tasks (heartbeat {status['nextHeartbeat']}):")
        if status['upcomingTasks']:
            for task in status['upcomingTasks']:
                print(f"  • {task['description']} (every {task['frequency']})")
        else:
            print("  (none)")
        
        if status['recentRuns']:
            print(f"\n⏮️  Recent runs:")
            for run in status['recentRuns']:
                print(f"  • {run['description']}")
                print(f"    Last: {run['lastRun']} (heartbeat {run['heartbeat']})")
        
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
