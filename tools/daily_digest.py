#!/usr/bin/env python3
"""
daily_digest.py - Generate end-of-day digest report

Summarizes the day's work, decisions, blockers encountered, and
provides context for next day. Complementary to morning_briefing.py
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


def get_today_work_items() -> List[str]:
    """Get all work items completed today"""
    work_log_path = WORKSPACE / "memory" / "work-log.md"
    
    if not work_log_path.exists():
        return []
    
    items = []
    today = datetime.utcnow().date()
    
    try:
        with open(work_log_path, 'r') as f:
            for line in f:
                if "|" in line:
                    parts = line.strip().split("|")
                    if len(parts) >= 2:
                        try:
                            timestamp_str = parts[0].strip()
                            dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M UTC")
                            
                            if dt.date() == today:
                                work_desc = parts[1].strip()
                                items.append(work_desc)
                        except (ValueError, IndexError):
                            continue
    except IOError:
        pass
    
    return items


def get_daily_log_summary() -> Optional[str]:
    """Extract summary from today's daily log"""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    daily_log_path = WORKSPACE / "memory" / f"{today}.md"
    
    if not daily_log_path.exists():
        return None
    
    try:
        with open(daily_log_path, 'r') as f:
            content = f.read()
            
            # Look for summary section
            if "## Summary" in content:
                lines = content.split("\n")
                summary_lines = []
                capturing = False
                
                for line in lines:
                    if line.startswith("## Summary"):
                        capturing = True
                        continue
                    elif capturing and line.startswith("##"):
                        break
                    elif capturing:
                        summary_lines.append(line)
                
                summary = "\n".join(summary_lines).strip()
                return summary if summary else None
            
            # If no summary section, return first paragraph
            paragraphs = [p.strip() for p in content.split("\n\n") if p.strip() and not p.startswith("#")]
            return paragraphs[0] if paragraphs else None
            
    except IOError:
        pass
    
    return None


def get_blockers_added_today() -> List[Dict]:
    """Get blockers added today"""
    blocked_file = WORKSPACE / "memory" / "blocked-items.json"
    items = load_json_file(blocked_file, [])
    
    today = datetime.utcnow().date()
    today_blockers = []
    
    for item in items:
        try:
            blocked_at = item.get("blocked_at", "")
            dt = datetime.fromisoformat(blocked_at.rstrip('Z'))
            
            if dt.date() == today:
                today_blockers.append(item)
        except (ValueError, TypeError):
            continue
    
    return today_blockers


def get_blockers_resolved_today() -> List[Dict]:
    """Get blockers resolved today"""
    blocked_file = WORKSPACE / "memory" / "blocked-items.json"
    items = load_json_file(blocked_file, [])
    
    today = datetime.utcnow().date()
    resolved_today = []
    
    for item in items:
        if item.get("status") != "resolved":
            continue
            
        try:
            resolved_at = item.get("resolved_at", "")
            dt = datetime.fromisoformat(resolved_at.rstrip('Z'))
            
            if dt.date() == today:
                resolved_today.append(item)
        except (ValueError, TypeError):
            continue
    
    return resolved_today


def get_mistakes_today() -> List[Dict]:
    """Get mistakes logged today"""
    mistake_log = WORKSPACE / "memory" / "mistakes.json"
    mistakes = load_json_file(mistake_log, [])
    
    today = datetime.utcnow().date()
    today_mistakes = []
    
    for mistake in mistakes:
        try:
            timestamp = mistake.get("timestamp", "")
            dt = datetime.fromisoformat(timestamp.rstrip('Z'))
            
            if dt.date() == today:
                today_mistakes.append(mistake)
        except (ValueError, TypeError):
            continue
    
    return today_mistakes


def get_heartbeat_delta() -> Dict:
    """Get heartbeat work done today"""
    heartbeat_state = WORKSPACE / "memory" / "heartbeat-state.json"
    state = load_json_file(heartbeat_state, {})
    
    # For now, just return current count
    # In future, could track daily deltas
    return {
        "total_work_items": state.get("heartbeatWorkItems", 0),
        "consecutive_no_work": state.get("consecutiveNoWork", 0)
    }


def get_kanban_progress() -> Optional[Dict]:
    """Get kanban task progress if available"""
    kanban_file = WORKSPACE / "memory" / "kanban-tasks.json"
    
    if not kanban_file.exists():
        return None
    
    kanban = load_json_file(kanban_file, {})
    
    # Count tasks by status
    counts = {
        "todo": len(kanban.get("todo", [])),
        "in_progress": len(kanban.get("in_progress", [])),
        "done": len(kanban.get("done", []))
    }
    
    return counts


def generate_digest() -> str:
    """Generate end-of-day digest report"""
    now = datetime.utcnow()
    today = now.strftime("%Y-%m-%d")
    
    # Header
    report = []
    report.append("=" * 70)
    report.append(f"🌙 Daily Digest - {today}")
    report.append(f"Generated: {now.strftime('%H:%M UTC')}")
    report.append("=" * 70)
    report.append("")
    
    # Daily Log Summary
    daily_summary = get_daily_log_summary()
    if daily_summary:
        report.append("📖 Daily Summary")
        report.append("-" * 70)
        for line in daily_summary.split("\n"):
            if line.strip():
                report.append(f"  {line}")
        report.append("")
    
    # Work Completed
    work_items = get_today_work_items()
    report.append(f"✅ Work Completed ({len(work_items)} items)")
    report.append("-" * 70)
    
    if work_items:
        for item in work_items:
            report.append(f"  • {item}")
    else:
        report.append("  No work items logged today")
    
    report.append("")
    
    # Blockers Activity
    blockers_added = get_blockers_added_today()
    blockers_resolved = get_blockers_resolved_today()
    
    if blockers_added or blockers_resolved:
        report.append("🚧 Blocker Activity")
        report.append("-" * 70)
        
        if blockers_resolved:
            report.append(f"  Resolved: {len(blockers_resolved)}")
            for item in blockers_resolved:
                report.append(f"    ✓ {item.get('task', 'Unknown')}")
        
        if blockers_added:
            report.append(f"  New blockers: {len(blockers_added)}")
            for item in blockers_added:
                report.append(f"    ⚠️  {item.get('task', 'Unknown')}")
                report.append(f"       Blocker: {item.get('blocker', 'Unknown')}")
        
        report.append("")
    
    # Mistakes
    mistakes = get_mistakes_today()
    if mistakes:
        report.append(f"🔍 Issues & Learnings ({len(mistakes)})")
        report.append("-" * 70)
        
        for mistake in mistakes:
            report.append(f"  • {mistake.get('description', 'Unknown')}")
            category = mistake.get('category', 'general')
            report.append(f"    Category: {category}")
            
            if mistake.get('lesson'):
                report.append(f"    Lesson: {mistake.get('lesson')}")
        
        report.append("")
    
    # Heartbeat Performance
    hb_delta = get_heartbeat_delta()
    report.append("💓 Heartbeat Performance")
    report.append("-" * 70)
    report.append(f"  Total work items: {hb_delta['total_work_items']}")
    report.append(f"  Consecutive no-work: {hb_delta['consecutive_no_work']}")
    
    if hb_delta['consecutive_no_work'] > 3:
        report.append("  ⚠️  High no-work count - check heartbeat productivity")
    
    report.append("")
    
    # Kanban Progress
    kanban = get_kanban_progress()
    if kanban:
        report.append("📊 Task Progress")
        report.append("-" * 70)
        report.append(f"  Todo: {kanban['todo']}")
        report.append(f"  In Progress: {kanban['in_progress']}")
        report.append(f"  Done: {kanban['done']}")
        
        total = sum(kanban.values())
        if total > 0:
            done_pct = (kanban['done'] / total) * 100
            report.append(f"  Completion: {done_pct:.1f}%")
        
        report.append("")
    
    # Next Day Preview
    report.append("🌅 Tomorrow's Focus")
    report.append("-" * 70)
    
    # Check if there are high-priority blockers
    blocked_file = WORKSPACE / "memory" / "blocked-items.json"
    all_blocked = [i for i in load_json_file(blocked_file, []) if i.get("status") == "blocked"]
    high_priority = [i for i in all_blocked if i.get("priority") in ["critical", "high"]]
    
    if high_priority:
        report.append(f"  ⚠️  {len(high_priority)} high-priority blocker(s) need attention")
    
    # Check backlog health
    backlog_path = WORKSPACE / "memory" / "heartbeat-backlog.md"
    if backlog_path.exists():
        uncompleted = 0
        try:
            with open(backlog_path, 'r') as f:
                for line in f:
                    if line.strip().startswith("- [ ]"):
                        uncompleted += 1
        except IOError:
            pass
        
        if uncompleted < 10:
            report.append(f"  📝 Backlog needs refill ({uncompleted} items)")
        else:
            report.append(f"  📝 Backlog healthy ({uncompleted} items)")
    
    report.append("")
    report.append("=" * 70)
    report.append("💤 End of day. Rest well!")
    report.append("=" * 70)
    
    return "\n".join(report)


def main():
    """CLI interface"""
    print(generate_digest())


if __name__ == "__main__":
    main()
