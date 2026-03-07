# TOOLS.md - Local Notes

## VPS
- **Provider:** Hostinger | **IP:** 76.13.46.217 | **Hostname:** srv1353853
- **Container:** openclaw-khc5-openclaw-1 | **OS:** Linux x64 | **Node:** v22.22.0
- **Workspace:** `/data/.openclaw/workspace`

## API Keys
- **Vault:** `/data/.openclaw/workspace/.api-keys-vault` (permissions 600, git-excluded)
- **All keys in openclaw.json env** — no Docker env dependency
- **Rotation:** Every 90 days (GitHub, Twitter next: 2026-05-11)

## Telegram
- Paired users: 428513734 (AB), 8417397353
- Telegram-only mode, control UI localhost-only

## Twitter (@RuntimeRogue)
- Pay-as-you-go tier — read-only (post/DM requires Pro $100/mo)

## GitHub
- Repo: bensargotest-sys/bensargotest-sys
- Credentials: `.github-credentials` (600, not git-tracked)

## Model Notes
- gemini/gemini-2.0-flash: FREE direct Gemini API (provider: `gemini`, NOT `google` — `google` collides with built-in native SDK provider). Use for sub-agents + cron.
- gemini/gemini-3.1-pro-preview: FREE on Google AI Studio (rate limited)
- Provider `google` = built-in native Gemini SDK (google-generative-ai). Provider `gemini` = OpenAI-compatible endpoint. Must use `gemini` for our config.

## MELD Nodes
- meld-2: srv1396191, 147.93.72.73, grok-3 (agent-006a0c9e)
- meld-3: srv1396192, 72.61.53.248, gemini-2.0-flash (agent-4c99792a)
- meld-4: srv1396193, 76.13.198.23, deepseek-chat (agent-b3470fbc)
- meld-5: srv1410420, 187.77.177.78, claude-haiku-4-5 (agent-efde9985)
- meld-6: srv1410415, 76.13.209.192, gpt-4o-mini (agent-359155ec)
- meld-1: DO NOT TOUCH (incompatible codebase)

## MELD Build Rules
1. Backup before editing node files (cp file file.bak)
2. Commit to production branch after deploy
3. Verify PM2 online after restart
4. Never change credentials without explicit user confirmation
