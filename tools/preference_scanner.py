#!/usr/bin/env python3
"""
preference_scanner.py - Extract user preferences from conversations

Scans recent message history for expressions of preference and logs them
to memory/preferences.json for future reference.

Usage:
    python3 tools/preference_scanner.py scan [--days 7]
    python3 tools/preference_scanner.py list [--format json|human]
    python3 tools/preference_scanner.py add <category> <preference>
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path("/data/.openclaw/workspace")
PREFS_FILE = WORKSPACE / "memory" / "preferences.json"

# Keywords that might indicate preferences
PREFERENCE_KEYWORDS = [
    "i prefer", "i like", "i hate", "i dislike", "i want",
    "i don't like", "i don't want", "my favorite", "i love",
    "i always", "i never", "i usually", "please always",
    "please never", "don't ever", "make sure to"
]

def load_preferences():
    """Load preferences file"""
    if not PREFS_FILE.exists():
        return {"preferences": {}, "lastScan": None}
    
    with open(PREFS_FILE, "r") as f:
        return json.load(f)

def save_preferences(data):
    """Save preferences file"""
    PREFS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PREFS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_preference(category, preference):
    """Manually add a preference"""
    data = load_preferences()
    
    if category not in data["preferences"]:
        data["preferences"][category] = []
    
    pref_entry = {
        "text": preference,
        "addedAt": datetime.now(timezone.utc).isoformat(),
        "source": "manual"
    }
    
    data["preferences"][category].append(pref_entry)
    save_preferences(data)
    
    print(f"✅ Added preference: {category}")
    print(f"   {preference}")

def list_preferences(format="human"):
    """List all preferences"""
    data = load_preferences()
    
    if format == "json":
        print(json.dumps(data, indent=2))
        return
    
    if not data["preferences"]:
        print("📋 No preferences recorded")
        return
    
    print(f"📋 User Preferences")
    if data.get("lastScan"):
        print(f"Last scan: {data['lastScan']}")
    print("=" * 60)
    
    for category, prefs in sorted(data["preferences"].items()):
        print(f"\n## {category.upper()}")
        for pref in prefs:
            print(f"  • {pref['text']}")
            print(f"    Added: {pref['addedAt']} ({pref['source']})")

def scan_for_preferences(days=7):
    """
    Scan recent daily logs for preference expressions
    Note: This is a simplified version - production would use sessions_history
    """
    data = load_preferences()
    
    # Look for daily logs
    memory_dir = WORKSPACE / "memory"
    found_prefs = []
    
    for log_file in sorted(memory_dir.glob("2026-*.md"), reverse=True)[:days]:
        content = log_file.read_text()
        lines = content.lower().split("\n")
        
        for line in lines:
            for keyword in PREFERENCE_KEYWORDS:
                if keyword in line:
                    found_prefs.append({
                        "text": line.strip(),
                        "source": log_file.name,
                        "keyword": keyword
                    })
    
    data["lastScan"] = datetime.now(timezone.utc).isoformat()
    
    if found_prefs:
        print(f"🔍 Found {len(found_prefs)} potential preferences:")
        for pref in found_prefs[:10]:  # Show first 10
            print(f"  • {pref['text'][:100]}")
            print(f"    ({pref['source']}, keyword: '{pref['keyword']}')")
        
        if len(found_prefs) > 10:
            print(f"\n  ... and {len(found_prefs) - 10} more")
    else:
        print("🔍 No obvious preferences found in recent logs")
    
    save_preferences(data)
    return found_prefs

def main():
    if len(sys.argv) < 2:
        print("Usage: preference_scanner.py scan|list|add [args]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "scan":
        days = 7
        if "--days" in sys.argv:
            idx = sys.argv.index("--days")
            if idx + 1 < len(sys.argv):
                days = int(sys.argv[idx + 1])
        scan_for_preferences(days)
    
    elif command == "list":
        format = "human"
        if "--format" in sys.argv:
            idx = sys.argv.index("--format")
            if idx + 1 < len(sys.argv):
                format = sys.argv[idx + 1]
        list_preferences(format)
    
    elif command == "add":
        if len(sys.argv) < 4:
            print("Usage: preference_scanner.py add <category> <preference>")
            sys.exit(1)
        category = sys.argv[2]
        preference = " ".join(sys.argv[3:])
        add_preference(category, preference)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
