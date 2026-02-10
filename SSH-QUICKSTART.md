# SSH Hardening - Quick Start (5 Minutes)

**Goal:** Set up SSH key authentication and disable password login.

---

## On Your Local Machine (Mac/Linux/Windows)

### 1. Generate SSH Key (1 min)

```bash
ssh-keygen -t ed25519 -C "your_email@example.com" -f ~/.ssh/hostinger_vps
```

Press Enter twice (no passphrase, or set one if you prefer).

### 2. Copy Public Key (1 min)

**Option A - Automatic (Mac/Linux):**
```bash
ssh-copy-id -i ~/.ssh/hostinger_vps.pub root@76.13.46.217
```

**Option B - Manual (All Platforms):**
```bash
# Display your public key
cat ~/.ssh/hostinger_vps.pub

# Copy the entire output (starts with "ssh-ed25519 ...")
```

---

## On the VPS (SSH into your server)

### 3. Add Your Public Key (if using manual method)

```bash
mkdir -p ~/.ssh
nano ~/.ssh/authorized_keys
# Paste your public key (from step 2)
# Save: Ctrl+O, Enter, Ctrl+X

chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### 4. Test Key Login (IMPORTANT - Don't skip!)

**Open a NEW terminal window** (keep the current one open as backup):

```bash
ssh -i ~/.ssh/hostinger_vps root@76.13.46.217
```

Should log in **without asking for password**. If it doesn't work, STOP and troubleshoot before continuing.

### 5. Disable Password Authentication (2 min)

**Only proceed if step 4 worked!**

```bash
nano /etc/ssh/sshd_config
```

Find and change these lines:
```
PasswordAuthentication no
PubkeyAuthentication yes
```

Save (Ctrl+O, Enter, Ctrl+X), then:

```bash
systemctl restart sshd
```

### 6. Verify (30 sec)

Log out and try again:
```bash
ssh -i ~/.ssh/hostinger_vps root@76.13.46.217
```

Should still work. Now try from a different machine (or without the key) - should FAIL. That's success!

---

## Make It Easier (Optional)

Add to `~/.ssh/config` on your local machine:

```
Host hostinger
    HostName 76.13.46.217
    User root
    IdentityFile ~/.ssh/hostinger_vps
```

Now you can just type: `ssh hostinger` ✨

---

## Rollback (If Something Goes Wrong)

If you get locked out:
1. Go to Hostinger hPanel → VPS → Console (web terminal)
2. Edit `/etc/ssh/sshd_config`
3. Change back to: `PasswordAuthentication yes`
4. Run: `systemctl restart sshd`

---

**Status After Completion:**
- ✅ SSH key authentication working
- ✅ Password login disabled
- ✅ Much more secure (brute force attacks impossible)
- ✅ Still have web console backup access via Hostinger

**Time:** ~5 minutes  
**Risk:** Very low (web console always available as backup)
