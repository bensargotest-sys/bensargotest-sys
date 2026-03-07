#!/usr/bin/env python3
"""
subagent_log.py - Track subagent spawns and prevent cascade failures

Usage:
    python3 tools/subagent_log.py log "agent-name-task" "started"
    python3 tools/subagent_log.py log "agent-name-task" "completed" --runtime "45s"
    python3 tools/subagent_log.py report
    python3 tools/subagent_log.py recent 10
    python3 tools/subagent_log.py health
    python3 tools/subagent_log.py validate  # Check active-tasks.md structure

Prevents cascade failures by detecting 2+ sequential spawn failures.
Implements Rule #13: State file validation (creates/validates active-tasks.md)
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from usage_logger import log_usage

LOG_FILE = Path(__file__).parent.parent / "memory" / "subagent-log.jsonl"
ACTIVE_TASKS = Path(__file__).parent.parent / "active-tasks.md"

DEFAULT_ACTIVE_TASKS_CONTENT = """# Active Tasks

**Purpose:** Track running subagents and prevent duplicate spawns  
**Updated:** {timestamp}

## Currently Running

(None)

## Completed Today

(None)

## Notes

This file is automatically managed by subagent_log.py (Rule #13: State File Validation).
If this file disappears, it will be recreated with this default structure.
"""

def ensure_active_tasks_exists():
    """
    Ensure active-tasks.md exists with valid structure.
    Implements Rule #13: State File Validation Before Updates.
    """
    if not ACTIVE_TASKS.exists():
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        content = DEFAULT_ACTIVE_TASKS_CONTENT.format(timestamp=timestamp)
        ACTIVE_TASKS.write_text(content)
        print(f"⚠️  active-tasks.md was missing, recreated with default structure")
        return False  # File didn't exist
    
    # Validate structure
    try:
        content = ACTIVE_TASKS.read_text()
        required_sections = ["# Active Tasks", "## Currently Running", "## Completed Today"]
        
        for section in required_sections:
            if section not in content:
                print(f"⚠️  active-tasks.md missing section: {section}, rebuilding")
                timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                new_content = DEFAULT_ACTIVE_TASKS_CONTENT.format(timestamp=timestamp)
                ACTIVE_TASKS.write_text(new_content)
                return False  # Structure was invalid
        
        return True  # File exists and structure is valid
    
    except Exception as e:
        print(f"❌ Error validating active-tasks.md: {e}")
        # If we can't read it, recreate it
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        content = DEFAULT_ACTIVE_TASKS_CONTENT.format(timestamp=timestamp)
        ACTIVE_TASKS.write_text(content)
        return False

def validate_active_tasks():
    """Validate active-tasks.md structure (command interface)."""
    print("Validating active-tasks.md...")
    
    if ensure_active_tasks_exists():
        print("✅ active-tasks.md exists with valid structure")
        
        # Show current content summary
        content = ACTIVE_TASKS.read_text()
        running = content.count("[RUNNING]")
        completed = content.count("[COMPLETED]") + content.count("[CLEANED]")
        
        print(f"   Currently tracking: {running} running, {completed} completed")
    else:
        print("⚠️  active-tasks.md was missing or invalid, recreated")

def log_spawn(label, status, runtime=None):
    """Log a subagent spawn event."""
    # Ensure active-tasks.md exists before logging (Rule #13)
    ensure_active_tasks_exists()
    
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "label": label,
        "status": status,
        "runtime": runtime
    }
    
    LOG_FILE.parent.mkdir(exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    
    print(f"✓ Logged: {label} → {status}" + (f" ({runtime})" if runtime else ""))

def read_logs():
    """Read all log entries."""
    if not LOG_FILE.exists():
        return []
    
    logs = []
    with open(LOG_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    logs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return logs

def recent_logs(count=10):
    """Show recent log entries."""
    logs = read_logs()
    recent = logs[-count:] if len(logs) > count else logs
    
    if not recent:
        print("No subagent logs found.")
        return
    
    print(f"\n📋 Last {len(recent)} Subagent Spawns:\n")
    for entry in recent:
        timestamp = entry['timestamp'][:19].replace('T', ' ')
        label = entry['label']
        status = entry['status']
        runtime = entry.get('runtime', 'N/A')
        
        status_icon = "✅" if status == "completed" else "🚀" if status == "started" else "❌"
        print(f"{status_icon} [{timestamp}] {label} → {status} ({runtime})")

def report():
    """Generate health report."""
    logs = read_logs()
    
    if not logs:
        print("No subagent logs found.")
        return
    
    total = len(logs)
    started = sum(1 for e in logs if e['status'] == 'started')
    completed = sum(1 for e in logs if e['status'] == 'completed')
    failed = sum(1 for e in logs if e['status'] == 'failed')
    
    success_rate = (completed / started * 100) if started > 0 else 0
    
    print(f"\n📊 Subagent Health Report\n")
    print(f"Total Spawns:    {total}")
    print(f"Started:         {started}")
    print(f"Completed:       {completed}")
    print(f"Failed:          {failed}")
    print(f"Success Rate:    {success_rate:.1f}%")
    
    # Check for cascade failures (2+ sequential failures)
    recent = logs[-10:]
    failures = [e for e in recent if e['status'] == 'failed']
    
    if len(failures) >= 2:
        # Check if failures are sequential
        recent_statuses = [e['status'] for e in recent[-5:]]
        sequential_failures = sum(1 for s in recent_statuses if s == 'failed')
        
        if sequential_failures >= 2:
            print(f"\n⚠️  WARNING: {sequential_failures} sequential failures detected!")
            print("   Consider changing approach before spawning more agents.")

def health_check():
    """Quick health check for heartbeat integration."""
    logs = read_logs()
    
    if not logs:
        print("HEALTHY")
        return
    
    recent = logs[-5:]
    failures = sum(1 for e in recent if e['status'] == 'failed')
    
    if failures >= 2:
        print("CASCADE_RISK")
    else:
        print("HEALTHY")

@log_usage
def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "log":
        if len(sys.argv) < 4:
            print("Usage: subagent_log.py log <label> <status> [--runtime <time>]")
            sys.exit(1)
        
        label = sys.argv[2]
        status = sys.argv[3]
        runtime = None
        
        if "--runtime" in sys.argv:
            runtime_idx = sys.argv.index("--runtime")
            if runtime_idx + 1 < len(sys.argv):
                runtime = sys.argv[runtime_idx + 1]
        
        log_spawn(label, status, runtime)
    
    elif command == "report":
        report()
    
    elif command == "recent":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        recent_logs(count)
    
    elif command == "health":
        health_check()
    
    elif command == "validate":
        validate_active_tasks()
    
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()
