# QMD Setup and Usage Guide

**Last Updated:** 2026-02-14  
**Status:** Production-ready, fully indexed

---

## What is QMD?

QMD is a local semantic search engine for markdown files. It provides:
- **Full-text search** (BM25) - Fast keyword matching
- **Vector search** - Semantic similarity using local embeddings
- **Hybrid search** - Combined query with expansion and reranking
- **MCP integration** - AI agent-friendly interface

**Key Features:**
- 100% local (no cloud dependencies)
- Auto-downloaded models from HuggingFace
- Fast indexing (~1 second per file)
- Efficient embeddings (800 token chunks, 15% overlap)

---

## Installation

QMD is already installed globally via Bun:
```bash
/data/.bun/bin/qmd
```

To install on a new system:
```bash
bun install -g https://github.com/tobi/qmd
```

---

## Current Setup

### Collection: workspace
- **Path:** `/data/.openclaw/workspace`
- **Pattern:** `*.md`
- **Files indexed:** 99 markdown files
- **Status:** Up-to-date (as of 2026-02-14)
- **Database:** `/data/.cache/qmd/index.sqlite` (4.2 MB)

### Embeddings
- **Chunks:** 292 embedded
- **Model:** embeddinggemma-300M-Q8_0
- **Reranking:** qwen3-reranker-0.6b-q8_0
- **Status:** ✅ Complete

---

## Basic Usage

### 1. Search (Full-text + Semantic)
```bash
# Hybrid search with reranking (best quality)
qmd query "smart router cost savings" -n 5

# Full-text search only (fastest)
qmd search "smart router" -n 10

# Vector search only (semantic similarity)
qmd vsearch "how to reduce costs" -n 5
```

### 2. List Files
```bash
# List all collections
qmd collection list

# List files in workspace collection
qmd ls workspace

# List files in specific directory
qmd ls workspace/tools
```

### 3. Get Documents
```bash
# Get full document
qmd get qmd://workspace/HEARTBEAT.md

# Get specific line range
qmd get qmd://workspace/MEMORY.md:50 -l 20

# Get from line 100 onwards
qmd get qmd://workspace/AGENTS.md --from 100
```

### 4. Multi-Get (Bulk Retrieval)
```bash
# Get multiple files by pattern
qmd multi-get "tools/*.py" -l 50

# Get specific files (comma-separated)
qmd multi-get "AGENTS.md,SOUL.md,USER.md"

# JSON output for parsing
qmd multi-get "memory/*.md" --json
```

### 5. Update Index
```bash
# Re-index all collections
qmd update

# Update and pull git repos first
qmd update --pull

# Update embeddings after adding new files
qmd embed
```

---

## Output Formats

### JSON
```bash
qmd query "cost tracking" --json -n 3
```
Returns: `{results: [{docid, score, filepath, snippet, context}]}`

### CSV
```bash
qmd search "heartbeat" --csv -n 10
```
Returns: `docid,score,filepath,snippet,context`

### Files Only
```bash
qmd query "smart router" --files -n 20
```
Returns: `docid,score,filepath,context` (no snippets, more results)

### Markdown
```bash
qmd search "enforcement rules" --md -n 5
```
Returns: Markdown-formatted results with headings

---

## Search Options

### Filtering
```bash
# Filter by collection
qmd query "backup script" -c workspace

# Minimum similarity score
qmd vsearch "security audit" --min-score 0.7

# Return all matches above threshold
qmd search "cron job" --all --min-score 0.5
```

### Output Control
```bash
# Change number of results (default: 5)
qmd query "session management" -n 10

# Show full documents instead of snippets
qmd search "heartbeat" --full

# Add line numbers
qmd query "checkpoint" --line-numbers
```

---

## Common Use Cases

### 1. Find Tool Documentation
```bash
qmd query "how to use heartbeat_enforcer.py" -n 3
```

### 2. Recall Past Decisions
```bash
qmd search "decided to" --json | jq '.results[] | .filepath'
```

### 3. Find Code Examples
```bash
qmd query "example usage of subagent spawn" -n 5 --md
```

### 4. Search Memory Files
```bash
qmd search "blocker" -c workspace | grep -E "memory/"
```

### 5. Find Configuration
```bash
qmd query "how to configure smart router" -n 3
```

---

## Maintenance

### Daily
```bash
# Quick update (only changed files)
qmd update
```

### Weekly
```bash
# Full update with embeddings
qmd update
qmd embed

# Check status
qmd status
```

### Monthly
```bash
# Clean up orphaned data
qmd cleanup
```

---

## Integration with Heartbeats

### Tool Rotation (Every 5th Heartbeat)
```bash
# Check if QMD index is stale
if [ $(find /data/.cache/qmd/index.sqlite -mtime +1) ]; then
    echo "QMD index stale, updating..."
    qmd update
fi
```

### Search Before Building
```bash
# Before creating a new tool, search for similar ones
qmd query "tool similar to session_audit" -n 5 --files
```

### Memory Recall
```bash
# Search memory for past context
qmd query "what did we decide about TSP" -c workspace | grep memory/
```

---

## Performance

### Indexing Speed
- **Initial index:** ~1 second per file
- **Updates:** Only changed files re-indexed
- **99 files:** ~2 seconds (incremental update)

### Search Speed
- **Full-text:** <100ms
- **Vector search:** ~1 second (with reranking)
- **Hybrid query:** ~1-2 seconds

### Storage
- **Index:** 4.2 MB (99 files, 292 chunks)
- **Models:** Auto-cached in `/data/.cache/qmd/`

---

## Troubleshooting

### Index Out of Date
```bash
# Force full re-index
qmd update
qmd embed -f
```

### No Results Found
```bash
# Check what's indexed
qmd status
qmd ls workspace

# Try different search methods
qmd search "keyword"        # Exact match
qmd vsearch "concept"       # Semantic
qmd query "fuzzy concept"   # Hybrid
```

### Slow Searches
```bash
# Use full-text search for speed
qmd search "exact phrase" -n 5

# Reduce result count
qmd query "concept" -n 3
```

---

## Advanced Features

### Context Annotations
```bash
# Add context for better search results
qmd context add qmd://workspace/tools "Python automation scripts"
qmd context list
```

### Custom Collections
```bash
# Add a new collection
qmd collection add ~/Documents --name docs --mask "*.md"

# Search specific collection
qmd query "notes" -c docs
```

### MCP Server Mode
```bash
# Start MCP server for AI agent integration
qmd mcp
```

---

## Files to Index

### Current Workspace (99 files)
- AGENTS.md, SOUL.md, USER.md, TOOLS.md
- HEARTBEAT.md, MEMORY.md, WORKING_STATE.md
- memory/*.md (daily logs)
- tools/*.md (tool documentation)
- workflows/*.md (agent templates)
- docs/*.md (guides)

### Exclusions
- node_modules/ (auto-excluded)
- .git/ (auto-excluded)
- Binary files (auto-excluded)

---

## Next Steps

1. **Use in heartbeats:** Search before creating new tools
2. **Memory recall:** Query memory files before answering questions
3. **Pattern discovery:** Find repeated patterns across files
4. **Documentation search:** Quick access to guides and references

---

## Resources

- **Repository:** https://github.com/tobi/qmd
- **Index location:** `/data/.cache/qmd/index.sqlite`
- **Help:** `qmd --help`
- **Status:** `qmd status`

---

**Status:** ✅ Production-ready  
**Last indexed:** 2026-02-14 11:12 UTC  
**Files:** 99  
**Embeddings:** 292  
**Quality:** High (semantic search tested and working)
