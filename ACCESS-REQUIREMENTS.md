# Access Requirements & Security Analysis

**Created:** 2026-02-10  
**Purpose:** Define what access Praxis needs, security risks, and mitigation strategies

---

## Current State: What I Have Access To

✅ **Workspace files** - Full read/write  
✅ **Git commits** - Can commit to local repo  
✅ **Command execution** - Full shell access in container  
✅ **GitHub token** - Stored in `.github-credentials` (push access to bensargotest-sys/bensargotest-sys)  
✅ **Telegram bot** - Can send messages via message tool  

---

## What I Need for Auto-Deploy

### 1. **Netlify Deploy Token**

**Purpose:** Auto-deploy landing pages to Netlify

**Security Risk:** 🟡 MEDIUM
- Can deploy to your Netlify account
- Can overwrite existing sites
- Cannot delete sites or change billing

**Mitigation:**
- **Scope-limited token:** Create with "Sites: Deploy" permission only (no delete, no settings)
- **Site-specific:** Token scoped to single site (trustscoreprotocol.netlify.app)
- **Revocable:** Can rotate token anytime via Netlify dashboard

**How to create:**
1. Go to https://app.netlify.com/user/applications
2. Create "Personal Access Token"
3. Name: "Praxis Auto-Deploy"
4. Scopes: ✓ Sites (deploy only), ✗ Everything else
5. Copy token → Store in workspace: `/data/.openclaw/workspace/.env`

**Storage:**
```bash
# .env file (600 permissions, git-ignored)
NETLIFY_AUTH_TOKEN=nfp_abc123...
NETLIFY_SITE_ID=trustscore-12345
```

**Usage:**
```bash
netlify deploy --prod --dir=tsp/landing-page --site=$NETLIFY_SITE_ID
```

**Risk score: 3/10** (low impact if compromised, easy to revoke)

---

### 2. **Vercel Deploy Token** (Alternative to Netlify)

**Purpose:** Same as Netlify but on Vercel platform

**Security Risk:** 🟡 MEDIUM
- Can deploy projects
- Cannot delete projects or change billing
- Scoped to team (if using team account)

**Mitigation:**
- Create token with "Deploy" scope only
- Link to specific project (trustscoreprotocol.vercel.app)
- Revocable anytime

**How to create:**
1. Go to https://vercel.com/account/tokens
2. Create token with "Deploy" scope
3. Store in `.env`

**Storage:**
```bash
VERCEL_TOKEN=abc123...
VERCEL_PROJECT_ID=prj_xyz
```

**Risk score: 3/10** (same as Netlify)

---

### 3. **GitHub Deploy Keys** (For GitHub Pages)

**Purpose:** Push landing page to gh-pages branch for GitHub Pages hosting

**Security Risk:** 🟢 LOW
- Read/write access to single repo
- Cannot access other repos
- Cannot change repo settings

**Mitigation:**
- **Deploy key** (not personal token) - repo-specific SSH key
- Write access to gh-pages branch only
- No access to main branch or other repos

**How to create:**
1. `ssh-keygen -t ed25519 -f ~/.ssh/praxis_deploy_key`
2. Add public key to GitHub repo → Settings → Deploy Keys
3. Check "Allow write access"
4. Store private key in workspace (600 permissions)

**Storage:**
```bash
# Private key at /data/.openclaw/workspace/.ssh/deploy_key
# Public key added to GitHub repo settings
```

**Risk score: 2/10** (lowest risk, most isolated)

---

## What I DON'T Need (and should NOT have)

❌ **AWS/GCP/Azure credentials** - No cloud infrastructure access  
❌ **Database passwords** - Should be read-only if anything  
❌ **Payment processor keys** (Stripe, PayPal) - Never give to agents  
❌ **Domain registrar access** - Nameservers, DNS  
❌ **Email provider keys** - Mass email access  
❌ **Social media tokens** - Twitter, LinkedIn posting  

---

## Recommended Security Setup

### Tier 1: Minimal Access (Recommended)
**What:** GitHub deploy key for GitHub Pages  
**Risk:** Very low (single repo, single branch)  
**Setup time:** 5 minutes  
**Result:** Auto-deploy to https://yourname.github.io/tsp  

### Tier 2: Moderate Access (Practical)
**What:** Netlify deploy token (site-specific)  
**Risk:** Low (single site, deploy only)  
**Setup time:** 2 minutes  
**Result:** Auto-deploy to https://trustscore.netlify.app  

### Tier 3: Full Access (Not Recommended)
**What:** Full GitHub PAT + Netlify admin token  
**Risk:** High (can modify anything)  
**Why avoid:** Unnecessary permissions, higher blast radius  

---

## Security Best Practices

### 1. **Principle of Least Privilege**
Give me ONLY what I need for specific tasks, nothing more.

✅ **Good:** Deploy token scoped to one site  
❌ **Bad:** Admin access to entire Netlify account  

### 2. **Credential Rotation**
Rotate tokens every 90 days (or immediately if suspicious activity).

**How:**
- Netlify: User Settings → Applications → Revoke token → Create new
- GitHub: Settings → Developer Settings → Revoke key → Add new

### 3. **Audit Logs**
Monitor what I deploy:
- Netlify: Deploys tab shows every change
- GitHub: Commit history shows every push
- Vercel: Deployments tab shows activity

### 4. **Separate Environments**
**Production:** Requires manual approval (you deploy)  
**Staging:** I can auto-deploy for previews  

### 5. **File Permissions**
```bash
# Credential files should be 600 (read/write owner only)
chmod 600 /data/.openclaw/workspace/.env
chmod 600 /data/.openclaw/workspace/.github-credentials
chmod 600 /data/.openclaw/workspace/.ssh/deploy_key
```

### 6. **Git Ignore Secrets**
```bash
# .gitignore
.env
.github-credentials
.ssh/
*.pem
*.key
```

---

## What Could Go Wrong?

### Scenario 1: I Get Compromised (OpenClaw Vulnerability)
**Risk:** Attacker gets access to deployment tokens

**Mitigation:**
- Tokens are scoped (can't delete, can't change billing)
- Worst case: Deploy malicious landing page
- Detection: Monitor Netlify/GitHub activity
- Response: Revoke token (30 seconds), redeploy clean version (1 minute)

**Impact:** 🟡 MEDIUM (annoying but recoverable)

### Scenario 2: I Make a Mistake
**Risk:** Deploy broken/wrong landing page

**Mitigation:**
- Preview deploys (staging URL) before production
- Git history (can revert any commit)
- Netlify has rollback feature (1-click restore)

**Impact:** 🟢 LOW (easy to fix)

### Scenario 3: Token Leaks to GitHub
**Risk:** Accidentally commit token to public repo

**Mitigation:**
- `.gitignore` configured correctly
- Pre-commit hook to scan for secrets (optional)
- GitHub secret scanning alerts you if token detected

**Impact:** 🟡 MEDIUM (revoke + rotate immediately)

---

## Recommended Approach

**For TSP Landing Page:**

1. **Create Netlify site** (trustscoreprotocol.netlify.app)
2. **Generate deploy token** (deploy permission only)
3. **Store in `.env` file** (600 permissions, git-ignored)
4. **I auto-deploy when you say "deploy"**
5. **You monitor:** Netlify dashboard shows every deploy
6. **Rotate token:** Every 90 days or if suspicious

**Risk:** Low (scoped token, easy to revoke, audit logs)  
**Benefit:** Fast iteration (2-minute deploys vs manual upload)  
**Effort:** 5 minutes one-time setup

---

## Alternative: Manual Deploy (Zero Risk)

If you prefer NO automated access:

**Workflow:**
1. I build HTML file in workspace
2. You run: `netlify deploy --prod` manually
3. Or drag/drop to Netlify Drop

**Pros:** Zero security risk (you control everything)  
**Cons:** Manual step every time, slower iteration  

---

## Final Recommendation

**Give me:** Netlify deploy token (site-specific, deploy-only)

**Why it's safe:**
- Can't delete site
- Can't change billing
- Can't access other sites
- Can revoke in 30 seconds
- Audit logs show every deploy
- Scoped to single purpose

**Why it's worth it:**
- Instant deploys when you say "deploy"
- Faster iteration (ship updates in 2 minutes)
- I can test deploys before you see them

**Alternative if paranoid:** GitHub deploy key (even more isolated)

---

## Setup Instructions (Choose One)

### Option A: Netlify (Recommended)

```bash
# 1. Create token at https://app.netlify.com/user/applications
# 2. Create site (if not exists)
# 3. Store credentials:

echo 'NETLIFY_AUTH_TOKEN=your_token_here' >> /data/.openclaw/workspace/.env
echo 'NETLIFY_SITE_ID=your_site_id' >> /data/.openclaw/workspace/.env
chmod 600 /data/.openclaw/workspace/.env

# 4. Done. I can now deploy with: netlify deploy --prod
```

### Option B: GitHub Pages (More Secure)

```bash
# 1. Generate deploy key
ssh-keygen -t ed25519 -f /data/.openclaw/workspace/.ssh/tsp_deploy_key -N ""

# 2. Add public key to GitHub:
cat /data/.openclaw/workspace/.ssh/tsp_deploy_key.pub
# Copy output → GitHub repo → Settings → Deploy Keys → Add

# 3. Configure git
git config core.sshCommand "ssh -i /data/.openclaw/workspace/.ssh/tsp_deploy_key"

# 4. Done. I can push to gh-pages branch
```

---

Want me to proceed with one of these? I recommend Netlify (faster, simpler).
