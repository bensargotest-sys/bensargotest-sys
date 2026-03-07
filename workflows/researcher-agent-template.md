# Researcher Agent Template

Spawn a research agent to investigate topics, evaluate options, and provide evidence-based recommendations.

## When to Use

- Need to evaluate multiple approaches/libraries/tools
- Require evidence-based decision making
- Want structured comparison of options
- Need deep dive into documentation/specs
- Want to avoid wasting time on dead ends

## Quick Spawn

```bash
sessions_spawn \
  --task "Research [TOPIC]: Find 3-5 [RESOURCES], compare [CRITERIA], document findings in research/[topic]-findings.md with citations and recommendation." \
  --label "researcher-[topic]" \
  --cleanup keep \
  --runTimeoutSeconds 900
```

## Template Variables

- `[TOPIC]` - What to research (e.g., "OAuth2 libraries", "PostgreSQL vs MongoDB", "deployment options")
- `[RESOURCES]` - What to find (e.g., "libraries", "articles", "tools", "APIs")
- `[CRITERIA]` - How to compare (e.g., "features, security, performance", "cost, reliability, ease of use")
- `[topic]` - Lowercase slug for filenames (e.g., "oauth2", "database-comparison")

## Standard Task Format

```
Research [TOPIC]: 
1. Find [N] [RESOURCES] for [USE CASE]
2. Compare based on: [CRITERION 1], [CRITERION 2], [CRITERION 3]
3. Evaluate: [SPECIFIC QUESTIONS]
4. Document findings in research/[topic]-findings.md
5. Include: comparison table, pros/cons, recommendation with reasoning
6. Cite sources with URLs
```

## Expected Outputs

Researcher agents should produce:

### Primary Deliverable: `research/[topic]-findings.md`

```markdown
# Research: [TOPIC]
**Date**: YYYY-MM-DD
**Researcher**: [agent label]
**Purpose**: [Why this research was needed]

## Summary

[2-3 sentence executive summary with recommendation]

## Options Evaluated

### Option 1: [Name]
- **Description**: [What it is]
- **Pros**: 
  - [Advantage 1]
  - [Advantage 2]
- **Cons**:
  - [Disadvantage 1]
  - [Disadvantage 2]
- **Best for**: [Use cases where this excels]
- **Source**: [URL]

[Repeat for each option]

## Comparison Table

| Criterion | Option 1 | Option 2 | Option 3 | Winner |
|-----------|----------|----------|----------|--------|
| [Feature] | [Value]  | [Value]  | [Value]  | ⭐     |
| [Feature] | [Value]  | [Value]  | [Value]  | ⭐     |

## Key Findings

1. **[Finding 1]**: [Description] - Implication: [What this means]
2. **[Finding 2]**: [Description] - Implication: [What this means]

## Recommendation

**Choice**: [Selected option]

**Reasoning**:
- [Reason 1]
- [Reason 2]
- [Reason 3]

**Risks**:
- 🔴 [High risk]: [Description] - Mitigation: [How to handle]
- 🟡 [Medium risk]: [Description] - Mitigation: [How to handle]

## Next Steps

1. [Action for analysis/implementation phase]
2. [Action for analysis/implementation phase]

## References

- [Source 1]: [URL] - [Why relevant]
- [Source 2]: [URL] - [Why relevant]
```

### Supporting Files

- `research/[topic]-comparison-data.json` - Structured comparison data
- `research/[topic]-references.md` - Detailed source list with notes
- `research/[topic]-examples.md` - Code examples or usage patterns

## Example Spawns

### Library Evaluation

```bash
sessions_spawn \
  --task "Research Node.js email libraries: Find 5 popular options (Nodemailer, EmailJS, SendGrid SDK, etc.). Compare based on: features, reliability, documentation quality, maintenance status, and pricing for 10k emails/month. Document in research/email-libraries.md with recommendation for TSP notification system." \
  --label "researcher-email" \
  --cleanup keep \
  --runTimeoutSeconds 600
```

### Technology Comparison

```bash
sessions_spawn \
  --task "Research container orchestration options: Compare Docker Compose, Kubernetes, Docker Swarm, and Nomad for single VPS deployment. Evaluate: complexity, resource usage, monitoring, backup/restore, upgrade path. Document in research/orchestration-comparison.md. Recommend best option for our current VPS setup." \
  --label "researcher-orchestration" \
  --cleanup keep \
  --runTimeoutSeconds 900
```

### Security Audit Research

```bash
sessions_spawn \
  --task "Research JWT security best practices: Find 5-7 authoritative sources (OWASP, RFC, security blogs). Document: token storage, expiry, refresh patterns, common vulnerabilities, signing algorithms. Output: research/jwt-security.md with implementation checklist for TSP." \
  --label "researcher-jwt-security" \
  --cleanup keep \
  --runTimeoutSeconds 600
```

### API Investigation

```bash
sessions_spawn \
  --task "Research GitHub API v4 (GraphQL): Document rate limits, authentication methods, webhook capabilities, and repo/issue/PR operations we need for TSP monitoring. Include code examples. Output: research/github-api-guide.md with integration recommendations." \
  --label "researcher-github-api" \
  --cleanup keep \
  --runTimeoutSeconds 600
```

### Performance Benchmarking

```bash
sessions_spawn \
  --task "Research PostgreSQL performance tuning for our VPS (2GB RAM, 1 CPU). Find 5-7 guides on configuration optimization. Document: recommended settings for pg_config, connection pooling options, indexing strategies. Test queries provided in docs/slow-queries.sql and document results. Output: research/postgres-tuning.md with specific config recommendations." \
  --label "researcher-postgres-perf" \
  --cleanup keep \
  --runTimeoutSeconds 900
```

### Deployment Options

```bash
sessions_spawn \
  --task "Research testnet deployment options for Solana smart contracts: Compare Remix IDE, Solana CLI, Anchor framework, and Hardhat alternatives. Evaluate: ease of use, debugging tools, cost, documentation. We have contracts/ ready but unclear on best deploy path. Output: research/solana-deploy-options.md with step-by-step recommendation." \
  --label "researcher-solana-deploy" \
  --cleanup keep \
  --runTimeoutSeconds 900
```

## Research Quality Checklist

Good researcher output includes:

- ✅ **Multiple sources**: 3-5 options compared (not just one)
- ✅ **Evidence-based**: URLs and citations for all claims
- ✅ **Structured comparison**: Table or clear criteria-based evaluation
- ✅ **Pros and cons**: Honest assessment, not just positives
- ✅ **Clear recommendation**: Specific choice with reasoning
- ✅ **Risk analysis**: What could go wrong, how to mitigate
- ✅ **Actionable next steps**: What should happen after this research
- ✅ **Examples included**: Code snippets, config samples, or usage patterns

Bad researcher output:

- ❌ Only researched one option
- ❌ No sources or citations
- ❌ Vague comparisons ("A is better than B")
- ❌ No recommendation or "it depends"
- ❌ Ignored negative aspects
- ❌ No consideration of risks
- ❌ Leaves next steps ambiguous

## Integration Patterns

### Research → Analysis → Implementation Pipeline

```bash
# Phase 1: Research
sessions_spawn \
  --task "Research [TOPIC]..." \
  --label "researcher-[topic]" \
  --cleanup keep

# Wait for completion, then spawn analyst
sessions_spawn \
  --task "Read research/[topic]-findings.md and create detailed implementation plan in workflows/[topic]-plan.md. Include architecture, file structure, dependencies, testing approach." \
  --label "analyst-[topic]" \
  --cleanup keep

# Wait for plan, then spawn coder
sessions_spawn \
  --task "Implement [FEATURE] following workflows/[topic]-plan.md..." \
  --label "coder-[topic]" \
  --cleanup keep
```

### Parallel Research Coordination

```bash
# Spawn multiple researchers in parallel
sessions_spawn --task "Research authentication options..." --label "researcher-auth" --cleanup keep
sessions_spawn --task "Research database options..." --label "researcher-db" --cleanup keep
sessions_spawn --task "Research hosting options..." --label "researcher-hosting" --cleanup keep

# Monitor with:
python3 tools/subagent_log.py

# After all complete, spawn integrator
sessions_spawn \
  --task "Review research/auth-findings.md, research/db-findings.md, research/hosting-findings.md. Create unified architecture plan combining all recommendations. Output: workflows/full-stack-architecture.md" \
  --label "architect-integration" \
  --cleanup keep
```

## Common Research Patterns

### "Best Tool for X" Research

```
Research [TOOL TYPE] for [USE CASE]:
1. Find 5 popular/recommended options
2. Compare: features, ease of use, documentation, community, pricing
3. Check: last update, GitHub stars, npm downloads, issues
4. Evaluate security: known vulnerabilities, maintenance status
5. Document in research/[tool-type]-comparison.md
6. Recommend best option with reasoning
```

### "How to X" Research

```
Research how to [TASK]:
1. Find 5-7 authoritative guides/tutorials
2. Document: recommended approach, common pitfalls, best practices
3. Extract: step-by-step process, required tools, gotchas
4. Include: code examples, config samples
5. Output: research/[task]-guide.md with implementation checklist
```

### "X vs Y" Research

```
Research [OPTION A] vs [OPTION B] for [USE CASE]:
1. Document both options thoroughly
2. Compare: [criterion 1], [criterion 2], [criterion 3]
3. Find real-world examples/case studies
4. Identify: when to use A, when to use B
5. Output: research/[a-vs-b]-comparison.md with decision matrix
```

### "Is X Worth It" Research

```
Research feasibility of [APPROACH/TOOL]:
1. Document benefits and costs
2. Find similar implementations/case studies
3. Identify risks and mitigation strategies
4. Calculate ROI or effort estimate
5. Output: research/[approach]-feasibility.md with go/no-go recommendation
```

## Tips for Effective Research Spawns

### Be Specific

❌ Bad: "Research databases"
✅ Good: "Research PostgreSQL vs MongoDB for storing agent trust scores with 1M records, comparing query performance, ACID guarantees, and JSON handling"

### Define Success Criteria

❌ Bad: "Find some options"
✅ Good: "Find 5 options, compare on X/Y/Z criteria, recommend top choice with reasoning"

### Set Reasonable Scope

❌ Bad: "Research everything about Kubernetes" (too broad)
✅ Good: "Research Kubernetes vs Docker Compose for single VPS deployment" (focused)

### Specify Output Format

❌ Bad: "Document your findings"
✅ Good: "Document in research/[topic].md with comparison table, pros/cons, and recommendation"

### Include Context

❌ Bad: "Research OAuth2 libraries"
✅ Good: "Research OAuth2 libraries for Node.js/TypeScript that support authorization code flow, for TSP agent authentication system"

## Monitoring Research Progress

```bash
# Check researcher status
sessions_list --kinds isolated | grep researcher

# View researcher logs
sessions_history --sessionKey <researcher-session-key> --limit 20

# Check if research file created
ls -lh research/

# Check for blockers
python3 tools/blocked_items.py list | grep researcher
```

## Handoff to Next Phase

After research completes, create handoff document:

```bash
# Create handoff for analyst
cat > memory/handoffs/research-to-analysis-$(date +%Y%m%d).md << EOF
# Handoff: Research → Analysis
**Date**: $(date -u '+%Y-%m-%d %H:%M UTC')
**Task**: [Topic]
**From**: researcher-[topic]
**To**: analyst-[topic]

## Research Completed
- Primary: research/[topic]-findings.md
- Recommendation: [Selected option]

## Key Findings
1. [Finding 1]
2. [Finding 2]

## Next Steps for Analyst
1. Read research/[topic]-findings.md
2. Design implementation plan based on [recommendation]
3. Create workflows/[topic]-plan.md with architecture and task breakdown
EOF
```

## Troubleshooting

### Researcher Gets Stuck

```bash
# Check what they're doing
sessions_history --sessionKey <session> --limit 5

# If blocked, check blocked_items.py
python3 tools/blocked_items.py list

# If taking too long, may need to increase timeout
# (default 300s, research often needs 600-900s)
```

### Researcher Produces Weak Output

Common issues:
- Task was too vague → Rewrite with specific criteria
- Not enough time → Increase runTimeoutSeconds
- No clear success criteria → Add "must include X, Y, Z"
- Topic too broad → Narrow the scope

### Researcher Can't Find Information

- Check if task is researchable (some questions need experimentation)
- May need to split into multiple research tasks
- Consider spawning a coder to build prototype instead

---

**Philosophy**: Good research saves implementation time. An hour of research can prevent days of wrong-direction coding. The researcher's job is to find the path, not walk it.
