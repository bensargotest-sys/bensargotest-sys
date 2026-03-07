
import json
import datetime
import os

def calculate_cost(model, duration_ms):
    # Simple cost estimation based on model type.  These are guesses.
    if "grok" in model:
        cost_per_ms = 0.000000005  # Placeholder
    elif "gemini" in model:
        cost_per_ms = 0.000000002  # Placeholder
    elif "claude" in model:
        cost_per_ms = 0.00000001   # Placeholder
    else:
        cost_per_ms = 0.000000001  # Default cheap model
    return cost_per_ms * duration_ms

def main():
    today = datetime.date.today()
    jobs_file = "/data/.openclaw/cron/jobs.json"
    obs_file = "data/obs.jsonl"
    total_daily_cost = 0

    try:
        with open(jobs_file, "r") as f:
            jobs_data = json.load(f)
            jobs = jobs_data.get("jobs", [])
    except FileNotFoundError:
        print(f"Error: {jobs_file} not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {jobs_file}")
        return

    for job in jobs:
        if "state" in job and "lastRunAtMs" in job["state"]:
            last_run_date = datetime.date.fromtimestamp(job["state"]["lastRunAtMs"] / 1000)
            if last_run_date == today:
                job_name = job.get("name", "Unnamed Job")
                model = job.get("payload", {}).get("model", "unknown")
                status = job["state"].get("lastStatus", "unknown")
                duration_ms = job["state"].get("lastDurationMs", 0)
                estimated_cost = calculate_cost(model, duration_ms)
                total_daily_cost += estimated_cost

                obs_entry = {
                    "ts": datetime.datetime.utcnow().isoformat(),
                    "job_name": job_name,
                    "model": model,
                    "status": status,
                    "duration_ms": duration_ms,
                    "estimated_cost": estimated_cost
                }
                try:
                    with open(obs_file, "a") as outfile:
                        outfile.write(json.dumps(obs_entry) + "\n")
                except FileNotFoundError:
                    os.makedirs(os.path.dirname(obs_file), exist_ok=True)
                    with open(obs_file, "a") as outfile:
                        outfile.write(json.dumps(obs_entry) + "\n")


    print(f"Total estimated daily cost: ${total_daily_cost:.6f}")

    if total_daily_cost > 5:
        print("ALERT: Daily cost exceeds $5")
    else:
        print("HEARTBEAT_OK")

if __name__ == "__main__":
    main()
