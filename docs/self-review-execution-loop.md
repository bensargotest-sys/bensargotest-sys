# Self-Review Execution Loop

## Overview
The self-review system runs every 4 hours via cron. It checks for repeated mistakes and promotes patterns to ENFORCEMENT.md when thresholds are met.

## Flow
```
Heartbeat → Work → Log → Self-Review (4h cron)
                              ↓
                    mistakes.json scan
                              ↓
                    Pattern detection (≥3 occurrences)
                              ↓
                    Promote to ENFORCEMENT.md (if new)
```

## Components

### 1. Heartbeat Enforcer (`tools/heartbeat_enforcer.py`)
- Rate limits heartbeats (min 30min between work items)
- Tracks consecutive no-work count
- Logs completed work items with timestamps

### 2. Mistake Logger (`tools/mistake_logger.py`)
- Records errors/failures with timestamps and descriptions
- Stores in `mistakes.json`

### 3. Mistake Promoter (`tools/mistake_promoter.py`)
- Scans `mistakes.json` for repeated patterns
- Current patterns tracked: subagent-fail (10x), tool-reuse (7x), path-error (2x)
- Promotes to ENFORCEMENT.md when threshold met (≥3 occurrences of same type)

### 4. Self-Review Cron (every 4 hours)
- Runs `mistake_promoter.py scan`
- Checks if any new patterns cross promotion threshold
- Reports findings to main session

## Key Metrics
- Work items completed: tracked by heartbeat_enforcer
- Mistake rate: mistakes / work items (target: <10%)
- Pattern promotion rate: patterns promoted / patterns detected

## Trigger Points
- **Heartbeat**: Every ~30min, picks one backlog item
- **Self-Review**: Every 4h, scans for patterns
- **Manual**: AB can trigger review anytime

## Files
- `tools/heartbeat_enforcer.py` — rate limiter + work logger
- `tools/mistake_logger.py` — error recorder
- `tools/mistake_promoter.py` — pattern scanner + promoter
- `mistakes.json` — raw mistake data
- `ENFORCEMENT.md` — promoted rules (permanent)
- `memory/heartbeat-backlog.md` — work queue
