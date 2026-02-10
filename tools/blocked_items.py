#!/usr/bin/env python3
"""
blocked_items.py - Track and manage blocked work items

Maintains a registry of blocked tasks with blocker details, timestamps,
and resolution tracking. Use this to surface blockers that need human
intervention or external dependencies.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

BLOCKED_ITEMS_FILE = Path(__file__).parent.parent / "memory" / "blocked-items.json"


def load_blocked_items() -> List[Dict]:
    """Load blocked items from JSON file"""
    if not BLOCKED_ITEMS_FILE.exists():
        return []
    
    try:
        with open(BLOCKED_ITEMS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_blocked_items(items: List[Dict]) -> None:
    """Save blocked items to JSON file"""
    BLOCKED_ITEMS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(BLOCKED_ITEMS_FILE, 'w') as f:
        json.dump(items, f, indent=2)


def add_blocked_item(
    task: str,
    blocker: str,
    category: str = "general",
    context: Optional[str] = None,
    priority: str = "medium"
) -> None:
    """
    Add a new blocked item
    
    Args:
        task: Description of the blocked task
        blocker: What's blocking it
        category: Category (general, technical, external, permission, unclear)
        context: Additional context or details
        priority: Priority level (low, medium, high, critical)
    """
    items = load_blocked_items()
    
    # Check for duplicates
    for item in items:
        if item.get("task") == task and item.get("status") == "blocked":
            print(f"⚠️  Task already blocked: {task}")
            print(f"   Existing blocker: {item.get('blocker')}")
            return
    
    new_item = {
        "id": len(items) + 1,
        "task": task,
        "blocker": blocker,
        "category": category,
        "context": context,
        "priority": priority,
        "status": "blocked",
        "blocked_at": datetime.utcnow().isoformat() + "Z",
        "resolved_at": None,
        "resolution": None
    }
    
    items.append(new_item)
    save_blocked_items(items)
    
    print(f"✓ Blocked item added (ID: {new_item['id']})")
    print(f"  Task: {task}")
    print(f"  Blocker: {blocker}")
    print(f"  Priority: {priority}")


def resolve_blocked_item(item_id: int, resolution: str) -> None:
    """
    Mark a blocked item as resolved
    
    Args:
        item_id: ID of the blocked item
        resolution: How it was resolved
    """
    items = load_blocked_items()
    
    for item in items:
        if item.get("id") == item_id and item.get("status") == "blocked":
            item["status"] = "resolved"
            item["resolved_at"] = datetime.utcnow().isoformat() + "Z"
            item["resolution"] = resolution
            
            save_blocked_items(items)
            
            print(f"✓ Blocked item resolved (ID: {item_id})")
            print(f"  Task: {item.get('task')}")
            print(f"  Resolution: {resolution}")
            return
    
    print(f"⚠️  No active blocked item found with ID: {item_id}")


def list_blocked_items(
    status_filter: str = "blocked",
    category_filter: Optional[str] = None,
    priority_filter: Optional[str] = None
) -> None:
    """
    List blocked items with optional filters
    
    Args:
        status_filter: Filter by status (blocked, resolved, all)
        category_filter: Filter by category
        priority_filter: Filter by priority
    """
    items = load_blocked_items()
    
    # Apply filters
    filtered = items
    
    if status_filter != "all":
        filtered = [i for i in filtered if i.get("status") == status_filter]
    
    if category_filter:
        filtered = [i for i in filtered if i.get("category") == category_filter]
    
    if priority_filter:
        filtered = [i for i in filtered if i.get("priority") == priority_filter]
    
    if not filtered:
        print("No blocked items found.")
        return
    
    # Sort by priority (critical > high > medium > low) and then by date
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    filtered.sort(key=lambda x: (
        priority_order.get(x.get("priority", "medium"), 2),
        x.get("blocked_at", "")
    ))
    
    print(f"\n{'='*70}")
    print(f"Blocked Items ({len(filtered)} found)")
    print(f"{'='*70}\n")
    
    for item in filtered:
        priority_icons = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢"
        }
        icon = priority_icons.get(item.get("priority", "medium"), "⚪")
        
        print(f"{icon} ID: {item.get('id')} | {item.get('priority', 'medium').upper()} | {item.get('category', 'general')}")
        print(f"   Task: {item.get('task')}")
        print(f"   Blocker: {item.get('blocker')}")
        
        if item.get("context"):
            print(f"   Context: {item.get('context')}")
        
        blocked_at = item.get('blocked_at', '')
        if blocked_at:
            # Parse and format timestamp
            try:
                dt = datetime.fromisoformat(blocked_at.rstrip('Z'))
                age_hours = (datetime.utcnow() - dt).total_seconds() / 3600
                
                if age_hours < 24:
                    age_str = f"{age_hours:.1f} hours ago"
                else:
                    age_str = f"{age_hours/24:.1f} days ago"
                
                print(f"   Blocked: {age_str}")
            except:
                print(f"   Blocked: {blocked_at}")
        
        if item.get("status") == "resolved":
            print(f"   Resolution: {item.get('resolution')}")
            print(f"   Resolved: {item.get('resolved_at')}")
        
        print()


def summary() -> None:
    """Print summary statistics"""
    items = load_blocked_items()
    
    if not items:
        print("No blocked items tracked yet.")
        return
    
    blocked = [i for i in items if i.get("status") == "blocked"]
    resolved = [i for i in items if i.get("status") == "resolved"]
    
    # Count by priority
    priority_counts = {}
    for item in blocked:
        p = item.get("priority", "medium")
        priority_counts[p] = priority_counts.get(p, 0) + 1
    
    # Count by category
    category_counts = {}
    for item in blocked:
        c = item.get("category", "general")
        category_counts[c] = category_counts.get(c, 0) + 1
    
    print(f"\n{'='*70}")
    print("Blocked Items Summary")
    print(f"{'='*70}\n")
    
    print(f"Total tracked: {len(items)}")
    print(f"Currently blocked: {len(blocked)}")
    print(f"Resolved: {len(resolved)}")
    
    if priority_counts:
        print(f"\nBy Priority:")
        for p in ["critical", "high", "medium", "low"]:
            count = priority_counts.get(p, 0)
            if count > 0:
                print(f"  {p.capitalize()}: {count}")
    
    if category_counts:
        print(f"\nBy Category:")
        for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {count}")
    
    # Find oldest blocked item
    if blocked:
        oldest = min(blocked, key=lambda x: x.get("blocked_at", ""))
        try:
            dt = datetime.fromisoformat(oldest.get("blocked_at", "").rstrip('Z'))
            age_days = (datetime.utcnow() - dt).total_seconds() / 86400
            print(f"\nOldest blocker: {age_days:.1f} days")
            print(f"  Task: {oldest.get('task')}")
        except:
            pass


def main():
    """CLI interface"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  blocked_items.py add <task> <blocker> [--category=X] [--priority=X] [--context=X]")
        print("  blocked_items.py resolve <id> <resolution>")
        print("  blocked_items.py list [--status=blocked|resolved|all] [--category=X] [--priority=X]")
        print("  blocked_items.py summary")
        print()
        print("Categories: general, technical, external, permission, unclear")
        print("Priorities: low, medium, high, critical")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "add":
        if len(sys.argv) < 4:
            print("Error: add requires <task> and <blocker>")
            sys.exit(1)
        
        task = sys.argv[2]
        blocker = sys.argv[3]
        
        # Parse optional arguments
        category = "general"
        priority = "medium"
        context = None
        
        for arg in sys.argv[4:]:
            if arg.startswith("--category="):
                category = arg.split("=", 1)[1]
            elif arg.startswith("--priority="):
                priority = arg.split("=", 1)[1]
            elif arg.startswith("--context="):
                context = arg.split("=", 1)[1]
        
        add_blocked_item(task, blocker, category, context, priority)
    
    elif action == "resolve":
        if len(sys.argv) < 4:
            print("Error: resolve requires <id> and <resolution>")
            sys.exit(1)
        
        try:
            item_id = int(sys.argv[2])
        except ValueError:
            print("Error: ID must be a number")
            sys.exit(1)
        
        resolution = sys.argv[3]
        resolve_blocked_item(item_id, resolution)
    
    elif action == "list":
        status_filter = "blocked"
        category_filter = None
        priority_filter = None
        
        for arg in sys.argv[2:]:
            if arg.startswith("--status="):
                status_filter = arg.split("=", 1)[1]
            elif arg.startswith("--category="):
                category_filter = arg.split("=", 1)[1]
            elif arg.startswith("--priority="):
                priority_filter = arg.split("=", 1)[1]
        
        list_blocked_items(status_filter, category_filter, priority_filter)
    
    elif action == "summary":
        summary()
    
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)


if __name__ == "__main__":
    main()
