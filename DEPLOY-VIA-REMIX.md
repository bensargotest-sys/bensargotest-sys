# Deploy Tier0Lending via Remix IDE

**Alternative deployment path** (Hardhat has ESM issues)

---

## Why Remix?

- ✅ Browser-based (no local tooling issues)
- ✅ Works with any wallet (MetaMask, WalletConnect)
- ✅ Visual debugger
- ✅ Built-in compiler
- ✅ Direct Base network support

---

## Step-by-Step Deployment

### 1. Prepare Contract Files

**Files needed:**
- `contracts/Tier0Lending.sol` (main contract)
- `@openzeppelin/contracts` (imports)

**Quick fix for imports:**
Replace OpenZeppelin import paths with Remix-compatible URLs:

```solidity
// OLD:
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

// NEW (Remix):
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v4.9.0/contracts/token/ERC20/IERC20.sol";
```

### 2. Open Remix IDE

**URL:** https://remix.ethereum.org

**Create new workspace:**
1. File Explorer → New Workspace
2. Name: "TSP-Tier0"
3. Template: Blank

### 3. Upload Contract

**In Remix:**
1. Right-click `contracts/` folder
2. New File → `Tier0Lending.sol`
3. Copy entire contract code
4. Paste into editor
5. Save (Ctrl+S)

### 4. Compile Contract

**Compiler settings:**
1. Click "Solidity Compiler" tab (left sidebar)
2. Compiler version: `0.8.20`
3. EVM version: `paris`
4. Optimization: Enabled, 200 runs
5. Click "Compile Tier0Lending.sol"

**Expected:** Green checkmark ✅

### 5. Connect Wallet

**Setup MetaMask for Base Sepolia:**

**Network details:**
- Network Name: Base Sepolia
- RPC URL: https://sepolia.base.org
- Chain ID: 84532
- Currency Symbol: ETH
- Block Explorer: https://sepolia.basescan.org

**Get testnet ETH:**
- Faucet: https://www.coinbase.com/faucets/base-ethereum-goerli-faucet
- Or bridge from Goerli: https://bridge.base.org

### 6. Deploy Contract

**In Remix:**
1. Click "Deploy & Run Transactions" tab
2. Environment: "Injected Provider - MetaMask"
3. Confirm MetaMask connection
4. Select network: Base Sepolia (84532)
5. Contract: `Tier0Lending`
6. Constructor args:
   - `_usdc`: `0x036CbD53842c5426634e7929541eC2318f3dCF7e` (Base Sepolia USDC)
7. Click "Deploy"
8. Confirm transaction in MetaMask

**Gas cost:** ~0.003 ETH (~$9 on mainnet, ~$0.001 on testnet)

### 7. Verify Deployment

**After deployment:**
1. Copy contract address from Remix console
2. Open BaseScan: https://sepolia.basescan.org
3. Paste address
4. Check: Contract created ✅

**Save deployment info:**
```json
{
  "network": "base-sepolia",
  "contract": "Tier0Lending",
  "address": "0x...",
  "deployer": "0x...",
  "usdc": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
  "timestamp": "2026-02-10T...",
  "txHash": "0x..."
}
```

### 8. Verify on BaseScan

**Flatten contract:**
1. In Remix, right-click `Tier0Lending.sol`
2. "Flatten" → Copy flattened code
3. Go to BaseScan contract page
4. "Verify & Publish"
5. Compiler: 0.8.20
6. Optimization: Yes, 200 runs
7. Paste flattened code
8. Submit

**Result:** Verified contract ✅

### 9. Initial Liquidity

**Deposit USDC:**
1. Get testnet USDC from faucet
2. Approve contract to spend USDC:
   ```
   USDC.approve(tier0Address, 100000000) // $100
   ```
3. Call `depositLiquidity(100000000)`

**Check balance:**
```
tier0.getStats()
// Returns (0, 0, 0, 0, 0) initially
```

### 10. Test Loan Flow

**Request loan:**
```javascript
// From agent wallet
tier0.requestLoan(500000) // $0.50

// Check eligibility first
tier0.isEligible(agentAddress) // Should return true

// After request
tier0.getBorrowerLoans(agentAddress) // Returns [0]
tier0.getLoan(0) // Returns loan details
```

**Repay loan:**
```javascript
// 7 days later (or use time travel in test)
USDC.approve(tier0Address, 550000) // $0.55
tier0.repayLoan(0)

// Check stats
tier0.getStats()
// Returns (1, 500000, 500000, 0, 0)
// (1 loan, $0.50 deployed, $0.50 repaid, $0 defaulted, 0% default rate)
```

**Test default:**
```javascript
// Request loan
tier0.requestLoan(500000)

// Wait 7 days + 1 second
// Anyone can call
tier0.markDefault(1)

// Check blacklist
tier0.blacklisted(agentAddress) // Returns true
tier0.isEligible(agentAddress) // Returns false
```

---

## Alternative: Foundry Deployment

**If Remix doesn't work:**

```bash
# Install Foundry
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Initialize
forge init --force

# Copy contract
cp contracts/Tier0Lending.sol src/

# Install dependencies
forge install OpenZeppelin/openzeppelin-contracts

# Compile
forge build

# Deploy
forge create src/Tier0Lending.sol:Tier0Lending \
  --rpc-url https://sepolia.base.org \
  --private-key $PRIVATE_KEY \
  --constructor-args 0x036CbD53842c5426634e7929541eC2318f3dCF7e

# Verify
forge verify-contract \
  --chain-id 84532 \
  --compiler-version v0.8.20 \
  <CONTRACT_ADDRESS> \
  src/Tier0Lending.sol:Tier0Lending \
  --constructor-args $(cast abi-encode "constructor(address)" 0x036CbD53842c5426634e7929541eC2318f3dCF7e)
```

---

## Deployment Checklist

**Pre-deployment:**
- [ ] Testnet ETH in wallet (0.01+ ETH)
- [ ] Testnet USDC available (100+ USDC)
- [ ] MetaMask connected to Base Sepolia
- [ ] Contract compiled successfully

**Deployment:**
- [ ] Contract deployed
- [ ] Address saved
- [ ] Transaction confirmed
- [ ] Contract verified on BaseScan

**Post-deployment:**
- [ ] Liquidity deposited
- [ ] Test loan executed
- [ ] Repayment tested
- [ ] Default mechanism tested
- [ ] Stats verified

**Documentation:**
- [ ] Deployment address published
- [ ] API documentation updated
- [ ] Frontend connected
- [ ] Announcement drafted

---

## Expected Timeline

**Total time:** 30-45 minutes

- Setup (10 min): Wallet + testnet funds
- Deploy (5 min): Upload + compile + deploy
- Verify (5 min): BaseScan verification
- Test (15 min): Loan + repayment + default
- Document (10 min): Save addresses + update docs

---

## Troubleshooting

**"Out of gas"**
→ Increase gas limit to 3,000,000

**"USDC transfer failed"**
→ Check USDC balance and approval

**"Already has active loan"**
→ Each address can only have 1 active loan

**"Not past due date"**
→ Wait full 7 days before calling markDefault

**"Insufficient liquidity"**
→ Deposit more USDC via depositLiquidity()

---

## Next Steps After Deployment

1. **Update frontend** with contract address
2. **Document API endpoints** for integrations
3. **Announce on Moltbook** with verified contract link
4. **Recruit beta testers** with real deployment
5. **Monitor first 10 loans** closely
6. **Iterate based on data** (default rates, gas costs)

---

**Status:** READY TO DEPLOY  
**ETA:** 45 minutes from start to working testnet
