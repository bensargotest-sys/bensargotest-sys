#!/usr/bin/env python3
"""
Health Dashboard - System and workspace health monitoring
Provides quick overview of disk, memory, CPU, backlog count, and blockers
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from usage_logger import log_usage

def run_command(cmd):
    """Run shell command and return output"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip(), result.returncode
    except Exception as e:
        return f"ERROR: {e}", 1

def get_disk_usage():
    """Get disk usage for workspace"""
    output, code = run_command("df -h /data/.openclaw/workspace | tail -1")
    if code == 0:
        parts = output.split()
        return {
            "total": parts[1],
            "used": parts[2],
            "available": parts[3],
            "percent": parts[4],
        }
    return {"error": "Failed to get disk usage"}

def get_memory_usage():
    """Get memory usage"""
    output, code = run_command("free -h | grep Mem:")
    if code == 0:
        parts = output.split()
        return {
            "total": parts[1],
            "used": parts[2],
            "free": parts[3],
            "percent": f"{int((float(parts[2].replace('Gi','').replace('Mi','')) / float(parts[1].replace('Gi','').replace('Mi',''))) * 100)}%"
        }
    return {"error": "Failed to get memory usage"}

def get_load_average():
    """Get system load average"""
    output, code = run_command("uptime | awk -F'load average:' '{print $2}'")
    if code == 0:
        return output.strip()
    return "N/A"

def get_backlog_count():
    """Count remaining backlog items"""
    backlog_file = "/data/.openclaw/workspace/memory/heartbeat-backlog.md"
    if not os.path.exists(backlog_file):
        return {"error": "Backlog file not found"}
    
    try:
        with open(backlog_file, 'r') as f:
            content = f.read()
            total = content.count("- [ ]")
            completed = content.count("- [x]")
            return {
                "remaining": total,
                "completed": completed,
                "total": total + completed
            }
    except Exception as e:
        return {"error": str(e)}

def get_blocker_count():
    """Get count of active blockers"""
    output, code = run_command("python3 /data/.openclaw/workspace/tools/blocked_items.py summary 2>/dev/null")
    if code == 0:
        # Parse summary output
        lines = output.split('\n')
        for line in lines:
            if 'Currently blocked:' in line:
                count = line.split(':')[1].strip()
                return int(count)
    return 0

def get_heartbeat_status():
    """Get heartbeat work stats"""
    output, code = run_command("python3 /data/.openclaw/workspace/tools/heartbeat_enforcer.py check 2>&1")
    if "Work items completed:" in output:
        stats = {}
        for line in output.split('\n'):
            if "Work items completed:" in line:
                stats["completed"] = int(line.split(':')[1].strip())
            elif "Consecutive no-work:" in line:
                stats["no_work_streak"] = int(line.split(':')[1].strip())
        return stats
    return {"error": "Could not read heartbeat status"}

def get_recent_mistakes():
    """Get count of recent mistakes"""
    mistakes_file = "/data/.openclaw/workspace/memory/mistakes.json"
    if not os.path.exists(mistakes_file):
        return 0
    
    try:
        with open(mistakes_file, 'r') as f:
            mistakes = json.load(f)
            return len(mistakes)
    except:
        return 0

def get_checkpoint_age():
    """Get age of last checkpoint"""
    checkpoint_log = "/data/.openclaw/workspace/memory/checkpoint-log.jsonl"
    if not os.path.exists(checkpoint_log):
        return "No checkpoints"
    
    try:
        # Get last line from checkpoint log
        output, code = run_command(f"tail -1 {checkpoint_log}")
        if code == 0 and output:
            data = json.loads(output)
            timestamp = data.get("timestamp", "Unknown")
            note = data.get("note", "")
            # Calculate age
            if timestamp != "Unknown":
                from datetime import datetime
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                age_hours = (datetime.now(dt.tzinfo) - dt).total_seconds() / 3600
                if age_hours < 1:
                    age_str = f"{int(age_hours * 60)}m ago"
                elif age_hours < 24:
                    age_str = f"{int(age_hours)}h ago"
                else:
                    age_str = f"{age_hours/24:.1f}d ago"
                return f"{age_str} ({note[:30]}...)" if len(note) > 30 else f"{age_str} ({note})"
            return timestamp
    except Exception as e:
        return f"Error: {e}"
    return "Unknown"

def format_status_indicator(value, thresholds):
    """Return colored status indicator based on thresholds"""
    # thresholds: (warning, critical)
    if isinstance(value, str):
        value = int(value.replace('%', ''))
    
    if value >= thresholds[1]:
        return "🔴"
    elif value >= thresholds[0]:
        return "🟡"
    else:
        return "🟢"

@log_usage
def main():
    """Main health dashboard display"""
    
    print("\n" + "="*70)
    print("🏥 HEALTH DASHBOARD")
    print("="*70)
    print(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
    
    # System Resources
    print("📊 SYSTEM RESOURCES")
    print("-" * 70)
    
    disk = get_disk_usage()
    if "error" not in disk:
        percent = int(disk["percent"].replace('%', ''))
        status = format_status_indicator(percent, (70, 85))
        print(f"{status} Disk:   {disk['used']:>8} / {disk['total']:>8} ({disk['percent']:>5}) | Available: {disk['available']:>8}")
    else:
        print(f"🔴 Disk:   {disk['error']}")
    
    mem = get_memory_usage()
    if "error" not in mem:
        print(f"🟢 Memory: {mem['used']:>8} / {mem['total']:>8} ({mem.get('percent', 'N/A'):>5}) | Free: {mem['free']:>8}")
    else:
        print(f"🔴 Memory: {mem['error']}")
    
    load = get_load_average()
    print(f"🟢 Load:   {load}")
    
    # Workspace Health
    print("\n📁 WORKSPACE HEALTH")
    print("-" * 70)
    
    backlog = get_backlog_count()
    if "error" not in backlog:
        remaining = backlog["remaining"]
        status = "🔴" if remaining < 10 else "🟢"
        print(f"{status} Backlog:    {remaining} remaining / {backlog['total']} total ({backlog['completed']} completed)")
    else:
        print(f"🔴 Backlog:    {backlog['error']}")
    
    blockers = get_blocker_count()
    status = "🔴" if blockers > 5 else "🟡" if blockers > 2 else "🟢"
    print(f"{status} Blockers:   {blockers} active")
    
    mistakes = get_recent_mistakes()
    status = "🟡" if mistakes > 10 else "🟢"
    print(f"{status} Mistakes:   {mistakes} logged")
    
    heartbeat = get_heartbeat_status()
    if "error" not in heartbeat:
        no_work = heartbeat.get("no_work_streak", 0)
        status = "🔴" if no_work > 3 else "🟡" if no_work > 1 else "🟢"
        print(f"{status} Heartbeats: {heartbeat.get('completed', 0)} work items completed | {no_work} consecutive no-work")
    else:
        print(f"🟡 Heartbeats: {heartbeat['error']}")
    
    checkpoint_age = get_checkpoint_age()
    print(f"🟢 Checkpoint: {checkpoint_age}")
    
    # Quick Actions
    print("\n🔧 QUICK ACTIONS")
    print("-" * 70)
    print("View blockers:  python3 tools/blocked_items.py list")
    print("View mistakes:  cat memory/mistakes.json | jq")
    print("View backlog:   cat memory/heartbeat-backlog.md")
    print("Run checkpoint: python3 tools/checkpoint.py --auto --note 'manual checkpoint'")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
