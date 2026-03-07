#!/usr/bin/env python3
"""
Cron Cost Analyzer
Tracks daily cron job costs and appends to data/obs.jsonl
"""

import json
from datetime import datetime, timezone
from pathlib import Path

# Model pricing (per token)
MODEL_PRICING = {
    "gemini/gemini-2.0-flash": 0.0,  # Free
    "xai/grok-4-1-fast-non-reasoning": 0.0,  # Free
    "xai/grok-3": 0.000003,
    "anthropic/claude-sonnet-4-5": 0.000003,
    "anthropic/claude-opus-4-6": 0.000015,
    "openai/gpt-4o": 0.0000025,
    "openai/gpt-4o-mini": 0.00000015,
}

def get_today_start_ms():
    """Get timestamp in ms for start of today (UTC)"""
    now = datetime.now(timezone.utc)
    today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    return int(today_start.timestamp() * 1000)

def estimate_cost(model, duration_ms):
    """Estimate cost based on model and duration"""
    # Very rough estimate: ~1000 tokens per second of execution
    estimated_tokens = (duration_ms / 1000) * 1000
    price_per_token = MODEL_PRICING.get(model, 0.000003)  # Default to $3/M tokens
    return estimated_tokens * price_per_token

def main():
    # Read jobs.json
    jobs_path = Path("/data/.openclaw/cron/jobs.json")
    if not jobs_path.exists():
        print("Error: jobs.json not found")
        return
    
    with open(jobs_path) as f:
        data = json.load(f)
    
    jobs = data.get("jobs", [])
    today_start_ms = get_today_start_ms()
    
    # Filter jobs that ran today
    today_jobs = []
    for job in jobs:
        state = job.get("state", {})
        last_run = state.get("lastRunAtMs")
        if last_run and last_run >= today_start_ms:
            today_jobs.append({
                "name": job.get("name", "Unknown"),
                "model": job.get("payload", {}).get("model", "unknown"),
                "status": state.get("lastStatus", "unknown"),
                "duration_ms": state.get("lastDurationMs", 0),
                "last_run_ms": last_run
            })
    
    # Append to obs.jsonl
    obs_path = Path("data/obs.jsonl")
    obs_path.parent.mkdir(exist_ok=True)
    
    total_cost = 0.0
    
    with open(obs_path, "a") as f:
        for job in today_jobs:
            cost = estimate_cost(job["model"], job["duration_ms"])
            total_cost += cost
            
            entry = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "type": "cron_cost",
                "job": job["name"],
                "model": job["model"],
                "status": job["status"],
                "duration_ms": job["duration_ms"],
                "cost_usd": round(cost, 6)
            }
            f.write(json.dumps(entry) + "\n")
    
    print(f"Total estimated cost for {datetime.now(timezone.utc).strftime('%Y-%m-%d')}: ${total_cost:.6f}")
    print(f"Jobs tracked: {len(today_jobs)}")

if __name__ == "__main__":
    main()
