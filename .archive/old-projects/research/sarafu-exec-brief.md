# Sarafu Multilateral Currency - Executive Brief

**Date:** 2026-02-13  
**Full report:** `sarafu-multilateral-currency-deep-research.md` (20K words)

---

## What is Sarafu?

**Community Inclusion Currency (CIC) system** operating in Kenya since 2015.

**Scale:**
- 52,000+ users (2024)
- $3M annual trade volume
- 239 unique community currencies
- 9 years continuous operation
- Feature-phone accessible (no smartphone needed)

**Innovation:** Multiple community currencies trade with each other through Sarafu (reserve currency), creating interconnected network of local economies.

---

## How Multilateral Currency Works

### Traditional Problem
- Community A → Community B requires direct exchange rate
- 10 communities = 45 bilateral rates needed
- Creates fragmentation, limits trade

### Sarafu's Solution
- All communities hold reserves in Sarafu (network token)
- Community A → Sarafu → Community B (2 steps)
- 10 communities = only 10 rates needed (90% complexity reduction)

### Example Transaction
1. Farmer in rural Kwale holds 100 Kwale-Pesa
2. Wants to buy from shop in urban Nairobi
3. System: 50 Kwale-Pesa → Sarafu → Nairobi-Pesa
4. Transaction completes via SMS (USSD interface)
5. No direct Kwale/Nairobi exchange rate needed

---

## Key Mechanisms

### 1. Three-Layer Architecture
- **Layer 1:** Community currencies (CICs) - each chama issues own currency
- **Layer 2:** Sarafu reserve currency - connects all CICs
- **Layer 3:** Exchange mechanism - automated or fixed rates

### 2. Chamas (Savings Groups) as Anchor
- 15-30 member community groups
- Pre-existing trust networks
- Govern currency distribution via loans
- 211 registered chamas in system

### 3. USSD Interface (No Smartphone Needed)
- Feature-phone compatible
- Works without internet (cellular signaling)
- 90% population accessibility
- Critical for marginalized communities

### 4. Blockchain Backend
- xDAI (2020-2021), now Celo (2023+)
- Transparent transaction records
- Enables research and auditing
- Off-chain USSD interface + on-chain settlement

### 5. Currency Circulation Incentives
- **Demurrage:** 2% monthly holding fee (discourages hoarding)
- **Weekly rewards:** For active traders
- **Referral bonuses:** For onboarding new users
- **Result:** High velocity, continuous circulation

---

## Economic Model Evolution

### 2013-2017: Paper Currencies
- Physical vouchers in individual communities
- Bangla-Pesa, Gatina-Pesa, Lindi-Pesa, etc.
- **Result:** 22% income increase, 10% of food purchases

### 2017-2019: Digital Transition
- USSD interface launched
- Multiple digital currencies on blockchain
- **Result:** Scaled from 1,000 → 8,000 users

### 2020: Unified Sarafu
- Consolidated 12 currencies into one
- Simplified user experience
- COVID humanitarian response
- **Result:** 8,000 → 55,000 users in 17 months

### 2019 Experiment: Variable Exchange Rates
- Bonding curves (automated market maker)
- Exchange rates adjust based on trade flows
- **Result:** Too complex, encouraged speculation, ABANDONED

### 2020-2023: Fixed 1:1 Rates
- All CICs exchange 1:1 with Sarafu
- Simple, no arbitrage opportunities
- **Result:** Stable, predictable, user-friendly

### 2024: Commitment Pooling
- Communities create production commitment pools
- 33 pools established
- Less emphasis on exchange rates
- Focus on rotational labor (Mweria)
- **Result:** Return to mutual credit roots

---

## Proven Impacts

### Quantitative
- **Income:** +22% for participating businesses (Bangla-Pesa)
- **Food security:** 10% of purchases in CICs
- **Scale:** 52K users, 930K+ transactions (17 months)
- **Volume:** $3M annually
- **Accuracy:** 99.98% accounting precision

### Qualitative
- **Trust:** Positive correlation with community cohesion
- **Humanitarian:** Effective COVID-19 aid distribution
- **Digital inclusion:** 90% phone accessibility
- **Sustainability:** 9 years continuous operation

### COVID-19 Response (2020-2021)
- Red Cross partnership in Mukuru & Kisauni
- Enabled trade when Kenyan Shillings scarce
- Distributed health kits, food via CICs
- Multiplier effect: $1 donated → $4 local circulation

---

## Critical Analysis

### What Worked ✅
1. **Feature-phone accessibility** - 90% reach without smartphones
2. **Chamas as anchor** - pre-existing trust and governance
3. **Demurrage** - keeps currency circulating
4. **Humanitarian partnerships** - Red Cross, WFP, UNICEF legitimacy
5. **Open source** - transparent, auditable, replicable

### What Didn't Work ❌
1. **Variable exchange rates** - too complex, encouraged speculation
2. **Cash redemptions** - drained currency from circulation
3. **Complex narratives** - users don't understand bonding curves
4. **Telco costs** - SMS fees unsustainable at million-user scale

### Key Tensions
1. **Standardization vs. Autonomy**
   - Need common protocol for inter-trading
   - But communities want sovereignty over rules

2. **Market Efficiency vs. Social Obligation**
   - Price signals enable efficient trade
   - But erode community reciprocity norms

3. **Technical Complexity vs. User Simplicity**
   - Engineers love bonding curves and AMMs
   - Users prefer fixed rates they understand

4. **Proof:** Users learned to speculate when shown exchange rates
   - Behavior changed from social → financial optimization
   - Performativity: Economic models create behavior they assume

---

## Academic Critique vs. Founder Response

### Academic (Ester Barinaga)
**Critique:**
- Smart contracts erode community democracy
- System rules set by engineers, not communities
- Bonding curves encode homo economicus behavior
- Undermines chama reciprocity with profit-seeking

### Founder (Will Ruddick)
**Response:**
- Never used chama savings as reserves (false claim)
- Variable rates discontinued Dec 2019 (before paper)
- Non-profit foundation, not "crypto-entrepreneurs"
- Open source = communities can customize
- 2024 commitment pools return to mutual credit

**Verdict:** Both have valid points
- Critique accurate for 2019 bonding curve experiment
- But experiment was abandoned quickly
- Current model (2024) addresses concerns

---

## Is the Multilateral Mechanism Actually Used?

### Theoretical Benefits
- Reduces exchange rate complexity (n not n²)
- Enables inter-community trade
- Network effects: easy to add new communities

### Practical Reality
> "Network flow analysis reveals that circulation was highly modular, geographically localized" (Scientific Data paper)

**Translation:** Most trade stays **within** communities, not **between** communities

**Implication:** Multilateral mechanism is elegant but **may not be the key driver of success**

**What actually drives success:**
1. Chama governance (social infrastructure)
2. Feature-phone accessibility (technical inclusivity)
3. Humanitarian partnerships (legitimacy & funding)
4. Existing liquidity problems (real need)

**The multilateral feature is useful but not essential**

---

## Lessons for Other Projects

### 1. Accessibility > Sophistication
- USSD (feature-phone) beats smartphone-only
- Simple fixed rates beat complex bonding curves
- User understanding > technical elegance

### 2. Embed in Existing Social Infrastructure
- Don't create new institutions from scratch
- Find the "chama equivalent" in your context
- Leverage pre-existing trust networks

### 3. Design for Behavior You Want
- Algorithms don't just calculate, they shape behavior
- Want reciprocity? Don't incentivize arbitrage
- Want solidarity? Don't show profit opportunities

### 4. Start Simple, Add Complexity Only If Needed
- Begin with single community currency
- Add multilateral features only when inter-community trade actually happens
- Don't assume network effects will emerge

### 5. Measure What Matters
- Not just: Transaction volume, user count
- But also: Income impact, food security, trust, community cohesion
- Economic impact > technical metrics

### 6. Social Infrastructure > Technical Infrastructure
- Success depends on chamas, trust, partnerships
- Not on blockchain sophistication or bonding curves
- Technology enables, but community drives adoption

---

## Comparison to Other Systems

| System | Type | Scale | Multilateral? |
|--------|------|-------|---------------|
| **Sarafu** | Community CICs | 52K users | ✅ 239 interconnected |
| WIR Bank | Business credit | 60K businesses | ❌ Single currency |
| Sardex | Regional credit | 4K businesses | ❌ Single per region |
| Time Banks | Time credits | Varies | ❌ Single time unit |
| Bancor | Crypto DEX | 100K+ | ✅ Multiple tokens |

**Sarafu's uniqueness:**
- Only community currency with true multilateral network
- Only one using blockchain + feature-phones (no smartphone)
- Only one at tens of thousands of users scale in developing country
- 9+ years continuous operation

---

## Verdict: Does Multilateral Currency Work?

### Technical Proof: ✅ YES
- 9 years operation, 52K users, $3M volume
- 239 interconnected currencies
- 99.98% accounting accuracy

### Economic Proof: ❓ UNCLEAR
- Income gains proven (22%)
- But: No comparison to isolated CICs
- Unknown: How much is due to multilateral vs. simple complementary currency?

### Social Proof: 🔀 MIXED
- Community empowerment: ✅ Yes (chamas control)
- Democratic governance: ⚠️ System rules by engineers
- Social cohesion: ⚠️ Bonding curves encouraged speculation (abandoned)

### The Real Insight
**Multilateral currency systems can work, but they succeed based on social foundations, not technical sophistication.**

**The "multilateral" feature is useful but not essential.**

**What matters:**
- Community trust
- Existing institutions (chamas)
- Simple interfaces (USSD)
- Solving real liquidity problems
- Humanitarian partnerships

---

## Relevance for Sargo (If Applicable)

**If considering multilateral mechanisms, ask:**

1. **Is there actual demand for inter-community trade?**
   - Sarafu: Most trade stays intra-community
   - Don't build multilateral for its own sake

2. **Do we have existing social infrastructure to embed in?**
   - Sarafu: Chamas provide trust + governance
   - Can't create from scratch

3. **Can we keep it simple enough for target users?**
   - Sarafu: Bonding curves too complex → abandoned
   - Fixed rates work better

4. **Are we solving a real liquidity problem?**
   - Sarafu: Kenyan Shilling scarcity in marginalized areas
   - Complementary currencies work when national currency fails

**Don't build multilateral features for technical elegance.**

**Build them only if inter-community trade is a proven need, and keep the mechanism as simple as possible.**

---

## Key References

1. **Dataset:** Zeller et al. (2022), "Sarafu Community Inclusion Currency 2020–2021," _Scientific Data_
2. **Critique:** Barinaga (2020), "Chamas, blockchain and the commons," _Frontiers in Blockchain_
3. **Impact:** Ruddick et al. (2015), "Complementary Currencies...Bangla-Pesa," _IJCCR_
4. **Network:** Crèvecoeur et al. (2023), "Circulation of a digital community currency," _PLOS ONE_

**Full report:** `sarafu-multilateral-currency-deep-research.md` (20,000 words)  
**Code:** https://gitlab.com/grassrootseconomics  
**Website:** https://sarafu.network

---

**Bottom line:** Sarafu proves multilateral community currencies can work at scale, but the social infrastructure (chamas, trust, partnerships) matters more than the technical sophistication (blockchain, bonding curves). The multilateral mechanism is elegant but not the key driver of success.
