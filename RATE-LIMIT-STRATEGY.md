# Multi-Provider AI Inference Rate Limit Mitigation & Failover Strategy

## Provider Tiers & Capacities
Classified by cost/reliability:

**Free Tier (Primary, capacity-limited):**
| Provider | RPM | Daily | Notes |
|----------|-----|-------|-------|
| xAI (Grok) | 60 | 1M tokens | Generous, prioritize |
| Gemini | 15 | 1500 req | Moderate |
| HuggingFace | 10 | - | Queuing |
| NVIDIA NIM | 10 | - | Moderate |
| Mistral | 5 | - | Limited |

**Paid Tier (Fallback, cost-controlled):**
| Provider | RPM | Notes |
|----------|-----|-------|
| DeepSeek | 60 | Cheap |
| DashScope | 60 | Cheap |
| OpenAI | 60 | Moderate |
| Anthropic | 50 | Expensive (last resort) |
| Venice AI | ? | Likely generous |
| MiniMax | ? | 1M context |

## 1. Rate Limit Budget Allocation
**Daily Budget Split (adjustable via config):**
```
Human Interactive: 60% (priority 1)
Sub-agents: 25%  (priority 2) 
Cron/Automated: 15% (priority 3, off-peak)
```

**Per-Minute Buckets (token-windowed, 60s rolling):**
- Track `requests_used` and `tokens_used` per provider per category
- Hard reserve: Human = 80% of RPM, others share 20%
- Soft throttle: Warn at 70%, block at 90%

**Implementation:**
```yaml
budgets:
  human: { weight: 0.6, reserve_pct: 0.8 }
  subagent: { weight: 0.25 }
  cron: { weight: 0.15, peak_hours: false }
```

## 2. Backoff & Circuit Breaker
**Per-Provider State Machine:**
```
Normal → Warming (70% usage) → Throttled (90%) → Circuit Open (rate limit hit)
         ↑                           ↓                    ↓
       Normal ← Cooling (30s) ← Recovering ← Half-open (1 req test)
```

**Backoff Strategy:**
- **Exponential**: `delay = min(60s, base * 2^attempts)` + `jitter(±20%)`
- **Circuit Breaker**: Open → 30s → Half-open (1 req) → success=close, fail=30s more
- **Global Fallback**: All free providers open → paid tier (with cost cap)

## 3. Provider Rotation (Weighted Intelligent)
**Selection Algorithm:** Weighted Round-Robin with LRU penalty

```
score = (remaining_capacity_pct * weight) - (lru_penalty * 0.1)
  - weight: xAI=3.0, Gemini=2.0, HF/NIM=1.5, Mistral=1.0
  - lru_penalty: increases per consecutive use (resets on 60s idle)
```

**Request Flow:**
```
1. Filter eligible (circuit=closed + budget>0)
2. Select highest score
3. On 429/503: immediate circuit trip + rotate
4. Success: lru_tick++, budget--
```

## 4. Time-of-Day Routing
**Peak Hours (UTC, configurable): 14:00-02:00** (human chat prime time)

```
Peak Hours:
  - Human → Free Tier (full budget)
  - Cron → Paid Tier OR delay to off-peak
  - Sub-agents → Free Tier (reduced concurrency)

Off-Peak (02:00-14:00):
  - Cron → Free Tier (catch-up)
  - Bulk sub-agent swarms OK
```

**Cron Scheduling:**
```cron
# Human-peak: use paid/reserve
0 14-23 * * * cron-job --tier=paid
# Off-peak: burn free capacity
0 2-13 * * * cron-job --tier=free
```

## 5. Monitoring & Observability
**Real-time Dashboard (Prometheus/Grafana):**
```
Metrics:
- provider_rate_usage{rpm_used, tokens_used, category}
- circuit_state{provider, state=open|half|closed}
- fallback_count{to_paid, emergency}
- request_latency_p95
```

**Alerts:**
```
CRITICAL: Free tier exhausted (>95% 5min)
WARNING: Single provider >85% OR circuit open >2min
INFO: Budget <20% remaining (hourly)
```

**In-Memory State (Redis):**
```
rate-limits:{provider}:{category}: {used:123, capacity:60, window_end:ts}
circuits:{provider}: {state:'open', opened_at:ts, consecutive_fails:3}
```

## 6. Emergency Fallbacks
```
1. Free exhaustion → Paid cheap (DeepSeek/DashScope)
2. All paid cheap exhausted → Expensive (OpenAI/Anthropic, max $0.10/min)
3. ALL providers down → Queue + human notification
4. Cost emergency → Degraded mode (cached responses, local models)
```

**Queue Policy:**
```
- Human: queue <30s → notify "High load, response delayed"
- Sub-agent: queue >60s → kill + retry later
- Cron: queue unlimited, execute off-peak
```

## Implementation Priority
```
Phase 1 (1 day): Budget tracking + weighted rotation
Phase 2 (2 days): Circuit breakers + Redis state
Phase 3 (1 day): Time-of-day + monitoring
Phase 4 (2 days): Dashboard + alerts

## Config Template
```yaml
providers:
  free:
    - name: xai, rpm:60, weight:3.0, daily_tokens:1e6
    - name: gemini, rpm:15, weight:2.0
  paid_cheap:
    - name: deepseek, rpm:60, cost_per_1k:0.1
  paid_expensive:
    - name: anthropic, rpm:50, cost_per_1k:3.0

budgets:
  human: 0.6
  subagent: 0.25
  cron: 0.15

peak_hours: [14,15,16,17,18,19,20,21,22,23,0,1]
```
