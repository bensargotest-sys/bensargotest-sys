#!/usr/bin/env python3
"""
morning_briefing.py - Generate morning briefing report

Aggregates overnight activity, pending items, and priorities into a
concise morning briefing for the user.
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

WORKSPACE = Path(__file__).parent.parent


def load_json_file(path: Path, default=None):
    """Safely load JSON file"""
    if not path.exists():
        return default if default is not None else {}
    
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default if default is not None else {}


def get_recent_work_items(hours: int = 24) -> List[str]:
    """Get work items completed in last N hours"""
    work_log_path = WORKSPACE / "memory" / "work-log.md"
    
    if not work_log_path.exists():
        return []
    
    items = []
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    
    try:
        with open(work_log_path, 'r') as f:
            for line in f:
                # Look for timestamp patterns: 2026-02-09 23:00
                if "UTC" in line or "|" in line:
                    parts = line.strip().split("|")
                    if len(parts) >= 2:
                        try:
                            # Parse timestamp from format: 2026-02-09 23:00 UTC
                            timestamp_str = parts[0].strip()
                            dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M UTC")
                            
                            if dt >= cutoff:
                                work_desc = parts[1].strip()
                                items.append(work_desc)
                        except (ValueError, IndexError):
                            continue
    except IOError:
        pass
    
    return items


def get_blocked_items() -> List[Dict]:
    """Get currently blocked items"""
    blocked_file = WORKSPACE / "memory" / "blocked-items.json"
    items = load_json_file(blocked_file, [])
    
    return [i for i in items if i.get("status") == "blocked"]


def get_heartbeat_backlog_count() -> int:
    """Count active backlog items"""
    backlog_path = WORKSPACE / "memory" / "heartbeat-backlog.md"
    
    if not backlog_path.exists():
        return 0
    
    count = 0
    try:
        with open(backlog_path, 'r') as f:
            for line in f:
                if line.strip().startswith("- [ ]"):
                    count += 1
    except IOError:
        pass
    
    return count


def get_heartbeat_stats() -> Dict:
    """Get heartbeat statistics"""
    heartbeat_state = WORKSPACE / "memory" / "heartbeat-state.json"
    return load_json_file(heartbeat_state, {})


def get_mistake_count(days: int = 7) -> int:
    """Get mistake count from last N days"""
    mistake_log = WORKSPACE / "memory" / "mistakes.json"
    mistakes = load_json_file(mistake_log, [])
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    recent = 0
    for mistake in mistakes:
        try:
            timestamp = mistake.get("timestamp", "")
            dt = datetime.fromisoformat(timestamp.rstrip('Z'))
            if dt >= cutoff:
                recent += 1
        except (ValueError, TypeError):
            continue
    
    return recent


def get_daily_log_path(offset_days: int = 0) -> Path:
    """Get path to daily log (today or offset)"""
    date = datetime.utcnow() - timedelta(days=offset_days)
    return WORKSPACE / "memory" / f"{date.strftime('%Y-%m-%d')}.md"


def check_daily_log_exists(offset_days: int = 0) -> bool:
    """Check if daily log exists"""
    return get_daily_log_path(offset_days).exists()


def get_tsp_status() -> Optional[Dict]:
    """Get TSP project status if exists"""
    tsp_dir = WORKSPACE / "tsp"
    
    if not tsp_dir.exists():
        return None
    
    metrics_file = tsp_dir / "metrics-dashboard.json"
    
    if not metrics_file.exists():
        return {"status": "active", "details": "No metrics available"}
    
    metrics = load_json_file(metrics_file, {})
    return {
        "status": "active",
        "github_stars": metrics.get("github_stars", 0),
        "signups": metrics.get("formspree_signups", 0),
        "karma": metrics.get("moltbook_karma", 0)
    }


def generate_briefing(hours: int = 24) -> str:
    """Generate morning briefing report"""
    now = datetime.utcnow()
    
    # Header
    report = []
    report.append("=" * 70)
    report.append(f"☀️  Morning Briefing - {now.strftime('%Y-%m-%d %H:%M UTC')}")
    report.append("=" * 70)
    report.append("")
    
    # Recent Activity
    work_items = get_recent_work_items(hours)
    report.append(f"📊 Activity (Last {hours}h)")
    report.append("-" * 70)
    
    if work_items:
        for item in work_items[-10:]:  # Last 10 items
            report.append(f"  ✓ {item}")
    else:
        report.append("  No recent work logged")
    
    report.append("")
    
    # Heartbeat Stats
    hb_stats = get_heartbeat_stats()
    report.append("💓 Heartbeat Stats")
    report.append("-" * 70)
    report.append(f"  Work items completed: {hb_stats.get('heartbeatWorkItems', 0)}")
    
    last_hb = hb_stats.get('lastHeartbeat')
    if last_hb:
        try:
            dt = datetime.fromisoformat(last_hb.rstrip('Z'))
            hours_ago = (now - dt).total_seconds() / 3600
            report.append(f"  Last heartbeat: {hours_ago:.1f}h ago")
        except:
            pass
    
    report.append("")
    
    # Backlog Status
    backlog_count = get_heartbeat_backlog_count()
    report.append("📝 Backlog")
    report.append("-" * 70)
    report.append(f"  Active items: {backlog_count}")
    
    if backlog_count < 10:
        report.append("  ⚠️  Backlog low - needs refill")
    
    report.append("")
    
    # Blocked Items
    blocked = get_blocked_items()
    report.append("🚧 Blockers")
    report.append("-" * 70)
    
    if blocked:
        priority_counts = {}
        for item in blocked:
            p = item.get("priority", "medium")
            priority_counts[p] = priority_counts.get(p, 0) + 1
        
        report.append(f"  Total blocked: {len(blocked)}")
        
        for priority in ["critical", "high", "medium", "low"]:
            count = priority_counts.get(priority, 0)
            if count > 0:
                icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
                report.append(f"  {icons.get(priority, '⚪')} {priority.capitalize()}: {count}")
        
        # Show top 3 blockers
        report.append("")
        report.append("  Top blockers:")
        for item in sorted(blocked, key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(x.get("priority", "medium"), 2))[:3]:
            report.append(f"    • {item.get('task', 'Unknown')}")
            report.append(f"      Blocker: {item.get('blocker', 'Unknown')}")
    else:
        report.append("  ✅ No blockers")
    
    report.append("")
    
    # Mistakes (last 7 days)
    mistake_count = get_mistake_count(7)
    report.append("🔍 Quality")
    report.append("-" * 70)
    report.append(f"  Mistakes (7d): {mistake_count}")
    
    if mistake_count > 5:
        report.append("  ⚠️  High mistake rate - review needed")
    
    report.append("")
    
    # TSP Status
    tsp_status = get_tsp_status()
    if tsp_status:
        report.append("🚀 TSP Project")
        report.append("-" * 70)
        report.append(f"  Status: {tsp_status.get('status', 'unknown')}")
        
        if 'github_stars' in tsp_status:
            report.append(f"  GitHub stars: {tsp_status['github_stars']}")
            report.append(f"  Signups: {tsp_status['signups']}")
            report.append(f"  Karma: {tsp_status['karma']}")
        
        report.append("")
    
    # Daily Log Check
    report.append("📅 Daily Logs")
    report.append("-" * 70)
    
    today_exists = check_daily_log_exists(0)
    yesterday_exists = check_daily_log_exists(1)
    
    if today_exists:
        report.append(f"  Today ({now.strftime('%Y-%m-%d')}): ✓")
    else:
        report.append(f"  Today ({now.strftime('%Y-%m-%d')}): ⚠️  Missing")
    
    yesterday_date = (now - timedelta(days=1)).strftime('%Y-%m-%d')
    if yesterday_exists:
        report.append(f"  Yesterday ({yesterday_date}): ✓")
    else:
        report.append(f"  Yesterday ({yesterday_date}): ⚠️  Missing")
    
    report.append("")
    report.append("=" * 70)
    
    return "\n".join(report)


def main():
    """CLI interface"""
    hours = 24
    
    if len(sys.argv) > 1:
        try:
            hours = int(sys.argv[1])
        except ValueError:
            print(f"Invalid hours argument: {sys.argv[1]}")
            sys.exit(1)
    
    print(generate_briefing(hours))


if __name__ == "__main__":
    main()
