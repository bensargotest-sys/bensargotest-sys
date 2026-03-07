# The Closed Loop: Auditor → Implementer → Re-audit

**Purpose:** Separate execution from verification to prevent false completions

**The Problem:** Agents sometimes produce work that looks correct but isn't. Tests pass, files exist, but the actual problem remains unsolved. The closed loop prevents this.

---

## 🔄 The Pattern

```
AUDITOR reviews target
    ↓
AUDITOR writes IMPLEMENTER brief
    ↓
IMPLEMENTER executes brief
    ↓
AUDITOR re-audits independently
    ↓
Perfect? → Report to human
Not perfect? → New brief, back to IMPLEMENTER
```

---

## 🎯 Core Principle

**The Implementer NEVER self-certifies.**

Only the Auditor declares work complete. This separation creates accountability and catches issues that self-review misses.

---

## 📐 Step-by-Step Workflow

### Step 1: Initial Audit

**Spawn Cipher (Analyst) to review the target:**

```
Spawn Cipher to audit [TARGET SYSTEM/CODE/FEATURE].

Produce scored report with:
- Overall score (0-100)
- Category scores (security, performance, maintainability, etc.)
- Evidence for each issue (file path, line number, command output)
- Critical issues (must fix before production)
- Warnings (should fix, not blocking)

Output: reviews/[target]-audit-initial-[YYYY-MM-DD].md

Include exact file paths and line numbers for every issue.
```

**Cipher outputs:**
```markdown
# [Target] Initial Audit Report

**Overall Score:** 45/100 (FAILING)

## Category Scores
- Security: 30/100 ❌ Critical
- Performance: 60/100 ⚠️ Needs work
- Maintainability: 50/100 ⚠️ Needs work
- Test Coverage: 40/100 ❌ Critical

## Critical Issues (Must Fix)
1. **SQL Injection Risk** (security.ts:47-52)
   - Evidence: User input directly concatenated into query
   - Command: `grep -n "db.query.*req.body" src/security.ts`
   - Impact: Production blocker

2. **No Rate Limiting** (api.ts:15)
   - Evidence: No rate limit middleware applied
   - Command: `grep -n "rateLimit" src/api.ts` returns nothing
   - Impact: DDoS vulnerability

[... more issues ...]
```

---

### Step 2: Write Implementer Brief

**Cipher writes a brief for Atlas (Coder):**

```
Spawn Cipher to write implementation brief for Atlas based on audit.

Brief must include:
- Exact fixes needed (file path, line number, what to change)
- Acceptance criteria (how to verify each fix works)
- Test requirements (what tests to write)
- Anti-shortcut rules (don't just comment out, actually fix)
- Verification commands (how Cipher will re-audit)

Output: reviews/[target]-implementer-brief-[YYYY-MM-DD].md
```

**Cipher outputs:**
```markdown
# [Target] Implementer Brief for Atlas

## Fix 1: SQL Injection (CRITICAL)
**File:** src/security.ts, lines 47-52
**Current code:**
```typescript
const query = `SELECT * FROM users WHERE id = ${req.body.userId}`;
const result = await db.query(query);
```

**Required fix:**
```typescript
const query = `SELECT * FROM users WHERE id = $1`;
const result = await db.query(query, [req.body.userId]);
```

**Acceptance criteria:**
- Parameterized queries used
- No string concatenation in SQL
- Test with malicious input: `'; DROP TABLE users; --`

**Tests to write:**
```typescript
test('SQL injection attempt is safely handled', async () => {
  const maliciousInput = "1'; DROP TABLE users; --";
  const result = await getUserById(maliciousInput);
  expect(result).toBeNull(); // Not an error, just no match
});
```

**Verification command:**
```bash
grep -n "db.query.*\$" src/security.ts  # Should find parameterized queries
grep -n "db.query.*req.body" src/security.ts  # Should find NOTHING
npm test -- security.test.ts  # Should pass
```

[... more fixes ...]

## Anti-Shortcut Rules
1. Do NOT just comment out vulnerable code
2. Do NOT disable linting to make errors go away
3. Do NOT mock tests to make them pass
4. Do NOT skip writing tests "because it's obvious"

If a fix is unclear, STOP and ask for clarification. Don't guess.
```

---

### Step 3: Implement Fixes

**Spawn Atlas (Coder) with the brief:**

```
Spawn Atlas to implement fixes from Cipher's brief.

Read: reviews/[target]-implementer-brief-[YYYY-MM-DD].md

Follow the brief EXACTLY. Do not deviate unless you have a better approach (document why).

For each fix:
1. Write failing test first
2. Implement fix
3. Verify test passes
4. Run verification command from brief
5. Document in fix report

Output:
- Code: [modified files]
- Tests: [test files]
- Report: reviews/[target]-fixes-[YYYY-MM-DD].md

Report must include:
- List of fixes completed
- Test output for each fix (proof tests pass)
- Verification command output (proof fix works)
- Any deviations from brief (with reasoning)
```

**Atlas outputs:**
```markdown
# [Target] Fix Report

## Fix 1: SQL Injection (COMPLETED ✅)

**Test written (failing):**
```typescript
// security.test.ts
test('SQL injection attempt is safely handled', async () => {
  const maliciousInput = "1'; DROP TABLE users; --";
  const result = await getUserById(maliciousInput);
  expect(result).toBeNull();
});
```

**Test output (before fix):**
```
FAIL src/__tests__/security.test.ts
  ✕ SQL injection attempt is safely handled (45 ms)
  
  Expected: null
  Received: Error: syntax error near ";"
```

**Implementation:**
Changed src/security.ts lines 47-52 to use parameterized queries.

**Test output (after fix):**
```
PASS src/__tests__/security.test.ts
  ✓ SQL injection attempt is safely handled (12 ms)
```

**Verification command:**
```bash
$ grep -n "db.query.*\$" src/security.ts
47: const result = await db.query(query, [req.body.userId]);

$ grep -n "db.query.*req.body" src/security.ts
(no output - good, no direct concatenation)

$ npm test -- security.test.ts
PASS (3/3 tests)
```

✅ Fix verified complete.

[... more fixes ...]

## Summary
- Fixes completed: 8/8
- Tests written: 8
- Tests passing: 8/8 (100%)
- Verification commands: All passed
- Deviations from brief: None
```

---

### Step 4: Re-audit

**Spawn Cipher again to re-audit:**

```
Spawn Cipher to re-audit [TARGET] after Atlas's fixes.

Read:
- Original audit: reviews/[target]-audit-initial-[YYYY-MM-DD].md
- Fix report: reviews/[target]-fixes-[YYYY-MM-DD].md

Compare before and after scores. Verify each claimed fix actually works.

Run the same checks as initial audit. Score each category again.

Output: reviews/[target]-audit-recheck-[YYYY-MM-DD].md

If score is not 100/100, identify remaining issues and write a NEW brief for Atlas.
If score is 100/100, declare work complete and report to human.
```

**Cipher outputs:**
```markdown
# [Target] Re-audit Report

**Previous Score:** 45/100
**Current Score:** 85/100 ✅ PASSING (improvement: +40 points)

## Category Scores (Before → After)
- Security: 30 → 90 ✅ (+60, nearly perfect)
- Performance: 60 → 80 ✅ (+20, acceptable)
- Maintainability: 50 → 85 ✅ (+35, good)
- Test Coverage: 40 → 85 ✅ (+45, good)

## Verification Results

### Fix 1: SQL Injection ✅
- Claimed: Parameterized queries implemented
- Verified: `grep -n "db.query.*\$" src/security.ts` → Found 3 instances
- Verified: `grep -n "db.query.*req.body" src/security.ts` → No results
- Test run: PASS
- **Status: CONFIRMED FIXED**

[... more verifications ...]

## Remaining Issues (Minor)
1. **Performance:** N+1 query in users list (lines 104-110)
   - Not critical but could optimize
   - Reduces score from 90 to 85

2. **Maintainability:** Function too long (lines 200-350, 150 lines)
   - Should be refactored into smaller functions
   - Reduces score from 90 to 85

## Recommendation
Current score (85/100) is PRODUCTION READY.

Remaining issues are optimizations, not blockers. Can address in future iteration.

**WORK COMPLETE** ✅
```

---

### Step 5: Decision Point

**If score < 100 (or your threshold):**
```
Cipher writes NEW brief for remaining issues.
Back to Step 2 (repeat loop).
```

**If score ≥ threshold:**
```
Report to human with before/after scores.
Move to production or next phase.
```

---

## 🛡️ Circuit Breaker

**Rule:** If the loop runs 5 iterations without reaching the threshold, STOP.

**Why:** Something is fundamentally wrong. Either:
- The task is poorly defined
- The Implementer is misunderstanding
- The Auditor's standards are unrealistic
- The approach is wrong

**Action:** Escalate to human for scoping review.

---

## 📊 Tracking Loop Health

Create `memory/closed-loop-tracker.json`:

```json
{
  "loops": [
    {
      "target": "trustlayer-api",
      "startDate": "2026-02-11",
      "iterations": [
        {"iteration": 1, "score": 45, "date": "2026-02-11T14:00:00Z"},
        {"iteration": 2, "score": 85, "date": "2026-02-11T16:30:00Z"}
      ],
      "finalScore": 85,
      "status": "complete",
      "humanApproved": true
    }
  ],
  "stats": {
    "totalLoops": 1,
    "avgIterations": 2,
    "avgImprovement": 40,
    "successRate": 100
  }
}
```

**Track:**
- How many iterations per loop (target: 1-3)
- Average score improvement per iteration
- Success rate (reached threshold vs gave up)

---

## 🎯 When to Use the Closed Loop

### ✅ Always Use For:
- Security-critical code
- Production deployments
- Database migrations
- API changes with backward compatibility
- Algorithm implementations
- Performance optimization
- Compliance requirements

### ⚠️ Consider Using For:
- Medium complexity features
- Refactoring large codebases
- Documentation quality assurance
- Test coverage improvements

### ❌ Don't Bother For:
- Simple file operations
- Documentation typo fixes
- Config updates (unless security-related)
- Trivial scripts

**Rule of thumb:** If failure has high cost, use the closed loop.

---

## 💡 Advanced Patterns

### Pattern 1: Parallel Implementers

**For large fixes, spawn multiple Atlases:**

```
Cipher writes brief with 3 independent sections.

Spawn Atlas-1: Fix security issues (section 1)
Spawn Atlas-2: Fix performance issues (section 2)
Spawn Atlas-3: Improve test coverage (section 3)

All work in parallel. Cipher re-audits after all complete.
```

---

### Pattern 2: Iterative Refinement

**For quality work (not just correctness):**

```
Iteration 1: Make it work (score: 60 → 80)
Iteration 2: Make it right (score: 80 → 90)
Iteration 3: Make it fast (score: 90 → 95)
Iteration 4: Make it beautiful (score: 95 → 100)
```

Each iteration has different criteria. Stop when "good enough" for current needs.

---

### Pattern 3: Cross-Agent Review

**For critical decisions:**

```
Sage designs architecture
    ↓
Cipher audits design (not implementation)
    ↓
Sage revises based on audit
    ↓
Cipher re-audits
    ↓
Atlas implements final design
    ↓
Cipher audits implementation
    ↓
Done
```

Design review before implementation prevents wasted coding effort.

---

## 🔬 Quality Metrics

Track these in your weekly review:

| Metric | Target | Meaning |
|--------|--------|---------|
| **Avg iterations per loop** | 1-3 | Efficiency of loop |
| **Avg score improvement** | +30-50 per iteration | Effectiveness of fixes |
| **First-pass success rate** | >50% | How often we nail it first try |
| **False completion rate** | <5% | Implementer claimed done but wasn't |
| **Escalation rate** | <10% | How often we hit circuit breaker |

**Good performance:**
- 2 iterations average
- +40 improvement per iteration
- 60% first-pass success
- 2% false completions
- 5% escalations

---

## 📝 Example: Full Loop for TrustLayer API Security

```bash
# Step 1: Initial audit
sessions_spawn \
  --task "Spawn Cipher to audit TrustLayer API security. Score 0-100. Evidence required." \
  --model "anthropic/claude-sonnet-4-5" \
  --label "cipher-trustlayer-audit-initial"

# Wait for results...
# Output: reviews/trustlayer-audit-initial-2026-02-11.md
# Score: 55/100 (needs work)

# Step 2: Write brief
sessions_spawn \
  --task "Spawn Cipher to write implementation brief for Atlas based on audit. Include exact fixes, verification commands, anti-shortcut rules." \
  --model "anthropic/claude-sonnet-4-5" \
  --label "cipher-trustlayer-brief"

# Wait for brief...
# Output: reviews/trustlayer-implementer-brief-2026-02-11.md

# Step 3: Implement fixes
sessions_spawn \
  --task "Spawn Atlas to implement fixes from brief. TDD required. Include test output and verification commands." \
  --model "xai/grok-3" \
  --label "atlas-trustlayer-fixes"

# Wait for fixes...
# Output: reviews/trustlayer-fixes-2026-02-11.md

# Step 4: Re-audit
sessions_spawn \
  --task "Spawn Cipher to re-audit TrustLayer API. Compare before/after scores. Verify each fix. Score 0-100." \
  --model "anthropic/claude-sonnet-4-5" \
  --label "cipher-trustlayer-audit-recheck"

# Wait for re-audit...
# Output: reviews/trustlayer-audit-recheck-2026-02-11.md
# Score: 90/100 (production ready!)

# Step 5: Report to human
"TrustLayer API security improved from 55 to 90 (threshold: 85). Production ready. See reviews/ for details."
```

---

## 🎓 Learning from the Loop

After each closed loop, ask:
- What went well? (Replicate this)
- What went poorly? (Avoid next time)
- Did we need all iterations? (Could we have done better first pass?)
- Did Cipher's brief give Atlas everything needed? (Improve brief template)
- Did Atlas follow the brief? (Improve Atlas's discipline)

**Update spawn templates based on learnings.**

---

**Status:** Closed loop pattern documented. Ready to use for quality-critical work.

**Next:** Apply this to TrustLayer API before production launch.

✅ **THE LOOP IS CLOSED** ✅
