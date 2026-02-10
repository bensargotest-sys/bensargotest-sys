#!/usr/bin/env python3
"""
monitor_daemon.py - Background monitoring daemon with SQLite storage

Collects system metrics periodically and stores in SQLite for historical analysis.

Usage:
    python3 tools/monitor_daemon.py start [--interval 300]
    python3 tools/monitor_daemon.py stop
    python3 tools/monitor_daemon.py status
    python3 tools/monitor_daemon.py query [--hours 24] [--metric all|cpu|memory|disk]
"""

import sqlite3
import sys
import time
import subprocess
import json
import signal
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path("/data/.openclaw/workspace")
DB_PATH = WORKSPACE / "memory" / "monitoring.db"
PID_FILE = WORKSPACE / "memory" / "monitor_daemon.pid"

def init_database():
    """Initialize SQLite database"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS metrics (
            timestamp TEXT PRIMARY KEY,
            metric_type TEXT,
            value REAL,
            metadata TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def collect_metrics():
    """Collect current system metrics"""
    metrics = []
    
    # CPU load
    try:
        result = subprocess.run(['uptime'], capture_output=True, text=True)
        if "load average:" in result.stdout:
            load_str = result.stdout.split("load average:")[1].strip()
            loads = [float(x.strip()) for x in load_str.split(",")]
            
            metrics.append({
                'type': 'cpu_load_1min',
                'value': loads[0],
                'metadata': {}
            })
            metrics.append({
                'type': 'cpu_load_5min',
                'value': loads[1],
                'metadata': {}
            })
    except:
        pass
    
    # Memory usage
    try:
        result = subprocess.run(['free'], capture_output=True, text=True)
        lines = result.stdout.strip().split("\n")
        if len(lines) > 1:
            mem_line = lines[1].split()
            total = int(mem_line[1])
            used = int(mem_line[2])
            percent = (used / total) * 100
            
            metrics.append({
                'type': 'memory_percent',
                'value': percent,
                'metadata': {'total_mb': total // 1024, 'used_mb': used // 1024}
            })
    except:
        pass
    
    # Disk usage
    try:
        result = subprocess.run(['df', '-h', '/data'], capture_output=True, text=True)
        lines = result.stdout.strip().split("\n")
        if len(lines) > 1:
            parts = lines[1].split()
            usage = int(parts[4].rstrip('%'))
            
            metrics.append({
                'type': 'disk_percent',
                'value': usage,
                'metadata': {'total': parts[1], 'used': parts[2], 'available': parts[3]}
            })
    except:
        pass
    
    return metrics

def store_metrics(metrics):
    """Store metrics in database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    timestamp = datetime.now(timezone.utc).isoformat()
    
    for metric in metrics:
        try:
            c.execute('''
                INSERT INTO metrics (timestamp, metric_type, value, metadata)
                VALUES (?, ?, ?, ?)
            ''', (
                timestamp,
                metric['type'],
                metric['value'],
                json.dumps(metric['metadata'])
            ))
        except sqlite3.IntegrityError:
            pass  # Skip duplicates
    
    conn.commit()
    conn.close()

def daemon_loop(interval=300):
    """Main daemon loop"""
    init_database()
    
    print(f"Monitor daemon started (PID: {os.getpid()}, interval: {interval}s)")
    
    # Write PID file
    PID_FILE.write_text(str(os.getpid()))
    
    def signal_handler(signum, frame):
        print("\nStopping monitor daemon...")
        if PID_FILE.exists():
            PID_FILE.unlink()
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    while True:
        try:
            metrics = collect_metrics()
            store_metrics(metrics)
            print(f"[{datetime.now(timezone.utc).isoformat()}] Collected {len(metrics)} metrics")
        except Exception as e:
            print(f"Error collecting metrics: {e}")
        
        time.sleep(interval)

def query_metrics(hours=24, metric_type='all'):
    """Query historical metrics"""
    if not DB_PATH.exists():
        print("❌ No monitoring data available")
        return
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Calculate time threshold
    from datetime import timedelta
    threshold = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    
    if metric_type == 'all':
        c.execute('''
            SELECT timestamp, metric_type, value, metadata
            FROM metrics
            WHERE timestamp > ?
            ORDER BY timestamp DESC
            LIMIT 100
        ''', (threshold,))
    else:
        c.execute('''
            SELECT timestamp, metric_type, value, metadata
            FROM metrics
            WHERE timestamp > ? AND metric_type LIKE ?
            ORDER BY timestamp DESC
            LIMIT 100
        ''', (threshold, f'{metric_type}%'))
    
    results = c.fetchall()
    conn.close()
    
    if not results:
        print(f"❌ No data found for last {hours} hours")
        return
    
    print(f"📊 Metrics (last {hours} hours, {len(results)} records)\n")
    
    for row in results:
        timestamp, metric_type, value, metadata = row
        print(f"{timestamp} | {metric_type}: {value:.2f}")
        if metadata and metadata != '{}':
            print(f"  └─ {metadata}")

def stop_daemon():
    """Stop running daemon"""
    if not PID_FILE.exists():
        print("❌ Daemon not running (no PID file)")
        return
    
    try:
        pid = int(PID_FILE.read_text())
        subprocess.run(['kill', str(pid)])
        print(f"✅ Sent SIGTERM to PID {pid}")
        
        # Wait for cleanup
        time.sleep(1)
        if PID_FILE.exists():
            PID_FILE.unlink()
    except Exception as e:
        print(f"❌ Error stopping daemon: {e}")

def daemon_status():
    """Check daemon status"""
    if not PID_FILE.exists():
        print("❌ Daemon not running")
        return
    
    try:
        pid = int(PID_FILE.read_text())
        # Check if process exists
        result = subprocess.run(['ps', '-p', str(pid)], capture_output=True)
        if result.returncode == 0:
            print(f"✅ Daemon running (PID: {pid})")
        else:
            print(f"❌ Daemon not running (stale PID file)")
            PID_FILE.unlink()
    except Exception as e:
        print(f"❌ Error checking status: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: monitor_daemon.py start|stop|status|query [args]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'start':
        interval = 300  # 5 minutes default
        if '--interval' in sys.argv:
            idx = sys.argv.index('--interval')
            if idx + 1 < len(sys.argv):
                interval = int(sys.argv[idx + 1])
        
        daemon_loop(interval)
    
    elif command == 'stop':
        stop_daemon()
    
    elif command == 'status':
        daemon_status()
    
    elif command == 'query':
        hours = 24
        metric_type = 'all'
        
        if '--hours' in sys.argv:
            idx = sys.argv.index('--hours')
            if idx + 1 < len(sys.argv):
                hours = int(sys.argv[idx + 1])
        
        if '--metric' in sys.argv:
            idx = sys.argv.index('--metric')
            if idx + 1 < len(sys.argv):
                metric_type = sys.argv[idx + 1]
        
        query_metrics(hours, metric_type)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    import os
    main()
