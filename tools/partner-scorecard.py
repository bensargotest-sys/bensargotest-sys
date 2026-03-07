#!/usr/bin/env python3
"""
Partner Scorecard — Self-accountability metrics for the agent.

Tracks: Reliability, Memory, Autonomy, Quality, Proactive
Each dimension scored 0-10. Updated by cron or manually.

Usage:
    python3 tools/partner-scorecard.py show
    python3 tools/partner-scorecard.py update --reliability 8 --memory 7 --autonomy 9 --quality 8 --proactive 7
    python3 tools/partner-scorecard.py log --dimension reliability --delta -1 --reason "Forgot to follow up on task"
    python3 tools/partner-scorecard.py history [--limit 10]
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCORECARD_PATH = Path("/data/.openclaw/workspace/memory/partner-scorecard.json")

def get_scorecard():
    if SCORECARD_PATH.exists():
        return json.loads(SCORECARD_PATH.read_text())
    return {
        "scores": {
            "reliability": 5.0,
            "memory": 5.0,
            "autonomy": 5.0,
            "quality": 5.0,
            "proactive": 5.0
        },
        "history": [],
        "lastUpdated": None
    }

def save_scorecard(data):
    SCORECARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    data["lastUpdated"] = datetime.now(tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    SCORECARD_PATH.write_text(json.dumps(data, indent=2))

def show(args):
    sc = get_scorecard()
    scores = sc["scores"]
    total = sum(scores.values())
    avg = total / len(scores)

    print("📊 Partner Scorecard")
    print("=" * 40)
    for dim, score in scores.items():
        bar = "█" * int(score) + "░" * (10 - int(score))
        print(f"  {dim:<12} {bar} {score:.1f}/10")
    print("-" * 40)
    print(f"  {'AVERAGE':<12} {'':>10} {avg:.1f}/10")
    print(f"  {'TOTAL':<12} {'':>10} {total:.1f}/50")
    if sc["lastUpdated"]:
        print(f"\n  Last updated: {sc['lastUpdated']}")

    # Recent history
    hist = sc.get("history", [])[-5:]
    if hist:
        print(f"\n  Recent changes:")
        for h in hist:
            sign = "+" if h["delta"] > 0 else ""
            print(f"    {h['ts'][:10]} {h['dimension']}: {sign}{h['delta']} — {h['reason']}")

def update(args):
    sc = get_scorecard()
    changes = {}
    for dim in ["reliability", "memory", "autonomy", "quality", "proactive"]:
        val = getattr(args, dim, None)
        if val is not None:
            old = sc["scores"][dim]
            sc["scores"][dim] = max(0, min(10, val))
            if old != val:
                changes[dim] = {"old": old, "new": val}
                sc["history"].append({
                    "ts": datetime.now(tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "dimension": dim,
                    "delta": val - old,
                    "reason": f"Manual update: {old} → {val}"
                })

    # Keep last 100 history entries
    sc["history"] = sc["history"][-100:]
    save_scorecard(sc)
    print(f"Updated {len(changes)} dimensions.")
    show(args)

def log_change(args):
    sc = get_scorecard()
    dim = args.dimension
    if dim not in sc["scores"]:
        print(f"Unknown dimension: {dim}")
        return
    old = sc["scores"][dim]
    new = max(0, min(10, old + args.delta))
    sc["scores"][dim] = new
    sc["history"].append({
        "ts": datetime.now(tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        "dimension": dim,
        "delta": args.delta,
        "reason": args.reason or "No reason given"
    })
    sc["history"] = sc["history"][-100:]
    save_scorecard(sc)
    sign = "+" if args.delta > 0 else ""
    print(f"{dim}: {old:.1f} → {new:.1f} ({sign}{args.delta}) — {args.reason}")

def history(args):
    sc = get_scorecard()
    hist = sc.get("history", [])
    if not hist:
        print("No history yet.")
        return
    for h in hist[-(args.limit):]:
        sign = "+" if h["delta"] > 0 else ""
        print(f"  {h['ts'][:16]} {h['dimension']:<12} {sign}{h['delta']:>+.1f}  {h['reason']}")

def main():
    parser = argparse.ArgumentParser(description='Partner Scorecard')
    sub = parser.add_subparsers(dest='command')

    sub.add_parser('show', help='Show current scores')

    p_upd = sub.add_parser('update', help='Set scores directly')
    for dim in ["reliability", "memory", "autonomy", "quality", "proactive"]:
        p_upd.add_argument(f'--{dim}', type=float)

    p_log = sub.add_parser('log', help='Log a score change')
    p_log.add_argument('--dimension', required=True)
    p_log.add_argument('--delta', type=float, required=True)
    p_log.add_argument('--reason')

    p_hist = sub.add_parser('history', help='Show change history')
    p_hist.add_argument('--limit', type=int, default=20)

    args = parser.parse_args()
    if args.command == 'show': show(args)
    elif args.command == 'update': update(args)
    elif args.command == 'log': log_change(args)
    elif args.command == 'history': history(args)
    else: parser.print_help()

if __name__ == '__main__':
    main()
