#!/usr/bin/env python3
"""
checkpoint.py - Save working state to survive context compaction

Usage:
  python3 checkpoint.py --auto                          # Quick checkpoint
  python3 checkpoint.py --auto --note "before spawn"    # With note
  python3 checkpoint.py --handoff --task "desc"         # Full handoff
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path("/data/.openclaw/workspace")
WORKING_STATE = WORKSPACE / "WORKING_STATE.md"
MEMORY_DIR = WORKSPACE / "memory"
CHECKPOINT_LOG = MEMORY_DIR / "checkpoint-log.jsonl"


def read_working_state():
    """Read current working state."""
    if WORKING_STATE.exists():
        return WORKING_STATE.read_text()
    return ""


def write_working_state(content):
    """Write updated working state."""
    WORKING_STATE.write_text(content)


def log_checkpoint(checkpoint_type, note=None, task=None):
    """Log checkpoint to JSONL for audit trail."""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": checkpoint_type,
        "note": note,
        "task": task
    }
    
    with open(CHECKPOINT_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")


def auto_checkpoint(note=None):
    """Quick checkpoint - just update timestamp and log."""
    state = read_working_state()
    
    # Update last updated timestamp
    lines = state.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("**Last Updated:**"):
            lines[i] = f"**Last Updated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
            break
    
    write_working_state("\n".join(lines))
    log_checkpoint("auto", note=note)
    
    print(f"✓ Auto-checkpoint saved ({note if note else 'no note'})")


def handoff_checkpoint(task, note=None):
    """Full session handoff - comprehensive state capture."""
    now = datetime.now(timezone.utc)
    timestamp = now.strftime('%Y-%m-%d %H:%M UTC')
    
    # Read current working state
    state = read_working_state()
    
    # Create handoff entry
    handoff = f"""

## Checkpoint: {timestamp}

**Task:** {task}
**Note:** {note if note else 'Session checkpoint'}

**Context at this point:**
- Active work preserved above
- Next session should continue from "Next Steps"
- All key decisions documented in "Key Decisions Made"

"""
    
    # Append to checkpoint log in working state
    if "## Checkpoint Log" in state:
        # Insert before checkpoint log table
        parts = state.split("## Checkpoint Log")
        checkpoint_table_start = parts[1].find("|")
        if checkpoint_table_start != -1:
            # Add entry to checkpoint log section
            state = parts[0] + handoff + "## Checkpoint Log" + parts[1]
    else:
        # No checkpoint log yet, append at end
        state += handoff
    
    write_working_state(state)
    
    # Also write to daily log
    today = now.strftime("%Y-%m-%d")
    daily_log = MEMORY_DIR / f"{today}.md"
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(daily_log, "a") as f:
        f.write(f"\n## Session Checkpoint - {now.strftime('%H:%M UTC')}\n\n")
        f.write(f"**Task:** {task}\n")
        f.write(f"**Note:** {note if note else 'Session checkpoint'}\n\n")
        f.write("State captured in WORKING_STATE.md\n\n")
    
    log_checkpoint("handoff", note=note, task=task)
    
    print(f"✓ Full handoff checkpoint saved")
    print(f"  - WORKING_STATE.md updated")
    print(f"  - Daily log entry: {daily_log}")


def main():
    parser = argparse.ArgumentParser(description="OpenClaw checkpoint tool")
    parser.add_argument("--auto", action="store_true", help="Quick checkpoint")
    parser.add_argument("--handoff", action="store_true", help="Full session handoff")
    parser.add_argument("--note", help="Optional note")
    parser.add_argument("--task", help="Task description (for handoff)")
    
    args = parser.parse_args()
    
    if args.handoff:
        if not args.task:
            print("Error: --handoff requires --task")
            return 1
        handoff_checkpoint(args.task, args.note)
    elif args.auto:
        auto_checkpoint(args.note)
    else:
        parser.print_help()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
