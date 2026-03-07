#!/usr/bin/env python3
"""
Feedback logging utility
Categorize and track user feedback across all channels
"""

import json
import sys
from datetime import datetime, timezone

FEEDBACK_FILE = "/data/.openclaw/workspace/feedback-tracker.json"

def load_feedback():
    """Load feedback from file"""
    try:
        with open(FEEDBACK_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "feature_requests": [],
            "bug_reports": [],
            "use_cases": [],
            "questions": [],
            "criticism": [],
            "positive_feedback": []
        }

def save_feedback(data):
    """Save feedback to file"""
    with open(FEEDBACK_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def add_feedback(category, channel, user, content, context=""):
    """Add feedback entry"""
    feedback = load_feedback()
    
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "channel": channel,
        "user": user,
        "content": content,
        "context": context,
        "status": "new"
    }
    
    if category in feedback:
        feedback[category].append(entry)
        save_feedback(feedback)
        print(f"✅ Logged {category}: {content[:50]}...")
        return True
    else:
        print(f"❌ Invalid category: {category}")
        return False

def list_feedback(category=None, status=None):
    """List feedback, optionally filtered"""
    feedback = load_feedback()
    
    if category:
        items = feedback.get(category, [])
        if status:
            items = [i for i in items if i.get("status") == status]
        print(f"\n{category.upper()} ({len(items)} items):")
        for idx, item in enumerate(items, 1):
            print(f"\n{idx}. [{item['channel']}] @{item['user']}")
            print(f"   {item['content']}")
            print(f"   Status: {item['status']} | {item['timestamp']}")
    else:
        print("\n📊 Feedback Summary:")
        for cat, items in feedback.items():
            print(f"  {cat}: {len(items)} items")

def summary():
    """Print summary statistics"""
    feedback = load_feedback()
    
    print("\n📊 Feedback Summary")
    print("=" * 50)
    
    total = sum(len(items) for items in feedback.values())
    print(f"Total feedback items: {total}\n")
    
    for category, items in feedback.items():
        if items:
            new = len([i for i in items if i.get("status") == "new"])
            print(f"{category}:")
            print(f"  Total: {len(items)}")
            print(f"  New: {new}")
            print(f"  Addressed: {len(items) - new}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 log-feedback.py add <category> <channel> <user> <content> [context]")
        print("  python3 log-feedback.py list [category] [status]")
        print("  python3 log-feedback.py summary")
        print("\nCategories: feature_requests, bug_reports, use_cases, questions, criticism, positive_feedback")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "add" and len(sys.argv) >= 6:
        category = sys.argv[2]
        channel = sys.argv[3]
        user = sys.argv[4]
        content = sys.argv[5]
        context = sys.argv[6] if len(sys.argv) > 6 else ""
        add_feedback(category, channel, user, content, context)
    
    elif action == "list":
        category = sys.argv[2] if len(sys.argv) > 2 else None
        status = sys.argv[3] if len(sys.argv) > 3 else None
        list_feedback(category, status)
    
    elif action == "summary":
        summary()
    
    else:
        print("Invalid command")
        sys.exit(1)
