#!/bin/bash
# OpenClaw Docker Volume Backup Script
# Backs up /data/.openclaw with timestamp and compression

set -euo pipefail

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/root/openclaw-backups}"
OPENCLAW_DATA_DIR="/data/.openclaw"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="openclaw-backup-${TIMESTAMP}.tar.gz"
KEEP_DAYS="${KEEP_DAYS:-7}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $*"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} WARNING: $*"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} ERROR: $*" >&2
}

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

log "Starting OpenClaw backup..."
log "Source: $OPENCLAW_DATA_DIR"
log "Destination: $BACKUP_DIR/$BACKUP_FILE"

# Check if source directory exists
if [ ! -d "$OPENCLAW_DATA_DIR" ]; then
    error "Source directory $OPENCLAW_DATA_DIR does not exist!"
    exit 1
fi

# Create backup
log "Creating compressed archive..."
cd /data
tar czf "$BACKUP_DIR/$BACKUP_FILE" .openclaw/ 2>&1 | tee -a "$BACKUP_DIR/backup.log"

# Verify backup was created
if [ ! -f "$BACKUP_DIR/$BACKUP_FILE" ]; then
    error "Backup file was not created!"
    exit 1
fi

# Get backup size
BACKUP_SIZE=$(du -h "$BACKUP_DIR/$BACKUP_FILE" | cut -f1)
log "Backup created successfully: $BACKUP_SIZE"

# Create symlink to latest backup
cd "$BACKUP_DIR"
ln -sf "$BACKUP_FILE" openclaw-backup-latest.tar.gz
log "Symlink created: openclaw-backup-latest.tar.gz -> $BACKUP_FILE"

# Clean up old backups (keep last N days)
log "Cleaning up backups older than $KEEP_DAYS days..."
find "$BACKUP_DIR" -name "openclaw-backup-*.tar.gz" -type f -mtime +$KEEP_DAYS -delete
REMAINING=$(find "$BACKUP_DIR" -name "openclaw-backup-*.tar.gz" -type f | wc -l)
log "Remaining backups: $REMAINING"

# Test backup integrity
log "Testing backup integrity..."
if tar tzf "$BACKUP_DIR/$BACKUP_FILE" > /dev/null 2>&1; then
    log "Backup integrity verified ✓"
else
    error "Backup integrity check FAILED!"
    exit 1
fi

# Write backup manifest
MANIFEST_FILE="$BACKUP_DIR/backup-manifest.json"
cat > "$MANIFEST_FILE" <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "filename": "$BACKUP_FILE",
  "size_bytes": $(stat -c%s "$BACKUP_DIR/$BACKUP_FILE"),
  "size_human": "$BACKUP_SIZE",
  "source": "$OPENCLAW_DATA_DIR",
  "keep_days": $KEEP_DAYS,
  "total_backups": $REMAINING
}
EOF

log "Backup manifest written: $MANIFEST_FILE"
log "Backup completed successfully!"

# Display summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Backup Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "File: $BACKUP_FILE"
echo "Size: $BACKUP_SIZE"
echo "Location: $BACKUP_DIR"
echo "Backups retained: $REMAINING"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
