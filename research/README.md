# Research Library

**Purpose:** Permanent storage for all research, analysis, and deep dives

**Philosophy:** Research dies in chat history. Research lives in files.

---

## Naming Convention

**Format:** `YYYY-MM-DD-topic-name.md`

**Examples:**
- `2026-02-10-reclaim-protocol.md`
- `2026-02-10-sargo-pivot-analysis.md`
- `2026-02-11-competitor-analysis-tsp.md`

**Why date-first:** Easy to sort chronologically, see research timeline

---

## File Structure

**Every research file should contain:**

```markdown
# Research: [Topic]

**Date:** YYYY-MM-DD  
**Question:** [What were we trying to answer?]  
**Commissioned by:** [AB / Self-initiated / Heartbeat task]

---

## Summary

[1-2 sentence summary of findings]

---

## Key Findings

1. [Finding 1]
2. [Finding 2]
3. [Finding 3]

---

## Detailed Analysis

[Full research content]

---

## Sources

- [Link 1]
- [Link 2]
- [Link 3]

---

## Related Files

- [Link to business context file]
- [Link to project doc]
- [Link to other research]

---

## Next Actions

[What should we do with this information?]
```

---

## Process

### Before Research
1. Check if similar research already exists (`grep` through research/)
2. If exists, update existing file instead of creating new

### During Research
1. Take notes in scratch file first
2. Organize findings
3. Identify key insights

### After Research
1. Create properly named research file
2. Document findings with structure above
3. Reference from related project/business files
4. Commit to git
5. Update this index (below)

---

## Research Index

### 2026-02-10
- **reclaim-protocol-analysis.md** - ZK-TLS for agent escrow feasibility
- **sargo-pivot-decision-analysis.md** - Agent payments vs TSP strategic analysis
- **qmd-tool-research.md** - QMD installation and usage for workspace search

### [Add new entries as research is done]

---

## Research Types

### Strategic Analysis
- Market sizing
- Competitive landscape
- Opportunity evaluation
- Pivot decisions

### Technical Research
- Tool evaluation
- Architecture options
- Implementation approaches
- Integration feasibility

### Customer/User Research
- Pain points
- Use cases
- Willingness to pay
- Feedback synthesis

### Competitive Intelligence
- Competitor features
- Pricing analysis
- Market positioning
- Differentiation opportunities

---

## Benefits of This System

**Short-term:**
- Never repeat the same research
- Reference findings months later
- Share context with future agents/teammates

**Long-term:**
- Build institutional knowledge
- Spot patterns across time
- Compound learning effect
- Train models on your specific domain

---

## Anti-Patterns (Don't Do This)

❌ Let research die in chat history  
❌ Take mental notes instead of writing  
❌ Save to random files without structure  
❌ Forget to commit to git  
❌ Skip the "Why this matters" context  

---

## Integration with Other Systems

**With memory system:**
- Daily logs reference research files
- Research findings flow into decisions

**With business context:**
- Business files link to supporting research
- Research informs strategy updates

**With SOPs:**
- Research on processes becomes SOPs
- Best practices documented

**With mistake log:**
- Research on why something failed
- Prevention strategies documented

---

**Every hour of research should pay dividends for years.**

**That's the difference between living files and dead files.**
