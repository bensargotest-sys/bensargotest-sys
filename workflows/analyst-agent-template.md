# Analyst Agent Template

Spawn an analyst agent to review research, create implementation plans, design architectures, or break down complex problems into actionable tasks.

## When to Use

- Have research findings that need analysis and planning
- Need to design architecture or system structure
- Want to break down complex feature into implementation steps
- Need to evaluate trade-offs and make design decisions
- Want to create detailed specifications for coders

## Quick Spawn

```bash
sessions_spawn \
  --task "Analyze [INPUT]: Review [SOURCE_FILE], design [DELIVERABLE] in [OUTPUT_FILE]. Include architecture, dependencies, task breakdown, and risks." \
  --label "analyst-[topic]" \
  --cleanup keep \
  --runTimeoutSeconds 900
```

## Template Variables

- `[INPUT]` - What to analyze (e.g., "research findings", "system requirements", "current architecture")
- `[SOURCE_FILE]` - Input document path (e.g., "research/oauth2-findings.md")
- `[DELIVERABLE]` - What to produce (e.g., "implementation plan", "architecture design", "migration strategy")
- `[OUTPUT_FILE]` - Where to save output (e.g., "workflows/oauth2-plan.md")
- `[topic]` - Lowercase slug for labels (e.g., "oauth2", "database-migration")

## Standard Task Format

```
Analyze [TOPIC]:
1. Read input: [SOURCE_FILE]
2. Design: [SYSTEM/FEATURE/ARCHITECTURE]
3. Create detailed plan in [OUTPUT_FILE] with:
   - Architecture overview
   - Component breakdown
   - File structure
   - Dependencies
   - Implementation steps
   - Testing approach
   - Risk analysis
4. Break down into task_queue.py items (optional)
5. Log to memory/work-log.md
```

## Expected Outputs

Analyst agents should produce:

### Primary Deliverable: `workflows/[topic]-plan.md`

```markdown
# Implementation Plan: [TOPIC]
**Date**: YYYY-MM-DD
**Analyst**: [agent label]
**Based on**: [research/source document]

## Overview

[2-3 sentence summary of what we're building and why]

## Architecture

### High-Level Design

[Diagram or description of system components and how they interact]

### Components

1. **[Component 1 Name]**
   - Purpose: [What it does]
   - Location: `src/[path]/`
   - Dependencies: [what it needs]
   - Interfaces: [what it exposes]

2. **[Component 2 Name]**
   - Purpose: [What it does]
   - Location: `src/[path]/`
   - Dependencies: [what it needs]
   - Interfaces: [what it exposes]

## File Structure

```
src/
  [module]/
    [feature].ts           - Main implementation
    [feature]-types.ts     - Type definitions
    [feature]-config.ts    - Configuration
test/
  [module]/
    [feature].test.ts      - Unit tests
docs/
  [feature].md             - Usage documentation
```

## Dependencies

### External Libraries
- [library-1] (version): [why we need it]
- [library-2] (version): [why we need it]

### Internal Dependencies
- [module-1]: [what we use from it]
- [module-2]: [what we use from it]

## Implementation Steps

### Phase 1: Core Logic ([N] hours)
1. Create `src/[module]/[file].ts`
2. Implement [specific functionality]
3. Add [specific methods/classes]
4. Handle [specific cases]

### Phase 2: Error Handling ([N] hours)
1. Add validation for [inputs]
2. Handle [error scenarios]
3. Add retry logic for [operations]
4. Log errors to [logging system]

### Phase 3: Testing ([N] hours)
1. Write unit tests: test/[file].test.ts
2. Cover: [test cases]
3. Mock: [external dependencies]
4. Target: [N]% coverage

### Phase 4: Documentation ([N] hours)
1. API documentation: docs/[file].md
2. Usage examples
3. Configuration guide
4. Troubleshooting section

## Testing Approach

### Unit Tests
- Test [component] in isolation
- Mock [external dependencies]
- Cover [scenarios]

### Integration Tests
- Test [component interaction]
- Use test database/services
- Verify [end-to-end flows]

### Manual Testing
- [Specific scenarios to test manually]
- [Edge cases to verify]

## Configuration

### Required Config
```json
{
  "[key]": "[value]",
  "[key]": "[value]"
}
```

### Environment Variables
- `[VAR_NAME]`: [description]
- `[VAR_NAME]`: [description]

## Risk Analysis

### High Risk 🔴
- **[Risk 1]**: [Description]
  - Impact: [What happens if this goes wrong]
  - Mitigation: [How to reduce risk]
  - Fallback: [Plan B]

### Medium Risk 🟡
- **[Risk 2]**: [Description]
  - Impact: [What happens]
  - Mitigation: [How to handle]

### Low Risk 🟢
- **[Risk 3]**: [Description]
  - Mitigation: [Basic handling]

## Success Criteria

- [ ] [Criterion 1 - measurable outcome]
- [ ] [Criterion 2 - measurable outcome]
- [ ] [Criterion 3 - measurable outcome]
- [ ] All tests pass
- [ ] Documentation complete
- [ ] Code review approved

## Task Breakdown (for task_queue.py)

1. **Core Implementation** (Est: [N]h)
   - Implement [specific functionality]
   - Files: `src/[files]`

2. **Error Handling** (Est: [N]h)
   - Add validation and error handling
   - Files: `src/[files]`

3. **Testing** (Est: [N]h)
   - Write comprehensive test suite
   - Files: `test/[files]`

4. **Documentation** (Est: [N]h)
   - Document API and usage
   - Files: `docs/[files]`

## Open Questions

- [ ] [Question 1 that needs answering]
- [ ] [Question 2 that needs deciding]

## References

- Research: [path/to/research.md]
- Similar implementation: [path/to/example.ts]
- External docs: [URL]
```

### Supporting Files

- `workflows/[topic]-architecture.md` - Detailed architecture diagrams
- `workflows/[topic]-api-spec.md` - API specifications
- `workflows/[topic]-migration-plan.md` - Migration strategy if applicable

## Example Spawns

### Research → Plan

```bash
sessions_spawn \
  --task "Analyze research/oauth2-findings.md and create implementation plan: Design OAuth2 server architecture using simple-oauth2 library. Create workflows/oauth2-implementation-plan.md with: 1) Component breakdown (auth endpoints, token storage, middleware), 2) File structure, 3) Database schema changes, 4) Implementation phases with time estimates, 5) Testing strategy, 6) Risk analysis. Break down into 5-7 task_queue.py items." \
  --label "analyst-oauth2" \
  --cleanup keep \
  --runTimeoutSeconds 900
```

### Requirements → Architecture

```bash
sessions_spawn \
  --task "Analyze TSP testnet requirements and design deployment architecture: Review docs/requirements.md and create workflows/deployment-architecture.md. Include: 1) Infrastructure diagram (VPS, containers, database, reverse proxy), 2) Component deployment strategy, 3) Environment configuration (dev/staging/prod), 4) Backup and recovery plan, 5) Monitoring approach, 6) Rollback procedure, 7) Cost estimate. Identify risks and mitigation strategies." \
  --label "analyst-deployment" \
  --cleanup keep \
  --runTimeoutSeconds 1200
```

### Technical Debt Assessment

```bash
sessions_spawn \
  --task "Analyze codebase for technical debt: Review src/ directory and create reviews/technical-debt-assessment.md. Identify: 1) Deprecated patterns (datetime.utcnow usage, etc.), 2) Missing error handling, 3) Inadequate test coverage, 4) Documentation gaps, 5) Performance bottlenecks, 6) Security concerns. Prioritize by impact (HIGH/MEDIUM/LOW) and effort. Create refactoring plan with estimated hours per item." \
  --label "analyst-tech-debt" \
  --cleanup keep \
  --runTimeoutSeconds 1200
```

### Performance Analysis

```bash
sessions_spawn \
  --task "Analyze PostgreSQL query performance: Review logs/slow-queries.log and src/db/ query patterns. Create workflows/database-optimization-plan.md with: 1) Identified slow queries with execution times, 2) Missing indexes, 3) N+1 query problems, 4) Connection pool tuning recommendations, 5) Query refactoring suggestions, 6) Caching strategy, 7) Before/after performance estimates. Include implementation priority and risk assessment." \
  --label "analyst-db-performance" \
  --cleanup keep \
  --runTimeoutSeconds 900
```

### Feature Breakdown

```bash
sessions_spawn \
  --task "Break down 'agent reputation system' feature: Read docs/reputation-spec.md and create workflows/reputation-implementation-plan.md. Include: 1) Database schema (reputation_events table, indexes), 2) API endpoints (/reputation/:agent_id, POST /reputation/event), 3) Scoring algorithm (time decay, category weights), 4) Component breakdown (collector, calculator, API), 5) Testing strategy (unit, integration, load), 6) 8-10 task_queue.py items with dependencies mapped, 7) 3-week timeline with milestones." \
  --label "analyst-reputation" \
  --cleanup keep \
  --runTimeoutSeconds 1200
```

### Migration Strategy

```bash
sessions_spawn \
  --task "Design database migration strategy: We're moving from JSON file storage to PostgreSQL for trust scores. Create workflows/migration-to-postgres.md with: 1) Data migration script plan, 2) Rollback procedure, 3) Downtime estimate and mitigation, 4) Data validation approach, 5) Dual-write period strategy, 6) Cutover checklist, 7) Risk analysis for data loss/corruption. Include step-by-step timeline and success criteria." \
  --label "analyst-migration" \
  --cleanup keep \
  --runTimeoutSeconds 1200
```

### Security Review Plan

```bash
sessions_spawn \
  --task "Create security hardening plan for TSP: Review current setup (TOOLS.md, src/auth/, src/api/) and create workflows/security-hardening-plan.md. Include: 1) Authentication vulnerabilities assessment, 2) API security improvements (rate limiting, input validation), 3) Database security (connection encryption, credential rotation), 4) Secrets management strategy, 5) Dependency vulnerability scan approach, 6) Security testing plan, 7) Prioritized task list with risk ratings. Reference OWASP Top 10." \
  --label "analyst-security" \
  --cleanup keep \
  --runTimeoutSeconds 1200
```

## Analysis Quality Checklist

Good analyst output includes:

- ✅ **Clear architecture**: Components and interactions well-defined
- ✅ **Actionable steps**: Coder can follow plan without ambiguity
- ✅ **File structure**: Exact paths for where code goes
- ✅ **Dependencies**: All external and internal deps identified
- ✅ **Risk analysis**: Potential problems and mitigations
- ✅ **Time estimates**: Realistic hours/days per phase
- ✅ **Testing strategy**: How to verify it works
- ✅ **Task breakdown**: Ready for task_queue.py or coder spawn

Bad analyst output:

- ❌ Vague architecture ("build a good system")
- ❌ No actionable steps (too high-level)
- ❌ Missing file structure
- ❌ Unidentified dependencies
- ❌ No risk consideration
- ❌ No time estimates
- ❌ No testing approach
- ❌ Can't translate to tasks

## Integration Patterns

### Research → Analysis → Implementation Pipeline

```bash
# Phase 1: Research
sessions_spawn --task "Research [TOPIC]..." --label "researcher-[topic]" --cleanup keep

# Phase 2: Analysis (after research)
sessions_spawn --task "Read research/[topic]-findings.md and create implementation plan..." --label "analyst-[topic]" --cleanup keep

# Phase 3: Implementation (after analysis)
sessions_spawn --task "Implement [FEATURE] following workflows/[topic]-plan.md..." --label "coder-[topic]" --cleanup keep
```

### Parallel Analysis for Large Projects

```bash
# Break analysis into specialized areas
sessions_spawn --task "Analyze data layer architecture..." --label "analyst-data" --cleanup keep
sessions_spawn --task "Analyze API layer architecture..." --label "analyst-api" --cleanup keep
sessions_spawn --task "Analyze frontend architecture..." --label "analyst-frontend" --cleanup keep

# After all complete, spawn integrator analyst
sessions_spawn --task "Integrate all architecture plans into unified system design..." --label "analyst-integration" --cleanup keep
```

### Iterative Analysis

```bash
# Initial analysis
sessions_spawn --task "Create high-level architecture for [SYSTEM]..." --label "analyst-[topic]-v1" --cleanup keep

# After review/feedback
sessions_spawn --task "Refine workflows/[topic]-plan.md based on feedback: [FEEDBACK]. Update architecture, revise estimates, add missing details." --label "analyst-[topic]-v2" --cleanup keep
```

## Common Analysis Patterns

### "Plan from Research"

```
Analyze [research findings]:
1. Read: research/[topic]-findings.md
2. Extract: key recommendations, chosen approach
3. Design: architecture implementing recommendation
4. Plan: step-by-step implementation
5. Estimate: time and effort per phase
6. Identify: risks and mitigation
7. Output: workflows/[topic]-plan.md
```

### "Break Down Feature"

```
Break down [feature]:
1. Read: feature specification
2. Identify: major components
3. Map: component dependencies
4. Design: database schema, API contracts
5. Create: file structure
6. Break into: 8-12 task_queue.py items
7. Estimate: timeline with milestones
8. Output: workflows/[feature]-plan.md
```

### "Architecture Review"

```
Review [system] architecture:
1. Analyze: current implementation in src/
2. Identify: pain points, bottlenecks, tech debt
3. Design: improved architecture
4. Create: migration strategy from current to improved
5. Assess: risks and effort
6. Output: workflows/[system]-refactor-plan.md
```

### "Trade-off Analysis"

```
Compare [approach A] vs [approach B]:
1. Define: evaluation criteria
2. Analyze: each approach against criteria
3. Create: comparison matrix with scores
4. Identify: pros, cons, risks for each
5. Consider: team skill, timeline, maintenance
6. Recommend: choice with detailed reasoning
7. Output: workflows/[topic]-decision.md
```

## Tips for Effective Analyst Spawns

### Provide Context

❌ Bad: "Make a plan"
✅ Good: "Read research/oauth2-findings.md (recommendation: simple-oauth2) and create implementation plan for TSP agent authentication"

### Define Scope

❌ Bad: "Design the whole system"
✅ Good: "Design OAuth2 authentication subsystem: auth endpoints, token storage, middleware integration"

### Specify Detail Level

❌ Bad: "Create architecture"
✅ Good: "Create architecture with component diagram, file structure, database schema, and task breakdown ready for coder"

### Include Constraints

❌ Bad: "Design deployment"
✅ Good: "Design deployment for single VPS (2GB RAM, 1 CPU), minimizing complexity, using Docker Compose"

### Set Output Format

❌ Bad: "Write some docs"
✅ Good: "Create workflows/[topic]-plan.md with architecture, phases, risks, and task breakdown"

## Monitoring Analyst Progress

```bash
# Check analyst status
sessions_list --kinds isolated | grep analyst

# View analyst output
sessions_history --sessionKey <analyst-session-key> --limit 20

# Check plan created
ls -lh workflows/

# Check for blockers
python3 tools/blocked_items.py list | grep analyst
```

## Handoff from Analyst

```bash
cat > memory/handoffs/analyst-to-coder-$(date +%Y%m%d).md << EOF
# Handoff: Analyst → Coder
**Date**: $(date -u '+%Y-%m-%d %H:%M UTC')
**Task**: [Feature name]
**From**: analyst-[topic]
**To**: coder-[topic]

## Plan Created

Primary: workflows/[topic]-plan.md

## Architecture Summary

[2-3 sentence architecture overview]

## Implementation Phases

1. Phase 1: [Name] - [N] hours
2. Phase 2: [Name] - [N] hours
3. Phase 3: [Name] - [N] hours

## Key Decisions

- [Decision 1]: Chose [option] because [reason]
- [Decision 2]: Using [approach] to handle [concern]

## Risks to Watch

- 🔴 [High risk] - [mitigation strategy]
- 🟡 [Medium risk] - [mitigation strategy]

## Next Steps for Coder

1. Read workflows/[topic]-plan.md completely
2. Start with Phase 1: [specific first task]
3. Follow file structure exactly as specified
4. Run tests after each phase
5. If blocked, check plan's "Open Questions" section

## Success Criteria

Code implementation should:
- [ ] Match architecture in plan
- [ ] Include all components specified
- [ ] Pass all tests outlined
- [ ] Follow file structure
EOF
```

## Troubleshooting

### Analyst Produces Vague Plan

Common issues:
- Task was too broad → Narrow scope, be more specific
- Missing input context → Provide research docs or requirements
- Not enough detail requested → Add "include file structure, task breakdown, time estimates"

### Plan Not Actionable

- Too high-level → Ask for detailed steps a coder can follow
- Missing dependencies → Request explicit dep list
- No file paths → Require exact file structure with paths

### Analyst Gets Stuck

```bash
# Check what they're analyzing
sessions_history --sessionKey <session> --limit 10

# May need more research first
# Or requirements are unclear
# Or problem needs breaking into smaller pieces
```

## Quality Review Checklist

After analyst completes, verify:

- [ ] Architecture clearly described
- [ ] All components identified
- [ ] File structure provided with paths
- [ ] Dependencies (external + internal) listed
- [ ] Implementation broken into phases
- [ ] Time estimates provided
- [ ] Testing approach defined
- [ ] Risks identified with mitigations
- [ ] Success criteria measurable
- [ ] Next steps actionable

---

**Philosophy**: Good analysis turns fuzzy problems into clear, actionable plans. The analyst bridges the gap between "what we want" and "how to build it." A coder should be able to follow the plan without making major design decisions.
