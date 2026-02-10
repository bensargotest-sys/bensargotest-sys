# Friction Log

**Purpose:** Track repeated pain points that should become automated tools.

**Rule:** If you do the same manual task 3+ times, it becomes a tool candidate.

---

## Active Friction Points

### 2026-02-10 - GitHub Push Blocked by Secret Scanning
- **Friction:** Can't push to GitHub due to old token in history
- **Frequency:** Blocked entire TSP launch
- **Impact:** HIGH (blocks deployment)
- **Workaround:** Manual upload to Netlify Drop
- **Tool Needed:** Pre-push secret scanner, or automated BFG cleanup
- **Status:** Promoted to ENFORCEMENT.md Rule #1

### 2026-02-10 - Finding Files Across Workspace
- **Friction:** Manual `find` commands to locate files
- **Frequency:** Daily (multiple times)
- **Impact:** MEDIUM (time sink, 2-3 min per search)
- **Tool Needed:** QMD workspace search (semantic + full-text)
- **Status:** Installing QMD now

### 2026-02-10 - Updating Multiple Outreach Messages
- **Friction:** Need to manually edit 4 separate files to insert landing page URL
- **Frequency:** One-time (but indicative of pattern)
- **Impact:** LOW (5 minutes)
- **Tool Needed:** Template variable substitution script
- **Status:** Note for future

---

## Resolved Friction

_(Friction that became tools)_

### 2026-02-09 - Manual Checkpoint Writing
- **Friction:** Forgetting to update WORKING_STATE.md
- **Resolution:** Built checkpoint.py (auto-checkpoint, handoff mode)
- **Status:** ✅ RESOLVED

### 2026-02-09 - Checking if Compaction Happened
- **Friction:** Not knowing if WORKING_STATE.md is stale
- **Resolution:** Built compaction_guard.sh (FRESH/STALE check)
- **Status:** ✅ RESOLVED

---

## Pattern Analysis

**Most common friction types:**
1. File operations (searching, editing, organizing)
2. State management (checkpoints, handoffs)
3. External integrations (GitHub, deployment, APIs)

**Tool candidates (future):**
- Workspace-wide find/replace with variable substitution
- Pre-commit hooks for secret scanning
- One-command deployment script (aggregates Netlify Drop + GitHub)

---

**Next Review:** Weekly (check for 3+ occurrences of same pattern)

### 2026-02-10 - QMD Installation (RESOLVED ✅)
- **Friction:** QMD tool installation via Bun doesn't work
- **Attempts:**
  1. `bun install -g qmd` → installed placeholder package (0.0.0, no binary)
  2. Searched for binary in ~/.bun → not found
  3. Removed placeholder package
  4. **Delegated to Researcher subagent** → found real source
  5. **Installed from GitHub** → success ✅
- **Root Cause:** "qmd" npm package is placeholder, actual tool is at github.com/tobi/qmd
- **Resolution:** `bun install -g https://github.com/tobi/qmd`
- **Status:** ✅ RESOLVED - QMD working (28 files indexed, search functional)
- **Commands:**
  - Search: `~/.bun/bin/qmd search "query"`
  - Index: `~/.bun/bin/qmd update`
  - Status: `~/.bun/bin/qmd status`
