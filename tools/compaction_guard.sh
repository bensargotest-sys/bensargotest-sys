#!/bin/bash
# compaction_guard.sh - Check if WORKING_STATE.md is stale
# Returns: FRESH or STALE
# Usage:
#   bash tools/compaction_guard.sh              # Check only
#   bash tools/compaction_guard.sh --auto-save  # Auto-checkpoint if stale

WORKING_STATE="/data/.openclaw/workspace/memory/heartbeat-state.json"
STALE_THRESHOLD=3600  # 1 hour in seconds
AUTO_SAVE=false

# Check for --auto-save flag
if [ "$1" == "--auto-save" ]; then
    AUTO_SAVE=true
fi

if [ ! -f "$WORKING_STATE" ]; then
    echo "MISSING"
    exit 2
fi

# Get file modification time
MODIFIED=$(stat -c %Y "$WORKING_STATE" 2>/dev/null || stat -f %m "$WORKING_STATE" 2>/dev/null)
NOW=$(date +%s)
AGE=$((NOW - MODIFIED))
AGE_HOURS=$((AGE / 3600))

if [ $AGE -gt $STALE_THRESHOLD ]; then
    echo "STALE (${AGE_HOURS}h old)"
    
    # Auto-checkpoint if requested
    if [ "$AUTO_SAVE" = true ]; then
        echo "Auto-checkpointing..."
        python3 /data/.openclaw/workspace/tools/checkpoint.py --auto --note "auto-checkpoint (stale detected: ${AGE_HOURS}h old)"
        if [ $? -eq 0 ]; then
            echo "Checkpoint saved successfully"
        else
            echo "Checkpoint failed (but continuing)"
        fi
    fi
    
    exit 1
else
    echo "FRESH (${AGE_HOURS}h old)"
    exit 0
fi
