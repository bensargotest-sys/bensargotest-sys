# Cost-Optimized Routing: Quick Start Guide

## What Is This?

A smart routing system that automatically selects the most cost-effective AI model for each task while maintaining quality.

**Goal:** Reduce AI costs by 30-50% without sacrificing output quality.

---

## Quick Setup (5 Minutes)

### 1. Add Opus to Config
```yaml
# Add to OpenClaw config
models:
  claude-opus-4-6:
    provider: anthropic
    model: claude-opus-4-6
    cost_per_1m_input_tokens: 15.0
    cost_per_1m_output_tokens: 75.0
```

### 2. Enable Routing
```yaml
routing:
  enabled: true
  default_model: claude-sonnet-4-5
```

### 3. Install Tools
```bash
chmod +x tools/routing_tier_classifier.py
chmod +x tools/routing_decision_logger.py
chmod +x tools/routing_cost_dashboard.py
```

---

## Daily Usage

### Check Current Costs
```bash
python3 tools/routing_cost_dashboard.py show 24
```

### Manually Trigger Opus
In your message to the agent:
> "Use Opus for this: [your complex task]"

### Manually Trigger Haiku
In your message to the agent:
> "Use Haiku for this: [your simple task]"

---

## Weekly Optimization

Every Monday:
```bash
# Run optimization process
python3 tools/weekly_routing_optimizer.py

# Review recommendations
cat reviews/routing-week-$(date +%Y%W).txt
```

---

## Decision Guide

### When to Use Opus (Tier 1)
- ✅ Multi-step complex reasoning
- ✅ Large codebase implementation (>1000 lines)
- ✅ Research requiring deep analysis
- ✅ Mission-critical decisions
- ❌ NOT for routine tasks

**Cost:** ~$15-75 per million tokens  
**When:** Sparingly, for high-value work

### When to Use Sonnet 4.5 (Tier 2)
- ✅ Standard complex tasks
- ✅ Most coding tasks
- ✅ Analysis and synthesis
- ✅ Default choice

**Cost:** ~$3-15 per million tokens  
**When:** Most of the time

### When to Use Haiku (Tier 4)
- ✅ Simple queries
- ✅ Status checks
- ✅ Lookups and lists
- ✅ Quick confirmations

**Cost:** ~$0.8-4 per million tokens  
**When:** Whenever possible

---

## Cost Projections

### Baseline (No Routing)
- All tasks use Sonnet 4.5
- **Cost:** $100/month

### With Smart Routing
- 5% use Opus (high-value)
- 60% use Sonnet (standard)
- 35% use Haiku (simple)
- **Cost:** $70/month (-30%)

### Optimized Routing
- 3% use Opus
- 50% use Sonnet
- 47% use Haiku
- **Cost:** $50/month (-50%)

---

## Red Flags

### Cost Alert (>$10/day)
1. Check dashboard: `python3 tools/routing_cost_dashboard.py show 24`
2. Review Opus usage: Is it justified?
3. Adjust tier thresholds if needed

### Quality Degradation
1. Check success rate in dashboard
2. Identify failing task types
3. Upgrade tier for those tasks

### Tier Mismatch
1. Review routing decisions log
2. Look for patterns of wrong classification
3. Update keyword triggers

---

## Troubleshooting

### "Too expensive!"
- Check if Opus is overused
- Lower tier thresholds
- Increase Haiku usage for simple tasks

### "Quality dropped!"
- Check which tasks are failing
- Upgrade tiers for affected task types
- Review tier boundaries

### "Routing not working"
- Verify routing enabled in config
- Check logs: `tail -f memory/routing-decisions.jsonl`
- Test classifier: `python3 tools/routing_tier_classifier.py "test task"`

---

## Best Practices

1. **Start Conservative**
   - Use higher-quality models initially
   - Gradually shift to cheaper models as confidence grows

2. **Monitor Daily**
   - Check dashboard every morning
   - Watch for cost spikes or quality issues

3. **Optimize Weekly**
   - Review full week's data
   - Make small, incremental adjustments

4. **Document Changes**
   - Log all optimization decisions
   - Track rationale and expected impact

5. **Trust the Data**
   - Let metrics guide decisions
   - Don't over-optimize based on hunches

---

## Success Metrics

### Cost Efficiency
- ✅ Target: 30-50% cost reduction
- 📊 Track: Weekly cost vs baseline
- 🎯 Goal: Consistent downward trend

### Quality Maintenance
- ✅ Target: >95% success rate
- 📊 Track: Success rate per tier
- 🎯 Goal: No degradation vs baseline

### Routing Accuracy
- ✅ Target: >90% correct tier assignment
- 📊 Track: Tier mismatches per week
- 🎯 Goal: Decreasing mismatches

---

## Next Steps

1. ✅ Complete setup (above)
2. ⏳ Run for 1 week (collect baseline data)
3. ⏳ First optimization (Week 2)
4. ⏳ Iterate based on data (ongoing)
5. ⏳ Automate what works (Week 4+)

---

**Questions?** Check full docs:
- `research/routing-implementation-plan.md` - Complete implementation guide
- `workflows/weekly-routing-optimization.md` - Optimization process
- `research/opus-config-template.yaml` - Configuration reference

**Last Updated:** 2026-02-14 (Template - will be finalized from research)
