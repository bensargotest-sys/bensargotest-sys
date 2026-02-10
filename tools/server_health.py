#!/usr/bin/env python3
"""
server_health.py - Monitor VPS health and report issues
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def run_cmd(cmd):
    """Run shell command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "TIMEOUT", 1
    except Exception as e:
        return f"ERROR: {e}", 1

def check_disk_usage():
    """Check disk usage on all mounted filesystems"""
    output, code = run_cmd("df -h / /var/lib/docker 2>/dev/null | tail -n +2")
    issues = []
    
    for line in output.split('\n'):
        if not line:
            continue
        parts = line.split()
        if len(parts) >= 5:
            usage_pct = int(parts[4].rstrip('%'))
            mount = parts[5]
            if usage_pct >= 90:
                issues.append(f"⚠️  {mount} at {usage_pct}% capacity")
            elif usage_pct >= 80:
                issues.append(f"⚡ {mount} at {usage_pct}% (watch)")
    
    return issues

def check_memory():
    """Check available memory"""
    output, code = run_cmd("free -m | grep Mem:")
    issues = []
    
    if code == 0 and output:
        parts = output.split()
        if len(parts) >= 4:
            total = int(parts[1])
            used = int(parts[2])
            available = int(parts[6]) if len(parts) > 6 else int(parts[3])
            pct_used = (used / total) * 100
            
            if pct_used >= 90:
                issues.append(f"⚠️  Memory at {pct_used:.1f}% ({used}MB/{total}MB)")
            elif pct_used >= 80:
                issues.append(f"⚡ Memory at {pct_used:.1f}% (watch)")
    
    return issues

def check_container_status():
    """Check OpenClaw container status"""
    output, code = run_cmd("docker ps --filter name=openclaw --format '{{.Status}}'")
    issues = []
    
    if code != 0:
        # Running inside container, docker CLI not available
        issues.append("⚡ Container check skipped (inside container)")
    elif not output:
        issues.append("⚠️  OpenClaw container not running")
    elif "Up" not in output:
        issues.append(f"⚠️  Container status: {output}")
    
    return issues

def check_firewall():
    """Check UFW firewall status"""
    output, code = run_cmd("which ufw 2>/dev/null")
    issues = []
    
    if code != 0 or not output:
        # ufw not available (container context)
        issues.append("⚡ Firewall check skipped (container context)")
        return issues
    
    output, code = run_cmd("ufw status | head -n 1")
    if "Status: active" not in output:
        issues.append("⚠️  UFW firewall is not active")
    
    return issues

def check_backup_age():
    """Check age of last backup"""
    backup_dir = Path("/root/openclaw-backups")
    issues = []
    
    try:
        if not backup_dir.exists():
            issues.append("⚡ Backup directory not accessible (container context)")
            return issues
        
        backups = sorted(backup_dir.glob("openclaw-backup-*.tar.gz"), reverse=True)
        
        if not backups:
            issues.append("⚠️  No backups found")
        else:
            latest = backups[0]
            age_hours = (datetime.now().timestamp() - latest.stat().st_mtime) / 3600
            
            if age_hours > 168:  # 1 week
                issues.append(f"⚠️  Latest backup is {age_hours/24:.1f} days old")
            elif age_hours > 72:  # 3 days
                issues.append(f"⚡ Latest backup is {age_hours/24:.1f} days old (consider refresh)")
    except PermissionError:
        # Running inside container, can't access host /root
        issues.append("⚡ Backup check skipped (container context)")
    
    return issues

def check_load_average():
    """Check system load average"""
    output, code = run_cmd("uptime")
    issues = []
    
    if code == 0 and "load average:" in output:
        load_str = output.split("load average:")[-1].strip()
        loads = [float(x.strip()) for x in load_str.split(",")]
        
        # Get CPU count
        cpu_output, _ = run_cmd("nproc")
        cpu_count = int(cpu_output) if cpu_output.isdigit() else 1
        
        # Check 5-minute load average
        if len(loads) >= 2:
            load_5min = loads[1]
            load_per_cpu = load_5min / cpu_count
            
            if load_per_cpu > 2.0:
                issues.append(f"⚠️  High load: {load_5min:.2f} ({cpu_count} CPUs)")
            elif load_per_cpu > 1.5:
                issues.append(f"⚡ Elevated load: {load_5min:.2f} (watch)")
    
    return issues

def main():
    """Run all health checks and report"""
    checks = {
        "Disk Usage": check_disk_usage,
        "Memory": check_memory,
        "Container": check_container_status,
        "Firewall": check_firewall,
        "Backups": check_backup_age,
        "Load Average": check_load_average,
    }
    
    all_issues = []
    
    print("🏥 VPS Health Check")
    print("=" * 50)
    
    for check_name, check_func in checks.items():
        issues = check_func()
        if issues:
            all_issues.extend(issues)
            print(f"\n{check_name}:")
            for issue in issues:
                print(f"  {issue}")
        else:
            print(f"\n{check_name}: ✓")
    
    print("\n" + "=" * 50)
    
    if all_issues:
        print(f"\n⚠️  Found {len(all_issues)} issue(s)")
        return 1
    else:
        print("\n✅ All checks passed")
        return 0

if __name__ == "__main__":
    sys.exit(main())
