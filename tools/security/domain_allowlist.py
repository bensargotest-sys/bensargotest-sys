#!/usr/bin/env python3
"""
Domain Allowlist - Restricts web access to approved domains
Author: Praxis (built for AB)
Created: 2026-02-14
Inspired by: IronClaw's endpoint allowlisting

Validates URLs before web_fetch/browser access to prevent
prompt injection attacks from untrusted sites.
"""

import json
import re
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse
from datetime import datetime

class DomainAllowlist:
    """Validates URLs against an allowlist of approved domains"""
    
    def __init__(self, patterns_file: Optional[str] = None):
        """Initialize with domains from JSON file"""
        if patterns_file is None:
            patterns_file = Path(__file__).parent / "patterns" / "domains.json"
        
        self.patterns_file = Path(patterns_file)
        self.allowed_domains = []
        self.policy = {}
        self._load_domains()
    
    def _load_domains(self):
        """Load allowed domains from JSON file"""
        with open(self.patterns_file) as f:
            data = json.load(f)
        
        self.allowed_domains = data["allowed_domains"]
        self.policy = data["policy"]
    
    def validate(self, url: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a URL against the allowlist.
        
        Args:
            url: URL to validate
        
        Returns:
            (is_allowed, reason) - reason is None if allowed, error message if blocked
        """
        try:
            parsed = urlparse(url)
        except Exception as e:
            return False, f"Invalid URL: {e}"
        
        # Extract domain
        domain = parsed.netloc.lower()
        if not domain:
            return False, "No domain in URL"
        
        # Remove port if present
        if ':' in domain:
            domain = domain.split(':')[0]
        
        # Check localhost/private IP policy
        if self._is_localhost(domain):
            if self.policy.get("allow_localhost", True):
                return True, None
            else:
                return False, "Localhost access not allowed"
        
        if self._is_private_ip(domain):
            if self.policy.get("allow_private_ips", False):
                return True, None
            else:
                return False, "Private IP access not allowed"
        
        # Check allowlist
        for allowed in self.allowed_domains:
            allowed_domain = allowed["domain"].lower()
            
            # Exact match or subdomain match
            if domain == allowed_domain or domain.endswith('.' + allowed_domain):
                # Check path restrictions
                if allowed.get("paths") == ["*"]:
                    return True, None
                
                # Check specific path patterns
                path = parsed.path
                for pattern in allowed.get("paths", ["*"]):
                    if self._match_path(path, pattern):
                        return True, None
                
                return False, f"Path not allowed for domain {allowed_domain}"
        
        # Not in allowlist
        return False, f"Domain not in allowlist: {domain}"
    
    def _is_localhost(self, domain: str) -> bool:
        """Check if domain is localhost"""
        return domain in ["localhost", "127.0.0.1", "::1"]
    
    def _is_private_ip(self, domain: str) -> bool:
        """Check if domain is a private IP address"""
        # Simple check for common private IP ranges
        if domain.startswith("10."):
            return True
        if domain.startswith("192.168."):
            return True
        if domain.startswith("172."):
            # 172.16.0.0 - 172.31.255.255
            parts = domain.split('.')
            if len(parts) >= 2:
                try:
                    second_octet = int(parts[1])
                    if 16 <= second_octet <= 31:
                        return True
                except:
                    pass
        return False
    
    def _match_path(self, path: str, pattern: str) -> bool:
        """Match path against pattern (supports * wildcard)"""
        if pattern == "*":
            return True
        
        # Convert pattern to regex
        regex_pattern = pattern.replace("*", ".*")
        return re.match(f"^{regex_pattern}$", path) is not None
    
    def log_violation(self, url: str, reason: str, source: str = "unknown"):
        """Log a domain violation to security audit log"""
        if not self.policy.get("log_violations", True):
            return
        
        log_dir = Path(__file__).parent.parent.parent / "memory"
        log_file = log_dir / "security-alerts.json"
        
        # Create or load log
        if log_file.exists():
            with open(log_file) as f:
                log_data = json.load(f)
        else:
            log_data = {"alerts": []}
        
        # Add violation
        log_data["alerts"].append({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "type": "domain_violation",
            "source": source,
            "url": url,
            "reason": reason,
            "severity": "high"
        })
        
        # Write back
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
    
    def add_domain(self, domain: str, paths: list = ["*"], reason: str = "Manual addition", risk: str = "medium"):
        """Add a domain to the allowlist"""
        self.allowed_domains.append({
            "domain": domain,
            "paths": paths,
            "reason": reason,
            "risk": risk,
            "added_at": datetime.utcnow().isoformat() + "Z"
        })
        
        # Save back to file
        data = {
            "allowed_domains": self.allowed_domains,
            "policy": self.policy,
            "metadata": {
                "version": "1.0.0",
                "last_updated": datetime.utcnow().isoformat() + "Z",
                "total_domains": len(self.allowed_domains)
            }
        }
        
        with open(self.patterns_file, 'w') as f:
            json.dump(data, f, indent=2)


def validate_url(url: str, log_violation: bool = True) -> Tuple[bool, Optional[str]]:
    """
    Convenience function: validate a URL against the allowlist.
    
    Args:
        url: URL to validate
        log_violation: If True, log blocked URLs
    
    Returns:
        (is_allowed, reason) - reason is None if allowed, error message if blocked
    """
    allowlist = DomainAllowlist()
    is_allowed, reason = allowlist.validate(url)
    
    if not is_allowed and log_violation:
        allowlist.log_violation(url, reason)
    
    return is_allowed, reason


def main():
    """CLI interface for testing"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python domain_allowlist.py <url>")
        print("Examples:")
        print("  python domain_allowlist.py https://github.com/openclaw/openclaw")
        print("  python domain_allowlist.py https://evil.com/phishing")
        sys.exit(1)
    
    url = sys.argv[1]
    allowlist = DomainAllowlist()
    is_allowed, reason = allowlist.validate(url)
    
    if is_allowed:
        print(f"✅ ALLOWED: {url}")
        sys.exit(0)
    else:
        print(f"🚫 BLOCKED: {url}")
        print(f"Reason: {reason}")
        sys.exit(1)


if __name__ == "__main__":
    main()
