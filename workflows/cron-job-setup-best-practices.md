# Cron Job Setup Best Practices

**Purpose:** Guidelines for creating reliable, maintainable cron jobs in OpenClaw

**Last Updated:** 2026-02-11

---

## ✅ Pre-Creation Checklist

Before creating a cron job, verify:

1. **Script exists and is executable**
   ```bash
   test -f /path/to/script.sh && echo "EXISTS" || echo "MISSING"
   ls -la /path/to/script.sh  # Check permissions
   ```

2. **Script has correct syntax**
   ```bash
   bash -n /path/to/script.sh  # For bash scripts
   python3 -m py_compile script.py  # For Python scripts
   ```

3. **Script works manually**
   ```bash
   bash /path/to/script.sh
   echo $?  # Should be 0 for success
   ```

4. **Model is allowed** (for agentTurn jobs)
   - Use `claude-sonnet-4-5` (default model)
   - Avoid deprecated models: `claude-haiku-3-5`, `claude-opus-3-5`

---

## 🚨 Common Mistakes

### Mistake #1: Referencing Non-Existent Scripts

**Problem:**
```json
{
  "payload": {
    "text": "cd /path && bash scripts/missing.sh"
  }
}
```

**Solution:**
```json
{
  "payload": {
    "text": "test -f /path/scripts/missing.sh && bash /path/scripts/missing.sh || echo 'ERROR: script not found'"
  }
}
```

**Rule:** Always wrap script execution in existence check (see ENFORCEMENT.md Rule #4)

### Mistake #2: Wrong Model Names

**Problem:**
```json
{
  "payload": {
    "kind": "agentTurn",
    "model": "claude-haiku-3-5"  // Not allowed
  }
}
```

**Solution:**
```json
{
  "payload": {
    "kind": "agentTurn",
    "model": "claude-sonnet-4-5"  // Default model
  }
}
```

### Mistake #3: No Error Handling

**Problem:**
```bash
cd /path && bash script.sh
```

**Solution:**
```bash
cd /path && bash script.sh 2>&1 || { echo "ERROR: script failed"; exit 1; }
```

---

## 📋 Cron Job Templates

### System Event (Main Session)

For simple script execution without agent reasoning:

```json
{
  "name": "Descriptive Name",
  "schedule": {
    "kind": "every",
    "everyMs": 3600000  // 1 hour
  },
  "sessionTarget": "main",
  "wakeMode": "now",
  "payload": {
    "kind": "systemEvent",
    "text": "test -f /path/to/script.sh && bash /path/to/script.sh || echo 'ERROR: script not found'"
  },
  "enabled": true
}
```

**When to use:**
- Running existing scripts
- No decision-making required
- Quick checks/backups
- Low-impact operations

### Agent Turn (Isolated Session)

For tasks requiring agent reasoning:

```json
{
  "name": "Descriptive Name",
  "schedule": {
    "kind": "cron",
    "expr": "0 8 * * *",
    "tz": "UTC"
  },
  "sessionTarget": "isolated",
  "wakeMode": "now",
  "payload": {
    "kind": "agentTurn",
    "message": "Task description with:\n1. Clear steps\n2. Success criteria\n3. What to report",
    "timeoutSeconds": 300,
    "model": "claude-sonnet-4-5"
  },
  "delivery": {
    "mode": "announce",  // or "none"
    "to": "user-id",
    "channel": "telegram"
  },
  "enabled": true
}
```

**When to use:**
- Complex analysis/decision-making
- Multi-step workflows
- Report generation
- User-facing summaries

---

## 🔧 Testing Cron Jobs

### Test Payload Manually

**System Event:**
```bash
# Just run the command
test -f /path/to/script.sh && bash /path/to/script.sh
```

**Agent Turn:**
```bash
# Use sessions_send or spawn isolated session
openclaw session spawn --task "Your message here" --label "test-cron"
```

### Test Schedule

```bash
# List all jobs
openclaw cron list

# Check specific job
openclaw cron list | jq '.jobs[] | select(.name == "Your Job Name")'

# View run history
openclaw cron runs --job-id <job-id>

# Trigger manually
openclaw cron run --job-id <job-id>
```

---

## 📊 Schedule Reference

### Every N Minutes/Hours

```json
{
  "kind": "every",
  "everyMs": 1800000  // 30 minutes
}
```

**Common intervals:**
- 15 min: `900000`
- 30 min: `1800000`
- 1 hour: `3600000`
- 6 hours: `21600000`
- 12 hours: `43200000`
- 24 hours: `86400000`

### Cron Expression

```json
{
  "kind": "cron",
  "expr": "0 8 * * *",  // 8:00 AM daily
  "tz": "UTC"
}
```

**Common patterns:**
- Daily 8 AM: `0 8 * * *`
- Daily 1 AM: `0 1 * * *`
- Daily 2 AM: `0 2 * * *`
- Sunday midnight: `0 0 * * 0`
- Every 6 hours: `0 */6 * * *`

### One-Shot (At Specific Time)

```json
{
  "kind": "at",
  "at": "2026-02-11T15:00:00Z"  // ISO 8601 UTC
}
```

---

## 🔍 Debugging Failed Jobs

### Check Last Run Status

```bash
openclaw cron list | jq '.jobs[] | select(.name == "Job Name") | .state'
```

### View Error Details

```bash
openclaw cron runs --job-id <job-id> | jq '.runs[0]'
```

### Common Issues

1. **"model not allowed"** → Update to `claude-sonnet-4-5`
2. **"script not found"** → Add existence check
3. **"timeout"** → Increase `timeoutSeconds`
4. **"permission denied"** → Check file permissions

---

## 📝 Maintenance

### Regular Checks

1. **Weekly:** Review all cron jobs for failures
   ```bash
   openclaw cron list | jq '.jobs[] | select(.state.lastStatus == "error")'
   ```

2. **Monthly:** Audit job necessity
   - Are all jobs still needed?
   - Can any be consolidated?
   - Should frequency change?

3. **After changes:** Test immediately
   ```bash
   openclaw cron run --job-id <job-id>
   ```

### Cleanup

Remove obsolete jobs:
```bash
openclaw cron remove --job-id <job-id>
```

Disable temporarily:
```bash
openclaw cron update --job-id <job-id> --enabled false
```

---

## 🎯 Best Practices Summary

1. ✅ **Always validate script existence** before creating job
2. ✅ **Use default model** (`claude-sonnet-4-5`) for agentTurn jobs
3. ✅ **Add error handling** in systemEvent commands
4. ✅ **Test manually first** before scheduling
5. ✅ **Set appropriate timeouts** (systemEvent: none, agentTurn: 180-600s)
6. ✅ **Log critical operations** to workspace files
7. ✅ **Use descriptive names** for easy identification
8. ✅ **Choose correct sessionTarget** (main for simple, isolated for complex)
9. ✅ **Test delivery settings** before enabling announcements
10. ✅ **Monitor job health** weekly

---

## 📚 Related Documentation

- **ENFORCEMENT.md Rule #4:** Script validation requirement
- **HEARTBEAT.md:** Heartbeat-specific cron patterns
- **memory/mistakes/:** Historical cron job failures
- **tools/:** Available scripts for cron execution

---

**Quick Start:**

1. Create/test script manually
2. Choose template (systemEvent vs agentTurn)
3. Fill in required fields
4. Test with `openclaw cron run`
5. Enable and monitor

**When in doubt:** Use systemEvent with script validation wrapper.
