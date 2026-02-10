#!/usr/bin/env python3
"""
self_eval.py - Self-evaluate output quality

Usage:
    python3 tools/self_eval.py log --auto
    python3 tools/self_eval.py report

Tracks output quality over time for continuous improvement.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone

EVAL_LOG = Path(__file__).parent.parent / "memory" / "self-improvement-log.md"

def auto_eval():
    """Run automatic self-evaluation."""
    questions = [
        "Did I follow enforcement gates?",
        "Did I checkpoint before major work?",
        "Did I delegate tasks >10 minutes?",
        "Did I provide evidence for claims?",
        "Did I update WORKING_STATE.md?"
    ]
    
    print("\n🔍 Self-Evaluation\n")
    
    for q in questions:
        print(f"✓ {q}")
    
    # Log to file
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    
    EVAL_LOG.parent.mkdir(exist_ok=True)
    with open(EVAL_LOG, "a") as f:
        f.write(f"\n## {timestamp}\n\n")
        for q in questions:
            f.write(f"- [ ] {q}\n")
        f.write("\n")
    
    print(f"\n✓ Logged to {EVAL_LOG}")

def report():
    """Generate self-evaluation report."""
    if not EVAL_LOG.exists():
        print("No self-evaluations logged yet")
        return
    
    with open(EVAL_LOG, "r") as f:
        content = f.read()
    
    sections = content.split('\n## ')
    eval_count = len([s for s in sections if s.strip()]) - 1  # Exclude header
    
    print(f"\n📊 Self-Evaluation Report\n")
    print(f"Total Evaluations: {eval_count}")
    print(f"Log file: {EVAL_LOG}")
    print()

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "log":
        auto = "--auto" in sys.argv
        if auto:
            auto_eval()
        else:
            print("Use --auto for automatic evaluation")
    
    elif command == "report":
        report()
    
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()
