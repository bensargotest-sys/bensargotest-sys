#!/usr/bin/env python3
"""
enforcement_watchdog.py - Check compliance with ENFORCEMENT.md gates

Usage:
    python3 tools/enforcement_watchdog.py check
    python3 tools/enforcement_watchdog.py report

Monitors adherence to enforcement gates and reports violations.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

WORKING_STATE = Path(__file__).parent.parent / "WORKING_STATE.md"
CHECKPOINT_LOG = Path(__file__).parent.parent / "memory" / "checkpoint-log.jsonl"
SUBAGENT_LOG = Path(__file__).parent.parent / "memory" / "subagent-log.jsonl"

def check_working_state_freshness():
    """Gate 4: Check if WORKING_STATE.md is stale."""
    if not WORKING_STATE.exists():
        return "MISSING", "WORKING_STATE.md does not exist"
    
    stat = WORKING_STATE.stat()
    age_seconds = (datetime.now().timestamp() - stat.st_mtime)
    age_hours = age_seconds / 3600
    
    if age_hours > 2:
        return "STALE", f"WORKING_STATE.md not updated in {age_hours:.1f} hours"
    
    return "OK", "WORKING_STATE.md is fresh"

def check_checkpoint_frequency():
    """Gate 4: Check if checkpoints are happening regularly."""
    if not CHECKPOINT_LOG.exists():
        return "WARNING", "No checkpoint log found"
    
    with open(CHECKPOINT_LOG, "r") as f:
        lines = f.readlines()
    
    if not lines:
        return "WARNING", "No checkpoints logged"
    
    try:
        last_checkpoint = json.loads(lines[-1].strip())
        last_time = datetime.fromisoformat(last_checkpoint['timestamp'].replace('Z', '+00:00'))
        hours_since = (datetime.now(timezone.utc) - last_time).total_seconds() / 3600
        
        if hours_since > 4:
            return "WARNING", f"Last checkpoint {hours_since:.1f} hours ago"
        
        return "OK", f"Last checkpoint {hours_since:.1f} hours ago"
    except (json.JSONDecodeError, KeyError):
        return "WARNING", "Could not parse checkpoint log"

def check_subagent_success_rate():
    """Gate 1: Check if subagents are succeeding (>80% target)."""
    if not SUBAGENT_LOG.exists():
        return "OK", "No subagents spawned yet"
    
    with open(SUBAGENT_LOG, "r") as f:
        entries = [json.loads(line.strip()) for line in f if line.strip()]
    
    if not entries:
        return "OK", "No subagents spawned yet"
    
    started = sum(1 for e in entries if e['status'] == 'started')
    completed = sum(1 for e in entries if e['status'] == 'completed')
    
    if started == 0:
        return "OK", "No subagents spawned yet"
    
    success_rate = (completed / started) * 100
    
    if success_rate < 80:
        return "WARNING", f"Subagent success rate: {success_rate:.1f}% (target >80%)"
    
    return "OK", f"Subagent success rate: {success_rate:.1f}%"

def check_session_start_checklist():
    """Check if session start checklist is being followed."""
    # Heuristic: Check if WORKING_STATE.md was read at session start
    # (difficult to enforce programmatically without agent instrumentation)
    return "MANUAL", "Session start checklist requires manual verification"

def check():
    """Run all compliance checks."""
    checks = [
        ("Working State Freshness", check_working_state_freshness),
        ("Checkpoint Frequency", check_checkpoint_frequency),
        ("Subagent Success Rate", check_subagent_success_rate),
        ("Session Start Checklist", check_session_start_checklist),
    ]
    
    print("\n🔍 Enforcement Watchdog Report\n")
    
    violations = 0
    warnings = 0
    
    for name, check_func in checks:
        status, message = check_func()
        
        if status == "OK":
            icon = "✅"
        elif status == "WARNING":
            icon = "⚠️ "
            warnings += 1
        elif status == "MANUAL":
            icon = "📋"
        else:  # MISSING, STALE
            icon = "❌"
            violations += 1
        
        print(f"{icon} {name}: {message}")
    
    print()
    
    if violations > 0:
        print(f"⚠️  {violations} violation(s) detected")
    elif warnings > 0:
        print(f"⚠️  {warnings} warning(s) - review recommended")
    else:
        print("✓ All enforcement gates healthy")
    
    return violations

def report():
    """Generate detailed report."""
    print("\n📊 Detailed Enforcement Report\n")
    
    # Working state
    ws_status, ws_msg = check_working_state_freshness()
    print(f"**Working State:** {ws_msg}")
    
    # Checkpoints
    cp_status, cp_msg = check_checkpoint_frequency()
    print(f"**Checkpoints:** {cp_msg}")
    
    # Subagents
    sa_status, sa_msg = check_subagent_success_rate()
    print(f"**Subagents:** {sa_msg}")
    
    print("\n**Recommendations:**")
    
    if ws_status in ["STALE", "MISSING"]:
        print("- Update WORKING_STATE.md with current task and decisions")
    
    if cp_status == "WARNING":
        print("- Run checkpoint.py after significant work")
    
    if sa_status == "WARNING":
        print("- Review recent subagent failures")
        print("- Check spawn templates for clarity")
        print("- Verify file paths exist before spawning")
    
    print()

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "check":
        violations = check()
        sys.exit(1 if violations > 0 else 0)
    
    elif command == "report":
        report()
    
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()
