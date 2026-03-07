# OpenClaw Autonomous Agent Setup Guide

A detailed blueprint for building a fully autonomous AI agent system on OpenClaw. Updated 2026-02-21 to reflect actual production configuration.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                 HUMAN (Telegram)                     │
│                      ↕                               │
│              OpenClaw Gateway (Docker)                │
│                      ↕                               │
│  ┌─────────────────────────────────────────────────┐ │
│  │ TIER 1: Orchestrator (Claude Opus 4.6)          │ │
│  │  - Main session, direct chat                    │ │
│  │  - Reads all context files on boot              │ │
│  │  - Spawns sub-agents, manages cron              │ │
│  ├─────────────────────────────────────────────────┤ │
│  │ TIER 2: Team Agents (Grok 4.1 Fast)            │ │
│  │  - Research, analysis, review cron jobs         │ │
│  │  - Morning briefing, security audit, intel      │ │
│  │  - Plan, review, synthesize (FREE via xAI)     │ │
│  ├─────────────────────────────────────────────────┤ │
│  │ TIER 3: Swarm (Gemini 2.0 Flash)               │ │
│  │  - Bulk execution workers (parallel spawning)   │ │
│  │  - Simple cron jobs (health checks, backups)    │ │
│  │  - Fire-and-forget tasks (FREE via Google)     │ │
│  │  - maxConcurrent: 8, auto-archive 30 min       │ │
│  └─────────────────────────────────────────────────┘ │
│                      ↕                               │
│  ┌──────────┐ ┌──────────┐ ┌───────────────────────┐│
│  │ Memory   │ │  Intel   │ │ Tools & Scripts       ││
│  │ System   │ │ Pipeline │ │ (Python, bash)        ││
│  └──────────┘ └──────────┘ └───────────────────────┘│
└─────────────────────────────────────────────────────┘
```

**Host:** Hostinger VPS, 76.13.46.217, Docker container, 4GB RAM
**Note:** Nesting (T2→T3→T4) is NOT supported by OpenClaw. Architecture is fan-out: T1 spawns T2/T3 in parallel.

---

## Model Routing

| Tier | Role | Model | Cost | Use |
|------|------|-------|------|-----|
| T1 Orchestrator | `main` session | Claude Opus 4.6 | $$$ | Human chat, planning, spawning |
| T2 Team Agents | Cron (isolated) | Grok 4.1 Fast (xAI) | FREE | Research, analysis, reviews, briefings |
| T3 Swarm | Workers + cron | Gemini 2.0 Flash (direct) | FREE | Execution, health checks, file ops |

### Cron Job → Tier Assignment
| T2 (Grok — reasoning) | T3 (Gemini — execution) |
|---|---|
| Weekly Full Review | MELD Health Check (hourly) |
| Daily Security Audit (02:00) | Total Recall Observer (every 2h) |
| Overnight Builder (02:00) | Daily Cost Tracker (23:00) |
| Morning Briefing (08:00) | Memory Consolidation (23:00) |
| Macro Intel Scanner (3x daily) | Episode Recorder (22:30) |
| Daily Digest (22:00) | Self-Improvement (06:00) |
| Self-Review (21:00) | Weekly Bloat Health Check |
| Instinct Evolution (weekly) | Weekly Backup Rotation |

---

## Core Files

| File | Purpose |
|------|---------|
| `AGENTS.md` | Boot sequence, safety rules, group chat behavior, heartbeat protocol |
| `SOUL.md` | Personality, values, decision-making, autonomy protocol |
| `USER.md` | Human's profile, preferences, projects |
| `TOOLS.md` | Local tool registry, SSH configs, API endpoints |
| `IDENTITY.md` | Quick-reference identity card |
| `HEARTBEAT.md` | Checklist for heartbeat system |
| `MEMORY.md` | Curated long-term memory (main session only) |

### Boot Sequence
```
1. Read SOUL.md → know who you are
2. Read USER.md → know who you serve
3. Read memory/YYYY-MM-DD.md (today + yesterday) → recent context
4. If main session: Read MEMORY.md → long-term context
```

---

## Memory System

### Layer 1: Daily Memory Files
- **Location:** `memory/YYYY-MM-DD.md`
- **Written by:** Cron + agent during conversations
- **Retention:** Indefinite (archived weekly)

### Layer 2: Long-Term Memory (MEMORY.md)
- **Written by:** Agent during main sessions + consolidation
- **Security:** Only loaded in 1:1 sessions, never in groups

### Layer 3: Semantic Memory (Voyage AI)
- **Backend:** Voyage AI embeddings + `memory_search`/`memory_get` tools
- **Auto-indexed:** MEMORY.md + memory/*.md files

### Layer 4: Total Recall (Autonomous Observer)
- **Cron:** Every 2 hours (isolated session)
- **Reads:** Last 20 messages from main session
- **Writes:** Compressed observations to `memory/observations.md`
- **Priority:** 🔴 HIGH / 🟡 MEDIUM / 🟢 LOW

### Layer 5: Episode Recorder
- **Cron:** 10:30pm daily
- **Writes:** Structured episode records (type, participants, topics, decisions)

### Layer 6: Instinct Learning
- **Script:** `tools/instincts/instinct_engine.py`
- **Cron:** Weekly evolution
- **Purpose:** Develops patterns from behavior over time

---

## Heartbeat System

OpenClaw sends heartbeat polls at configured intervals. Agent runs through HEARTBEAT.md checklist.

- Something needs attention → ONE message to human
- Nothing → `HEARTBEAT_OK` (suppressed)

### Checks Per Heartbeat
- Cron health, service health, compaction risk
- Self-accountability (partner scorecard)

### Heartbeat vs Cron
| Use Heartbeat When | Use Cron When |
|---|---|
| Multiple checks batch together | Exact timing matters |
| Need conversational context | Task needs session isolation |
| Timing can drift | Want a different model |

---

## Cron Job Orchestration

We run **15 cron jobs**, all on `xai/grok-4-1-fast-non-reasoning`.

### Current Jobs

| Job | Schedule | Purpose |
|-----|----------|---------|
| MELD Health Check | Hourly | Node health monitoring |
| Total Recall Observer | Every 2h | Memory safety net |
| Auto-archive sessions | Every 2h | Clean up idle sessions |
| Morning Briefing | 8:00 AM | Daily priorities + health |
| Daily Active Tasks Sync | 6:00 AM | Update active-tasks.md |
| Macro Intel Scanner | 8/14/20 UTC | Geopolitical + economic research |
| Daily Security Audit | 2:00 AM | Security scan |
| Self-Review | 9:00 PM | Self-accountability |
| Daily Digest | 10:00 PM | Day summary to Telegram |
| Daily Cost Tracker | 11:00 PM | Monitor API spend |
| Instinct Evolution | Sunday 10:30 AM | Weekly pattern learning |
| Weekly Full Review | Sunday midnight | Memory consolidation + review |
| Weekly Backup Rotation | Sunday 3:00 AM | Cleanup old backups |
| Weekly Bloat Health | Monday 9:00 AM | Disk/workspace health |
| Workspace Backup | Every 12h | Git backup |

### Cost: ~$21/month (all on Grok Fast)

---

## Multi-Agent Configuration

### openclaw.json agents config
```json
{
  "agents": {
    "defaults": {
      "subagents": {
        "maxConcurrent": 8,
        "archiveAfterMinutes": 30,
        "model": "openrouter/google/gemini-2.0-flash-001"
      }
    },
    "list": [
      {
        "id": "main",
        "name": "main",
        "subagents": { "allowAgents": ["main", "worker"] }
      },
      {
        "id": "worker",
        "name": "worker",
        "subagents": { "allowAgents": ["worker"] }
      }
    ]
  },
  "tools": {
    "subagents": {
      "tools": {
        "deny": ["gateway", "cron", "session_status"]
      }
    }
  }
}
```

### Spawning Pattern (fan-out)
```
# T1 spawns 3 workers in parallel
sessions_spawn(task="Research topic A", agentId="worker")
sessions_spawn(task="Research topic B", agentId="worker")
sessions_spawn(task="Research topic C", agentId="worker")
# Results announce back as they complete
```

### Platform Limitations
- **No nesting:** Workers cannot spawn sub-workers (OpenClaw hard-blocks `sessions_spawn` from sub-agent sessions)
- **No direct Gemini API:** OpenClaw has an internal bug with Google's Gemini API; route through OpenRouter instead
- **Tool restrictions:** Workers are denied `gateway`, `cron`, `session_status` for safety

---

## Intelligence Pipeline

```
8:00 AM  │ Morning Briefing: priorities + health
8/14/20  │ Macro Intel Scanner (3x daily)
         │  → intel/GEO-RISK.json, macro-signals.json, DAILY-INTEL.md
9:00 PM  │ Self-Review: accountability check
10:00 PM │ Daily Digest: summary to Telegram
11:00 PM │ Cost Tracker: monitor spend
2:00 AM  │ Security Audit: overnight scan
```

### Intel File Structure
```
intel/
├── GEO-RISK.json       # Level: GREEN/YELLOW/RED
├── macro-signals.json   # Economic indicators
└── DAILY-INTEL.md       # Running intel log
```

---

## Custom Tooling

| Tool | Purpose |
|------|---------|
| `tools/cron-health-check.py` | Detect stuck/failing cron jobs |
| `tools/cron-log/cli.py` | Query cron run history |
| `tools/compaction/compaction_advisor.py` | Monitor context window |
| `tools/retrieval/retrieval_engine.py` | Build context for sub-agents |
| `tools/eval-harness/eval.py` | Define and run evaluations |
| `tools/partner-scorecard.py` | Self-accountability metrics |
| `tools/instincts/instinct_engine.py` | Pattern learning |
| `tools/meld-health-check.sh` | MELD node monitoring |
| `tools/backup.sh` | Workspace backup |
| `tools/daily_digest.py` | Daily summary generation |

---

## Health Monitoring

- **Gateway:** `openclaw gateway status`
- **Cron:** `python3 tools/cron-health-check.py`
- **Cron logs:** `python3 tools/cron-log/cli.py recent`
- **Bloat:** `bash tools/bloat_health_check.sh`

### Alerting
All alerts via Telegram: service outages, cron failures (3+), security issues.

---

## How to Replicate

### Step 1: Core Files
Create AGENTS.md, SOUL.md, USER.md, TOOLS.md, HEARTBEAT.md, MEMORY.md

### Step 2: Memory Structure
```bash
mkdir -p memory intel tools/cron-log data
```

### Step 3: Model Routing
- Main: Best model (Opus/GPT-5 class)
- Workers: Cheapest via OpenRouter (Gemini Flash ~$0.001/call)
- Cron: Cheap fast model (Grok Fast ~$0.70/day)

### Step 4: Cron Jobs (start small)
Week 1: Total Recall + Daily Digest
Week 2: Health checks + security
Week 3: Intel pipeline
Week 4: Self-improvement + overnight builder

### Key Principles
1. Files are memory — write everything down
2. Cheap models for execution, expensive for thinking
3. One message max per alert
4. Act first, ask second (within defined boundaries)
5. MEMORY.md only in direct sessions (security)
6. Self-accountability — track performance metrics

---

## Summary Stats
- **Cron jobs:** 15 running (all Grok Fast)
- **Memory layers:** 6 (daily, MEMORY.md, Voyage AI, Total Recall, episodes, instincts)
- **Models:** 2 tiers (Opus orchestrator, Gemini Flash workers)
- **Worker swarm:** Fan-out via `worker` agent, Gemini Flash via OpenRouter
- **Alert channel:** Telegram
- **Monthly cost:** ~$21 cron + ~$0.001/worker call + Opus for main session

---

*Built on [OpenClaw](https://github.com/openclaw/openclaw). Docs at [docs.openclaw.ai](https://docs.openclaw.ai). Community at [discord.com/invite/clawd](https://discord.com/invite/clawd).*
