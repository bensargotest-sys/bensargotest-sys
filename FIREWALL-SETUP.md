# Hostinger VPS Firewall Setup

**VPS IP:** 76.13.46.217  
**Goal:** Block all inbound traffic except SSH and HTTPS, specifically blocking exposed OpenClaw ports

## Critical Ports to Block

These are currently listening on 0.0.0.0 (all interfaces) and must be firewalled:

- **59415** - Unknown service (detected via /proc/net/tcp)
- **63362** - OpenClaw Control UI (should only be accessed via SSH tunnel or Tailscale)

## Required Firewall Rules

### Allow (Inbound)
1. **SSH (22)** - For remote access
   - Optional: Restrict to your IP address for extra security
   - Current IP (for reference): Check your local IP via `curl ifconfig.me`

2. **HTTPS (443)** - For future reverse proxy (when configured)
   - Can be added later when reverse proxy is set up
   - Not needed immediately

### Block (Inbound)
1. **Port 59415** - Explicitly block
2. **Port 63362** - Explicitly block
3. **All other ports** - Default deny

## Hostinger Panel Instructions

### Method 1: Hostinger Firewall (Recommended)

1. Log into Hostinger hPanel: https://hpanel.hostinger.com
2. Go to **VPS → [Your VPS] → Firewall** (or Security section)
3. Create firewall rules:

   **Rule 1: Allow SSH**
   - Protocol: TCP
   - Port: 22
   - Source: 0.0.0.0/0 (or your specific IP for added security)
   - Action: ACCEPT

   **Rule 2: Block OpenClaw ports**
   - Protocol: TCP
   - Ports: 59415, 63362
   - Source: 0.0.0.0/0
   - Action: DROP

   **Rule 3: Default Policy**
   - Default inbound: DROP
   - Default outbound: ACCEPT

4. Apply rules
5. Test SSH still works: `ssh root@76.13.46.217`

### Method 2: UFW (If Hostinger panel doesn't have firewall)

If the Hostinger panel doesn't provide a firewall interface, configure UFW on the VPS:

```bash
# SSH into VPS
ssh root@76.13.46.217

# Install UFW if not present
apt update && apt install -y ufw

# Set defaults
ufw default deny incoming
ufw default allow outgoing

# Allow SSH (CRITICAL - do this first or you'll lock yourself out)
ufw allow 22/tcp

# Block OpenClaw ports explicitly
ufw deny 59415/tcp
ufw deny 63362/tcp

# Enable firewall
ufw enable

# Check status
ufw status verbose
```

### Method 3: iptables (Advanced)

If neither UFW nor Hostinger firewall is available:

```bash
# SSH into VPS
ssh root@76.13.46.217

# Allow SSH
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Allow established connections
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Block OpenClaw ports
iptables -A INPUT -p tcp --dport 59415 -j DROP
iptables -A INPUT -p tcp --dport 63362 -j DROP

# Default deny
iptables -P INPUT DROP

# Save rules (Ubuntu/Debian)
apt install -y iptables-persistent
netfilter-persistent save
```

## Verification

After applying firewall rules, test from your local machine:

```bash
# These should timeout/refuse (good):
telnet 76.13.46.217 59415
telnet 76.13.46.217 63362

# SSH should still work (critical):
ssh root@76.13.46.217

# Telegram should still work (uses outbound connections, not affected)
```

## Access Patterns After Firewall

- **Telegram:** ✅ Works (outbound connections from VPS to Telegram servers)
- **Control UI:** Via SSH tunnel only (see below)
- **Future HTTPS:** Via Tailscale or reverse proxy on port 443

## SSH Tunnel for Control UI Access

When you need the web interface:

```bash
# From your local machine
ssh -L 8080:localhost:63362 root@76.13.46.217

# Then open in browser:
http://localhost:8080
```

The tunnel encrypts all traffic through SSH, making it safe.

## Security Checklist

- [ ] Firewall rules applied (verify via Hostinger panel or `ufw status`)
- [ ] SSH still works from your machine
- [ ] Ports 59415 and 63362 blocked (verified via telnet timeout)
- [ ] Telegram connection still works
- [ ] SSH tunnel tested for Control UI access

## Next Steps After Firewall

1. Set up automated backups (task-002)
2. Configure Tailscale for secure HTTPS access (task-005)
3. Build memory and recovery system (Phase 2)

---

**Status:** Waiting on human to apply firewall rules  
**Created:** 2026-02-09  
**Last Updated:** 2026-02-09
