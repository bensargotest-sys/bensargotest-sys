# AI-Powered Patent Prior Art Discovery: Product Strategy

**Date:** March 6, 2026  
**Status:** Brutal honesty mode engaged

---

## Executive Summary: The Uncomfortable Truth

**The thesis is sound. The execution is harder than you think. The competitive moat is thin. But there's a viable path.**

The good news: AI *can* find prior art humans missed. The bad news: well-funded companies with 100+ engineers are already doing this. The neutral news: they're selling to corporations for $50K+/year. You're proposing to give it away. That's either brilliant disruption or financial suicide. Let's figure out which.

---

## 1. WHAT TO BUILD (MVP)

### The Brutal Minimum (2 weeks)

**Goal:** Prove AI can find prior art that invalidates ONE high-value patent that no existing tool flagged.

**What you're building:**
- A Python script, not a product
- Input: USPTO patent number
- Output: A markdown report ranking top 10 prior art candidates with relevance scores
- That's it. No UI. No database. No scaling.

**Tech stack (total cost: $0-200/month):**
```
Core:
├── Python 3.11+ (free)
├── OpenAI API / Anthropic API (~$50-100/mo)
├── Sentence transformers (free, runs locally or on vast.ai for $0.15/hr)
└── Git + markdown (free)

Data sources (all free tier):
├── Google Patents Public Data (BigQuery free tier: 1TB/mo)
├── USPTO Bulk Data (free download)
├── PubMed API (free, rate limited)
├── arXiv API (free)
├── Semantic Scholar API (free, 100 req/min)
└── The Lens.org API (free academic tier: 50k requests/mo)
```

**The 2-week pipeline:**

```
INPUT: US Patent #
  ↓
STEP 1: Parse patent claims (claims 1-3 only, ignore dependent claims)
  Tool: PatentPublicData library or manual XML parsing
  Output: Structured JSON of independent claims
  ↓
STEP 2: Extract core concepts from each claim
  Tool: GPT-4o-mini or Claude Haiku ($0.15/1M tokens)
  Prompt: "Extract the 5 most novel technical concepts from this claim"
  Output: Ranked list of concepts with synonyms/variations
  ↓
STEP 3: Generate semantic search queries
  Tool: Embedding model (sentence-transformers/all-mpnet-base-v2)
  Output: 10-20 query vectors
  ↓
STEP 4: Parallel search across sources
  ├── Google Patents (semantic search via embeddings)
  ├── PubMed (MeSH term expansion + semantic)
  ├── arXiv (category-filtered semantic search)
  ├── Semantic Scholar (cross-domain papers)
  └── The Lens (patent + scholarly literature)
  Output: Top 100 candidates per source (500 total documents)
  ↓
STEP 5: Re-rank by novelty destruction score
  Tool: GPT-4o or Claude Sonnet
  Prompt: "Does this document anticipate the patent claim? Score 0-100."
  Process: Batch process in groups of 50 (use structured outputs)
  Output: Ranked list with reasoning
  ↓
STEP 6: Generate human-readable report
  Format: Markdown with:
  - Patent summary
  - Top 10 prior art candidates
  - For each: relevance score, publication date, key overlapping concepts, PDF link
  - Legal disclaimer: "This is research, not legal advice"
```

**What you CAN'T build in 2 weeks:**
- Multi-language search (stick to English)
- Conference proceedings (no good API)
- Wayback Machine search (too slow, no semantic search)
- A web UI (waste of time)
- User accounts (premature)
- A database (just use files)

### The Viable Product (2 months)

**Goal:** Process 50 pharma patents, find invalidating prior art for 3-5 of them, publish findings.

**Additions to MVP:**
1. **Automated batch processing:** Run 10 patents/day unattended
2. **Multi-language support:** Add Google Translate API for Chinese, Japanese, German, French patent abstracts ($20/1M chars)
3. **Citation network analysis:** Scrape forward/backward citations to find "hidden" prior art (patents citing patents that cite the target)
4. **Conference proceedings:** Manual scraping of IEEE Xplore, ACM Digital Library (use institution access or pay-per-download $30/paper)
5. **Temporal filtering:** Only search documents published BEFORE the patent's priority date (critical for legal validity)
6. **False positive filter:** Second-pass LLM check to eliminate weak matches
7. **Public website:** Static site (Hugo/Jekyll) hosted on GitHub Pages (free) showing:
   - Search index of analyzed patents
   - Full reports (PDF + web)
   - Methodology explanation
   - Submission form (Google Form) for patent suggestions

**Total cost at 2 months:** $300-500/month
- APIs: $200/mo (OpenAI/Anthropic, Google Translate)
- Compute: $50/mo (Vast.ai GPU instances)
- Misc: $50/mo (Google Workspace for forms, Cloudflare for CDN)

### The Defendable Product (6 months)

The "what stops a big player from copying this?" question is real. Here's your moat:

1. **Domain-specific training data:** Fine-tune an embedding model on 10,000 patent invalidation cases (manually labeled). This is tedious. Large companies won't bother because they already have products. Startups won't because they're building general tools.

2. **Citation network graph database:** Build a Neo4j graph of all patent citations + scholarly citations. This takes months of ETL work. It's boring but valuable.

3. **Expert validation dataset:** Partner with 10 generic drug companies or law clinics to validate your findings. Publish accuracy metrics. This is your credibility moat.

4. **Speed to market:** Publish 100 invalidation reports before anyone notices. Once you're the "known" brand for free prior art, you have distribution advantage.

**The moat is thin.** PatSnap or IPRally could replicate your core tech in a month. But they won't give it away for free because they have paying customers. That's your wedge.

---

## 2. SUCCESS CRITERIA

### Week 1: Proof of Concept
**MUST HAVE:**
- Pipeline runs end-to-end on 1 test patent (pick US10294290B2 - Pfizer's Ibrance cancer drug, expired 2023, good test case)
- Generates a report with 10 prior art candidates
- At least 1 candidate published before the patent's priority date (2008) that a human reviewer confirms "could be relevant"

**KILL CRITERIA:**
- If you can't parse USPTO XML or Google Patents data after 3 days → STOP, pivot to using existing APIs only
- If embedding search returns 100% irrelevant results (garbage in, garbage out) → Your concept extraction is broken, simplify it

### Month 1: MVP Validation
**MUST HAVE:**
- Process 10 pharma patents (focus on monoclonal antibodies, they're heavily patented and have rich prior art)
- Find at least 1 patent where your AI discovers prior art that:
  - Was NOT cited during prosecution (check USPTO file wrapper)
  - Was published before the priority date
  - A domain expert (PhD student, retired patent examiner, generic drug company IP person) confirms "this is interesting"

**SUCCESS METRICS:**
- **Technical:** 
  - 10 patents processed → 1000 prior art candidates generated → 100 passed first filter → 10 reach final report → 1-3 are "real finds"
  - Pipeline runtime: <2 hours per patent on $0.15/hr hardware
  - API costs: <$5 per patent
- **Validation:** 
  - 1+ "real find" confirmed by expert
  - 0 false claims (you haven't said something invalidates when it clearly doesn't)

**KILL CRITERIA:**
- After 10 patents, if ZERO prior art candidates pass basic expert review (they're all irrelevant or mis-dated) → Your pipeline is fundamentally broken
- If your "discoveries" are already on The Lens or in Orange Book listings → You're not finding anything new, just re-discovering public data
- If cost exceeds $10/patent → Not economically viable at scale

### Month 3: Traction / Product-Market Fit
**MUST HAVE:**
- 50 patents processed
- 5-10 "strong finds" (prior art that legitimately wasn't found during prosecution and is temporally valid)
- Public website with all 50 reports published
- 1,000+ website visitors (SEO, HN launch, Reddit r/bioinformatics, Twitter/X)
- 10+ submissions via your "suggest a patent" form
- 1+ mention in IP media (IPWatchdog, Law360, generic drug blogs)

**PRODUCT-MARKET FIT SIGNALS:**
- Generic drug companies start emailing you asking for custom searches (paid opportunity)
- Patent attorneys cite your reports in PTAB filings or litigation (validation)
- Unified Patents or EFF reaches out to discuss data sharing
- A pharma company's legal team sends a cease-and-desist (you're making an impact)

**KILL CRITERIA:**
- <100 website visitors after month 3 → No distribution, no one cares
- Zero inbound interest from generics/law firms/activists → No market pull
- Your "strong finds" get debunked by experts (dating errors, misunderstood claims) → Your methodology is flawed
- You find prior art but it's already been used in existing IPR challenges → You're late to every party

---

## 3. MEANS OF VERIFICATION

### The Legal Standard: Anticipation vs. Obviousness

**You need to understand patent law basics:**

- **Anticipation (35 U.S.C. § 102):** A SINGLE prior art reference that discloses EVERY element of a claim. This is hard to find but kills a patent instantly.
- **Obviousness (35 U.S.C. § 103):** Multiple references that, combined, make the invention obvious to a "person of ordinary skill in the art." This is easier to argue but requires more evidence.

**Your AI should target anticipation first** (single smoking-gun document), obviousness second (combination of 2-3 docs).

**DO NOT claim you've "invalidated" a patent.** Say: "We identified prior art that may be relevant to patentability." Legal weasel words matter.

### Validation Without $500K in Attorneys

**Free/cheap validation sources:**

1. **Law school IP clinics:** 
   - Duke, Stanford, Berkeley, Georgetown all have free IP clinics
   - They'll review your findings for educational purposes
   - Reach out to clinic directors, offer to be a "research partner"

2. **Retired patent examiners:**
   - Post on LinkedIn "seeking patent examiner feedback, $50/hour for consultation"
   - Many retirees do consulting, you can get 10 hours of expert review for $500

3. **Generic drug company IP teams:**
   - Companies like Teva, Sandoz, Mylan have in-house teams that WANT this data
   - Offer free early access in exchange for validation feedback
   - They won't sign NDAs, but they'll tell you "this is crap" or "this is interesting"

4. **Open-source validation:**
   - Post your top 10 findings on r/Patents, r/legaladvice (with disclaimers)
   - Patent nerds will tear you apart (for free)
   - If you survive the roasting, your methodology is probably sound

5. **Back-testing (CRITICAL):**
   - Find 20 patents that WERE invalidated in IPR proceedings (PTAB publishes all decisions)
   - Example: Search PTAB for "claims unpatentable" + pharmaceutical
   - Take the invalidated patent, the prior art that killed it, and the date it was filed
   - Run your AI on the patent (without telling it the answer)
   - Did your AI find the SAME prior art that killed it?
   - **Target: 70%+ hit rate** (find the killing prior art in your top 20 results)
   - If you hit 70%, your AI is competitive with human searchers

### Benchmarking Against Existing Tools

**Test datasets:**
1. Use the same 10 patents across:
   - Your tool (free)
   - Google Patents (free)
   - The Lens (free)
   - PatSnap (request a demo, test during trial)
   - IPRally (request a demo, test during trial)

2. **Metrics to compare:**
   - Coverage: How many prior art docs does each tool surface?
   - Precision: What % of top 10 results are actually relevant?
   - Recall: Did they find the "answer" (if back-testing on invalidated patents)?
   - Novelty: Did your tool find something the others missed?

3. **Publish the comparison:**
   - Make it an open methodology
   - Share the test dataset (patent numbers + results)
   - Let others replicate
   - This builds credibility

### Measuring False Positives

**The nightmare scenario:** Your AI says "this invalidates the patent" but it's wrong because:
- Document was published AFTER priority date (dating error)
- Document is a patent that itself was invalidated (you cited bad prior art)
- Document doesn't actually teach all claim elements (LLM hallucination)
- Document is in a different field (semantic search gone wild)

**False positive mitigation:**
1. **Automated date checking:** 
   - Extract publication date from every candidate
   - Flag any document within 1 year of priority date (ambiguous publication dates)
   - Require human review for borderline cases

2. **Claim element checklist:**
   - For each claim, break into elements (LLM task)
   - For each prior art candidate, check: "Does it teach element A? B? C?" (LLM task)
   - Only pass candidates that teach 100% of elements (anticipation) or 80%+ (obviousness combination)

3. **Human review of top 10:**
   - Never publish a report without a human reading the top 10 results
   - Use contract researchers (Upwork, Fiverr) - $50 for 2 hours of review per patent
   - They don't need to be patent attorneys, just scientifically literate

4. **Track accuracy over time:**
   - For every report you publish, track whether anyone challenges your findings
   - If a law firm or pharma company says "you're wrong," document why
   - Iterate on your methodology
   - Publish a "corrections" page (builds trust)

**Accuracy target:**
- **Precision (top 10 results relevant): >60%** - If a human would consider it worth reading, it counts
- **Recall (find the killer prior art in top 20): >70%** - Based on back-testing
- **False positive rate (claimed strong match but isn't): <5%** - You can't afford to cry wolf

---

## COMPETITIVE LANDSCAPE ANALYSIS

### What Already Exists (and Why You Might Be Screwed)

**Tier 1: Enterprise Tools (Not Your Competition)**
- **PatSnap ($30K-$100K/year):** 170M+ patents, AI semantic search, used by 12,000+ companies. They have $300M+ in funding. You can't compete on features.
- **IPRally ($10K-$50K/year):** Graph AI, knowledge graphs, used by Unilever, Össur. Their back-testing shows 50% time savings for patent attorneys. Your AI needs to beat this.
- **Ambercite:** Citation network analysis (finds non-obvious connections). Your MVP doesn't do this. You're missing a key signal.

**What they DON'T do:**
- Publish findings publicly (they're B2B SaaS, not a public good)
- Target patent invalidation specifically (they're "IP intelligence" generalists)
- Optimize for pharma evergreening (that's your niche)

**Tier 2: Free/Academic Tools (Your Actual Competition)**
- **The Lens.org:** FREE patent + scholarly search. 130M+ patents, 300M+ scholarly works. Semantic search. API access. Used by researchers worldwide.
  - **THREAT LEVEL: EXTREME.** They already do 80% of what you're proposing.
  - **Your edge:** They're a search tool, not an analysis service. You're publishing reports, not just providing search.

- **Google Patents:** FREE, fast, good UI. 100M+ patents. Basic semantic search.
  - **THREAT LEVEL: MEDIUM.** Good for known-unknown searches, bad at finding obscure prior art.
  - **Your edge:** Their AI is general-purpose. Yours is task-specific.

- **Unified Patents Prior Art Database:** FREE, community-driven, focuses on NPEs (non-practicing entities).
  - **THREAT LEVEL: HIGH.** They're already doing public-interest patent invalidation.
  - **Your edge:** They focus on tech patents (software, telecom). You're targeting pharma, which has a $10B+ invalidation market.

### How You're Different (Your Positioning)

**You are NOT:**
- A search tool (use existing APIs)
- A B2B SaaS (you're a public good)
- A litigation shop (you publish, others sue)

**You ARE:**
- An AI research service that publishes patent invalidation findings
- A public-interest project that targets evergreening abuse
- A signal for generic drug companies / activists / law firms

**Your 3 competitive advantages:**
1. **Pharma-specific:** Existing tools are general-purpose. You're optimizing for monoclonal antibodies, small molecules, formulations. You know the ANDA process, the Orange Book, the Hatch-Waxman Act.

2. **Public output:** PatSnap's users can't share findings (trade secrets). You're publishing everything. This creates a network effect (more eyes = more validation = more credibility).

3. **Invalidation-optimized:** Most tools are for "IP intelligence" (landscape analysis, FTO). You're specifically targeting "can we kill this patent?" That's a different prompt, different ranking algorithm, different output format.

### What Could Kill You

**Scenario 1: The Lens adds an "invalidation report" feature.**
- Likelihood: 30% in next 2 years
- Impact: Fatal (they have better data, more users, more credibility)
- Mitigation: Move fast. Get 100 reports published before they add the feature. Become the known brand.

**Scenario 2: Unified Patents launches a pharma-focused initiative.**
- Likelihood: 50% (they're already doing this in tech)
- Impact: Severe (they have $50M+ in funding, partnerships with Google/Cloudflare)
- Mitigation: Partner with them. Offer to be a data contributor. Don't compete, collaborate.

**Scenario 3: Pharma lobby pressures platforms to delist your findings.**
- Likelihood: 10% (Streisand effect risk)
- Impact: Medium (you move to decentralized hosting, BitTorrent, IPFS)
- Mitigation: Publish on multiple platforms (GitHub, Internet Archive, academic preprint servers). Make it uncensorable.

**Scenario 4: Your AI is just... wrong.**
- Likelihood: 60% in first 6 months (you WILL make dating errors, claim misinterpretations, false positives)
- Impact: Fatal (credibility destroyed)
- Mitigation: Conservative claims. Publish methodology. Accept corrections. Iterate openly.

---

## THE BRUTAL VERDICT

### This Idea Is Viable If:
1. You can back-test at 70%+ accuracy within Month 1
2. You focus on pharma (don't dilute to "all patents")
3. You publish fast (100 reports in 6 months)
4. You partner with Unified Patents, generics companies, or law clinics (you can't do this alone)
5. You treat this as a public-interest project, not a VC-backable startup (the revenue model is murky)

### This Idea Is Dead If:
1. The Lens already surfaces the same prior art you're finding (test this in Week 1)
2. You can't get expert validation (no one trusts a black-box AI)
3. Your false positive rate is >10% (you become a joke)
4. No one uses your reports after Month 3 (no distribution = no impact)

### The Real Business Model (Not What You Described)

**You said:** "Publish findings publicly, market pressure does the rest."

**Reality:** You need revenue or this dies when you run out of savings.

**Possible revenue streams:**
1. **Freemium:** Free reports on published patents. $500/month subscription for "watch list" alerts (notify me if prior art emerges for patents I care about).
2. **Custom searches:** Generics companies pay $5K-$50K for deep-dive invalidation reports on specific patents.
3. **Consulting:** You become a known expert, get hired for expert witness testimony ($500-$1000/hour).
4. **Data licensing:** Sell your prior art dataset to Unified Patents, The Lens, or academic researchers ($10K-$100K/year).

**The free public reports are your marketing.** They build credibility, distribution, and SEO. But you need a revenue layer or you're a nonprofit that needs grants (harder to scale).

---

## FINAL RECOMMENDATION

**BUILD IT. But with three changes:**

1. **Start with back-testing:** Don't touch a new patent until you've proven your AI can find prior art on 10 ALREADY-invalidated patents. This de-risks your methodology.

2. **Partner early:** Email Unified Patents, EFF, and 5 generic drug companies in Week 2. Say: "We're building this, want to be a validation partner?" Get feedback before you're too far down the wrong path.

3. **Plan for revenue from Day 1:** Even if you're giving 90% away, figure out the 10% that's monetizable. You need runway.

**This is not a $100M startup. This is a $1M/year lifestyle business with significant public impact.** That's not a bad outcome.

Now go prove me wrong.

---

**Next Steps (Your Week 1 Checklist):**
- [ ] Set up Python environment + APIs (OpenAI/Anthropic, The Lens, Google Patents)
- [ ] Find 10 pharma patents that were invalidated in IPR proceedings (PTAB database)
- [ ] Extract the "answer" (what prior art killed them?)
- [ ] Run your MVP on Patent #1 without looking at the answer
- [ ] Compare your top 20 results to the known answer
- [ ] If you found it: celebrate, iterate, do the other 9
- [ ] If you didn't: debug your concept extraction or search parameters
- [ ] Publish your back-testing results (even if they're bad) on GitHub

**Budget for Month 1:** $200
**Time investment:** 60-80 hours
**Kill/continue decision point:** Day 14

You're building a tool that could cost pharma companies billions in lost exclusivity. They will notice. Be ready.

---

*Document version: 1.0*  
*Last updated: March 6, 2026*  
*Next review: When you hit Month 1 metrics (or fail them)*
