#!/bin/bash
# compaction_guard.sh - Check if WORKING_STATE.md is stale
# Returns: FRESH or STALE

WORKING_STATE="/data/.openclaw/workspace/WORKING_STATE.md"
STALE_THRESHOLD=3600  # 1 hour in seconds

if [ ! -f "$WORKING_STATE" ]; then
    echo "MISSING"
    exit 2
fi

# Get file modification time
MODIFIED=$(stat -c %Y "$WORKING_STATE" 2>/dev/null || stat -f %m "$WORKING_STATE" 2>/dev/null)
NOW=$(date +%s)
AGE=$((NOW - MODIFIED))

if [ $AGE -gt $STALE_THRESHOLD ]; then
    echo "STALE"
    exit 1
else
    echo "FRESH"
    exit 0
fi
