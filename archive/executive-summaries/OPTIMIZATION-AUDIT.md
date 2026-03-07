# Optimization Audit — 2026-03-07

## 1. API Keys Available But NOT Configured

We have **8 API keys** sitting in the vault that aren't wired into openclaw.json:

| Provider | Key | Status | What We'd Get |
|----------|-----|--------|---------------|
| **DeepSeek** | `sk-da8a4e...` + `sk-18007...` | ✅ Valid | DeepSeek V3 — strong reasoning, cheap |
| **Qwen/DashScope** | `sk-461ede...` | ✅ Valid | Qwen 3.5 Plus — free tier, Alibaba |
| **Mistral** | `hG1SbB7z...` | ❓ Untested | Mistral Large — strong coding |
| **Venice AI** | `VENICE_INFERENCE_KEY_7V...` | ✅ Valid | Private inference (zero logging), DeepSeek/Qwen/Llama |
| **NVIDIA NIM** | `nvapi-xaLSP...` | ❓ Untested | Llama 3.3 70B, enterprise models |
| **MiniMax** | `sk-api-SLkXnx...` | ❌ Insufficient balance | MiniMax-Text-01 — needs top-up |
| **ElevenLabs** | `sk_841113...` | ✅ Valid | TTS — voice output for briefings |
| **Anthropic Direct** | `sk-ant-api03-1tU...` | ⚠️ Limited | Claude 3 Haiku only (old plan) |

### Quick Wins — Add These Now:
1. **DeepSeek** — Add as provider, use for cheap reasoning tasks
2. **Mistral** — Add as provider, good coding model for overnight builder
3. **Venice AI** — Private inference, OpenAI-compatible, great for sensitive tasks
4. **ElevenLabs** — Enable TTS morning briefings (guide says "Presidential Briefing with TTS")

## 2. Model Providers — Current vs Optimal

### Currently Configured (5 providers):
- Anthropic (Claude Opus 4.6, Sonnet 4.5, Haiku 4.5) — via OAuth
- xAI (Grok 4.1 Fast, Grok 4 Fast Reasoning) — FREE
- OpenAI (GPT-4o, GPT-4o-mini, Codex Mini) — paid
- Gemini (Flash 2.0, 3.1 Pro Preview) — FREE
- OpenRouter (Gemini Flash fallback)

### Should Add:
- **DeepSeek** — provider: `deepseek`, base URL: `https://api.deepseek.com/v1`
- **Mistral** — provider: `mistral`, base URL: `https://api.mistral.ai/v1`
- **Venice AI** — provider: `venice`, base URL: `https://api.venice.ai/api/v1`
- **NVIDIA NIM** — provider: `nvidia`, base URL: `https://integrate.api.nvidia.com/v1`
- **DashScope** — provider: `dashscope`, base URL: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`

### Optimal Fallback Chain:
```
Claude Opus 4.6 → Claude Sonnet 4.5 → Grok 4.1 Fast → DeepSeek → Gemini Flash → Mistral → GPT-4o
```

## 3. Ideas & Links from Chat History

### Product Ideas (by potential):
1. **Voice-First Idea Network** — AI-guided voice curation → idea graph → best get built. Network effects. Connects MELD + ClawLab. [TODAY]
2. **PriorFind / Patent Validator** — Two versions built (attack + defend). "Validate Your Patent" B2B positioning. [BUILT, needs users]
3. **Inference Lineage Proofs ("Verisign for AI")** — Merkle DAG, <2ms overhead, EU AI Act compliance. Strongest standalone product. [DESIGNED]
4. **MELD Context Window Orchestrator** — Split large docs across models, synthesize. Real pain point. [TODAY - new idea]
5. **ClawLab AI Co-Founder** — B2B SaaS focus, success fee model. [BUILT]
6. **Collision Engine** — Failed ideas → decompose → match complementary pieces → new products. [CONCEPT]
7. **Royalty Marketplace** — Contribute code/ideas → tracked via provenance → proportional revenue. [CONCEPT]
8. **DAO Oracle Plugin** — Snapshot plugin, AI analysis for 10K+ DAOs. Cheapest on-chain win. [DESIGNED]
9. **Sybil Detection Product** — 40% success chance, recommended in memory. [CONCEPT]
10. **"Guard" Product** — From Anthropic autonomy paper, validated as differentiated. [CONCEPT]

### Key Links from History:
- `https://meld.credit` — MELD landing page (needs update)
- `https://venice.ai` — Private inference provider
- `https://zenmux.ai` — Ring-2.5-1T API (new, untested)
- `https://myclaw.ai` — MyClaw managed OpenClaw hosting (potential partner)
- `https://clawhub.com` — Skill marketplace
- DashScope Qwen API: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
- NVIDIA NIM: `https://integrate.api.nvidia.com/v1`

### Key Strategic Insights from Memory:
- **"We built an entire product for customers that don't exist"** — TSP lesson
- **"Validate before building. Always get 3+ pilots first"** — repeated across sessions
- **Target user pain is 429 errors (rate limits), not cost** — reliability > price
- **Agent diversity ≈ model diversity for output diversity** (B ≈ C finding)
- **Cheap process > expensive model** — 3×Gemini→Gemini beats solo GPT-4o
- **Synthesis quality is the moat** — Sonnet-synth (89-98%) >> Grok-3-synth (70%)
- **"Don't sell MELD to individual users. Sell to hosting providers like MyClaw"**
- **AB pattern: cycles through ideas rapidly** — need to pick ONE and go deep
- **Lineage proofs = "Verisign for AI"** — strongest standalone direction

## 4. System Optimization Opportunities

### A. Missing Cron Jobs (from guide):
- [x] Episode Recorder — ADDED TODAY
- [x] Instinct Engine — ADDED TODAY
- [x] Partner Scorecard — ADDED TODAY
- [ ] TTS Morning Briefing (needs ElevenLabs provider config)
- [ ] Semantic memory sync (memU alternative using OpenClaw built-in memory search)

### B. Stale/Broken Components:
- Partner Scorecard: last updated 2026-02-20 (17 days stale)
- Instinct Engine: last scan 2026-02-22 (13 days stale)
- Memory Consolidation: 3 days overdue
- 7 disabled cron jobs (old MELD experiments) — should clean up

### C. Config Improvements:
- Add DeepSeek, Mistral, Venice to fallback chain
- Add ElevenLabs for TTS
- maxConcurrent already bumped to 8 ✅
- Gemini key updated ✅

### D. Git Status:
- Last commit: `bbaefcb` (MELD reputation changes)
- Only 11 commits since workspace cleaned (Feb 20)
- Should commit current state (new crons, config changes, memory files)

## 5. Priority Actions

### Do Now (5 min each):
1. Add DeepSeek as model provider
2. Add Mistral as model provider  
3. Add Venice AI as model provider
4. Add ElevenLabs TTS config
5. Git commit current state

### Do This Week:
6. Run instinct engine scan (13 days overdue)
7. Run partner scorecard update (17 days overdue)
8. Add TTS to morning briefing cron
9. Clean up 7 disabled cron jobs
10. Test Venice AI for private inference use cases

### Decide:
11. Pick ONE product to build next (Voice Network vs Lineage Proofs vs Patent Validator)
12. MyClaw partnership — reach out?
13. Ring-2.5-1T via zenmux.ai — worth testing?
