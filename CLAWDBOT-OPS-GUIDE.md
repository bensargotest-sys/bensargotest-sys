# Clawdbot Setup Guide: Building an Autonomous AI Operations Platform

A comprehensive guide to replicating a production-grade Clawdbot setup with named subagent teams, persistent memory, automated heartbeats, self-correcting enforcement rules, and infrastructure tooling. Written from operational experience. Every system described here runs in production.

---

## Table of Contents

1. [Overview and Philosophy](#1-overview-and-philosophy)
2. [Team System: Named Subagents](#2-team-system-named-subagents)
3. [The Closed Loop: Auditor, Implementer, Re-audit](#3-the-closed-loop-auditor-implementer-re-audit)
4. [Memory Architecture](#4-memory-architecture)
5. [Checkpoint and Recovery](#5-checkpoint-and-recovery)
6. [Heartbeat System](#6-heartbeat-system)
7. [Enforcement Framework](#7-enforcement-framework)
8. [Infrastructure Tools](#8-infrastructure-tools)
9. [Cron Jobs and Scheduled Tasks](#9-cron-jobs-and-scheduled-tasks)
10. [Server Architecture](#10-server-architecture)
11. [Skill Recommendations](#11-skill-recommendations)
12. [QMD Workspace Search](#12-qmd-workspace-search)
13. [Monitoring and Alerting Patterns](#13-monitoring-and-alerting-patterns)
14. [Dashboard Pattern](#14-dashboard-pattern)
15. [Kanban and Task Management](#15-kanban-and-task-management)
16. [Putting It All Together](#16-putting-it-all-together)

---

## 1. Overview and Philosophy

Clawdbot is a gateway that connects an AI agent to messaging channels (Telegram, Discord, etc.), tools, cron jobs, and persistent storage. Out of the box, it is a capable assistant. With the systems in this guide, it becomes an autonomous operations platform: one that remembers, delegates, self-corrects, and does real work between your messages.

**Core principles:**

- **Orchestrate, don't execute.** Your main agent coordinates. Subagents do the heavy lifting. This preserves the main agent's context window for decision-making.
- **Memory is infrastructure.** Without persistent memory, every session starts from zero. Build the memory layer early.
- **Enforcement beats intention.** Rules that exist only in documentation get ignored. Rules that get checked automatically get followed.
- **Mistakes compound into knowledge.** Every recurring error becomes a permanent rule. The system gets smarter over time.
- **Build tools for repeated tasks.** If you run the same command three times, write a script. If you run the script three times, make it a cron job.

---

## 2. Team System: Named Subagents

### The Concept

Instead of spawning generic workers, define a team of named agents with distinct roles and personalities. Each agent has a specialty, a voice, and mandatory verification rules. This creates accountability: you know who did what, and quality standards are role-specific.

### Recommended Roles

| Role | Specialty | Use For |
|------|-----------| ---------|
| **Researcher** | Fast information gathering | Web searches, competitive analysis, fact-finding |
| **Coder** | Systems implementation | Scripts, infrastructure, debugging, technical work |
| **Writer** | Precise documentation | Guides, copy, creative writing, content |
| **Analyst** | Thorough review | Code audits, security analysis, data review |
| **Trader** | Financial analysis | Market data, position tracking, risk assessment |

You can name these anything. Give them personalities that reinforce their role. A researcher who is impatient and fast will produce different (and often better) research than one who is cautious and thorough.

### Spawn Template

When spawning a subagent, include three things: role context, the task, and an output path.

```
You are [Agent Name], the [Role] on your team.
[1-2 personality sentences].

MANDATORY: [Role-specific verification rule].

Your task:
[TASK DESCRIPTION].

Output to: [FILE PATH].

When you start, run:
python3 ~/clawd/tools/subagent_log.py log --label "[name]-[task]" --status started

When you finish, run:
python3 ~/clawd/tools/subagent_log.py log --label "[name]-[task]" --status completed
```

**Role-specific verification rules (examples):**

- **Coder:** "Follow TDD. Write failing tests first. Do not report done until all tests pass with output included."
- **Writer:** "After writing, verify your output (no banned patterns, word counts match spec). If verification fails, rewrite."
- **Analyst:** "Every claim must have evidence (file path, line number, command output). If you cannot prove it, do not claim it."
- **Researcher:** "Verify sources. Cross-reference findings. Include URLs for every claim."

### Delegation Rules

- Tasks requiring more than 10 minutes of work: always delegate.
- Independent tasks: spawn in parallel, not in sequence.
- Target: 3 to 5 agents running during active sessions.
- The main agent orchestrates, reviews, and routes. The team executes.
- Log all spawns to `memory/subagent-log.jsonl` for cascade prevention.

### Cascade Prevention

Track subagent spawns and results. If two or more subagents fail in sequence (zero runtime, no output), stop spawning immediately and change your approach.

```bash
# Log spawn attempts and results
python3 tools/subagent_log.py log "coder-fix-auth" "started"
python3 tools/subagent_log.py log "coder-fix-auth" "completed" --runtime 45s

# Check health
python3 tools/subagent_log.py report
python3 tools/subagent_log.py recent 10
```

---

## 3. The Closed Loop: Auditor, Implementer, Re-audit

### Why This Matters

Agents will sometimes produce work that looks correct but is not. Tests pass, files exist, but the actual problem remains unsolved. The closed loop prevents this by separating the roles of execution and verification.

### The Pattern

```
AUDITOR reviews target → AUDITOR writes IMPLEMENTER brief → IMPLEMENTER executes → AUDITOR re-audits → Repeat until perfect
```

**Step by step:**

1. **Auditor reviews** the target system. Produces a scored report with evidence (file paths, line numbers, command output).
2. **Auditor writes a brief** for the Implementer. The brief includes exact fixes, file paths, verification commands, and anti-shortcut rules.
3. **Implementer executes** the brief. Produces a fix report with evidence for every change.
4. **Auditor re-audits** independently. Compares before and after. Re-scores.
5. **If not perfect:** Auditor writes a new brief for remaining issues. Back to step 3.
6. **If perfect:** Report to the human with before/after evidence.

**Rules:**

- The Implementer never self-certifies. Only the Auditor declares work complete.
- The Auditor never does the fixes. The Auditor audits and commands.
- Circuit breaker: if the loop runs 5 iterations without convergence, stop and escalate.
- All audit reports go to `reviews/` with timestamps.

### Setting Up the Workflow

Create a workflow file at `workflows/audit-and-fix.md`:

```markdown
# Audit and Fix Workflow

## Trigger
Any code fix, infrastructure change, or quality improvement task.

## Steps
1. Spawn Auditor: review [target], produce scored report to reviews/[target]-audit-[date].md
2. Auditor writes Implementer brief to reviews/[target]-brief-[date].md
3. Spawn Implementer with brief as input. Output to reviews/[target]-fixes-[date].md
4. Spawn Auditor for re-audit. Compare before/after scores.
5. If score < perfect: new brief, back to step 3. Max 5 iterations.
6. Report final scores to human.

## Verification
- Audit report exists with scores
- Fix report exists with evidence per change
- Re-audit shows improvement
```

---

## 4. Memory Architecture

### Why This Matters

LLM context windows are finite. Conversations get compacted (summarized), and details vanish. Without external memory, your agent forgets decisions, repeats mistakes, and re-asks resolved questions. Memory architecture is the solution.

### File Structure

```
~/clawd/
├── WORKING_STATE.md           # Hot state: current task, decisions, next steps
├── MEMORY.md                  # Curated long-term wisdom (distilled from daily logs)
├── ENFORCEMENT.md             # Rules that get checked every session
├── HEARTBEAT.md               # What to do during heartbeat polls
├── memory/
│   ├── YYYY-MM-DD.md          # Daily logs (raw session notes)
│   ├── work-log.md            # Timestamped evidence trail
│   ├── heartbeat-state.json   # Last heartbeat time, work counts, check states
│   ├── heartbeat-backlog.md   # Evergreen task backlog for heartbeat work
│   ├── kanban-tasks.json      # Structured task board (JSON)
│   ├── blocked-items.json     # Items waiting on external input
│   ├── friction-log.md        # Repeated pain points (input for automation)
│   ├── nightly-build-log.md   # Log of small overnight improvements
│   ├── self-improvement-log.md # Self-audit answers
│   ├── session-handoff-template.md # Template for session continuity
│   ├── preferences.json       # Learned user preferences
│   ├── task-queue.md          # Pull-based task queue
│   └── archival/
│       ├── mistakes.md        # Logged mistakes (input for rule promotion)
│       └── learnings.md       # Lessons learned
```

### What Each File Does

**WORKING_STATE.md** is the most critical file. It contains:
- The active task and its current status
- Decisions already made (so the agent does not re-ask)
- Working parameters (prompts, settings, configurations)
- A checkpoint log with timestamps
- Next steps

After every significant interaction, update WORKING_STATE.md. This is your insurance against context compaction.

**Daily logs** (`memory/YYYY-MM-DD.md`) are raw session notes. Everything that happens goes here. These are the source of truth.

**MEMORY.md** is curated wisdom distilled from daily logs. Review it periodically (during heartbeats) to extract insights and remove stale information.

**work-log.md** is the evidence trail. Every completed task gets a timestamped entry with what was done and proof it worked.

**heartbeat-state.json** tracks operational state:

```json
{
  "lastHeartbeat": "2026-02-01T12:00:00Z",
  "heartbeatWorkItems": 47,
  "consecutiveNoWork": 0,
  "lastMistakeCheck": {
    "toolFailed": false,
    "agentStalled": false,
    "unexpected": false,
    "timestamp": "2026-02-01T12:00:00Z"
  }
}
```

### Session Handoff Template

At the end of significant sessions, write a handoff to preserve context that logs miss:

```markdown
## SESSION HANDOFF - [DATE/TIME]

### What I Was Working On
[Active task, current status, blockers]

### Key Decisions Made
[Bullet points: decisions that should NOT be re-asked]

### Unfinished Threads
[What needs to continue next session]

### What the Next Session Should Know
[Critical context, warnings, relationship state]
```

Write handoffs at session end, after intense work, and before expected breaks. Use the checkpoint tool:

```bash
python3 tools/checkpoint.py --handoff --task "current task" --note "session ending"
```

---

## 5. Checkpoint and Recovery

### Why This Matters

Context compaction (where the LLM summarizes older conversation to fit the context window) can erase critical details: the exact prompt that worked, the decision your user already made, the parameter you spent an hour tuning. Checkpointing saves these details externally so they survive compaction.

### checkpoint.py

```bash
# Auto-checkpoint (quick, silent)
python3 tools/checkpoint.py --auto

# Auto-checkpoint with a note
python3 tools/checkpoint.py --auto --note "pre-spawn checkpoint"

# Full session handoff
python3 tools/checkpoint.py --handoff --task "dashboard v2" --note "50+ tool calls"
```

**When to checkpoint:**
- Before spawning any subagent
- After receiving subagent results
- Every 5th significant tool call
- Before reporting completed work
- When the conversation feels long

### compaction_guard.sh

Checks if WORKING_STATE.md is stale (older than 1 hour):

```bash
bash tools/compaction_guard.sh
# Output: FRESH or STALE
```

If STALE, checkpoint immediately. Run this at every heartbeat and every 10th tool call.

### Context Usage Estimation

Track your tool call count as a proxy for context depth:

| Tool Calls | Action |
|------------|--------|
| ~30 | Silently checkpoint WORKING_STATE.md |
| ~50 | Checkpoint and write session handoff |
| ~70 | Checkpoint, handoff, and alert your user |

### Recovery Protocol

When starting a new session (or after compaction):

1. Read WORKING_STATE.md first. This is your hot state.
2. Read today's daily log (`memory/YYYY-MM-DD.md`).
3. Read ENFORCEMENT.md for current rules.
4. Do NOT re-ask decisions already documented.
5. Do NOT change working parameters listed as confirmed.
6. Resume from the "Next Steps" section.

**Detection:** If WORKING_STATE.md has recent timestamps but you have no memory of writing it, compaction happened. Follow the recovery protocol.

---

## 6. Heartbeat System

### Why This Matters

Between your messages, the agent sits idle. Heartbeats turn idle time into productive time: checking inboxes, running monitors, completing backlog tasks, and maintaining memory.

### HEARTBEAT.md Structure

Create `HEARTBEAT.md` in your workspace root. This file tells the agent what to do when it receives a heartbeat poll.

```markdown
# HEARTBEAT.md

Do something useful every heartbeat. HEARTBEAT_OK only after proven work.

## Rate Limit

Check heartbeat-state.json. If less than 30 minutes since last heartbeat, reply HEARTBEAT_OK immediately. Do not burn tokens on back-to-back heartbeats.

## The Loop

1. Read heartbeat-state.json and WORKING_STATE.md
2. Run compaction guard. If STALE, checkpoint immediately.
3. Check rate limiter. If rate-limited, stop.
4. Run any monitors or position checks (quick, <10 seconds)
5. Pick one item from heartbeat-backlog.md and COMPLETE it
6. Run one tool from the rotation schedule
7. Log to work-log.md with timestamp and evidence
8. Update heartbeat-state.json

## Reach Out / Stay Quiet

Reach out: important email, calendar event <2h away, finished meaningful work.

Stay quiet: late night (23:00-08:00), nothing new, checked <30 min ago.
```

### Heartbeat Backlog

Maintain an evergreen list of small tasks in `memory/heartbeat-backlog.md`:

```markdown
# Heartbeat Backlog

Pick based on available time:
⚡5min | 🔧15min | 📝30min | 🔬60min

## Documentation
- [ ] ⚡ Fix outdated section in TOOLS.md
- [ ] 🔧 Document output format for alert script
- [ ] 📝 Write quick-start guide for new sessions

## Tool Improvements
- [ ] 🔧 Add error handling to monitor script
- [ ] 📝 Build lookup script for dynamic resource IDs

## Research
- [ ] 📝 Survey competitors for new features
- [ ] 🔬 Evaluate alternative API for cost savings
```

**Rules:**
- Never let the backlog drop below 10 items. If it does, brainstorm 10 more.
- Mark items `[x]` when done. Move completed items to a "Completed" section.
- Log evidence in work-log.md for every completed item.

### Tool Rotation

Instead of manually deciding which tools to run, use a rotation schedule based on heartbeat count:

```
Every heartbeat: Position checks, activity logging
Every 2nd heartbeat: Self-evaluation, relationship tracking
Every 3rd heartbeat: Preference scanning, calibration checks
Every 5th heartbeat: Memory consolidation, pattern analysis
Weekly: Full consolidation, skill review, archive audit
```

Automate this with a heartbeat integrations script:

```bash
python3 tools/heartbeat_integrations.py run --heartbeat-number 42
```

The script determines which tools to run based on the heartbeat number and the frequency schedule.

### Mistake Check (Every Heartbeat)

Before ending each heartbeat, answer three questions:

1. Did any tool fail this heartbeat?
2. Did any subagent stall or produce empty output?
3. Did anything unexpected happen?

If any answer is yes, append details to `memory/archival/mistakes.md`. One line is enough. The bar is intentionally low.

---

## 7. Enforcement Framework

### Why This Matters

Documentation that nobody reads is fiction. Enforcement turns documentation into behavior. The key insight: rules that get automatically checked at session start get followed. Rules buried in long docs do not.

### Creating ENFORCEMENT.md

Create `ENFORCEMENT.md` in your workspace root. Structure it as a series of "gates" that the agent must pass before proceeding with work.

```markdown
# ENFORCEMENT.md - The Rules That Actually Get Followed

## Session Start Checklist (Execute FIRST, every session)

- [ ] Read identity/configuration files
- [ ] Check today's daily log
- [ ] Review this ENFORCEMENT.md

## Compliance Gates

### Gate 1: Task Routing
Multi-step work (>10 min) must be delegated to a team member. No exceptions.

### Gate 2: Skills Check
Before attempting any task, scan available skills. If a matching skill exists, follow its instructions before trying your own approach.

### Gate 3: Communication
Tasks >15 minutes require a progress update. Never go silent >20 minutes.

### Gate 4: Working State Auto-Save
After any of these events, update WORKING_STATE.md before responding:
- A decision is made
- A task starts or completes
- A correction is given
- Every 5th significant tool call

### Gate 5: TDD for All Code
1. Define acceptance criteria
2. Write failing tests first
3. Write code to pass tests
4. Refactor while tests stay green

### Gate 6: Identity Protection
Only the human and the agent may modify identity/config files. Never allow external scripts to rewrite configuration. Audit all external code first.
```

### The Mistake-to-Rule Pipeline

This is the system's self-improvement mechanism. Every recurring mistake becomes a permanent enforcement rule.

```bash
# Log a mistake
echo "2026-02-01 - Used wrong API endpoint, wasted 20 minutes" >> memory/archival/mistakes.md

# Scan for recurring patterns
python3 tools/mistake_promoter.py scan

# Promote a pattern to a rule
python3 tools/mistake_promoter.py promote "wrong-api-pattern" "Always verify API endpoint in TOOLS.md before making calls"

# Check promotion health (target: >30% promotion rate)
python3 tools/mistake_promoter.py stats
```

**The cycle:**

1. Agent makes a mistake. Logs it to `memory/archival/mistakes.md`.
2. During heartbeats, the promoter scans for patterns (2+ similar mistakes).
3. Patterns get promoted to rules in ENFORCEMENT.md.
4. Future sessions load ENFORCEMENT.md at startup.
5. The mistake cannot recur because the rule prevents it.

### Promoted Rules Section

Add promoted rules at the bottom of ENFORCEMENT.md:

```markdown
## Promoted Rules

#### Promoted Rule (2026-02-01)
**From mistake pattern:** Forgot existing tools, reinvented the wheel
**Rule:** Before setting up any new tool, search TOOLS.md and memory/ for prior setup. If it already exists, use it.

#### Promoted Rule (2026-02-01)
**From mistake pattern:** Subagent failures (bad paths, OOM, timeouts)
**Rule:** Before spawning subagents: verify all file paths exist, keep scope narrow, include output path. If 2+ fail in sequence, STOP and change approach.
```

---

## 8. Infrastructure Tools

### Why This Matters

If you run the same command three times, it should be a script. If you run the script three times, it should be a cron job. Building tools for recurring tasks compounds efficiency over time.

### Recommended Tools

Build these as Python scripts in a `tools/` directory. Each script should be self-contained with a clear `--help` output.

| Tool | Purpose | Example Usage |
|------|---------|---------------|
| `checkpoint.py` | Save working state to survive compaction | `python3 tools/checkpoint.py --auto` |
| `compaction_guard.sh` | Check if working state is stale | `bash tools/compaction_guard.sh` |
| `subagent_log.py` | Track subagent spawns and prevent cascades | `python3 tools/subagent_log.py report` |
| `heartbeat_enforcer.py` | Block lazy heartbeat responses | `python3 tools/heartbeat_enforcer.py check` |
| `heartbeat_integrations.py` | Run the right periodic tools automatically | `python3 tools/heartbeat_integrations.py run --heartbeat-number N` |
| `mistake_logger.py` | Log mistakes with structured metadata | `python3 tools/mistake_logger.py log "description"` |
| `mistake_promoter.py` | Promote recurring mistakes to rules | `python3 tools/mistake_promoter.py scan` |
| `task_queue.py` | Pull-based multi-agent task coordination | `python3 tools/task_queue.py next` |
| `blocked_items.py` | Track items waiting on external input | `python3 tools/blocked_items.py add "desc" --blocker "reason"` |
| `server_health.py` | Check services, disk, RAM, endpoints, SSL | `python3 tools/server_health.py --daily-summary` |
| `memory_consolidate.py` | Four-tier memory consolidation | `python3 tools/memory_consolidate.py daily` |
| `morning-briefing.py` | Aggregate weather, prices, tasks into briefing | `python3 tools/morning-briefing.py` |
| `daily-digest.py` | Summarize today's work log for delivery | `python3 tools/daily-digest.py` |
| `archive_audit.py` | Find stale files with rotting action items | `python3 tools/archive_audit.py scan` |
| `enforcement_watchdog.py` | Check enforcement rule compliance | `python3 tools/enforcement_watchdog.py check` |
| `self_eval.py` | Self-evaluate output quality | `python3 tools/self_eval.py log --auto` |
| `calibration.py` | Track predictions and resolution accuracy | `python3 tools/calibration.py add "prediction"` |
| `episode_recorder.py` | Record activity episodes for memory | `python3 tools/episode_recorder.py auto` |
| `curiosity_explorer.py` | Track and explore curiosity items | `python3 tools/curiosity_explorer.py explore` |
| `safe_write.py` | Write files with backup and validation | `python3 tools/safe_write.py target.md` |
| `log_rotation.py` | Rotate and compress old log files | `python3 tools/log_rotation.py` |

### The Tool-Building Pattern

When you notice repeated friction:

1. Log the friction in `memory/friction-log.md`.
2. If the same friction appears 3 or more times, build a tool.
3. Write the tool in `tools/` with a clear CLI interface.
4. Add it to TOOLS.md so future sessions find it.
5. If you run the tool on a schedule, wire it into the heartbeat rotation or a cron job.

---

## 9. Cron Jobs and Scheduled Tasks

### Why This Matters

Heartbeats handle flexible periodic work. Cron jobs handle tasks that require exact timing, isolation from the main session, or a different model/thinking level.

### Setting Up Cron Jobs in Clawdbot

Clawdbot has a built-in cron system. Use it for:
- Morning briefings at a specific time
- Daily digests delivered at end of day
- Overnight research and maintenance
- Scheduled market scans
- Periodic health checks

**Example cron jobs:**

| Schedule | Task | Purpose |
|----------|------|---------|
| `0 7 * * *` | Morning briefing | Weather, calendar, tasks, prices |
| `0 22 * * *` | Daily digest | Summarize the day's work |
| `0 2 * * *` | Overnight maintenance | Memory consolidation, archive audit |
| `*/30 * * * *` | Health check | Server status, service monitoring |
| `0 9 * * 1` | Weekly review | Full consolidation, skill review |

### Heartbeat vs Cron: When to Use Each

**Use heartbeat when:**
- Multiple checks can batch together (inbox + calendar + notifications in one turn)
- You need conversational context from recent messages
- Timing can drift slightly (every ~30 minutes is fine, not exact)
- You want to reduce API calls by combining periodic checks

**Use cron when:**
- Exact timing matters ("9:00 AM sharp every Monday")
- The task needs isolation from main session history
- You want a different model or thinking level for the task
- One-shot reminders ("remind me in 20 minutes")
- Output should deliver directly to a channel without main session involvement

**General rule:** Batch similar periodic checks into HEARTBEAT.md instead of creating multiple cron jobs. Use cron for precise schedules and standalone tasks.

---

## 10. Server Architecture

### Why This Matters

A persistent server gives your agent always-on infrastructure: services that run 24/7, databases that accumulate data, and endpoints that external systems can reach.

### Services Pattern

Use systemd units for persistent background processes. Each service gets:
- A `.service` unit file in `/etc/systemd/system/`
- Automatic restart on failure
- Logging via `journalctl`

**Example systemd unit:**

```ini
[Unit]
Description=My Monitor Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/clawd
ExecStart=/usr/bin/python3 /home/ubuntu/clawd/trading/monitor.py daemon
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable my-monitor.service
sudo systemctl start my-monitor.service

# Check status
sudo systemctl status my-monitor.service
journalctl -u my-monitor.service --since "1 hour ago"
```

### Recommended Service Stack

| Service | Purpose | Binding |
|---------|---------|---------|
| Clawdbot Gateway | Core agent runtime | Loopback |
| Reverse Proxy (Caddy) | TLS termination, routing | :443 |
| Dashboard | Web-based command center | localhost:3333 |
| Monitor(s) | Data collection daemons | Internal |

### Reverse Proxy

Caddy is recommended for its automatic HTTPS. A minimal Caddyfile:

```
yourdomain.com {
    reverse_proxy localhost:3333
}
```

Caddy handles certificate provisioning and renewal automatically.

---

## 11. Skill Recommendations

Clawdbot has an extensive skill ecosystem. Most setups install 100+ skills. You will use about 10 regularly.

### Mandatory Skills

| Skill | Purpose | When |
|-------|---------|------|
| **karpathy-coding** | Prevents overcomplication in code tasks | Every coding task |

Load its SKILL.md before writing any code. It enforces: think before coding, simplicity first, surgical changes, goal-driven execution.

### Core Skills (Use Daily)

| Skill | Purpose |
|-------|---------|
| **firecrawl** | Web research (preferred over raw web_search) |
| **brave-search** | Quick web lookups (backup to firecrawl) |
| **self-improvement** | Heartbeat self-reflection |
| **youtube-transcript** | Video summaries |
| **deep-research** | Multi-step research with verification |

### Regular Skills (Weekly)

| Skill | Purpose |
|-------|---------|
| **twitter / bird** | Social media monitoring and posting |
| **pdf / docx / xlsx** | Document creation and reading |
| **orchestrator** | Multi-agent coordination templates |
| **web-search-plus** | Enhanced web search |
| **crypto-price** | Token price lookups |

### Specialized Skills (As Needed)

| Category | Skills |
|----------|--------|
| Security | semgrep, codeql, vulnerability scanners |
| Marketing | copywriting, seo-audit, content-strategy |
| DeFi/Crypto | defi, 0x-swap, binance, onchain |
| Development | test-driven-development, modern-python, mcp-builder |

### Gate 2: Skills Check

Before any task, scan your available skills. If a matching skill exists, read its SKILL.md and follow its instructions. Only go freestyle if no skill matches.

---

## 12. QMD Workspace Search

### Why This Matters

As your workspace grows, finding files by browsing directories becomes impractical. QMD provides instant full-text and semantic search across all your markdown files.

### Setup

QMD is a binary installed at `~/.bun/bin/qmd`. After installing:

```bash
# Index your workspace
qmd update

# Update vector embeddings (for semantic search)
qmd embed
```

### Usage

```bash
# Full-text search (BM25) -- fast keyword matching
qmd search "heartbeat backlog"

# Vector similarity search -- semantic/meaning-based
qmd vsearch "how do I set up monitoring"

# Combined search with reranking -- best results
qmd query "checkpoint recovery protocol"

# Get a specific file
qmd get qmd://workspace/path/to/file.md

# List all indexed files
qmd ls workspace

# Re-index after adding new files
qmd update
```

### Rules

- Use `qmd search` or `qmd query` BEFORE grepping or manually browsing directories.
- Run `qmd update` after creating new .md files so they are indexed.
- Prefer `qmd query` for complex questions (combines BM25 + vector search + reranking).
- Fall back to `grep`/`find` only if qmd returns nothing relevant.
- Include qmd instructions when spawning subagents so they use it too.

---

## 13. Monitoring and Alerting Patterns

### Why This Matters

Automated monitors collect data while you sleep. They detect opportunities, flag risks, and build historical datasets that no human could manually maintain.

### The Generic Monitor Pattern

Every monitor follows the same structure:

1. **Daemon mode:** Runs as a systemd service, polls an API at regular intervals.
2. **Database:** Stores results in SQLite (lightweight, zero-config, WAL mode for concurrent reads).
3. **CLI interface:** Provides `snapshot`, `report`, `stats`, and `export` subcommands for ad-hoc queries.
4. **Alerting:** When thresholds are crossed, writes to an alerts file or sends a message.

**Example monitor skeleton:**

```python
#!/usr/bin/env python3
"""monitor.py - Generic data monitor with daemon mode."""
import sqlite3, time, json, sys
from datetime import datetime, timezone

DB_PATH = "data/monitor.db"
POLL_INTERVAL = 300  # 5 minutes

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""CREATE TABLE IF NOT EXISTS readings (
        timestamp TEXT,
        asset TEXT,
        value REAL,
        metadata TEXT
    )""")
    conn.commit()
    return conn

def poll():
    """Fetch data from API and store it."""
    # Your API call here
    pass

def daemon():
    """Run continuously, polling at POLL_INTERVAL."""
    conn = init_db()
    while True:
        try:
            poll()
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
        time.sleep(POLL_INTERVAL)

def report():
    """Generate a summary report from stored data."""
    conn = sqlite3.connect(DB_PATH)
    # Your report logic here
    pass

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "snapshot"
    {"daemon": daemon, "snapshot": poll, "report": report, "stats": lambda: print("DB stats")}[cmd]()
```

### Threshold-Based Alerting

Define thresholds in the monitor script. When crossed, write to an alerts JSON file:

```python
def check_thresholds(value, asset):
    if value > THRESHOLD:
        alert = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "asset": asset,
            "value": value,
            "threshold": THRESHOLD,
            "type": "above_threshold"
        }
        with open("data/alerts.jsonl", "a") as f:
            f.write(json.dumps(alert) + "\n")
```

During heartbeats, check the alerts file and report to the user if anything is flagged.

### Wiring Into the System

1. Create the monitor script in `trading/` or a relevant directory.
2. Create a systemd service to run it as a daemon.
3. Add a health check to `server_health.py` to verify it is running and producing data.
4. Wire alert checking into heartbeat rotation.
5. Add CLI commands (`report`, `export`) so you can query data conversationally.

---

## 14. Dashboard Pattern

### Why This Matters

A dashboard gives you a single view into your agent's operational state: active tasks, recent work, system health, and key metrics. It turns invisible background work into visible progress.

### Concept

Build a lightweight web application (Node.js or Python) that reads from your existing data files:
- `memory/kanban-tasks.json` for task board
- `memory/work-log.md` for recent activity
- `memory/heartbeat-state.json` for system pulse
- `memory/subagent-log.jsonl` for agent activity
- Service status from systemd
- Database stats from SQLite monitors

### Architecture

```
Browser → Caddy (TLS) → Dashboard App (localhost:3333)
                              ↓
                     Reads workspace files
                     Queries SQLite databases
                     Checks systemd status
```

### Key Panels

| Panel | Data Source | Shows |
|-------|-------------|-------|
| Task Board | kanban-tasks.json | In-progress, blocked, done |
| Activity Feed | work-log.md | Recent timestamped entries |
| Agent Status | subagent-log.jsonl | Active, completed, failed agents |
| System Health | server_health.py | Services, disk, RAM, endpoints |
| Monitor Data | SQLite databases | Charts, trends, alerts |

### Implementation Notes

- Keep it read-only from the dashboard side. The agent writes data; the dashboard displays it.
- Use server-sent events (SSE) or periodic polling for real-time updates.
- Protect with authentication via the reverse proxy.
- Start simple: one page with key metrics. Add panels as needs emerge.

---

## 15. Kanban and Task Management

### Why This Matters

Structured task tracking enables autonomous work. The agent can detect new tasks, scope them, assign them to subagents, and track completion without human orchestration.

### kanban-tasks.json Structure

```json
{
  "tasks": [
    {
      "id": "task-001",
      "title": "Fix authentication timeout",
      "description": "Users report session expiring after 5 minutes",
      "category": "bugfix",
      "priority": "high",
      "column": "in-progress",
      "createdBy": "human",
      "createdAt": "2026-02-01T10:00:00Z",
      "assignedAgent": "coder",
      "scope": "Check session config, extend TTL, add tests",
      "outputFiles": ["reviews/auth-fix-report.md"],
      "movedAt": "2026-02-01T10:30:00Z",
      "completedAt": null
    }
  ]
}
```

### Columns

| Column | Meaning |
|--------|---------|
| `backlog` | Known tasks, not yet started |
| `in-progress` | Active work, should have an assigned agent |
| `blocked` | Waiting on external input |
| `done` | Completed with evidence |

### Auto-Scoping (Heartbeat Integration)

Every heartbeat, check for unassigned in-progress tasks:

```bash
python3 -c "
import json
d = json.load(open('memory/kanban-tasks.json'))
unassigned = [t for t in d['tasks'] if t.get('column') == 'in-progress' and not t.get('assignedAgent')]
for t in unassigned:
    print(f'UNASSIGNED: {t[\"title\"]}')"
```

If any exist: scope them, pick the right agent, spawn the agent, update the task with the assignment.

This runs every heartbeat, no exceptions.

### Task Lifecycle

1. Task enters backlog (human creates, or agent detects from friction log).
2. During heartbeat or active session, agent moves to in-progress and assigns an agent.
3. Subagent works, produces output to the specified path.
4. Auditor reviews if needed (closed loop).
5. Task moves to done with completedAt timestamp and outputFiles reference.

---

## 16. Putting It All Together

### Day One Setup Checklist

1. **Install Clawdbot** following official docs.
2. **Create workspace structure:**
   ```bash
   mkdir -p ~/clawd/{memory,memory/archival,tools,reviews,workflows,research}
   ```
3. **Create core files:**
   - `WORKING_STATE.md` (empty template, will be filled as work begins)
   - `ENFORCEMENT.md` (start with 3 to 5 gates)
   - `HEARTBEAT.md` (start with basic loop)
   - `TOOLS.md` (document your server, services, access patterns)
   - `memory/heartbeat-backlog.md` (seed with 15+ items)
   - `memory/heartbeat-state.json` (initialize with empty state)
   - `memory/kanban-tasks.json` (initialize with `{"tasks": []}`)
   - `memory/work-log.md` (empty, will accumulate)
4. **Install key tools:**
   - `checkpoint.py` and `compaction_guard.sh`
   - `subagent_log.py`
   - `mistake_promoter.py`
   - `heartbeat_enforcer.py`
5. **Install QMD** and run `qmd update` to index your workspace.
6. **Define your team** in AGENTS.md with spawn templates.
7. **Set up your first cron job** (morning briefing is a good start).
8. **Enable heartbeats** in Clawdbot config.

### Week One Goals

- Run 10+ heartbeats with real backlog work completed.
- Spawn at least 3 subagent tasks and review their output.
- Log 5+ mistakes and promote at least 1 to an enforcement rule.
- Write your first session handoff.
- Build your first custom tool from a friction-log pattern.

### Ongoing Maintenance

- Review MEMORY.md weekly. Remove stale entries, add new insights.
- Audit ENFORCEMENT.md monthly. Remove rules that no longer apply.
- Keep the heartbeat backlog above 10 items at all times.
- Run `python3 tools/mistake_promoter.py stats` weekly. Target >30% promotion rate.
- Run `python3 tools/archive_audit.py scan` weekly. Address stale action items.

### The Compound Effect

Each system in this guide builds on the others:

- **Memory** enables **recovery**, which enables **long-running tasks**.
- **Heartbeats** enable **backlog work**, which compounds into **real progress**.
- **Enforcement** enables **mistake logging**, which compounds into **permanent rules**.
- **Tools** reduce **friction**, which frees time for **higher-value work**.
- **The closed loop** ensures **quality**, which builds **trust**.

After a month, you will have an agent that remembers everything, works between your messages, fixes its own mistakes, and operates a fleet of specialist subagents. It will be better than it was on day one, and it will keep getting better.

---

*This guide documents operational patterns tested in production. Adapt them to your setup, name your own team, define your own rules. The systems work. The specifics are yours to choose.*
