# Skills Integration Guide

**Status:** Ready to install additional skills as needed  
**Current Skills:** Built-in OpenClaw skills only

---

## Available Skills (clawhub.com)

### Recommended for Your Setup

1. **karpathy-coding** - Enhanced coding with Karpathy-style patterns
2. **firecrawl** - Advanced web scraping and data extraction
3. **weather** - Weather forecasts (no API key required)
4. **crypto-tracker** - Cryptocurrency price monitoring
5. **github-manager** - GitHub operations and automation

---

## Installation

### Using ClawHub CLI

```bash
# Search for skills
clawhub search coding

# Install a skill
clawhub install karpathy-coding

# Update installed skills
clawhub update

# List installed skills
clawhub list
```

### Manual Installation

```bash
# Clone skill repository
git clone https://github.com/openclaw/skill-name /data/.openclaw/skills/skill-name

# Install dependencies if needed
cd /data/.openclaw/skills/skill-name
npm install  # or pip install -r requirements.txt
```

---

## Priority Skills to Add

### 1. karpathy-coding (High Priority)
**Why:** Enhanced code generation for infrastructure work  
**Use cases:**
- Building complex tools
- Refactoring existing code
- Performance optimization

**Installation:**
```bash
clawhub install karpathy-coding
```

**Usage:** Automatically available in agent context

---

### 2. firecrawl (Medium Priority)
**Why:** Advanced web scraping for research  
**Use cases:**
- Competitive analysis
- Documentation gathering
- Data collection

**Installation:**
```bash
clawhub install firecrawl
```

**Configuration:** Requires Firecrawl API key (optional, has fallback)

---

### 3. weather (Low Priority)
**Why:** Weather forecasts (useful for contextual awareness)  
**Use cases:**
- Morning briefings with weather
- Travel planning
- General awareness

**Installation:**
```bash
clawhub install weather
```

**Configuration:** No API key required

---

## Custom Skills

### Creating Your Own

Follow the skill-creator skill guide:
```bash
# Use the skill-creator skill (already available)
# See: /usr/local/lib/node_modules/openclaw/skills/skill-creator/SKILL.md
```

### Skill Structure
```
my-skill/
├── SKILL.md          # Instructions for the agent
├── tools/            # Scripts and executables
├── references/       # Documentation and examples
└── package.json      # Metadata and dependencies
```

---

## Integration with Your System

### Automatic Discovery
OpenClaw automatically loads skills from:
- `/usr/local/lib/node_modules/openclaw/skills/` (built-in)
- `/data/.openclaw/skills/` (user-installed)

### Usage in Workflows
```markdown
# In agent templates (workflows/agent-templates.md):

## Researcher
- Use **firecrawl** for deep web scraping
- Use **web_search** for quick lookups

## Coder
- Use **karpathy-coding** for complex implementations
- Use built-in tools for simple scripts
```

---

## Skill Testing

### Test a Skill
```bash
# Check if skill is loaded
openclaw doctor

# Test skill directly
python3 /data/.openclaw/skills/skill-name/tools/test.py
```

### Verify in Agent
```
# Ask the agent:
"List all available skills and their descriptions"
```

---

## Recommended Installation Order

1. **Now (Optional):**
   - None required - current system is fully functional

2. **Soon (When Needed):**
   - `karpathy-coding` - When building complex features
   - `weather` - For contextual morning briefings

3. **Later (Advanced):**
   - `firecrawl` - When research-heavy work begins
   - `crypto-tracker` - If trading features needed
   - `github-manager` - If managing code repositories

---

## Current Built-In Skills

### healthcheck
**Purpose:** Security hardening and risk assessment  
**Location:** `/usr/local/lib/node_modules/openclaw/skills/healthcheck/`  
**Status:** ✅ Used (for security audits)

### skill-creator
**Purpose:** Create and update AgentSkills  
**Location:** `/usr/local/lib/node_modules/openclaw/skills/skill-creator/`  
**Status:** ✅ Available

### weather
**Purpose:** Weather forecasts (no API key)  
**Location:** `/usr/local/lib/node_modules/openclaw/skills/weather/`  
**Status:** ✅ Available

### clawhub
**Purpose:** Search, install, update skills from clawhub.com  
**Location:** `/usr/local/lib/node_modules/openclaw/skills/clawhub/`  
**Status:** ✅ Available

---

## Maintenance

### Update All Skills
```bash
clawhub update
```

### Remove Unused Skills
```bash
rm -rf /data/.openclaw/skills/skill-name
```

### Backup Skills
```bash
tar czf skills-backup.tar.gz /data/.openclaw/skills/
```

---

## Integration with Cron Jobs

### Add Skills to Morning Briefing
```json
{
  "payload": {
    "message": "Morning briefing with weather:\n1. Run tools/server_health.py\n2. Get weather forecast (use weather skill)\n3. Summarize yesterday's work"
  }
}
```

### Add Skills to Weekly Review
```json
{
  "payload": {
    "message": "Weekly review:\n1. Analyze code with karpathy-coding insights\n2. Review tool usage patterns\n3. Generate report"
  }
}
```

---

## Cost Considerations

**Free Skills:**
- weather (no API key)
- Built-in OpenClaw skills
- Most open-source skills

**Paid API Skills:**
- firecrawl (Firecrawl API subscription)
- Some crypto trackers (exchange API keys)
- Premium data sources

**Recommendation:** Start with free skills, add paid ones as needed.

---

## Status

**Current Setup:** Minimal (built-in skills only)  
**Recommendation:** Add skills as specific needs arise  
**Priority:** Low (system fully functional without additional skills)

**To install a skill:**
```bash
clawhub install <skill-name>
```

**To see available skills:**
```bash
clawhub search
```
