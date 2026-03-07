# Agent Observability Dashboard - Technical Specification

**Version:** 1.0  
**Date:** 2026-02-13  
**Author:** Researcher Subagent  
**Status:** Ready for Architect Review

---

## Executive Summary

This specification defines a comprehensive observability dashboard for monitoring OpenClaw agent operations. The dashboard provides real-time insights into agent performance, resource usage, costs, and operational health, enabling proactive issue detection and optimization.

**Key Goals:**
- **Visibility:** Real-time view of all agent sessions and their states
- **Cost Control:** Track and alert on token usage and API costs
- **Performance:** Identify stuck agents, cascade failures, and resource leaks
- **Quality:** Surface mistakes, blockers, and patterns requiring attention
- **Trends:** Historical analysis for capacity planning and optimization

**Estimated Scope:**
- MVP: 2-3 days (1 developer)
- Full Implementation: 1-2 weeks (1 developer)
- Maintenance: ~2 hours/week

---

## Table of Contents

1. [Data Source Analysis](#1-data-source-analysis)
2. [Dashboard Features](#2-dashboard-features)
3. [UI/UX Design](#3-uiux-design)
4. [Technical Architecture](#4-technical-architecture)
5. [Implementation Phases](#5-implementation-phases)
6. [Security & Access Control](#6-security--access-control)
7. [Testing Strategy](#7-testing-strategy)
8. [Deployment Options](#8-deployment-options)
9. [Maintenance & Operations](#9-maintenance--operations)
10. [Appendix](#10-appendix)

---

## 1. Data Source Analysis

### 1.1 Primary Data Sources

#### **sessions.json** 
**Location:** `/data/.openclaw/agents/main/sessions/sessions.json`  
**Update Frequency:** Real-time (every agent interaction)  
**Format:** JSON object with session keys  

**Data Structure:**
```json
{
  "agent:main:main": {
    "sessionId": "uuid",
    "updatedAt": 1770998585250,  // Unix timestamp (ms)
    "chatType": "direct",
    "inputTokens": 10,
    "outputTokens": 162,
    "totalTokens": 95686,
    "contextTokens": 1000000,
    "modelProvider": "anthropic",
    "model": "claude-sonnet-4-5",
    "compactionCount": 0,
    "abortedLastRun": false,
    "lastHeartbeatText": "...",
    "lastHeartbeatSentAt": 1770994223339
  },
  "agent:main:subagent:uuid": { /* subagent data */ }
}
```

**Available Metrics:**
- Session state (active, idle, completed)
- Token usage per session
- Model costs (derived from model + tokens)
- Last activity timestamp
- Compaction count (context window management)
- Heartbeat status and frequency
- Error states (abortedLastRun)

**Dashboard Use Cases:**
- Active session list
- Idle agent detection (updatedAt > threshold)
- Token/cost tracking per session
- Model usage distribution

---

#### **work-log.md**
**Location:** `/data/.openclaw/workspace/memory/work-log.md`  
**Update Frequency:** Every heartbeat (~30-60 min)  
**Format:** Markdown with timestamp headers

**Data Structure:**
```markdown
## 2026-02-09 20:26 UTC [Heartbeat]
Documented Telegram bot setup + VPS infrastructure in TOOLS.md

---
**2026-02-09 20:28 UTC** - ⏰ **Progress Monitoring Scheduled**
[detailed log entry]
```

**Available Metrics:**
- Work items completed per heartbeat
- Task types (infrastructure, coding, documentation)
- Time spent per task (approximate from timestamps)
- Autonomous work patterns
- Blocker mentions

**Dashboard Use Cases:**
- Activity timeline
- Productivity trends (work items per day/week)
- Task categorization and time allocation
- Blocker detection from log mentions

---

#### **active-tasks.md**
**Location:** `/data/.openclaw/workspace/active-tasks.md`  
**Update Frequency:** On subagent spawn/completion  
**Format:** Markdown with status tags

**Data Structure:**
```markdown
### Sargo Strategy Team (2026-02-13 11:05 UTC)

**[RUNNING]** strategist-sargo (session: agent:main:subagent:uuid)
- Task: Build 90-day product + fundraising strategy
- Started: 11:05 UTC
- Est. completion: 30 minutes

**[COMPLETED]** researcher-pottery (completed 08:00 UTC)
- Task: Pottery distribution research
- Output: pottery-distribution-strategy.md
```

**Available Metrics:**
- Running subagent count
- Completed subagent count
- Task duration estimates vs actuals
- Success/failure rates
- Cascade failure detection

**Dashboard Use Cases:**
- Live subagent status board
- Task completion timeline
- Performance metrics (estimated vs actual duration)
- Failure analysis

---

#### **cost-tracking.db**
**Location:** `/data/.openclaw/workspace/memory/cost-tracking.db`  
**Update Frequency:** Every model API call  
**Format:** SQLite database

**Schema:**
```sql
CREATE TABLE costs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    model TEXT NOT NULL,
    input_tokens INTEGER NOT NULL,
    output_tokens INTEGER NOT NULL,
    input_cost REAL NOT NULL,
    output_cost REAL NOT NULL,
    total_cost REAL NOT NULL,
    session_key TEXT,
    context TEXT
);
CREATE INDEX idx_timestamp ON costs(timestamp);
CREATE INDEX idx_model ON costs(model);
```

**Sample Data:**
```
1|2026-02-11T15:04:54.954972|anthropic/claude-sonnet-4-5|48000|3000|0.144|0.045|0.189||Phase 3 testing
2|2026-02-11T15:04:58.849080|openrouter/meta-llama/llama-3.3-70b-instruct|5000|500|0.0009|9.0e-05|0.00099||Heartbeat
```

**Available Metrics:**
- Cost per session
- Cost per model
- Daily/weekly/monthly cost trends
- Token usage efficiency (cost per output token)
- Budget burn rate

**Dashboard Use Cases:**
- Real-time cost tracking
- Budget alerts (daily/monthly limits)
- Cost breakdown by model
- Token efficiency analysis
- Cost projections

---

#### **session_cleanup.py logs**
**Location:** `/data/.openclaw/workspace/memory/session-cleanup.log`  
**Update Frequency:** Every cleanup run (~hourly via cron)  
**Format:** Plain text log

**Data Structure:**
```
2026-02-13T14:00:00Z | KILL | agent:main:subagent:uuid | Idle for 3.2h (>2h threshold)
2026-02-13T15:00:00Z | KILL | agent:main:subagent:uuid2 | Idle for 2.5h (>2h threshold)
```

**Available Metrics:**
- Zombie agent detection count
- Cleanup frequency
- Idle time distribution
- Resource leak patterns

**Dashboard Use Cases:**
- Cleanup history timeline
- Idle agent statistics
- Resource leak detection trends

---

### 1.2 Secondary Data Sources

| Source | Location | Purpose |
|--------|----------|---------|
| **heartbeat-state.json** | `memory/heartbeat-state.json` | Last check timestamps, rotation schedule |
| **blocked-items.json** | `memory/blocked-items.json` | Active blockers with priority/category |
| **checkpoint-log.jsonl** | `memory/checkpoint-log.jsonl` | Checkpoint history (context window management) |
| **subagent-log.jsonl** | `memory/subagent-log.jsonl` | Subagent spawn/completion events |
| **mistakes.json** | `memory/mistakes.json` | Logged mistakes with patterns |
| **tool-usage.log** | `memory/tool-usage.log` | Tool invocation frequency |

---

### 1.3 Derived Metrics

**Computed from Primary Sources:**

| Metric | Calculation | Use Case |
|--------|-------------|----------|
| **Active Sessions** | Count sessions where `updatedAt > now - 5min` | System load |
| **Idle Sessions** | Count sessions where `updatedAt > now - 2hr` | Resource leaks |
| **Hourly Cost** | Sum cost from last 60min | Budget burn rate |
| **Success Rate** | `completed / (completed + failed)` from active-tasks | Quality metric |
| **Avg Session Duration** | Median `completedAt - startedAt` | Performance |
| **Token Efficiency** | `output_tokens / total_cost` | Cost optimization |
| **Heartbeat Frequency** | Avg time between heartbeats | Proactivity metric |
| **Blocker Density** | `active_blockers / work_items` | Quality risk |

---

## 2. Dashboard Features

### 2.1 Feature Priority Matrix

| Priority | Feature | Impact | Effort | MVP |
|----------|---------|--------|--------|-----|
| **P0** | Live session list | High | Low | ✅ |
| **P0** | Real-time cost tracker | High | Medium | ✅ |
| **P0** | Idle agent alerts | High | Low | ✅ |
| **P1** | Cost breakdown by model | High | Low | ✅ |
| **P1** | Activity timeline | Medium | Medium | ✅ |
| **P1** | Blocker dashboard | Medium | Low | ❌ |
| **P2** | Historical trends (7/30 days) | Medium | High | ❌ |
| **P2** | Token efficiency analysis | Medium | Medium | ❌ |
| **P2** | Subagent cascade detection | High | Medium | ❌ |
| **P3** | Session replay (log viewer) | Low | High | ❌ |
| **P3** | Automated cost reports (email) | Low | Medium | ❌ |
| **P3** | Webhook alerts (Telegram/Slack) | Low | Medium | ❌ |

---

### 2.2 Feature Specifications

#### **F1: Live Session Monitor**
**Priority:** P0  
**Description:** Real-time list of all active agent sessions

**Data Sources:**
- `sessions.json` (primary)
- `active-tasks.md` (subagent details)

**Metrics Displayed:**
- Session key (e.g., `agent:main:main`, `agent:main:subagent:uuid`)
- Session type (main, subagent, group chat)
- Model in use
- Tokens used (input/output/total)
- Cost to date ($)
- Last active timestamp
- Status indicator (🟢 Active, 🟡 Idle <2h, 🔴 Stuck >2h)
- Heartbeat status (✅ Recent, ⏰ Overdue)

**User Actions:**
- Click to view session detail
- Kill idle session (with confirmation)
- Export session metrics (JSON/CSV)

**Update Frequency:** 10 seconds (polling) or real-time (WebSocket)

**UI Wireframe:**
```
┌─────────────────────────────────────────────────────────────┐
│ 🔴 Live Sessions (5 active, 2 idle)        [Refresh] [Kill] │
├─────────────────────────────────────────────────────────────┤
│ 🟢 agent:main:main                                          │
│    Model: claude-sonnet-4-5 | Tokens: 95.6K | Cost: $0.42  │
│    Last Active: 2s ago | ✅ Heartbeat: 5m ago               │
├─────────────────────────────────────────────────────────────┤
│ 🟡 agent:main:subagent:d0fc17e0-09df                        │
│    Model: claude-sonnet-4-5 | Tokens: 12.3K | Cost: $0.08  │
│    Last Active: 45m ago | ⏰ Heartbeat: Never               │
│    [View Details] [Kill Session]                            │
├─────────────────────────────────────────────────────────────┤
│ 🔴 agent:main:telegram:group:-10037...                      │
│    Model: claude-sonnet-4-5 | Tokens: 24.9K | Cost: $0.15  │
│    Last Active: 3h 12m ago | ⚠️ IDLE THRESHOLD EXCEEDED    │
│    [View Details] [Kill Session]                            │
└─────────────────────────────────────────────────────────────┘
```

---

#### **F2: Real-Time Cost Tracker**
**Priority:** P0  
**Description:** Live dashboard of API costs with budget alerts

**Data Sources:**
- `cost-tracking.db` (primary)
- `sessions.json` (model usage)

**Metrics Displayed:**
- **Today:** Current cost | Daily budget | % used | Projected EOD cost
- **This Month:** Current cost | Monthly budget | % used | Projected EOM cost
- **Hourly Burn Rate:** Cost per hour (last 24h average)
- **Top Spenders:** Sessions ranked by cost
- **Cost Breakdown:** Pie chart by model

**Alert Thresholds:**
- 🟢 <70% of budget
- 🟡 70-90% of budget
- 🔴 >90% of budget (alert triggered)

**User Actions:**
- Set daily/monthly budgets
- Configure alert thresholds
- Export cost report (CSV/JSON)
- View cost history (line chart)

**Update Frequency:** 30 seconds

**UI Wireframe:**
```
┌─────────────────────────────────────────────────────────────┐
│ 💰 Cost Tracker                          [Set Budget] [📧]  │
├─────────────────────────────────────────────────────────────┤
│ TODAY: $2.34 / $5.00 (47%) 🟢 | Projected EOD: $4.12        │
│ MONTH: $42.18 / $100.00 (42%) 🟢 | Projected EOM: $87.23    │
│ Burn Rate: $0.12/hr (24h avg)                               │
├─────────────────────────────────────────────────────────────┤
│ Top Spenders (Last 24h)                                     │
│ 1. agent:main:main .................... $1.82 (78%)         │
│ 2. agent:main:subagent:d0fc17e0 ....... $0.34 (14%)         │
│ 3. agent:main:telegram:dm:428513734 .... $0.18 (8%)         │
├─────────────────────────────────────────────────────────────┤
│ Cost by Model                       [View Details]          │
│ ███████████████░░░░░ claude-sonnet-4-5 (78% - $1.83)        │
│ ███░░░░░░░░░░░░░░░░░ llama-3.3-70b (12% - $0.28)            │
│ ██░░░░░░░░░░░░░░░░░░ grok-3 (10% - $0.23)                   │
└─────────────────────────────────────────────────────────────┘
```

---

#### **F3: Idle Agent Detector**
**Priority:** P0  
**Description:** Automated detection and alerting for stuck/zombie agents

**Data Sources:**
- `sessions.json` (updatedAt timestamps)
- `session-cleanup.log` (cleanup history)
- `active-tasks.md` (expected completion times)

**Detection Logic:**
```python
def detect_idle(session):
    idle_time = now - session['updatedAt']
    
    # Main session: never flag as idle
    if session_key == 'agent:main:main':
        return False
    
    # Subagent: flag if idle > 2 hours
    if 'subagent' in session_key and idle_time > 2 * 3600:
        return True
    
    # Group chat: flag if idle > 4 hours
    if session['chatType'] == 'group' and idle_time > 4 * 3600:
        return True
    
    return False
```

**Alert Types:**
- 🟡 Warning: Idle 1-2 hours (monitor)
- 🔴 Critical: Idle >2 hours (auto-kill candidate)
- ⚠️ Anomaly: Expected completion time exceeded by 2x

**User Actions:**
- View idle session details
- Manual kill session
- Configure auto-kill threshold
- Whitelist sessions (don't auto-kill)

**Update Frequency:** 60 seconds

**UI Wireframe:**
```
┌─────────────────────────────────────────────────────────────┐
│ ⚠️ Idle Agent Monitor              [Auto-Kill: ON] [Config] │
├─────────────────────────────────────────────────────────────┤
│ 🔴 CRITICAL: 2 agents idle >2h (auto-kill pending)          │
│ 🟡 WARNING: 1 agent idle >1h                                │
├─────────────────────────────────────────────────────────────┤
│ 🔴 agent:main:subagent:d0fc17e0                             │
│    Task: Dashboard requirements research                    │
│    Expected: 30min | Actual: 2h 18m | Status: STUCK         │
│    Last Output: "Let me analyze..." (2h 12m ago)            │
│    [View Logs] [Kill Now] [Extend Deadline]                 │
├─────────────────────────────────────────────────────────────┤
│ 🟡 agent:main:telegram:group:-10037...                      │
│    Idle: 1h 22m | Last: "HEARTBEAT_OK"                      │
│    [Monitor] [Kill]                                          │
└─────────────────────────────────────────────────────────────┘
```

---

#### **F4: Activity Timeline**
**Priority:** P1  
**Description:** Visual timeline of all agent activities

**Data Sources:**
- `work-log.md` (parsed into events)
- `subagent-log.jsonl` (spawn/complete events)
- `checkpoint-log.jsonl` (checkpoint events)

**Event Types:**
- 🚀 Subagent spawn
- ✅ Task completion
- ❌ Task failure
- 💾 Checkpoint created
- 🔧 Tool usage
- 📊 Heartbeat
- 🚨 Alert triggered

**Filters:**
- By date range
- By event type
- By session/agent
- By keyword search

**Update Frequency:** 30 seconds

**UI Wireframe:**
```
┌─────────────────────────────────────────────────────────────┐
│ 📅 Activity Timeline           [Today] [Week] [Month] [All] │
│ Filters: [All Events] [Subagents] [Errors] [Costs]          │
├─────────────────────────────────────────────────────────────┤
│ 16:03 UTC  🚀 Spawned researcher-agent-dashboard            │
│            └─ Task: Dashboard requirements research          │
│                                                              │
│ 15:50 UTC  📊 Heartbeat: Health check complete              │
│            └─ No blockers, 18 backlog items                  │
│                                                              │
│ 15:24 UTC  ✅ Completed pottery-distribution-strategy       │
│            └─ Duration: 42min | Output: 25KB report          │
│                                                              │
│ 15:10 UTC  💰 Cost alert: Daily budget 80% used ($4.00)     │
│            └─ Projected EOD: $4.95 (🟡 under budget)         │
│                                                              │
│ 14:50 UTC  💾 Checkpoint created                             │
│            └─ Compacted 50K tokens → 12K summary            │
└─────────────────────────────────────────────────────────────┘
```

---

#### **F5: Cost Breakdown by Model**
**Priority:** P1  
**Description:** Detailed analysis of costs per model

**Data Sources:**
- `cost-tracking.db` (cost per model)

**Metrics Displayed:**
- Total cost per model (absolute and %)
- Token usage per model
- Average cost per call
- Cost efficiency (output tokens per $1)
- Recommendation: Switch to cheaper model?

**Visualizations:**
- Pie chart: Cost distribution
- Bar chart: Tokens by model
- Line chart: Cost trend over time

**Update Frequency:** 60 seconds

**UI Wireframe:**
```
┌─────────────────────────────────────────────────────────────┐
│ 💎 Cost by Model (Last 7 Days)              [Export] [CSV]  │
├─────────────────────────────────────────────────────────────┤
│ claude-sonnet-4-5 ........................ $28.34 (67%)     │
│   Calls: 142 | Avg: $0.20 | Efficiency: 50K tokens/$       │
│   💡 Tip: Consider llama-3.3 for non-critical tasks         │
│                                                              │
│ llama-3.3-70b-instruct .................... $8.12 (19%)     │
│   Calls: 89 | Avg: $0.09 | Efficiency: 110K tokens/$        │
│   ✅ Cost-effective for heartbeats                           │
│                                                              │
│ grok-3 .................................... $5.92 (14%)      │
│   Calls: 34 | Avg: $0.17 | Efficiency: 58K tokens/$         │
│   ⚠️ Higher cost than llama, similar performance            │
├─────────────────────────────────────────────────────────────┤
│ [Pie Chart: Cost Distribution]                              │
│ [Line Chart: Daily Cost Trend]                              │
└─────────────────────────────────────────────────────────────┘
```

---

#### **F6: Blocker Dashboard**
**Priority:** P1  
**Description:** Track and manage operational blockers

**Data Sources:**
- `blocked-items.json` (active blockers)
- `work-log.md` (blocker mentions)

**Metrics Displayed:**
- Active blocker count
- Blocker age (days since created)
- Priority distribution (High/Medium/Low)
- Category breakdown (Infrastructure, Code, External)
- Resolution rate (resolved per week)

**User Actions:**
- Mark blocker as resolved
- Update blocker priority
- Add notes/comments
- Export blocker report

**Update Frequency:** 60 seconds

**UI Wireframe:**
```
┌─────────────────────────────────────────────────────────────┐
│ 🚧 Active Blockers (3)                    [Add] [Resolved]  │
├─────────────────────────────────────────────────────────────┤
│ 🔴 #1 [HIGH] TSP CI/CD Pipeline Failing (1.0 days)         │
│    Category: Infrastructure | Age: 1.0 days                 │
│    Impact: Cannot build testnet-mvp                         │
│    Recommendation: Create .openclaw/ci.sh script            │
│    [View Details] [Mark Resolved]                           │
├─────────────────────────────────────────────────────────────┤
│ 🟡 #2 [MEDIUM] Formspree Credentials Missing (1.2 days)    │
│    Category: External | Age: 1.2 days                       │
│    Impact: Agent-first landing page form broken             │
│    [View Details] [Mark Resolved]                           │
├─────────────────────────────────────────────────────────────┤
│ 🟡 #3 [MEDIUM] TSP Backup Script Missing (0.9 days)        │
│    Category: Infrastructure | Age: 0.9 days                 │
│    Impact: Hourly backup cron failing                       │
│    [View Details] [Mark Resolved]                           │
└─────────────────────────────────────────────────────────────┘
```

---

#### **F7: Historical Trends (7/30 Days)**
**Priority:** P2  
**Description:** Long-term analysis of agent performance and costs

**Data Sources:**
- `cost-tracking.db` (historical costs)
- `work-log.md` (parsed for work items)
- `subagent-log.jsonl` (completion rates)

**Metrics Displayed:**
- **Cost Trends:** Daily/weekly/monthly spend
- **Token Efficiency:** Output tokens per $1 over time
- **Success Rate:** % of subagents that complete successfully
- **Average Duration:** Median subagent runtime
- **Heartbeat Frequency:** Avg time between heartbeats
- **Work Item Velocity:** Work items completed per day

**Visualizations:**
- Line charts for all trend metrics
- Heatmap: Activity by day/hour
- Scatter plot: Cost vs duration (efficiency analysis)

**Update Frequency:** 5 minutes (less critical)

**UI Wireframe:**
```
┌─────────────────────────────────────────────────────────────┐
│ 📈 Historical Trends                [7D] [30D] [90D] [All]  │
├─────────────────────────────────────────────────────────────┤
│ Cost Trend (Last 7 Days)                                    │
│ [Line Chart: Daily cost with trend line]                    │
│ Average: $6.23/day | Trend: ↗️ +12% week-over-week          │
├─────────────────────────────────────────────────────────────┤
│ Subagent Performance                                         │
│ Success Rate: 87% (13 of 15 completed) ↗️ +5%               │
│ Avg Duration: 32min ↘️ -8min (improving)                    │
│ [Bar Chart: Success vs failure by day]                      │
├─────────────────────────────────────────────────────────────┤
│ Activity Heatmap                                             │
│       00 02 04 06 08 10 12 14 16 18 20 22                   │
│ Mon   ░░ ░░ ░░ ░░ ██ ██ ██ ██ ██ ░░ ░░ ░░                   │
│ Tue   ░░ ░░ ░░ ░░ ██ ██ ██ ██ ██ ██ ░░ ░░                   │
│ Wed   ░░ ░░ ░░ ░░ ██ ██ ██ ██ ██ ░░ ░░ ░░                   │
│ Peak: 10:00-16:00 UTC | Low: 00:00-06:00 UTC                │
└─────────────────────────────────────────────────────────────┘
```

---

### 2.3 Alert System

**Alert Types:**

| Alert | Trigger | Action | Priority |
|-------|---------|--------|----------|
| **Cost Limit** | Daily cost >90% budget | Email + Dashboard notification | 🔴 High |
| **Idle Agent** | Agent idle >2 hours | Auto-kill + Log | 🟡 Medium |
| **Cascade Failure** | 3+ subagents fail in 30min | Pause spawning + Alert | 🔴 High |
| **Token Spike** | Hourly usage >2x average | Dashboard notification | 🟡 Medium |
| **Blocker Stale** | Blocker active >3 days | Weekly reminder | 🟢 Low |
| **Heartbeat Miss** | No heartbeat in 2 hours | Dashboard notification | 🟡 Medium |

**Notification Channels:**
- Dashboard banner (all alerts)
- Email (High priority only)
- Telegram bot message (configurable)
- Webhook (optional, for integration)

---

## 3. UI/UX Design

### 3.1 Dashboard Layout

**Primary Layout:** Single-page dashboard with sections

```
┌─────────────────────────────────────────────────────────────┐
│ 🔍 OpenClaw Agent Dashboard            [⚙️ Settings] [🔐]   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐    │
│ │ 🟢 Active │ │ 💰 Today  │ │ 📊 Tasks  │ │ 🚨 Alerts │    │
│ │    5      │ │  $2.34    │ │    12     │ │     2     │    │
│ └───────────┘ └───────────┘ └───────────┘ └───────────┘    │
│                                                              │
│ ┌──────────────────────┐ ┌──────────────────────────────┐   │
│ │ 🔴 Live Sessions     │ │ 💰 Cost Tracker              │   │
│ │ [Session list...]    │ │ [Cost charts...]             │   │
│ └──────────────────────┘ └──────────────────────────────┘   │
│                                                              │
│ ┌──────────────────────────────────────────────────────────┐│
│ │ 📅 Activity Timeline                                     ││
│ │ [Timeline events...]                                     ││
│ └──────────────────────────────────────────────────────────┘│
│                                                              │
│ ┌──────────────────────┐ ┌──────────────────────────────┐   │
│ │ ⚠️ Idle Agents       │ │ 🚧 Active Blockers           │   │
│ │ [Idle list...]       │ │ [Blocker list...]            │   │
│ └──────────────────────┘ └──────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

### 3.2 Navigation

**Top Bar:**
- Logo + "OpenClaw Agent Dashboard"
- Quick stats (Active sessions, Today's cost, Alerts)
- Settings icon (⚙️)
- Logout/Auth indicator (🔐)

**Sidebar (Optional for Full Version):**
- 🏠 Overview (main dashboard)
- 🔴 Live Sessions
- 💰 Costs & Budgets
- 📊 Analytics
- 🚧 Blockers
- ⚙️ Settings
- 📖 Docs

---

### 3.3 Color Scheme

**Status Colors:**
- 🟢 Green: Healthy, active, success
- 🟡 Yellow: Warning, idle, approaching limit
- 🔴 Red: Critical, failed, over budget
- ⚪ Gray: Inactive, completed, neutral

**UI Palette:**
- Background: Dark mode (#1a1a1a) or Light mode (#ffffff)
- Primary: Blue (#3b82f6)
- Secondary: Purple (#8b5cf6)
- Accent: Orange (#f97316)
- Text: Light gray (#e5e5e5) or Dark gray (#404040)

---

### 3.4 Responsive Design

**Desktop (>1024px):**
- 3-column grid layout
- All sections visible simultaneously
- Sidebar navigation (optional)

**Tablet (768px-1024px):**
- 2-column grid layout
- Collapsible sections
- Hamburger menu for navigation

**Mobile (<768px):**
- Single-column stack
- Swipeable cards
- Bottom navigation tabs

---

## 4. Technical Architecture

### 4.1 Tech Stack Evaluation

| Stack | Pros | Cons | Recommendation |
|-------|------|------|----------------|
| **Next.js + React** | Modern, SSR/SSG, large ecosystem, Vercel deployment | Heavier bundle, more complex setup | ⭐ **RECOMMENDED** |
| **Flask + Jinja2** | Python-native, simple setup, easy integration | Less modern UI, manual frontend work | ✅ Good for MVP |
| **Static Site (HTML/CSS/JS)** | Ultra-simple, no server, fast | No SSR, limited features, manual data fetching | ❌ Too limited |
| **SvelteKit** | Fast, modern, smaller bundles | Smaller ecosystem, less familiar | ✅ Alternative |
| **Streamlit** | Python-native, rapid prototyping | Not designed for production dashboards | ❌ Not suitable |

---

### 4.2 Recommended Stack: **Next.js + TypeScript + Tailwind**

**Rationale:**
1. **Modern:** React ecosystem with SSR/SSG for performance
2. **TypeScript:** Type safety for data models (sessions, costs, etc.)
3. **Tailwind CSS:** Rapid UI development with utility classes
4. **API Routes:** Built-in backend for data fetching
5. **Vercel Deployment:** One-click deploy, free tier available
6. **Real-time:** Easy WebSocket integration (Socket.io or Pusher)

**Tech Stack Details:**
```
Frontend:
  - Next.js 14+ (App Router)
  - React 18
  - TypeScript 5+
  - Tailwind CSS 3
  - Recharts (charts/graphs)
  - SWR or React Query (data fetching)

Backend (API Routes):
  - Node.js runtime
  - File system access to data sources
  - SQLite driver (better-sqlite3)
  - Markdown parser (remark)
  - JSON parser (native)

Real-time:
  - Socket.io (WebSocket fallback)
  - OR Polling (10-30s interval, simpler)

Deployment:
  - Vercel (recommended)
  - OR VPS (localhost:3000)
  - OR Docker container
```

---

### 4.3 Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Browser)                    │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐             │
│  │ Live       │  │ Cost       │  │ Timeline   │             │
│  │ Sessions   │  │ Tracker    │  │ View       │             │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘             │
└────────┼───────────────┼───────────────┼────────────────────┘
         │               │               │
         │ HTTP GET /api/sessions        │
         │ HTTP GET /api/costs           │
         │ HTTP GET /api/timeline        │
         │ (10-30s polling OR WebSocket) │
         │               │               │
┌────────▼───────────────▼───────────────▼────────────────────┐
│                    Backend (API Routes)                      │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ /api/sessions → Read sessions.json                     │  │
│  │ /api/costs → Query cost-tracking.db                    │  │
│  │ /api/timeline → Parse work-log.md + subagent-log.jsonl│  │
│  │ /api/blockers → Read blocked-items.json                │  │
│  │ /api/alerts → Compute alerts based on thresholds       │  │
│  │ /api/kill-session → Kill idle agent (exec command)     │  │
│  └────────────────────────────────────────────────────────┘  │
└────────┬───────────────┬───────────────┬────────────────────┘
         │               │               │
         │ File System Access            │
         │               │               │
┌────────▼───────────────▼───────────────▼────────────────────┐
│                      Data Sources                            │
│  ┌────────────┐  ┌────────────┐  �┌────────────┐            │
│  │ sessions.  │  │ cost-      │  │ work-log.  │            │
│  │ json       │  │ tracking.db│  │ md         │            │
│  └────────────┘  └────────────┘  └────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

---

### 4.4 Data Refresh Strategy

**Option 1: HTTP Polling (RECOMMENDED for MVP)**

**Pros:**
- Simple to implement
- Works everywhere (no WebSocket issues)
- Easy to debug
- Lower complexity

**Cons:**
- Higher latency (10-30s delay)
- More HTTP requests
- Less "real-time" feel

**Implementation:**
```typescript
// Frontend: SWR with polling
import useSWR from 'swr';

const { data, error } = useSWR('/api/sessions', fetcher, {
  refreshInterval: 10000, // Poll every 10 seconds
  revalidateOnFocus: true,
});
```

**Polling Intervals by Feature:**
- Live sessions: 10s
- Cost tracker: 30s
- Timeline: 30s
- Blockers: 60s
- Historical trends: 5min

---

**Option 2: WebSocket (Real-time Updates)**

**Pros:**
- True real-time updates
- Lower latency (<1s)
- More efficient (single connection)
- Better UX for live data

**Cons:**
- More complex setup
- Requires WebSocket server
- Firewall issues on some networks
- Harder to debug

**Implementation:**
```typescript
// Backend: Socket.io server
import { Server } from 'socket.io';

const io = new Server(httpServer);

// Watch sessions.json for changes
fs.watch('/data/.openclaw/agents/main/sessions/sessions.json', () => {
  io.emit('sessions:update', loadSessions());
});

// Frontend: Socket.io client
import { io } from 'socket.io-client';

const socket = io('http://localhost:3000');
socket.on('sessions:update', (data) => {
  setSessions(data);
});
```

**Recommendation:** Start with **polling** for MVP, add WebSocket in Phase 2 if needed.

---

### 4.5 API Endpoints

| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/api/sessions` | GET | List all sessions | `{ sessions: [...] }` |
| `/api/sessions/:id` | GET | Get session details | `{ session: {...} }` |
| `/api/sessions/:id/kill` | POST | Kill idle session | `{ success: true }` |
| `/api/costs` | GET | Cost summary | `{ today: {...}, month: {...}, breakdown: [...] }` |
| `/api/costs/trend` | GET | Cost trend data | `{ daily: [...], weekly: [...] }` |
| `/api/timeline` | GET | Activity events | `{ events: [...] }` |
| `/api/blockers` | GET | Active blockers | `{ blockers: [...] }` |
| `/api/blockers/:id/resolve` | POST | Mark blocker resolved | `{ success: true }` |
| `/api/alerts` | GET | Active alerts | `{ alerts: [...] }` |
| `/api/health` | GET | System health | `{ disk: {...}, memory: {...}, ... }` |

---

### 4.6 Data Models (TypeScript)

```typescript
// Session model
interface Session {
  sessionId: string;
  sessionKey: string;
  updatedAt: number; // Unix timestamp (ms)
  chatType: 'direct' | 'group' | 'subagent';
  model: string;
  modelProvider: string;
  inputTokens: number;
  outputTokens: number;
  totalTokens: number;
  compactionCount: number;
  lastHeartbeatText?: string;
  lastHeartbeatSentAt?: number;
  abortedLastRun: boolean;
  status: 'active' | 'idle' | 'stuck'; // Computed
  cost: number; // Computed from tokens + model
}

// Cost entry model
interface CostEntry {
  id: number;
  timestamp: string; // ISO 8601
  model: string;
  inputTokens: number;
  outputTokens: number;
  inputCost: number;
  outputCost: number;
  totalCost: number;
  sessionKey?: string;
  context?: string;
}

// Timeline event model
interface TimelineEvent {
  id: string;
  timestamp: string; // ISO 8601
  type: 'spawn' | 'complete' | 'fail' | 'checkpoint' | 'heartbeat' | 'alert';
  title: string;
  description?: string;
  sessionKey?: string;
  metadata?: Record<string, any>;
}

// Blocker model
interface Blocker {
  id: number;
  task: string;
  blocker: string;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  category: 'Infrastructure' | 'Code' | 'External' | 'Unknown';
  createdAt: string; // ISO 8601
  resolvedAt?: string; // ISO 8601
  ageInDays: number; // Computed
}

// Alert model
interface Alert {
  id: string;
  type: 'cost' | 'idle' | 'cascade' | 'token_spike' | 'blocker_stale' | 'heartbeat_miss';
  severity: 'high' | 'medium' | 'low';
  message: string;
  timestamp: string; // ISO 8601
  metadata?: Record<string, any>;
}
```

---

## 5. Implementation Phases

### Phase 1: MVP (2-3 days)

**Goal:** Core monitoring functionality with manual refresh

**Features:**
- ✅ Live session list (read-only, manual refresh)
- ✅ Real-time cost tracker (daily + monthly totals)
- ✅ Idle agent detection (visual indicators)
- ✅ Basic activity timeline (last 24 hours)
- ✅ Simple alert banners (cost + idle thresholds)

**Tech Stack:**
- Next.js (App Router)
- TypeScript
- Tailwind CSS
- HTTP polling (30s interval)
- No authentication (localhost only)

**Deliverables:**
- `/pages/index.tsx` - Main dashboard
- `/api/sessions.ts` - Session data API
- `/api/costs.ts` - Cost data API
- `/api/timeline.ts` - Timeline API
- `/lib/parsers.ts` - Data parsing utilities
- `README.md` - Setup instructions

**Acceptance Criteria:**
- Dashboard loads in <2s
- All metrics display correctly
- Polling updates every 30s
- Runs on `localhost:3000`

---

### Phase 2: Enhanced Features (3-5 days)

**Goal:** Add interactivity, detailed views, and improved UX

**Features:**
- ✅ Session detail view (click to expand)
- ✅ Kill idle session button (with confirmation)
- ✅ Cost breakdown by model (pie + bar charts)
- ✅ Blocker dashboard (read + resolve)
- ✅ Historical trends (7-day charts)
- ✅ Configurable alert thresholds
- ✅ Export data (JSON/CSV)

**Tech Stack:**
- Add Recharts for visualizations
- Add SWR for efficient polling
- Add form handling (react-hook-form)

**Deliverables:**
- `/pages/session/[id].tsx` - Session detail page
- `/pages/costs.tsx` - Full cost analytics page
- `/pages/blockers.tsx` - Blocker management page
- `/api/sessions/[id]/kill.ts` - Kill session endpoint
- `/api/blockers/[id]/resolve.ts` - Resolve blocker endpoint

**Acceptance Criteria:**
- Can kill idle sessions from UI
- Charts render correctly
- Exports work (JSON + CSV)
- Alert thresholds configurable

---

### Phase 3: Real-time & Advanced (5-7 days)

**Goal:** True real-time updates, advanced analytics, and automation

**Features:**
- ✅ WebSocket real-time updates (<1s latency)
- ✅ 30-day historical trends
- ✅ Token efficiency analysis
- ✅ Cascade failure detection
- ✅ Session replay (log viewer)
- ✅ Automated alerts (email + Telegram)
- ✅ Authentication (basic auth or OAuth)

**Tech Stack:**
- Add Socket.io for WebSocket
- Add nodemailer for email alerts
- Add Telegram Bot API for notifications
- Add NextAuth.js for authentication

**Deliverables:**
- `/lib/websocket.ts` - WebSocket server
- `/pages/analytics.tsx` - Advanced analytics page
- `/pages/replay/[id].tsx` - Session replay viewer
- `/api/auth/[...nextauth].ts` - Authentication
- `/api/alerts/configure.ts` - Alert configuration

**Acceptance Criteria:**
- Real-time updates work (<1s)
- Alerts sent to email + Telegram
- Authentication protects dashboard
- Session replay functional

---

### Phase 4: Production Hardening (2-3 days)

**Goal:** Security, performance, and deployment

**Features:**
- ✅ Production-ready authentication
- ✅ Rate limiting on API endpoints
- ✅ Error handling + logging
- ✅ Performance optimization
- ✅ Monitoring (Sentry or similar)
- ✅ Docker deployment
- ✅ CI/CD pipeline

**Tech Stack:**
- Add rate-limit-redis
- Add Sentry for error tracking
- Add Docker + docker-compose
- Add GitHub Actions for CI/CD

**Deliverables:**
- `Dockerfile` + `docker-compose.yml`
- `.github/workflows/deploy.yml`
- Error handling middleware
- Performance monitoring setup
- Production deployment guide

**Acceptance Criteria:**
- Dashboard loads in <1s
- No security vulnerabilities
- Can deploy with one command
- Errors tracked in Sentry

---

## 6. Security & Access Control

### 6.1 Threat Model

**Sensitive Data:**
- Session keys (reveal user IDs, chat IDs)
- Cost data (financial information)
- Agent logs (may contain prompts/responses)
- System health metrics (attack surface mapping)

**Threats:**
- **Unauthorized Access:** Attacker views sensitive data
- **Data Exfiltration:** Attacker exports session logs
- **Session Hijacking:** Attacker kills active sessions
- **Cost Manipulation:** Attacker modifies cost data

---

### 6.2 Authentication Strategy

**Phase 1 (MVP): No Auth (Localhost Only)**
- Dashboard binds to `127.0.0.1:3000`
- Firewall blocks external access
- Assumes trusted local environment

**Phase 2 (Production): Basic Auth**
- HTTP Basic Authentication
- Single username + password (env variable)
- Simple, no OAuth complexity

**Phase 3 (Enterprise): OAuth/JWT**
- NextAuth.js with multiple providers
- GitHub OAuth (for team access)
- JWT tokens with refresh
- Role-based access (Admin, Viewer)

---

### 6.3 Authorization Levels

| Role | Permissions | Use Case |
|------|-------------|----------|
| **Admin** | Read + Write + Kill sessions | Main user |
| **Operator** | Read + Write (no kill) | Team members |
| **Viewer** | Read-only | Stakeholders, auditors |
| **Auditor** | Read costs + logs only | Finance team |

---

### 6.4 Security Checklist

- [ ] Authentication enabled (basic auth minimum)
- [ ] HTTPS/TLS for production deployment
- [ ] Rate limiting on API endpoints (10 req/s per IP)
- [ ] Input validation on all forms
- [ ] SQL injection protection (parameterized queries)
- [ ] XSS protection (React escaping + CSP headers)
- [ ] CSRF tokens on POST/DELETE requests
- [ ] Secure session storage (httpOnly cookies)
- [ ] Audit log for sensitive actions (kill session, change config)
- [ ] Environment variables for secrets (no hardcoded passwords)

---

## 7. Testing Strategy

### 7.1 Unit Tests

**Coverage Target:** 80%

**Test Files:**
- `lib/parsers.test.ts` - Data parsing functions
- `lib/costs.test.ts` - Cost calculation logic
- `lib/alerts.test.ts` - Alert threshold logic
- `api/sessions.test.ts` - Session API endpoints

**Example:**
```typescript
// lib/costs.test.ts
import { calculateCost } from './costs';

describe('calculateCost', () => {
  it('calculates cost for claude-sonnet-4-5', () => {
    const cost = calculateCost('claude-sonnet-4-5', 10000, 1000);
    expect(cost.total).toBe(0.045); // $3/M input + $15/M output
  });
  
  it('falls back to default pricing for unknown model', () => {
    const cost = calculateCost('unknown-model', 10000, 1000);
    expect(cost.total).toBe(0.045); // Uses default
  });
});
```

---

### 7.2 Integration Tests

**Coverage Target:** Key user flows

**Test Scenarios:**
1. Load dashboard → Verify all sections render
2. Poll sessions → Verify data updates every 10s
3. Kill idle session → Verify API call + UI update
4. Set budget alert → Verify alert triggers when exceeded
5. Export CSV → Verify download + data integrity

**Example:**
```typescript
// e2e/dashboard.test.ts
import { test, expect } from '@playwright/test';

test('dashboard loads and displays sessions', async ({ page }) => {
  await page.goto('http://localhost:3000');
  
  // Check header
  await expect(page.locator('h1')).toContainText('Agent Dashboard');
  
  // Check session count
  const sessions = page.locator('[data-testid="session-item"]');
  await expect(sessions).toHaveCount(5);
  
  // Check cost display
  await expect(page.locator('[data-testid="cost-today"]')).toContainText('$');
});
```

---

### 7.3 Performance Tests

**Metrics:**
- Initial page load: <2s
- API response time: <200ms
- Polling overhead: <10ms per request
- Memory usage: <100MB (frontend)

**Tools:**
- Lighthouse (Core Web Vitals)
- k6 (API load testing)
- Chrome DevTools (performance profiling)

---

## 8. Deployment Options

### 8.1 Option 1: Localhost (MVP)

**Use Case:** Personal development, single-user

**Pros:**
- Simple setup (`npm run dev`)
- No deployment complexity
- Full control

**Cons:**
- Not accessible remotely
- No redundancy
- Must run manually

**Steps:**
```bash
git clone <repo>
cd agent-dashboard
npm install
npm run dev
# Open http://localhost:3000
```

---

### 8.2 Option 2: VPS Deployment

**Use Case:** Team access, always-on monitoring

**Pros:**
- Accessible from anywhere
- Can run 24/7
- Full control over stack

**Cons:**
- Requires VPS management
- Manual SSL setup
- Must handle uptime

**Steps:**
```bash
# On VPS (e.g., Hostinger 76.13.46.217)
git clone <repo>
cd agent-dashboard
npm install
npm run build
npm run start
# Use nginx reverse proxy + SSL
```

**nginx config:**
```nginx
server {
  listen 80;
  server_name dashboard.yourdomain.com;
  
  location / {
    proxy_pass http://localhost:3000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
  }
}
```

---

### 8.3 Option 3: Vercel (Recommended)

**Use Case:** Zero-config deployment, free tier

**Pros:**
- One-click deploy
- Automatic SSL
- Global CDN
- Free tier (100GB bandwidth)
- Serverless functions (API routes)

**Cons:**
- Serverless limitations (10s timeout)
- File system access limited (read-only)
- Must deploy data to Vercel (or use external DB)

**Steps:**
```bash
npm install -g vercel
vercel login
vercel deploy
# Dashboard live at https://your-project.vercel.app
```

**Configuration:**
```json
// vercel.json
{
  "env": {
    "DATA_DIR": "/data/.openclaw/workspace"
  },
  "regions": ["iad1"]
}
```

**Note:** Vercel deployment requires data to be accessible via API or mounted volume.

---

### 8.4 Option 4: Docker Container

**Use Case:** Consistent deployment, easy scaling

**Pros:**
- Reproducible environment
- Easy to deploy anywhere
- Can include data volume mount
- Portable across VPS/cloud

**Cons:**
- Requires Docker knowledge
- Slightly more complex setup

**Dockerfile:**
```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

**docker-compose.yml:**
```yaml
version: '3.8'
services:
  dashboard:
    build: .
    ports:
      - "3000:3000"
    volumes:
      - /data/.openclaw/workspace:/data:ro
    environment:
      - NODE_ENV=production
      - DASHBOARD_PASSWORD=${DASHBOARD_PASSWORD}
```

**Deployment:**
```bash
docker-compose up -d
```

---

### 8.5 Recommended Deployment Path

| Phase | Deployment | Reason |
|-------|-----------|--------|
| **MVP** | Localhost | Fast iteration, no deploy complexity |
| **Beta** | VPS (Docker) | Team access, controlled environment |
| **Production** | Vercel OR VPS | Scale based on usage |

---

## 9. Maintenance & Operations

### 9.1 Maintenance Tasks

| Task | Frequency | Owner | Time |
|------|-----------|-------|------|
| Update dependencies | Weekly | Dev | 15min |
| Review logs for errors | Daily | Ops | 5min |
| Check alert thresholds | Monthly | Admin | 10min |
| Database cleanup (old logs) | Monthly | Ops | 5min |
| Performance review | Quarterly | Dev | 1hr |

---

### 9.2 Monitoring

**Dashboard Uptime:**
- Use UptimeRobot or similar (free)
- Alert if dashboard down >5min

**Error Tracking:**
- Sentry for frontend errors
- Logs to `/tmp/dashboard-errors.log`

**Performance:**
- Lighthouse CI in GitHub Actions
- Alert if performance score <90

---

### 9.3 Backup Strategy

**Data to Backup:**
- Dashboard configuration (alert thresholds, etc.)
- User settings (if stored locally)

**Note:** Source data (`sessions.json`, `cost-tracking.db`) is already backed up by workspace backup scripts.

---

## 10. Appendix

### 10.1 Example API Responses

**GET /api/sessions**
```json
{
  "sessions": [
    {
      "sessionKey": "agent:main:main",
      "sessionId": "4d6a1582-7edd-49df-a0f5-537bb85b55e9",
      "status": "active",
      "model": "claude-sonnet-4-5",
      "totalTokens": 95686,
      "cost": 0.42,
      "lastActive": "2026-02-13T16:03:02Z",
      "idleMinutes": 0
    },
    {
      "sessionKey": "agent:main:subagent:d0fc17e0",
      "sessionId": "c87a553f-9ddd-4562-b72d-f7609cfaa8bf",
      "status": "idle",
      "model": "claude-sonnet-4-5",
      "totalTokens": 12300,
      "cost": 0.08,
      "lastActive": "2026-02-13T14:18:00Z",
      "idleMinutes": 105
    }
  ]
}
```

**GET /api/costs**
```json
{
  "today": {
    "total": 2.34,
    "budget": 5.00,
    "percent": 47,
    "projected": 4.12
  },
  "month": {
    "total": 42.18,
    "budget": 100.00,
    "percent": 42,
    "projected": 87.23
  },
  "breakdown": [
    { "model": "claude-sonnet-4-5", "cost": 28.34, "percent": 67 },
    { "model": "llama-3.3-70b", "cost": 8.12, "percent": 19 },
    { "model": "grok-3", "cost": 5.92, "percent": 14 }
  ]
}
```

---

### 10.2 Code Style Guide

**TypeScript:**
- ESLint + Prettier
- 2-space indentation
- Single quotes
- Trailing commas

**React:**
- Functional components only
- Named exports for components
- Props interface per component

**Example:**
```typescript
interface SessionCardProps {
  session: Session;
  onKill: (sessionKey: string) => void;
}

export function SessionCard({ session, onKill }: SessionCardProps) {
  const status = getSessionStatus(session);
  
  return (
    <div className="border rounded p-4">
      <h3 className="font-bold">{session.sessionKey}</h3>
      <p>Status: {status}</p>
      <button onClick={() => onKill(session.sessionKey)}>
        Kill Session
      </button>
    </div>
  );
}
```

---

### 10.3 Performance Optimization Tips

1. **Polling Optimization:**
   - Use SWR `dedupingInterval` to prevent duplicate requests
   - Implement exponential backoff on errors
   - Cache responses with stale-while-revalidate

2. **Data Parsing:**
   - Parse large files (work-log.md) incrementally
   - Cache parsed data with TTL
   - Use Web Workers for heavy parsing

3. **Rendering:**
   - Virtualize long lists (react-window)
   - Memoize expensive components
   - Lazy load charts (dynamic import)

4. **Bundle Size:**
   - Tree-shake unused dependencies
   - Use dynamic imports for large libraries
   - Compress with gzip/brotli

---

### 10.4 Future Enhancements (Post-MVP)

**Advanced Features:**
- AI-powered anomaly detection (unusual cost spikes)
- Predictive analytics (forecast next month's costs)
- A/B testing for model selection (cost vs quality)
- Multi-agent comparison (performance benchmarking)
- Custom dashboard widgets (user-configurable layout)
- Mobile app (React Native)
- Public status page (for stakeholders)

**Integrations:**
- Slack notifications
- PagerDuty alerts
- Grafana/Prometheus metrics export
- LangSmith integration (if using LangChain)

---

### 10.5 Reference Links

**OpenClaw Docs:**
- Sessions: `/docs/sessions.md`
- Cost Tracking: `/tools/cost_tracker.py`
- Session Cleanup: `/tools/session_cleanup.py`

**Industry Best Practices:**
- [AI Agent Monitoring Best Practices (UptimeRobot)](https://uptimerobot.com/knowledge-hub/monitoring/ai-agent-monitoring-best-practices-tools-and-metrics/)
- [11 Key Observability Best Practices (Spacelift)](https://spacelift.io/blog/observability-best-practices)

**Tech Stack:**
- [Next.js Documentation](https://nextjs.org/docs)
- [Recharts Examples](https://recharts.org/en-US/examples)
- [SWR Documentation](https://swr.vercel.app/)
- [Socket.io Guide](https://socket.io/docs/v4/)

---

## Summary

This specification provides a complete blueprint for building an agent observability dashboard for OpenClaw. The recommended approach is:

1. **Phase 1 (MVP):** Build core monitoring (live sessions, costs, alerts) with Next.js + polling
2. **Phase 2:** Add interactivity (kill sessions, manage blockers, export data)
3. **Phase 3:** Implement real-time updates (WebSocket), advanced analytics, and automation
4. **Phase 4:** Production hardening (auth, security, deployment)

**Estimated Timeline:**
- MVP: 2-3 days
- Full Implementation: 2 weeks
- Ongoing Maintenance: 2 hours/week

**Recommended Tech Stack:** Next.js + TypeScript + Tailwind CSS + HTTP Polling (MVP) → WebSocket (Phase 3)

**Deployment:** Start with localhost, move to VPS (Docker) for team access, or Vercel for zero-config deployment.

---

**Document Status:** ✅ COMPLETE - Ready for Architect Review  
**Next Steps:** Review with team → Prioritize features → Begin Phase 1 implementation  
**Author:** Researcher Subagent (OpenClaw)  
**Date:** 2026-02-13 16:30 UTC
