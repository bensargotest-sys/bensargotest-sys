#!/usr/bin/env python3
"""
Engagement Monitor - Automated tracking script
Monitors Moltbook, Twitter, HN, Reddit for engagement
"""

import json
import time
from datetime import datetime, timezone

STATE_FILE = "/data/.openclaw/workspace/engagement-state.json"
LOG_FILE = "/data/.openclaw/workspace/ENGAGEMENT-LOG.md"

def load_state():
    """Load previous state from file"""
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "moltbook": {
                "upvotes": 0,
                "comments": 0,
                "last_check": None
            },
            "github": {
                "stars": 0,
                "last_check": None
            },
            "twitter": {
                "posted": False,
                "mentions": 0,
                "last_check": None
            },
            "hacker_news": {
                "posted": False,
                "post_time": "14:00",
                "upvotes": 0,
                "comments": 0,
                "last_check": None
            },
            "reddit": {
                "posted": False,
                "threads": [],
                "last_check": None
            }
        }

def save_state(state):
    """Save current state to file"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def log_event(event_type, channel, details):
    """Append event to engagement log"""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    
    with open(LOG_FILE, 'a') as f:
        f.write(f"\n### {timestamp} - {event_type}\n")
        f.write(f"- **Channel:** {channel}\n")
        for key, value in details.items():
            f.write(f"- **{key.title()}:** {value}\n")

def check_moltbook_status():
    """Check current Moltbook metrics"""
    # This will be called via browser automation
    # Return placeholder for now
    return {
        "upvotes": 0,
        "comments": 0,
        "new_comments": []
    }

def check_github_stars():
    """Check GitHub star count"""
    # This will be called via web fetch
    return 0

def should_check_channel(state, channel, interval_minutes):
    """Determine if we should check a channel based on last check time"""
    last_check = state.get(channel, {}).get("last_check")
    if not last_check:
        return True
    
    last_time = datetime.fromisoformat(last_check)
    now = datetime.now(timezone.utc)
    elapsed = (now - last_time).total_seconds() / 60
    
    return elapsed >= interval_minutes

def get_next_check_time(interval_minutes):
    """Calculate next check time"""
    now = datetime.now(timezone.utc)
    next_check = now.timestamp() + (interval_minutes * 60)
    return datetime.fromtimestamp(next_check, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

if __name__ == "__main__":
    print("Engagement Monitor - Status Check")
    print("=" * 50)
    
    state = load_state()
    now = datetime.now(timezone.utc)
    
    # Check what needs attention
    checks_needed = []
    
    if should_check_channel(state, "moltbook", 10):
        checks_needed.append("Moltbook (every 10 min)")
    
    if should_check_channel(state, "github", 60):
        checks_needed.append("GitHub stars (every hour)")
    
    # Check if HN should be posted (14:00 UTC)
    if now.hour >= 14 and not state["hacker_news"]["posted"]:
        checks_needed.append("Hacker News (POST NOW - 14:00 UTC)")
    
    if checks_needed:
        print("\n🔔 Checks needed:")
        for check in checks_needed:
            print(f"  - {check}")
    else:
        print("\n✅ All checks up to date")
    
    # Display current metrics
    print("\n📊 Current Metrics:")
    print(f"  Moltbook: {state['moltbook']['upvotes']} upvotes, {state['moltbook']['comments']} comments")
    print(f"  GitHub: {state['github']['stars']} stars")
    print(f"  Twitter: {'Posted' if state['twitter']['posted'] else 'Not posted yet'}")
    print(f"  HN: {'Posted' if state['hacker_news']['posted'] else 'Not posted yet (scheduled 14:00 UTC)'}")
    print(f"  Reddit: {'Posted' if state['reddit']['posted'] else 'Not posted yet'}")
    
    # Show next check times
    print("\n⏰ Next check times:")
    if state["moltbook"]["last_check"]:
        print(f"  Moltbook: {get_next_check_time(10)}")
    if state["github"]["last_check"]:
        print(f"  GitHub: {get_next_check_time(60)}")
