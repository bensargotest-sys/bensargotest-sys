#!/bin/bash
# Auto-archive bloated sessions
# Created: 2026-02-14
# Purpose: Prevent session bloat, maintain performance

THRESHOLD_MB=2
ALERT_MB=5
ARCHIVE_DIR="/data/.openclaw/workspace/checkpoints/auto-archive"
WORK_LOG="/data/.openclaw/workspace/memory/work-log.md"

mkdir -p "$ARCHIVE_DIR"

# Find current main session
SESSION_FILE=$(ls -t /data/.openclaw/agents/main/sessions/*.jsonl 2>/dev/null | head -1)

if [ -z "$SESSION_FILE" ]; then
  echo "[$(date -u +"%Y-%m-%d %H:%M:%S UTC")] No active session found" >> "$WORK_LOG"
  exit 0
fi

# Check size
SIZE_MB=$(du -m "$SESSION_FILE" | cut -f1)

echo "[$(date -u +"%Y-%m-%d %H:%M:%S UTC")] Session size check: ${SIZE_MB}MB" >> "$WORK_LOG"

if [ "$SIZE_MB" -gt "$ALERT_MB" ]; then
  echo "🚨 SESSION CRITICAL: ${SIZE_MB}MB (threshold: ${ALERT_MB}MB)" >> "$WORK_LOG"
  echo "Running emergency checkpoint..." >> "$WORK_LOG"
  cd /data/.openclaw/workspace
  python3 tools/checkpoint.py --auto --note "Emergency archive (${SIZE_MB}MB)" >> "$WORK_LOG" 2>&1
  echo "Emergency checkpoint complete" >> "$WORK_LOG"
elif [ "$SIZE_MB" -gt "$THRESHOLD_MB" ]; then
  echo "⚠️ Session ${SIZE_MB}MB - archiving (threshold: ${THRESHOLD_MB}MB)" >> "$WORK_LOG"
  cd /data/.openclaw/workspace
  python3 tools/checkpoint.py --auto --note "Auto-archive (${SIZE_MB}MB)" >> "$WORK_LOG" 2>&1
  echo "Auto-archive complete" >> "$WORK_LOG"
else
  echo "✅ Session healthy: ${SIZE_MB}MB (threshold: ${THRESHOLD_MB}MB)" >> "$WORK_LOG"
fi
