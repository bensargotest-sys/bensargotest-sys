#!/bin/bash
# Auto-recovery: detect work gaps and log alerts
# Run via cron or heartbeat to catch gaps early

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE="$(dirname "$SCRIPT_DIR")"

# Run gap detector (2h threshold)
RESULT=$(python3 "$SCRIPT_DIR/gap_detector.py" 2 2>&1) || true
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "OK: No work gaps detected"
    exit 0
fi

# Gap detected — log it as a mistake
echo "⚠️ Work gap detected:"
echo "$RESULT"

# Log to mistakes if mistake_logger exists
if [ -f "$SCRIPT_DIR/mistake_logger.py" ]; then
    GAP_COUNT=$(echo "$RESULT" | head -1 | grep -oP '\d+' | head -1)
    python3 "$SCRIPT_DIR/mistake_logger.py" log "Work gap detected: ${GAP_COUNT:-unknown} gaps >2h in last 24h" 2>/dev/null || true
fi

exit 1
