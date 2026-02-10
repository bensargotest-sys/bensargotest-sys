# OpenClaw Production Setup - Master Plan

**Started:** 2026-02-09  
**VPS:** Hostinger, 76.13.46.217  
**User:** AB (@ABDB09)  
**Goal:** Full autonomous AI operations platform

## Phase 1: Security & Foundation (CRITICAL - Do First)
**Status:** In Progress

### 1.1 Immediate Security Hardening ✅ STARTED
- [x] Fix file permissions (API keys, state dir)
- [x] Disable insecure HTTP auth
- [ ] Set up Hostinger firewall rules
- [ ] Set up automated backups (Docker volumes)
- [ ] Document SSH tunnel access pattern

### 1.2 Workspace Structure ✅ COMPLETE
- [x] Create directory structure (memory/, tools/, reviews/, workflows/)
- [x] Create core files (WORKING_STATE.md, ENFORCEMENT.md, HEARTBEAT.md)
- [x] Set up daily log template
- [x] Initialize task tracking system

### 1.3 HTTPS Access (Tailscale or Reverse Proxy)
- [ ] Choose approach (Tailscale vs domain + Let's Encrypt)
- [ ] Install and configure
- [ ] Test secure access
- [ ] Document access procedures

## Phase 2: Memory & Recovery System
**Status:** Complete

### 2.1 Memory Architecture ✅ COMPLETE
- [x] Create memory file structure
- [x] Build checkpoint.py tool
- [x] Build compaction_guard.sh
- [x] Set up session handoff template
- [x] Initialize heartbeat-state.json

### 2.2 Recovery Protocol
- [ ] Document recovery workflow
- [ ] Test context recovery after compaction
- [ ] Build auto-recovery on session start

## Phase 3: Agent Team System
**Status:** Not Started

### 3.1 Team Definition
- [ ] Define team roles (Researcher, Coder, Writer, Analyst)
- [ ] Create spawn templates with verification rules
- [ ] Document delegation rules
- [ ] Build subagent_log.py for tracking

### 3.2 Closed Loop (Auditor/Implementer)
- [ ] Create audit-and-fix workflow template
- [ ] Define Auditor spawn template
- [ ] Define Implementer spawn template
- [ ] Test full closed loop cycle

## Phase 4: Infrastructure Tools
**Status:** Not Started

### 4.1 Core Tools (Build These First) ✅ COMPLETE
- [x] checkpoint.py
- [x] compaction_guard.sh
- [x] subagent_log.py
- [x] heartbeat_enforcer.py
- [x] mistake_logger.py
- [x] mistake_promoter.py

### 4.2 Monitoring Tools
- [ ] server_health.py (disk, RAM, services, SSL)
- [ ] monitor.py template (generic daemon pattern)
- [ ] Alert system (threshold-based)

### 4.3 Task Management Tools
- [ ] task_queue.py
- [ ] blocked_items.py
- [ ] kanban integration

## Phase 5: Heartbeat System
**Status:** Not Started

### 5.1 Heartbeat Configuration
- [ ] Create HEARTBEAT.md with full loop
- [ ] Create heartbeat-backlog.md (seed with 15+ items)
- [ ] Build heartbeat_integrations.py (rotation scheduler)
- [ ] Configure rate limiting (30min minimum)

### 5.2 Automated Checks
- [ ] Position/status monitors
- [ ] Email/calendar checks
- [ ] Memory consolidation
- [ ] Self-evaluation logging

## Phase 6: Enforcement Framework
**Status:** Not Started

### 6.1 Enforcement Rules
- [ ] Create ENFORCEMENT.md with initial gates
- [ ] Build enforcement_watchdog.py
- [ ] Set up mistake-to-rule pipeline
- [ ] Test promotion workflow

### 6.2 Compliance Automation
- [ ] Session start checklist enforcement
- [ ] Auto-checkpoint triggers
- [ ] TDD enforcement for code
- [ ] Identity protection rules

## Phase 7: Scheduled Jobs & Automation
**Status:** Not Started

### 7.1 Cron Job Setup
- [ ] Morning briefing (7am)
- [ ] Daily digest (10pm)
- [ ] Overnight maintenance (2am)
- [ ] Health checks (every 30min)
- [ ] Weekly review (Monday 9am)

### 7.2 Service Configuration
- [ ] Create systemd units for monitors
- [ ] Configure auto-restart on failure
- [ ] Set up journald logging

## Phase 8: Server Infrastructure
**Status:** Not Started

### 8.1 Reverse Proxy
- [ ] Install Caddy
- [ ] Configure automatic HTTPS
- [ ] Set up TLS termination
- [ ] Test external access

### 8.2 Service Stack
- [ ] OpenClaw gateway service
- [ ] Monitor daemons
- [ ] Dashboard service (optional)

## Phase 9: Skills & Integrations
**Status:** Not Started

### 9.1 Core Skills Installation
- [ ] karpathy-coding (mandatory for all coding tasks)
- [ ] firecrawl (web research)
- [ ] self-improvement (heartbeat reflection)
- [ ] deep-research

### 9.2 Skills Gate Implementation
- [ ] Add skills check to ENFORCEMENT.md
- [ ] Build skills scanner
- [ ] Document skill usage patterns

## Phase 10: Advanced Features
**Status:** Not Started

### 10.1 QMD Workspace Search
- [ ] Install QMD
- [ ] Index workspace
- [ ] Build vector embeddings
- [ ] Integrate into workflows

### 10.2 Dashboard (Optional)
- [ ] Design dashboard panels
- [ ] Build web app
- [ ] Wire to data sources
- [ ] Deploy behind reverse proxy

### 10.3 Monitoring & Alerting
- [ ] Build generic monitor pattern
- [ ] Set up SQLite databases
- [ ] Configure threshold alerts
- [ ] Wire into heartbeat checks

---

## Execution Strategy

**Priority Order:**
1. Phase 1 (Security) - CRITICAL, do immediately
2. Phase 2 (Memory) - Essential for persistence
3. Phase 3 (Team) - Enables delegation
4. Phase 4 (Tools) - Compounds efficiency
5. Phase 5 (Heartbeat) - Enables autonomous work
6. Rest as needed

**Estimated Timeline:**
- Phase 1: 2-4 hours
- Phases 2-5: 1-2 days
- Phases 6-10: 1-2 weeks (iterative)

**Next Steps:**
1. Complete Phase 1.1 (firewall + backups)
2. Complete Phase 1.2 (workspace structure)
3. Choose HTTPS approach (Phase 1.3)
4. Begin Phase 2 (memory system)
