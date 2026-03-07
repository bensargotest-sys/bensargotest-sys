# OpenAI Shell API Inspired Improvements

**Date:** 2026-02-13  
**Context:** OpenAI launched hosted shell execution with several smart patterns. We've implemented three of them.

---

## 1. Session Auto-Cleanup

**Inspiration:** OpenAI's `expires_after: { anchor: "last_active_at", minutes: 20 }`

**Problem:** Subagents spawned but never cleaned up → resource leaks, token waste, confusion about what's running.

**Solution:** `tools/session_cleanup.py`

### Usage

```bash
# Dry-run to see what would be cleaned
python3 tools/session_cleanup.py --dry-run

# Clean sessions idle >2 hours (default)
python3 tools/session_cleanup.py

# Custom idle threshold (6 hours)
python3 tools/session_cleanup.py --max-idle-hours 6
```

### Features

- Reads sessions directly from OpenClaw's sessions.json
- Skips main session (never auto-kill)
- Logs all kills to `memory/session-cleanup.log`
- Updates `active-tasks.md` (marks [RUNNING] → [CLEANED])
- Configurable idle threshold

### Automation

Add to cron for automatic cleanup:

```yaml
# Every hour, clean sessions idle >2 hours
schedule:
  kind: cron
  expr: "0 * * * *"
payload:
  kind: systemEvent
  text: "Run: python3 tools/session_cleanup.py"
```

---

## 2. Exec Output Limiting

**Inspiration:** OpenAI's `max_output_length: 4096` on shell calls

**Problem:** Commands like `npm install` or log dumps produce thousands of lines → token bloat, context loss.

**Solution:** `tools/exec_limited.py`

### Usage (Python)

```python
from tools.exec_limited import exec_limited

# Execute with 4KB output limit
result = exec_limited("npm install", max_output=4096)

print(result.stdout)  # Truncated if needed
print(f"Truncated: {result.truncated}")
print(f"Original size: {result.original_size} bytes")
```

### Usage (CLI)

```bash
# Execute with output limiting
python3 tools/exec_limited.py "find / -name '*.log'" --max-output 2048

# Output:
# === STDOUT ===
# /var/log/system.log
# ...
# [TRUNCATED: 15234 more bytes, 17282 total]
# === EXIT CODE: 0 ===
# ✂️  TRUNCATED (original: 17282 bytes)
```

### Features

- Truncates stdout/stderr independently
- Shows truncation notice with original size
- Preserves exit codes and timeout info
- Works as Python library or CLI tool

### Integration

Replace direct `exec` calls with `exec_limited` for verbose commands:

```python
# Before: exec("npm install")  # Could be 10K+ lines
# After:
from tools.exec_limited import exec_limited
result = exec_limited("npm install", max_output=4096)  # Capped at 4KB
```

---

## 3. Domain Secrets (Security Hardening)

**Inspiration:** OpenAI's domain_secrets pattern (tokens only resolve for specific domains)

**Problem:** Flat vault allows any code to access any token → prompt injection exfiltration risk, cross-service token reuse.

**Solution:** `tools/domain_secrets.py` + `.api-keys-vault-scoped`

### Migration

```bash
# Migrate flat vault to domain-scoped
python3 tools/domain_secrets.py migrate

# Creates .api-keys-vault-scoped with domain restrictions
```

### Vault Format

```bash
# .api-keys-vault-scoped
GITHUB_TOKEN=ghp_xxx domains=github.com,api.github.com
VERCEL_TOKEN=xxx domains=vercel.com,api.vercel.com
TWITTER_BEARER=xxx domains=api.twitter.com,twitter.com

# Unrestricted (backwards compatible)
SOME_KEY=value
```

### Usage (Python)

```python
from tools.domain_secrets import DomainSecrets

secrets = DomainSecrets()

# Get token only if domain matches
token = secrets.get("GITHUB_TOKEN", target_url="https://api.github.com/repos")
# Returns token ✓

token = secrets.get("GITHUB_TOKEN", target_url="https://evil.com/steal")
# Returns None ✗

# Export environment for subprocess (only allowed secrets)
env = secrets.export_for_domain("https://api.github.com")
subprocess.run(["curl", "..."], env=env)
```

### CLI Tools

```bash
# List all secrets with domain restrictions
python3 tools/domain_secrets.py list

# Verify access for a URL
python3 tools/domain_secrets.py verify --name GITHUB_TOKEN --url "https://api.github.com"
# Output: ✓ GITHUB_TOKEN accessible for api.github.com

python3 tools/domain_secrets.py verify --name GITHUB_TOKEN --url "https://evil.com"
# Output: ✗ GITHUB_TOKEN NOT accessible for evil.com
```

### Security Benefits

1. **Prevents prompt injection exfiltration:** Even if model is tricked into calling `curl evil.com`, token won't be exposed
2. **Prevents cross-service leakage:** GitHub token can't accidentally be sent to Twitter API
3. **Audit trail:** Clear mapping of which tokens work with which services
4. **Backwards compatible:** Tokens without domain restrictions still work everywhere

### Domain Matching Rules

- Exact match: `api.github.com` matches `api.github.com`
- Subdomain match: `api.github.com` matches domain restriction `github.com`
- No wildcards needed (automatic subdomain matching)

---

## Testing

All three tools have been tested:

```bash
# Session cleanup (dry-run)
python3 tools/session_cleanup.py --dry-run
# ✓ Detected 1 idle session (44.7h old)

# Exec limiting
python3 tools/exec_limited.py "seq 1 100" --max-output 100
# ✓ Truncated 292 bytes to 100 bytes

# Domain secrets
python3 tools/domain_secrets.py migrate
python3 tools/domain_secrets.py list
python3 tools/domain_secrets.py verify --name GITHUB_TOKEN --url "https://api.github.com"
# ✓ All working
```

---

## Implementation Notes

### Why These Patterns Matter

1. **Session cleanup:** Prevents slow resource leaks that compound over time
2. **Output limiting:** Prevents sudden context loss from one verbose command
3. **Domain secrets:** Hardens security against prompt injection attacks (increasingly relevant as models interact with untrusted content)

### OpenClaw vs OpenAI Trade-offs

| Feature | OpenAI Hosted Shell | OpenClaw (Self-Hosted) |
|---------|---------------------|------------------------|
| Execution | Sandboxed containers | Direct host/PTY access |
| Network | Allowlist required | Full access by default |
| Persistence | Ephemeral (expires_after) | Persistent (manual cleanup) |
| Security model | Restrictive (safe by default) | Permissive (trust-based) |
| Flexibility | Limited | Full control |

**Our approach:** Trust-based by default, but add security layers where they matter (domain secrets, session cleanup, output limiting).

---

## Next Steps (Future Improvements)

1. **Network allowlisting:** Implement domain-based network filtering (harder, requires proxy/firewall)
2. **Exec sandboxing:** Run untrusted commands in isolated containers (Docker, firejail)
3. **Token rotation:** Auto-rotate secrets based on domain access patterns
4. **Audit logging:** Track which secrets were accessed for which domains

---

**Created:** 2026-02-13 07:23 UTC  
**Status:** All three tools implemented and tested  
**Files:** tools/session_cleanup.py, tools/exec_limited.py, tools/domain_secrets.py
