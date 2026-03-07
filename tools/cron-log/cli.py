#!/usr/bin/env python3
"""
Cron Log CLI — SQLite-based cron job logging and querying.

Usage:
    python3 tools/cron-log/cli.py log --job "name" --status ok --duration 5.2 [--error "msg"]
    python3 tools/cron-log/cli.py recent [--limit 20]
    python3 tools/cron-log/cli.py failures [--hours 24]
    python3 tools/cron-log/cli.py stats [--job "name"]
"""

import argparse
import sqlite3
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path("/data/.openclaw/workspace/data/cron-log.db")

def get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cron_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_name TEXT NOT NULL,
            status TEXT NOT NULL,
            duration_sec REAL,
            error TEXT,
            output TEXT,
            ts TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_job ON cron_runs(job_name)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ts ON cron_runs(ts)")
    conn.commit()
    return conn

def log_run(args):
    conn = get_db()
    conn.execute(
        "INSERT INTO cron_runs (job_name, status, duration_sec, error, output) VALUES (?, ?, ?, ?, ?)",
        (args.job, args.status, args.duration, args.error, args.output)
    )
    conn.commit()
    print(f"Logged: {args.job} [{args.status}] {args.duration or 0:.1f}s")

def recent(args):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM cron_runs ORDER BY ts DESC LIMIT ?", (args.limit,)
    ).fetchall()
    if not rows:
        print("No runs recorded yet.")
        return
    print(f"{'TIME':<20} {'JOB':<35} {'STATUS':<8} {'DURATION':<10} {'ERROR'}")
    print("-" * 95)
    for r in rows:
        err = (r['error'] or '')[:40]
        dur = f"{r['duration_sec']:.1f}s" if r['duration_sec'] else '-'
        print(f"{r['ts']:<20} {r['job_name']:<35} {r['status']:<8} {dur:<10} {err}")

def failures(args):
    conn = get_db()
    since = (datetime.now(tz=__import__("datetime").timezone.utc) - timedelta(hours=args.hours)).strftime('%Y-%m-%dT%H:%M:%SZ')
    rows = conn.execute(
        "SELECT * FROM cron_runs WHERE status != 'ok' AND ts > ? ORDER BY ts DESC", (since,)
    ).fetchall()
    if not rows:
        print(f"No failures in last {args.hours}h. ✅")
        return
    print(f"⚠️ {len(rows)} failures in last {args.hours}h:")
    print(f"{'TIME':<20} {'JOB':<35} {'STATUS':<8} {'ERROR'}")
    print("-" * 90)
    for r in rows:
        err = (r['error'] or '')[:50]
        print(f"{r['ts']:<20} {r['job_name']:<35} {r['status']:<8} {err}")

def stats(args):
    conn = get_db()
    if args.job:
        rows = conn.execute("""
            SELECT status, COUNT(*) as cnt, AVG(duration_sec) as avg_dur, MAX(ts) as last_run
            FROM cron_runs WHERE job_name = ? GROUP BY status
        """, (args.job,)).fetchall()
        print(f"Stats for: {args.job}")
    else:
        rows = conn.execute("""
            SELECT job_name, COUNT(*) as total,
                   SUM(CASE WHEN status='ok' THEN 1 ELSE 0 END) as ok_cnt,
                   SUM(CASE WHEN status!='ok' THEN 1 ELSE 0 END) as fail_cnt,
                   AVG(duration_sec) as avg_dur,
                   MAX(ts) as last_run
            FROM cron_runs GROUP BY job_name ORDER BY last_run DESC
        """).fetchall()
        if not rows:
            print("No data yet.")
            return
        print(f"{'JOB':<35} {'TOTAL':<7} {'OK':<5} {'FAIL':<6} {'AVG DUR':<10} {'LAST RUN'}")
        print("-" * 95)
        for r in rows:
            dur = f"{r['avg_dur']:.1f}s" if r['avg_dur'] else '-'
            print(f"{r['job_name']:<35} {r['total']:<7} {r['ok_cnt']:<5} {r['fail_cnt']:<6} {dur:<10} {r['last_run']}")

def main():
    parser = argparse.ArgumentParser(description='Cron Log CLI')
    sub = parser.add_subparsers(dest='command')

    p_log = sub.add_parser('log', help='Log a cron run')
    p_log.add_argument('--job', required=True)
    p_log.add_argument('--status', default='ok')
    p_log.add_argument('--duration', type=float)
    p_log.add_argument('--error')
    p_log.add_argument('--output')

    p_recent = sub.add_parser('recent', help='Show recent runs')
    p_recent.add_argument('--limit', type=int, default=20)

    p_fail = sub.add_parser('failures', help='Show failures')
    p_fail.add_argument('--hours', type=int, default=24)

    p_stats = sub.add_parser('stats', help='Show stats')
    p_stats.add_argument('--job')

    args = parser.parse_args()
    if args.command == 'log': log_run(args)
    elif args.command == 'recent': recent(args)
    elif args.command == 'failures': failures(args)
    elif args.command == 'stats': stats(args)
    else: parser.print_help()

if __name__ == '__main__':
    main()
