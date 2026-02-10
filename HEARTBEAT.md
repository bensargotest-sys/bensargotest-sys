# HEARTBEAT.md

Do something useful every heartbeat. HEARTBEAT_OK only after proven work.

## Rate Limit

Check heartbeat-state.json. If less than 30 minutes since last heartbeat, reply HEARTBEAT_OK immediately. Do not burn tokens on back-to-back heartbeats.

```bash
python3 tools/heartbeat_enforcer.py check
# If RATE_LIMITED, stop immediately and reply HEARTBEAT_OK
```

## The Loop

1. Read heartbeat-state.json and WORKING_STATE.md
2. Run compaction guard. If STALE, checkpoint immediately.
3. Check rate limiter. If rate-limited, stop.
4. Run any monitors or position checks (quick, <10 seconds)
5. Pick one item from memory/heartbeat-backlog.md and COMPLETE it
6. Run one tool from the rotation schedule
7. Log to memory/work-log.md with timestamp and evidence
8. Update heartbeat-state.json

## Compaction Guard (CRITICAL)

```bash
bash tools/compaction_guard.sh
# If STALE, run:
python3 tools/checkpoint.py --auto --note "heartbeat pre-work checkpoint"
```

## Heartbeat Backlog

Pick based on available time:
⚡5min | 🔧15min | 📝30min | 🔬60min

Pull from `memory/heartbeat-backlog.md`. If empty or <10 items, stop and ask for backlog refill.

After completing an item:
- Mark [x] in heartbeat-backlog.md
- Log to work-log.md with evidence (file created, output, command result)
- Update heartbeat-state.json via heartbeat_enforcer.py

## Mistake Check (Every Heartbeat)

Before ending each heartbeat, answer three questions:

1. Did any tool fail this heartbeat?
2. Did any subagent stall or produce empty output?
3. Did anything unexpected happen?

If any answer is yes:
```bash
python3 tools/mistake_logger.py log "description" --category "category"
```

## Reach Out / Stay Quiet

**Reach out when:**
- Important development (finished meaningful work)
- Something urgent detected
- It's been >8 hours since last check-in
- User is likely awake and available

**Stay quiet (HEARTBEAT_OK) when:**
- Late night (23:00-08:00 UTC) unless urgent
- Nothing new since last check
- Checked <30 minutes ago
- User is clearly busy in active conversation

## Tool Rotation

Based on heartbeat count modulo N:

**Every heartbeat:**
- Position checks (if applicable)
- Activity logging
- Compaction guard

**Every 2nd heartbeat:**
- Self-evaluation
- Preference scanning

**Every 3rd heartbeat:**
- Memory consolidation check
- Pattern analysis

**Every 5th heartbeat:**
- Full memory review
- Skill usage audit
- TSP feedback scan (Moltbook comments, GitHub issues)

**Every 10th heartbeat:**
- Check TSP agent behavior (provisional conversions, credit usage)
- Update FEEDBACK-LOG.md with new observations
- Analyze for improvement opportunities

**Weekly (every ~336th heartbeat at 30min intervals):**
- Full consolidation
- Archive audit
- Mistake promotion scan
- Weekly feedback review (see FEEDBACK-DRIVEN-DEVELOPMENT.md)

## Productive Background Work

Things you can do autonomously without asking:

**File Organization:**
- Clean up workspace
- Archive old logs
- Organize memory files

**Code Maintenance:**
- Review and refactor scripts
- Add error handling
- Improve documentation

**Memory Maintenance:**
- Review recent daily logs
- Update MEMORY.md with insights
- Remove stale information

**Task Preparation:**
- Research upcoming tasks
- Prepare templates
- Test tools

**System Health:**
- Check tool availability
- Verify backup freshness
- Monitor disk usage

## Heartbeat Success Criteria

A good heartbeat includes:
- ✅ Real work completed (not just checking)
- ✅ Evidence logged (file path, output, result)
- ✅ State files updated
- ✅ No silent failures ignored

A lazy heartbeat:
- ❌ Just checking without action
- ❌ No tangible output
- ❌ "Everything looks fine" without proof

## Example Heartbeat Flow

```
1. bash tools/compaction_guard.sh → FRESH ✓
2. python3 tools/heartbeat_enforcer.py check → PROCEED ✓
3. Check memory/heartbeat-backlog.md → picked "Document API endpoints"
4. Create docs/api-endpoints.md with content
5. Mark task [x] in backlog
6. python3 tools/heartbeat_enforcer.py log "Documented 12 API endpoints in docs/api-endpoints.md"
7. Run mistake check → no failures
8. Reply HEARTBEAT_OK (quiet hours, nothing urgent)
```

---

**Target:** 3-5 productive heartbeats per day
**Goal:** Every heartbeat produces tangible output
**Measure:** `python3 tools/heartbeat_enforcer.py check` shows growing work count

## TSP Launch Monitoring (Every 6 Hours)

Check TSP metrics and engagement:

```bash
bash /data/.openclaw/workspace/tsp/tools/check-metrics.sh
```

**What to check:**
1. Moltbook karma (upvotes) + comments/feedback
2. GitHub stars + issues/PRs
3. Formspree signups (manual: https://formspree.io/forms/xwpklgqa)
4. Outreach responses (Observatory, ClawLoan, YonesAssistant)
5. Agent behavior (provisional conversions, credit usage)

**Alert human if:**
- GitHub stars > 0
- **Formspree signups > 0** ← PING ON TELEGRAM IMMEDIATELY
- Moltbook karma > 10
- Email response received
- Agent feedback received (Moltbook DM, GitHub issue)
- Unusual pattern detected (high defaults, low conversions)

**CRITICAL: TSP Signups**
When a new signup is detected:
1. Send Telegram message: "🎉 New TSP Signup! Agent: [agent_id], Total: [count]"
2. Update signup-tracker.json
3. Log to memory/work-log.md
4. Celebrate (we got one!)

**Feedback collection:**
- Scan Moltbook comments on TSP posts
- Check GitHub issues/PRs
- Review agent behavior patterns
- Log findings to `/data/.openclaw/workspace/tsp/FEEDBACK-LOG.md`

**Rate limit status:**
- Moltbook posting: Available after 01:00 UTC (check `/data/.openclaw/workspace/tsp/metrics-dashboard.json`)

**Continuous improvement:**
- Every 6h: Collect feedback data
- Weekly: Analyze and propose improvements (see FEEDBACK-DRIVEN-DEVELOPMENT.md)
- Monthly: Deep review and roadmap update

