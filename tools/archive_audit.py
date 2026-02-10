#!/usr/bin/env python3
"""
archive_audit.py - Find stale files with rotting action items

Usage:
    python3 tools/archive_audit.py scan
    python3 tools/archive_audit.py report --days 30

Scans workspace for files with TODO/FIXME/TODO items that are old or stale.
"""

import sys
import re
from pathlib import Path
from datetime import datetime, timezone

WORKSPACE = Path(__file__).parent.parent
ACTION_PATTERNS = [
    r'\[ \]',  # Unchecked checkbox
    r'TODO:',
    r'FIXME:',
    r'BLOCKED:',
    r'NEXT:',
    r'ACTION:',
]

def find_action_items(file_path):
    """Find action items in a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return []
    
    items = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        for pattern in ACTION_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                items.append({
                    'line': i,
                    'text': line.strip()[:80]  # First 80 chars
                })
                break
    
    return items

def get_file_age_days(file_path):
    """Get file age in days since last modification."""
    stat = file_path.stat()
    age_seconds = datetime.now().timestamp() - stat.st_mtime
    return age_seconds / 86400  # Convert to days

def scan_workspace(min_age_days=7):
    """Scan for stale files with action items."""
    stale_files = []
    
    # Scan markdown files in workspace
    for md_file in WORKSPACE.rglob("*.md"):
        # Skip certain directories
        skip_dirs = ['node_modules', '.git', 'tsp', 'tsp-fresh', 'tsp-integration']
        if any(skip in str(md_file) for skip in skip_dirs):
            continue
        
        age_days = get_file_age_days(md_file)
        
        if age_days < min_age_days:
            continue
        
        action_items = find_action_items(md_file)
        
        if action_items:
            rel_path = md_file.relative_to(WORKSPACE)
            stale_files.append({
                'path': rel_path,
                'age_days': age_days,
                'items': action_items
            })
    
    return stale_files

def scan():
    """Run scan and display results."""
    print("\n🔍 Archive Audit: Scanning for stale action items...\n")
    
    stale_files = scan_workspace(min_age_days=7)
    
    if not stale_files:
        print("✓ No stale files with action items found")
        print("  (Scanned .md files >7 days old)")
        return
    
    # Sort by age (oldest first)
    stale_files.sort(key=lambda x: x['age_days'], reverse=True)
    
    print(f"Found {len(stale_files)} files with stale action items:\n")
    
    for item in stale_files:
        print(f"📄 {item['path']} ({int(item['age_days'])} days old)")
        print(f"   {len(item['items'])} action item(s):")
        for action in item['items'][:3]:  # Show first 3
            print(f"   L{action['line']}: {action['text']}")
        if len(item['items']) > 3:
            print(f"   ... and {len(item['items']) - 3} more")
        print()
    
    print("\n**Recommendations:**")
    print("  - Review files >30 days: decide to complete, archive, or delete")
    print("  - Update or remove stale action items")
    print("  - Move completed work to archive/")

def report(days=30):
    """Generate detailed report."""
    print(f"\n📊 Archive Audit Report (files >{days} days old)\n")
    
    stale_files = scan_workspace(min_age_days=days)
    
    if not stale_files:
        print(f"✓ No files >{days} days old with action items")
        return
    
    # Group by age buckets
    buckets = {
        '7-30 days': [],
        '30-90 days': [],
        '90+ days': []
    }
    
    for item in stale_files:
        age = item['age_days']
        if age < 30:
            buckets['7-30 days'].append(item)
        elif age < 90:
            buckets['30-90 days'].append(item)
        else:
            buckets['90+ days'].append(item)
    
    for bucket_name, items in buckets.items():
        if not items:
            continue
        
        print(f"\n**{bucket_name}:** {len(items)} file(s)")
        for item in items[:5]:  # Show top 5
            print(f"  - {item['path']} ({len(item['items'])} items)")
        if len(items) > 5:
            print(f"  ... and {len(items) - 5} more")
    
    print()

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "scan":
        scan()
    
    elif command == "report":
        days = 30
        if "--days" in sys.argv:
            try:
                idx = sys.argv.index("--days")
                days = int(sys.argv[idx + 1])
            except (IndexError, ValueError):
                print("Invalid --days value")
                sys.exit(1)
        
        report(days)
    
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()
