#!/bin/bash
# backup_rotation.sh - Rotate workspace backups
# Usage: bash tools/backup_rotation.sh [--dry-run]

set -e

BACKUP_DIR="/data/.openclaw/workspace/backups"
MAX_AGE_DAYS=30
MAX_COUNT=7
DRY_RUN=false

if [ "$1" = "--dry-run" ]; then
  DRY_RUN=true
  echo "🔍 DRY RUN MODE - No files will be deleted"
fi

echo "=== Backup Rotation Started ==="
echo "Backup directory: $BACKUP_DIR"
echo "Max age: $MAX_AGE_DAYS days"
echo "Max count: $MAX_COUNT backups"
echo ""

# Create rotation log
LOG_FILE="$BACKUP_DIR/rotation.log"
echo "[$(date -u +"%Y-%m-%d %H:%M:%S UTC")] Rotation started" >> "$LOG_FILE"

# Count current backups
CURRENT_COUNT=$(find "$BACKUP_DIR" -name "*.tar.gz" -type f 2>/dev/null | wc -l)
echo "Current backup count: $CURRENT_COUNT"

# Calculate current size
CURRENT_SIZE=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)
echo "Current backup size: $CURRENT_SIZE"
echo ""

# Step 1: Delete backups older than MAX_AGE_DAYS
echo "Step 1: Removing backups older than $MAX_AGE_DAYS days..."
OLD_FILES=$(find "$BACKUP_DIR" -name "*.tar.gz" -type f -mtime +$MAX_AGE_DAYS 2>/dev/null)
OLD_COUNT=$(echo "$OLD_FILES" | grep -c "tar.gz" || echo "0")

if [ $OLD_COUNT -gt 0 ]; then
  echo "Found $OLD_COUNT old backups to delete:"
  echo "$OLD_FILES" | while read -r file; do
    SIZE=$(du -h "$file" 2>/dev/null | cut -f1)
    AGE=$(find "$file" -printf '%TY-%Tm-%Td\n' 2>/dev/null)
    echo "  - $(basename "$file") ($SIZE, created $AGE)"
    
    if [ "$DRY_RUN" = false ]; then
      rm "$file"
      echo "    ✓ Deleted"
      echo "[$(date -u +"%Y-%m-%d %H:%M:%S UTC")] Deleted old backup: $(basename "$file") ($SIZE)" >> "$LOG_FILE"
    else
      echo "    [DRY RUN] Would delete"
    fi
  done
else
  echo "  No backups older than $MAX_AGE_DAYS days found"
fi
echo ""

# Step 2: Keep only MAX_COUNT most recent backups
echo "Step 2: Keeping only $MAX_COUNT most recent backups..."
REMAINING=$(find "$BACKUP_DIR" -name "*.tar.gz" -type f 2>/dev/null | wc -l)

if [ $REMAINING -gt $MAX_COUNT ]; then
  EXCESS=$((REMAINING - MAX_COUNT))
  echo "Found $REMAINING backups, removing $EXCESS oldest..."
  
  # Get oldest backups to delete
  OLDEST_FILES=$(ls -t "$BACKUP_DIR"/*.tar.gz 2>/dev/null | tail -n +$((MAX_COUNT + 1)))
  
  echo "$OLDEST_FILES" | while read -r file; do
    SIZE=$(du -h "$file" 2>/dev/null | cut -f1)
    AGE=$(find "$file" -printf '%TY-%Tm-%Td\n' 2>/dev/null)
    echo "  - $(basename "$file") ($SIZE, created $AGE)"
    
    if [ "$DRY_RUN" = false ]; then
      rm "$file"
      echo "    ✓ Deleted"
      echo "[$(date -u +"%Y-%m-%d %H:%M:%S UTC")] Deleted excess backup: $(basename "$file") ($SIZE)" >> "$LOG_FILE"
    else
      echo "    [DRY RUN] Would delete"
    fi
  done
else
  echo "  Only $REMAINING backups found, no excess to remove"
fi
echo ""

# Final status
echo "=== Rotation Complete ==="
FINAL_COUNT=$(find "$BACKUP_DIR" -name "*.tar.gz" -type f 2>/dev/null | wc -l)
FINAL_SIZE=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)

echo "Final backup count: $FINAL_COUNT"
echo "Final backup size: $FINAL_SIZE"
echo ""

if [ "$DRY_RUN" = false ]; then
  # Calculate savings
  SIZE_BEFORE_MB=$(du -sm "$BACKUP_DIR" 2>/dev/null | cut -f1)
  DELETED_COUNT=$((CURRENT_COUNT - FINAL_COUNT))
  
  echo "✅ Summary:"
  echo "  - Deleted $DELETED_COUNT backups"
  echo "  - Space freed: Calculated from size change"
  echo "  - Remaining backups: $FINAL_COUNT (max $MAX_COUNT)"
  echo ""
  
  echo "[$(date -u +"%Y-%m-%d %H:%M:%S UTC")] Rotation complete: $DELETED_COUNT deleted, $FINAL_COUNT remaining, $FINAL_SIZE total" >> "$LOG_FILE"
else
  echo "🔍 DRY RUN COMPLETE - Run without --dry-run to execute"
fi

# List remaining backups
echo "Remaining backups:"
ls -lh "$BACKUP_DIR"/*.tar.gz 2>/dev/null | awk '{print "  "$9, "("$5", "$6, $7, $8")"}'

exit 0
