#!/usr/bin/env python3
"""
Brave LLM Context API - Pre-extracted web content optimized for AI agents.

Launched: 2026-02-06
Best general-purpose search for agents in February 2026.

Features:
- Independent index (not Google/Bing)
- LLM-optimized chunks (not raw HTML)
- Clean pricing (no hidden costs)
- Zero-data retention (privacy)
- MCP server ready (agent-native)
- Token budget control
- Relevance filtering

Usage:
    python3 tools/brave_llm_context.py "your query here"
    python3 tools/brave_llm_context.py "best practices for React hooks" --max-tokens 4096
    python3 tools/brave_llm_context.py "coffee shops near me" --city "San Francisco" --state "CA"
"""

import os
import sys
import json
import requests
import argparse
from typing import Optional, Dict, Any, List

# API Configuration
API_BASE = "https://api.search.brave.com/res/v1/llm/context"
API_KEY = os.getenv("BRAVE_API_KEY")

# Load from vault if not in environment
if not API_KEY:
    vault_path = "/data/.openclaw/workspace/.api-keys-vault"
    if os.path.exists(vault_path):
        with open(vault_path) as f:
            for line in f:
                if line.startswith("BRAVE_API_KEY="):
                    API_KEY = line.split("=", 1)[1].strip().strip('"')
                    break

def search_llm_context(
    query: str,
    count: int = 20,
    max_tokens: int = 8192,
    max_urls: int = 20,
    max_snippets: int = 50,
    max_tokens_per_url: int = 4096,
    threshold_mode: str = "balanced",
    country: str = "us",
    search_lang: str = "en",
    enable_local: Optional[bool] = None,
    location: Optional[Dict[str, str]] = None,
    goggles: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Query Brave LLM Context API for pre-extracted, LLM-optimized content.
    
    Args:
        query: Search query (1-400 chars, max 50 words)
        count: Maximum search results to consider (1-50)
        max_tokens: Approximate maximum tokens in response (1024-32768)
        max_urls: Maximum URLs in response (1-50)
        max_snippets: Maximum snippets across all URLs (1-100)
        max_tokens_per_url: Maximum tokens per URL (512-8192)
        threshold_mode: Relevance threshold (strict/balanced/lenient/disabled)
        country: 2-char country code
        search_lang: 2+ char language code
        enable_local: Enable local recall (true/false/null for auto)
        location: Dict with lat, long, city, state, country, postal_code
        goggles: Goggle URL or inline definition for custom ranking
    
    Returns:
        Dict with grounding (generic/poi/map) and sources metadata
    """
    if not API_KEY:
        raise ValueError("BRAVE_API_KEY not found in environment or vault")
    
    # Build query parameters
    params = {
        "q": query,
        "count": count,
        "maximum_number_of_tokens": max_tokens,
        "maximum_number_of_urls": max_urls,
        "maximum_number_of_snippets": max_snippets,
        "maximum_number_of_tokens_per_url": max_tokens_per_url,
        "context_threshold_mode": threshold_mode,
        "country": country,
        "search_lang": search_lang,
    }
    
    if enable_local is not None:
        params["enable_local"] = str(enable_local).lower()
    
    if goggles:
        params["goggles"] = goggles
    
    # Build headers
    headers = {
        "X-Subscription-Token": API_KEY,
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
    }
    
    # Add location headers if provided
    if location:
        if "lat" in location:
            headers["X-Loc-Lat"] = str(location["lat"])
        if "long" in location:
            headers["X-Loc-Long"] = str(location["long"])
        if "city" in location:
            headers["X-Loc-City"] = location["city"]
        if "state" in location:
            headers["X-Loc-State"] = location["state"]
        if "country" in location:
            headers["X-Loc-Country"] = location["country"]
        if "postal_code" in location:
            headers["X-Loc-Postal-Code"] = location["postal_code"]
    
    # Make request (GET for simple, POST for complex queries)
    if len(query) < 200:
        response = requests.get(API_BASE, params=params, headers=headers, timeout=30)
    else:
        headers["Content-Type"] = "application/json"
        response = requests.post(API_BASE, json=params, headers=headers, timeout=30)
    
    response.raise_for_status()
    return response.json()


def format_context_for_llm(data: Dict[str, Any]) -> str:
    """
    Format LLM Context API response for direct LLM consumption.
    
    Returns markdown-formatted text with sources and snippets.
    """
    output = []
    
    grounding = data.get("grounding", {})
    sources = data.get("sources", {})
    
    # Generic web results
    generic = grounding.get("generic", [])
    if generic:
        output.append("## Web Search Results\n")
        for item in generic:
            url = item.get("url", "")
            title = item.get("title", "Untitled")
            snippets = item.get("snippets", [])
            
            output.append(f"### [{title}]({url})\n")
            for snippet in snippets:
                output.append(f"{snippet}\n")
            output.append("")
    
    # POI (Point of Interest) results
    poi = grounding.get("poi")
    if poi:
        output.append("## Point of Interest\n")
        output.append(f"**{poi.get('name', 'Unknown')}**\n")
        output.append(f"URL: {poi.get('url', '')}\n")
        for snippet in poi.get("snippets", []):
            output.append(f"{snippet}\n")
        output.append("")
    
    # Map/place results
    map_results = grounding.get("map", [])
    if map_results:
        output.append("## Local Places\n")
        for place in map_results:
            output.append(f"### {place.get('name', 'Unknown')}\n")
            output.append(f"URL: {place.get('url', '')}\n")
            for snippet in place.get("snippets", []):
                output.append(f"{snippet}\n")
            output.append("")
    
    # Sources metadata
    if sources:
        output.append("## Sources\n")
        for url, meta in sources.items():
            hostname = meta.get("hostname", "unknown")
            age = meta.get("age")
            age_str = age[2] if age and len(age) > 2 else "unknown age"
            output.append(f"- [{hostname}]({url}) ({age_str})\n")
    
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="Brave LLM Context API - Agent-optimized web search")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--count", type=int, default=20, help="Max results to consider (1-50)")
    parser.add_argument("--max-tokens", type=int, default=8192, help="Max tokens in response (1024-32768)")
    parser.add_argument("--max-urls", type=int, default=20, help="Max URLs in response (1-50)")
    parser.add_argument("--threshold", default="balanced", choices=["strict", "balanced", "lenient", "disabled"])
    parser.add_argument("--country", default="us", help="2-char country code")
    parser.add_argument("--lang", default="en", help="2+ char language code")
    parser.add_argument("--city", help="City name for local search")
    parser.add_argument("--state", help="State/region code for local search")
    parser.add_argument("--lat", type=float, help="Latitude for local search")
    parser.add_argument("--long", type=float, help="Longitude for local search")
    parser.add_argument("--enable-local", choices=["true", "false"], help="Force enable/disable local recall")
    parser.add_argument("--raw", action="store_true", help="Output raw JSON instead of formatted text")
    parser.add_argument("--goggles", help="Goggle URL or inline definition")
    
    args = parser.parse_args()
    
    # Build location dict
    location = None
    if any([args.city, args.state, args.lat, args.long]):
        location = {}
        if args.lat:
            location["lat"] = args.lat
        if args.long:
            location["long"] = args.long
        if args.city:
            location["city"] = args.city
        if args.state:
            location["state"] = args.state
        if args.country:
            location["country"] = args.country
    
    # Convert enable_local string to bool or None
    enable_local = None
    if args.enable_local:
        enable_local = args.enable_local == "true"
    
    try:
        result = search_llm_context(
            query=args.query,
            count=args.count,
            max_tokens=args.max_tokens,
            max_urls=args.max_urls,
            threshold_mode=args.threshold,
            country=args.country,
            search_lang=args.lang,
            enable_local=enable_local,
            location=location,
            goggles=args.goggles,
        )
        
        if args.raw:
            print(json.dumps(result, indent=2))
        else:
            formatted = format_context_for_llm(result)
            print(formatted)
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
