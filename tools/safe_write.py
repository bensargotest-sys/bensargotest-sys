#!/usr/bin/env python3
"""
safe_write.py - Write files with backup and validation

Usage:
    python3 tools/safe_write.py target.md < content
    echo "content" | python3 tools/safe_write.py target.md

Creates backup before writing, validates after.
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime

def safe_write(target_path, content):
    """Write file with backup."""
    target = Path(target_path)
    
    # Create backup if file exists
    if target.exists():
        backup_dir = target.parent / ".backups"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"{target.name}.{timestamp}.bak"
        
        shutil.copy2(target, backup_path)
        print(f"✓ Backup: {backup_path}")
    
    # Write new content
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w") as f:
        f.write(content)
    
    # Validate
    if not target.exists():
        print(f"✗ Write failed: {target}")
        sys.exit(1)
    
    size = target.stat().st_size
    print(f"✓ Written: {target} ({size} bytes)")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    target_path = sys.argv[1]
    
    # Read from stdin
    content = sys.stdin.read()
    
    if not content:
        print("Error: No content provided")
        sys.exit(1)
    
    safe_write(target_path, content)

if __name__ == "__main__":
    main()
