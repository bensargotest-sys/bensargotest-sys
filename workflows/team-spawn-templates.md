# Team Spawn Templates

Multi-agent coordination patterns for complex tasks requiring specialized roles.

## Core Principles

- **Pull-based coordination**: Use task_queue.py for task distribution
- **Explicit handoffs**: Document what each agent produces for the next
- **Central logging**: All agents log to memory/work-log.md
- **Failure resilience**: Blocked items tracked in blocked_items.py
- **Clean boundaries**: Each agent has clear scope and outputs

## Template: Research → Analysis → Implementation

**Use when:** Building something new that requires research, planning, and coding.

### Phase 1: Research Agent

```bash
# Spawn researcher
task="Research [TOPIC]: Find 5-7 relevant resources, extract key patterns, document findings in research/[topic]-findings.md with citations and recommendations for next phase."

sessions_spawn --task "$task" --label "researcher-[topic]" --cleanup keep
```

**Outputs:**
- `research/[topic]-findings.md` - Key findings with citations
- Recommendations for analysis phase

### Phase 2: Analysis Agent

```bash
# After research completes
task="Analyze research/[topic]-findings.md and create detailed implementation plan in workflows/[topic]-plan.md. Include architecture, dependencies, risks, and task breakdown."

sessions_spawn --task "$task" --label "analyst-[topic]" --cleanup keep
```

**Outputs:**
- `workflows/[topic]-plan.md` - Implementation roadmap
- Task queue entries for implementation

### Phase 3: Implementation Agent(s)

```bash
# After plan is ready
task="Implement [FEATURE] following workflows/[topic]-plan.md. Write code, tests, documentation. Log progress to memory/work-log.md. If blocked, use blocked_items.py."

sessions_spawn --task "$task" --label "coder-[topic]" --cleanup keep
```

**Outputs:**
- Working code in appropriate directory
- Tests and documentation
- Work log entries with evidence

## Template: Parallel Workers + Coordinator

**Use when:** Multiple independent tasks that need final integration.

### Spawn Workers

```bash
# Worker 1
sessions_spawn --task "Build component A: [SPECS]" --label "worker-a" --cleanup keep

# Worker 2  
sessions_spawn --task "Build component B: [SPECS]" --label "worker-b" --cleanup keep

# Worker 3
sessions_spawn --task "Build component C: [SPECS]" --label "worker-c" --cleanup keep
```

### Monitor Progress

```bash
# Check worker status
python3 tools/subagent_log.py

# Check for blockers
python3 tools/blocked_items.py list
```

### Spawn Integrator

```bash
# After all workers complete
task="Integrate components A, B, C. Test integration, fix conflicts, document in docs/integration.md."

sessions_spawn --task "$task" --label "integrator" --cleanup keep
```

## Template: Audit → Fix → Verify

**Use when:** Fixing issues or improving existing code.

### Phase 1: Auditor

```bash
task="Audit [SYSTEM]: Check for bugs, security issues, performance problems, tech debt. Document findings in reviews/[system]-audit.md with severity ratings."

sessions_spawn --task "$task" --label "auditor-[system]" --cleanup keep
```

**Outputs:**
- `reviews/[system]-audit.md` - Issues with severity ratings
- Recommended fix priorities

### Phase 2: Fixer

```bash
task="Fix issues from reviews/[system]-audit.md. Start with HIGH severity, then MEDIUM. Log each fix to memory/work-log.md with evidence."

sessions_spawn --task "$task" --label "fixer-[system]" --cleanup keep
```

**Outputs:**
- Code changes (commits)
- Fix documentation
- Work log entries

### Phase 3: Verifier

```bash
task="Verify fixes for [SYSTEM]. Run tests, check original issues are resolved, confirm no regressions. Document in reviews/[system]-verification.md."

sessions_spawn --task "$task" --label "verifier-[system]" --cleanup keep
```

**Outputs:**
- `reviews/[system]-verification.md` - Verification results
- Sign-off or additional issues found

## Template: Documentation Team

**Use when:** Generating comprehensive documentation for a project.

```bash
# API Documentation
sessions_spawn --task "Document all API endpoints in docs/api/. Include examples, error codes, rate limits." --label "docs-api"

# User Guide
sessions_spawn --task "Write user guide in docs/user-guide.md. Cover installation, quickstart, common tasks." --label "docs-user"

# Architecture
sessions_spawn --task "Document system architecture in docs/architecture.md. Include diagrams, data flow, security model." --label "docs-arch"

# Troubleshooting
sessions_spawn --task "Create troubleshooting guide in docs/troubleshooting.md from common issues in memory/mistakes.json." --label "docs-troubleshoot"
```

## Template: Quality Assurance Pipeline

**Use when:** Comprehensive testing before deployment.

```bash
# Unit Tests
sessions_spawn --task "Write unit tests for [MODULE]. Target 80%+ coverage. Log results." --label "qa-unit"

# Integration Tests  
sessions_spawn --task "Write integration tests for [SYSTEM]. Test all major workflows." --label "qa-integration"

# Security Scan
sessions_spawn --task "Run security audit: dependency check, code scan, config review. Document in reviews/security-scan.md." --label "qa-security"

# Performance Test
sessions_spawn --task "Run performance tests for [SYSTEM]. Document benchmarks, identify bottlenecks in reviews/perf-test.md." --label "qa-perf"
```

## Coordination Patterns

### Task Queue Coordination

```bash
# Main agent creates tasks
python3 tools/task_queue.py add "Build feature X" "Details..."
python3 tools/task_queue.py add "Write tests for X" "Details..."
python3 tools/task_queue.py add "Document X" "Details..."

# Spawn workers who pull from queue
sessions_spawn --task "Pull tasks from queue using 'python3 tools/task_queue.py claim worker-1'. Complete and mark done. Repeat until queue empty." --label "worker-1"
```

### File-Based Handoff

```bash
# Agent A produces output file
# Agent B spawned with explicit input file path
sessions_spawn --task "Process data/input.json and generate data/output.json according to spec in workflows/transform-spec.md" --label "processor"
```

### Blocked Item Escalation

```bash
# Worker hits blocker
python3 tools/blocked_items.py add "Build feature Y" "Missing API credentials"

# Main agent resolves blocker
# Notify worker via sessions_send or file flag

# Worker checks and resumes
python3 tools/blocked_items.py resolve 1 "API key added to .env"
```

## Best Practices

1. **Single Responsibility**: Each agent should have one clear job
2. **Explicit Outputs**: Define exactly what files/data each agent produces
3. **Failure Handling**: All agents should use blocked_items.py for blockers
4. **Progress Logging**: Every agent logs to memory/work-log.md with evidence
5. **Clean Handoffs**: Next agent's task explicitly references previous outputs
6. **Timeout Protection**: Set reasonable runTimeoutSeconds (default: 300s)
7. **Cleanup Policy**: Use `--cleanup keep` for important work you might need to review
8. **Status Checks**: Monitor with `sessions_list` and `python3 tools/subagent_log.py`

## Common Pitfalls

❌ **Vague tasks**: "Fix the thing" → ✅ "Fix TypeScript error in src/scoring/provisional.ts:17 where AgentId is not exported"

❌ **No outputs defined**: Task completes but where's the work? → ✅ "Document findings in research/results.md"

❌ **No failure plan**: Agent gets stuck silently → ✅ "If blocked, log to blocked_items.py and exit"

❌ **Circular dependencies**: A waits for B, B waits for A → ✅ Plan linear or parallel flows

❌ **Token waste**: Spawning agents for trivial tasks → ✅ Direct execution when simple

## Example: Full Feature Implementation

```bash
# 1. Research phase
sessions_spawn \
  --task "Research OAuth2 implementations for Node.js. Find 3-5 libraries, compare features, security track record. Document in research/oauth2-options.md with recommendation." \
  --label "research-oauth2" \
  --cleanup keep

# Wait for completion, then:

# 2. Planning phase  
sessions_spawn \
  --task "Read research/oauth2-options.md and create implementation plan in workflows/oauth2-plan.md. Include file structure, configuration, error handling, tests." \
  --label "plan-oauth2" \
  --cleanup keep

# Wait for completion, then:

# 3. Parallel implementation
sessions_spawn \
  --task "Implement OAuth2 server code per workflows/oauth2-plan.md. Focus on auth endpoints. Output: src/auth/oauth2.ts" \
  --label "code-oauth2-server" \
  --cleanup keep

sessions_spawn \
  --task "Write OAuth2 client library per workflows/oauth2-plan.md. Focus on token handling. Output: src/client/oauth2-client.ts" \
  --label "code-oauth2-client" \
  --cleanup keep

sessions_spawn \
  --task "Write OAuth2 tests per workflows/oauth2-plan.md. Cover happy path and error cases. Output: test/oauth2.test.ts" \
  --label "test-oauth2" \
  --cleanup keep

# Wait for all, then:

# 4. Integration
sessions_spawn \
  --task "Integrate OAuth2 components. Wire up server + client + tests. Fix conflicts. Run full test suite. Document in docs/oauth2.md." \
  --label "integrate-oauth2" \
  --cleanup keep

# 5. Final review
sessions_spawn \
  --task "Security review of OAuth2 implementation. Check for common vulnerabilities (token leakage, CSRF, etc). Document findings in reviews/oauth2-security.md." \
  --label "review-oauth2" \
  --cleanup keep
```

## Monitoring Dashboard

```bash
# Check all active agents
sessions_list --kinds isolated

# Check subagent history
python3 tools/subagent_log.py

# Check task queue
python3 tools/task_queue.py list

# Check blockers
python3 tools/blocked_items.py summary

# View recent work
tail -20 memory/work-log.md
```

---

**Philosophy:** Good teams have clear roles, explicit communication, and no ambiguity about who does what. Same applies to agent teams.
