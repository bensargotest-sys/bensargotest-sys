#!/usr/bin/env python3
"""
mistake_promoter.py - Promote recurring mistakes to permanent enforcement rules

Usage:
    python3 tools/mistake_promoter.py scan
    python3 tools/mistake_promoter.py promote "pattern-id" "Rule text"
    python3 tools/mistake_promoter.py stats

Automatically detects patterns (2+ similar mistakes) and promotes them to ENFORCEMENT.md.
"""

import sys
import re
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

MISTAKES_FILE = Path(__file__).parent.parent / "memory" / "archival" / "mistakes.md"
ENFORCEMENT_FILE = Path(__file__).parent.parent / "ENFORCEMENT.md"

def read_mistakes():
    """Read all logged mistakes."""
    if not MISTAKES_FILE.exists():
        return []
    
    with open(MISTAKES_FILE, "r") as f:
        lines = f.readlines()
    
    mistakes = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            mistakes.append(line)
    
    return mistakes

def extract_patterns(mistakes):
    """Extract patterns from mistakes using keyword matching."""
    patterns = defaultdict(list)
    
    # Define pattern keywords
    keywords = {
        "github-push": ["github", "push", "secret", "token", "blocked"],
        "subagent-fail": ["subagent", "spawn", "fail", "stall", "empty"],
        "tool-reuse": ["forgot", "tool", "exist", "rebuild", "duplicate"],
        "context-loss": ["forget", "decision", "compaction", "lost", "re-ask"],
        "timeout": ["timeout", "hang", "stuck", "frozen"],
        "path-error": ["path", "not found", "no such file", "directory"],
        "api-error": ["api", "endpoint", "authentication", "rate limit"],
    }
    
    for mistake in mistakes:
        mistake_lower = mistake.lower()
        for pattern_id, pattern_keywords in keywords.items():
            if any(kw in mistake_lower for kw in pattern_keywords):
                patterns[pattern_id].append(mistake)
    
    return patterns

def scan():
    """Scan for recurring patterns."""
    mistakes = read_mistakes()
    
    if not mistakes:
        print("No mistakes logged yet.")
        return
    
    patterns = extract_patterns(mistakes)
    
    # Filter for 2+ occurrences
    recurring = {k: v for k, v in patterns.items() if len(v) >= 2}
    
    if not recurring:
        print(f"✓ No recurring patterns found ({len(mistakes)} mistakes logged)")
        print("  Keep logging mistakes - patterns will emerge.")
        return
    
    print(f"\n🔍 Recurring Patterns Found ({len(recurring)}):\n")
    
    for pattern_id, instances in recurring.items():
        print(f"**{pattern_id}** ({len(instances)} occurrences)")
        for instance in instances[:3]:  # Show first 3
            print(f"  - {instance[:80]}...")
        if len(instances) > 3:
            print(f"  ... and {len(instances) - 3} more")
        print()
    
    print("To promote a pattern:")
    print('  python3 tools/mistake_promoter.py promote "pattern-id" "Rule text"')

def promote(pattern_id, rule_text):
    """Promote a pattern to ENFORCEMENT.md."""
    if not ENFORCEMENT_FILE.exists():
        print("ERROR: ENFORCEMENT.md not found")
        return
    
    # Read current enforcement file
    with open(ENFORCEMENT_FILE, "r") as f:
        content = f.read()
    
    # Check if pattern already promoted
    if pattern_id in content:
        print(f"⚠️  Pattern '{pattern_id}' already promoted to ENFORCEMENT.md")
        return
    
    # Find the "Promoted Rules" section
    if "## Promoted Rules" not in content:
        print("ERROR: No '## Promoted Rules' section in ENFORCEMENT.md")
        return
    
    # Count existing promoted rules
    rule_count = content.count("### Promoted Rule #")
    new_rule_num = rule_count + 1
    
    # Generate new rule entry
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    new_rule = f"""
### Promoted Rule #{new_rule_num} ({today})
**From mistake pattern:** {pattern_id}
**Rule:** {rule_text}
"""
    
    # Insert before the closing meta-rule section or at the end
    if "## Meta-Rule" in content:
        parts = content.split("## Meta-Rule")
        content = parts[0] + new_rule + "\n## Meta-Rule" + parts[1]
    else:
        content += new_rule
    
    # Write back
    with open(ENFORCEMENT_FILE, "w") as f:
        f.write(content)
    
    print(f"✓ Promoted pattern '{pattern_id}' to ENFORCEMENT.md as Rule #{new_rule_num}")
    print(f"  Rule: {rule_text}")

def stats():
    """Show promotion statistics."""
    mistakes = read_mistakes()
    
    if not mistakes:
        print("No mistakes logged yet.")
        return
    
    # Read enforcement file to count promoted rules
    if ENFORCEMENT_FILE.exists():
        with open(ENFORCEMENT_FILE, "r") as f:
            content = f.read()
        promoted_count = content.count("### Promoted Rule #")
    else:
        promoted_count = 0
    
    # Extract patterns
    patterns = extract_patterns(mistakes)
    recurring = {k: v for k, v in patterns.items() if len(v) >= 2}
    
    total_mistakes = len(mistakes)
    total_patterns = len(patterns)
    recurring_patterns = len(recurring)
    promotion_rate = (promoted_count / total_mistakes * 100) if total_mistakes > 0 else 0
    
    print(f"\n📊 Mistake Promotion Statistics\n")
    print(f"Total Mistakes:       {total_mistakes}")
    print(f"Unique Patterns:      {total_patterns}")
    print(f"Recurring Patterns:   {recurring_patterns} (2+ occurrences)")
    print(f"Promoted to Rules:    {promoted_count}")
    print(f"Promotion Rate:       {promotion_rate:.1f}%")
    print()
    
    if promotion_rate < 30:
        print(f"⚠️  Target promotion rate: >30%")
        print(f"   Current: {promotion_rate:.1f}%")
        print(f"   Scan for patterns and promote recurring issues.")
    else:
        print(f"✓ Promotion rate healthy (>30%)")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "scan":
        scan()
    
    elif command == "promote":
        if len(sys.argv) < 4:
            print("Usage: mistake_promoter.py promote <pattern-id> <rule-text>")
            sys.exit(1)
        
        pattern_id = sys.argv[2]
        rule_text = " ".join(sys.argv[3:])
        promote(pattern_id, rule_text)
    
    elif command == "stats":
        stats()
    
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()
