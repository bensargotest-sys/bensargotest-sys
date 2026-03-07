# Self-Improvement Pipeline

**Last Updated:** 2026-02-14  
**Purpose:** Document how the system learns from mistakes and continuously improves

---

## Overview

The self-improvement pipeline is a closed-loop system that captures mistakes, identifies patterns, promotes them to enforcement rules, and prevents recurrence. It's built on three principles:

1. **Mistakes are data** - Every error is captured with full context
2. **Patterns become rules** - Recurring mistakes get promoted to ENFORCEMENT.md
3. **Rules are enforced** - Automated gates prevent known mistakes

---

## The Pipeline

### Stage 1: Mistake Capture

**Tool:** `tools/mistake_logger.py`

Every time something goes wrong:
```bash
python3 tools/mistake_logger.py log "description" --category "category"
```

**Categories:**
- `technical` - Code errors, build failures, test failures
- `process` - Workflow mistakes, missing steps
- `communication` - Misunderstandings, unclear instructions
- `planning` - Wrong estimates, missed dependencies
- `tooling` - Tool failures, configuration errors

**Storage:** `memory/mistakes.json`

**What gets captured:**
- Timestamp (when it happened)
- Description (what went wrong)
- Category (type of mistake)
- Context (what was being attempted)
- Resolution (how it was fixed, if applicable)

---

### Stage 2: Pattern Detection

**Tool:** `tools/mistake_promoter.py`

Automatically scans mistakes.json for patterns:
```bash
python3 tools/mistake_promoter.py scan
```

**Detection criteria:**
- Same mistake occurs 2+ times
- Similar error messages
- Same category + similar context
- Related root causes

**Output:** Candidates for promotion to ENFORCEMENT.md

---

### Stage 3: Rule Promotion

**Manual step:** Review candidates and promote to ENFORCEMENT.md

**Process:**
1. Review pattern detected by mistake_promoter.py
2. Identify root cause
3. Define prevention rule
4. Add to ENFORCEMENT.md with gate number
5. Implement automated check (if possible)

**Example:**
```markdown
## Rule #12: Validate Script Existence Before Cron Configuration

**Pattern:** Cron jobs referencing non-existent scripts fail hourly
**Root cause:** Script creation and cron setup done separately
**Prevention:** Use `test -f <path>` before creating cron job
**Enforcement:** Gate in cron job creation template
```

---

### Stage 4: Automated Enforcement

**Tool:** `tools/enforcement_watchdog.py`

Monitors for violations of promoted rules:
```bash
python3 tools/enforcement_watchdog.py check
```

**Checks:**
- File existence before operations
- Prerequisite completion
- Configuration validation
- Process adherence

**Actions on violation:**
- Log warning
- Block operation (if gate is strict)
- Alert user
- Suggest fix

---

### Stage 5: Effectiveness Measurement

**Tool:** `tools/effectiveness_monitor.py`

Tracks:
- Mistake frequency over time
- Rule effectiveness (prevented vs not prevented)
- False positive rate (rules blocking valid actions)
- Coverage (% of mistakes preventable)

**Metrics:**
```bash
python3 tools/effectiveness_monitor.py report
```

**Output:**
- Mistakes per day (trending down = good)
- Rule hit rate (how often rules catch issues)
- Escape rate (mistakes that bypass rules)
- Quality score (overall system health)

---

## Current State

### Active Rules (as of 2026-02-14)

From ENFORCEMENT.md:
1. Validate tool existence before use
2. Check file before reading
3. Verify API keys before requests
4. Validate script existence before cron
5. Test builds before deployment
6. Confirm subagent output exists
7. Verify database schema before queries
8. Check session state before operations
9. Validate configuration before applying
10. Test tools before marking complete
11. Measure before claiming metrics

### Promoted Patterns

**Process mistakes → Process rules:**
- "Cron job references missing script" → Rule #4
- "Tool called without validation" → Rule #1
- "Config applied without testing" → Rule #9

**Technical mistakes → Technical rules:**
- "Database query on missing schema" → Rule #7
- "API call with expired key" → Rule #3
- "Build deployed untested" → Rule #5

---

## Workflow

### Daily Operations

1. **When mistake occurs:**
   ```bash
   python3 tools/mistake_logger.py log "what went wrong" --category type
   ```

2. **Heartbeat check (every 5th):**
   ```bash
   python3 tools/mistake_promoter.py scan
   # Review candidates
   ```

3. **Weekly review:**
   ```bash
   python3 tools/mistake_promoter.py stats
   # Check trends, effectiveness
   ```

---

### Promotion Process

**Threshold:** 2+ occurrences OR 1 critical mistake

**Steps:**
1. Run `python3 tools/mistake_promoter.py scan`
2. Review candidates (check context, similarity)
3. If pattern is clear:
   - Write rule in ENFORCEMENT.md
   - Implement automated check (if possible)
   - Document in rule description
   - Mark pattern as promoted
4. If pattern is unclear:
   - Log "needs more data"
   - Wait for more occurrences

**Example promotion:**
```bash
# Scan for patterns
python3 tools/mistake_promoter.py scan

# Output shows:
# Pattern detected: "file not found" (3 occurrences)
# Candidate for promotion

# Add to ENFORCEMENT.md:
# Rule #N: Check file existence before operations
# Pattern: Multiple "file not found" errors
# Prevention: Use test -f or try/except
# Gate: Pre-operation validation
```

---

## Integration Points

### Heartbeat System

**Every 5th heartbeat:**
- Run mistake_promoter.py scan
- Check for new patterns
- Alert if promotion threshold reached

### Tool Usage

**Every tool should:**
- Log mistakes on failure
- Include context (what was attempted)
- Suggest fix (if known)

**Example:**
```python
try:
    result = do_operation()
except FileNotFoundError as e:
    log_mistake(f"File not found: {e.filename}", "technical")
    print(f"Suggestion: Create file first or check path")
    sys.exit(1)
```

### Subagent Spawns

**Before spawning:**
- Check past subagent failures (cascade detection)
- Verify similar tasks didn't fail recently
- Adjust approach based on past mistakes

**After completion:**
- Log success/failure
- If failure: capture mistake
- If pattern: consider rule

---

## Success Metrics

### Leading Indicators
- Mistakes logged per week (coverage increasing)
- Pattern detection rate (automation working)
- Rule promotion velocity (learning rate)

### Lagging Indicators
- Mistake recurrence rate (declining = good)
- Time to pattern detection (decreasing = good)
- Rule effectiveness (prevented mistakes / total)

### Target KPIs
- **Coverage:** >80% of mistakes logged
- **Detection:** Patterns found within 3 occurrences
- **Prevention:** >70% of rule-covered mistakes prevented
- **Recurrence:** <10% same mistake twice

---

## Current Performance

**As of 2026-02-14:**
- Mistakes logged: ~15
- Rules promoted: 11
- Patterns detected: ~5
- Effectiveness: Not yet measured (tool deployed)

**Next measurement:** 2026-02-21 (weekly review)

---

## Tools Reference

### mistake_logger.py
```bash
# Log a mistake
python3 tools/mistake_logger.py log "description" --category type

# List recent mistakes
python3 tools/mistake_logger.py list --recent 10

# Search mistakes
python3 tools/mistake_logger.py search "keyword"
```

### mistake_promoter.py
```bash
# Scan for patterns
python3 tools/mistake_promoter.py scan

# Get statistics
python3 tools/mistake_promoter.py stats

# List promotion candidates
python3 tools/mistake_promoter.py candidates
```

### enforcement_watchdog.py
```bash
# Check for violations
python3 tools/enforcement_watchdog.py check

# Validate specific operation
python3 tools/enforcement_watchdog.py validate --operation "cron-create"
```

### effectiveness_monitor.py
```bash
# Generate report
python3 tools/effectiveness_monitor.py report

# Check specific dimension
python3 tools/effectiveness_monitor.py check --dimension reliability
```

---

## Future Enhancements

### Planned
1. **Auto-promotion:** Automatically promote patterns after threshold
2. **ML pattern detection:** Use clustering to find non-obvious patterns
3. **Severity scoring:** Weight mistakes by impact
4. **Rule deprecation:** Remove ineffective rules
5. **A/B testing:** Test rule effectiveness

### Ideas
1. **Visual dashboard:** Mistake trends over time
2. **Cost tracking:** Mistakes cost money - track it
3. **Blame-free culture:** Focus on learning, not blame
4. **Team learning:** Share patterns across agents
5. **External integration:** Import mistakes from logs, monitoring

---

## Best Practices

### When to Log
✅ **Always log:**
- Unexpected errors
- Operations that failed
- Assumptions that were wrong
- Processes that need improvement

❌ **Don't log:**
- Expected failures (e.g., user input validation)
- External service downtime (not our mistake)
- Deliberate experiments
- User-triggered errors

### How to Write Good Mistake Descriptions
✅ **Good:**
- "Cron job failed: script tools/backup.sh not found (expected at path, file doesn't exist)"

❌ **Bad:**
- "Something broke"
- "Error"
- "Failed"

**Template:**
"[What failed]: [Why it failed] ([Context: what was being attempted, what was expected])"

### When to Promote
- **Threshold:** 2+ occurrences of same pattern
- **Severity:** 1 critical mistake (data loss, security breach)
- **Cost:** Mistake costs significant time/money
- **Preventability:** Clear rule can prevent it

---

## Case Studies

### Case Study 1: Cron Job Validation

**Mistake:** TSP cron jobs failed hourly for 2 days  
**Pattern:** 3 cron jobs referencing non-existent scripts  
**Root cause:** Script creation and cron setup done separately  
**Rule promoted:** #4 "Validate script existence before cron configuration"  
**Implementation:** Added `test -f` check to cron creation template  
**Effectiveness:** 100% prevention (no recurrence in 3 days)  
**ROI:** Saved ~50 failed cron runs, prevented alert fatigue

### Case Study 2: Cost Tracker Editing

**Mistake:** Broke cost_tracker.py with indentation errors  
**Pattern:** 1 occurrence (but high severity)  
**Root cause:** Complex inline editing without validation  
**Lesson:** Don't edit complex Python inline during heartbeats  
**Action:** Logged mistake, reverted changes, flagged for dedicated session  
**Effectiveness:** Prevented file damage from persisting  
**ROI:** 15 minutes recovery time vs potential hours debugging

---

## Related Documentation

- ENFORCEMENT.md - Current rules and gates
- AGENTS.md - Process improvements section
- OPERATIONS-GUIDE.md Section 7 - Enforcement framework
- tools/mistake_logger.py - Usage reference
- tools/mistake_promoter.py - Pattern detection reference

---

**Status:** Living document  
**Next review:** 2026-02-21 (weekly)  
**Owner:** Main agent + quality monitoring tools
