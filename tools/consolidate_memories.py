#!/usr/bin/env python3
"""
Memory Consolidation Loop
Inspired by Google's always-on-memory-agent consolidation pattern.

Reads recent daily memory files, cross-references with long-term memory,
generates insights and connections, writes consolidated output.

Usage:
  python3 tools/consolidate_memories.py [--days 3] [--dry-run]
"""

import os
import sys
import glob
import json
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = "/data/.openclaw/workspace"
MEMORY_DIR = os.path.join(WORKSPACE, "memory")
MEMORY_MD = os.path.join(WORKSPACE, "MEMORY.md")
CONSOLIDATION_FILE = os.path.join(MEMORY_DIR, "consolidations.md")


def get_recent_daily_files(days=3):
    """Get daily memory files from the last N days."""
    files = []
    for i in range(days):
        date = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
        path = os.path.join(MEMORY_DIR, f"{date}.md")
        if os.path.exists(path):
            files.append((date, path))
    return files


def read_file(path, max_chars=10000):
    """Read file content, truncated."""
    try:
        with open(path, "r") as f:
            content = f.read()
        return content[:max_chars]
    except Exception as e:
        return f"[Error reading {path}: {e}]"


def get_unconsolidated_entries(daily_files, consolidation_file):
    """Find entries not yet consolidated."""
    # Read existing consolidation timestamps
    consolidated_dates = set()
    if os.path.exists(consolidation_file):
        with open(consolidation_file, "r") as f:
            for line in f:
                if line.startswith("## Consolidated:"):
                    date_str = line.strip().split("Consolidated: ")[-1]
                    consolidated_dates.add(date_str)

    unconsolidated = []
    for date, path in daily_files:
        if date not in consolidated_dates:
            content = read_file(path)
            if content.strip():
                unconsolidated.append((date, content))

    return unconsolidated


def build_consolidation_prompt(unconsolidated, long_term_memory):
    """Build the prompt for consolidation."""
    prompt = """You are a memory consolidation system. Like the human brain during sleep,
your job is to review recent memories, find connections, generate insights, and identify
contradictions or patterns.

## Long-Term Memory (summary):
"""
    prompt += long_term_memory[:5000] + "\n\n"
    prompt += "## Recent Unconsolidated Memories:\n\n"

    for date, content in unconsolidated:
        prompt += f"### {date}\n{content[:3000]}\n\n"

    prompt += """## Your Task:
1. **Connections**: What links exist between recent events and long-term memory?
2. **Insights**: What patterns or themes emerge?
3. **Contradictions**: Does anything recent contradict earlier decisions or learnings?
4. **Action items**: What should be done based on these connections?
5. **Updates to long-term memory**: What from recent memories should be promoted to MEMORY.md?

Be concise. Focus on non-obvious connections. Skip anything trivial."""

    return prompt


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Memory Consolidation Loop")
    parser.add_argument("--days", type=int, default=3, help="Days to look back")
    parser.add_argument("--dry-run", action="store_true", help="Print prompt without running")
    parser.add_argument("--check", action="store_true", help="Check if consolidation needed")
    args = parser.parse_args()

    daily_files = get_recent_daily_files(args.days)
    unconsolidated = get_unconsolidated_entries(daily_files, CONSOLIDATION_FILE)

    if args.check:
        if unconsolidated:
            print(f"NEEDS_CONSOLIDATION: {len(unconsolidated)} days unconsolidated")
            for date, _ in unconsolidated:
                print(f"  - {date}")
        else:
            print("CONSOLIDATED: All recent memories are consolidated")
        sys.exit(0 if not unconsolidated else 1)

    if not unconsolidated:
        print("Nothing to consolidate.")
        sys.exit(0)

    long_term = read_file(MEMORY_MD, max_chars=5000) if os.path.exists(MEMORY_MD) else "[No long-term memory]"
    prompt = build_consolidation_prompt(unconsolidated, long_term)

    if args.dry_run:
        print("=== CONSOLIDATION PROMPT ===")
        print(prompt)
        print(f"\n=== {len(unconsolidated)} days to consolidate ===")
        sys.exit(0)

    # Output the prompt for the agent to process
    # The agent will call this script, get the prompt, run it through an LLM,
    # and write the results to consolidations.md
    print(json.dumps({
        "action": "consolidate",
        "days_unconsolidated": len(unconsolidated),
        "dates": [d for d, _ in unconsolidated],
        "prompt": prompt
    }))


if __name__ == "__main__":
    main()
