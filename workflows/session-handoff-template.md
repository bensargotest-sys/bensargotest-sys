# Session Handoff Template

Clean transitions between agents, sessions, or work phases. Use this when handing off context to ensure nothing gets lost.

## Why Handoffs Matter

Bad handoffs lose context. Good handoffs preserve:
- **State**: What's done, what's in progress, what's blocked
- **Context**: Why decisions were made, what failed, what worked
- **Next steps**: Clear actions with no ambiguity
- **Artifacts**: Where to find the work

## Template: Agent-to-Agent Handoff

```markdown
# Handoff: [FROM AGENT] → [TO AGENT]
**Date**: 2026-02-10 06:55 UTC
**Task**: [Brief description of overall goal]
**From**: [Agent name/role - e.g., "Researcher", "main-agent"]
**To**: [Agent name/role - e.g., "Coder", "analyst-subagent"]

## What I Completed

- ✅ [Specific deliverable 1] → `path/to/file.md`
- ✅ [Specific deliverable 2] → `path/to/code.ts`
- ✅ [Specific deliverable 3] → Logged in `memory/work-log.md`

## What's In Progress

- 🔄 [Item 1]: 60% complete, next step is [specific action]
- 🔄 [Item 2]: Waiting for [dependency], then [next action]

## What's Blocked

- 🔴 [Blocker #1]: [Description] - logged in blocked_items.py as ID #X
- 🔴 [Blocker #2]: [Description] - needs [specific resource/decision]

## Key Decisions Made

1. **[Decision 1]**: Chose [option A] over [option B] because [reason]. See `docs/decision-log.md`.
2. **[Decision 2]**: Implemented [pattern] based on [research findings].

## Things That Failed

- ❌ [Approach 1]: Tried [method], failed because [reason]. Don't repeat.
- ❌ [Tool/library]: Doesn't support [feature], switched to [alternative].

## Next Agent Should

1. **First**: [Most important next action with file path or command]
2. **Then**: [Second action with context]
3. **Finally**: [Completion criteria - how to know you're done]

## Artifacts & Locations

- Research findings: `research/topic-findings.md`
- Code: `src/module/feature.ts`
- Tests: `test/feature.test.ts`
- Logs: `memory/work-log.md` (search for "[KEYWORD]")
- Backup: `checkpoints/auto-checkpoint-TIMESTAMP.json`

## Context for Next Agent

[2-3 sentences of critical context that isn't obvious from the artifacts. What should they know that isn't written down elsewhere?]

## Questions for Next Agent

- [ ] [Question 1 if something is ambiguous]
- [ ] [Question 2 if next agent needs to make a decision]

## Contact

If next agent gets stuck: [How to reach out - e.g., "Check blocked_items.py", "sessions_send to main-agent", "Add task to task_queue.py"]
```

## Template: Shift Handoff (Daily/Weekly)

```markdown
# Shift Handoff: [DATE/TIME]
**From**: [Your name/agent]
**To**: [Next shift agent or future self]
**Period**: [e.g., "2026-02-09 evening shift" or "Week 6"]

## Active Projects

### Project: [Name]
- **Status**: [In Progress / Blocked / Waiting]
- **Last Action**: [What was just done]
- **Next Action**: [What needs to happen next]
- **Location**: `path/to/project/`
- **Notes**: [Any important context]

### Project: [Name]
- **Status**: [In Progress / Blocked / Waiting]
- **Last Action**: [What was just done]
- **Next Action**: [What needs to happen next]
- **Location**: `path/to/project/`
- **Notes**: [Any important context]

## Hot Issues

1. 🔥 **[Critical Issue]**: [Brief description] - needs attention within [timeframe]
2. ⚠️ **[Warning]**: [Description] - monitor for [specific signal]

## Completed This Shift

- ✅ [Task 1] - evidence: `file.md`
- ✅ [Task 2] - evidence: commit hash or log entry
- ✅ [Task 3] - evidence: output file

## Blocked Items

- 🔴 [Item] - blocked by [reason] - ID #X in blocked_items.py

## Things to Watch

- [ ] [System/metric to monitor - e.g., "TSP build status"]
- [ ] [Upcoming deadline - e.g., "API key expires 2026-02-15"]
- [ ] [Dependency - e.g., "Waiting for external API response"]

## System State

- **Backup**: Last successful backup: [timestamp or "needs backup"]
- **Health**: Server health: [OK / Check logs / Issue detected]
- **TSP CI/CD**: [Passing / Failing - blocker #X]
- **Queue**: [N] tasks in task_queue.py
- **Blockers**: [N] active blockers in blocked_items.py

## Notes for Next Shift

[Anything unusual, patterns noticed, things to be aware of, recommendations]
```

## Template: Phase Handoff (Research → Analysis → Implementation)

```markdown
# Phase Handoff: [PHASE NAME]
**Phase**: [Research / Analysis / Implementation / Testing / Deploy]
**Date**: 2026-02-10 06:55 UTC
**Project**: [Project name]

## This Phase Delivered

**Primary Deliverable**: `path/to/main-artifact.md`

**Supporting Artifacts**:
- `path/to/supporting-doc-1.md`
- `path/to/supporting-doc-2.md`
- `path/to/data/results.json`

## Key Findings

1. **[Finding 1]**: [Summary] - implications: [what this means for next phase]
2. **[Finding 2]**: [Summary] - implications: [what this means for next phase]
3. **[Finding 3]**: [Summary] - implications: [what this means for next phase]

## Recommendations for Next Phase

1. ✅ **Recommended**: [Approach A] because [reasons from research]
2. ⚠️ **Avoid**: [Approach B] because [reasons - failures, limitations]
3. 💡 **Consider**: [Alternative C] if [condition]

## Risks Identified

- 🔴 **High**: [Risk description] - mitigation: [suggestion]
- 🟡 **Medium**: [Risk description] - mitigation: [suggestion]

## Resources & References

- [Resource 1]: [URL or file path] - [why it's relevant]
- [Resource 2]: [URL or file path] - [why it's relevant]
- [Resource 3]: [URL or file path] - [why it's relevant]

## Next Phase Checklist

- [ ] Read this handoff completely
- [ ] Review primary deliverable: `path/to/main-artifact.md`
- [ ] Check for any blockers in blocked_items.py
- [ ] Confirm understanding of [critical decision/requirement]
- [ ] Start with [specific first action]
```

## Template: Emergency Handoff (Mid-Task)

```markdown
# EMERGENCY HANDOFF
**Time**: 2026-02-10 06:55 UTC
**Reason**: [Why stopping - timeout, error, blocking issue, etc.]
**Task**: [What was being worked on]

## Current State

**What's Open**:
- Files: [list of files that have uncommitted changes]
- Terminals: [any background processes running]
- Sessions: [any active browser/DB/SSH sessions]

**Last Command**: 
```bash
[exact command that was running or about to run]
```

**Status**: [Where in the process - e.g., "50% through file processing", "just started build"]

## What Just Happened

1. [Action taken]
2. [Result or error]
3. [Where it stopped]

## Problem

**Error Message**:
```
[exact error output if applicable]
```

**Why Stuck**: [Brief explanation of the blocker]

**Already Tried**:
- ❌ [Attempt 1] - didn't work because [reason]
- ❌ [Attempt 2] - didn't work because [reason]

## To Resume

**Immediate Next Step**: [Exact action to continue from here]

**File State**:
- Modified: `path/to/file1.ts`
- Created: `path/to/file2.md`
- Uncommitted changes: [yes/no]

**To Recover**:
```bash
# Commands to get back to this state if needed
cd /path/to/workspace
git status
# [any other setup commands]
```

## Context

[Critical context that would be lost if not captured now - assumptions, decisions in progress, things discovered]

## Help Needed

- [ ] [Specific help needed - e.g., "Need AgentId type definition"]
- [ ] [Resource needed - e.g., "API credentials"]
- [ ] [Decision needed - e.g., "Should we use approach A or B?"]
```

## Best Practices

### Do

✅ **Be specific**: "Completed `src/auth.ts` lines 1-150" not "worked on auth"  
✅ **Include paths**: Always give file paths so next agent can find your work  
✅ **Log blockers**: Use blocked_items.py for any blocked items  
✅ **Document decisions**: Explain *why* you chose something, not just *what*  
✅ **List failures**: "Tried X, didn't work because Y" saves next agent time  
✅ **Give evidence**: Point to log entries, file diffs, command output  
✅ **Set clear next steps**: Make it obvious what to do next  

### Don't

❌ **Be vague**: "Made progress" tells next agent nothing  
❌ **Assume context**: Next agent might be different model/persona  
❌ **Skip blockers**: Undocumented blockers cause wasted work  
❌ **Leave mess**: Clean state = faster pickup  
❌ **Over-explain**: Next agent can read your artifacts, just link them  
❌ **Hide failures**: Failed attempts are valuable data  

## Handoff Locations

Store handoffs where they'll be found:

- **Agent-to-agent**: `memory/handoffs/[from]-to-[to]-[date].md`
- **Shift handoffs**: `memory/handoffs/shift-[date]-[time].md`
- **Phase handoffs**: `[project]/docs/phase-handoff-[phase].md`
- **Emergency**: `memory/handoffs/emergency-[timestamp].md`

## Quick Handoff Script

```bash
#!/bin/bash
# Generate quick handoff template
HANDOFF_FILE="memory/handoffs/handoff-$(date +%Y%m%d-%H%M%S).md"

cat > "$HANDOFF_FILE" << 'EOF'
# Quick Handoff
**Time**: $(date -u '+%Y-%m-%d %H:%M UTC')
**From**: [your-name]
**To**: [next-agent]

## Completed
- 

## In Progress
- 

## Blocked
- 

## Next Steps
1. 

## Files Changed
- 

## Context
[Critical context here]
EOF

echo "Handoff template created: $HANDOFF_FILE"
```

## Integration with Tools

### With blocked_items.py

```bash
# Log blocker during handoff
python3 tools/blocked_items.py add "Task description" "Blocker reason"
# Reference in handoff: "See blocker ID #X"
```

### With task_queue.py

```bash
# Create tasks for next agent
python3 tools/task_queue.py add "Complete phase 2" "Details from handoff"
# Reference in handoff: "Task added to queue: ID #Y"
```

### With sessions_send

```bash
# Notify next agent
sessions_send --session "analyst-agent" --message "Handoff ready: memory/handoffs/research-to-analysis-20260210.md"
```

## Example: Real Research → Analysis Handoff

```markdown
# Handoff: Research → Analysis
**Date**: 2026-02-10 06:55 UTC
**Task**: OAuth2 library evaluation for TSP
**From**: Researcher agent (research-oauth2)
**To**: Analyst agent (analyst-oauth2)

## What I Completed

- ✅ Evaluated 5 OAuth2 libraries (Passport, OAuth2orize, node-oauth2-server, simple-oauth2, grant)
- ✅ Documented findings → `research/oauth2-library-comparison.md`
- ✅ Security audit of top 3 candidates → `research/oauth2-security-review.md`
- ✅ Performance benchmarks → `research/oauth2-benchmarks.json`

## Key Findings

1. **Passport.js most popular** (23k stars) but heavyweight for our needs - full auth framework
2. **simple-oauth2 best fit** - lightweight, maintained, good docs, supports all OAuth2 flows we need
3. **OAuth2orize unmaintained** - last commit 2 years ago, avoid
4. **Security concern**: All libraries require careful token storage - none provide this automatically

## Recommendations for Next Phase

1. ✅ **Recommended**: Use simple-oauth2 as base, build custom token storage layer
2. ⚠️ **Avoid**: Passport.js (too much overhead), OAuth2orize (unmaintained)
3. 💡 **Consider**: Combining simple-oauth2 + jose for JWT handling if we need custom claims

## Risks Identified

- 🔴 **High**: Token storage must be secure - research didn't find good existing solution, analyst should design this
- 🟡 **Medium**: Rate limiting not built into any library - we'll need to implement

## Next Phase Checklist

- [ ] Read `research/oauth2-library-comparison.md` (full comparison table)
- [ ] Review security notes in `research/oauth2-security-review.md`
- [ ] Design token storage layer (persistent, encrypted, with expiry)
- [ ] Create implementation plan in `workflows/oauth2-implementation-plan.md`
- [ ] Add rate limiting approach to plan
- [ ] Break down into task_queue.py items for coder phase

## Artifacts

- Main: `research/oauth2-library-comparison.md` (3.2KB, comparison table + notes)
- Security: `research/oauth2-security-review.md` (2.1KB, top 3 libraries audited)
- Data: `research/oauth2-benchmarks.json` (0.8KB, performance numbers)
- References: `research/oauth2-references.md` (1.5KB, docs + examples links)
```

---

**Philosophy**: A great handoff means the next agent can start productive work in under 5 minutes. If they need to spend 30 minutes figuring out what you did, the handoff failed.
