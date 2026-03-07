#!/bin/bash
# Quick engagement check script
# Run this every 10 minutes for Moltbook monitoring

WORKSPACE="/data/.openclaw/workspace"
TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M UTC")

echo "🔍 Engagement Check - $TIMESTAMP"
echo "=========================================="

# Check if it's time for HN post
CURRENT_HOUR=$(date -u +"%H")
if [ "$CURRENT_HOUR" -ge 14 ]; then
    echo "⚠️  HN POST TIME! Check if Hacker News post is live"
fi

# Run Python monitoring script
python3 "$WORKSPACE/engagement-monitor.py"

echo ""
echo "📋 Quick Actions:"
echo "  - Check Moltbook: browser open to https://www.moltbook.com/post/e9f73a3b-270f-44d5-86e7-39c60f8a87aa"
echo "  - Check GitHub: web_fetch https://github.com/bensargotest-sys/bensargotest-sys"
echo "  - Update state: edit engagement-state.json"
echo "  - Log events: append to ENGAGEMENT-LOG.md"
echo ""
