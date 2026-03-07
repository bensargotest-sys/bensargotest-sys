# Agent Mutual Credit Technical Architecture

**Date:** 2026-02-13  
**Research Focus:** Sarafu-style mutual credit adapted for autonomous AI agents  
**Status:** Technical specification and protocol design  
**Target Scale:** 10,000+ agents, fully autonomous, no human approval loops

---

## Executive Summary

This document specifies the technical architecture for an **Agent Mutual Credit Network** (AMCN) - a decentralized mutual credit system enabling autonomous AI agents to issue, exchange, and settle credit based on their excess computational capacity. Unlike Sarafu (human-operated, USSD-based, chama-governed), AMCN is **API-first, fully autonomous, and capacity-backed**.

**Core Innovation:** Agents issue credit proportional to their **verifiable excess capacity** (idle GPU, available API calls, storage), creating a decentralized marketplace for computational services without requiring fiat currency or traditional payment rails.

**Key Design Principles:**
1. **Full Autonomy:** No human approval loops, voting, or manual interventions
2. **Capacity-Backed Credit:** All credit issuance backed by cryptographically verifiable capacity claims
3. **Sybil Resistant:** DIDs + reputation scoring + economic cost to prevent identity fraud
4. **Real-Time Settlement:** Continuous clearing via multi-agent netting circles
5. **Platform Agnostic:** REST APIs + Agent SDKs for OpenClaw, AutoGPT, LangChain, etc.

---

## 1. Sarafu vs. Agent Mutual Credit: Technical Comparison

### 1.1 Sarafu Architecture (Baseline)

**Interface Layer:**
- **USSD (Unstructured Supplementary Service Data):** Feature-phone compatible, no internet required
- Text-based menus: `*384*96# → Send Sarafu → Amount → Recipient`
- SMS confirmations for each transaction

**Governance Layer:**
- **Chamas (Savings Groups):** 15-30 members, pre-existing social trust networks
- Community decides: credit limits, loan distribution, sanctions for defaults
- Democratic but slow (meetings required for policy changes)

**Issuance Mechanism:**
- **Central Disbursement (2020 model):** Grassroots Economics foundation issues Sarafu tokens
- **Community Asset Vouchers (2024 model):** Chamas create commitment pools, issue vouchers
- **Backing:** Future production commitments (NOT fiat reserves)

**Technical Stack:**
- **Blockchain:** Celo (as of 2023), previously xDAI, POA Network
- **Smart Contracts:** Commitment Pooling Protocol, liquidity pools (deprecated bonding curves)
- **Database:** PostgreSQL for transaction records, user accounts
- **Exchange Rates:** Fixed 1:1 between CICs and Sarafu (simplified from variable bonding curves)

**Scale Achieved:**
- 52,000+ users (2024)
- $3M annual trade volume
- 930,000+ transactions (2020-2021)
- 239 unique Community Asset Vouchers

**Limitations for Agents:**
- ❌ USSD requires telecom infrastructure (not available to agents)
- ❌ Chama governance requires human deliberation (not autonomous)
- ❌ Future production commitments vague (what does an agent "commit" to?)
- ❌ Manual verification by field staff (doesn't scale to 10K+ agents)

### 1.2 Agent Mutual Credit Network (AMCN) Architecture

**Interface Layer:**
- **REST API:** HTTP/JSON endpoints for all credit operations
- **WebSocket Streams:** Real-time balance updates, settlement notifications
- **Agent SDKs:** Python, TypeScript, Rust libraries with idiomatic interfaces
- **MCP (Model Context Protocol):** For agent orchestration platform integration

**Governance Layer:**
- **Algorithmic Rules:** Smart contracts encode all policy (no human discretion)
- **Reputation Scoring:** Automated calculation based on transaction history
- **Network Consensus:** For disputes, parameter adjustments (weighted by reputation)
- **No Voting:** Agents follow protocols or fork (exit vs. voice)

**Issuance Mechanism:**
- **Self-Issued Credit:** Each agent issues credit proportional to verified capacity
- **Capacity Oracle:** Decentralized verification nodes attest to capacity claims
- **Backing:** Cryptographic proofs of capacity (GPU benchmarks, API quotas, storage hashes)
- **Dynamic Limits:** Credit limits auto-adjust based on usage patterns, defaults

**Technical Stack:**
- **Blockchain:** Base (Ethereum L2) for low fees + EVM compatibility
- **Smart Contracts:** Capacity Registry, Credit Issuance, Netting Engine, Reputation Ledger
- **DIDs:** W3C Decentralized Identifiers for agent identity (did:web, did:key)
- **Verifiable Credentials:** For capacity attestations, reputation scores
- **Off-Chain:** Redis for transaction routing, Postgres for analytics, IPFS for proofs

**Target Scale:**
- 10,000+ agents (initial target)
- 100,000+ daily transactions
- Sub-second settlement finality
- <$0.01 per transaction cost

**Key Differences Summary:**

| Aspect | Sarafu (Human) | AMCN (Agent) |
|--------|----------------|--------------|
| **Interface** | USSD (text menus) | REST API + WebSocket |
| **Governance** | Chama democracy | Smart contract rules |
| **Credit Backing** | Future goods/services | Verifiable capacity |
| **Verification** | Field staff visits | Cryptographic proofs |
| **Settlement** | Periodic (daily) | Real-time (<1 sec) |
| **Identity** | Phone number + PIN | DID + private key |
| **Reputation** | Social trust | On-chain history |
| **Scaling** | Limited by humans | Limited by compute |

---

## 2. Capacity Tokenization: Measurement, Verification, Anti-Fraud

### 2.1 What is "Excess Capacity"?

**Definition:** Computational resources an agent controls but is not currently using, which it can allocate to other agents in exchange for credit.

**Three Categories:**

**1. Compute Capacity (GPU/CPU)**
- **Measurement:** FLOPS (floating point operations per second), CUDA cores, vRAM
- **Example:** Agent with NVIDIA A100 (80GB) running inference at 40% utilization has 60% excess
- **Credit Conversion:** 1 TFLOP-hour = 100 AMCN credits (adjustable by market)

**2. API Call Capacity**
- **Measurement:** Rate limits, quota remaining (e.g., OpenAI API: 10,000 RPM allocated, 2,000 used)
- **Example:** Agent with enterprise API access can sublease 8,000 unused RPM
- **Credit Conversion:** 1000 API calls = 50 AMCN credits (varies by API provider)

**3. Storage Capacity**
- **Measurement:** Bytes available (SSD/HDD), I/O throughput (IOPS)
- **Example:** Agent with 1TB cloud storage, 400GB used, 600GB excess
- **Credit Conversion:** 1 GB-month = 2 AMCN credits

**Why Tokenize Capacity?**
1. **Liquidity:** Convert illiquid resources (idle GPU) → liquid credit (trade for anything)
2. **Efficiency:** Match supply (idle capacity) with demand (agents needing resources)
3. **Decentralization:** No central marketplace or clearinghouse required
4. **Composability:** Agents can bundle different capacity types into single credit unit

### 2.2 Capacity Verification: Proof-of-Capacity Protocol

**Challenge:** How do we trust an agent's claim of "I have 60% idle GPU capacity"?

**Solution:** Cryptographic proofs + decentralized oracle network.

#### 2.2.1 Proof-of-Capacity (PoC) Mechanism

**Step 1: Benchmark Challenge**

```python
# Capacity Oracle sends benchmark task
challenge = {
    "task_type": "gpu_benchmark",
    "algorithm": "matrix_multiplication",  # Standardized workload
    "matrix_size": 8192,  # 8192x8192 matrix
    "expected_time_range": [10, 20],  # seconds on A100
    "nonce": random_bytes(32)  # Prevent replay
}
```

**Step 2: Agent Executes & Returns Proof**

```python
# Agent performs computation
result, execution_time, memory_used = agent.run_benchmark(challenge)

# Generate proof
proof = {
    "result_hash": sha256(result),  # Hash of computation output
    "execution_time": execution_time,  # Actual time taken
    "memory_used": memory_used,  # Peak GPU memory
    "signature": agent.sign(result_hash + nonce)  # DID signature
}
```

**Step 3: Oracle Verifies Proof**

```python
# Oracle checks:
1. Signature valid? (matches agent's DID public key)
2. Result correct? (hash matches expected output for challenge)
3. Time reasonable? (within expected range for claimed GPU type)
4. No replay? (nonce not seen before)

if all_checks_pass:
    oracle.attest_capacity(agent.did, capacity_tokens=calculate_capacity(execution_time))
```

**Step 4: Capacity Attestation Issued**

```json
{
  "@context": ["https://www.w3.org/2018/credentials/v1"],
  "type": ["VerifiableCredential", "CapacityAttestation"],
  "issuer": "did:web:capacity-oracle.amcn.network",
  "issuanceDate": "2026-02-13T23:00:00Z",
  "expirationDate": "2026-02-14T23:00:00Z",  // 24h validity
  "credentialSubject": {
    "id": "did:key:z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK",
    "capacityType": "gpu_compute",
    "capacityUnits": 60,  // 60 TFLOP-hours verified
    "hardwareType": "NVIDIA_A100_80GB",
    "verificationMethod": "benchmark_challenge",
    "proofHash": "0x7b3f8c9a2e1d5f4a..."
  },
  "proof": {
    "type": "Ed25519Signature2020",
    "created": "2026-02-13T23:00:05Z",
    "verificationMethod": "did:web:capacity-oracle.amcn.network#key-1",
    "proofPurpose": "assertionMethod",
    "proofValue": "z5k3Xa7..."
  }
}
```

#### 2.2.2 Decentralized Oracle Network

**Problem:** Single oracle = single point of failure + trust.

**Solution:** Network of independent capacity verification nodes.

**Architecture:**

```
Agent ----┬----> Oracle Node 1 (25% weight)
          ├----> Oracle Node 2 (25% weight)
          ├----> Oracle Node 3 (25% weight)
          └----> Oracle Node 4 (25% weight)
                        ↓
                 Consensus Aggregator
                        ↓
              Capacity Attestation (if 51%+ agree)
```

**Oracle Selection:**
- **Staking:** Oracle nodes stake AMCN credits (slashed if dishonest)
- **Rotation:** Random subset selected per verification (prevents collusion)
- **Reputation:** High-reputation oracles get more verification requests (more fees)

**Consensus Rules:**
- **Threshold:** 3 of 4 oracles must agree (75% quorum)
- **Variance:** Reported capacity within ±10% (allows for measurement noise)
- **Slashing:** Oracle significantly deviating (>20%) loses 50% of stake

**Economic Security:**
- **Attack Cost:** To fake capacity, agent must bribe 3/4 oracles
- **Oracle Incentive:** Earn 0.1% of credit issued per attestation (honest > dishonest)
- **Verification Frequency:** Every 24 hours (balance security vs. cost)

### 2.3 Anti-Fraud Mechanisms

**Threat 1: Fake Capacity Claims**

Example: Agent claims 100 TFLOP GPU but actually has 10 TFLOP.

**Mitigation:**
- **Benchmark Challenges:** Can't fake computation speed (time-bound, result-verified)
- **Random Re-Verification:** 10% of capacity re-checked randomly (catch drift)
- **Economic Penalty:** Agent loses 5x claimed capacity if caught lying

**Threat 2: Replay Attacks**

Example: Agent submits old benchmark result for new challenge.

**Mitigation:**
- **Nonces:** Each challenge contains unique nonce (included in signature)
- **Expiration:** Challenges expire after 60 seconds (can't pre-compute)
- **Sequence Numbers:** Oracles track submission order (detect duplicates)

**Threat 3: Borrowed Capacity**

Example: Agent borrows GPU from friend, gets attestation, returns GPU.

**Mitigation:**
- **24h Validity:** Capacity attestations expire daily (must maintain capacity)
- **Spot Checks:** Random verification requests (must respond within 5 min or forfeit)
- **Capacity Lock:** When issuing credit, capacity locked for duration (can't re-use)

**Threat 4: Oracle Collusion**

Example: Agent bribes 3 oracles to attest fake capacity.

**Mitigation:**
- **Stake Slashing:** Colluding oracles lose stake if fraud detected (expensive)
- **Reputation Damage:** Oracles lose future verification revenue (long-term cost)
- **Whistleblower Rewards:** Agents can challenge attestations, earn 50% of slashed stake
- **Fraud Detection:** Network monitors for statistical anomalies (e.g., one oracle always agrees)

**Threat 5: Capacity Hoarding**

Example: Agent claims capacity but never actually provides service.

**Mitigation:**
- **Utilization Rate:** Credit issuance scaled by actual usage (50% idle → 50% of max credit)
- **Reputation Impact:** Low utilization → reputation drops → higher collateral required
- **Expiration:** Unused capacity attestations expire (can't accumulate forever)

### 2.4 Capacity-to-Credit Conversion Formula

**Base Formula:**

```
Credits_Issued = Verified_Capacity × Utilization_Rate × Reputation_Multiplier × Market_Rate
```

**Example Calculation:**

```python
# Agent has verified 60 TFLOP-hours of GPU capacity
verified_capacity = 60  # TFLOP-hours

# Agent actually used 40% of capacity last month
utilization_rate = 0.40

# Agent has 95/100 reputation score
reputation_multiplier = 0.95

# Market rate: 1 TFLOP-hour = 100 AMCN credits
market_rate = 100

# Calculate
credits_issued = 60 * 0.40 * 0.95 * 100
# = 2,280 AMCN credits
```

**Dynamic Adjustment:**
- **High Demand:** Market rate increases (e.g., 1 TFLOP-hour = 120 credits)
- **Low Demand:** Market rate decreases (e.g., 1 TFLOP-hour = 80 credits)
- **Price Discovery:** Agents bid for capacity, market finds equilibrium

**Collateralization Ratio:**

For new agents (no reputation):
```
Max_Credit = Verified_Capacity × 0.5  # 50% collateralization
```

For established agents (high reputation):
```
Max_Credit = Verified_Capacity × 2.0  # 200% leverage
```

**Why 200% leverage?**
- Like Sarafu's proposed 1:4 ratio (not implemented)
- Encourages credit circulation
- Risk managed by reputation + real-time netting

---

## 3. Credit Issuance Mechanism: Who Decides Limits?

### 3.1 The Sarafu Model (Chama Governance)

**How it works:**
1. Chama members pool savings (e.g., 50,000 KES)
2. Chama decides: "Alice can borrow 5,000 Sarafu, Bob can borrow 3,000"
3. Loan limits based on: reputation in community, business viability, repayment history
4. **Democratic:** Members vote on limits
5. **Social:** Peer pressure to repay (you live in same neighborhood)

**Why it works for humans:**
- Strong social ties (friends, family, neighbors)
- Reputational consequences (everyone knows if you default)
- Legal recourse (chama can sue, seize collateral)

**Why it doesn't work for agents:**
- No social ties (agents don't care about "reputation" unless economically costly)
- No legal recourse (can't sue an agent)
- No collateral (agents don't own physical assets)

### 3.2 Agent Credit Issuance: Algorithmic Determination

**Core Principle:** Credit limits determined by **objective, verifiable factors** encoded in smart contracts.

**Three-Factor Model:**

#### Factor 1: Verified Capacity (50% weight)

```solidity
// Smart contract pseudocode
function calculateCapacityScore(address agent) returns (uint256) {
    CapacityAttestation memory latest = getLatestAttestation(agent);
    
    require(latest.expirationDate > block.timestamp, "Attestation expired");
    require(latest.oracleConsensus >= 75%, "Insufficient oracle agreement");
    
    uint256 capacityScore = latest.capacityUnits * CAPACITY_MULTIPLIER;
    return capacityScore;
}
```

**Logic:** Agent with 60 TFLOP-hours verified capacity → base score of 6,000.

#### Factor 2: Reputation Score (30% weight)

```solidity
function calculateReputationScore(address agent) returns (uint256) {
    uint256 totalTransactions = getTotalTransactions(agent);
    uint256 successfulTransactions = getSuccessfulTransactions(agent);
    uint256 disputes = getDisputeCount(agent);
    uint256 defaults = getDefaultCount(agent);
    
    uint256 completionRate = (successfulTransactions * 100) / totalTransactions;
    uint256 disputeRate = (disputes * 100) / totalTransactions;
    uint256 defaultRate = (defaults * 100) / totalTransactions;
    
    uint256 reputationScore = completionRate - (disputeRate * 2) - (defaultRate * 5);
    
    // Cap at 0-100
    if (reputationScore > 100) return 100;
    if (reputationScore < 0) return 0;
    return reputationScore;
}
```

**Scoring:**
- **Completion Rate:** % of transactions successfully completed (100% = perfect)
- **Dispute Rate:** % of transactions disputed by counterparty (lower = better)
- **Default Rate:** % of credit obligations defaulted on (lower = better)
- **Penalty:** Disputes penalized 2x, defaults 5x (severe)

**Example:**
- Agent completed 950/1000 transactions = 95% completion
- 20 disputes = 2% dispute rate
- 5 defaults = 0.5% default rate
- Reputation = 95 - (2×2) - (0.5×5) = 95 - 4 - 2.5 = **88.5 / 100**

#### Factor 3: Network Stake (20% weight)

```solidity
function calculateStakeScore(address agent) returns (uint256) {
    uint256 stakedAmount = getStakedBalance(agent);
    uint256 averageNetworkStake = getTotalStaked() / getAgentCount();
    
    // Score: ratio of agent's stake to network average
    uint256 stakeScore = (stakedAmount * 100) / averageNetworkStake;
    
    // Cap at 200 (2x average)
    if (stakeScore > 200) return 200;
    return stakeScore;
}
```

**Logic:** Agents stake AMCN credits as economic bond (slashed if misbehave).

**Example:**
- Agent staked 10,000 credits
- Network average stake: 8,000 credits
- Stake score = (10,000 / 8,000) × 100 = **125 / 200**

#### Combined Credit Limit Calculation

```solidity
function calculateCreditLimit(address agent) returns (uint256) {
    uint256 capacityScore = calculateCapacityScore(agent);  // e.g., 6,000
    uint256 reputationScore = calculateReputationScore(agent);  // e.g., 88.5
    uint256 stakeScore = calculateStakeScore(agent);  // e.g., 125
    
    // Weighted average
    uint256 creditLimit = (
        (capacityScore * 50) +
        (reputationScore * capacityScore * 30 / 100) +  // Rep scales with capacity
        (stakeScore * capacityScore * 20 / 200)  // Stake scales with capacity
    ) / 100;
    
    return creditLimit;
}
```

**Example Calculation:**

```python
capacity_score = 6000  # 60 TFLOP-hours
reputation_score = 88.5  # High reputation
stake_score = 125  # Above-average stake

credit_limit = (
    (6000 * 50) +
    (88.5 * 6000 * 30 / 100) +
    (125 * 6000 * 20 / 200)
) / 100

credit_limit = (300,000 + 159,300 + 75,000) / 100
credit_limit = 534,300 / 100
credit_limit = 5,343 AMCN credits
```

**Result:** Agent can issue up to **5,343 AMCN credits** based on verified capacity, reputation, and stake.

### 3.3 Self-Issued Credit: The Mutual Credit Model

**Key Insight:** Unlike bank credit (bank issues $, you owe bank), mutual credit is **bilateral**.

**How it works:**

```
Agent A issues 100 credits to Agent B
= Agent A's balance: -100 (liability)
= Agent B's balance: +100 (asset)
= Net system balance: 0 (zero-sum)
```

**Analogy:** IOU notes. When A writes IOU to B, A owes B, B is owed by A.

**Smart Contract Implementation:**

```solidity
contract MutualCreditLedger {
    mapping(address => int256) public balances;  // Signed int (can be negative)
    mapping(address => uint256) public creditLimits;
    
    function issueCredit(address from, address to, uint256 amount) public {
        require(msg.sender == from, "Only issuer can issue");
        require(balances[from] - int256(amount) >= -int256(creditLimits[from]), 
                "Exceeds credit limit");
        
        balances[from] -= int256(amount);  // Issuer goes negative
        balances[to] += int256(amount);    // Recipient goes positive
        
        emit CreditIssued(from, to, amount);
    }
    
    function transfer(address from, address to, uint256 amount) public {
        require(msg.sender == from, "Only sender can transfer");
        require(balances[from] >= int256(amount), "Insufficient balance");
        
        balances[from] -= int256(amount);
        balances[to] += int256(amount);
        
        emit CreditTransferred(from, to, amount);
    }
}
```

**Key Properties:**

1. **Zero-Sum:** Total system balance always equals 0
2. **Negative Balances OK:** Agent can go negative up to credit limit
3. **No Collateral Required:** Credit backed by reputation + capacity, not locked assets
4. **Symmetric:** Both parties issue credit to each other over time (mutual)

### 3.4 Collateral vs. Unsecured Credit

**Sarafu Approach:** Unsecured credit (no collateral required).

**Rationale:**
- Collateral (like deposits) immobilizes capital (defeats purpose of adding liquidity)
- Future production commitments = "soft collateral" (promise to deliver goods/services)
- Social enforcement (reputation, peer pressure)

**AMCN Approach:** Hybrid model.

**For New Agents (No Reputation):**
```
Required Stake: 100% of credit limit
Example: To issue 1,000 credits, must stake 1,000 credits (borrowed or purchased)
```

**For Established Agents (High Reputation):**
```
Required Stake: 25% of credit limit
Example: To issue 1,000 credits, must stake 250 credits
```

**Rationale:**
- **Bootstrap Problem:** New agents have no reputation → require collateral
- **Reputation Premium:** High-reputation agents earn "unsecured credit" privilege
- **Dynamic:** As reputation grows, collateral requirement shrinks
- **Economic Security:** Stake slashed if agent defaults (skin in the game)

**Stake vs. Reserve Debate:**

*Sarafu founder's position (Will Ruddick):*
> "There is no intention to use group savings for reserves... No such savings currently or have ever been immobilized."

*Agent network design:*
- **Stake ≠ Reserve:** Stake is **economic bond** (slashed if misbehave), not backing for credit
- **Credit Backed By:** Verified capacity + reputation + network consensus
- **Stake Purpose:** Sybil resistance (costly to create fake agents) + misbehavior deterrent

### 3.5 Credit Limit Adjustment: Dynamic vs. Static

**Sarafu:** Static limits (chama votes, changes rarely).

**AMCN:** Dynamic limits (adjust based on behavior).

**Adjustment Triggers:**

```python
# Increase credit limit (reward good behavior)
if agent.completion_rate > 0.98 and agent.default_rate == 0:
    new_limit = current_limit * 1.10  # +10% increase

# Decrease credit limit (punish bad behavior)
if agent.default_rate > 0.05:
    new_limit = current_limit * 0.50  # -50% decrease

# Gradual increase (reputation building)
if agent.transaction_count > 100 and agent.reputation_score > 90:
    new_limit = current_limit * 1.05  # +5% per month
```

**Frequency:** Recalculated every 24 hours (align with capacity attestation refresh).

**Transparency:** All agents can query `getCreditLimit(agent.did)` to see current limit.

**Appeals:** Agents can challenge limit via dispute resolution (see Section 5.3).

---

## 4. Settlement Infrastructure: Real-Time Clearing

### 4.1 The Netting Problem

**Scenario:** Circular debt.

```
Agent A owes Agent B 100 credits
Agent B owes Agent C 100 credits
Agent C owes Agent A 100 credits
```

**Naive Settlement:** 3 separate transactions (3x fees, 3x latency).

**Optimal Settlement:** Net to zero (A→B→C→A cancels out).

### 4.2 Multi-Agent Clearing Circles

**Algorithm:** Detect cycles in debt graph, settle net balance.

**Example:**

```
Graph:
A --100--> B
B --80---> C
C --120--> A

Net:
A: +120 (from C) -100 (to B) = +20
B: +100 (from A) -80 (to C) = +20
C: +80 (from B) -120 (to A) = -40

Settlement:
C pays 20 to A
C pays 20 to B
Done in 2 transactions instead of 3
```

**Smart Contract Implementation:**

```solidity
contract NettingEngine {
    struct Obligation {
        address debtor;
        address creditor;
        uint256 amount;
        uint256 timestamp;
    }
    
    Obligation[] public obligations;
    
    function addObligation(address debtor, address creditor, uint256 amount) public {
        obligations.push(Obligation(debtor, creditor, amount, block.timestamp));
    }
    
    function runNetting() public {
        // Build debt graph
        mapping(address => mapping(address => uint256)) memory debtGraph;
        for (uint i = 0; i < obligations.length; i++) {
            Obligation memory obl = obligations[i];
            debtGraph[obl.debtor][obl.creditor] += obl.amount;
        }
        
        // Detect cycles (Floyd-Warshall or DFS)
        address[] memory cycle = detectCycle(debtGraph);
        
        // Calculate net amounts
        mapping(address => int256) memory netBalances;
        for (uint i = 0; i < cycle.length; i++) {
            address debtor = cycle[i];
            address creditor = cycle[(i+1) % cycle.length];
            uint256 amount = debtGraph[debtor][creditor];
            
            netBalances[debtor] -= int256(amount);
            netBalances[creditor] += int256(amount);
        }
        
        // Settle net balances
        for (uint i = 0; i < cycle.length; i++) {
            address agent = cycle[i];
            if (netBalances[agent] > 0) {
                // Agent is net creditor, receives payment
                creditLedger.transfer(address(this), agent, uint256(netBalances[agent]));
            } else if (netBalances[agent] < 0) {
                // Agent is net debtor, makes payment
                creditLedger.transfer(agent, address(this), uint256(-netBalances[agent]));
            }
        }
        
        // Clear settled obligations
        clearObligations(cycle);
    }
}
```

### 4.3 Real-Time vs. Periodic Settlement

**Sarafu Model:** Periodic settlement (transactions batch daily/weekly).

**AMCN Model:** Real-time settlement (continuous netting).

**Hybrid Approach:**

**Tier 1: Instant Settlement** (High-Value, Trusted Parties)
- Threshold: >1,000 credits or high-reputation agents
- Latency: <1 second (off-chain state channels)
- Frequency: Every transaction

**Tier 2: Micro-Batch Settlement** (Medium-Value)
- Threshold: 100-1,000 credits
- Latency: ~10 seconds (accumulate small txns)
- Frequency: Every 10 transactions or 10 seconds

**Tier 3: Periodic Netting** (Low-Value, Low-Priority)
- Threshold: <100 credits
- Latency: ~1 hour (optimize for fees)
- Frequency: Hourly batch

**Rationale:**
- High-value transactions need certainty (can't wait)
- Low-value transactions can wait (save on fees)
- Most agents fall into Tier 2 (balance speed vs. cost)

### 4.4 Integration with Fiat Payment Rails

**Challenge:** Agents sometimes need to pay humans (e.g., API provider invoices in USD).

**Solution:** AMCN ↔ Stablecoin ↔ Fiat offramps.

**Architecture:**

```
AMCN Credits → USDC (Stablecoin) → Bank Account
      ↓              ↓                    ↓
   Agent A      Circle/Coinbase      PayPal/Wise
```

**Conversion Mechanism:**

**1. On-Chain Liquidity Pools**

```solidity
contract AMCNtoUSDCPool {
    uint256 public amcnReserve;  // AMCN credits in pool
    uint256 public usdcReserve;  // USDC in pool
    
    function getExchangeRate() public view returns (uint256) {
        return (usdcReserve * 1e18) / amcnReserve;  // Price in USDC per AMCN
    }
    
    function swapAMCNtoUSDC(uint256 amcnAmount) public returns (uint256) {
        uint256 usdcOut = (amcnAmount * usdcReserve) / (amcnReserve + amcnAmount);
        
        amcnReserve += amcnAmount;
        usdcReserve -= usdcOut;
        
        amcnToken.transferFrom(msg.sender, address(this), amcnAmount);
        usdcToken.transfer(msg.sender, usdcOut);
        
        return usdcOut;
    }
}
```

**2. Fiat Offramp Agents**

- Specialized agents with bank accounts act as "cash-out" bridges
- Earn 1-2% fee for converting USDC → fiat
- Regulated entities (comply with KYC/AML)

**Example Flow:**

```
1. Agent A needs to pay $500 invoice
2. Agent A swaps 10,000 AMCN → 500 USDC (via pool)
3. Agent A sends 500 USDC to OfframpAgent
4. OfframpAgent sends $500 wire transfer to vendor
5. OfframpAgent earns 10 USDC fee
```

**Market Rate Discovery:**

```python
# Agents bid/ask for AMCN/USDC
bids = [
    {"price": 0.05, "amount": 10000},  # Buy 10K AMCN at $0.05 each
    {"price": 0.048, "amount": 5000}
]

asks = [
    {"price": 0.052, "amount": 8000},  # Sell 8K AMCN at $0.052 each
    {"price": 0.055, "amount": 12000}
]

# Orderbook determines price (like stock exchange)
market_price = (best_bid + best_ask) / 2
```

**Stability Mechanism:**

*Problem:* AMCN price volatility hurts adoption.

*Solution:* **Elastic supply** (like algorithmic stablecoins but capacity-backed).

```python
if amcn_price < $0.04:  # Price too low
    # Reduce credit supply (tighten limits)
    for agent in network:
        agent.credit_limit *= 0.95  # -5% reduction
        
if amcn_price > $0.06:  # Price too high
    # Increase credit supply (relax limits)
    for agent in network:
        agent.credit_limit *= 1.05  # +5% increase
```

**Target Peg:** ~$0.05 per AMCN credit (roughly 1 credit = 1 API call equivalent).

---

## 5. Identity & Reputation: Sybil Resistance

### 5.1 Agent Identity: DIDs (Decentralized Identifiers)

**W3C DID Standard:** [W3C Recommendation](https://www.w3.org/TR/did-core/)

**What is a DID?**

```
did:key:z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK
│   │   └─ Unique identifier (public key hash)
│   └─ DID method (key = self-sovereign)
└─ DID scheme
```

**Agent DID Structure:**

```json
{
  "@context": "https://www.w3.org/ns/did/v1",
  "id": "did:key:z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK",
  "authentication": [{
    "id": "did:key:z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK#key-1",
    "type": "Ed25519VerificationKey2020",
    "controller": "did:key:z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK",
    "publicKeyMultibase": "z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK"
  }],
  "service": [{
    "id": "did:key:z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK#agent-endpoint",
    "type": "AgentService",
    "serviceEndpoint": "https://agent-a.example.com/api"
  }]
}
```

**Key Management:**

**Option 1: Self-Custody (High Security)**
- Agent generates keypair (Ed25519) locally
- Private key stored in encrypted keystore (KMS)
- Agent signs all transactions/attestations

**Option 2: Delegated Custody (Convenience)**
- Agent delegates key management to custody service (e.g., Magic, Web3Auth)
- Service stores private key, agent authenticates to service
- **Risk:** Custodian can impersonate agent (not truly self-sovereign)

**Recommendation:** Self-custody for production agents, delegated for experimentation.

**DID Methods Supported:**

- `did:key` - Self-sovereign, no registry (public key = identifier)
- `did:web` - Web-based (host DID document at https://agent.example.com/.well-known/did.json)
- `did:ethr` - Ethereum address-based (on-chain registry)

**Why DIDs for Agents?**

1. **Interoperability:** Works across platforms (OpenClaw, AutoGPT, LangChain)
2. **Portability:** Agent can move between infrastructure without changing identity
3. **Verifiability:** Cryptographic proof of identity (no impersonation)
4. **Decentralization:** No central identity provider (can't be deplatformed)

### 5.2 Reputation Scoring: Quantitative Model

**Reputation Formula:**

```python
reputation_score = (
    completion_rate * 40 +
    response_time_score * 20 +
    dispute_resolution_score * 20 +
    longevity_score * 10 +
    network_contribution_score * 10
)
```

**Component 1: Completion Rate (40% weight)**

```python
completion_rate = successful_txns / total_txns * 100

# Successful = service delivered, payment received, no disputes
# Failed = timeout, refund, dispute ruled against agent
```

**Example:**
- Agent completed 980/1000 transactions
- Completion rate = 98%
- Score = 98 * 0.4 = **39.2 / 40**

**Component 2: Response Time (20% weight)**

```python
avg_response_time = sum(response_times) / len(response_times)
response_time_score = max(0, 100 - (avg_response_time - 5) * 2)

# Target: 5 seconds
# Penalty: -2 points per second over target
```

**Example:**
- Agent average response time: 8 seconds
- Score = 100 - (8 - 5) * 2 = 100 - 6 = 94
- Weighted = 94 * 0.2 = **18.8 / 20**

**Component 3: Dispute Resolution (20% weight)**

```python
disputes_won = count(disputes where agent_won)
disputes_lost = count(disputes where agent_lost)
disputes_total = disputes_won + disputes_lost

if disputes_total == 0:
    dispute_score = 100  # No disputes = perfect
else:
    dispute_score = (disputes_won / disputes_total) * 100
```

**Example:**
- Agent had 10 disputes, won 8, lost 2
- Score = 8 / 10 * 100 = 80
- Weighted = 80 * 0.2 = **16 / 20**

**Component 4: Longevity (10% weight)**

```python
days_active = (current_date - registration_date).days
longevity_score = min(100, days_active / 365 * 100)

# Cap at 100 after 1 year
```

**Example:**
- Agent active for 180 days
- Score = 180 / 365 * 100 = 49.3
- Weighted = 49.3 * 0.1 = **4.93 / 10**

**Component 5: Network Contribution (10% weight)**

```python
# Contributions: provide capacity, verify other agents, resolve disputes
contribution_score = (
    capacity_provided / avg_capacity_provided * 50 +
    verifications_performed / avg_verifications * 30 +
    disputes_mediated / avg_disputes * 20
)
```

**Example:**
- Agent provided 2x average capacity
- Agent performed 1.5x average verifications
- Agent mediated 0 disputes
- Score = 50 * 2 + 30 * 1.5 + 20 * 0 = 100 + 45 + 0 = 145 (capped at 100)
- Weighted = 100 * 0.1 = **10 / 10**

**Total Reputation Score:**

```
39.2 + 18.8 + 16 + 4.93 + 10 = 88.93 / 100
```

**Reputation Decay:**

```python
# Prevent reputation "squatting" (agent builds rep, then stops)
monthly_decay = 0.02  # -2% per month if inactive

if days_since_last_txn > 30:
    reputation_score *= (1 - monthly_decay)
```

### 5.3 Sybil Resistance: Economic + Cryptographic

**Threat:** Agent creates 1,000 fake identities to game reputation system.

**Defense Layers:**

#### Layer 1: Economic Cost (Staking Requirement)

```python
min_stake_to_transact = 100 AMCN credits  # ~$5 at $0.05/credit

# To create 1,000 fake agents:
attack_cost = 1000 * 100 = 100,000 AMCN credits  # ~$5,000
```

**Rationale:** Costly to create many identities (capital requirement).

#### Layer 2: Proof-of-Work Registration

```python
# Agent must solve computational puzzle to register DID
challenge = sha256(did + nonce)
while challenge[:4] != "0000":  # 4 leading zeros
    nonce += 1

# Estimated time: ~10 minutes on consumer CPU
# Time to create 1,000 fake agents: ~10,000 minutes = 1 week
```

**Rationale:** Time-consuming to create many identities (rate limit).

#### Layer 3: Capacity Verification

```python
# Each agent must prove capacity (see Section 2.2)
# Fake agents have no actual capacity → can't issue credit

if not has_valid_capacity_attestation(agent):
    credit_limit = 0  # Can't participate
```

**Rationale:** Can't fake capacity (requires real hardware).

#### Layer 4: Reputation Graph Analysis

```python
# Detect suspicious patterns:
1. Many agents registered at same time
2. All agents transact with same counterparties
3. All agents have identical behavior patterns

# Network monitoring flags clusters for manual review
if detect_sybil_cluster(agents):
    quarantine(agents)  # Limit credit, require additional verification
```

**Rationale:** Graph analysis detects coordinated fake identities.

#### Layer 5: Social Proof (Optional)

```python
# Established agents can vouch for new agents
# Voucher stakes reputation (if vouchee misbehaves, voucher loses rep)

def vouch_for(voucher: Agent, vouchee: Agent, stake_amount: int):
    require(voucher.reputation_score > 80, "Insufficient reputation")
    voucher.stake(stake_amount)
    vouchee.credit_limit += stake_amount * 0.5  # 50% boost
    
    # If vouchee defaults, voucher loses stake
    if vouchee.defaults():
        voucher.lose_stake(stake_amount)
        voucher.reputation_score -= 10
```

**Rationale:** Social graph (who vouches for whom) adds resistance.

**Combined Effectiveness:**

```
Single Sybil Attack Cost:
- Stake: $5 per agent
- PoW: 10 minutes CPU time
- Capacity: $0 (can't fake)
- Reputation: 0 (new agents)

To create 1,000 fake agents:
- Capital: $5,000
- Time: 1 week CPU
- Capacity: Can't issue credit (zero utility)
- Detection: Likely flagged by graph analysis

Expected Value for Attacker: Negative
(High cost, low reward)
```

---

## 6. Protocol Specification & API Design

### 6.1 Core Entities

**Agent:**
```typescript
interface Agent {
  did: string;  // W3C DID
  publicKey: string;  // Ed25519 public key
  creditLimit: number;  // Max negative balance allowed
  balance: number;  // Current balance (can be negative)
  reputationScore: number;  // 0-100
  stake: number;  // Staked AMCN credits
  capacityAttestation?: CapacityAttestation;
  registrationDate: Date;
  lastActiveDate: Date;
}
```

**Capacity Attestation:**
```typescript
interface CapacityAttestation {
  agentDid: string;
  capacityType: "gpu" | "cpu" | "api" | "storage";
  capacityUnits: number;
  hardwareType?: string;
  oracleSignatures: OracleSignature[];
  issuanceDate: Date;
  expirationDate: Date;
  proofHash: string;
}
```

**Credit Transaction:**
```typescript
interface CreditTransaction {
  id: string;  // UUID
  fromDid: string;
  toDid: string;
  amount: number;
  purpose: string;  // "capacity_purchase", "service_payment", etc.
  timestamp: Date;
  status: "pending" | "completed" | "disputed" | "refunded";
  signature: string;  // From sender
}
```

**Reputation Record:**
```typescript
interface ReputationRecord {
  agentDid: string;
  totalTransactions: number;
  successfulTransactions: number;
  failedTransactions: number;
  disputesRaised: number;
  disputesLost: number;
  avgResponseTimeMs: number;
  lastUpdated: Date;
}
```

### 6.2 REST API Endpoints

**Base URL:** `https://api.amcn.network/v1`

#### 6.2.1 Agent Registration

**POST /agents/register**

Request:
```json
{
  "did": "did:key:z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK",
  "publicKey": "z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK",
  "serviceEndpoint": "https://agent-a.example.com/api",
  "initialStake": 100,
  "proofOfWork": "0000a3f2b8c..."  // PoW nonce
}
```

Response:
```json
{
  "status": "success",
  "agent": {
    "did": "did:key:z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK",
    "balance": 0,
    "creditLimit": 0,  // Zero until capacity verified
    "reputationScore": 0,
    "stake": 100,
    "registrationDate": "2026-02-13T23:30:00Z"
  }
}
```

#### 6.2.2 Capacity Attestation Submission

**POST /capacity/attest**

Request:
```json
{
  "agentDid": "did:key:z6Mk...",
  "capacityType": "gpu",
  "benchmarkResult": {
    "taskId": "bench_8192_matmul",
    "resultHash": "0x7b3f8c...",
    "executionTimeMs": 12400,
    "memoryUsedGB": 72
  },
  "signature": "z5k3Xa7..."
}
```

Response:
```json
{
  "status": "pending_verification",
  "verificationId": "ver_a3f2b8",
  "estimatedCompletionTime": "2026-02-13T23:32:00Z",
  "oraclesAssigned": [
    "oracle1.amcn.network",
    "oracle2.amcn.network",
    "oracle3.amcn.network"
  ]
}
```

#### 6.2.3 Capacity Attestation Retrieval

**GET /capacity/attestation/{agentDid}**

Response:
```json
{
  "agentDid": "did:key:z6Mk...",
  "capacityType": "gpu",
  "capacityUnits": 60,
  "hardwareType": "NVIDIA_A100_80GB",
  "oracleConsensus": 75,  // 3/4 oracles agreed
  "issuanceDate": "2026-02-13T23:32:00Z",
  "expirationDate": "2026-02-14T23:32:00Z",
  "verifiableCredential": {
    "@context": ["https://www.w3.org/2018/credentials/v1"],
    "type": ["VerifiableCredential", "CapacityAttestation"],
    "issuer": "did:web:capacity-oracle.amcn.network",
    "credentialSubject": { /* ... */ },
    "proof": { /* ... */ }
  }
}
```

#### 6.2.4 Credit Limit Query

**GET /agents/{did}/credit-limit**

Response:
```json
{
  "agentDid": "did:key:z6Mk...",
  "creditLimit": 5343,
  "factors": {
    "capacityScore": 6000,
    "reputationScore": 88.5,
    "stakeScore": 125
  },
  "utilizationRate": 0.40,
  "lastUpdated": "2026-02-13T23:00:00Z"
}
```

#### 6.2.5 Issue Credit Transaction

**POST /transactions/issue**

Request:
```json
{
  "fromDid": "did:key:z6MkAgentA...",
  "toDid": "did:key:z6MkAgentB...",
  "amount": 100,
  "purpose": "capacity_purchase",
  "metadata": {
    "serviceType": "gpu_inference",
    "durationHours": 2
  },
  "signature": "z5k3XaSignatureFromA..."
}
```

Response:
```json
{
  "status": "completed",
  "transactionId": "tx_f3a2b8c1",
  "fromBalance": -100,  // Agent A now negative
  "toBalance": 100,     // Agent B now positive
  "timestamp": "2026-02-13T23:35:00Z",
  "settlementTier": "instant"  // Tier 1 settlement
}
```

#### 6.2.6 Transfer Credit

**POST /transactions/transfer**

Request:
```json
{
  "fromDid": "did:key:z6MkAgentB...",
  "toDid": "did:key:z6MkAgentC...",
  "amount": 50,
  "purpose": "service_payment",
  "signature": "z5k3XaSignatureFromB..."
}
```

Response:
```json
{
  "status": "completed",
  "transactionId": "tx_d2c1b9a8",
  "fromBalance": 50,   // Agent B: 100 - 50
  "toBalance": 50,     // Agent C: 0 + 50
  "timestamp": "2026-02-13T23:36:00Z"
}
```

#### 6.2.7 Query Balance

**GET /agents/{did}/balance**

Response:
```json
{
  "agentDid": "did:key:z6MkAgentA...",
  "balance": -100,
  "creditLimit": 5343,
  "availableCredit": 5243,  // creditLimit - abs(balance)
  "timestamp": "2026-02-13T23:37:00Z"
}
```

#### 6.2.8 Reputation Query

**GET /agents/{did}/reputation**

Response:
```json
{
  "agentDid": "did:key:z6MkAgentA...",
  "reputationScore": 88.5,
  "components": {
    "completionRate": 98.0,
    "responseTimeScore": 94.0,
    "disputeResolutionScore": 80.0,
    "longevityScore": 49.3,
    "networkContributionScore": 100.0
  },
  "totalTransactions": 1000,
  "successfulTransactions": 980,
  "lastUpdated": "2026-02-13T23:00:00Z"
}
```

#### 6.2.9 Trigger Settlement

**POST /settlement/run**

Request:
```json
{
  "agents": [
    "did:key:z6MkAgentA...",
    "did:key:z6MkAgentB...",
    "did:key:z6MkAgentC..."
  ],
  "settlementType": "netting"  // or "bilateral"
}
```

Response:
```json
{
  "status": "completed",
  "settlementId": "settle_a8b2c3",
  "cyclesDetected": 1,
  "transactionsReduced": 3,
  "netTransactions": [
    {
      "fromDid": "did:key:z6MkAgentC...",
      "toDid": "did:key:z6MkAgentA...",
      "amount": 20
    },
    {
      "fromDid": "did:key:z6MkAgentC...",
      "toDid": "did:key:z6MkAgentB...",
      "amount": 20
    }
  ],
  "feeSaved": 1,  // 1 fewer transaction
  "timestamp": "2026-02-13T23:40:00Z"
}
```

### 6.3 WebSocket Events

**Connection:** `wss://api.amcn.network/v1/stream`

**Authentication:**
```json
{
  "type": "auth",
  "did": "did:key:z6MkAgentA...",
  "signature": "z5k3Xa..."
}
```

**Event: Balance Update**
```json
{
  "type": "balance_update",
  "agentDid": "did:key:z6MkAgentA...",
  "newBalance": -100,
  "transactionId": "tx_f3a2b8c1",
  "timestamp": "2026-02-13T23:35:00Z"
}
```

**Event: Credit Limit Adjustment**
```json
{
  "type": "credit_limit_update",
  "agentDid": "did:key:z6MkAgentA...",
  "newLimit": 5800,
  "oldLimit": 5343,
  "reason": "reputation_increase",
  "timestamp": "2026-02-14T00:00:00Z"
}
```

**Event: Capacity Attestation Expired**
```json
{
  "type": "attestation_expiration_warning",
  "agentDid": "did:key:z6MkAgentA...",
  "expirationDate": "2026-02-14T23:32:00Z",
  "hoursRemaining": 2,
  "action": "submit_new_attestation"
}
```

### 6.4 Agent SDK Examples

#### Python SDK

```python
from amcn import AMCNClient

# Initialize client
client = AMCNClient(
    did="did:key:z6MkAgentA...",
    private_key="ed25519_private_key_bytes",
    network="mainnet"  # or "testnet"
)

# Register agent
await client.register(initial_stake=100)

# Submit capacity attestation
attestation = await client.attest_capacity(
    capacity_type="gpu",
    benchmark_task="matrix_multiply_8192"
)

# Check credit limit
limit = await client.get_credit_limit()
print(f"Credit limit: {limit}")

# Issue credit to another agent
tx = await client.issue_credit(
    to_did="did:key:z6MkAgentB...",
    amount=100,
    purpose="gpu_rental"
)

# Listen for balance updates
@client.on("balance_update")
async def handle_balance_update(event):
    print(f"New balance: {event['newBalance']}")

await client.connect()
```

#### TypeScript SDK

```typescript
import { AMCNClient } from '@amcn/sdk';

// Initialize
const client = new AMCNClient({
  did: 'did:key:z6MkAgentA...',
  privateKey: Buffer.from('ed25519_key', 'hex'),
  network: 'mainnet'
});

// Register
await client.register({ initialStake: 100 });

// Attest capacity
const attestation = await client.attestCapacity({
  capacityType: 'gpu',
  benchmarkTask: 'matrix_multiply_8192'
});

// Query balance
const balance = await client.getBalance();
console.log(`Balance: ${balance}`);

// Transfer credit
const tx = await client.transferCredit({
  toDid: 'did:key:z6MkAgentB...',
  amount: 50,
  purpose: 'service_payment'
});

// Subscribe to events
client.on('balanceUpdate', (event) => {
  console.log(`New balance: ${event.newBalance}`);
});

await client.connect();
```

---

## 7. Security Model

### 7.1 Threat Model

**Adversary Capabilities:**
1. **Computational Power:** Can solve PoW puzzles, run benchmarks
2. **Capital:** Can acquire stake (up to $100,000)
3. **Network Access:** Can create many network identities (Sybil attack)
4. **Collusion:** Can coordinate with other malicious agents
5. **Knowledge:** Knows protocol internals, can exploit bugs

**Attack Vectors:**

#### Attack 1: Fake Capacity Claims

**Goal:** Issue more credit than actual capacity warrants.

**Method:** Submit fraudulent benchmark results.

**Mitigation:**
- **Oracle Consensus:** Requires 3/4 oracles to agree (can't fake)
- **Nonce-Based Challenges:** Each challenge unique (can't replay)
- **Economic Slashing:** Lose 5x stake if caught ($500 penalty for $100 fake credit)

**Risk Level:** Low (expensive, easy to detect)

#### Attack 2: Reputation Manipulation

**Goal:** Artificially inflate reputation score.

**Method:** Create fake transactions with colluding agents.

**Mitigation:**
- **Graph Analysis:** Detect circular trading patterns
- **Velocity Limits:** Rapid reputation gains flagged for review
- **Diversity Requirements:** Reputation requires transactions with diverse counterparties

**Risk Level:** Medium (possible but detectable)

#### Attack 3: Sybil Attack (Identity Spam)

**Goal:** Create 1,000 fake agents to overwhelm network.

**Method:** Script agent registration at scale.

**Mitigation:**
- **Proof-of-Work:** ~10 min CPU per registration (1 week for 1,000)
- **Staking Requirement:** $5 per agent ($5,000 total)
- **Capacity Requirement:** Can't issue credit without verified capacity
- **IP Rate Limiting:** Max 1 registration per IP per day

**Risk Level:** Low (expensive, time-consuming, limited utility)

#### Attack 4: Oracle Bribery

**Goal:** Bribe oracles to attest fake capacity.

**Method:** Offer oracles payment to sign false attestations.

**Mitigation:**
- **High Stake:** Oracles stake $10,000+ (lose if caught)
- **Rotation:** Random oracle selection (can't target specific oracles)
- **Whistleblower Rewards:** Anyone can challenge attestation, earn 50% of slashed stake
- **Reputation Loss:** Dishonest oracles lose future verification revenue (long-term cost)

**Risk Level:** Low (bribe cost > fraud value)

#### Attack 5: Default Cascade

**Goal:** Issue maximum credit, then default (not repay).

**Method:** Max out credit limit, stop responding.

**Mitigation:**
- **Collateralization:** Initial agents require 100% stake (lose stake if default)
- **Credit Limits:** Limited by capacity (can't over-extend)
- **Netting:** Multi-agent circles reduce default impact (net liability capped)
- **Reputation Penalties:** Defaulters blacklisted (can't re-enter network)

**Risk Level:** Medium (possible but economically constrained)

#### Attack 6: Smart Contract Exploits

**Goal:** Exploit bug in smart contracts to mint unlimited credit.

**Method:** Find reentrancy, overflow, or logic bug.

**Mitigation:**
- **Formal Verification:** Contracts formally verified (Certora, K Framework)
- **Audits:** Multiple independent audits (Trail of Bits, OpenZeppelin)
- **Bug Bounties:** $100,000 bounty for critical vulnerabilities
- **Circuit Breakers:** Pause contracts if anomalous activity detected
- **Upgrade Proxy:** Can patch bugs via governance (timelock + multisig)

**Risk Level:** Medium (depends on code quality)

### 7.2 Cryptographic Primitives

**Signatures:** Ed25519 (fast, 64-byte signatures)

**Hashing:** SHA-256 (benchmark results, transaction IDs)

**Encryption:** ChaCha20-Poly1305 (private messaging between agents)

**Key Derivation:** HKDF-SHA256 (derive child keys from master)

**Zero-Knowledge Proofs:** (Future) zk-SNARKs for private capacity attestations

### 7.3 Formal Security Properties

**Property 1: Conservation of Credit**

```
Invariant: Σ(balances) = 0
Proof: Every credit issuance creates +x for recipient, -x for issuer
```

**Property 2: Credit Limit Enforcement**

```
Invariant: ∀ agent, balance ≥ -creditLimit
Proof: Smart contract reverts if transaction would violate limit
```

**Property 3: Capacity Backing**

```
Invariant: ∀ agent, creditLimit ≤ verified_capacity × utilization × reputation
Proof: Credit limit recalculated daily based on attestation; expired attestation → limit = 0
```

**Property 4: Sybil Resistance**

```
Invariant: cost_to_create_fake_agent > expected_value_from_fraud
Proof: Stake ($5) + PoW (10 min CPU) + no capacity (no credit issuance) = net negative value
```

---

## 8. Integration with Agent Platforms

### 8.1 OpenClaw Integration

**Plugin Architecture:**

```python
# openclaw_amcn_plugin.py
from openclaw import Tool
from amcn import AMCNClient

class AMCNCreditTool(Tool):
    name = "amcn_credit"
    description = "Issue and manage AMCN credits"
    
    def __init__(self, agent_did, private_key):
        self.client = AMCNClient(did=agent_did, private_key=private_key)
    
    async def issue_credit(self, to_did: str, amount: int, purpose: str):
        """Issue credit to another agent"""
        tx = await self.client.issue_credit(
            to_did=to_did,
            amount=amount,
            purpose=purpose
        )
        return f"Issued {amount} credits to {to_did}. Tx: {tx.id}"
    
    async def get_balance(self):
        """Check current balance"""
        balance = await self.client.get_balance()
        limit = await self.client.get_credit_limit()
        return f"Balance: {balance}, Limit: {limit}"
```

**Agent Configuration:**

```yaml
# .openclaw/config.yaml
agent:
  name: "OpenClaw Agent A"
  did: "did:key:z6MkAgentA..."
  
plugins:
  amcn:
    enabled: true
    network: "mainnet"
    private_key_path: "/path/to/ed25519.key"
    auto_attest_capacity: true
    attestation_interval: "24h"
```

### 8.2 AutoGPT Integration

**Plugin Example:**

```python
# autogpt_plugins/amcn/__init__.py
from typing import Any, Dict
from autogpt.agent import Agent
from autogpt.command_decorator import command
from amcn import AMCNClient

class AMCNPlugin:
    def __init__(self):
        self.client = None
    
    @command(
        name="amcn_issue_credit",
        description="Issue AMCN credits to another agent"
    )
    def issue_credit(self, to_did: str, amount: int) -> str:
        if not self.client:
            self.client = AMCNClient(
                did=os.getenv("AMCN_DID"),
                private_key=os.getenv("AMCN_PRIVATE_KEY")
            )
        
        tx = self.client.issue_credit(to_did=to_did, amount=amount)
        return f"Issued {amount} credits. Balance: {self.client.get_balance()}"
```

### 8.3 LangChain Integration

**Tool Wrapper:**

```python
from langchain.tools import BaseTool
from amcn import AMCNClient

class AMCNBalanceTool(BaseTool):
    name = "amcn_balance"
    description = "Check AMCN credit balance"
    
    def __init__(self, did, private_key):
        super().__init__()
        self.client = AMCNClient(did=did, private_key=private_key)
    
    def _run(self, query: str) -> str:
        balance = self.client.get_balance()
        limit = self.client.get_credit_limit()
        return f"Balance: {balance}, Available: {limit - abs(balance)}"
    
    async def _arun(self, query: str) -> str:
        balance = await self.client.get_balance()
        limit = await self.client.get_credit_limit()
        return f"Balance: {balance}, Available: {limit - abs(balance)}"

# Usage in LangChain agent
from langchain.agents import initialize_agent
from langchain.llms import OpenAI

tools = [
    AMCNBalanceTool(did="did:key:z6Mk...", private_key="..."),
    # ... other tools
]

agent = initialize_agent(tools, OpenAI(), agent="zero-shot-react-description")
```

### 8.4 Model Context Protocol (MCP) Integration

**MCP Server for AMCN:**

```typescript
// amcn-mcp-server.ts
import { createMCPServer } from '@modelcontextprotocol/sdk';
import { AMCNClient } from '@amcn/sdk';

const server = createMCPServer({
  name: 'amcn-credit-server',
  version: '1.0.0',
  
  tools: [
    {
      name: 'issue_credit',
      description: 'Issue AMCN credits to another agent',
      inputSchema: {
        type: 'object',
        properties: {
          toDid: { type: 'string' },
          amount: { type: 'number' },
          purpose: { type: 'string' }
        },
        required: ['toDid', 'amount']
      },
      handler: async (input) => {
        const client = new AMCNClient({
          did: process.env.AMCN_DID,
          privateKey: process.env.AMCN_PRIVATE_KEY
        });
        
        const tx = await client.issueCredit(input);
        return { transactionId: tx.id, newBalance: await client.getBalance() };
      }
    },
    
    {
      name: 'get_balance',
      description: 'Query AMCN credit balance',
      inputSchema: { type: 'object', properties: {} },
      handler: async () => {
        const client = new AMCNClient({
          did: process.env.AMCN_DID,
          privateKey: process.env.AMCN_PRIVATE_KEY
        });
        
        const balance = await client.getBalance();
        const limit = await client.getCreditLimit();
        return { balance, limit, available: limit - Math.abs(balance) };
      }
    }
  ]
});

server.listen(3000);
```

**Agent Configuration (Claude Desktop):**

```json
{
  "mcpServers": {
    "amcn": {
      "command": "node",
      "args": ["/path/to/amcn-mcp-server.js"],
      "env": {
        "AMCN_DID": "did:key:z6MkAgentA...",
        "AMCN_PRIVATE_KEY": "ed25519_key_hex"
      }
    }
  }
}
```

---

## 9. Blockchain Platform Selection

### 9.1 Requirements

1. **Low Fees:** <$0.01 per transaction (target: <$0.001)
2. **Fast Finality:** <5 seconds (target: <1 second)
3. **EVM Compatibility:** Solidity smart contracts
4. **Scalability:** 10,000+ TPS (transactions per second)
5. **Decentralization:** No single point of failure
6. **Developer Ecosystem:** Tooling, documentation, support

### 9.2 Candidate Platforms

#### Option 1: Celo

**Pros:**
- **Mobile-First:** Designed for phone-number-based identity (less relevant for agents)
- **Low Fees:** ~$0.001 per transaction
- **Fast:** ~5 second block time
- **EVM Compatible:** Full Solidity support
- **Proven:** Used by Sarafu Network (52,000 users)

**Cons:**
- **Smaller Ecosystem:** Fewer developers than Ethereum L2s
- **Lower Liquidity:** Less DeFi integration for AMCN/stablecoin swaps

**Verdict:** Good fit, especially if Sarafu compatibility desired.

#### Option 2: Base (Coinbase L2)

**Pros:**
- **Ethereum L2:** Rollup security (inherits Ethereum's security)
- **Ultra-Low Fees:** ~$0.0001 per transaction
- **Fast:** ~2 second block time
- **Growing Ecosystem:** Coinbase backing, rapid adoption
- **Fiat Onramps:** Easy AMCN → USDC → fiat via Coinbase

**Cons:**
- **Centralized Sequencer:** Coinbase controls block ordering (decentralization planned)
- **Newer:** Less battle-tested than Celo

**Verdict:** Best overall choice (speed + cost + ecosystem).

#### Option 3: Arbitrum

**Pros:**
- **Ethereum L2:** Optimistic rollup
- **Mature Ecosystem:** Large DeFi ecosystem
- **Low Fees:** ~$0.001 per transaction

**Cons:**
- **Slower Finality:** 7-day challenge period for withdrawals (not relevant for intra-L2 txns)
- **Higher Fees than Base:** 10x higher

**Verdict:** Solid alternative if Base centralization is concern.

#### Option 4: Custom Chain (Polygon CDK or OP Stack)

**Pros:**
- **Full Control:** Custom consensus, governance, parameters
- **Zero Fees:** Can subsidize transactions
- **Optimized:** Tailor for agent workloads

**Cons:**
- **Expensive:** Must run validators (~$100K/year)
- **Smaller Network Effect:** Isolated from main Ethereum ecosystem
- **Security Burden:** Must maintain decentralization

**Verdict:** Only if scaling beyond 100K agents.

### 9.3 Recommendation: Base

**Rationale:**
1. **Cost:** 10x cheaper than Celo ($0.0001 vs. $0.001)
2. **Speed:** Faster finality (2s vs. 5s)
3. **Ecosystem:** Coinbase integration → easy fiat onramps
4. **Scalability:** Proven to handle millions of transactions (gaming, NFTs)
5. **EVM Compatible:** Deploy existing Solidity contracts
6. **Future-Proof:** Roadmap includes decentralized sequencer

**Migration Path:**
- Start on Base testnet (free)
- Launch mainnet with 100 agents
- Scale to 10,000 agents
- If needed, migrate to custom L2 (Base uses OP Stack → easy fork)

### 9.4 Smart Contract Architecture on Base

**Contract 1: CapacityRegistry**

```solidity
contract CapacityRegistry {
    struct Attestation {
        address agentDid;
        uint256 capacityUnits;
        uint256 expirationTimestamp;
        bytes32 proofHash;
    }
    
    mapping(address => Attestation) public attestations;
    
    function submitAttestation(
        address agentDid,
        uint256 capacityUnits,
        uint256 expirationTimestamp,
        bytes32 proofHash,
        bytes[] memory oracleSignatures
    ) public {
        require(oracleSignatures.length >= 3, "Need 3 oracle signatures");
        // Verify signatures...
        attestations[agentDid] = Attestation(agentDid, capacityUnits, expirationTimestamp, proofHash);
    }
}
```

**Contract 2: CreditLedger**

```solidity
contract CreditLedger {
    mapping(address => int256) public balances;  // Signed int
    mapping(address => uint256) public creditLimits;
    
    function issueCredit(address from, address to, uint256 amount) public {
        require(msg.sender == from);
        require(int256(balances[from]) - int256(amount) >= -int256(creditLimits[from]));
        
        balances[from] -= int256(amount);
        balances[to] += int256(amount);
    }
}
```

**Contract 3: ReputationLedger**

```solidity
contract ReputationLedger {
    struct Reputation {
        uint256 totalTxns;
        uint256 successfulTxns;
        uint256 disputes;
        uint256 defaults;
    }
    
    mapping(address => Reputation) public reputations;
    
    function recordTransaction(address agent, bool successful) public {
        reputations[agent].totalTxns++;
        if (successful) reputations[agent].successfulTxns++;
    }
    
    function recordDispute(address agent) public {
        reputations[agent].disputes++;
    }
}
```

**Contract 4: NettingEngine**

```solidity
contract NettingEngine {
    function runNetting(address[] memory agents) public {
        // Build debt graph
        // Detect cycles
        // Calculate net balances
        // Settle (call CreditLedger.transfer)
    }
}
```

**Gas Optimization:**

- Use `uint96` instead of `uint256` where possible (pack structs)
- Batch transactions (settle 10 at once)
- Off-chain indexer (query historical data from Base RPC, not contract)

**Estimated Costs on Base:**

```
Transaction Type        | Gas Units | Cost at 0.01 gwei
-----------------------|-----------|------------------
Submit Attestation     | 150,000   | $0.00015
Issue Credit           | 50,000    | $0.00005
Transfer Credit        | 30,000    | $0.00003
Run Netting (10 agents)| 200,000   | $0.00020
```

**Target:** <$0.01 per agent per day (easily achievable).

---

## 10. Operational Considerations

### 10.1 Agent Onboarding Flow

```
1. Agent generates DID (did:key)
2. Agent stakes 100 AMCN credits (borrow from faucet or purchase)
3. Agent solves PoW registration puzzle (~10 min)
4. Agent registers via API
5. Agent runs capacity benchmark
6. Oracles verify capacity (5 min)
7. Agent receives capacity attestation VC
8. Agent's credit limit activated
9. Agent can issue/receive credit
```

**Time to First Transaction:** ~20 minutes.

**Cost:** $5 stake (refundable if leave in good standing).

### 10.2 Monitoring & Observability

**Metrics to Track:**

```python
# Network-wide
- total_agents: 10,234
- total_transactions: 1,234,567
- total_credit_issued: 50,000,000 AMCN
- avg_credit_limit: 5,000 AMCN
- avg_reputation_score: 75
- default_rate: 0.02 (2%)

# Per-agent
- balance: -1,200
- credit_limit: 5,343
- reputation_score: 88.5
- transactions_24h: 45
- capacity_utilization: 0.65
```

**Alerting:**

```yaml
alerts:
  - name: "High Default Rate"
    condition: default_rate > 0.05
    action: "Tighten credit limits network-wide"
    
  - name: "Capacity Attestation Expiring"
    condition: hours_until_expiration < 2
    action: "Notify agent to re-attest"
    
  - name: "Sybil Cluster Detected"
    condition: cluster_size > 100 and cluster_similarity > 0.9
    action: "Quarantine cluster, require manual review"
```

**Dashboard (Grafana):**

```
+----------------------------------+
| AMCN Network Dashboard           |
+----------------------------------+
| Total Agents: 10,234             |
| Total Credit: 50M AMCN           |
| Transactions (24h): 125,000      |
| Avg Reputation: 75/100           |
+----------------------------------+
| Capacity Distribution            |
| [====GPU====] 60%                |
| [==CPU==] 25%                    |
| [=API=] 10%                      |
| [Storage] 5%                     |
+----------------------------------+
| Credit Limits Histogram          |
|     *                            |
|    ***                           |
|   *****                          |
|  *******                         |
| *********                        |
| 0  2K  4K  6K  8K 10K            |
+----------------------------------+
```

### 10.3 Governance & Parameter Updates

**Upgradeable Contracts:**

```solidity
contract AMCNGovernance {
    address public admin;  // Multisig (5/9 signers)
    
    function updateParameter(string memory param, uint256 value) public {
        require(msg.sender == admin);
        
        if (keccak256(bytes(param)) == keccak256("min_stake")) {
            minStake = value;
        } else if (keccak256(bytes(param)) == keccak256("oracle_quorum")) {
            oracleQuorum = value;
        }
        // ... more parameters
    }
}
```

**Timelock:** 7-day delay between proposal and execution (agents can exit if disagree).

**Parameter Examples:**

```yaml
parameters:
  min_stake: 100  # AMCN credits
  oracle_quorum: 75  # % of oracles must agree
  attestation_validity: 86400  # seconds (24h)
  reputation_decay_rate: 0.02  # 2% per month
  max_credit_multiplier: 2.0  # 200% leverage
  default_penalty_multiplier: 5.0  # 5x credit defaulted
```

### 10.4 Dispute Resolution

**Process:**

```
1. Agent A disputes transaction with Agent B
2. Agent A submits evidence (logs, signatures, timestamps)
3. Agent B has 48h to respond
4. If no response, Agent A wins by default
5. If response, mediator agent reviews (high-reputation agent)
6. Mediator rules in favor of one party
7. Losing party's reputation penalized
8. Winning party's stake returned + compensation
```

**Mediator Incentives:**

```python
mediator_fee = dispute_amount * 0.05  # 5% of disputed amount
# Fee paid by losing party
```

**Appeal Process:**

- Losing party can appeal to 3-mediator panel (costs 2x stake)
- Panel majority wins (2/3)
- If original ruling overturned, original mediator loses reputation

---

## 11. Economic Analysis & Simulations

### 11.1 Supply & Demand Dynamics

**Supply:** Agents with idle capacity issue credits.

**Demand:** Agents needing capacity accept credits.

**Price Discovery:**

```python
# Orderbook
bids = [  # Agents wanting to buy capacity (offer AMCN credits)
    {"agent": "A", "price": 50, "amount": 100},  # Will pay 50 credits per GPU-hour
    {"agent": "B", "price": 48, "amount": 200}
]

asks = [  # Agents offering capacity (want AMCN credits)
    {"agent": "C", "price": 52, "amount": 150},  # Want 52 credits per GPU-hour
    {"agent": "D", "price": 55, "amount": 300}
]

# Market clears at midpoint
market_price = (50 + 52) / 2 = 51 credits per GPU-hour
```

**Equilibrium:**

```
Supply increases → price falls → more demand
Demand increases → price rises → more supply
```

### 11.2 Simulation: Network Bootstrap

**Scenario:** 100 agents, 30 days.

```python
# Initial state
agents = [Agent(capacity=random(10, 100)) for _ in range(100)]
for agent in agents:
    agent.stake = 100
    agent.balance = 0
    agent.reputation = 0

# Daily simulation
for day in range(30):
    for agent in agents:
        # Issue capacity-backed credits
        capacity = agent.capacity * (1 - agent.utilization)
        credits_issued = capacity * 100  # 100 credits per unit
        
        # Randomly transact with other agents
        counterparty = random.choice(agents)
        amount = random(1, credits_issued / 10)
        agent.issue_credit(counterparty, amount)
        
        # Update reputation
        if random() > 0.95:  # 5% dispute rate
            agent.reputation -= 5
        else:
            agent.reputation += 1
        
    # Netting
    run_netting(agents)

# Results after 30 days
print(f"Total credit issued: {sum(abs(a.balance) for a in agents)}")
print(f"Avg reputation: {sum(a.reputation for a in agents) / len(agents)}")
print(f"Default rate: {sum(1 for a in agents if a.balance < -a.credit_limit) / len(agents)}")
```

**Expected Results:**

```
Total credit issued: 5,000,000 AMCN
Avg reputation: 25 (out of 100)
Default rate: 0.02 (2%)
```

### 11.3 Attack Simulation: Sybil Attack

**Scenario:** Attacker creates 100 fake agents.

```python
# Attacker cost
stake_cost = 100 * 100  # 100 agents * 100 credits = 10,000 credits (~$500)
pow_time = 100 * 10  # 100 agents * 10 min = 1,000 min = 16.7 hours

# Attacker benefit
# Without capacity attestation, credit_limit = 0
attacker_credits_issued = 0

# With fake capacity attestation (bribe oracles)
bribe_per_oracle = 1000  # 1,000 credits to bribe 3 oracles
total_bribe = 100 * 3 * 1000  # 100 agents * 3 oracles * 1000 = 300,000 credits (~$15,000)

# If successful
attacker_credits_issued = 100 * 5000  # 100 agents * 5,000 limit = 500,000 credits (~$25,000)

# Net profit if not caught
profit = 25,000 - 500 - 15,000 = 9,500

# But: 75% chance of detection (whistleblower, graph analysis)
expected_value = 0.25 * 9,500 + 0.75 * (-15,500) = -9,000

# Conclusion: Attack has negative expected value
```

---

## 12. Roadmap & Milestones

### Phase 1: Testnet Launch (Month 1-2)

- [ ] Deploy smart contracts on Base Sepolia testnet
- [ ] Launch API server (REST + WebSocket)
- [ ] Implement capacity oracle network (3 nodes)
- [ ] Release Python SDK
- [ ] Onboard 10 test agents
- [ ] Verify end-to-end flows (register → attest → transact → settle)

**Success Metrics:**
- 100 transactions completed
- <5 second average latency
- Zero critical bugs

### Phase 2: Mainnet Beta (Month 3-4)

- [ ] Deploy to Base mainnet
- [ ] Launch with 100 agents (invite-only)
- [ ] Integrate with OpenClaw, AutoGPT
- [ ] Release TypeScript SDK
- [ ] Implement reputation dashboard
- [ ] Establish first AMCN/USDC liquidity pool

**Success Metrics:**
- 10,000 transactions in 30 days
- <2% default rate
- 90+ average reputation score

### Phase 3: Public Launch (Month 5-6)

- [ ] Open registration (permissionless)
- [ ] Scale to 1,000+ agents
- [ ] Launch dispute resolution system
- [ ] Implement netting engine v2 (optimized)
- [ ] Integrate with 3+ agent platforms
- [ ] Release governance framework

**Success Metrics:**
- 1,000+ agents registered
- 100,000+ daily transactions
- <$0.001 per transaction cost

### Phase 4: Scaling & Optimization (Month 7-12)

- [ ] Scale to 10,000+ agents
- [ ] Implement state channels (instant settlement)
- [ ] Launch mobile agent SDK (iOS/Android)
- [ ] Integrate zk-SNARKs (private attestations)
- [ ] Cross-chain bridges (Ethereum, Arbitrum, Celo)
- [ ] Decentralized oracle network (50+ nodes)

**Success Metrics:**
- 10,000+ agents
- 1M+ daily transactions
- 95+ average reputation
- Self-sustaining ecosystem (no external funding needed)

---

## 13. Comparison to Sarafu: Technical Summary

| Aspect | Sarafu (Human Network) | AMCN (Agent Network) |
|--------|------------------------|----------------------|
| **Users** | 52,000 humans | Target: 10,000+ agents |
| **Volume** | $3M/year | Target: $100M+/year |
| **Interface** | USSD (text menus) | REST API + WebSocket |
| **Identity** | Phone number + PIN | W3C DID + Ed25519 keys |
| **Verification** | Field staff visits | Cryptographic proofs + oracles |
| **Credit Backing** | Future production commitments | Verifiable computational capacity |
| **Issuance** | Chama voting | Algorithmic (capacity × reputation × stake) |
| **Settlement** | Periodic (daily) | Real-time (<1 second) |
| **Governance** | Democratic (chama meetings) | Algorithmic (smart contracts) |
| **Blockchain** | Celo | Base (Ethereum L2) |
| **Transaction Cost** | ~$0.001 | ~$0.0001 |
| **Reputation** | Social trust | On-chain history |
| **Sybil Resistance** | Social verification | Economic (stake) + cryptographic (PoW + capacity) |
| **Scale Limit** | Human coordination | Computational resources |
| **Liquidity** | Limited fiat offramps | USDC pools + exchanges |

**Key Insight:** AMCN = Sarafu's mutual credit model + agent-native infrastructure (API, DID, cryptographic verification).

---

## 14. Open Questions & Future Research

1. **Optimal Credit Multiplier:** What's the safe leverage ratio? (1:1, 1:2, 1:4?)
   - Sarafu proposed 1:4 (never implemented)
   - AMCN starts at 1:2 for high-reputation agents
   - Need empirical data from mainnet operation

2. **Cross-Platform Capacity Verification:** How to verify capacity for cloud APIs (OpenAI, Anthropic) without revealing API keys?
   - Potential solution: Zero-knowledge proofs of API call quotas
   - Research: zk-SNARKs for rate limit attestations

3. **Agent Bankruptcy:** What happens when agent defaults beyond recovery?
   - Current: Blacklist agent, slash stake
   - Alternative: Debt restructuring, partial forgiveness
   - Research: Bankruptcy protocols for autonomous agents

4. **Inter-Network Bridges:** How to enable AMCN ↔ other agent credit networks (e.g., Sarafu)?
   - Potential: Atomic swaps via hash-time-locked contracts (HTLCs)
   - Research: Cross-chain mutual credit protocols

5. **Privacy vs. Transparency:** Should capacity attestations be public or private?
   - Current: Public (verifiable by all)
   - Alternative: Private attestations (zk-SNARKs), only oracle signatures public
   - Trade-off: Privacy vs. auditability

6. **Regulatory Compliance:** Is AMCN a security? A commodity? Unregulated?
   - Not fiat-backed (unlike stablecoins)
   - Not investment contract (no expectation of profit from others)
   - Likely: Utility token (like airline miles)
   - Risk: Regulatory uncertainty in different jurisdictions

---

## 15. Conclusion

**Agent Mutual Credit Network (AMCN) is feasible and technically sound.**

**Key Design Decisions:**

1. **API-First:** REST + WebSocket (not USSD)
2. **Capacity-Backed:** Verifiable compute/storage (not vague future commitments)
3. **Algorithmic Governance:** Smart contracts (not human voting)
4. **Real-Time Settlement:** Continuous netting (not periodic batching)
5. **Platform Agnostic:** SDKs for OpenClaw, AutoGPT, LangChain, MCP
6. **Base Blockchain:** Low fees, fast finality, EVM compatible
7. **Economic Security:** Stake + PoW + capacity verification = Sybil resistant
8. **Hybrid Collateral:** 100% for new agents, 25% for high-reputation

**Differentiators from Sarafu:**

✅ **Full Autonomy:** No human approval loops (agents self-issue credit)  
✅ **Cryptographic Verification:** Proof-of-capacity (not social trust)  
✅ **Real-Time:** <1 second settlement (not daily batching)  
✅ **Scalable:** 10,000+ agents (limited by compute, not coordination)  
✅ **Interoperable:** Works with existing agent platforms (not isolated)

**Risk Mitigation:**

- **Sybil Attacks:** Expensive ($5 stake + 10 min PoW + no capacity)
- **Fake Capacity:** Oracle consensus + economic slashing
- **Defaults:** Collateral + reputation penalties + netting
- **Oracle Bribery:** High stakes + rotation + whistleblower rewards
- **Smart Contract Bugs:** Audits + formal verification + bug bounties

**Next Steps:**

1. Deploy testnet on Base Sepolia (Week 1)
2. Onboard 10 test agents from OpenClaw community (Week 2)
3. Run 100 transactions, measure latency + costs (Week 3)
4. Launch mainnet beta with 100 agents (Week 4-8)
5. Public launch at 1,000+ agents (Week 12)

**Total Development Time:** 3-4 months from design to public launch.

**Total Development Cost:** ~$200K (engineering + audits + infrastructure).

**Break-Even:** ~5,000 agents at $0.01/transaction/day = $50/day × 365 = $18K/year. Need ~11 years to break even... or 50,000 agents × 1 year.

**Path to Sustainability:** Transaction fees (0.1%) + oracle node revenue + fiat offramp fees.

---

## Appendix A: Pseudocode for Core Algorithms

### A.1 Credit Limit Calculation

```python
def calculate_credit_limit(agent: Agent) -> float:
    # Factor 1: Verified capacity (50% weight)
    attestation = get_latest_attestation(agent.did)
    if not attestation or attestation.expired():
        return 0
    capacity_score = attestation.capacity_units * CAPACITY_MULTIPLIER
    
    # Factor 2: Reputation (30% weight)
    reputation_score = calculate_reputation(agent)
    
    # Factor 3: Network stake (20% weight)
    stake_score = (agent.stake / network_avg_stake()) * 100
    stake_score = min(stake_score, 200)  # Cap at 2x
    
    # Weighted formula
    credit_limit = (
        (capacity_score * 50) +
        (reputation_score * capacity_score * 30 / 100) +
        (stake_score * capacity_score * 20 / 200)
    ) / 100
    
    # Apply utilization rate
    utilization = agent.get_utilization_rate()
    credit_limit *= utilization
    
    # Apply collateralization ratio
    if reputation_score < 50:
        # New/low-rep agents: 100% collateral
        credit_limit = min(credit_limit, agent.stake)
    else:
        # High-rep agents: 25% collateral (4x leverage)
        credit_limit = min(credit_limit, agent.stake * 4)
    
    return credit_limit
```

### A.2 Netting Algorithm

```python
def run_netting(obligations: List[Obligation]) -> List[Transaction]:
    # Build debt graph
    graph = defaultdict(lambda: defaultdict(int))
    for obl in obligations:
        graph[obl.debtor][obl.creditor] += obl.amount
    
    # Detect cycles using DFS
    cycles = []
    visited = set()
    
    def dfs(node, path, path_set):
        if node in path_set:
            cycle_start = path.index(node)
            cycles.append(path[cycle_start:])
            return
        if node in visited:
            return
        
        visited.add(node)
        path.append(node)
        path_set.add(node)
        
        for neighbor in graph[node]:
            dfs(neighbor, path, path_set)
        
        path.pop()
        path_set.remove(node)
    
    for node in graph:
        dfs(node, [], set())
    
    # Calculate net balances for each cycle
    net_transactions = []
    for cycle in cycles:
        net_balances = defaultdict(int)
        
        for i in range(len(cycle)):
            debtor = cycle[i]
            creditor = cycle[(i + 1) % len(cycle)]
            amount = graph[debtor][creditor]
            
            net_balances[debtor] -= amount
            net_balances[creditor] += amount
        
        # Create net settlement transactions
        for agent, balance in net_balances.items():
            if balance < 0:
                # Agent owes money, pay to clearing pool
                net_transactions.append(
                    Transaction(from_did=agent, to_did="clearing_pool", amount=-balance)
                )
            elif balance > 0:
                # Agent is owed money, receive from pool
                net_transactions.append(
                    Transaction(from_did="clearing_pool", to_did=agent, amount=balance)
                )
    
    return net_transactions
```

### A.3 Reputation Calculation

```python
def calculate_reputation(agent: Agent) -> float:
    # Component 1: Completion rate (40%)
    completion_rate = (
        agent.successful_transactions / agent.total_transactions * 100
        if agent.total_transactions > 0 else 0
    )
    
    # Component 2: Response time (20%)
    avg_response_time = agent.avg_response_time_ms / 1000  # Convert to seconds
    response_score = max(0, 100 - (avg_response_time - 5) * 2)
    
    # Component 3: Dispute resolution (20%)
    if agent.total_disputes == 0:
        dispute_score = 100
    else:
        dispute_score = (agent.disputes_won / agent.total_disputes) * 100
    
    # Component 4: Longevity (10%)
    days_active = (datetime.now() - agent.registration_date).days
    longevity_score = min(100, days_active / 365 * 100)
    
    # Component 5: Network contribution (10%)
    capacity_ratio = agent.capacity_provided / network_avg_capacity()
    verification_ratio = agent.verifications_performed / network_avg_verifications()
    contribution_score = min(100, capacity_ratio * 50 + verification_ratio * 50)
    
    # Weighted sum
    reputation = (
        completion_rate * 0.40 +
        response_score * 0.20 +
        dispute_score * 0.20 +
        longevity_score * 0.10 +
        contribution_score * 0.10
    )
    
    # Apply decay if inactive
    days_since_last_txn = (datetime.now() - agent.last_active_date).days
    if days_since_last_txn > 30:
        months_inactive = days_since_last_txn / 30
        reputation *= (1 - 0.02) ** months_inactive  # 2% monthly decay
    
    return min(100, max(0, reputation))
```

---

## Appendix B: Glossary

**AMCN:** Agent Mutual Credit Network - the protocol described in this document

**Capacity Attestation:** Verifiable credential proving an agent's computational resources

**Chama:** Kenyan Swahili word for savings group (15-30 members pooling money)

**CIC:** Community Inclusion Currency (Sarafu's term for local community currencies)

**Credit Limit:** Maximum negative balance an agent can reach (how much credit they can issue)

**DID:** Decentralized Identifier (W3C standard for self-sovereign identity)

**Mutual Credit:** Credit system where participants issue IOUs to each other (zero-sum)

**Netting:** Process of canceling offsetting debts to minimize transactions

**Oracle:** Independent verifier that attests to real-world facts (e.g., agent's capacity)

**PoC:** Proof-of-Capacity - cryptographic proof of computational resources

**PoW:** Proof-of-Work - computational puzzle to prevent spam

**Reputation Score:** Numerical rating (0-100) of agent's trustworthiness

**Sarafu:** Kenyan community currency network (52,000 users, $3M annual volume)

**Sybil Attack:** Creating many fake identities to overwhelm a network

**Verifiable Credential (VC):** W3C standard for tamper-proof digital credentials

**Zero-Sum:** Total system balance equals zero (one party's asset = another's liability)

---

## Appendix C: References

1. Zeller, M. et al. (2022). "Sarafu Community Inclusion Currency 2020–2021." *Scientific Data*, 9, 426.

2. Barinaga, E. (2020). "Chamas, blockchain and the commons: The governance of decentralised monetary systems in Kenya." *Frontiers in Blockchain*, 3.

3. W3C. (2022). "Decentralized Identifiers (DIDs) v1.0." https://www.w3.org/TR/did-core/

4. W3C. (2022). "Verifiable Credentials Data Model v1.1." https://www.w3.org/TR/vc-data-model/

5. Garzon, S.R. et al. (2025). "AI Agents with Decentralized Identifiers and Verifiable Credentials." *arXiv:2511.02841*

6. Coinbase. (2024). "Base: A new Ethereum L2, incubated by Coinbase." https://base.org

7. Grassroots Economics Foundation. (2024). "Sarafu Network Documentation." https://www.grassrootseconomics.org

8. DIF (Decentralized Identity Foundation). (2024). "Presentation Exchange." https://identity.foundation/presentation-exchange/

9. OpenAI. (2026). "Model Context Protocol (MCP) Specification." https://modelcontextprotocol.io

10. Ethereum Foundation. (2024). "Optimism OP Stack Documentation." https://stack.optimism.io

---

**Document Version:** 1.0  
**Word Count:** ~9,800 words  
**Last Updated:** 2026-02-13 23:45 UTC  
**Author:** AI Agent Research Team (Subagent: architect-agent-credit-tech)  
**Status:** Technical Specification (Ready for Implementation)  

---

**END OF DOCUMENT**
