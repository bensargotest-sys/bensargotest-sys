# Security Enhancements from Clawdbot Guide

**Source:** Comprehensive setup guide PDF (received 2026-02-09)  
**Current Status:** Good baseline, but missing several hardening options  
**Priority:** Apply recommended sandbox and security settings

---

## What We Already Have ✅

**From Our Implementation:**
- ✅ gateway.mode: "local" (localhost-bound)
- ✅ gateway.controlUi.allowInsecureAuth: false (secure auth required)
- ✅ session.dmScope: "per-channel-peer" (session isolation)
- ✅ Telegram-only access (all other channels disabled)
- ✅ Firewall active (UFW + Hostinger)
- ✅ File permissions secured (700/600)
- ✅ Daily security audits (automated)

**Security Audit Result:** 0 critical, 1 warning (trusted proxies - not relevant), 1 info

---

## Critical Warnings from PDF

### 🔴 DANGEROUS COMMANDS (Never Use)

**AVOID THESE COMMANDS:**
```bash
openclaw doctor --fix         # ❌ DANGEROUS - Writes secrets to plaintext
openclaw configure            # ❌ DANGEROUS - Writes secrets to plaintext
```

**Why dangerous:**
- Expands ${VAR} environment variables to plaintext
- Writes actual secrets to `~/.openclaw/openclaw.json`
- Creates permanent readable secrets that might sync to Git/cloud

**Safe alternatives:**
```bash
openclaw security audit       # ✅ SAFE - Read-only check
openclaw security audit --deep # ✅ SAFE - Deep read-only check
openclaw status --all         # ✅ SAFE - Read-only status
openclaw doctor --validate    # ✅ SAFE - Read-only health check
```

**If you accidentally ran doctor --fix:**
1. Stop all processes: `systemctl --user stop openclaw*`
2. Check git: `git status` (don't commit!)
3. Restore config from backup
4. Rotate ALL secrets (Telegram token, API keys)
5. Run `openclaw security audit --deep`
6. Restart safely

---

## CVE Warnings (From PDF)

**Known vulnerabilities (patched in current versions):**
- **CVE-2026-25253** (CVSS 8.8, RCE): Unauthenticated command execution
- **CVE-2026-25157** (CVSS 7.5, High): SSH injection via channel integration
- **CVE-2026-25475** (CVSS 7.2, High): Path traversal in sandbox escape

**Current version:** 2026.2.6-3  
**Status:** Patched (if configured correctly)

**Recommendation:** Always use the hardened config to ensure patches are effective.

---

## Recommended Enhancements

### 1. Add Sandbox Configuration (High Priority)

**Current:** No sandbox settings (skills run with full permissions)  
**Recommended:** Add to openclaw.json:

```json
{
  "sandbox": {
    "mode": "non-main",
    "scope": "session",
    "workspaceAccess": "none",
    "docker": {
      "enabled": true,
      "network": "none",
      "memoryLimit": "512M",
      "cpuLimit": "1.0"
    },
    "blockList": [
      "/etc/passwd",
      "/etc/shadow",
      "/home/*/.ssh",
      "/home/*/.aws",
      "/var/run/docker.sock"
    ]
  }
}
```

**What this does:**
- `mode: "non-main"` - Sandboxes all skill execution
- `scope: "session"` - Fresh isolated environment per execution
- `workspaceAccess: "none"` - Skills can't read/write workspace
- `docker.network: "none"` - No network access for containers
- `blockList` - Blocks access to sensitive system files

**Impact:** Prevents malicious skills from accessing sensitive data

---

### 2. Add Tool Allowlist/Denylist (Medium Priority)

**Current:** All tools available  
**Recommended:**

```json
{
  "tools": {
    "allow": ["web_search", "brave_search", "firecrawl"],
    "deny": ["elevated", "browser", "kernel_access"],
    "maxExecutionTime": 300,
    "maxMemory": "256M"
  }
}
```

**What this does:**
- Only allow specific safe tools
- Deny dangerous operations
- Limit execution time and memory

---

### 3. Add Cost Limits (Medium Priority)

**Current:** No cost tracking or limits  
**Recommended:**

```json
{
  "costs": {
    "dailyLimit": 5.00,
    "monthlyLimit": 50.00,
    "alertThreshold": 0.80,
    "action": "pause",
    "trackingEnabled": true
  }
}
```

**What this does:**
- Daily budget: $5
- Monthly budget: $50
- Alert at 80% usage
- Pause operations if limit exceeded

---

### 4. Add Explicit Gateway Bind (Low Priority)

**Current:** Implicit localhost (via mode: "local")  
**Recommended:**

```json
{
  "gateway": {
    "mode": "local",
    "bind": "127.0.0.1",
    "port": 18789,
    "maxConnections": 100,
    "requestTimeoutSeconds": 30,
    "rateLimitPerIP": 100,
    "controlUi": {
      "allowInsecureAuth": false
    }
  }
}
```

**What this does:**
- Explicit localhost binding (defense in depth)
- Rate limiting per IP
- Connection limits
- Request timeouts

---

### 5. Add TLS Configuration (Low Priority, Optional)

**Current:** No TLS (localhost-only, not exposed)  
**Recommended if exposing:**

```json
{
  "gateway": {
    "tlsEnabled": true,
    "tlsCertPath": "/home/clawd/.openclaw/certs/openclaw.crt",
    "tlsKeyPath": "/home/clawd/.openclaw/certs/openclaw.key"
  }
}
```

**When needed:** Only if exposing gateway externally (we don't - Telegram-only)

---

### 6. Add Logging Configuration (Medium Priority)

**Current:** Default logging  
**Recommended:**

```json
{
  "logging": {
    "level": "info",
    "format": "json",
    "filePath": "/data/.openclaw/logs/openclaw.log",
    "maxSizeMB": 100,
    "maxAgeDays": 30
  }
}
```

**What this does:**
- Structured JSON logs
- Automatic log rotation
- 30-day retention

---

## Comparison: Our Setup vs PDF Guide

| Feature | Our Setup | PDF Recommends | Status |
|---------|-----------|----------------|--------|
| **Gateway localhost** | ✅ (mode: local) | ✅ (bind: 127.0.0.1) | Good |
| **Session isolation** | ✅ (per-channel-peer) | ✅ (per-channel-peer) | Perfect |
| **Insecure auth disabled** | ✅ | ✅ | Perfect |
| **Telegram-only** | ✅ | ✅ | Perfect |
| **Firewall** | ✅ (UFW) | ✅ | Perfect |
| **File permissions** | ✅ (700/600) | ✅ | Perfect |
| **Security audits** | ✅ (daily cron) | ✅ | Perfect |
| **Sandbox mode** | ❌ (not configured) | ✅ (non-main) | **Missing** |
| **Workspace access** | ❌ (default: full) | ✅ (none) | **Missing** |
| **Tool allowlist** | ❌ (all available) | ✅ (restricted) | **Missing** |
| **Cost limits** | ❌ (tracking only) | ✅ (hard limits) | **Missing** |
| **Rate limiting** | ❌ | ✅ (100 req/IP) | **Missing** |
| **Structured logging** | ❌ (default) | ✅ (JSON logs) | **Missing** |

---

## Implementation Priority

### High Priority (Should Apply)
1. **Sandbox configuration** - Prevents malicious skills
2. **Workspace access: none** - Protects workspace files
3. **Cost limits** - Prevents runaway spending

### Medium Priority (Nice to Have)
4. **Tool allowlist** - Defense in depth
5. **Structured logging** - Better audit trail
6. **Explicit gateway bind** - Additional safety layer

### Low Priority (Optional)
7. **TLS** - Only if exposing externally (we're not)
8. **Advanced rate limiting** - Current setup is low-traffic

---

## Proposed Enhanced Configuration

**Apply these patches to openclaw.json:**

```json
{
  "sandbox": {
    "mode": "non-main",
    "scope": "session",
    "workspaceAccess": "none",
    "docker": {
      "enabled": true,
      "network": "none",
      "memoryLimit": "512M",
      "cpuLimit": "1.0"
    },
    "blockList": [
      "/etc/passwd",
      "/etc/shadow",
      "/home/*/.ssh",
      "/home/*/.aws",
      "/var/run/docker.sock",
      "/data/.openclaw/openclaw.json"
    ]
  },
  "costs": {
    "dailyLimit": 5.00,
    "monthlyLimit": 50.00,
    "alertThreshold": 0.80,
    "action": "alert",
    "trackingEnabled": true
  },
  "gateway": {
    "bind": "127.0.0.1",
    "maxConnections": 100,
    "requestTimeoutSeconds": 30,
    "rateLimitPerIP": 100
  },
  "logging": {
    "level": "info",
    "format": "json",
    "filePath": "/data/.openclaw/logs/openclaw.log",
    "maxSizeMB": 100,
    "maxAgeDays": 30
  }
}
```

---

## Risk Assessment

**Current Setup Risk:** 🟡 **MEDIUM-LOW**
- External exposure: None (firewall + localhost)
- Channel security: Good (Telegram-only, session isolation)
- Skill safety: **Vulnerable** (no sandboxing, full workspace access)
- Cost protection: **None** (no hard limits)

**After Enhancements Risk:** 🟢 **LOW**
- External exposure: None (unchanged)
- Channel security: Good (unchanged)
- Skill safety: **Protected** (sandboxed, no workspace access)
- Cost protection: **Active** ($5/day, $50/month limits)

---

## Testing Plan

**Before applying enhancements:**
1. Backup current config: `cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.backup`
2. Test current setup: `openclaw status --all`
3. Record working state

**After applying:**
1. Apply config patches (use gateway.config.patch)
2. Restart gateway
3. Run `openclaw security audit --deep`
4. Test subagent spawn (ensure sandbox works)
5. Verify Telegram still works

**Rollback if issues:**
1. Restore backup: `cp ~/.openclaw/openclaw.json.backup ~/.openclaw/openclaw.json`
2. Restart: `openclaw restart`

---

## Additional PDF Insights

### From the Guide:

**Best Practices:**
- "Security is not something added later. It is the first thing configured."
- "Orchestrate, don't execute. Your main agent coordinates. Subagents do the heavy lifting."
- "Enforcement beats intention. Rules that exist only in documentation get ignored."
- "Build tools for repeated tasks. If you run the same command three times, write a script."

**We've already implemented these!**
- ✅ Security first (firewall before features)
- ✅ Orchestration (subagent system tested)
- ✅ Enforcement (ENFORCEMENT.md with automated checks)
- ✅ Tools for repetition (14 scripts built)

---

## Recommendations

### Apply Now (High Priority)
1. **Sandbox configuration** - Critical for skill safety
2. **Cost limits** - Prevents runaway spending
3. **Workspace access: none** - Protects your files

**Command:**
```bash
# I can apply these via gateway.config.patch
# Requires your approval
```

### Apply Soon (Medium Priority)
4. **Structured logging** - Better audit trail
5. **Explicit rate limiting** - Defense in depth

### Monitor (Ongoing)
6. **Never run** `openclaw doctor --fix` or `openclaw configure`
7. **Always use** `openclaw security audit` (safe, read-only)
8. **Check CVE updates** quarterly

---

## Status

**Current State:** Good baseline security, missing skill sandboxing and cost limits  
**Risk Level:** Medium-low (external attack surface is minimal, but skill safety is a concern)  
**Recommendation:** Apply sandbox + cost limit patches

**Want me to apply the high-priority enhancements now?**
1. Sandbox configuration (skill safety)
2. Cost limits (budget protection)
3. Enhanced gateway settings (defense in depth)

Say "apply enhancements" and I'll patch the config safely.
