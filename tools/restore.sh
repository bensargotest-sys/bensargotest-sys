#!/bin/bash
# OpenClaw Docker Volume Restore Script
# Restores from backup with safety checks

set -euo pipefail

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/root/openclaw-backups}"
OPENCLAW_DATA_DIR="/data/.openclaw"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $*"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} WARNING: $*"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} ERROR: $*" >&2
}

# Check arguments
if [ $# -eq 0 ]; then
    echo "Usage: $0 <backup-file|latest>"
    echo ""
    echo "Available backups:"
    ls -lh "$BACKUP_DIR"/openclaw-backup-*.tar.gz 2>/dev/null || echo "  No backups found"
    exit 1
fi

# Determine backup file
if [ "$1" == "latest" ]; then
    BACKUP_FILE="$BACKUP_DIR/openclaw-backup-latest.tar.gz"
else
    BACKUP_FILE="$1"
fi

# Verify backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    error "Backup file not found: $BACKUP_FILE"
    exit 1
fi

log "Restore from: $BACKUP_FILE"
warn "This will REPLACE all data in $OPENCLAW_DATA_DIR"

# Safety confirmation
read -p "Are you sure you want to continue? (yes/no): " -r
echo
if [[ ! $REPLY =~ ^yes$ ]]; then
    log "Restore cancelled"
    exit 0
fi

# Create safety backup of current state
if [ -d "$OPENCLAW_DATA_DIR" ]; then
    SAFETY_BACKUP="/tmp/openclaw-pre-restore-$(date +%Y%m%d-%H%M%S).tar.gz"
    log "Creating safety backup of current state..."
    tar czf "$SAFETY_BACKUP" -C /data .openclaw/
    log "Safety backup created: $SAFETY_BACKUP"
fi

# Test backup integrity before extracting
log "Testing backup integrity..."
if ! tar tzf "$BACKUP_FILE" > /dev/null 2>&1; then
    error "Backup file is corrupted!"
    exit 1
fi
log "Backup integrity verified ✓"

# Stop OpenClaw (if running as a service)
if systemctl is-active --quiet openclaw; then
    log "Stopping OpenClaw service..."
    systemctl stop openclaw
fi

# Clear current data directory
log "Removing current data..."
rm -rf "$OPENCLAW_DATA_DIR"

# Extract backup
log "Extracting backup..."
mkdir -p /data
cd /data
tar xzf "$BACKUP_FILE"

# Verify extraction
if [ ! -d "$OPENCLAW_DATA_DIR" ]; then
    error "Extraction failed! Restore safety backup manually:"
    error "  tar xzf $SAFETY_BACKUP -C /data"
    exit 1
fi

# Fix permissions
log "Fixing permissions..."
chown -R node:node "$OPENCLAW_DATA_DIR"
chmod 700 "$OPENCLAW_DATA_DIR"
chmod 600 "$OPENCLAW_DATA_DIR"/*.json 2>/dev/null || true

# Restart OpenClaw (if it was running)
if systemctl list-unit-files | grep -q openclaw.service; then
    log "Starting OpenClaw service..."
    systemctl start openclaw
fi

log "Restore completed successfully!"
log "Safety backup retained at: $SAFETY_BACKUP"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Restore Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Restored from: $(basename $BACKUP_FILE)"
echo "Restored to: $OPENCLAW_DATA_DIR"
echo "Safety backup: $SAFETY_BACKUP"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
