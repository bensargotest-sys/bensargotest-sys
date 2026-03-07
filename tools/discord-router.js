#!/usr/bin/env node
/**
 * MELD Discord Router
 * 
 * Reads recent Telegram session transcript, categorizes messages by topic,
 * and posts summaries to appropriate Discord channels.
 * 
 * Run via OpenClaw cron (isolated session with message tool access).
 * 
 * Channel mapping:
 *   #research (1476987786778382336) — research findings, experiment results, papers
 *   #dev (1476987786778382337) — code changes, bugs, deploys, technical
 *   #strategy (1476987786778382338) — business, positioning, pricing, market
 *   #ops (1476987786778382339) — infrastructure, monitoring, alerts
 *   #log (1476987786778382340) — general updates, decisions, summaries
 */

// This script is meant to be called as a prompt for an OpenClaw cron agentTurn.
// The actual routing logic lives in the cron job's prompt.

console.log("Discord Router - use via cron agentTurn prompt, not direct execution.");
console.log("See DISCORD-ROUTER-PRD.md for architecture.");
