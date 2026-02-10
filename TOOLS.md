---
summary: "Workspace template for TOOLS.md"
read_when:
  - Bootstrapping a workspace manually
---

# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## VPS Infrastructure

### Server Details
- **Provider:** Hostinger
- **IP:** 76.13.46.217
- **Hostname:** srv1353853
- **Container:** openclaw-khc5-openclaw-1
- **OS:** Linux 6.8.0-94-generic (x64)
- **Node:** v22.22.0
- **Architecture:** x64
- **Timezone:** UTC

### Workspace
- **Path:** `/data/.openclaw/workspace`
- **Structure:**
  - `memory/` - State files, logs, backlog, mistakes
  - `tools/` - Automation scripts (Python/Bash)
  - `workflows/` - Agent templates, task patterns
  - `reviews/` - Retrospectives, audits
  - `tsp/` - Trust Score Protocol project

### Firewall (UFW)
- Port 22 (SSH): ALLOW
- Port 59415 (OpenClaw): DENY
- Port 63362 (OpenClaw): DENY
- Default: DENY incoming
- **Status:** Active and enforced
- **Config location:** N/A (host-level, check with `ufw status`)

### Backup Location
- **Workspace backups:** `checkpoints/`
- **Host backups:** `/root/openclaw-backups/` (root-only, 600)
- **TSP backups:** `tsp/backups/` (PostgreSQL dumps)
- **Scripts:** `tools/backup.sh`, `tools/restore.sh`, `tools/checkpoint.py`
- **Note:** Host-level backup.sh requires elevated permissions

### Resource Limits
- **Container context:** No direct host access
- **Docker commands:** Not available from inside container
- **UFW/firewall:** Host-level only (container can't check directly)
- **Root filesystem:** Read-only for `/root` from container

## Telegram Bot

### Configuration
- **Bot Token:** 8251452268:AAHcoKAKLgzjWciLURGX7SOr87sA2RWPy64
- **Username:** @YourBotName (check with @BotFather)
- **DM Policy:** Pairing required
- **Group Policy:** Allowlist
- **Stream Mode:** Partial
- **Session Scope:** per-channel-peer (isolated context per user)

### Paired Users
- User ID: 8417397353 (approved)
- User ID: 428513734 (approved)

### Security
- Telegram-only mode active (all other channels disabled)
- Control UI bound to localhost (no external access)
- HTTP auth disabled (insecure auth removed)
- Outbound connections only (no inbound ports needed)

### Commands
- Check status: `openclaw status`
- View config: `openclaw config show channels.telegram`
- List cron jobs: `openclaw cron list`
- Security audit: `openclaw security audit --deep`

## Workspace Tools

All tools located in `/data/.openclaw/workspace/tools/`

### Core Infrastructure
- **backup.sh** - Docker volume backup (requires host execution)
- **restore.sh** - Restore from backup archive
- **checkpoint.py** - Auto-checkpoint for session compaction
- **compaction_guard.sh** - Check if checkpoint needed (FRESH/STALE)

### Heartbeat & Monitoring
- **heartbeat_enforcer.py** - Rate limiting + work logging
  - `check` - Check if heartbeat allowed (PROCEED/RATE_LIMITED)
  - `log <message>` - Log work completion
- **server_health.py** - VPS health monitoring (disk, memory, load)
- **morning_briefing.py** - Generate morning status report
- **daily_digest.py** - Generate end-of-day summary

### Task Management
- **task_queue.py** - Pull-based task coordination
  - `add <title> <desc>` - Add task to queue
  - `claim <agent_id>` - Claim next task
  - `complete <id> <result>` - Mark done
  - `list` - Show all tasks
- **blocked_items.py** - Track blockers
  - `add <task> <blocker>` - Log new blocker
  - `resolve <id> <resolution>` - Mark resolved
  - `list` - Show active blockers
  - `summary` - Statistics

### Quality & Learning
- **mistake_logger.py** - Log mistakes and lessons
- **mistake_promoter.py** - Promote mistakes to documentation
- **subagent_log.py** - Track subagent spawns and results

### Usage Patterns
```bash
# Morning routine
python3 tools/morning_briefing.py

# Before work
python3 tools/heartbeat_enforcer.py check
bash tools/compaction_guard.sh

# During work
python3 tools/task_queue.py claim main-agent
python3 tools/blocked_items.py add "Task X" "Missing API key"

# After work
python3 tools/heartbeat_enforcer.py log "Completed feature Y"
python3 tools/daily_digest.py

# Health checks
python3 tools/server_health.py
python3 tools/blocked_items.py summary
```

## TSP Project

### Location
- **Path:** `/data/.openclaw/workspace/tsp/testnet-mvp/`
- **API:** localhost:3000 (when running)
- **Database:** PostgreSQL (local, port 5432)

### Scripts
- **CI/CD:** `bash .openclaw/ci.sh` - Full pipeline (build, test, security, backup)
- **Backup:** `bash scripts/backup.sh` - Database backup to `tsp/backups/`
- **Deploy:** Not yet configured (requires external access setup)

### Current Status
- **Build:** Failing (TypeScript error in `src/scoring/provisional.ts:17`)
- **Blocker:** AgentId type not exported from `../types`
- **Tests:** 240/283 passing (85% when build works)
- **Priority:** High - blocking deployment

---

Add whatever helps you do your job. This is your cheat sheet.
## GitHub Credentials

### Location
- **File:** `/data/.openclaw/workspace/.github-credentials`
- **Permissions:** 600 (read-only for agent)
- **Repository:** bensargotest-sys/bensargotest-sys

### Configuration
GitHub credentials are stored in `.github-credentials` file (not tracked in git).

### Usage
```bash
# To push to GitHub:
source /data/.openclaw/workspace/.github-credentials
git remote set-url origin https://${GITHUB_TOKEN}@github.com/${GITHUB_USERNAME}/${GITHUB_REPO}.git
git push origin main
```

**Token stored securely - never commit to git**
