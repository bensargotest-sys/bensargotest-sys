#!/usr/bin/env python3
"""
heartbeat_enforcer.py - Prevent lazy heartbeat responses

Usage:
  python3 heartbeat_enforcer.py check     # Verify rate limit & real work
  python3 heartbeat_enforcer.py log <work_description>
"""

import argparse
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

WORKSPACE = Path("/data/.openclaw/workspace")
STATE_FILE = WORKSPACE / "memory" / "heartbeat-state.json"
MIN_INTERVAL_MINUTES = 30


def read_state():
    """Read heartbeat state."""
    if not STATE_FILE.exists():
        return {
            "lastHeartbeat": None,
            "heartbeatWorkItems": 0,
            "consecutiveNoWork": 0,
            "lastMistakeCheck": {
                "toolFailed": False,
                "agentStalled": False,
                "unexpected": False,
                "timestamp": None
            }
        }
    
    with open(STATE_FILE) as f:
        return json.load(f)


def write_state(state):
    """Write heartbeat state."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def check():
    """Check if heartbeat should proceed or be rate-limited."""
    state = read_state()
    
    if state["lastHeartbeat"]:
        last_dt = datetime.fromisoformat(state["lastHeartbeat"])
        now = datetime.now(timezone.utc)
        elapsed = (now - last_dt).total_seconds() / 60
        
        if elapsed < MIN_INTERVAL_MINUTES:
            print(f"RATE_LIMITED")
            print(f"Last heartbeat was {elapsed:.1f} minutes ago")
            print(f"Wait at least {MIN_INTERVAL_MINUTES - elapsed:.1f} more minutes")
            return 1
    
    print("PROCEED")
    
    # Show stats
    print(f"\nHeartbeat Stats:")
    print(f"  Work items completed: {state['heartbeatWorkItems']}")
    print(f"  Consecutive no-work: {state['consecutiveNoWork']}")
    
    if state["consecutiveNoWork"] >= 3:
        print(f"\n⚠️  WARNING: {state['consecutiveNoWork']} heartbeats without real work")
        print("  Consider adding items to heartbeat-backlog.md")
    
    return 0


def log_work(description):
    """Log that real work was done during heartbeat."""
    state = read_state()
    
    state["lastHeartbeat"] = datetime.now(timezone.utc).isoformat()
    state["heartbeatWorkItems"] += 1
    state["consecutiveNoWork"] = 0
    
    write_state(state)
    
    # Also log to work log
    work_log = WORKSPACE / "memory" / "work-log.md"
    work_log.parent.mkdir(parents=True, exist_ok=True)
    
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    
    with open(work_log, "a") as f:
        f.write(f"\n## {now} [Heartbeat]\n")
        f.write(f"{description}\n")
    
    print(f"✓ Work logged: {description[:60]}{'...' if len(description) > 60 else ''}")


def log_no_work():
    """Log that no work was done (for tracking consecutive no-work)."""
    state = read_state()
    
    state["lastHeartbeat"] = datetime.now(timezone.utc).isoformat()
    state["consecutiveNoWork"] += 1
    
    write_state(state)
    
    print(f"⚠️  No work logged (consecutive: {state['consecutiveNoWork']})")


def main():
    parser = argparse.ArgumentParser(description="Heartbeat enforcement")
    subparsers = parser.add_subparsers(dest="command")
    
    # Check command
    subparsers.add_parser("check", help="Check if heartbeat should proceed")
    
    # Log command
    log_parser = subparsers.add_parser("log", help="Log work done")
    log_parser.add_argument("description", help="What was done")
    
    # No-work command
    subparsers.add_parser("no-work", help="Log no work done")
    
    args = parser.parse_args()
    
    if args.command == "check":
        return check()
    elif args.command == "log":
        log_work(args.description)
    elif args.command == "no-work":
        log_no_work()
    else:
        parser.print_help()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
