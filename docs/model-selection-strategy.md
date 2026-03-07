# Model Selection Strategy

**Last Updated:** 2026-02-14  
**Purpose:** Guidelines for choosing the right model for different tasks

---

## Current Model Portfolio

### Primary: Claude Sonnet 4.5 (anthropic/claude-sonnet-4-5)
- **Cost:** $3/1M input tokens, $15/1M output tokens
- **Context:** 200K tokens
- **Best for:** Complex reasoning, code generation, tool use, creative work
- **Default:** Yes (all sessions unless overridden)

### Available Alternatives (via X.AI)
- **Grok 4.1 Fast Reasoning** - Free tier, reasoning capable
- **Grok 4.1 Fast** - Free tier, non-reasoning
- **Grok 4 Fast Reasoning** - Free tier, reasoning capable
- **Grok 3** - Free tier, general purpose
- **Grok Code Fast** - Free tier, code-optimized

### Smart Router (When Deployed)
- **Heartbeat tier:** Llama 3.3 70B ($0.059/1M) - 98% savings
- **Simple tier:** Llama 3.3 70B - 98% savings
- **Moderate tier:** Gemini Flash ($0.15/1M) - 95% savings
- **Complex tier:** Claude Haiku ($1/1M) - 67% savings
- **Frontier tier:** Claude Sonnet 4.5 ($3/1M) - No downgrade

---

## Decision Framework

### 1. Task Classification

**Heartbeat / Status Checks**
- Model: Llama 70B (when router deployed)
- Why: Minimal reasoning, high repetition, huge volume
- Examples: HEARTBEAT_OK responses, status checks, health checks

**Simple Queries**
- Model: Llama 70B or Grok 4.1 Fast
- Why: Straightforward Q&A, no tools needed
- Examples: "What's in AGENTS.md?", "List files in tools/"

**Moderate Work**
- Model: Gemini Flash or Claude Haiku
- Why: Some reasoning, moderate complexity, tool use acceptable
- Examples: File organization, log analysis, documentation updates

**Complex Reasoning**
- Model: Claude Haiku or Claude Sonnet 4.5
- Why: Multi-step logic, nuanced decisions, quality matters
- Examples: Architecture decisions, code review, strategic planning

**Frontier / Critical**
- Model: Claude Sonnet 4.5 (always)
- Why: Maximum capability needed, mistakes are costly
- Examples: Production code, security audits, user-facing content

### 2. Quality vs Cost Trade-offs

**When to pay premium (Claude Sonnet):**
- User-facing work (messages, reports)
- Production code changes
- Security-critical tasks
- Strategic decisions
- Creative content
- When mistakes are expensive

**When to save (cheaper models):**
- Internal tools and automation
- Repetitive tasks (heartbeats, status checks)
- File management and organization
- Log parsing and summarization
- Exploratory research (can verify after)

### 3. Tool Use Considerations

**Tools present → No downgrade**
- Smart router enforces this
- Tools require reliable function calling
- Claude Sonnet is proven reliable
- Cheaper models may fail on complex tools

**No tools → Can downgrade**
- Pure text generation
- Simple Q&A
- Status checks
- File reading

---

## Model Selection Patterns

### Pattern 1: Session Override
```bash
# Use Grok for testing/exploration
/model grok-4-1-fast-reasoning

# Return to default
/model default
```

### Pattern 2: Subagent Spawn
```bash
# Researcher (needs quality)
sessions_spawn --task "..." --agentId researcher --model anthropic/claude-sonnet-4-5

# Status checker (can be cheap)
sessions_spawn --task "..." --agentId monitor --model xai/grok-4-1-fast
```

### Pattern 3: Cron Jobs
```yaml
# Heartbeats: use cheap model
schedule: "*/30 * * * *"
model: "xai/grok-4-1-fast"  # or Llama 70B via router

# Critical jobs: use premium
schedule: "0 9 * * *"
model: "anthropic/claude-sonnet-4-5"
```

---

## Cost Optimization Guidelines

### Target Cost Structure
- **Heartbeats:** 20-30% of total (98% cost reduction via router)
- **Tool calls:** 40-50% of total (no downgrade, quality critical)
- **General work:** 20-30% of total (moderate savings possible)
- **User interaction:** 10-20% of total (premium justified)

### Monthly Budget Targets
- **Current:** ~$90/month (mostly premium)
- **With router:** ~$30/month (67% reduction)
- **Aggressive optimization:** ~$20/month (78% reduction)

### Warning Signs
- Premium usage >80% → Not using router/alternatives
- Heartbeat costs >40% → Not using cheap models
- Tool call errors >5% → Downgraded too aggressively
- User complaints → Quality suffered for savings

---

## Model Characteristics (Observed)

### Claude Sonnet 4.5
- ✅ Exceptional tool use reliability
- ✅ Strong code generation
- ✅ Excellent instruction following
- ✅ Good at complex reasoning
- ❌ Expensive ($3-15/1M)
- ❌ Overkill for simple tasks

### Grok 4.1 Fast Reasoning
- ✅ Free tier available
- ✅ Decent reasoning capability
- ✅ Fast responses
- ⚠️ Tool use not as reliable
- ⚠️ Quality varies on complex tasks

### Llama 3.3 70B (OpenRouter)
- ✅ Very cheap ($0.059/1M)
- ✅ Good for simple tasks
- ✅ Fast inference
- ❌ Weaker reasoning
- ❌ Less reliable tool use

### Gemini Flash
- ✅ Cheap ($0.15/1M)
- ✅ Fast
- ✅ Good balance for moderate tasks
- ⚠️ Sometimes verbose
- ⚠️ Instruction following can drift

---

## Deployment Strategy

### Phase 1: Smart Router (Recommended)
1. Deploy smart router proxy (already built)
2. Configure OpenClaw to route through it
3. Monitor for 1 week (shadow mode)
4. Enable full routing after validation
5. Expected: 60-70% cost reduction

### Phase 2: Subagent Optimization
1. Use Grok models for researchers (free tier)
2. Reserve Claude Sonnet for coders/analysts
3. Test quality on non-critical tasks
4. Adjust based on results

### Phase 3: Cron Job Tuning
1. Switch heartbeat jobs to cheap models
2. Keep critical jobs on premium
3. Monitor failure rates
4. Iterate

---

## Quality Metrics

### Acceptable Quality Thresholds
- Tool call success: >95%
- User satisfaction: Positive feedback
- Error rate: <1% on critical tasks
- Rework rate: <10% (tasks needing redoing)

### When to Revert to Premium
- Tool calls failing repeatedly
- User complaints about quality
- Critical errors in production
- Strategic decisions being made

---

## Override Scenarios

### Always Use Premium (Claude Sonnet)
1. Production deployments
2. User-facing messages
3. Security audits
4. Financial decisions
5. Legal/compliance work
6. When user explicitly requests quality

### Can Use Free/Cheap
1. Heartbeats and status checks
2. File organization
3. Log parsing
4. Test data generation
5. Exploratory research
6. Internal documentation

---

## Monitoring

### Daily Checks
```bash
# Check model usage distribution
python3 tools/session_audit.py --summary

# Check cost trends
python3 tools/cost_tracker.py report --daily
```

### Weekly Review
1. Review model distribution (target: 70% cheap, 30% premium)
2. Check quality issues (user feedback, error logs)
3. Analyze cost vs quality trade-offs
4. Adjust strategy if needed

---

## Examples

### Example 1: Heartbeat Response
**Task:** Check if anything needs attention  
**Model:** Llama 70B via smart router  
**Why:** Status check, no tools, happens 48x/day  
**Savings:** ~$0.30/day = $9/month

### Example 2: Code Generation
**Task:** Implement new feature  
**Model:** Claude Sonnet 4.5  
**Why:** Production code, needs quality, tool use  
**Cost:** Worth it (mistakes expensive)

### Example 3: Research Task
**Task:** Find 10 competitor projects  
**Model:** Grok 4.1 Fast (free) or cheap via router  
**Why:** Exploratory, can verify findings, non-critical  
**Savings:** ~$2/research task

---

## Future Improvements

1. **Auto-selection:** Model router automatically picks based on task
2. **Quality tracking:** Log quality scores per model/task type
3. **Cost dashboards:** Real-time cost monitoring per model
4. **A/B testing:** Compare model quality on same tasks
5. **User preferences:** Let user set cost vs quality preference

---

## References

- Smart router docs: `tools/ROUTER_README.md`
- Cost tracking: `tools/cost_tracker.py`
- Session audit: `tools/session_audit.py`
- Model pricing: OpenRouter, Anthropic, X.AI docs

---

**Status:** Living document  
**Next review:** 2026-02-21 (weekly)  
**Owner:** Main agent + cost monitoring tools
