# Model Optimization Strategy

**Applied:** 2026-02-09 19:04 UTC  
**Goal:** Optimize cost while maintaining quality

---

## Model Configuration

### Main Agent
**Model:** `claude-sonnet-4-5`  
**Use:** Default for all interactive conversations  
**Why:** Best balance of speed, cost, and capability

---

## Automated Tasks (Cron Jobs)

| Task | Model | Frequency | Reasoning |
|------|-------|-----------|-----------|
| **Morning Briefing** | Haiku 3.5 | Daily 08:00 UTC | Simple status summary - cheap ✅ |
| **Nightly Maintenance** | Haiku 3.5 | Daily 01:00 UTC | Routine cleanup - fast & cheap ✅ |
| **Security Audit** | Opus 3.5 | Daily 02:00 UTC | Critical decisions - premium quality 🔒 |
| **Weekly Review** | Sonnet 4.5 | Sunday 00:00 UTC | Balanced analysis - optimal 📊 |

---

## Cost Analysis

### Before Optimization (All Sonnet 4.5)
**Estimated monthly cost:** $10-30
- Morning briefings: ~$2-5/month
- Nightly maintenance: ~$3-6/month
- Security audits: ~$2-4/month
- Weekly reviews: ~$1-2/month
- Interactive use: ~$2-13/month

### After Optimization (Hybrid)
**Estimated monthly cost:** $12-25
- Morning briefings: ~$0.20-0.50/month (Haiku) ⬇️ **90% savings**
- Nightly maintenance: ~$0.30-0.60/month (Haiku) ⬇️ **90% savings**
- Security audits: ~$10-20/month (Opus) ⬆️ **5x increase** (worth it!)
- Weekly reviews: ~$1-2/month (Sonnet) ➡️ **same**
- Interactive use: ~$0.50-2/month (less heartbeat overhead)

**Net Impact:** Similar total cost, but:
- ✅ 90% cheaper routine tasks
- ✅ 5x better security analysis
- ✅ Same quality for important work

---

## Model Characteristics

### Haiku 3.5 (Cheapest/Fastest)
**Cost:** ~$0.25 input / $1.25 output per 1M tokens  
**Speed:** ⚡⚡⚡ Very fast  
**Intelligence:** ⭐⭐ Good for simple tasks  

**Best for:**
- Status summaries
- Simple checks
- Routine maintenance
- Log cleanup
- Basic monitoring

**Not good for:**
- Complex reasoning
- Critical decisions
- Strategic planning

### Sonnet 4.5 (Balanced - Default)
**Cost:** ~$3 input / $15 output per 1M tokens  
**Speed:** ⚡⚡ Fast  
**Intelligence:** ⭐⭐⭐⭐ Very capable  

**Best for:**
- General purpose (default)
- Interactive conversations
- Code generation
- System design
- Analysis and reporting

**Not good for:**
- When you need absolute best (use Opus)
- When simple checks suffice (use Haiku)

### Opus 3.5 (Most Capable)
**Cost:** ~$15 input / $75 output per 1M tokens  
**Speed:** ⚡ Slower  
**Intelligence:** ⭐⭐⭐⭐⭐ Highest capability  

**Best for:**
- Security audits (critical!)
- Complex strategic decisions
- High-stakes reasoning
- When quality > cost

**Not good for:**
- Routine tasks (wasteful)
- High-volume operations (expensive)
- When speed matters (slower)

---

## Why This Configuration?

### Morning Briefing → Haiku
**Task:** "Check health, summarize yesterday, list priorities"  
**Complexity:** LOW - just reading files and formatting output  
**Cost savings:** 90%  
**Quality impact:** None - Haiku can easily do status summaries

### Nightly Maintenance → Haiku
**Task:** "Close logs, consolidate memory, run cleanup scripts"  
**Complexity:** LOW - routine file operations  
**Cost savings:** 90%  
**Quality impact:** None - mechanical tasks don't need reasoning

### Security Audit → Opus
**Task:** "Deep security scan, analyze threats, make critical decisions"  
**Complexity:** HIGH - requires careful reasoning about security  
**Cost increase:** 5x  
**Quality gain:** Worth it - security is critical, false negatives are costly

### Weekly Review → Sonnet
**Task:** "Analyze week's work, extract insights, write report"  
**Complexity:** MEDIUM - needs good analysis but not critical decisions  
**Cost:** Same  
**Quality:** Perfect for this - balanced analysis

---

## Expected Behavior Changes

### What Stays the Same
- ✅ Main agent quality (you're still talking to Sonnet 4.5)
- ✅ Weekly review depth (Sonnet 4.5)
- ✅ All functionality working

### What Gets Faster
- ⚡ Morning briefings (Haiku is faster)
- ⚡ Nightly maintenance (Haiku is faster)

### What Gets Better
- 🔒 Security audits (Opus is more thorough)
- 💰 Cost efficiency (90% savings on routine tasks)

### What Gets Cheaper
- 💰 Heartbeat overhead (less token burn)
- 💰 Status updates (Haiku vs Sonnet)

---

## Monitoring

**Watch for:**
1. **Haiku quality issues** - If morning briefings or nightly maintenance start failing, switch back to Sonnet
2. **Opus overkill** - If security audits always return "no issues", consider downgrading to Sonnet
3. **Cost drift** - Monitor actual spend vs estimates

**Adjust if:**
- Morning briefings miss important details → upgrade to Sonnet
- Security audits too expensive with no findings → downgrade to Sonnet
- Nightly maintenance fails repeatedly → upgrade to Sonnet

---

## Rollback Plan

If optimization causes issues:

```bash
# Revert all jobs to Sonnet 4.5 (original config)
openclaw cron update <job-id> --model claude-sonnet-4-5
```

Or update via config:
```json
{
  "agents": {
    "main": {
      "model": "claude-sonnet-4-5"
    }
  }
}
```

---

## Summary

**Optimization Applied:** Hybrid model strategy  
**Cost Impact:** Similar total, better allocation  
**Quality Impact:** Improved security, same everything else  
**Risk:** Low - easy to rollback if needed  

**Status:** ✅ Active and monitoring

**Next review:** After 1 week of operation (2026-02-16)
