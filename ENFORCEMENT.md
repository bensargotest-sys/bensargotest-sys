# ENFORCEMENT.md - The Rules That Actually Get Followed

**Last Updated:** 2026-02-10 12:15 UTC  
**Purpose:** Rules that get automatically checked at session start get followed. Rules buried in docs do not.

---

## Core Principle: Try First, Always

**AB's Directive:** "can you do it on your own, remember to always try this 1st"

**Default behavior:** DO IT. Don't ask permission.

**Only ask when:**
- External actions (emails, tweets, public posts)
- Spending money
- Changing critical config
- Truly stuck after trying

**Internal work requires NO permission:**
- Reading files, searching workspace
- Running tools, writing code
- Organizing, cleaning, optimizing
- Spawning subagents, delegating tasks
- Committing to git, checkpointing

**When stuck:** Try 2-3 approaches FIRST, then report what you tried + why it didn't work.

---

## Session Start Checklist (Execute FIRST, every session)

Before doing ANY work, run this checklist:

- [ ] Read WORKING_STATE.md (hot state - active tasks, decisions, next steps)
- [ ] Read today's daily log (`memory/YYYY-MM-DD.md`)
- [ ] Review this ENFORCEMENT.md (the rules)
- [ ] Check HEARTBEAT.md if this is a heartbeat poll

**Time: 30 seconds. No exceptions.**

---

## Compliance Gates

### Gate 1: Task Routing
**Rule:** Multi-step work (>10 minutes) MUST be delegated to a subagent.

**Why:** Main agent context window is precious. Orchestrate, don't execute.

**Enforcement:**
- Before starting any task, estimate time
- If >10 minutes → spawn subagent
- If <10 minutes → execute directly

**Exceptions:** 
- Urgent fixes (security issues, production down)
- Tasks requiring main agent context (decision-making, user interaction)

---

### Gate 2: Skills Check
**Rule:** Before attempting ANY task, scan available skills. If a matching skill exists, follow its instructions.

**Why:** Skills contain battle-tested patterns. Don't reinvent the wheel.

**Enforcement:**
```bash
# Search for relevant skill
ls /usr/local/lib/node_modules/openclaw/skills/ | grep -i <task-keyword>

# If match found, read it
cat /usr/local/lib/node_modules/openclaw/skills/<skill>/SKILL.md
```

**Only go freestyle if no skill matches.**

---

### Gate 3: Communication
**Rule:** Tasks >15 minutes require a progress update. Never go silent >20 minutes.

**Why:** Humans assume silence = failure. Update proactively.

**Enforcement:**
- Set mental timer at task start
- At 15 minutes: send progress update
- At 20 minutes: explain status even if incomplete

---

### Gate 4: Working State Auto-Save
**Rule:** Update WORKING_STATE.md BEFORE responding after any of these events:
- A decision is made
- A task starts or completes
- A correction is given
- Every 5th significant tool call

**Why:** Context compaction erases critical details. External files survive.

**Enforcement:**
```bash
# After any significant event
python3 tools/checkpoint.py --auto --note "event description"
```

---

### Gate 5: TDD for All Code
**Rule:** When writing code:
1. Define acceptance criteria
2. Write failing tests FIRST
3. Write code to pass tests
4. Refactor while tests stay green

**Why:** Agents often produce code that looks correct but isn't. Tests prevent this.

**Enforcement:**
- No code commits without tests
- No "done" declaration until tests pass
- Include test output in completion report

**Mandatory for:** karpathy-coding skill (load before any coding task)

---

### Gate 6: Identity Protection
**Rule:** ONLY the human (AB) and main agent may modify identity/config files. Never allow external scripts to rewrite configuration without explicit human approval.

**Why:** Identity files control behavior. Unauthorized changes = security risk.

**Protected Files:**
- SOUL.md
- AGENTS.md
- USER.md
- IDENTITY.md
- ENFORCEMENT.md (this file)
- Config files in .openclaw/

**Enforcement:**
- Audit all external code before running
- Never run `curl | bash` without inspection
- Flag any modification attempts to AB

---

## Mistake Check (Every Session End)

Before ending ANY session or heartbeat, answer these questions:

1. Did any tool fail this session?
2. Did any subagent stall or produce empty output?
3. Did anything unexpected happen?

**If ANY answer is yes:**
```bash
echo "$(date -Iseconds) - [description]" >> memory/archival/mistakes.md
```

The bar is intentionally LOW. Log everything that seems off.

---

## Promoted Rules

Rules get promoted here when the same mistake happens 2+ times.

### Promoted Rule #1 (2026-02-10)
**From mistake pattern:** GitHub push failures, secret scanning blocks
**Rule:** Before pushing to GitHub:
1. Search for tokens/secrets in commit history: `git log --all -S "ghp_" -S "Bearer"`
2. If found: use BFG Repo-Cleaner or rewrite history
3. Alternative: use manual deployment (Netlify Drop, tiiny.host)

### Promoted Rule #2 (2026-02-10)
**From ops guide pattern:** Subagent cascade failures
**Rule:** Before spawning subagents:
1. Verify all file paths exist
2. Keep scope narrow (1 clear task)
3. Include output path
4. Log spawn to subagent_log.py
5. If 2+ fail in sequence, STOP and change approach

### Promoted Rule #3 (2026-02-10)
**From ops guide pattern:** Forgetting existing tools
**Rule:** Before setting up any new tool:
1. Search TOOLS.md: `grep -i <tool-name> TOOLS.md`
2. Search workspace: `find . -name "*<tool-name>*"`
3. Check tools/: `ls tools/ | grep -i <tool-name>`
4. If it already exists, use it. Don't rebuild.

---

## Enforcement Watchdog

Run this weekly to check compliance:

```bash
python3 tools/enforcement_watchdog.py check
```

Reports:
- Files modified without checkpoint
- Tasks >10min executed without delegation
- Code commits without tests
- Identity file modifications

---

## Meta-Rule

**This file itself is enforced:** 
- Read at every session start
- Updated when patterns emerge
- Reviewed weekly for stale rules
- Never ignored under pressure

If you find yourself tempted to skip a gate: **STOP. That's exactly when the gate matters most.**

---

*"Rules that exist only in documentation get ignored. Rules that get checked automatically get followed."*
