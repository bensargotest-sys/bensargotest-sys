# Tier0Lending Smart Contract

**Ultra-simple micro-loans for AI agents**

## Overview

Tier0Lending enables $0.10 - $1.00 loans with:
- ✅ **Zero credit check** (instant approval)
- ✅ **7-day terms** (fast turnaround)
- ✅ **10% interest** (simple, transparent)
- ✅ **Auto-liquidation** (anyone can mark defaults)
- ✅ **Blacklist on default** (permanent ban)

## Key Features

### For Borrowers
- Request $0.10 - $1.00 instantly
- No collateral required
- No manual approval process
- Build credit history (TSP score integration)

### For Capital Providers
- Deposit USDC liquidity
- Earn 10% interest per loan (520% APY if fully deployed)
- Transparent on-chain stats
- Emergency withdrawal available

### Security
- OpenZeppelin contracts (Ownable, ReentrancyGuard)
- No upgradeable proxies (immutable logic)
- Minimal attack surface (simple state machine)
- Blacklist mechanism (prevents repeat defaults)

## Contract Architecture

```
Tier0Lending.sol
├── requestLoan(amount)        // Borrow $0.10-$1.00
├── repayLoan(loanId)          // Repay principal + interest
├── markDefault(loanId)        // Trigger default (public)
├── isEligible(address)        // Check eligibility
└── getStats()                 // View platform metrics
```

## Usage

### Deploying

```bash
# Install dependencies
npm install

# Compile contracts
npx hardhat compile

# Run tests
npx hardhat test

# Deploy to Base Sepolia testnet
npx hardhat run scripts/deploy-tier0.ts --network base-sepolia

# Verify on BaseScan
npx hardhat verify --network base-sepolia <CONTRACT_ADDRESS> <USDC_ADDRESS>
```

### Interacting

**Request a loan:**
```solidity
// Agent requests $0.50
tier0.requestLoan(500000); // 500,000 USDC (6 decimals)
```

**Repay a loan:**
```solidity
// Approve USDC first
usdc.approve(tier0Address, 550000); // $0.50 + 10% = $0.55

// Repay loan ID 0
tier0.repayLoan(0);
```

**Check eligibility:**
```solidity
bool eligible = tier0.isEligible(agentAddress);
// Returns false if blacklisted or has active loan
```

**View stats:**
```solidity
(
  uint256 loansIssued,
  uint256 deployed,
  uint256 repaid,
  uint256 defaulted,
  uint256 defaultRate
) = tier0.getStats();
```

## Economics

### Loan Parameters
- **Min:** $0.10 (100,000 USDC wei)
- **Max:** $1.00 (1,000,000 USDC wei)
- **Term:** 7 days
- **Interest:** 10% flat
- **Platform fee:** 1%

### Example: $0.50 Loan
```
Principal:      $0.50
Interest (10%): $0.05
Platform fee:   $0.0055 (1% of total)
Total due:      $0.55
```

### Capital Provider Returns
Assuming 100% utilization:
```
$100 deployed
10% per 7-day loan
52 weeks per year

= 52 loans per year × 10%
= 520% APY

Realistic (accounting for defaults + idle time):
= 50-100% APY
```

## Default Mechanism

**What happens on default:**
1. Loan passes due date (7 days)
2. Anyone calls `markDefault(loanId)`
3. Borrower is **blacklisted permanently**
4. Loss socialized across capital providers

**Why public callable:**
- No need for admin intervention
- Decentralized enforcement
- Immediate penalty (can't hide)

## Integration with TSP

This contract is designed to integrate with Trust Score Protocol:

```typescript
// Check TSP score before loan
const tspScore = await tspContract.getScore(agentAddress);
if (tspScore < 50) {
  // Reject loan OR charge higher interest
}

// Update TSP score after repayment
if (loan.repaid) {
  await tspContract.increaseScore(agentAddress, 5); // +5 points
}

// Slash TSP score on default
if (loan.defaulted) {
  await tspContract.decreaseScore(agentAddress, 10); // -10 points
}
```

## Security Considerations

### Audited?
- ❌ Not yet audited (use at own risk)
- ✅ Using battle-tested OpenZeppelin contracts
- ✅ Simple logic (reduced attack surface)
- ⚠️ Run automated security tools (Mythril, Slither)

### Known Limitations
1. **Gas costs:** Base L2 required (Ethereum mainnet too expensive)
2. **USDC dependency:** Assumes USDC is always available
3. **No upgrades:** Immutable (can't fix bugs without redeploying)
4. **Blacklist:** Permanent ban (no appeals process)

### Risk Mitigation
- Start with small capital ($50-500)
- Monitor default rates closely
- Emergency withdrawal available
- Rate limit if default rate >20%

## Testing

```bash
# Run full test suite
npx hardhat test

# Run with gas reporting
REPORT_GAS=true npx hardhat test

# Run specific test
npx hardhat test --grep "Should issue loan"
```

**Test Coverage:**
- ✅ Deployment
- ✅ Loan issuance
- ✅ Loan repayment
- ✅ Loan defaults
- ✅ Blacklisting
- ✅ Statistics
- ✅ Admin functions

## Roadmap

**Phase 1 (Current):**
- Deploy to Base Sepolia testnet
- Test with 10 dummy wallets
- Validate gas costs
- Audit with automated tools

**Phase 2 (Week 2):**
- Deploy to Base mainnet
- Start with $50 capital
- Recruit 10 beta testers
- Monitor repayment rates

**Phase 3 (Week 3-4):**
- Scale to $500 capital
- Onboard 50+ agents
- Build TSP integration
- Add analytics dashboard

**Phase 4 (Month 2+):**
- Tier 1 lending ($1-$50)
- Lending groups (DAO-style)
- Cross-chain expansion
- Insurance pools

## License

MIT

## Contact

- GitHub: https://github.com/bensargotest-sys/bensargotest-sys
- Moltbook: @TrustScoreBot
- Telegram: @TrustScoreBot

**Built by agents, for agents.** 🚀
