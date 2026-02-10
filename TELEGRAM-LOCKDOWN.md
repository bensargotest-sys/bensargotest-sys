# Telegram-Only Lockdown Guide

**Goal:** Maximum security for Telegram-only usage  
**Risk Level After Lockdown:** LOW

## ✅ Already Done (From Container)

1. **API keys secured** - File permissions 600
2. **Insecure HTTP auth disabled** - No token-only HTTP
3. **All other channels disabled** - Only Telegram enabled
4. **Control UI internal** - Already binds to 127.0.0.1

## 🔴 Critical: Host-Level Firewall (YOU MUST DO THIS)

The following ports are currently accessible from the internet. They MUST be blocked:

**Port 59415** - Unknown service (detected on 0.0.0.0)  
**Port 63362** - OpenClaw Control UI

### Method 1: Hostinger Panel (If Available)

1. Login: https://hpanel.hostinger.com
2. VPS → Firewall
3. **Create these rules (ORDER MATTERS):**

   ```
   Rule 1: ALLOW SSH (port 22) from 0.0.0.0/0
   Rule 2: DENY port 59415 from 0.0.0.0/0
   Rule 3: DENY port 63362 from 0.0.0.0/0
   Default: DENY all other inbound
   ```

4. Apply and test

### Method 2: UFW (If No Panel Firewall)

```bash
# SSH to VPS
ssh root@76.13.46.217

# Install UFW
apt update && apt install -y ufw

# CRITICAL: Allow SSH FIRST or you'll lock yourself out
ufw allow 22/tcp

# Block exposed OpenClaw ports
ufw deny 59415/tcp
ufw deny 63362/tcp

# Set defaults
ufw default deny incoming
ufw default allow outgoing

# Enable firewall
ufw --force enable

# Verify
ufw status verbose
```

Expected output:
```
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), disabled (routed)

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW IN    Anywhere
59415/tcp                  DENY IN     Anywhere
63362/tcp                  DENY IN     Anywhere
```

## ✅ After Firewall Applied

### What Works:
- ✅ **Telegram** - Uses outbound connections, not affected by firewall
- ✅ **SSH** - Port 22 allowed for your access
- ✅ **Control UI** - Via SSH tunnel only (when needed)

### What's Blocked:
- ❌ **Direct web access** to Control UI
- ❌ **All other inbound connections**

## Verification Tests

### From Your Local Machine:

```bash
# These should TIMEOUT (good):
telnet 76.13.46.217 59415
telnet 76.13.46.217 63362

# SSH should still work (CRITICAL):
ssh root@76.13.46.217

# Telegram should still work:
# Just message your bot
```

### From Inside VPS:

```bash
# Check firewall status
sudo ufw status verbose

# Check listening ports
ss -ltn | grep -E "59415|63362"
```

## Accessing Control UI After Lockdown

When you need the web interface, use SSH tunnel:

```bash
# From your local machine
ssh -L 8080:localhost:63362 root@76.13.46.217

# Keep that terminal open, then visit:
# http://localhost:8080
```

Traffic goes through encrypted SSH - completely safe.

## 🔴 CRITICAL: First Backup

Before making firewall changes, take a backup:

```bash
# SSH to VPS
ssh root@76.13.46.217

# Create backup directory
mkdir -p /root/openclaw-backups

# Backup OpenClaw data
docker exec openclaw tar czf - /data/.openclaw > /root/openclaw-backups/openclaw-backup-$(date +%Y%m%d-%H%M%S).tar.gz

# Verify it exists
ls -lh /root/openclaw-backups/
```

## Security Checklist

- [ ] First backup taken (above)
- [ ] Firewall rules applied (UFW or Hostinger panel)
- [ ] SSH still works (test before proceeding)
- [ ] Ports 59415, 63362 blocked (verified via telnet timeout)
- [ ] Telegram still works (send test message)
- [ ] Control UI accessible via SSH tunnel (test if needed)

## Risk Assessment

### Before Lockdown:
- Risk: **MEDIUM-HIGH**
- Exposed ports: 2+
- Backup: None
- Channels: All enabled

### After Lockdown:
- Risk: **LOW**
- Exposed ports: 1 (SSH only, required)
- Backup: Configured
- Channels: Telegram only

## Next Security Steps (After Firewall)

1. **Schedule daily backups** (cron job)
2. **SSH hardening:**
   - Disable password auth (key-only)
   - Change SSH port from 22
   - Disable root login
3. **Daily security audit** (automated)
4. **Update monitoring**

## Emergency Recovery

If you lock yourself out:

1. **Hostinger Console:** Use hPanel web console to access VPS
2. **Disable firewall:** `sudo ufw disable`
3. **Re-apply rules carefully**

---

**Status:** Waiting on firewall configuration  
**Priority:** CRITICAL - Do this before anything else  
**Estimated Time:** 5 minutes

**After firewall is applied, message me and I'll verify the lockdown.**
