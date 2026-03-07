#!/usr/bin/env python3
"""
Secure Wrappers - Safe alternatives to OpenClaw native tools
Author: Praxis (built for AB)
Created: 2026-02-14

These wrappers add security layers to tool operations.
Use these instead of direct tool calls for security-critical operations.
"""

import subprocess
import sys
from pathlib import Path
from typing import Tuple, Dict, Optional

# Import security layers
sys.path.insert(0, str(Path(__file__).parent))
from leak_detector import scan_command_output, scan_web_content as scan_leaks
from domain_allowlist import validate_url
from injection_defense import scan_web_content as scan_injection, wrap_for_context

class SecureCommandError(Exception):
    """Raised when command fails security checks"""
    pass

class SecureDomainError(Exception):
    """Raised when domain is blocked"""
    pass

class SecureInjectionError(Exception):
    """Raised when injection attempt detected"""
    pass


def safe_exec(
    command: str,
    shell: bool = True,
    check_leaks: bool = True,
    sanitize_leaks: bool = True,
    timeout: int = 30
) -> Tuple[int, str, str]:
    """
    Execute command with credential leak scanning.
    
    Args:
        command: Command to execute
        shell: Run in shell (default True)
        check_leaks: Scan output for credential leaks
        sanitize_leaks: Sanitize detected credentials
        timeout: Command timeout in seconds
    
    Returns:
        (returncode, stdout, stderr) - output is sanitized if leaks found
    
    Raises:
        SecureCommandError: If security check fails
    """
    try:
        # Execute command
        result = subprocess.run(
            command,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        stdout = result.stdout
        stderr = result.stderr
        
        if check_leaks:
            # Scan stdout for leaks
            if stdout:
                safe, stdout = scan_command_output(command, stdout, sanitize=sanitize_leaks)
                if not safe and not sanitize_leaks:
                    raise SecureCommandError(f"Credential leak detected in command output: {command}")
            
            # Scan stderr for leaks
            if stderr:
                safe, stderr = scan_command_output(command, stderr, sanitize=sanitize_leaks)
                if not safe and not sanitize_leaks:
                    raise SecureCommandError(f"Credential leak detected in command errors: {command}")
        
        return result.returncode, stdout, stderr
    
    except subprocess.TimeoutExpired:
        raise SecureCommandError(f"Command timed out after {timeout}s: {command}")
    except Exception as e:
        raise SecureCommandError(f"Command execution failed: {e}")


def validate_url_before_fetch(url: str) -> tuple:
    """
    Step 1: Validate URL BEFORE calling web_fetch.
    
    USAGE PATTERN:
        is_safe, reason = validate_url_before_fetch(url)
        if not is_safe:
            return {"error": f"Domain blocked: {reason}"}
        
        # Then call OpenClaw's web_fetch tool
        content = web_fetch(url)
        
        # Then scan the content
        result = scan_fetched_content(url, content)
    
    Args:
        url: URL to validate
    
    Returns:
        (is_safe, reason) - If False, don't fetch
    """
    is_allowed, reason = validate_url(url)
    return is_allowed, reason


def scan_fetched_content(
    url: str,
    content: str,
    check_leaks: bool = True,
    check_injection: bool = True,
    wrap_content: bool = True
) -> Dict:
    """
    Step 2: Scan content AFTER calling web_fetch.
    
    USAGE PATTERN:
        # After web_fetch returns content
        content = web_fetch(url)
        
        # Scan it for security issues
        result = scan_fetched_content(url, content)
        
        if not result["safe"]:
            return {"error": result["warnings"]}
        
        # Use the safe content
        safe_content = result["content"]
    
    Args:
        url: URL that was fetched
        content: Clean content from web_fetch
        check_leaks: Scan for credential leaks
        check_injection: Scan for injection attempts
        wrap_content: Wrap with security notices
    
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
    if check_leaks:
        safe, sanitized_content = scan_leaks(url, content, sanitize=True)
        if not safe:
            content = sanitized_content
            warnings.append("Credentials detected and sanitized")
            actions.append("leak_sanitized")
    
    # Scan for injection attempts
    if check_injection:
        result = scan_injection(url, content)
        
        if result.should_block:
            return {
                "safe": False,
                "content": None,
                "warnings": [f"BLOCKED: {[d.pattern_name for d in result.detections]}"],
                "actions": ["injection_blocked"]
            }
        
        if result.sanitized_content:
            content = result.sanitized_content
            warnings.append("Injection patterns sanitized")
            actions.append("injection_sanitized")
        
        if result.warnings:
            warnings.extend(result.warnings)
    
    # Wrap content for LLM context
    if wrap_content:
        content = wrap_for_context(content, source=f"web: {url}")
        actions.append("content_wrapped")
    
    return {
        "safe": True,
        "content": content,
        "warnings": warnings,
        "actions": actions
    }


def safe_file_read(
    file_path: str,
    check_leaks: bool = True,
    sanitize_leaks: bool = True
) -> Tuple[str, bool, list]:
    """
    Read file with credential leak scanning.
    
    Args:
        file_path: Path to file
        check_leaks: Scan content for credential leaks
        sanitize_leaks: Sanitize detected credentials
    
    Returns:
        (content, is_safe, warnings) - content is sanitized if leaks found
    """
    warnings = []
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except Exception as e:
        raise SecureCommandError(f"File read failed: {e}")
    
    is_safe = True
    
    if check_leaks:
        from leak_detector import LeakDetector
        detector = LeakDetector()
        result = detector.scan(content, sanitize=sanitize_leaks)
        
        if not result.clean:
            is_safe = False
            warnings.append(f"Found {len(result.detections)} credential(s) in file")
            
            if sanitize_leaks and result.sanitized_text:
                content = result.sanitized_text
                warnings.append("Credentials sanitized")
    
    return content, is_safe, warnings


# Convenience functions for common operations

def exec_safe(command: str) -> str:
    """
    Execute command and return stdout (sanitized).
    Raises exception if command fails or has security issues.
    """
    returncode, stdout, stderr = safe_exec(command)
    if returncode != 0:
        raise SecureCommandError(f"Command failed with code {returncode}: {stderr}")
    return stdout


# Usage examples in docstring
"""
USAGE EXAMPLES:

# Safe command execution
try:
    returncode, stdout, stderr = safe_exec("git config --list")
    print(stdout)  # Credentials automatically sanitized
except SecureCommandError as e:
    print(f"Security error: {e}")

# Safe web fetching (TWO-STEP PATTERN):
try:
    # Step 1: Validate domain BEFORE web_fetch
    is_safe, reason = validate_url_before_fetch(url)
    if not is_safe:
        print(f"Domain blocked: {reason}")
    else:
        # Step 2: Call web_fetch (OpenClaw tool)
        content = web_fetch(url)  # This gets clean extracted content
        
        # Step 3: Scan the content
        result = scan_fetched_content(url, content)
        if result["safe"]:
            safe_content = result["content"]  # Sanitized, wrapped
        else:
            print(f"Security threat: {result['warnings']}")

except SecureCommandError as e:
    print(f"Error: {e}")

# Convenience function for commands
stdout = exec_safe("ls -la")  # Raises on failure
"""

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python secure_wrappers.py <test_exec|test_validate|test_scan|test_file>")
        sys.exit(1)
    
    mode = sys.argv[1]
    
    if mode == "test_exec":
        # Test safe exec
        print("Testing safe_exec...")
        returncode, stdout, stderr = safe_exec("echo 'API_KEY=sk-test-12345'")
        print(f"Output: {stdout}")  # Should be sanitized
    
    elif mode == "test_validate":
        # Test URL validation
        print("Testing validate_url_before_fetch...")
        test_urls = [
            "https://github.com",
            "https://evil-site.com",
            "https://stackoverflow.com"
        ]
        for url in test_urls:
            is_safe, reason = validate_url_before_fetch(url)
            print(f"{url}: {'✅ SAFE' if is_safe else '❌ BLOCKED'} - {reason}")
    
    elif mode == "test_scan":
        # Test content scanning
        print("Testing scan_fetched_content...")
        test_content = "Here is some content with sk-or-v1-abc123 and normal text"
        result = scan_fetched_content("https://example.com", test_content)
        print(f"Safe: {result['safe']}")
        print(f"Warnings: {result['warnings']}")
        print(f"Content preview: {result['content'][:100]}...")
    
    elif mode == "test_file":
        # Test safe file read
        print("Testing safe_file_read...")
        content, is_safe, warnings = safe_file_read(".api-keys-vault")
        print(f"Is safe: {is_safe}")
        print(f"Warnings: {warnings}")
        print(f"Content preview: {content[:100]}...")
    
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)
