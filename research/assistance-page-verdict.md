# Assistance Page: Devil's Advocate Verdict

**Date:** 2026-02-13  
**Question:** Should Sargo build partial settlement / assistance page feature?

---

## The Brutal Answer: **NO. Don't Build It.**

---

## 10 Reasons Agencies Won't Use It

1. **Zero customer demand** - No one's asking for it
2. **Agencies have alternatives** - Escrow, payment terms, invoice financing
3. **Trust problem unsolved** - Partial settlement doesn't create trust
4. **Complexity without benefit** - 3-4 weeks eng time, unclear ROI
5. **Solves wrong problem** - Root issue is trust or demand, not liquidity
6. **Suppliers won't want it** - Why accept partial when they can invoice?
7. **No network effects** - Feature needs scale you don't have
8. **Simpler alternative exists** - Multiple small orders instead of one partial
9. **Legal nightmare** - Disputes, taxes, compliance complexity
10. **Wrong priority** - 60 days to funding, focus on Base + 2nd client

---

## The Sarafu Lesson

**Sarafu's multilateral currency:**
- ✅ Technically elegant (bonding curves, AMMs, reserve)
- ❌ Actually used: 90% intra-community (simple bilateral suffices)
- **Lesson:** "Don't build for scale before you have scale"

**Sargo's partial settlement:**
- ✅ Technically interesting (smart contract escrow)
- ❌ Actually needed: Unknown (zero requests)
- **Risk:** Building solution for problem that doesn't exist

**Pattern:** Both are **solutions looking for problems**.

---

## What Would Make It Worth Building?

**Don't build until ALL of these are true:**

1. **3+ agencies explicitly request it** (not "might be nice", but "need this to place order")
2. **At least 1 agency regularly placing $500K+ orders** (proves scale exists)
3. **Legal scoping confirms low risk** (not a compliance nightmare)
4. **10+ clients using basic P2P successfully** (core product proven)
5. **Competitive pressure** (losing deals because you lack this feature)

**Current status:** 0 out of 5 conditions met

---

## What to Build Instead?

**Ask 2nd B2B prospect:** "What would make you switch to Sargo?"

**Likely answers (these are what to build):**
- Lower fees → optimize costs
- Faster settlement → ZK proofs (already planned)
- Multi-chain → Base launch (already planned)
- Better reporting → transaction dashboard
- API integration → webhooks for accounting

**Notice:** Partial settlement probably NOT on list.

---

## Alternative: Sales Theater (Smart)

**Don't build it, but show it:**
- Create Figma mockup (1 day)
- Show in demos: "We're exploring this"
- Ask: "Would you use this? At what order size?"
- Measure interest

**Decision rule:**
- If 3+ agencies say "I'd use this for $500K+ orders" → build
- If not → drop forever

**Time:** 2 hours customer interviews vs. 3-4 weeks engineering

**ROI:** Avoid building wrong thing = infinite

---

## The Real Questions

### "Why would agencies use this?"
**Honest answer:** We don't know. We haven't asked them.

### "What problem does this solve?"
**Possible:** Agency has $100K but wants to de-risk via incremental payment  
**Reality:** That's an extremely narrow use case  
**Simpler:** Just do 5x $20K orders over time (existing flow handles this)

### "Is this the simplest solution?"
**No.** Simpler options:
- Milestone payments (3 steps, not continuous partial)
- Deposit + balance (2 steps)
- Supplier-side financing (outsource complexity)

---

## The Opportunity Cost

**60 days to funding. 3 critical priorities:**

1. **Base launch** (Mar 10) ← Fundability
2. **2nd B2B client** (Mar 15) ← Repeatability  
3. **ZK proofs MVP** (Mar 10) ← Moat story

**Assistance page:**
- 3-4 weeks engineering time
- 25-33% of remaining runway
- **For a feature no one's asking for**

**Question:** What's more valuable?
- Close 3rd B2B client? (definitely)
- Improve ZK proofs? (definitely)
- Build partial settlement? (definitely not)

---

## Recommended Action

### Step 1: Customer Discovery (2 hours)
Ask 5 agencies:
- "Have you wanted to place large order but couldn't afford upfront payment?"
- "If yes, what order size? What stopped you?"
- "Would you trust crypto platform for partial payments?"
- "Why not use invoice financing instead?"

### Step 2: Decision Gate
- **If 3+ say yes:** Spec it based on real needs, revisit post-fundraise
- **If <3 say yes:** Drop it permanently

### Step 3: Focus
Build what gets you funded:
- Base launch
- 2nd client acquisition
- ZK proofs MVP

---

## Bottom Line

**You have 60 days and zero runway buffer.**

**Build:**
- ✅ What customers explicitly want
- ✅ What gets you funded
- ✅ What proves repeatability

**Don't build:**
- ❌ Clever features no one's asking for
- ❌ Solutions for problems that don't exist yet
- ❌ Complexity for theoretical future scale

**Verdict:** Assistance page = over-engineering. Don't do it.

**Sarafu taught us:** Simple beats clever. Social infrastructure beats technical sophistication. Solve actual pain, not imagined problems.

**Apply that here:** Focus on Base + 2nd client. Drop the assistance page.

---

**Full analysis:** `research/sargo-assistance-page-interrogation.md` (8K words, 10 angles, brutal honesty)
