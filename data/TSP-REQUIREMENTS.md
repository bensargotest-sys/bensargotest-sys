# Trust Score Protocol - Infrastructure Requirements

**Date:** 2026-02-09  
**Status:** Pre-Launch Checklist

---

## What You Need to Provide (One-Time Setup)

### 1. VPS / Cloud Server
**Options:**
- DigitalOcean Droplet ($20-40/month)
- AWS Lightsail ($10-20/month)
- Hetzner Cloud ($5-15/month, Europe-based)
- Current Hostinger VPS (if sufficient specs)

**Minimum Specs:**
- 2 CPU cores
- 4GB RAM
- 80GB SSD
- Ubuntu 22.04 LTS
- SSH access with sudo

**Setup Steps:**
1. Create account, provision server
2. Give me SSH access (add my SSH key or share credentials securely)
3. I'll handle all software installation (Node.js, PostgreSQL, Docker, etc.)

**Cost:** $20-40/month

---

### 2. Domain Name
**What to Buy:**
- Something like `trustscore.xyz` or `agentscore.io`
- Register via Namecheap, Cloudflare, or Google Domains

**Setup Steps:**
1. Purchase domain ($10-15/year)
2. Point A record to VPS IP address
3. I'll handle SSL certificate setup (Let's Encrypt)

**Cost:** $10-15/year

---

### 3. Blockchain Access (Base Mainnet)

#### 3a. RPC Endpoint
**Options:**
- Alchemy (recommended, has Base support)
- Infura
- Public Base RPC (free but rate-limited)

**Setup Steps:**
1. Create Alchemy account: https://www.alchemy.com/
2. Create new app, select "Base" network
3. Copy API key
4. Give me API key (I'll store securely in .env)

**Cost:** Free tier should work initially (30M requests/month)

#### 3b. Validator Wallet
**CRITICAL SECURITY:**
- YOU create the wallet (I should NEVER see the private key directly)
- Use MetaMask or hardware wallet
- Fund with ~$100-500 USDC on Base for gas fees

**Setup Steps:**
1. Create new Ethereum wallet (MetaMask)
2. Switch to Base network in MetaMask
3. Transfer USDC to wallet (bridge from Ethereum or Coinbase)
4. Give me ONLY the public address (0x...)
5. **Private key handling:** You keep it in your own secrets vault. When we need to sign transactions:
   - Option A: You run a signing service locally, I call it via API
   - Option B: You manually sign via MetaMask when I prepare the transaction
   - Option C: We use a hardware wallet (Ledger) for production

**Cost:** $100-500 USDC for gas

---

### 4. IPFS Storage (Pinata)
**Setup Steps:**
1. Create Pinata account: https://www.pinata.cloud/
2. Get API key (JWT token)
3. Give me API key

**Cost:** Free tier (1GB storage, 100k requests/month) - should work for MVP

---

### 5. Database (PostgreSQL)

**Option A: Self-Hosted (Recommended for MVP)**
- I install PostgreSQL on the VPS
- Free, full control
- You just provide the VPS

**Option B: Managed Database**
- DigitalOcean Managed PostgreSQL ($15/month)
- AWS RDS ($20/month)
- Better backups, easier scaling

**Cost:** $0 (self-hosted) or $15-20/month (managed)

---

### 6. Payment Processing (USDC on Base)

**What's Needed:**
- x402 protocol integration (I build this)
- Payment wallet address (same as validator wallet, or separate)
- No Stripe/PayPal needed (blockchain-native payments)

**Setup Steps:**
1. Decide if payments go to same wallet as validator, or separate treasury wallet
2. Give me the payment address
3. I implement x402 payment verification in the API

**Cost:** $0 (blockchain-native)

---

## Total Monthly Costs (Minimum Viable)

| Item | Cost |
|------|------|
| VPS (DigitalOcean) | $20-40 |
| Domain (yearly / 12) | $1 |
| Alchemy RPC | $0 (free tier) |
| Pinata IPFS | $0 (free tier) |
| PostgreSQL | $0 (self-hosted) |
| Gas fees (amortized) | $10-50 |
| **Total** | **$31-91/month** |

**Break-even:** Need 620-1,820 "standard tier" queries/month ($0.01 each)

---

## What I Need Access To

1. **SSH to VPS** (for deployment, monitoring)
2. **GitHub repo** (I'll create and manage, you can make an org)
3. **API keys** (Alchemy, Pinata - store in .env file)
4. **Validator address** (public address only, NOT private key)

---

## Security Best Practices

### Private Key Management
**NEVER give me the private key directly.**

**Safe alternatives:**
1. **Hardware wallet** (Ledger): I prepare transactions, you approve via device
2. **Signing service**: You run a local API that signs transactions, I call it
3. **Manual signing**: For critical operations (validator registration), you sign via MetaMask

### API Key Storage
- I store in `.env` file with chmod 600
- Never committed to git (in .gitignore)
- Rotated every 90 days

### Database Security
- PostgreSQL user with limited permissions (not root)
- SSL connections enabled
- Firewall rules (only VPS can access DB)

---

## Next Steps (Week 0: Pre-Launch)

**Day 1-2: You Provision Infrastructure**
- [ ] Buy VPS
- [ ] Register domain
- [ ] Create Alchemy account
- [ ] Create Pinata account
- [ ] Create validator wallet
- [ ] Fund wallet with USDC

**Day 3-4: I Set Up Environment**
- [ ] Install Node.js, PostgreSQL, Docker
- [ ] Configure SSH, firewall, SSL
- [ ] Clone TSP workspace
- [ ] Set up .env with API keys
- [ ] Initialize database schema

**Day 5: Verification**
- [ ] Test RPC connection to Base mainnet
- [ ] Test IPFS uploads to Pinata
- [ ] Test database queries
- [ ] Confirm validator address has USDC

**Day 6-7: Start Build**
- [ ] Begin Week 1 tasks from kanban-tasks.json
- [ ] First milestone: ERC-8004 contract address verification

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Private key compromise | Never share with me, use hardware wallet |
| API rate limits exceeded | Monitor usage, upgrade to paid tier if needed |
| VPS goes down | Set up monitoring, automatic restarts |
| Database corruption | Daily backups, point-in-time recovery |
| Gas costs spike | Set max gas price limits, monitor Base gas prices |

---

## Questions to Answer Before Starting

1. **Budget:** Can you afford $31-91/month for 6+ months?
2. **Time commitment:** Can you handle infrastructure setup (Days 1-2)?
3. **Risk tolerance:** Understand this is experimental, might not generate revenue for 3-6 months?
4. **Private key handling:** Comfortable managing crypto wallet security?
5. **Legal:** Need to form a business entity, or launch as individual?

---

**Once you answer these and complete Day 1-2 setup, I can start building on Day 3.** 🚀
