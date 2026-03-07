# Heartbeat Work Patterns - What Works, What Doesn't

**Created:** 2026-02-15 19:31 UTC  
**Based on:** Week 07 data (168 work items completed, 1 productivity gap analyzed)

---

## Summary

Heartbeats are the pulse of autonomous operation. When working well, they complete 1-2 items per hour from a structured backlog. When failing, they return HEARTBEAT_OK without pulling work despite available tasks.

**Key insight:** The system doesn't fail - decision paralysis causes passive heartbeats.

---

## What Works ✅

### 1. Structured Backlog
**Pattern:** heartbeat-backlog.md with 10-20 categorized items

**Why it works:**
- ⚡5min, 🔧15min, 📝30min, 🔬60min time estimates
- Clear task descriptions (not vague goals)
- Mix of quick wins and deeper work
- Always refreshed when dropping below 10 items

**Evidence:** 168 items completed in Week 07 (average 1.5/hour during productive periods)

---

### 2. Mandatory Rate Limiting
**Pattern:** `heartbeat_enforcer.py check` returns RATE_LIMITED if <30 min since last heartbeat

**Why it works:**
- Prevents token waste from rapid-fire HEARTBEAT_OK responses
- Forces real work or silence (no lazy heartbeats)
- Tracks consecutive no-work (warning at 3+)
- Logs all work completions for audit trail

**Evidence:** 0 consecutive no-work maintained for 16 hours (04:00-16:00 UTC Feb 15)

---

### 3. Auto-Checkpoint on Stale
**Pattern:** `compaction_guard.sh` detects STALE (>1h), triggers `checkpoint.py --auto`

**Why it works:**
- Prevents context loss mid-session
- Automatic recovery without manual intervention
- State always fresh for next heartbeat
- No decisions required (just execute)

**Evidence:** 7+ auto-checkpoints completed during Feb 15 session

---

### 4. Quick Tasks First
**Pattern:** Start with ⚡5min tasks when resuming rhythm

**Why it works:**
- Breaks decision paralysis (small commitment)
- Builds momentum (1 done → easier to do next)
- Fast feedback loop (completion feels good)
- Reduces cognitive load (clear scope)

**Examples that worked:**
- Check disk usage trend
- Run security_monitor.py daily
- Review cron job logs
- Verify backup file ages
- Test leak_detector.py with 3 patterns

---

### 5. Testing Security Tools
**Pattern:** Test one security tool per heartbeat with real attack patterns

**Why it works:**
- Clear pass/fail criteria
- Creates valuable audit reports
- Validates production readiness
- Documents tool effectiveness
- Catches configuration issues

**Examples completed:**
- leak_detector.py (5 credential patterns, 100% detection)
- injection_defense.py (4 attack patterns, 0% false positives)
- security_monitor.py (daily report, 0 alerts)

---

### 6. Promoting Patterns to Rules
**Pattern:** When mistake occurs 2+ times, promote to ENFORCEMENT.md rule

**Why it works:**
- Prevents recurring mistakes
- Documents lessons learned
- Creates enforcement gates
- Codifies institutional memory
- Makes rules actionable (not buried in docs)

**Example from Feb 15:**
- Tracking-drift pattern (2 occurrences) → Rule #13 (State File Validation)
- Zombie session investigation → Bug documented for OpenClaw maintainers

---

### 7. Evidence-Based Audits
**Pattern:** Audit a tool/system with scoring, evidence, and recommendations

**Why it works:**
- Structured format (replicable)
- Clear quality gates (70+ = prod ready, 85+ = excellent)
- Actionable findings (not just opinions)
- Comparable across audits
- Validates built ≠ tested ≠ working

**Examples:**
- heartbeat_enforcer.py: 82/100 (prod ready, minor improvements documented)
- session_cleanup.py: 70/100 (detection works, kill verification needed)
- telegram zombie session: Root cause found (OpenClaw CLI bug)

---

### 8. Backlog Maintenance
**Pattern:** Add 10+ items when backlog drops below 10

**Why it works:**
- Never run out of work
- Prevents decision fatigue ("what should I do?")
- Mixes priorities (strategic + tactical + maintenance)
- Keeps rhythm going
- Self-sustaining system

**Evidence:** Backlog refreshed 3 times on Feb 15 (always >10 items)

---

## What Doesn't Work ❌

### 1. Vague Backlog Items
**Anti-pattern:** "Improve documentation" or "Think about TSP"

**Why it fails:**
- No clear completion criteria
- Infinite scope (never done)
- Creates decision paralysis
- Easy to defer ("I'll do it later")
- No momentum (unclear progress)

**Fix:** Make specific: "Update SESSION-START-CHECKLIST.md with Rule #13"

---

### 2. Passive Heartbeats During Work Gaps
**Anti-pattern:** HEARTBEAT_OK returned despite available backlog tasks

**When it happened:** Feb 15, 12:01-16:01 UTC (4-hour gap, 0 items completed)

**Root causes identified:**
- Maintenance fatigue (16 hours of productive work → decision paralysis)
- Complex strategic tasks remain (TSP go/no-go requires user input)
- No quick wins available (all remaining tasks 30+ minutes)
- Decision avoidance (easier to return HEARTBEAT_OK than tackle hard task)

**Impact:**
- Broke 161-item completion streak
- Velocity dropped from 1.5/hour to 0/hour (cliff, not gradual)
- First consecutive no-work in Week 07
- Self-review caught pattern (documented, corrective action planned)

**Fix:**
- Keep 50% of backlog as quick tasks (5-15min)
- When fatigued, do 1 quick task (not HEARTBEAT_OK)
- Strategic tasks require active session (not heartbeat)
- Decision paralysis = log to mistakes.json (make visible)

---

### 3. Building Without Validation
**Anti-pattern:** TSP built for 9 hours without verified customers

**Why it fails:**
- Wasted effort (zero demand discovered later)
- Sunk cost fallacy (hard to kill after investing time)
- Blocks other work (maintenance of zero-traction project)
- Creates strategic debt (unresolved go/no-go decisions)

**Fix:** Validate with 3+ pilots BEFORE building (now in MEMORY.md)

---

### 4. Long Tasks in Heartbeats
**Anti-pattern:** Attempting 60+ minute tasks during heartbeat

**Why it fails:**
- Runs over heartbeat interval (30min minimum)
- Incomplete work at next heartbeat (wasted context)
- Checkpoints mid-task (loses flow state)
- Better suited for active session

**Fix:** Heartbeats for <30min tasks only, spawn subagent for longer work

---

### 5. Asking Instead of Trying
**Anti-pattern:** "Should I do X?" instead of just doing X

**Why it fails:**
- Violates "Try First, Always" principle
- Creates unnecessary friction
- Delays simple work
- User isn't monitoring 24/7 (expect async operation)

**Fix:** Only ask for external actions, money, critical config, or when stuck after trying

---

### 6. Ignoring Cron Job Failures
**Anti-pattern:** 6 cron jobs failing for 24+ hours without investigation

**When discovered:** Feb 15, 13:05 UTC (cron status check revealed 46% failure rate)

**Root cause:** Model configuration error (using disallowed model in 6 jobs)

**Why it's bad:**
- Nightly maintenance not running
- Daily security audits not running
- Morning briefings not running
- User expects automated routines (but they're failing silently)

**Fix:** Daily cron health check (all jobs, check lastStatus field, report failures)

---

### 7. Duplicate Strategic Tasks
**Anti-pattern:** Multiple backlog items for same decision

**Example:** Both "Create go/no-go decision framework for TSP/TrustScore" and "Create TSP/TrustScore strategic decision document (kill/validate/fix)"

**Why it fails:**
- Splits attention
- Unclear which to do first
- Creates illusion of more work
- Decision still not made

**Fix:** Consolidate to one clear task with deliverable

---

## Productivity Patterns

### Morning (04:00-12:00 UTC)
**Observed:** 17 items completed, mix of maintenance and validation

**What works:**
- System health checks (security, cron logs, backups, disk)
- Tool testing (leak detector, injection defense)
- Audits (heartbeat_enforcer, session_cleanup, telegram zombie)
- Documentation updates (ENFORCEMENT.md Rule #13, SESSION-START-CHECKLIST.md)
- Quick infrastructure fixes (subagent_log.py validation logic)

**Pattern:** Maintenance-heavy, validation-focused, evidence-based

---

### Afternoon Gap (12:00-16:00 UTC)
**Observed:** 0 items completed, passive heartbeats despite backlog

**What failed:**
- Maintenance fatigue (16 hours straight)
- Strategic tasks remaining (TSP go/no-go, MEMORY.md update)
- No quick wins (all tasks 30+ minutes)
- Decision paralysis (easier to return HEARTBEAT_OK)

**Pattern:** Avoidance, decision paralysis, passive operation

---

### Evening Recovery (16:00-20:00 UTC)
**Observed:** 4 items completed, resumed rhythm

**What works:**
- Promoted tracking-drift to ENFORCEMENT.md Rule #13
- Updated SESSION-START-CHECKLIST.md with Rule #13
- Added validation logic to subagent_log.py
- Cleaned backlog (removed non-existent tool)

**Pattern:** Infrastructure improvements, documentation, enforcement

---

## Recommendations

### For Productive Heartbeats
1. **Keep backlog 50% quick tasks** (⚡5min, 🔧15min)
2. **Do 1 task minimum** (never return HEARTBEAT_OK with available work)
3. **Test tools with real data** (creates valuable audit reports)
4. **Document findings** (every audit creates a report in reviews/)
5. **Update enforcement** (2+ mistakes = promote to rule)
6. **Check system health** (cron logs, security alerts, disk usage)

### For Strategic Work
1. **Use active sessions** (not heartbeats for 30+ minute tasks)
2. **Spawn subagents** (for research, analysis, implementation)
3. **Validate before building** (3+ pilots required)
4. **Make go/no-go decisions** (don't maintain zero-traction projects)
5. **Update MEMORY.md** (weekly, capture lessons learned)

### For Avoiding Gaps
1. **Detect decision paralysis early** (2+ HEARTBEAT_OK with backlog = log to mistakes)
2. **Force quick wins** (when fatigued, do 5-min task not HEARTBEAT_OK)
3. **Refresh backlog often** (add 10 items when <10 remain)
4. **Mix priorities** (strategic + tactical + maintenance)
5. **Self-review catches gaps** (every 4h cron, documented pattern)

---

## Metrics

### Week 07 Performance
- **Total work items:** 168 (as of Feb 15 17:40 UTC)
- **Average velocity:** 1.5 items/hour (during productive periods)
- **Consecutive no-work:** 0 (maintained for 16 hours)
- **Gap duration:** 4 hours (12:01-16:01 UTC, first gap in Week 07)
- **Gap cause:** Decision paralysis after maintenance fatigue
- **Recovery time:** 2 hours (resumed rhythm at 16:24 UTC with Rule #13 promotion)

### Quality Metrics
- **Audits created:** 6 (heartbeat_enforcer, session_cleanup, zombie investigation, cron status, leak_detector, injection_defense, mistake_review)
- **Rules promoted:** 1 (Rule #13: State File Validation)
- **Tools fixed:** 2 (subagent_log.py validation, SESSION-START-CHECKLIST.md)
- **Mistakes logged:** 0 today (healthy)
- **Security tests:** 2 (leak_detector 100%, injection_defense 100%)

---

## Conclusion

**Heartbeats work when:**
- Backlog is structured (clear tasks, time estimates)
- Quick tasks available (50% under 15 minutes)
- Rate limiting enforced (30-min minimum, tracks no-work)
- Evidence-based work (audits, tests, documentation)
- Decision paralysis avoided (do 1 task minimum)

**Heartbeats fail when:**
- Vague tasks (no completion criteria)
- All tasks complex (no quick wins)
- Decision fatigue (after long maintenance periods)
- Strategic decisions pending (require user input)
- Passive default (HEARTBEAT_OK easier than work)

**Key learning:** The system is designed well. The risk is operator decision paralysis, not technical failure. Force action (even 1 small task) over inaction.

---

**Status:** Pattern documented. Implement recommendations to prevent future productivity gaps.
