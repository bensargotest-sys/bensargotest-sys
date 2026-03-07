#!/usr/bin/env python3
"""Detect work gaps >2h in heartbeat_enforcer log."""

import json
import os
import sys
from datetime import datetime, timedelta

LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "memory", "work-log.md")

def parse_timestamps():
    """Extract timestamps from work-log.md entries."""
    timestamps = []
    if not os.path.exists(LOG_FILE):
        print("ERROR: work-log.md not found")
        sys.exit(1)
    
    with open(LOG_FILE) as f:
        for line in f:
            line = line.strip()
            # Match "## YYYY-MM-DD HH:MM UTC [...]"
            if line.startswith("## ") and "UTC" in line:
                try:
                    ts_str = line[3:].split("UTC")[0].strip()
                    ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M")
                    timestamps.append(ts)
                except (ValueError, IndexError):
                    pass
            # Match "[YYYY-MM-DDTHH:MM:SS UTC]"
            elif "[202" in line and "UTC]" in line:
                try:
                    start = line.index("[202") + 1
                    end = line.index("UTC]")
                    ts_str = line[start:end].strip()
                    ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                    timestamps.append(ts)
                except (ValueError, IndexError):
                    pass
    return sorted(timestamps)

def detect_gaps(threshold_hours=2):
    timestamps = parse_timestamps()
    if len(timestamps) < 2:
        print(f"Only {len(timestamps)} entries found, need at least 2")
        return []
    
    gaps = []
    for i in range(1, len(timestamps)):
        delta = timestamps[i] - timestamps[i-1]
        if delta > timedelta(hours=threshold_hours):
            gaps.append({
                "start": timestamps[i-1].isoformat(),
                "end": timestamps[i].isoformat(),
                "hours": round(delta.total_seconds() / 3600, 1)
            })
    
    return gaps

def main():
    threshold = float(sys.argv[1]) if len(sys.argv) > 1 else 2.0
    gaps = detect_gaps(threshold)
    
    if not gaps:
        print(f"NO_GAPS (threshold: {threshold}h)")
        sys.exit(0)
    
    print(f"Found {len(gaps)} gaps > {threshold}h:")
    for g in gaps:
        print(f"  {g['start']} → {g['end']} ({g['hours']}h)")
    
    # Last 24h gaps are alerts
    now = datetime.utcnow()
    recent = [g for g in gaps if datetime.fromisoformat(g['end']) > now - timedelta(hours=24)]
    if recent:
        print(f"\n⚠️ {len(recent)} gaps in last 24h")
        sys.exit(1)

if __name__ == "__main__":
    main()
