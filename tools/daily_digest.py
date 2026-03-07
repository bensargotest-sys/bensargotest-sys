#!/usr/bin/env python3
"""
Daily Digest: End-of-day summary

Summarizes:
- Work completed today (from work-log.md)
- Tasks completed (from heartbeat-backlog.md)
- Mistakes logged (from mistakes.md)
- Rules promoted (from ENFORCEMENT.md)
- Decisions made (from WORKING_STATE.md checkpoint log)

Usage:
    python3 tools/daily_digest.py
    python3 tools/daily_digest.py --date 2026-02-11
    python3 tools/daily_digest.py --deliver telegram
"""

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from usage_logger import log_action
from usage_logger import log_usage

WORKSPACE = Path("/data/.openclaw/workspace")
WORK_LOG = WORKSPACE / "memory" / "work-log.md"
BACKLOG = WORKSPACE / "memory" / "heartbeat-backlog.md"
MISTAKES = WORKSPACE / "memory" / "archival" / "mistakes.md"
ENFORCEMENT = WORKSPACE / "ENFORCEMENT.md"
WORKING_STATE = WORKSPACE / "WORKING_STATE.md"
TOOL_USAGE_LOG = WORKSPACE / "memory" / "tool-usage.log"

def get_work_completed(date):
    """Get work completed on specific date"""
    if not WORK_LOG.exists():
        return []
    
    work = []
    target_date = date.strftime("%Y-%m-%d")
    
    for line in WORK_LOG.read_text().split("\n"):
        if target_date in line and "|" in line:
            # Format: timestamp | description | evidence
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 2:
                work.append(parts[1])
    
    return work

def get_tasks_completed(date):
    """Get tasks completed from backlog"""
    if not BACKLOG.exists():
        return []
    
    completed = []
    target_date = date.strftime("%Y-%m-%d")
    in_completed = False
    
    for line in BACKLOG.read_text().split("\n"):
        if "## Completed" in line:
            in_completed = True
            continue
        
        if in_completed:
            if target_date in line and "[x]" in line:
                # Extract task description
                task = line.split("]", 1)[1] if "]" in line else line
                completed.append(task.strip())
    
    return completed

def get_mistakes_logged(date):
    """Get mistakes logged today"""
    if not MISTAKES.exists():
        return []
    
    mistakes = []
    target_date = date.strftime("%Y-%m-%d")
    
    for line in MISTAKES.read_text().split("\n"):
        if target_date in line and line.strip():
            mistakes.append(line.strip())
    
    return mistakes

def get_rules_promoted(date):
    """Check if any rules were promoted today"""
    if not ENFORCEMENT.exists():
        return []
    
    promoted = []
    target_date = date.strftime("%Y-%m-%d")
    
    content = ENFORCEMENT.read_text()
    in_promoted = False
    
    for line in content.split("\n"):
        if "## Promoted Rules" in line:
            in_promoted = True
            continue
        
        if in_promoted and target_date in line:
            # Get the rule title (next few lines)
            lines = content.split("\n")
            idx = lines.index(line)
            for i in range(idx, min(idx + 5, len(lines))):
                if "**Rule:**" in lines[i]:
                    promoted.append(lines[i].replace("**Rule:**", "").strip())
                    break
    
    return promoted

def get_tool_usage(date):
    """Get tool usage statistics for today"""
    if not TOOL_USAGE_LOG.exists():
        return {"total": 0, "tools": {}}
    
    target_date = date.strftime("%Y-%m-%d")
    stats = {"total": 0, "tools": {}}
    
    for line in TOOL_USAGE_LOG.read_text().split("\n"):
        if line.strip():
            try:
                entry = json.loads(line)
                if target_date in entry.get("timestamp", ""):
                    stats["total"] += 1
                    tool = entry.get("tool", "unknown")
                    stats["tools"][tool] = stats["tools"].get(tool, 0) + 1
            except json.JSONDecodeError:
                continue
    
    return stats

def generate_digest(date):
    """Generate daily digest"""
    digest = []
    digest.append(f"🌙 Daily Digest - {date.strftime('%A, %B %d, %Y')}")
    digest.append("")
    
    # Work Completed
    work = get_work_completed(date)
    digest.append(f"## ✅ Work Completed ({len(work)} items)")
    if work:
        for item in work:
            digest.append(f"  • {item}")
    else:
        digest.append("  _No work logged_")
    digest.append("")
    
    # Tasks Completed
    tasks = get_tasks_completed(date)
    digest.append(f"## 📋 Tasks Completed ({len(tasks)} items)")
    if tasks:
        for task in tasks:
            digest.append(f"  • {task}")
    else:
        digest.append("  _No tasks marked complete_")
    digest.append("")
    
    # Mistakes Logged
    mistakes = get_mistakes_logged(date)
    digest.append(f"## ⚠️ Mistakes Logged ({len(mistakes)} items)")
    if mistakes:
        for mistake in mistakes:
            digest.append(f"  • {mistake}")
    else:
        digest.append("  _No mistakes logged_")
    digest.append("")
    
    # Rules Promoted
    rules = get_rules_promoted(date)
    digest.append(f"## 📜 Rules Promoted ({len(rules)} items)")
    if rules:
        for rule in rules:
            digest.append(f"  • {rule}")
    else:
        digest.append("  _No rules promoted_")
    digest.append("")
    
    # Tool Usage
    usage = get_tool_usage(date)
    digest.append(f"## 🔧 Tool Usage ({usage['total']} calls)")
    if usage['tools']:
        # Top 5 most-used tools
        top_tools = sorted(usage['tools'].items(), key=lambda x: x[1], reverse=True)[:5]
        for tool, count in top_tools:
            digest.append(f"  • {tool}: {count} calls")
    else:
        digest.append("  _No tool usage logged_")
    digest.append("")
    
    # Footer
    digest.append("---")
    digest.append("_Generated by daily_digest.py_")
    
    return "\n".join(digest)

@log_usage
def main():
    parser = argparse.ArgumentParser(description="Generate daily digest")
    parser.add_argument("--date", help="Date (YYYY-MM-DD), defaults to today")
    parser.add_argument("--deliver", choices=["telegram", "discord"], help="Deliver to channel")
    parser.add_argument("--save", action="store_true", help="Save to file")
    
    args = parser.parse_args()
    
    # Parse date
    if args.date:
        date = datetime.strptime(args.date, "%Y-%m-%d")
    else:
        date = datetime.now()
    
    digest = generate_digest(date)
    
    # Always print to console
    print(digest)
    
    # Save to file if requested
    if args.save:
        output_path = WORKSPACE / "memory" / f"digest-{date.strftime('%Y-%m-%d')}.md"
        output_path.write_text(digest)
        print(f"\n✅ Saved to {output_path}")
    
    # Deliver to channel if requested
    if args.deliver:
        # TODO: Implement channel delivery via message tool
        print(f"\n⚠️ Channel delivery not yet implemented")
    
    # Log usage
    log_action("daily_digest", "generate", success=True,
               details={"date": date.strftime("%Y-%m-%d"), "delivered": args.deliver, "saved": args.save})

if __name__ == "__main__":
    main()
