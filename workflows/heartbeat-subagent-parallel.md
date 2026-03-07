# Heartbeat + Subagent Parallel Work Guide

**Created:** 2026-02-17 04:42 UTC  
**Reason:** Pattern detected (2 occurrences) - Main agent idle during subagent execution  
**Impact:** 8-hour period with 0.25 items/hour (wasteful)

---

## The Problem

**Pattern:** Main agent spawns subagent, then sits idle until completion.

**Examples:**
1. 2026-02-16 20:00-00:00 UTC: meld-sprint2-complete running, main agent idle (4 hours)
2. Previous occurrence: [similar pattern]

**Cost:** 0.25 items/hour instead of target 0.5-1.0 items/hour

---

## The Solution: Parallel Maintenance Work

**When you spawn a subagent:**
1. Spawn the subagent
2. **DO NOT wait idle**
3. Pick maintenance work from list below
4. Check subagent status every 30-60 minutes
5. When subagent completes, integrate results

---

## Parallel Work Checklist

### 📝 Documentation (Safe, No Conflicts)
- [ ] Update MEMORY.md with recent events
- [ ] Consolidate old daily logs (>7 days)
- [ ] Review and update TOOLS.md
- [ ] Document patterns in workflows/
- [ ] Update ENFORCEMENT.md if patterns detected

### 🔍 Monitoring (Read-Only)
- [ ] Run server_health.py
- [ ] Check blocked_items.py list
- [ ] Review mistake_logger.py recent entries
- [ ] Check cron job status
- [ ] Audit security logs

### 🧹 Cleanup (Low-Risk)
- [ ] Archive old checkpoints (>30 days)
- [ ] Compress large log files
- [ ] Remove temp files
- [ ] Git status check (uncommitted changes?)
- [ ] Check for abandoned branches

### 🔬 Analysis (Value-Add)
- [ ] Run mistake_promoter.py (pattern detection)
- [ ] Review effectiveness metrics
- [ ] Check cost tracking trends
- [ ] Audit API key usage
- [ ] Review subagent spawn history

### 🛠️ Infrastructure (Non-Breaking)
- [ ] Update dependencies (audit first)
- [ ] Run security tests
- [ ] Check disk space trends
- [ ] Review backup status
- [ ] Test tool functionality

---

## Example Workflow

```bash
# 1. Spawn subagent
sessions_spawn --task "Fix MELD onboarding UX" --label "meld-ux-fix"

# 2. Immediately pick parallel work (don't wait!)
python3 tools/server_health.py --daily-summary
python3 tools/mistake_promoter.py
# ... consolidate daily logs
# ... update MEMORY.md

# 3. Check subagent status every ~30min
sessions_list --kinds isolated

# 4. When subagent completes, integrate results
# Review output, verify changes, update documentation
```

---

## What NOT to Do in Parallel

❌ **Avoid conflicts with subagent work:**
- Don't edit files the subagent is working on
- Don't run deployments while subagent is deploying
- Don't modify git state if subagent is committing
- Don't change configs the subagent depends on

✅ **Stick to orthogonal work:**
- Different files, different systems
- Read-only operations
- Cleanup and monitoring
- Documentation updates

---

## Success Metrics

**Before pattern (idle):**
- 8 hours, 2 items completed = 0.25 items/hour

**Target (parallel work):**
- 8 hours, 4-8 items completed = 0.5-1.0 items/hour
- Subagent + main agent both productive

**Measurement:**
- Track in work-log.md
- Compare subagent-spawn sessions vs others
- Review in weekly effectiveness reports

---

## Integration with Heartbeat

**HEARTBEAT.md should check:**
1. Are any subagents running? (`sessions_list --kinds isolated`)
2. If yes: Pick parallel work from this guide
3. If no: Normal heartbeat-backlog.md work

**Pattern:**
```markdown
## Heartbeat Cycle

1. Check rate limit (heartbeat_enforcer.py check)
2. Check compaction (compaction_guard.sh)
3. **Check for running subagents** (sessions_list)
4. If subagent active: Pick from heartbeat-subagent-parallel.md
5. If no subagent: Pick from heartbeat-backlog.md
6. Do work
7. Log work (heartbeat_enforcer.py log)
```

---

## Enforcement

**Current Status:** Pattern detected (2 occurrences)

**Next Steps:**
- Monitor for 3rd occurrence
- If happens again → Promote to ENFORCEMENT.md
- Rule would be: "Never sit idle during subagent execution - always do parallel maintenance work"

**Tracking:** Log each subagent spawn in work-log.md with note about parallel work done

---

**References:**
- HEARTBEAT.md (main heartbeat guide)
- heartbeat-backlog.md (task list)
- ENFORCEMENT.md Rule #13 (self-review cycle)
- mistake_logger.py (pattern tracking)
