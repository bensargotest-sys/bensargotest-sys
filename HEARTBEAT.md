# HEARTBEAT.md

**Do something useful every heartbeat. HEARTBEAT_OK only after proven work.**

## Checklist

1. **Rate limit:** `python3 tools/heartbeat_enforcer.py check` → If RATE_LIMITED, reply HEARTBEAT_OK and stop
2. **Compaction:** `bash tools/compaction_guard.sh` → If STALE, checkpoint before work
3. **Check subagents:** Check if any subagents running (`sessions_list --kinds isolated`)
   - **If subagent active:** Pick parallel work from `workflows/heartbeat-subagent-parallel.md` (never sit idle!)
   - **If no subagent:** Pick one item from `memory/heartbeat-backlog.md`
4. **MELD feedback loop:** Check `curl -s http://localhost:8090/v1/metrics/queue 2>/dev/null` for open issues. Fix high-severity items immediately.
4a. **Memory consolidation:** `python3 tools/consolidate_memories.py --check` → If NEEDS_CONSOLIDATION, run consolidation (cross-reference recent memories, generate insights, update consolidations.md). Use cheap model for the LLM call.
5. **Log:** Update `memory/work-log.md` with evidence (file path, output, result)
5. **Confirm:** `python3 tools/heartbeat_enforcer.py log "what you completed"`
6. **Mistakes:** Did anything fail? → `python3 tools/mistake_logger.py log "description"`
7. **Reach out or stay quiet:**
   - Reach out: Important work done, urgent issue, >8h since last check
   - Stay quiet: Late night (23:00-08:00 UTC), nothing new, <30min since last check

## Success Criteria

✅ Real work completed (not just checking)  
✅ Evidence logged  
✅ State files updated  

❌ Just checking without action = lazy heartbeat

---

**Reference:** Full documentation in OPERATIONS-GUIDE.md Section 6 (Heartbeat System)
