#!/usr/bin/env python3
"""
Compaction Advisor — Monitors context window usage and advises on compaction.

Usage:
    python3 tools/compaction/compaction_advisor.py check     # Score 0-100 (higher = more urgent)
    python3 tools/compaction/compaction_advisor.py snapshot   # Save state before compaction
    python3 tools/compaction/compaction_advisor.py history    # Show snapshot history
"""

import argparse
import json
import glob
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path("/data/.openclaw/workspace")
SNAPSHOTS_DIR = WORKSPACE / "data" / "compaction-snapshots"
SESSIONS_DIR = Path("/data/.openclaw/agents/main/sessions")

def get_session_sizes():
    """Get sizes of active session files"""
    sessions = {}
    for f in SESSIONS_DIR.glob("*.jsonl"):
        if f.name.endswith('.lock'):
            continue
        size_kb = f.stat().st_size / 1024
        sessions[f.stem] = {
            "file": f.name,
            "size_kb": round(size_kb, 1),
            "lines": sum(1 for _ in open(f))
        }
    return sessions

def check(args):
    """Score compaction urgency 0-100"""
    sessions = get_session_sizes()
    
    if not sessions:
        print("Score: 0/100 — No sessions found")
        return

    # Find largest session (likely main)
    largest = max(sessions.values(), key=lambda s: s['size_kb'])
    total_kb = sum(s['size_kb'] for s in sessions.values())
    total_lines = sum(s['lines'] for s in sessions.values())

    # Scoring factors
    score = 0
    reasons = []

    # Largest session size (0-40 points)
    if largest['size_kb'] > 500:
        score += min(40, int((largest['size_kb'] - 500) / 50))
        reasons.append(f"Largest session: {largest['size_kb']:.0f}KB")
    
    # Total sessions size (0-20 points)
    if total_kb > 1000:
        score += min(20, int((total_kb - 1000) / 100))
        reasons.append(f"Total session data: {total_kb:.0f}KB")

    # Line count (0-20 points)
    if largest['lines'] > 200:
        score += min(20, int((largest['lines'] - 200) / 20))
        reasons.append(f"Largest session: {largest['lines']} messages")

    # Number of sessions (0-10 points)
    if len(sessions) > 10:
        score += min(10, len(sessions) - 10)
        reasons.append(f"{len(sessions)} active sessions")

    # Memory file bloat (0-10 points)
    mem_files = list(WORKSPACE.glob("memory/*.md"))
    mem_total_kb = sum(f.stat().st_size / 1024 for f in mem_files)
    if mem_total_kb > 500:
        score += min(10, int((mem_total_kb - 500) / 100))
        reasons.append(f"Memory files: {mem_total_kb:.0f}KB")

    score = min(100, score)

    # Output
    if score < 20:
        status = "🟢 LOW"
        advice = "No action needed."
    elif score < 50:
        status = "🟡 MODERATE"
        advice = "Consider compacting if spawning heavy sub-agents."
    elif score < 80:
        status = "🔴 HIGH"
        advice = "Compact soon. Take a snapshot first."
    else:
        status = "🔴 CRITICAL"
        advice = "Compact NOW. Context window at risk."

    print(f"Compaction Score: {score}/100 — {status}")
    print(f"Advice: {advice}")
    if reasons:
        print(f"Factors:")
        for r in reasons:
            print(f"  - {r}")
    print(f"\nSessions: {len(sessions)} | Total: {total_kb:.0f}KB | Largest: {largest['size_kb']:.0f}KB ({largest['lines']} lines)")

def snapshot(args):
    """Save current state before compaction"""
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(tz=timezone.utc).strftime('%Y%m%d-%H%M%S')

    sessions = get_session_sizes()
    snap = {
        "timestamp": datetime.now(tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        "sessions": sessions,
        "total_kb": sum(s['size_kb'] for s in sessions.values()),
        "total_lines": sum(s['lines'] for s in sessions.values()),
        "session_count": len(sessions)
    }

    snap_path = SNAPSHOTS_DIR / f"snapshot-{ts}.json"
    snap_path.write_text(json.dumps(snap, indent=2))
    print(f"Snapshot saved: {snap_path.name}")
    print(f"  Sessions: {snap['session_count']} | Total: {snap['total_kb']:.0f}KB | Lines: {snap['total_lines']}")

def history(args):
    """Show snapshot history"""
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    snaps = sorted(SNAPSHOTS_DIR.glob("snapshot-*.json"))
    if not snaps:
        print("No snapshots yet. Run: compaction_advisor.py snapshot")
        return
    
    print(f"{'TIMESTAMP':<22} {'SESSIONS':<10} {'SIZE':<10} {'LINES'}")
    print("-" * 55)
    for s in snaps[-10:]:
        data = json.loads(s.read_text())
        print(f"{data['timestamp']:<22} {data['session_count']:<10} {data['total_kb']:.0f}KB{'':<5} {data['total_lines']}")

def main():
    parser = argparse.ArgumentParser(description='Compaction Advisor')
    sub = parser.add_subparsers(dest='command')
    sub.add_parser('check', help='Score compaction urgency 0-100')
    sub.add_parser('snapshot', help='Save state before compaction')
    sub.add_parser('history', help='Show snapshot history')

    args = parser.parse_args()
    if args.command == 'check': check(args)
    elif args.command == 'snapshot': snapshot(args)
    elif args.command == 'history': history(args)
    else: parser.print_help()

if __name__ == '__main__':
    main()
