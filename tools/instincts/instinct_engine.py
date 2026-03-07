#!/usr/bin/env python3
"""
Instinct Engine — Learns patterns from agent behavior over time.

Reads memory files, mistakes, scorecard, and work logs.
Extracts recurring patterns. Clusters them into "instincts" (learned behaviors).
Evolves weekly — promotes strong patterns into actionable rules.

Usage:
    python3 tools/instincts/instinct_engine.py scan          # Scan recent files for patterns
    python3 tools/instincts/instinct_engine.py show           # Show current instincts
    python3 tools/instincts/instinct_engine.py evolve         # Weekly: cluster and promote
    python3 tools/instincts/instinct_engine.py suggest        # Get instinct-based suggestions
"""

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

WORKSPACE = Path("/data/.openclaw/workspace")
INSTINCTS_FILE = WORKSPACE / "memory" / "instincts.json"
MISTAKES_FILE = WORKSPACE / "memory" / "mistakes.json"
SCORECARD_FILE = WORKSPACE / "memory" / "partner-scorecard.json"
MEMORY_DIR = WORKSPACE / "memory"
WORK_LOG = MEMORY_DIR / "work-log.md"

# Pattern categories
CATEGORIES = {
    "time_patterns": "When things happen (time-of-day, day-of-week preferences)",
    "failure_patterns": "Recurring failure modes and their triggers",
    "success_patterns": "What works consistently well",
    "tool_patterns": "Tool usage frequency and effectiveness",
    "communication_patterns": "How the human prefers to interact",
    "decision_patterns": "Decision-making tendencies and outcomes"
}

def load_instincts():
    if INSTINCTS_FILE.exists():
        return json.loads(INSTINCTS_FILE.read_text())
    return {
        "version": 1,
        "lastScan": None,
        "lastEvolve": None,
        "patterns": [],
        "instincts": [],
        "rawSignals": []
    }

def save_instincts(data):
    INSTINCTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    INSTINCTS_FILE.write_text(json.dumps(data, indent=2))

def scan_memory_files(days=7):
    """Extract signals from recent memory files"""
    signals = []
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=days)

    for f in sorted(MEMORY_DIR.glob("2026-*.md")):
        # Parse date from filename
        try:
            fdate = datetime.strptime(f.stem, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        if fdate < cutoff:
            continue

        content = f.read_text(errors='ignore')
        lines = content.split('\n')

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Detect failure signals
            if any(w in line.lower() for w in ['fail', 'error', 'bug', 'broke', 'wrong', 'mistake', 'fix']):
                signals.append({
                    "type": "failure",
                    "source": f.name,
                    "text": line[:200],
                    "date": f.stem
                })

            # Detect success signals
            if any(w in line.lower() for w in ['✅', 'complete', 'done', 'success', 'working', 'deployed', 'fixed']):
                signals.append({
                    "type": "success",
                    "source": f.name,
                    "text": line[:200],
                    "date": f.stem
                })

            # Detect decision signals
            if any(w in line.lower() for w in ['decided', 'pivot', 'chose', 'switched', 'instead of', 'rather than']):
                signals.append({
                    "type": "decision",
                    "source": f.name,
                    "text": line[:200],
                    "date": f.stem
                })

            # Detect tool usage
            if any(w in line.lower() for w in ['python3 tools/', 'bash tools/', 'run ', 'execute']):
                signals.append({
                    "type": "tool_usage",
                    "source": f.name,
                    "text": line[:200],
                    "date": f.stem
                })

    return signals

def scan_mistakes():
    """Extract patterns from mistakes log"""
    signals = []
    if not MISTAKES_FILE.exists():
        return signals

    try:
        mistakes = json.loads(MISTAKES_FILE.read_text())
        if isinstance(mistakes, list):
            for m in mistakes[-20:]:
                signals.append({
                    "type": "mistake",
                    "source": "mistakes.json",
                    "text": str(m.get('description', m.get('mistake', str(m))))[:200],
                    "date": m.get('date', 'unknown')
                })
        elif isinstance(mistakes, dict):
            for entry in mistakes.get('entries', mistakes.get('mistakes', []))[-20:]:
                signals.append({
                    "type": "mistake",
                    "source": "mistakes.json",
                    "text": str(entry)[:200],
                    "date": entry.get('date', 'unknown') if isinstance(entry, dict) else 'unknown'
                })
    except (json.JSONDecodeError, Exception):
        pass

    return signals

def extract_patterns(signals):
    """Find recurring themes in signals"""
    patterns = []

    # Group by type
    by_type = defaultdict(list)
    for s in signals:
        by_type[s['type']].append(s)

    # Failure pattern: look for repeated words in failures
    if by_type['failure']:
        words = Counter()
        for s in by_type['failure']:
            for w in re.findall(r'\b[a-z]{4,}\b', s['text'].lower()):
                if w not in {'that', 'this', 'with', 'from', 'have', 'been', 'were', 'they', 'their', 'about', 'would', 'could', 'should', 'some', 'other'}:
                    words[w] += 1
        common = words.most_common(5)
        for word, count in common:
            if count >= 2:
                examples = [s['text'][:80] for s in by_type['failure'] if word in s['text'].lower()][:3]
                patterns.append({
                    "category": "failure_patterns",
                    "theme": word,
                    "frequency": count,
                    "confidence": min(1.0, count / 5),
                    "examples": examples,
                    "insight": f"'{word}' appears in {count} failure signals — possible recurring issue"
                })

    # Success pattern: what tools/approaches keep working
    if by_type['success']:
        words = Counter()
        for s in by_type['success']:
            for w in re.findall(r'\b[a-z]{4,}\b', s['text'].lower()):
                if w not in {'that', 'this', 'with', 'from', 'have', 'been', 'were', 'done', 'complete'}:
                    words[w] += 1
        common = words.most_common(5)
        for word, count in common:
            if count >= 2:
                patterns.append({
                    "category": "success_patterns",
                    "theme": word,
                    "frequency": count,
                    "confidence": min(1.0, count / 5),
                    "insight": f"'{word}' appears in {count} success signals — reliable approach"
                })

    # Tool usage frequency
    if by_type['tool_usage']:
        tools = Counter()
        for s in by_type['tool_usage']:
            match = re.search(r'tools/[\w/.-]+', s['text'])
            if match:
                tools[match.group()] += 1
        for tool, count in tools.most_common(5):
            patterns.append({
                "category": "tool_patterns",
                "theme": tool,
                "frequency": count,
                "confidence": min(1.0, count / 3),
                "insight": f"{tool} used {count} times — {'core tool' if count >= 3 else 'occasional use'}"
            })

    # Decision patterns
    if len(by_type['decision']) >= 2:
        patterns.append({
            "category": "decision_patterns",
            "theme": "active_decision_making",
            "frequency": len(by_type['decision']),
            "confidence": 0.5,
            "insight": f"{len(by_type['decision'])} explicit decisions logged — good decision hygiene"
        })

    return patterns

def scan(args):
    """Scan recent files and update patterns"""
    data = load_instincts()

    print("Scanning memory files (last 7 days)...")
    mem_signals = scan_memory_files(days=7)
    print(f"  Found {len(mem_signals)} signals from memory")

    print("Scanning mistakes log...")
    mistake_signals = scan_mistakes()
    print(f"  Found {len(mistake_signals)} signals from mistakes")

    all_signals = mem_signals + mistake_signals
    print(f"\nTotal signals: {len(all_signals)}")

    # Extract patterns
    patterns = extract_patterns(all_signals)
    print(f"Patterns found: {len(patterns)}")

    # Update data
    data["lastScan"] = datetime.now(tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    data["rawSignals"] = all_signals[-200:]  # Keep last 200
    data["patterns"] = patterns

    save_instincts(data)

    # Display
    if patterns:
        print("\n📊 Detected Patterns:")
        for p in patterns:
            conf_bar = "●" * int(p['confidence'] * 5) + "○" * (5 - int(p['confidence'] * 5))
            print(f"  [{p['category']}] {p['theme']} (×{p['frequency']}) [{conf_bar}]")
            print(f"    → {p['insight']}")
    else:
        print("\nNo strong patterns detected yet. Need more data.")

def show(args):
    """Show current instincts and patterns"""
    data = load_instincts()

    print("🧠 Instinct Engine Status")
    print("=" * 50)
    print(f"Last scan: {data.get('lastScan', 'never')}")
    print(f"Last evolve: {data.get('lastEvolve', 'never')}")
    print(f"Raw signals: {len(data.get('rawSignals', []))}")
    print(f"Patterns: {len(data.get('patterns', []))}")
    print(f"Instincts: {len(data.get('instincts', []))}")

    instincts = data.get('instincts', [])
    if instincts:
        print(f"\n💡 Active Instincts:")
        for i in instincts:
            print(f"  [{i['strength']:.0%}] {i['rule']}")
            print(f"    Based on: {i['evidence']}")
    
    patterns = data.get('patterns', [])
    if patterns:
        print(f"\n📊 Current Patterns:")
        for p in patterns[:10]:
            print(f"  [{p['category']}] {p['theme']} — {p['insight']}")

def evolve(args):
    """Weekly: promote strong patterns into instincts"""
    data = load_instincts()
    patterns = data.get('patterns', [])

    if not patterns:
        print("No patterns to evolve. Run 'scan' first.")
        return

    new_instincts = []
    existing_themes = {i['theme'] for i in data.get('instincts', [])}

    for p in patterns:
        # Promote patterns with high confidence and frequency
        if p['confidence'] >= 0.6 and p['frequency'] >= 3 and p['theme'] not in existing_themes:
            instinct = {
                "theme": p['theme'],
                "category": p['category'],
                "rule": generate_rule(p),
                "strength": p['confidence'],
                "evidence": p['insight'],
                "created": datetime.now(tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                "applied": 0
            }
            new_instincts.append(instinct)

    # Decay old instincts slightly
    for i in data.get('instincts', []):
        i['strength'] = max(0.1, i['strength'] * 0.95)

    # Add new instincts
    data['instincts'] = data.get('instincts', []) + new_instincts
    data['lastEvolve'] = datetime.now(tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    # Remove dead instincts (strength < 0.2)
    data['instincts'] = [i for i in data['instincts'] if i['strength'] >= 0.2]

    save_instincts(data)

    print(f"Evolution complete:")
    print(f"  New instincts: {len(new_instincts)}")
    print(f"  Total active: {len(data['instincts'])}")
    for i in new_instincts:
        print(f"  💡 NEW: [{i['strength']:.0%}] {i['rule']}")

def generate_rule(pattern):
    """Generate a human-readable rule from a pattern"""
    cat = pattern['category']
    theme = pattern['theme']

    if cat == 'failure_patterns':
        return f"Watch out for issues involving '{theme}' — recurring failure area"
    elif cat == 'success_patterns':
        return f"Keep using approaches involving '{theme}' — proven effective"
    elif cat == 'tool_patterns':
        return f"'{theme}' is a core tool — prioritize maintaining it"
    elif cat == 'decision_patterns':
        return f"Decision pattern '{theme}' detected — continue logging decisions explicitly"
    else:
        return f"Pattern '{theme}' in {cat} — monitor and adapt"

def suggest(args):
    """Get instinct-based suggestions for current context"""
    data = load_instincts()
    instincts = data.get('instincts', [])

    if not instincts:
        print("No instincts developed yet. Run 'scan' then 'evolve' first.")
        return

    print("🧠 Instinct Suggestions:")
    print()
    for i in sorted(instincts, key=lambda x: x['strength'], reverse=True):
        if i['strength'] >= 0.4:
            strength = "STRONG" if i['strength'] >= 0.7 else "MODERATE"
            print(f"  [{strength}] {i['rule']}")

def main():
    parser = argparse.ArgumentParser(description='Instinct Engine')
    sub = parser.add_subparsers(dest='command')

    sub.add_parser('scan', help='Scan recent files for patterns')
    sub.add_parser('show', help='Show current instincts')
    sub.add_parser('evolve', help='Promote patterns to instincts')
    sub.add_parser('suggest', help='Get instinct-based suggestions')

    args = parser.parse_args()
    if args.command == 'scan': scan(args)
    elif args.command == 'show': show(args)
    elif args.command == 'evolve': evolve(args)
    elif args.command == 'suggest': suggest(args)
    else: parser.print_help()

if __name__ == '__main__':
    main()
