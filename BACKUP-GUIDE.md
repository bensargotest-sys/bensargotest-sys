# OpenClaw Backup & Recovery Guide

**Created:** 2026-02-09  
**VPS:** 76.13.46.217 (Hostinger)

## Overview

This guide covers automated backups for your OpenClaw VPS deployment. Backups protect against:
- Accidental deletion
- Configuration errors
- System failures
- Data corruption

## What Gets Backed Up

**Everything in `/data/.openclaw`:**
- Configuration files (`openclaw.json`)
- API keys and credentials (`auth-profiles.json`)
- Telegram session data
- Memory files and daily logs
- Workspace files
- Session history
- All agent state

## Backup Scripts

Two scripts handle backup/restore:

- **`tools/backup.sh`** - Creates compressed backups with timestamp
- **`tools/restore.sh`** - Restores from backup with safety checks

Both are in your workspace: `/data/.openclaw/workspace/tools/`

## Manual Backup (Run Now)

### From Inside Docker Container

```bash
# Make scripts executable
chmod +x /data/.openclaw/workspace/tools/backup.sh
chmod +x /data/.openclaw/workspace/tools/restore.sh

# Run backup (output goes to container, need host access for persistence)
bash /data/.openclaw/workspace/tools/backup.sh
```

**⚠️ Container backups are ephemeral!** They disappear if the container is removed.

### From VPS Host (Recommended)

This is the **proper way** - backups persist on the host.

```bash
# SSH into VPS
ssh root@76.13.46.217

# Backup entire OpenClaw Docker volume
mkdir -p /root/openclaw-backups
docker exec openclaw tar czf - /data/.openclaw > /root/openclaw-backups/openclaw-backup-$(date +%Y%m%d-%H%M%S).tar.gz

# Verify backup exists
ls -lh /root/openclaw-backups/
```

## Automated Daily Backups

### Method 1: Host-Level Cron (Recommended)

Run backups from the VPS host so they persist:

```bash
# SSH into VPS
ssh root@76.13.46.217

# Edit root crontab
crontab -e

# Add this line (runs daily at 2 AM):
0 2 * * * docker exec openclaw tar czf - /data/.openclaw > /root/openclaw-backups/openclaw-backup-$(date +\%Y\%m\%d).tar.gz 2>&1 | tee -a /root/openclaw-backups/backup.log
```

### Method 2: OpenClaw Cron Job

You can schedule backups using OpenClaw's cron system, but output stays in container unless you copy it to host.

```bash
# From Telegram or Control UI:
/cron add --name "daily-backup" --schedule "0 2 * * *" --task "Run daily backup"
```

**Note:** Still need to copy backups to host for true persistence.

## Backup Retention

Default: Keep 7 days of backups

To change retention period:
```bash
export KEEP_DAYS=14
bash /data/.openclaw/workspace/tools/backup.sh
```

## Testing Backups

**Test your backups now** before you need them:

```bash
# List available backups
ls -lh /root/openclaw-backups/

# Test integrity of latest backup
tar tzf /root/openclaw-backups/openclaw-backup-latest.tar.gz

# Dry-run restore (extract to /tmp)
mkdir /tmp/restore-test
tar xzf /root/openclaw-backups/openclaw-backup-latest.tar.gz -C /tmp/restore-test
ls -la /tmp/restore-test/data/.openclaw/
```

## Recovery Procedures

### Full Restore from Backup

⚠️ **This will replace all current data!**

```bash
# SSH into VPS
ssh root@76.13.46.217

# Stop OpenClaw container
docker stop openclaw

# Restore from backup
docker exec openclaw tar xzf /root/openclaw-backups/openclaw-backup-latest.tar.gz -C /

# Or restore specific backup
docker exec openclaw tar xzf /root/openclaw-backups/openclaw-backup-20260209-020000.tar.gz -C /

# Restart container
docker start openclaw
```

### Partial File Recovery

Recover specific files without full restore:

```bash
# Extract single file
tar xzf backup.tar.gz -C /tmp data/.openclaw/openclaw.json

# Copy to container
docker cp /tmp/data/.openclaw/openclaw.json openclaw:/data/.openclaw/
```

### Disaster Recovery (New VPS)

If you need to migrate to a new VPS:

1. Copy backup from old VPS:
   ```bash
   scp root@76.13.46.217:/root/openclaw-backups/openclaw-backup-latest.tar.gz ./
   ```

2. Set up OpenClaw on new VPS (follow Hostinger Docker setup)

3. Restore backup:
   ```bash
   scp openclaw-backup-latest.tar.gz root@NEW_VPS_IP:/root/
   ssh root@NEW_VPS_IP
   docker exec openclaw tar xzf /root/openclaw-backup-latest.tar.gz -C /
   docker restart openclaw
   ```

4. Update Telegram webhook/bot settings if needed

## Off-Site Backups (Recommended)

For true disaster recovery, copy backups off the VPS:

### Method 1: Download to Local Machine

```bash
# Run daily from your local machine
scp root@76.13.46.217:/root/openclaw-backups/openclaw-backup-latest.tar.gz ~/openclaw-backups/$(date +%Y%m%d).tar.gz
```

### Method 2: Sync to Cloud Storage

```bash
# Install rclone on VPS
curl https://rclone.org/install.sh | sudo bash

# Configure cloud provider (e.g., Dropbox, Google Drive, S3)
rclone config

# Sync backups to cloud daily
rclone sync /root/openclaw-backups remote:openclaw-backups
```

### Method 3: Hostinger Backups

Check if Hostinger provides automatic VPS snapshots:
- hPanel → VPS → Backups
- May need to enable or upgrade plan

## Backup Checklist

- [ ] Backup scripts created and tested
- [ ] Daily cron job configured on VPS host
- [ ] Test restore performed successfully
- [ ] Off-site backup method configured
- [ ] Backup monitoring added to heartbeat checks
- [ ] Recovery procedures documented and tested

## Monitoring Backup Health

Add to heartbeat checks:

```bash
# Check last backup age
LAST_BACKUP=$(ls -t /root/openclaw-backups/openclaw-backup-*.tar.gz | head -1)
BACKUP_AGE=$(($(date +%s) - $(stat -c %Y "$LAST_BACKUP")))

if [ $BACKUP_AGE -gt 86400 ]; then
    echo "⚠️ Last backup is older than 24 hours!"
fi
```

## Common Issues

### "No space left on device"

Backups consume disk space. Monitor with:
```bash
df -h
du -sh /root/openclaw-backups/
```

Clean up old backups:
```bash
find /root/openclaw-backups/ -name "openclaw-backup-*.tar.gz" -mtime +7 -delete
```

### "Permission denied"

Ensure scripts are executable:
```bash
chmod +x /data/.openclaw/workspace/tools/*.sh
```

### Backup size growing too large

Exclude logs or temporary data if needed:
```bash
tar czf backup.tar.gz --exclude='*/logs/*' --exclude='*/temp/*' /data/.openclaw/
```

## Next Steps

1. **Immediate:** Run your first manual backup from VPS host
2. **Today:** Set up daily cron job
3. **This week:** Configure off-site backup sync
4. **Monthly:** Test restore procedure

---

**Status:** Ready to implement  
**Priority:** Critical (no backups currently)  
**Dependencies:** None (can start immediately)
