#!/usr/bin/env python3
"""
mistake_logger.py - Log mistakes with structured metadata

Usage:
  python3 mistake_logger.py log "description"
  python3 mistake_logger.py log "description" --category "tool-failure"
  python3 mistake_logger.py recent [n]
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path("/data/.openclaw/workspace")
MISTAKES_FILE = WORKSPACE / "memory" / "archival" / "mistakes.md"
MISTAKES_JSON = WORKSPACE / "memory" / "archival" / "mistakes.jsonl"


def log_mistake(description, category=None, context=None):
    """Log a mistake to both markdown and JSON."""
    MISTAKES_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y-%m-%d %H:%M UTC")
    
    # Append to markdown
    with open(MISTAKES_FILE, "a") as f:
        f.write(f"\n## {timestamp}\n")
        if category:
            f.write(f"**Category:** {category}\n")
        f.write(f"{description}\n")
        if context:
            f.write(f"**Context:** {context}\n")
    
    # Append to JSON for programmatic analysis
    entry = {
        "timestamp": now.isoformat(),
        "description": description,
        "category": category,
        "context": context
    }
    
    with open(MISTAKES_JSON, "a") as f:
        f.write(json.dumps(entry) + "\n")
    
    print(f"✓ Mistake logged: {description[:60]}{'...' if len(description) > 60 else ''}")


def recent(n=10):
    """Show recent mistakes."""
    if not MISTAKES_JSON.exists():
        print("No mistakes logged yet. (That's... suspicious? 🤔)")
        return
    
    entries = []
    with open(MISTAKES_JSON) as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    
    entries = entries[-n:]
    
    print(f"Recent {len(entries)} mistakes:")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    for e in entries:
        ts = datetime.fromisoformat(e["timestamp"]).strftime("%Y-%m-%d %H:%M")
        cat = f"[{e['category']}]" if e.get("category") else ""
        desc = e["description"][:70]
        print(f"{ts} {cat:15} {desc}")


def main():
    parser = argparse.ArgumentParser(description="Mistake logger")
    subparsers = parser.add_subparsers(dest="command")
    
    # Log command
    log_parser = subparsers.add_parser("log", help="Log a mistake")
    log_parser.add_argument("description", help="What went wrong")
    log_parser.add_argument("--category", help="Mistake category")
    log_parser.add_argument("--context", help="Additional context")
    
    # Recent command
    recent_parser = subparsers.add_parser("recent", help="Show recent mistakes")
    recent_parser.add_argument("n", nargs="?", type=int, default=10)
    
    args = parser.parse_args()
    
    if args.command == "log":
        log_mistake(args.description, args.category, args.context)
    elif args.command == "recent":
        recent(args.n)
    else:
        parser.print_help()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
