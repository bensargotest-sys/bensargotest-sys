#!/usr/bin/env python3
"""
memory_consolidate.py - Four-tier memory consolidation system

Usage:
    python3 tools/memory_consolidate.py daily     # Tier 1: Daily summary
    python3 tools/memory_consolidate.py weekly    # Tier 2: Weekly rollup
    python3 tools/memory_consolidate.py monthly   # Tier 3: Monthly review
    python3 tools/memory_consolidate.py review    # Tier 4: Major insights

Consolidates daily logs into higher-level memory tiers to prevent memory bloat.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

MEMORY_DIR = Path(__file__).parent.parent / "memory"
MEMORY_FILE = Path(__file__).parent.parent / "MEMORY.md"

def get_daily_logs(days=7):
    """Get recent daily log files."""
    logs = []
    for i in range(days):
        date = (datetime.now(timezone.utc) - timedelta(days=i)).strftime("%Y-%m-%d")
        log_file = MEMORY_DIR / f"{date}.md"
        if log_file.exists():
            logs.append((date, log_file))
    return logs

def daily_summary():
    """Tier 1: Summarize today's work."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log_file = MEMORY_DIR / f"{today}.md"
    
    if not log_file.exists():
        print(f"No daily log for {today}")
        return
    
    with open(log_file, "r") as f:
        content = f.read()
    
    # Extract key sections
    sections = content.split('\n## ')
    
    print(f"\n📝 Daily Summary: {today}\n")
    
    # Count activities
    activity_count = len([s for s in sections if s.strip()]) - 1  # Subtract header
    
    print(f"**Activities:** {activity_count} logged")
    
    # List key activities (first line of each section)
    if len(sections) > 1:
        print("\n**Key Activities:**")
        for section in sections[1:]:
            lines = section.split('\n')
            if lines:
                header = lines[0].strip()
                print(f"  - {header}")
    
    print()

def weekly_rollup():
    """Tier 2: Roll up last 7 days."""
    logs = get_daily_logs(7)
    
    if not logs:
        print("No daily logs found for past 7 days")
        return
    
    print(f"\n📅 Weekly Rollup: {len(logs)} days\n")
    
    all_content = []
    for date, log_file in logs:
        with open(log_file, "r") as f:
            content = f.read()
        all_content.append((date, content))
    
    # Extract patterns
    print("**This Week:**")
    for date, content in all_content:
        sections = content.split('\n## ')
        activity_count = len([s for s in sections if s.strip()]) - 1
        print(f"  - {date}: {activity_count} activities")
    
    print("\n**Consolidation Candidates:**")
    print("  (Review these daily logs for insights to promote to MEMORY.md)")
    for date, _ in all_content:
        print(f"  - memory/{date}.md")
    
    print()

def monthly_review():
    """Tier 3: Monthly review (last 30 days)."""
    logs = get_daily_logs(30)
    
    if not logs:
        print("No daily logs found for past 30 days")
        return
    
    print(f"\n📆 Monthly Review: {len(logs)} days\n")
    
    total_activities = 0
    for date, log_file in logs:
        with open(log_file, "r") as f:
            content = f.read()
        sections = content.split('\n## ')
        total_activities += len([s for s in sections if s.strip()]) - 1
    
    print(f"**Total Activities:** {total_activities}")
    print(f"**Daily Average:** {total_activities / len(logs):.1f}")
    
    print("\n**Recommendations:**")
    print("  - Review old daily logs (>30 days)")
    print("  - Extract key insights to MEMORY.md")
    print("  - Archive or delete stale logs")
    
    print()

def major_insights():
    """Tier 4: Extract major insights to MEMORY.md."""
    if not MEMORY_FILE.exists():
        print("MEMORY.md does not exist. Create it first.")
        return
    
    with open(MEMORY_FILE, "r") as f:
        memory_content = f.read()
    
    print("\n🧠 MEMORY.md Current State\n")
    
    lines = memory_content.split('\n')
    print(f"**Total Lines:** {len(lines)}")
    
    sections = memory_content.split('\n## ')
    print(f"**Sections:** {len(sections) - 1}")
    
    print("\n**Review Process:**")
    print("  1. Read recent daily logs (memory/YYYY-MM-DD.md)")
    print("  2. Identify recurring patterns, key decisions, lessons")
    print("  3. Add to MEMORY.md as curated wisdom")
    print("  4. Remove stale/outdated entries from MEMORY.md")
    
    print()

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "daily":
        daily_summary()
    
    elif command == "weekly":
        weekly_rollup()
    
    elif command == "monthly":
        monthly_review()
    
    elif command == "review":
        major_insights()
    
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()
