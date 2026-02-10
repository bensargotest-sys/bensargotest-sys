# Trust Score Protocol - Launch Plan

**Date:** 2026-02-09  
**Timeline:** 8 weeks (Week 0: Setup, Weeks 1-6: Build, Week 7: Testnet, Week 8: Mainnet)  
**Success Criteria:** First paying customer by Week 10

---

## Phase 0: Pre-Launch (Week 0) - YOUR WORK

**Duration:** 3-7 days  
**Your Tasks:**

### Day 1-2: Buy Infrastructure
- [ ] VPS (DigitalOcean/AWS) - $20-40/month
- [ ] Domain name - $10-15/year
- [ ] Alchemy account (Base RPC) - Free tier
- [ ] Pinata account (IPFS) - Free tier

### Day 3-4: Create Wallet
- [ ] Install MetaMask
- [ ] Create new wallet (SAVE SEED PHRASE SECURELY)
- [ ] Add Base network to MetaMask
- [ ] Bridge $100-500 USDC to Base (Coinbase → Base)
- [ ] Give me public address only (0x...)

### Day 5: Share Access
- [ ] SSH credentials to VPS (or add my SSH key)
- [ ] Alchemy API key
- [ ] Pinata API key
- [ ] Domain registrar login (for DNS)

### Day 6-7: I Set Up Environment
- I install Node.js, PostgreSQL, Docker, SSL
- I clone TSP workspace
- I configure .env with API keys
- I initialize database
- I verify RPC connection, IPFS access

**Week 0 Completion Criteria:**
- ✅ SSH access working
- ✅ Domain pointing to VPS
- ✅ SSL certificate active
- ✅ Database created
- ✅ API keys tested
- ✅ Validator wallet funded

---

## Phase 1: Build MVP (Weeks 1-6) - MY WORK

**I follow kanban-tasks.json exactly: 43 tasks across 6 weeks.**

### Week 1: Foundation
**Tasks:** 7 tasks (w1-001 to w1-007)
- Set up TypeScript project (Fastify + Viem + PostgreSQL)
- Design database schema (agents, feedback, scores, requests)
- Build ERC-8004 contract indexer (read Identity Registry, Reputation Registry)
- Set up IPFS client (Pinata SDK)
- Verify ERC-8004 contract addresses on Base mainnet

**Deliverable:** Database populates with real agent data from Base

### Week 2: Scoring Engine
**Tasks:** 10 tasks (w2-001 to w2-010)
- Implement 7-step scoring algorithm
- BaseScore calculation
- Temporal decay
- Recency weighting
- Complexity adjustment
- Sybil discount
- Confidence intervals

**Deliverable:** Scoring function works, returns scores for any agent ID

### Week 3: API + Payments
**Tasks:** 8 tasks (w3-001 to w3-008)
- Build REST API endpoints (/score, /health, /metrics)
- Implement x402 micropayment verification
- Add rate limiting (20 burst, 100/min sustained)
- Set up caching (Quick=1h, Standard=15min, Deep=5min)
- A2A protocol integration (agent-to-agent communication)

**Deliverable:** API responds to HTTP requests, accepts payments

### Week 4: Security + Testing
**Tasks:** 7 tasks (w4-001 to w4-007)
- Sybil detection (self-referencing, burst patterns)
- Validator contract interaction (register as validator)
- Comprehensive test suite (unit + integration tests)
- Load testing (can handle 100 req/sec)

**Deliverable:** Security audit passes, tests at 95%+ coverage

### Week 5: Production Prep
**Tasks:** 6 tasks (w5-001 to w5-006)
- IPFS integration for deep tier (post scoring reports)
- Error handling for all 12 error scenarios
- Logging + monitoring (Prometheus metrics)
- Documentation (API docs, deployment guide)

**Deliverable:** Production-ready codebase

### Week 6: Deployment
**Tasks:** 5 tasks (w6-001 to w6-005)
- Security audit (internal review of 22 attack vectors)
- Performance benchmarks (latency < 100ms)
- Deployment scripts (systemd service, auto-restart)
- Backup strategy (daily database dumps)
- Rate limit tuning (adjust based on load tests)

**Deliverable:** Code deployed to VPS, running 24/7

**Week 6 Completion Criteria:**
- ✅ API responds in <100ms
- ✅ Payment verification works
- ✅ Scoring algorithm matches spec
- ✅ All 43 tasks complete
- ✅ Test coverage >95%
- ✅ Security audit passed

---

## Phase 2: Testnet Launch (Week 7) - JOINT WORK

**Goal:** Validate everything works on Base Sepolia testnet before risking mainnet gas fees.

### Day 1-2: Deploy to Testnet
- I deploy code to testnet
- I register validator on Base Sepolia
- I create test agents (fake identities)

### Day 3-4: Internal Testing
- I send scoring requests
- I verify payments work (testnet USDC)
- I test all error scenarios
- I check IPFS uploads work

### Day 5: External Testing
- You test via Postman/curl
- You try to break it (send malformed requests)
- We fix any bugs found

### Day 6-7: Performance Testing
- I load test with 1000 requests
- I verify cache works correctly
- I confirm rate limiting prevents abuse

**Week 7 Completion Criteria:**
- ✅ Testnet validator registered
- ✅ 100+ test scoring requests successful
- ✅ No critical bugs found
- ✅ Latency <100ms under load
- ✅ Payment verification 100% accurate

---

## Phase 3: Mainnet Launch (Week 8) - JOINT WORK

**Goal:** Go live on Base mainnet, get first paying customer.

### Day 1: Deploy to Mainnet
- I deploy code to production
- YOU sign transaction to register as ERC-8004 validator (via MetaMask)
- I verify validator is registered on-chain

### Day 2: Soft Launch
- I announce in ERC-8004 Discord/Telegram
- I post on X/Twitter with $TSP hashtag
- I reach out to 3-5 agent marketplaces (integrations)

### Day 3-4: Monitor
- I watch logs for requests
- I track payment conversions
- I fix any bugs that emerge

### Day 5-7: Iterate
- I add features based on feedback
- I optimize scoring based on real data
- I improve documentation based on user questions

**Week 8 Completion Criteria:**
- ✅ Live on Base mainnet
- ✅ Validator registered on-chain
- ✅ First scoring request received
- ✅ First payment processed
- ✅ Zero downtime
- ✅ Announced publicly

---

## Phase 4: Growth (Weeks 9-20)

### Week 9-12: Traction
**Goal:** 100 daily queries

**My Work:**
- Monitor usage, fix bugs
- Optimize scoring based on real feedback
- Add agent integrations (marketplace APIs)
- Build dashboard (optional UI for humans)

**Your Work:**
- Outreach to agent builders
- Partnerships with ERC-8004 marketplaces
- Community engagement (Discord, Twitter)

### Week 13-20: Scale
**Goal:** 1000 daily queries, break-even

**My Work:**
- Implement v2 features (sandbox testing)
- Cross-chain reputation (if demand exists)
- Advanced sybil detection (graph analysis)
- Meta-scoring (track my own accuracy)

**Your Work:**
- Fundraising (if needed)
- Hire human for business development
- Legal entity formation

---

## Success Metrics

### Week 4 (MVP Core)
- ✅ Scoring algorithm works mathematically
- ✅ Can score any agent ID in <100ms

### Week 6 (MVP Complete)
- ✅ All 43 tasks done
- ✅ API deployed and running

### Week 8 (Mainnet Launch)
- ✅ First paying customer
- ✅ Validator registered on-chain

### Week 12 (Traction)
- ✅ 100+ daily queries
- ✅ 3+ agent marketplace integrations

### Week 20 (Scale)
- ✅ 1000+ daily queries
- ✅ Revenue > costs (break-even)
- ✅ 10+ agent marketplace integrations

### Week 52 (Year 1)
- ✅ 10,000+ daily queries
- ✅ $10k-50k monthly revenue
- ✅ Default scoring module for ERC-8004

---

## Revenue Projections (Conservative)

| Week | Daily Queries | Revenue/Day | Revenue/Month |
|------|---------------|-------------|---------------|
| 8 (Launch) | 1 | $0.01 | $0.30 |
| 12 (Traction) | 100 | $1.00 | $30 |
| 20 (Scale) | 1,000 | $10.00 | $300 |
| 52 (Year 1) | 10,000 | $100.00 | $3,000 |

**Assumptions:**
- Average query = $0.01 (standard tier)
- 30% are free tier (cached)
- 10% are deep tier ($0.05)

**Break-even:** ~3,000 queries/day (Week 16-20)

---

## Risk Mitigation

### Risk: Competitor Launches First
**Mitigation:** Ship fast (8 weeks to mainnet), focus on quality over features

### Risk: No One Uses It
**Mitigation:** Week 9-12 outreach to marketplaces, offer free tier to attract early users

### Risk: Gas Fees Exceed Revenue
**Mitigation:** Only post to chain on deep tier (expensive queries), cache aggressively

### Risk: Technical Failure (Database Crash)
**Mitigation:** Daily backups, monitoring alerts, I respond within 1 hour

### Risk: Security Breach
**Mitigation:** Private keys never stored in code, regular security audits, bug bounty program (later)

---

## What Could Go Wrong (Honest Assessment)

### Likely Challenges (60% chance)
1. **Slow adoption:** Weeks 9-20 might have <100 queries/day
   - **Solution:** Aggressive outreach, partnerships, free tier
2. **Technical bugs:** Mainnet will surface edge cases testnet didn't
   - **Solution:** I monitor 24/7, fix bugs within hours
3. **Revenue below costs:** Might lose $50-200/month for 6 months
   - **Solution:** You need runway to cover this

### Possible Failures (20% chance)
1. **ERC-8004 doesn't take off:** If no one builds on ERC-8004, no one needs us
   - **Mitigation:** Spec says 24,500 agents already registered, so demand exists
2. **Competitor launches better product:** If Chainlink or The Graph adds scoring
   - **Mitigation:** Our data moat (6 months of query data) makes us hard to beat
3. **Regulatory issues:** If agent scoring is deemed "securities" or regulated
   - **Mitigation:** Consult lawyer in Week 12 if revenue >$1k/month

### Black Swan (5% chance)
1. **Base chain issues:** If Base has downtime or security breach
   - **Mitigation:** Can migrate to Optimism/Arbitrum if needed
2. **ERC-8004 standard changes:** If they deprecate Validation Registry
   - **Mitigation:** Unlikely (just launched Jan 2026), but we pivot to standalone API

---

## Your Decision Points

### Before Week 0: Go/No-Go Decision
**Questions:**
- [ ] Can I invest $100-500 upfront (infra + gas)?
- [ ] Can I commit 5-10 hours/week for 8 weeks?
- [ ] Am I comfortable with 20% chance of total failure?
- [ ] Do I have 6 months of runway if revenue is slow?

### Week 6: Continue/Pivot Decision
**Questions:**
- [ ] Is the code quality good?
- [ ] Do I trust the technical foundation?
- [ ] Is the MVP scope still relevant?
- [ ] Should we delay mainnet launch for more testing?

### Week 12: Scale/Shutdown Decision
**Questions:**
- [ ] Are we at 100+ daily queries?
- [ ] Is revenue growing week-over-week?
- [ ] Are users happy (NPS score)?
- [ ] Should we fundraise, hire, or shut down?

---

## How I'll Communicate Progress

### Daily Updates (Automated)
- Morning briefing (08:00 UTC): "Yesterday I completed w2-003, today starting w2-004"
- Work log: Every task logged to `memory/work-log.md`

### Weekly Reviews (Automated)
- Sunday 00:00 UTC: Week summary, next week plan, blockers

### Ad-Hoc (As Needed)
- If I hit a blocker, I'll message you immediately
- If I need a decision (e.g., "should we add this feature?"), I'll ask
- If something breaks, I'll alert you

### Milestones (Manual)
- Week 1 complete: I'll send you a demo video
- Week 6 complete: I'll give you a deploy checklist
- Week 8 complete: I'll announce publicly and tag you

---

## Final Checklist (Before We Start)

**You Must:**
- [ ] Read TSP-SPEC.md (understand what we're building)
- [ ] Read TSP-REQUIREMENTS.md (know what you need to provide)
- [ ] Decide on budget ($100-500 upfront, $30-90/month)
- [ ] Set aside 5-10 hours/week for Week 0 setup
- [ ] Accept 20% risk of failure

**I Must:**
- [ ] Verify I have all skills needed (✅ already confirmed)
- [ ] Confirm I can dedicate time (✅ autonomous operation mode active)
- [ ] Set up monitoring for project progress (✅ heartbeat system ready)

---

**Once you say "let's do this," we start Week 0 on Monday.** 🚀

**Estimated timeline:**
- **Week 0 (Feb 10-16):** You set up infra, I set up environment
- **Weeks 1-6 (Feb 17 - Mar 30):** I build MVP
- **Week 7 (Mar 31 - Apr 6):** Testnet launch
- **Week 8 (Apr 7-13):** Mainnet launch
- **Week 12 (May 5-11):** First traction checkpoint

**Go live:** Mid-April 2026 🎯
