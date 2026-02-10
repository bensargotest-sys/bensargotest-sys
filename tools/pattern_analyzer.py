#!/usr/bin/env python3
"""
pattern_analyzer.py - Detect patterns in agent behavior and user interactions

Analyzes logs, mistakes, and activity to identify:
- Recurring issues
- Common workflows
- Time-of-day patterns
- Tool usage frequency

Usage:
    python3 tools/pattern_analyzer.py analyze [--days 7]
    python3 tools/pattern_analyzer.py report [--format json|human]
"""

import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path("/data/.openclaw/workspace")
MISTAKE_LOG = WORKSPACE / "memory" / "mistakes.jsonl"
WORK_LOG = WORKSPACE / "memory" / "work-log.md"
PATTERNS_FILE = WORKSPACE / "memory" / "patterns.json"

def load_mistakes():
    """Load mistake log"""
    if not MISTAKE_LOG.exists():
        return []
    
    mistakes = []
    with open(MISTAKE_LOG, "r") as f:
        for line in f:
            if line.strip():
                mistakes.append(json.loads(line))
    return mistakes

def analyze_patterns(days=7):
    """Analyze patterns in logs and mistakes"""
    mistakes = load_mistakes()
    
    # Analyze mistake patterns
    mistake_categories = Counter(m.get("category", "unknown") for m in mistakes)
    mistake_tools = Counter(m.get("tool", "unknown") for m in mistakes if m.get("tool"))
    
    # Analyze work log patterns (simplified - would need better parsing)
    work_activities = []
    if WORK_LOG.exists():
        content = WORK_LOG.read_text()
        lines = content.split("\n")
        for line in lines:
            if line.strip().startswith("##"):
                work_activities.append(line.strip("# "))
    
    patterns = {
        "analyzedAt": datetime.now(timezone.utc).isoformat(),
        "mistakePatterns": {
            "byCategory": dict(mistake_categories.most_common(10)),
            "byTool": dict(mistake_tools.most_common(10)),
            "totalMistakes": len(mistakes)
        },
        "workPatterns": {
            "recentActivities": work_activities[-20:] if work_activities else []
        },
        "insights": []
    }
    
    # Generate insights
    if mistake_categories:
        top_category = mistake_categories.most_common(1)[0]
        patterns["insights"].append({
            "type": "mistake_hotspot",
            "message": f"Most common mistake category: {top_category[0]} ({top_category[1]} occurrences)"
        })
    
    if mistake_tools:
        problematic_tool = mistake_tools.most_common(1)[0]
        patterns["insights"].append({
            "type": "tool_reliability",
            "message": f"Tool with most errors: {problematic_tool[0]} ({problematic_tool[1]} errors)"
        })
    
    # Save patterns
    PATTERNS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PATTERNS_FILE, "w") as f:
        json.dump(patterns, f, indent=2)
    
    return patterns

def format_report(patterns, format="human"):
    """Format patterns report"""
    if format == "json":
        return json.dumps(patterns, indent=2)
    
    lines = []
    lines.append(f"📊 Pattern Analysis Report")
    lines.append(f"Analyzed: {patterns['analyzedAt']}")
    lines.append("=" * 60)
    
    # Mistake patterns
    mp = patterns["mistakePatterns"]
    lines.append(f"\n## Mistake Patterns ({mp['totalMistakes']} total)")
    
    if mp["byCategory"]:
        lines.append("\n### By Category:")
        for category, count in sorted(mp["byCategory"].items(), key=lambda x: -x[1])[:5]:
            bar = "█" * min(count, 20)
            lines.append(f"  {bar} {category}: {count}")
    
    if mp["byTool"]:
        lines.append("\n### By Tool:")
        for tool, count in sorted(mp["byTool"].items(), key=lambda x: -x[1])[:5]:
            bar = "█" * min(count, 20)
            lines.append(f"  {bar} {tool}: {count}")
    
    # Insights
    if patterns["insights"]:
        lines.append(f"\n## 💡 Insights ({len(patterns['insights'])})")
        for insight in patterns["insights"]:
            icon = "🔴" if insight["type"] == "mistake_hotspot" else "🔧"
            lines.append(f"  {icon} {insight['message']}")
    
    # Recent work
    if patterns["workPatterns"]["recentActivities"]:
        lines.append(f"\n## Recent Work Activities")
        for activity in patterns["workPatterns"]["recentActivities"][-10:]:
            lines.append(f"  • {activity}")
    
    return "\n".join(lines)

def main():
    if len(sys.argv) < 2:
        print("Usage: pattern_analyzer.py analyze|report [args]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "analyze":
        days = 7
        if "--days" in sys.argv:
            idx = sys.argv.index("--days")
            if idx + 1 < len(sys.argv):
                days = int(sys.argv[idx + 1])
        
        patterns = analyze_patterns(days)
        print(format_report(patterns, "human"))
    
    elif command == "report":
        format = "human"
        if "--format" in sys.argv:
            idx = sys.argv.index("--format")
            if idx + 1 < len(sys.argv):
                format = sys.argv[idx + 1]
        
        if not PATTERNS_FILE.exists():
            print("❌ No analysis results found. Run 'analyze' first.")
            sys.exit(1)
        
        with open(PATTERNS_FILE, "r") as f:
            patterns = json.load(f)
        
        print(format_report(patterns, format))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
