#!/usr/bin/env python3
"""
Cron Health Check — Detects stuck, failing, or overdue cron jobs.

Usage:
    python3 tools/cron-health-check.py          # Human-readable output
    python3 tools/cron-health-check.py --json    # JSON output

Exit codes: 0 = healthy, 1 = issues found

Checks:
- Jobs with 3+ consecutive errors
- Jobs that haven't run in 2x their interval
- Jobs that took >2h (stuck)
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def load_cron_jobs():
    """Load cron jobs from OpenClaw's session files"""
    # Try reading from the cron list via the state
    # Try OpenClaw's actual cron jobs location
    for p in [
        Path("/data/.openclaw/cron/jobs.json"),
        Path("/data/.openclaw/sessions/cron-jobs.json"),
    ]:
        if p.exists():
            data = json.loads(p.read_text())
            return data if isinstance(data, list) else data.get("jobs", [])
    return []

def check_health(jobs, as_json=False):
    issues = []
    now_ms = int(datetime.now(tz=__import__("datetime").timezone.utc).timestamp() * 1000)

    for job in jobs:
        if not job.get('enabled', True):
            continue

        name = job.get('name', job.get('id', 'unknown'))
        state = job.get('state', {})
        schedule = job.get('schedule', {})

        # Check consecutive errors
        consec = state.get('consecutiveErrors', 0)
        if consec >= 3:
            issues.append({
                'job': name,
                'type': 'consecutive_failures',
                'detail': f'{consec} consecutive errors',
                'lastError': state.get('lastError', ''),
                'severity': 'critical'
            })

        # Check last error
        if state.get('lastStatus') == 'error':
            err = state.get('lastError', 'unknown')
            if consec < 3:  # Already caught above
                issues.append({
                    'job': name,
                    'type': 'last_run_failed',
                    'detail': err[:100],
                    'severity': 'warning'
                })

        # Check overdue (2x interval)
        last_run = state.get('lastRunAtMs')
        if last_run and schedule.get('kind') == 'every':
            interval = schedule.get('everyMs', 0)
            if interval > 0 and (now_ms - last_run) > interval * 2:
                overdue_h = (now_ms - last_run - interval) / 3600000
                issues.append({
                    'job': name,
                    'type': 'overdue',
                    'detail': f'Overdue by {overdue_h:.1f}h',
                    'severity': 'warning'
                })

        # Check stuck (last run >2h duration)
        last_dur = state.get('lastDurationMs', 0)
        if last_dur > 7200000:  # 2 hours
            issues.append({
                'job': name,
                'type': 'stuck',
                'detail': f'Last run took {last_dur/3600000:.1f}h',
                'severity': 'critical'
            })

    result = {
        'healthy': len(issues) == 0,
        'checked': len([j for j in jobs if j.get('enabled', True)]),
        'issues': issues,
        'ts': datetime.now(tz=__import__("datetime").timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    }

    if as_json:
        print(json.dumps(result, indent=2))
    else:
        if result['healthy']:
            print(f"✅ All {result['checked']} cron jobs healthy")
        else:
            print(f"⚠️ {len(issues)} issues found across {result['checked']} jobs:\n")
            for i in issues:
                icon = '🔴' if i['severity'] == 'critical' else '🟡'
                print(f"  {icon} {i['job']}: {i['type']} — {i['detail']}")

    return 0 if result['healthy'] else 1

def main():
    as_json = '--json' in sys.argv

    # Try loading from file first
    jobs = load_cron_jobs()

    if not jobs:
        # If no file, we can't check without the cron tool
        if as_json:
            print(json.dumps({'healthy': True, 'checked': 0, 'issues': [], 'note': 'No cron state file found'}))
        else:
            print("⚠️ No cron state file found at /data/.openclaw/sessions/cron-jobs.json")
            print("   Run via OpenClaw cron tool for live data.")
        sys.exit(0)

    sys.exit(check_health(jobs, as_json))

if __name__ == '__main__':
    main()
