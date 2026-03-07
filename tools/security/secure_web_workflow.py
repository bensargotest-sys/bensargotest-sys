#!/usr/bin/env python3
"""
Secure Web Workflow - Proper integration with OpenClaw's web_fetch

This is the CORRECT way to use security layers with OpenClaw's web_fetch.
Since we can't modify OpenClaw's TypeScript tools, we post-process their output.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from domain_allowlist import validate_url
from injection_defense import scan_web_content, wrap_for_context
from leak_detector import scan_web_content as scan_leaks

class SecureWebWorkflow:
    """
    Correct workflow for secure web fetching with OpenClaw.
    
    PATTERN:
    1. Validate domain BEFORE calling web_fetch
    2. Call OpenClaw's web_fetch (gets clean extracted content)
    3. Scan content for leaks (sanitize if found)
    4. Scan content for injection (block/sanitize if found)
    5. Wrap content for LLM context
    """
    
    @staticmethod
    def validate_url_safe(url: str) -> tuple[bool, str]:
        """
        Step 1: Validate URL before fetching.
        Call this BEFORE web_fetch.
        
        Returns:
            (is_safe, reason) - If not safe, don't fetch
        """
        is_allowed, reason = validate_url(url)
        return is_allowed, reason
    
    @staticmethod
    def scan_fetched_content(url: str, content: str, wrap: bool = True) -> dict:
        """
        Step 2: Scan content AFTER web_fetch.
        Call this with the result from web_fetch.
        
        Args:
            url: The URL that was fetched
            content: Clean content from web_fetch
            wrap: Whether to wrap with security notices
        
        Returns:
            {
                "safe": bool,
                "content": str,  # Potentially sanitized/wrapped
                "warnings": List[str],
                "actions": List[str]
            }
        """
        warnings = []
        actions = []
        
        # Scan for credential leaks
        safe, sanitized = scan_leaks(url, content, sanitize=True)
        if not safe:
            content = sanitized
            warnings.append("Credentials detected and sanitized")
            actions.append("leak_sanitized")
        
        # Scan for injection attempts
        injection_result = scan_web_content(url, content)
        
        if injection_result.should_block:
            return {
                "safe": False,
                "content": None,
                "warnings": [f"BLOCKED: {[d.pattern_name for d in injection_result.detections]}"],
                "actions": ["injection_blocked"]
            }
        
        if injection_result.sanitized_content:
            content = injection_result.sanitized_content
            warnings.append("Injection patterns sanitized")
            actions.append("injection_sanitized")
        
        if injection_result.warnings:
            warnings.extend(injection_result.warnings)
        
        # Wrap content for LLM
        if wrap:
            content = wrap_for_context(content, source=f"web: {url}")
            actions.append("content_wrapped")
        
        return {
            "safe": True,
            "content": content,
            "warnings": warnings,
            "actions": actions
        }


def secure_web_fetch_workflow_example():
    """
    Example of the correct workflow.
    This is what agents should follow.
    """
    url = "https://example.com/article"
    
    # Step 1: Validate domain BEFORE calling web_fetch
    workflow = SecureWebWorkflow()
    is_safe, reason = workflow.validate_url_safe(url)
    
    if not is_safe:
        print(f"❌ Domain blocked: {reason}")
        return None
    
    # Step 2: Call OpenClaw's web_fetch (via tool system)
    # This is pseudocode - in reality, agent calls web_fetch tool
    # content = web_fetch(url)
    content = "Sample content from web_fetch..."
    
    # Step 3: Scan the fetched content
    result = workflow.scan_fetched_content(url, content)
    
    if not result["safe"]:
        print(f"❌ Security threat: {result['warnings']}")
        return None
    
    if result["warnings"]:
        print(f"⚠️  Warnings: {result['warnings']}")
    
    # Step 4: Use the safe content
    safe_content = result["content"]
    print(f"✅ Safe content ready: {len(safe_content)} chars")
    return safe_content


if __name__ == "__main__":
    secure_web_fetch_workflow_example()
