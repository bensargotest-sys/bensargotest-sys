#!/usr/bin/env python3
"""
Cron Wrapper — Wraps any command and logs results to SQLite.

Usage:
    python3 tools/cron-wrapper.py --job "my-task" -- python3 my_script.py
    python3 tools/cron-wrapper.py --job "backup" -- bash tools/backup.sh
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

# Import the cron-log cli for logging
sys.path.insert(0, str(Path(__file__).parent / 'cron-log'))
from cli import get_db

def main():
    parser = argparse.ArgumentParser(description='Cron Wrapper')
    parser.add_argument('--job', required=True, help='Job name for logging')
    parser.add_argument('--timeout', type=int, default=3600, help='Timeout in seconds')
    parser.add_argument('command', nargs=argparse.REMAINDER, help='Command to run')

    args = parser.parse_args()

    # Remove leading -- if present
    cmd = args.command
    if cmd and cmd[0] == '--':
        cmd = cmd[1:]

    if not cmd:
        print("Error: No command specified")
        sys.exit(1)

    start = time.time()
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=args.timeout
        )
        duration = time.time() - start
        status = 'ok' if result.returncode == 0 else 'error'
        error = result.stderr[:500] if result.returncode != 0 else None
        output = result.stdout[:1000]

        conn = get_db()
        conn.execute(
            "INSERT INTO cron_runs (job_name, status, duration_sec, error, output) VALUES (?, ?, ?, ?, ?)",
            (args.job, status, duration, error, output)
        )
        conn.commit()
        print(f"[{args.job}] {status} in {duration:.1f}s")

        # Pass through the original exit code
        sys.exit(result.returncode)

    except subprocess.TimeoutExpired:
        duration = time.time() - start
        conn = get_db()
        conn.execute(
            "INSERT INTO cron_runs (job_name, status, duration_sec, error) VALUES (?, ?, ?, ?)",
            (args.job, 'timeout', duration, f'Killed after {args.timeout}s')
        )
        conn.commit()
        print(f"[{args.job}] TIMEOUT after {args.timeout}s")
        sys.exit(1)

    except Exception as e:
        duration = time.time() - start
        conn = get_db()
        conn.execute(
            "INSERT INTO cron_runs (job_name, status, duration_sec, error) VALUES (?, ?, ?, ?)",
            (args.job, 'error', duration, str(e)[:500])
        )
        conn.commit()
        print(f"[{args.job}] ERROR: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
