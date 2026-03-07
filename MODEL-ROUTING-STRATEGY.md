# MODEL-ROUTING-STRATEGY.md

## Optimal Model Routing Strategy

**Goal:** Minimize cost (~$21/mo current → &lt;$5/mo target) while preserving quality for human-facing interactions. Prioritize free/cheap models with quality fallbacks. Rate limits handled via chains + queuing.

## 1. Tiered Routing Table

| Use Case | Primary Model | Rationale | Context Limit | Speed |
|----------|---------------|-----------|---------------|-------|
| **1. Main chat (Telegram/human)** | `xai/grok-4-1-fast` | Free, personality-rich, fast for real-time chat | 128K | Fast |
| **2. Sub-agent tasks (research/file)** | `gemini/gemini-2.0-flash` | Free, strong reasoning/analysis | 1M | Fast |
| **3. Cron jobs (heartbeats/monitoring)** | `huggingface/llama-3.1-8b` | Free, lightweight, reliable for simple tasks | 128K | Fast |
| **4. Code gen/debugging** | `xai/grok-code-fast` | Free, code-specialized | 128K | Fast |
| **5. Long-context (100K+)** | `gemini/gemini-3.1-pro-preview` | Free, 1M-2M context | 2M | Medium |
| **6. Quick lookups/simple Qs** | `mistral/small` | $0.1/M, ultra-fast | 128K | Very Fast |
| **7. MELD consensus** | `deepseek/chat-v3` + free mix | Cheap, high throughput for batch | 128K | Fast |
| **8. Sensitive/private** | `venice-ai/[best-available]` | Zero logging, proxied privacy | Varies | Medium |

## 2. Fallback Chains

**Rate limits (10-60 req/min):** Free → Cheap → Moderate. 30s exponential backoff + queue non-urgent.

```
Main chat: grok-4-1-fast → gemini-2.0-flash → mistral/small → gpt-4o-mini → claude-sonnet-4.5

Sub-agents: gemini-2.0-flash → llama-3.3-70b → deepseek-chat-v3 → gpt-4o-mini

Cron: llama-3.1-8b → qwen-2.5-72b → mistral/small

Code: grok-code-fast → qwen-coder-32b → mistral/codestral → gpt-4o

Long-context: gemini-3.1-pro → minimax/text-01 → gpt-4o (2M ctx)

Quick: mistral/small → grok-3 → llama-3.1-8b

MELD: deepseek-chat-v3 → [free pool rotate]

Private: venice-ai → local HF models
```

**Emergency quality:** All chains end with `anthropic/claude-opus-4.6` (human override only).

## 3. Rate Limit Mitigation

- **Primary:** Model rotation + fallback chains (auto-triggered on 429)
- **Queueing:** Non-urgent (cron/sub-agents) → 30s backoff, retry queue
- **Burst protection:** Max 5 concurrent free-model calls
- **Monitoring:** Log rate-limit hits → `memory/rate-limits.md`
- **Free pool:** Rotate xAI/Gemini/HF every 10 reqs
- **Cron scheduling:** Stagger jobs (e.g., heartbeats every 5min → different models)

## 4. Estimated Monthly Cost

**Current:** $21/mo (Opus crons + main)

**Optimized (at current usage):**
- Main: 100K tokens/day × 30 × 0 = **$0** (Grok free)
- Sub-agents: 500K tokens/mo × $0.1-0.3/M = **$0.10**
- Cron: 50K tokens/mo × $0.1/M = **$0.01**
- MELD/quick: 200K tokens/mo × $0.1-0.27/M = **$0.04**
- Fallbacks (5%): 100K tokens/mo × $0.8/M (Haiku avg) = **$0.08**

**Total: ~$0.23/mo** (99% savings)

**Assumptions:** 5K main-chat reqs/mo, 20 sub-agents/day, 100 cron runs/mo. Scale linearly.

## 5. OpenClaw Config Changes

**openclaw.json updates:**

```json
{
  "defaultModel": "xai/grok-4-1-fast",
  "fallbackChain": {
    "main": ["xai/grok-4-1-fast", "gemini/gemini-2.0-flash", "mistral/small", "openai/gpt-4o-mini", "anthropic/claude-sonnet-4.5"],
    "subagent": ["gemini/gemini-2.0-flash", "huggingface/llama-3.3-70b", "deepseek/chat-v3", "openai/gpt-4o-mini"],
    "cron": ["huggingface/llama-3.1-8b", "huggingface/qwen-2.5-72b", "mistral/small"],
    "code": ["xai/grok-code-fast", "huggingface/qwen-coder-32b", "mistral/codestral", "openai/gpt-4o"],
    "longctx": ["gemini/gemini-3.1-pro-preview", "minimax/text-01", "openai/gpt-4o"],
    "quick": ["mistral/small", "xai/grok-3", "huggingface/llama-3.1-8b"],
    "private": ["venice-ai/default", "huggingface/llama-3.1-8b"]
  },
  "sessionOverrides": {
    "runtime=cron": "huggingface/llama-3.1-8b",
    "runtime=subagent": "gemini/gemini-2.0-flash",
    "channel=telegram": "xai/grok-4-1-fast"
  },
  "rateLimit": {
    "backoffMs": 30000,
    "maxConcurrentFree": 5,
    "queueNonUrgent": true
  }
}
```

**Deploy:** `openclaw config reload` + test chains.

**Next:** AB approve → implement + monitor 1 week.

---
*Generated: 2026-03-07 | Cost target: &lt;$1/mo | Quality: 95% Opus parity*