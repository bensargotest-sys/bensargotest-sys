#!/usr/bin/env python3
"""
Retrieval Engine — Builds rich context blocks for sub-agent prompts.

Searches across memory files, intel, and workspace to build relevant context.

Usage:
    python3 tools/retrieval/retrieval_engine.py retrieve "task description"
    python3 tools/retrieval/retrieval_engine.py build-context "task description" [--max-tokens 4000]
"""

import argparse
import os
import re
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path("/data/.openclaw/workspace")

SEARCH_DIRS = [
    ("memory", WORKSPACE / "memory", "*.md"),
    ("intel", WORKSPACE / "intel", "*.*"),
    ("research", WORKSPACE / "research", "*.md"),
    ("docs", WORKSPACE / "docs", "*.md"),
]

CORE_FILES = [
    WORKSPACE / "MEMORY.md",
    WORKSPACE / "AGENTS.md",
    WORKSPACE / "USER.md",
]

def search_files(query, max_results=10):
    """Simple keyword search across workspace files"""
    terms = query.lower().split()
    results = []

    for label, dir_path, glob_pattern in SEARCH_DIRS:
        if not dir_path.exists():
            continue
        for f in dir_path.glob(glob_pattern):
            try:
                content = f.read_text(errors='ignore')
                lower = content.lower()
                score = sum(lower.count(t) for t in terms)
                if score > 0:
                    # Extract best matching snippet
                    snippet = extract_snippet(content, terms)
                    results.append({
                        "file": str(f.relative_to(WORKSPACE)),
                        "source": label,
                        "score": score,
                        "size_kb": f.stat().st_size / 1024,
                        "snippet": snippet
                    })
            except Exception:
                continue

    # Also search core files
    for f in CORE_FILES:
        if f.exists():
            try:
                content = f.read_text(errors='ignore')
                lower = content.lower()
                score = sum(lower.count(t) for t in terms)
                if score > 0:
                    snippet = extract_snippet(content, terms)
                    results.append({
                        "file": f.name,
                        "source": "core",
                        "score": score,
                        "size_kb": f.stat().st_size / 1024,
                        "snippet": snippet
                    })
            except Exception:
                continue

    results.sort(key=lambda r: r['score'], reverse=True)
    return results[:max_results]

def extract_snippet(content, terms, context_chars=200):
    """Extract the best matching snippet from content"""
    lower = content.lower()
    best_pos = -1
    best_score = 0

    for term in terms:
        pos = lower.find(term)
        while pos != -1:
            # Score based on term density around this position
            window = lower[max(0, pos-100):pos+100]
            score = sum(window.count(t) for t in terms)
            if score > best_score:
                best_score = score
                best_pos = pos
            pos = lower.find(term, pos + 1)

    if best_pos == -1:
        return content[:context_chars].strip()

    start = max(0, best_pos - context_chars // 2)
    end = min(len(content), best_pos + context_chars // 2)
    snippet = content[start:end].strip()
    if start > 0:
        snippet = "..." + snippet
    if end < len(content):
        snippet = snippet + "..."
    return snippet

def retrieve(args):
    """Search and display results"""
    results = search_files(args.query)
    if not results:
        print(f"No results for: {args.query}")
        return

    print(f"Found {len(results)} results for: {args.query}\n")
    for i, r in enumerate(results, 1):
        print(f"{i}. [{r['source']}] {r['file']} (score: {r['score']}, {r['size_kb']:.1f}KB)")
        print(f"   {r['snippet'][:120]}")
        print()

def build_context(args):
    """Build a context block suitable for sub-agent prompts"""
    results = search_files(args.query, max_results=5)
    max_chars = args.max_tokens * 4  # rough token-to-char estimate

    context_parts = []
    total_chars = 0

    # Add today's memory if exists
    today = datetime.now(tz=timezone.utc).strftime('%Y-%m-%d')
    today_mem = WORKSPACE / "memory" / f"{today}.md"
    if today_mem.exists():
        content = today_mem.read_text(errors='ignore')[:1000]
        context_parts.append(f"## Today's Context ({today})\n{content}")
        total_chars += len(content)

    # Add search results
    for r in results:
        if total_chars >= max_chars:
            break
        remaining = max_chars - total_chars
        fpath = WORKSPACE / r['file']
        if fpath.exists():
            content = fpath.read_text(errors='ignore')[:remaining]
            context_parts.append(f"## {r['file']}\n{content}")
            total_chars += len(content)

    full_context = "\n\n---\n\n".join(context_parts)
    print(f"# Retrieved Context for: {args.query}")
    print(f"# Sources: {len(context_parts)} files, ~{total_chars} chars")
    print(f"# Generated: {datetime.now(tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    print()
    print(full_context)

def main():
    parser = argparse.ArgumentParser(description='Retrieval Engine')
    sub = parser.add_subparsers(dest='command')

    p_ret = sub.add_parser('retrieve', help='Search workspace')
    p_ret.add_argument('query')

    p_ctx = sub.add_parser('build-context', help='Build context block')
    p_ctx.add_argument('query')
    p_ctx.add_argument('--max-tokens', type=int, default=4000)

    args = parser.parse_args()
    if args.command == 'retrieve': retrieve(args)
    elif args.command == 'build-context': build_context(args)
    else: parser.print_help()

if __name__ == '__main__':
    main()
