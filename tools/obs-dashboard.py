#!/usr/bin/env python3
"""
Observability Dashboard — Lightweight cron cost + health tracking.
No external deps. Writes to data/obs.json and data/obs-daily.json.

Usage:
    python3 tools/obs-dashboard.py track <job_name> <model> <status> [duration_s]
    python3 tools/obs-dashboard.py report [--days N]
    python3 tools/obs-dashboard.py cost [--days N]
"""

import json, sys, os
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

OBS_PATH = Path("/data/.openclaw/workspace/data/obs.jsonl")
DAILY_PATH = Path("/data/.openclaw/workspace/data/obs-daily.json")

# Cost per 1M tokens (input) - approximate
MODEL_COSTS = {
    "claude-opus-4-6": 15.00,
    "anthropic/claude-opus-4-6": 15.00,
    "claude-sonnet-4-5": 3.00,
    "anthropic/claude-sonnet-4-5": 3.00,
    "xai/grok-4-1-fast-non-reasoning": 0.30,
    "xai/grok-3": 3.00,
    "xai/grok-4-1-fast-reasoning": 2.00,
}

AVG_CRON_TOKENS = 30000  # ~30k tokens per cron run

def track(job_name, model, status, duration_s=0):
    """Log a cron run."""
    entry = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "job": job_name,
        "model": model,
        "status": status,
        "duration_s": float(duration_s),
        "est_cost": (AVG_CRON_TOKENS / 1_000_000) * MODEL_COSTS.get(model, 1.0)
    }
    OBS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OBS_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"Tracked: {job_name} ({model}) = ${entry['est_cost']:.4f}")

def load_entries(days=7):
    """Load entries from last N days."""
    if not OBS_PATH.exists():
        return []
    cutoff_dt = datetime.utcnow() - timedelta(days=days)
    cutoff_ts = int(cutoff_dt.timestamp() * 1000)
    entries = []
    for line in OBS_PATH.read_text().strip().split("\n"):
        if not line:
            continue
        e = json.loads(line)
        if e["ts"] >= cutoff_ts:
            entries.append(e)
    return entries

def report(days=7):
    """Print summary report."""
    entries = load_entries(days)
    if not entries:
        print(f"No data in last {days} days.")
        return

    by_job = defaultdict(lambda: {"runs": 0, "errors": 0, "cost": 0, "duration": 0})
    by_model = defaultdict(lambda: {"runs": 0, "cost": 0})
    total_cost = 0

    for e in entries:
        j = by_job[e.get("job") or e.get("job_name", "unknown")]
        j["runs"] += 1
        j["cost"] += e.get("est_cost", 0)
        j["duration"] += e.get("duration_s", 0)
        if e["status"] != "ok":
            j["errors"] += 1

        m = by_model[e.get("model", "unknown")]
        m["runs"] += 1
        m["cost"] += e.get("est_cost", 0)
        total_cost += e.get("est_cost", 0)

    print(f"=== Observability Report ({days} days) ===")
    print(f"Total runs: {len(entries)} | Total est. cost: ${total_cost:.2f}")
    print(f"\n--- By Model ---")
    for model, d in sorted(by_model.items(), key=lambda x: -x[1]["cost"]):
        print(f"  {model}: {d['runs']} runs, ${d['cost']:.2f}")
    print(f"\n--- By Job (top 10 by cost) ---")
    for job, d in sorted(by_job.items(), key=lambda x: -x[1]["cost"])[:10]:
        err_str = f" ({d['errors']} errors)" if d["errors"] else ""
        print(f"  {job}: {d['runs']} runs, ${d['cost']:.2f}, avg {d['duration']/max(d['runs'],1):.1f}s{err_str}")

def cost(days=7):
    """Print cost breakdown."""
    entries = load_entries(days)
    daily = defaultdict(float)
    for e in entries:
        day = datetime.utcfromtimestamp(e["ts"] / 1000).strftime("%Y-%m-%d")
        daily[day] += e.get("est_cost", 0)
    
    print(f"=== Daily Cost ({days} days) ===")
    for day in sorted(daily.keys()):
        bar = "█" * int(daily[day] * 10)
        print(f"  {day}: ${daily[day]:.2f} {bar}")
    total = sum(daily.values())
    avg = total / max(len(daily), 1)
    print(f"\n  Total: ${total:.2f} | Avg/day: ${avg:.2f} | Projected/mo: ${avg*30:.2f}")

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)
    
    cmd = args[0]
    if cmd == "track":
        track(args[1], args[2], args[3], args[4] if len(args) > 4 else 0)
    elif cmd == "report":
        days = int(args[2]) if len(args) > 2 and args[1] == "--days" else 7
        report(days)
    elif cmd == "cost":
        days = int(args[2]) if len(args) > 2 and args[1] == "--days" else 7
        cost(days)
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
