# Sargo 90-Day Strategy: Fundraising & Product Prioritization

**Date:** February 13, 2026  
**Timeline:** Now → Mid-April 2026 (60-75 days runway)  
**Team:** 3 people, 50% salary cuts  
**Current state:** 1 retained B2B client, Celo live, Base pending  

---

## Executive Summary

**The fundability question:** VCs need to see **repeatable B2B traction + technical differentiation + clear growth trajectory** by end of March.

**Core strategy:** Ruthlessly prioritize revenue-generating activities. Base launch + 2nd B2B client are the twin engines of fundability. ZK proofs are the moat story. Everything else defers.

**Critical path:** 
- **Week 1-2 (Feb 13-23):** Prep for Variant dinner with momentum proof points
- **Week 3-6 (Feb 24-Mar 15):** Execute Base launch + close 2nd B2B client
- **Week 7-10 (Mar 16-Apr 15):** Fundraise aggressively with traction data + push for term sheet

---

## 1. Product Roadmap: Build vs Defer

### 🚀 BUILD NOW (Feb-Mar)

#### Priority 1: Base Launch (Weeks 1-4)
**Timeline:** Ship by March 10  
**Why:** Strategic positioning. Base = Coinbase ecosystem = VC credibility + potential Coinbase Ventures interest.  
**Blockers to resolve:**
- Smart contract deployment (1 week)
- Liquidity bootstrapping (partner with existing Base DEX, don't build own)
- Compliance review (Base is US-focused, need clean story)

**Value prop for Base:**
- Lower fees than Celo (attracts price-sensitive B2B users)
- Access to Coinbase's 100M+ user base for future B2C expansion
- Ethereum L2 credibility (VCs love ETH ecosystem more than Celo)

**Success metric:** $50K+ volume in first 30 days on Base (shows market demand)

#### Priority 2: 2nd B2B Client Acquisition (Weeks 1-6)
**Timeline:** Close by March 15  
**Why:** Proves repeatability. 1 client = lucky. 2 clients = pattern. 3 clients = platform.

**Who to target:**
- **Remittance corridors with Kenya shillings:** NGOs, payroll providers, cross-border payment firms
- **Ideal profile:** $100K-500K/month volume potential, existing pain with high fees or slow settlement
- **Specific leads to pursue:**
  - **Microfinance institutions** (MFIs) in Kenya - they move money cross-border for lending
  - **Payroll processors** for remote teams (Kenya is remote work hub)
  - **Crypto OTC desks** needing KES liquidity

**Sales approach:**
- Leverage existing client as reference (case study: "We saved Client X $Y in fees")
- Offer 90-day pilot with volume-based pricing (align incentives)
- Emphasize trust/speed via express lane (once ZK proofs are ready)

**Success metric:** 1 signed LOI + 1 active pilot by March 15

#### Priority 3: ZK Proofs MVP (Weeks 2-6)
**Timeline:** Working prototype by March 10  
**Why:** This is your **technical moat**. Express lane with fraud-proof settlements is defensible.

**Scope:**
- Prove sender has funds without revealing balance (basic ZK circuit)
- Integrate with express lane flow (reduce hold times for trusted users)
- Document security assumptions (for VC due diligence)

**Don't over-engineer:** Use existing ZK libraries (Circom, Noir), don't build from scratch.

**Success metric:** Demo to VCs showing instant settlement with ZK verification

---

### ⏸️ DEFER (Post-Fundraise)

#### Partial Settlement Concept
**Why defer:** High complexity, unclear immediate revenue impact. This is a "nice to have" for large orders, but you don't have large orders yet.  
**When to revisit:** After you have a client requesting $1M+ orders. Until then, focus on core P2P flow.

#### Patent Filing
**AB's instinct is correct:** Patents are expensive ($15K-30K), slow (18+ months), and don't matter for seed-stage fundability. VCs care about traction, not IP at this stage.  
**When to revisit:** Post-Series A when you have revenue + competitors nipping at your heels. For now, trade secrets > patents.

#### B2C Product
**Why defer:** B2B clients are more predictable revenue. B2C requires user acquisition spend you don't have runway for.  
**When to revisit:** After 5+ B2B clients, use them as distribution for B2C (white-label their apps).

---

## 2. Traction Milestones That Unlock VC Interest

### Define "Triple Current Volume"
First, need to know baseline. Assuming current volume = $X/month, define this concretely:
- **Transaction volume:** Dollar value of all trades (e.g., $100K → $300K/month)
- **Transaction count:** Number of P2P swaps (e.g., 500 → 1,500/month)
- **User growth:** Active wallets (e.g., 50 → 150 MAU)

**Recommendation:** Focus on **dollar volume** as primary metric (VCs care about revenue potential, not vanity metrics).

### Milestones by Timeline

#### By Feb 23 (Variant Dinner - 10 days)
- **Base testnet live** (show it works, even if not public)
- **2nd B2B prospect in pipeline** (signed NDA + scoping call)
- **Month-over-month growth:** Show 20-30% volume increase from existing client

**Story to tell Variant:** "We've proven Celo works. We're launching Base in 2 weeks to access 100M Coinbase users. We have 2 B2B clients in pipeline. We're building ZK proofs to enable instant trust. We need capital to scale GTM."

#### By Mar 15 (Pre-VC Blitz)
- **Base mainnet live** with $50K+ volume (30 days of data)
- **2 active B2B clients** (1 existing + 1 new)
- **ZK proofs MVP** (can demo to VCs)
- **2x volume growth** from baseline (not 3x yet, but clear trajectory)

**Story to tell VCs:** "We've de-risked product (multi-chain works). We've de-risked GTM (2 paying clients). We have technical moat (ZK proofs). Now we're ready to scale: hire sales, expand to more chains, onboard 10+ B2B clients in 12 months."

#### By Apr 1 (Term Sheet Target)
- **3x volume** from baseline (hit AB's goal)
- **$X in monthly recurring revenue** (even if small, shows monetization)
- **Base > 50% of volume** (proves multi-chain strategy works)
- **Pipeline of 3-5 additional B2B prospects** (shows scalability)

**Story to tell VCs:** "We've hit our milestones. We're capital-efficient (team on 50% salaries extended runway). We have clear path to $1M ARR in 12 months. We're raising to accelerate, not survive."

---

## 3. Fundraising Timeline: When to Push, What Proof Points Needed

### Feb 13-23: Prep Phase
**Focus:** Build proof points for Variant dinner  
**Actions:**
- Ship Base testnet + document launch plan
- Outreach to 10 B2B prospects (remittance, payroll, OTC desks)
- Prepare 1-pager: problem, solution, traction, ask

**Variant dinner prep:**
- Research Variant portfolio (what do they care about? DeFi, infrastructure, etc.)
- Prepare 3 questions to ask THEM (show you're selective, not desperate)
- Have specific ask: "$500K seed extension on [terms], close by March 15"

### Feb 24-Mar 15: Execution Phase
**Focus:** Ship Base + close 2nd client  
**Actions:**
- Base mainnet launch (Mar 1-10)
- 2nd B2B client signed (LOI or pilot agreement)
- ZK proofs MVP working (even if not production-ready)

**Funding actions:**
- **Heather @ Prelude.xyz:** Reconnect by Feb 25. Send update: "We're launching Base in 2 weeks, closing 2nd client, would love to chat about bridge round."
- **Charles (angel):** Send monthly update by Feb 28. Make specific ask: "$50K-100K on SAFE, close in 7 days." Angels move fast, don't wait.
- **Base grant:** Check status by Mar 1. If approved, announce publicly (credibility signal).

### Mar 16-Apr 15: Fundraise Sprint
**Focus:** Close term sheet  
**Actions:**
- Batch VC outreach (20-30 intros via warm connections)
- Send weekly investor updates (show momentum)
- Target: 5-8 partner meetings, 2-3 term sheets, pick best

**Proof points to emphasize:**
- "We 2x'd volume in 60 days" (show growth chart)
- "We launched Base in 4 weeks" (show execution speed)
- "We have 2 paying B2B clients" (show repeatability)
- "We built ZK proofs for fraud prevention" (show technical depth)

**Ask:** "$1M-1.5M seed round, $8M-10M post-money, close by April 10"

---

## 4. Risks + Mitigation

### Risk 1: Base launch delayed (technical issues)
**Impact:** Miss Variant dinner proof point, lose momentum story  
**Likelihood:** Medium (smart contract bugs, liquidity issues)  
**Mitigation:**
- Use audited contract templates (OpenZeppelin, don't reinvent)
- Partner with existing Base DEX for liquidity (Uniswap, Aerodrome)
- Have rollback plan: If Base isn't ready by Mar 10, pivot story to "launching in 2 weeks" with testnet demo

### Risk 2: 2nd B2B client doesn't close
**Impact:** Can't prove repeatability, VCs see you as one-trick pony  
**Likelihood:** High (sales cycles are slow, trust is hard in crypto)  
**Mitigation:**
- Pursue 5+ prospects in parallel (assume 20% close rate)
- Offer aggressive pilot terms (90 days free, then volume-based pricing)
- Get existing client to intro warm leads (referrals close faster)
- Fallback: Get 3 signed LOIs instead of 1 closed client (shows pipeline)

### Risk 3: Volume doesn't 3x
**Impact:** Miss AB's goal, VCs see flat growth  
**Likelihood:** Medium (depends on client engagement)  
**Mitigation:**
- Work with existing client to increase volume (offer incentives, solve their pain points)
- Count Base volume separately (even small numbers show multi-chain works)
- Reframe goal: "We 2x'd volume AND launched second chain" (still impressive)

### Risk 4: Fundraise takes longer than expected
**Impact:** Run out of runway in April  
**Likelihood:** High (fundraising always takes 2x longer than expected)  
**Mitigation:**
- Start fundraising NOW (don't wait for perfect traction)
- Pursue angel + VC in parallel (angels close faster, can bridge)
- Have emergency plan: If no term sheet by April 1, go to existing client for $100K bridge loan (desperate but survivable)
- Extend runway: Cut remaining salaries to 25% if needed (brutal but buys 30 days)

### Risk 5: ZK proofs don't work / too complex
**Impact:** Lose moat story, become commodity P2P platform  
**Likelihood:** Medium (ZK is hard)  
**Mitigation:**
- Use proven ZK libraries (Circom, Noir) instead of building from scratch
- Scope MVP narrowly: Just prove funds exist, not full privacy
- If blocked, pivot moat story to "multi-chain interoperability" or "B2B-first platform" (still defensible)

---

## 5. Resource Allocation: 3 People, 3 Months

Total capacity: **9 person-months**

### Recommended Split

#### Engineer 1: Full-Stack (50% Backend, 50% Frontend)
- **Weeks 1-4:** Base smart contracts + integration (4 weeks)
- **Weeks 5-8:** ZK proofs MVP (3 weeks)
- **Weeks 9-12:** B2B client customizations + bug fixes (5 weeks)

#### Engineer 2: Full-Stack (60% Backend, 40% DevOps)
- **Weeks 1-12:** Existing Celo platform maintenance + Base monitoring (ongoing)
- **Weeks 5-8:** Support ZK proofs integration (2 weeks)
- **Weeks 9-12:** Performance optimization for volume growth (4 weeks)

#### Founder/BD (100% Sales + Fundraising)
- **Weeks 1-2:** Variant prep + initial B2B outreach (2 weeks)
- **Weeks 3-6:** 2nd client sales (close by week 6) (4 weeks)
- **Weeks 7-12:** Fundraising sprint (20 VC meetings, close term sheet) (6 weeks)

### What We're NOT Staffing
- Marketing/content (defer until post-fundraise)
- Customer support (founders handle until 5+ clients)
- Legal (only as needed for client contracts)

### Capacity Realities
**Can realistically achieve:**
- Base launch (4 weeks eng time = doable)
- ZK proofs MVP (3 weeks = doable but tight)
- 1-2 B2B clients (6 weeks founder time = aggressive but possible)
- Fundraise (6 weeks = standard timeline)

**Cannot achieve in 90 days:**
- 3x volume (unless clients grow organically)
- Full ZK privacy (scope to MVP only)
- B2C product (no bandwidth)

---

## The Fundability Story

**By end of March, VCs should see:**

1. **Traction:** "We grew from $X to $2.5X volume in 60 days across 2 chains"
2. **Repeatability:** "We have 2 paying B2B clients + 3 prospects in pipeline"
3. **Technical moat:** "We're the only P2P platform with ZK-proof instant settlement"
4. **Market positioning:** "We're live on Base (Coinbase ecosystem) + Celo (emerging markets)"
5. **Capital efficiency:** "We extended runway 3 months on 50% salaries, now ready to scale"
6. **Clear ask:** "We're raising $1M-1.5M to hire 2 sales + 1 eng, onboard 10 B2B clients in 12 months, hit $1M ARR"

**The emotional story:** "We believed in this so much we cut our salaries in half to make it work. Now we've proven the model. We just need capital to scale."

---

## Immediate Next Actions (Next 48 Hours)

1. **Confirm baseline metrics:** What is current volume ($/month)? How many transactions? How many active users?
2. **Base launch scoping:** What are actual blockers? Smart contracts? Liquidity? Compliance?
3. **B2B prospect list:** Create list of 10 warm leads (ask existing client for intros)
4. **Variant dinner prep:** Draft 1-pager, research Variant portfolio, schedule prep call with team
5. **Reconnect with Heather:** Send email today: "Wanted to catch up on progress since we last spoke..."

---

## Final Recommendation: Patent Question

**Don't file patents now.** Here's why:

1. **Cost:** $15K-30K you don't have (that's 1-2 months of runway)
2. **Time:** 18+ months to issue (you need funding in 60 days)
3. **VC perspective:** Seed investors care about traction, not IP. Patents matter at Series A+.
4. **Defensibility:** Your moat is execution speed + B2B relationships, not patent protection.

**Alternative:** Document your ZK proof architecture internally (prior art defense) and move fast. If you raise a Series A, revisit then.

AB's instinct is correct. Stay focused on what unlocks funding: revenue, clients, growth.

---

**Strategy in one sentence:** Launch Base + close 2nd client by March 15, then fundraise aggressively with proof of multi-chain traction and technical differentiation.

**Time to execute: 60 days. Let's move.**
