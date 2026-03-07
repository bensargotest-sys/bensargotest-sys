#!/bin/bash
# bloat_health_check.sh - Weekly workspace bloat health monitoring
# Usage: bash tools/bloat_health_check.sh [--verbose]

set -e

WORKSPACE="/data/.openclaw/workspace"
VERBOSE=false
ALERT_BACKUP_GB=5
ALERT_WORKSPACE_GB=20
ALERT_MEMORY_FILE_KB=100

if [ "$1" = "--verbose" ]; then
  VERBOSE=true
fi

echo "=== Workspace Bloat Health Check ==="
echo "Date: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
echo "Workspace: $WORKSPACE"
echo ""

# Total workspace size
TOTAL_SIZE=$(du -sh "$WORKSPACE" 2>/dev/null | cut -f1)
TOTAL_MB=$(du -sm "$WORKSPACE" 2>/dev/null | cut -f1)
echo "📊 Total workspace size: $TOTAL_SIZE"
echo ""

# Top 10 directories
echo "📁 Top 10 largest directories:"
du -sh "$WORKSPACE"/* 2>/dev/null | sort -hr | head -10 | while read -r size dir; do
  echo "  $size  $(basename "$dir")"
done
echo ""

# Backup status
echo "💾 Backup status:"
BACKUP_DIR="$WORKSPACE/backups"
if [ -d "$BACKUP_DIR" ]; then
  BACKUP_COUNT=$(find "$BACKUP_DIR" -name "*.tar.gz" -type f 2>/dev/null | wc -l)
  BACKUP_SIZE=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)
  BACKUP_MB=$(du -sm "$BACKUP_DIR" 2>/dev/null | cut -f1)
  echo "  Count: $BACKUP_COUNT backups"
  echo "  Size: $BACKUP_SIZE"
  
  if [ "$VERBOSE" = true ]; then
    echo "  Files:"
    ls -lh "$BACKUP_DIR"/*.tar.gz 2>/dev/null | awk '{print "    "$9, "("$5", "$6, $7, $8")"}'
  fi
else
  echo "  Backup directory not found"
fi
echo ""

# Memory file sizes
echo "📝 Memory file sizes:"
if [ -d "$WORKSPACE/memory" ]; then
  ls -lh "$WORKSPACE/memory"/*.md 2>/dev/null | awk '{
    size=$5
    file=$9
    # Convert size to KB for comparison
    if (size ~ /K/) {
      kb=int(size)
    } else if (size ~ /M/) {
      kb=int(size) * 1024
    } else {
      kb=0
    }
    printf "  %5s  %s", size, file
    if (kb > 100) {
      printf "  ⚠️ >100KB"
    }
    printf "\n"
  }' | sort -rh | head -10
else
  echo "  Memory directory not found"
fi
echo ""

# Files by directory
echo "📊 File counts by directory:"
for dir in "$WORKSPACE"/*/; do 
  if [ -d "$dir" ]; then
    COUNT=$(find "$dir" -type f 2>/dev/null | wc -l)
    echo "$COUNT $(basename "$dir")"
  fi
done | sort -rn | head -10 | while read -r count name; do
  printf "  %7s files  %s\n" "$count" "$name"
done
echo ""

# Node_modules monitoring
echo "📦 node_modules sizes:"
NODE_TOTAL=0
if find "$WORKSPACE" -type d -name "node_modules" 2>/dev/null | grep -q .; then
  find "$WORKSPACE" -type d -name "node_modules" 2>/dev/null | while read -r nm_dir; do
    SIZE=$(du -sh "$nm_dir" 2>/dev/null | cut -f1)
    SIZE_MB=$(du -sm "$nm_dir" 2>/dev/null | cut -f1)
    REL_PATH=$(echo "$nm_dir" | sed "s|$WORKSPACE/||")
    echo "  $SIZE  $REL_PATH"
    NODE_TOTAL=$((NODE_TOTAL + SIZE_MB))
  done
else
  echo "  No node_modules directories found"
fi
echo ""

# Alerts
echo "🚨 Health Alerts:"
ALERTS=0

# Check backup size
if [ -d "$BACKUP_DIR" ] && [ $BACKUP_MB -gt $((ALERT_BACKUP_GB * 1024)) ]; then
  echo "  ⚠️  Backup directory exceeds ${ALERT_BACKUP_GB}GB (${BACKUP_SIZE})"
  echo "      Action: Run 'bash tools/backup_rotation.sh' to clean old backups"
  ALERTS=$((ALERTS + 1))
fi

# Check workspace size
if [ $TOTAL_MB -gt $((ALERT_WORKSPACE_GB * 1024)) ]; then
  echo "  ⚠️  Workspace exceeds ${ALERT_WORKSPACE_GB}GB (${TOTAL_SIZE})"
  echo "      Action: Review large directories, consider archiving unused projects"
  ALERTS=$((ALERTS + 1))
fi

# Check for large memory files
if [ -d "$WORKSPACE/memory" ]; then
  LARGE_FILES=$(find "$WORKSPACE/memory" -name "*.md" -size +100k 2>/dev/null)
  if [ -n "$LARGE_FILES" ]; then
    echo "  ⚠️  Memory files exceeding 100KB found:"
    echo "$LARGE_FILES" | while read -r file; do
      SIZE=$(du -h "$file" 2>/dev/null | cut -f1)
      echo "      $SIZE  $(basename "$file")"
    done
    echo "      Action: Run 'python3 tools/memory_consolidate.py' or rotate logs"
    ALERTS=$((ALERTS + 1))
  fi
fi

# Check for abandoned project directories
ABANDONED_DIRS="tsp tsp-integration tsp-fresh trustlayer"
for dir in $ABANDONED_DIRS; do
  if [ -d "$WORKSPACE/$dir" ]; then
    SIZE=$(du -sh "$WORKSPACE/$dir" 2>/dev/null | cut -f1)
    echo "  ⚠️  Abandoned project still in workspace: $dir ($SIZE)"
    echo "      Action: Move to archive/ and document reason"
    ALERTS=$((ALERTS + 1))
  fi
done

# Check archive size
if [ -d "$WORKSPACE/archive" ]; then
  ARCHIVE_SIZE=$(du -sh "$WORKSPACE/archive" 2>/dev/null | cut -f1)
  ARCHIVE_MB=$(du -sm "$WORKSPACE/archive" 2>/dev/null | cut -f1)
  ARCHIVE_AGE_DAYS=90
  
  OLD_ARCHIVES=$(find "$WORKSPACE/archive" -mindepth 1 -maxdepth 1 -type d -mtime +$ARCHIVE_AGE_DAYS 2>/dev/null)
  if [ -n "$OLD_ARCHIVES" ]; then
    echo "  ⚠️  Archives older than $ARCHIVE_AGE_DAYS days found:"
    echo "$OLD_ARCHIVES" | while read -r dir; do
      SIZE=$(du -sh "$dir" 2>/dev/null | cut -f1)
      AGE=$(find "$dir" -printf '%TY-%Tm-%Td\n' 2>/dev/null | head -1)
      echo "      $SIZE  $(basename "$dir") (created $AGE)"
    done
    echo "      Action: Review for permanent deletion if no revival interest"
    ALERTS=$((ALERTS + 1))
  fi
fi

if [ $ALERTS -eq 0 ]; then
  echo "  ✅ No alerts - workspace health is good"
fi
echo ""

# Summary
echo "=== Summary ==="
echo "Total size: $TOTAL_SIZE"
echo "Total files: $(find "$WORKSPACE" -type f 2>/dev/null | wc -l)"
echo "Alerts: $ALERTS"
echo ""

# Log to file
LOG_FILE="$WORKSPACE/memory/bloat-health.log"
echo "[$(date -u +"%Y-%m-%d %H:%M:%S UTC")] Health check complete: $TOTAL_SIZE workspace, $ALERTS alerts" >> "$LOG_FILE"

if [ $ALERTS -gt 0 ]; then
  echo "⚠️  Action required - $ALERTS alerts found"
  exit 1
else
  echo "✅ Health check complete - workspace is healthy"
  exit 0
fi
