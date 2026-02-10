#!/usr/bin/env python3
"""
workspace_search.py - Semantic workspace search

A lightweight alternative to QMD for searching workspace files.
Uses simple keyword matching with ranking.

Usage:
    python3 tools/workspace_search.py "error handling" [--limit 10]
    python3 tools/workspace_search.py "security audit" --type md
    python3 tools/workspace_search.py "checkpoint" --path memory/
"""

import sys
import re
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path("/data/.openclaw/workspace")

# File extensions to search
SEARCHABLE_EXTENSIONS = {
    '.md', '.py', '.sh', '.json', '.txt', '.yml', '.yaml'
}

def search_file(file_path, query_terms):
    """Search a file for query terms and return matches with context"""
    try:
        content = file_path.read_text()
        lines = content.split('\n')
        
        matches = []
        score = 0
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            line_score = 0
            
            for term in query_terms:
                if term in line_lower:
                    line_score += 1
                    score += 1
            
            if line_score > 0:
                # Get context (line before and after)
                context_start = max(0, i - 1)
                context_end = min(len(lines), i + 2)
                context = lines[context_start:context_end]
                
                matches.append({
                    'line_num': i + 1,
                    'line': line.strip(),
                    'context': context,
                    'score': line_score
                })
        
        return {
            'file': str(file_path.relative_to(WORKSPACE)),
            'score': score,
            'matches': matches
        }
    
    except Exception as e:
        return None

def search_workspace(query, file_type=None, search_path=None, limit=10):
    """Search workspace files"""
    query_terms = [term.lower() for term in query.split()]
    
    search_root = WORKSPACE / search_path if search_path else WORKSPACE
    
    results = []
    
    # Find all searchable files
    for file_path in search_root.rglob('*'):
        if not file_path.is_file():
            continue
        
        # Skip hidden files and directories
        if any(part.startswith('.') for part in file_path.parts):
            continue
        
        # Check extension
        if file_path.suffix not in SEARCHABLE_EXTENSIONS:
            continue
        
        # Filter by type if specified
        if file_type and file_path.suffix != f'.{file_type}':
            continue
        
        # Search the file
        result = search_file(file_path, query_terms)
        if result and result['score'] > 0:
            results.append(result)
    
    # Sort by score (highest first)
    results.sort(key=lambda x: x['score'], reverse=True)
    
    return results[:limit]

def format_results(results, verbose=False):
    """Format search results"""
    if not results:
        print("❌ No results found")
        return
    
    print(f"🔍 Found {len(results)} file(s) matching query\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['file']} (score: {result['score']})")
        
        if verbose:
            for match in result['matches'][:3]:  # Show top 3 matches per file
                print(f"   Line {match['line_num']}: {match['line'][:80]}")
        
        print()

def main():
    if len(sys.argv) < 2:
        print("Usage: workspace_search.py <query> [--limit N] [--type ext] [--path dir] [--verbose]")
        sys.exit(1)
    
    query = sys.argv[1]
    limit = 10
    file_type = None
    search_path = None
    verbose = False
    
    # Parse arguments
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg == '--limit' and i + 1 < len(sys.argv):
            limit = int(sys.argv[i + 1])
            i += 2
        elif arg == '--type' and i + 1 < len(sys.argv):
            file_type = sys.argv[i + 1]
            i += 2
        elif arg == '--path' and i + 1 < len(sys.argv):
            search_path = sys.argv[i + 1]
            i += 2
        elif arg == '--verbose':
            verbose = True
            i += 1
        else:
            i += 1
    
    results = search_workspace(query, file_type, search_path, limit)
    format_results(results, verbose)

if __name__ == "__main__":
    main()
