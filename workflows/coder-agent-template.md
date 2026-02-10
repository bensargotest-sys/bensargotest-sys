# Coder Agent Template

Spawn a coder agent to implement features, write code, build prototypes, or fix bugs based on specifications.

## When to Use

- Have clear specifications or implementation plan
- Need to build a feature from scratch
- Want to prototype something quickly
- Have bugs that need fixing
- Need refactoring or code improvements

## Quick Spawn

```bash
sessions_spawn \
  --task "Implement [FEATURE]: Build [DESCRIPTION] in [LOCATION]. Follow spec in [SPEC_FILE]. Include tests. Log progress to memory/work-log.md." \
  --label "coder-[feature]" \
  --cleanup keep \
  --runTimeoutSeconds 1200
```

## Template Variables

- `[FEATURE]` - What to build (e.g., "OAuth2 authentication", "API rate limiter", "webhook handler")
- `[DESCRIPTION]` - Detailed description of what code should do
- `[LOCATION]` - Where to put the code (e.g., "src/auth/", "test/", "scripts/")
- `[SPEC_FILE]` - Path to specification document (e.g., "workflows/oauth2-plan.md", "research/api-spec.md")
- `[feature]` - Lowercase slug for labels (e.g., "oauth2", "rate-limiter")

## Standard Task Format

```
Implement [FEATURE]:
1. Read specification: [SPEC_FILE]
2. Create files in [LOCATION]
3. Implement [SPECIFIC REQUIREMENTS]
4. Write tests in test/[feature].test.ts
5. Document in docs/[feature].md
6. Log progress to memory/work-log.md with evidence
7. If blocked, use blocked_items.py
```

## Expected Outputs

Coder agents should produce:

### Code Files

```
src/[module]/[feature].ts     - Main implementation
test/[feature].test.ts         - Test suite
docs/[feature].md              - Usage documentation
```

### Work Log Entry

```
2026-02-10 10:55 UTC - Implemented [FEATURE]: Created src/[files], tests pass (N/N), documented in docs/[feature].md. Evidence: npm test shows all passing.
```

### Optional Deliverables

- `examples/[feature]-example.ts` - Usage examples
- `[feature].config.json` - Configuration files
- Migration scripts if database changes

## Example Spawns

### Feature Implementation (with spec)

```bash
sessions_spawn \
  --task "Implement OAuth2 server endpoints: Read workflows/oauth2-plan.md and implement authorization code flow in src/auth/oauth2.ts. Include: /authorize endpoint, /token endpoint, token validation middleware. Write tests in test/oauth2.test.ts covering happy path and error cases. Document API in docs/oauth2-api.md. Log progress to memory/work-log.md." \
  --label "coder-oauth2-server" \
  --cleanup keep \
  --runTimeoutSeconds 1800
```

### Bug Fix

```bash
sessions_spawn \
  --task "Fix TypeScript build error in src/scoring/provisional.ts:17: AgentId is not exported from ../types. Read src/types/index.ts to find correct type export (likely should be Agent or add AgentId export). Fix import statement. Verify build passes with 'npm run build'. Log fix to memory/work-log.md with before/after code." \
  --label "coder-fix-agentid-import" \
  --cleanup keep \
  --runTimeoutSeconds 600
```

### Refactoring

```bash
sessions_spawn \
  --task "Refactor tools/heartbeat_enforcer.py to remove deprecated datetime.utcnow() calls. Replace with datetime.now(datetime.UTC) throughout. Verify all tests pass. Ensure no behavior changes, only deprecation fixes. Log changes to memory/work-log.md with line numbers affected." \
  --label "coder-refactor-datetime" \
  --cleanup keep \
  --runTimeoutSeconds 600
```

### API Integration

```bash
sessions_spawn \
  --task "Implement GitHub API integration for TSP monitoring: Create src/integrations/github.ts with methods to fetch repo stars, issues, PRs using Octokit. Follow research/github-api-guide.md for authentication and rate limits. Include error handling and retry logic. Write tests mocking API responses. Document in docs/github-integration.md." \
  --label "coder-github-api" \
  --cleanup keep \
  --runTimeoutSeconds 1200
```

### Database Schema

```bash
sessions_spawn \
  --task "Create PostgreSQL migration for trust score history table: In migrations/004_trust_score_history.sql, create table with columns: id (serial), agent_id (text), score (integer), timestamp (timestamptz), reason (text). Add indexes on agent_id and timestamp. Write rollback migration. Test with scripts/migrate.sh. Document schema in docs/database-schema.md." \
  --label "coder-db-migration" \
  --cleanup keep \
  --runTimeoutSeconds 900
```

### CLI Tool

```bash
sessions_spawn \
  --task "Build CLI tool for TSP admin tasks: Create tools/tsp-admin.ts with subcommands: 'reset-score <agent_id>', 'list-agents', 'force-provisional <agent_id>'. Use commander.js for CLI parsing. Connect to database using existing config. Include help text and input validation. Add to package.json scripts. Document in docs/admin-cli.md." \
  --label "coder-admin-cli" \
  --cleanup keep \
  --runTimeoutSeconds 1500
```

### Test Suite

```bash
sessions_spawn \
  --task "Write comprehensive test suite for src/scoring/provisional.ts: Create test/scoring/provisional.test.ts covering: new agent gets provisional score, provisional converts to established after N credits, provisional expires after timeout, edge cases (zero credits, negative amounts). Mock database calls. Aim for 90%+ coverage. Run with 'npm test' and document results in memory/work-log.md." \
  --label "coder-provisional-tests" \
  --cleanup keep \
  --runTimeoutSeconds 1200
```

## Code Quality Checklist

Good coder output includes:

- ✅ **Follows spec**: Implements exactly what was specified
- ✅ **Tests included**: Unit tests for new code, tests pass
- ✅ **Error handling**: Graceful failures, no silent errors
- ✅ **Documentation**: Code comments, usage docs, examples
- ✅ **Type safety**: TypeScript types, no `any` unless justified
- ✅ **Clean code**: Readable, no magic numbers, clear variable names
- ✅ **Logged work**: Evidence in work-log.md (file paths, test results)
- ✅ **Blockers reported**: Uses blocked_items.py if stuck

Bad coder output:

- ❌ Partial implementation (missing parts of spec)
- ❌ No tests or failing tests
- ❌ No error handling (crashes on edge cases)
- ❌ No documentation
- ❌ Type errors or excessive `any` usage
- ❌ Unreadable code (unclear logic, poor naming)
- ❌ No work logged
- ❌ Silent failures (got stuck, didn't report)

## Integration Patterns

### Research → Implementation

```bash
# After researcher completes
sessions_spawn \
  --task "Implement [FEATURE] using [LIBRARY] as recommended in research/[topic]-findings.md. Follow the implementation pattern from research examples. Create src/[module]/[feature].ts, write tests, document in docs/[feature].md." \
  --label "coder-[feature]" \
  --cleanup keep
```

### Plan → Implementation

```bash
# After analyst creates plan
sessions_spawn \
  --task "Implement [FEATURE] following workflows/[feature]-plan.md step-by-step. Complete each section in order: 1) Core logic, 2) Error handling, 3) Tests, 4) Documentation. Log completion of each section to memory/work-log.md." \
  --label "coder-[feature]" \
  --cleanup keep
```

### Parallel Implementation (Multiple Coders)

```bash
# Break large feature into components
sessions_spawn --task "Implement server endpoints per workflows/oauth2-plan.md section 1..." --label "coder-oauth2-server" --cleanup keep

sessions_spawn --task "Implement client library per workflows/oauth2-plan.md section 2..." --label "coder-oauth2-client" --cleanup keep

sessions_spawn --task "Implement token storage per workflows/oauth2-plan.md section 3..." --label "coder-oauth2-storage" --cleanup keep

# Monitor and integrate
sessions_list --kinds isolated | grep coder
# After all complete, spawn integrator
```

### Test-Driven Development

```bash
# 1. Write tests first
sessions_spawn \
  --task "Write test suite for [FEATURE] in test/[feature].test.ts based on spec in [SPEC_FILE]. Tests should fail initially (feature not implemented yet). Document expected behavior." \
  --label "coder-tests-[feature]" \
  --cleanup keep

# 2. Implement to pass tests
sessions_spawn \
  --task "Implement [FEATURE] in src/[module]/[feature].ts to pass all tests in test/[feature].test.ts. Run 'npm test' until all pass. Log final test results." \
  --label "coder-impl-[feature]" \
  --cleanup keep
```

## Common Coding Patterns

### "Build Feature from Spec"

```
Implement [FEATURE]:
1. Read spec: [SPEC_FILE]
2. Create main implementation: src/[module]/[feature].ts
3. Implement core logic following spec requirements
4. Add error handling for edge cases
5. Write tests: test/[feature].test.ts
6. Run tests: npm test
7. Document: docs/[feature].md with usage examples
8. Log: memory/work-log.md with file paths and test results
9. If blocked: blocked_items.py
```

### "Fix Bug"

```
Fix [BUG]:
1. Reproduce bug: [steps or test case]
2. Identify root cause in [FILE]
3. Implement fix
4. Add regression test to prevent reoccurrence
5. Verify fix: [verification method]
6. Log: memory/work-log.md with before/after code snippets
```

### "Refactor Code"

```
Refactor [MODULE]:
1. Read current implementation: [FILE]
2. Identify improvements: [what to change]
3. Refactor while maintaining behavior
4. Ensure all existing tests still pass
5. Add tests for any new edge cases uncovered
6. Document changes in commit message or docs
7. Log: memory/work-log.md with refactoring summary
```

### "Add Tests"

```
Write tests for [MODULE]:
1. Read implementation: [FILE]
2. Identify test cases: happy path, error cases, edge cases
3. Write tests in test/[module].test.ts
4. Aim for [N]% coverage
5. Run: npm test -- --coverage
6. Log: memory/work-log.md with coverage report
```

## Tips for Effective Coder Spawns

### Be Specific

❌ Bad: "Fix the auth system"
✅ Good: "Fix TypeScript error in src/auth/oauth2.ts line 42 where token expiry check fails for UTC timestamps"

### Provide Context

❌ Bad: "Build authentication"
✅ Good: "Build OAuth2 authentication following workflows/oauth2-plan.md using simple-oauth2 library (from research/oauth2-findings.md recommendation)"

### Define Done

❌ Bad: "Work on the API"
✅ Good: "Implement /api/v1/trust-score GET endpoint returning agent score from database. Tests must pass. Document in docs/api.md."

### Include Specs

❌ Bad: "Make it work like the other thing"
✅ Good: "Implement following the pattern in src/existing/similar.ts, adapted for our use case per workflows/plan.md"

### Set Success Criteria

❌ Bad: "Build tests"
✅ Good: "Write tests achieving 80%+ coverage for src/scoring/provisional.ts, covering all public methods and error paths"

## Monitoring Coder Progress

```bash
# Check coder status
sessions_list --kinds isolated | grep coder

# View coder output
sessions_history --sessionKey <coder-session-key> --limit 30

# Check work log
tail -20 memory/work-log.md

# Check for blockers
python3 tools/blocked_items.py list | grep coder

# Check files created
ls -ltr src/[module]/  # sorted by time
git status             # uncommitted changes
```

## Handoff from Coder

After coder completes, document what was built:

```bash
cat > memory/handoffs/coder-to-review-$(date +%Y%m%d).md << EOF
# Handoff: Coder → Review
**Date**: $(date -u '+%Y-%m-%d %H:%M UTC')
**Task**: [Feature name]
**From**: coder-[feature]
**To**: [reviewer or next phase]

## Implemented

- ✅ Core logic: \`src/[module]/[feature].ts\` ([N] lines)
- ✅ Tests: \`test/[feature].test.ts\` ([N] tests, all passing)
- ✅ Documentation: \`docs/[feature].md\`

## Test Results

\`\`\`
npm test
[test output showing passes]
\`\`\`

## Usage Example

\`\`\`typescript
[simple usage example]
\`\`\`

## Known Limitations

- [Limitation 1]
- [Limitation 2]

## Next Steps

1. Code review
2. Integration testing
3. Deploy to staging
EOF
```

## Troubleshooting

### Coder Gets Stuck

```bash
# Check what they're doing
sessions_history --sessionKey <session> --limit 10

# Check if they reported blocker
python3 tools/blocked_items.py list

# If stuck on build error, may need to provide more context
# or fix environment issue before respawning
```

### Coder Produces Broken Code

Common issues:
- Spec was unclear → Improve spec, respawn with clearer task
- Missing dependencies → Install deps, add to task instructions
- Environment issue → Fix environment, retry
- Timeout too short → Increase runTimeoutSeconds

### Tests Fail

```bash
# Check what's failing
cd [project] && npm test

# If coder couldn't fix:
# Option 1: Spawn new coder with specific fix task
# Option 2: Fix manually and document in mistake_logger.py
```

### Code Quality Issues

- No error handling → Add to task: "Include error handling for [scenarios]"
- No tests → Add to task: "Must include tests, all must pass"
- Poor documentation → Add to task: "Document with usage examples in docs/"
- Type errors → Add to task: "Use proper TypeScript types, no any"

## Code Review Checklist

After coder completes, review:

- [ ] Code compiles/builds without errors
- [ ] Tests exist and pass
- [ ] Error handling present
- [ ] Documentation exists
- [ ] Follows existing code style
- [ ] No security issues (SQL injection, XSS, etc.)
- [ ] No hardcoded secrets or credentials
- [ ] Logged to work-log.md with evidence

## Example: Full Feature Implementation

```bash
# After analyst creates plan
sessions_spawn \
  --task "Implement provisional trust score system following workflows/trust-score-plan.md:

1. Create src/scoring/provisional.ts with:
   - provisionalize(agentId: string): Promise<void> - Set agent to provisional
   - checkConversion(agentId: string): Promise<boolean> - Check if should convert to established
   - PROVISIONAL_CREDIT_THRESHOLD = 100
   - PROVISIONAL_TIMEOUT_DAYS = 30

2. Add database functions in src/db/trust-scores.ts:
   - setProvisionalStatus(agentId, isProvisional)
   - getProvisionallTimestamp(agentId)
   - getCreditsSinceProvisional(agentId)

3. Write comprehensive tests in test/scoring/provisional.test.ts:
   - New agent gets provisional status
   - Conversion after 100 credits
   - Timeout after 30 days
   - Edge cases (zero credits, exactly threshold)

4. Document in docs/provisional-scoring.md with:
   - How it works
   - API reference
   - Usage examples

5. Run: npm run build && npm test
6. Log results to memory/work-log.md with test output
7. If blocked: use blocked_items.py

Success criteria: All tests pass, build succeeds, documented." \
  --label "coder-provisional-scoring" \
  --cleanup keep \
  --runTimeoutSeconds 1800
```

---

**Philosophy**: Good code is code that works, is tested, and can be understood by the next person. The coder's job is to turn specifications into working, maintainable software.
