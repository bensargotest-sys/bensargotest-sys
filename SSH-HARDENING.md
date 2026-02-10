# SSH Hardening Guide

**Status:** Optional enhancement (current setup is already secure with firewall)  
**Time Required:** 15-20 minutes  
**Risk Level:** Low (reversible if issues occur)

---

## Current State

✅ **Already Secure:**
- Firewall active (Hostinger + UFW)
- Port 22 open (SSH only)
- Strong password required
- No unauthorized access detected

⚠️ **Can Be Improved:**
- Password authentication (keys are more secure)
- Root login enabled (unnecessary)
- Default SSH port 22 (predictable)

---

## Hardening Steps (In Order)

### Step 1: Generate SSH Key Pair (On Your Local Machine)

**Mac/Linux:**
```bash
# Generate key (do this on YOUR computer, not the VPS)
ssh-keygen -t ed25519 -C "your_email@example.com" -f ~/.ssh/hostinger_vps

# Press Enter for no passphrase, or set one for extra security
```

**Windows (PowerShell):**
```powershell
# Generate key
ssh-keygen -t ed25519 -C "your_email@example.com" -f $HOME\.ssh\hostinger_vps
```

This creates:
- `~/.ssh/hostinger_vps` (private key - keep secret!)
- `~/.ssh/hostinger_vps.pub` (public key - safe to share)

---

### Step 2: Copy Public Key to VPS

**Method 1: Using ssh-copy-id (Mac/Linux):**
```bash
ssh-copy-id -i ~/.ssh/hostinger_vps.pub root@76.13.46.217
```

**Method 2: Manual (All Platforms):**
```bash
# On your local machine, print the public key:
cat ~/.ssh/hostinger_vps.pub

# Then SSH into your VPS and run:
mkdir -p ~/.ssh
chmod 700 ~/.ssh
nano ~/.ssh/authorized_keys
# Paste the public key, save (Ctrl+O, Enter, Ctrl+X)
chmod 600 ~/.ssh/authorized_keys
```

---

### Step 3: Test Key-Based Login

**Before disabling password auth, verify keys work!**

```bash
# From your local machine:
ssh -i ~/.ssh/hostinger_vps root@76.13.46.217

# Should log in WITHOUT asking for password
```

If this works, you're good. If not, **DO NOT CONTINUE** - fix the keys first.

---

### Step 4: Disable Password Authentication

```bash
# On the VPS:
nano /etc/ssh/sshd_config
```

**Find and change these lines:**
```
PasswordAuthentication no
PubkeyAuthentication yes
ChallengeResponseAuthentication no
```

**Save and restart SSH:**
```bash
systemctl restart sshd
```

**Test again from local machine:**
```bash
ssh -i ~/.ssh/hostinger_vps root@76.13.46.217
```

---

### Step 5: Disable Root Login (Optional, Advanced)

**Why:** Even safer - create a regular user, disable root entirely.

```bash
# Create a new user with sudo
adduser yourname
usermod -aG sudo yourname

# Copy SSH keys to new user
mkdir -p /home/yourname/.ssh
cp ~/.ssh/authorized_keys /home/yourname/.ssh/
chown -R yourname:yourname /home/yourname/.ssh
chmod 700 /home/yourname/.ssh
chmod 600 /home/yourname/.ssh/authorized_keys

# Test login as new user (from local machine):
ssh -i ~/.ssh/hostinger_vps yourname@76.13.46.217

# If it works, disable root login:
nano /etc/ssh/sshd_config
# Change: PermitRootLogin no
systemctl restart sshd
```

---

### Step 6: Change SSH Port (Optional)

**Why:** Reduces automated bot attacks on port 22.

```bash
# Pick a random high port (e.g., 2849)
nano /etc/ssh/sshd_config
# Change: Port 2849

# Update firewall FIRST (critical!):
ufw allow 2849/tcp
ufw status

# Restart SSH:
systemctl restart sshd

# Update Hostinger firewall (hPanel):
# Add rule: TCP port 2849
# Remove rule: TCP port 22 (after verifying new port works!)

# Test from local machine:
ssh -i ~/.ssh/hostinger_vps -p 2849 root@76.13.46.217
```

⚠️ **WARNING:** If you change the port, update your SSH command everywhere (including in scripts)!

---

## Rollback Plan

If you get locked out:

1. **Hostinger Control Panel → VPS → Console**
   - Web-based terminal (always works)
   - Reverse the changes in `/etc/ssh/sshd_config`

2. **Restore original config:**
   ```bash
   # In the web console:
   nano /etc/ssh/sshd_config
   # Set back to:
   # PasswordAuthentication yes
   # PermitRootLogin yes
   # Port 22
   systemctl restart sshd
   ```

---

## Verification Checklist

After hardening:

- [ ] Can log in with SSH key (no password prompt)
- [ ] Firewall allows SSH port
- [ ] Docker containers still running (`docker ps`)
- [ ] OpenClaw gateway responding (send Telegram message)
- [ ] Backup exists before making changes

---

## Summary of Benefits

| Before | After (Full Hardening) |
|--------|------------------------|
| Password login | Key-only (no brute force possible) |
| Root login enabled | Regular user + sudo (principle of least privilege) |
| Port 22 (predictable) | Custom port (less bot noise) |
| Manual audits | Automated daily checks (already done!) |

**Recommended Order:**
1. ✅ SSH keys (reversible, low risk)
2. ✅ Disable password auth (after testing keys)
3. ⚠️ Disable root login (optional, test thoroughly)
4. ⚠️ Change SSH port (optional, remember to update everywhere)

---

**Current Status:** Phase 1 (keys + password disable) is sufficient for most users. Steps 5-6 are optional hardening for maximum security.
