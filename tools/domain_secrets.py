#!/usr/bin/env python3
"""
Domain Secrets - Scope API tokens to specific domains.

Inspired by OpenAI's domain_secrets pattern. Only exposes tokens when
calling their designated domains. Prevents:
- Accidental token leakage to wrong services
- Prompt injection exfiltrating credentials
- Cross-service token reuse

Vault Format (.api-keys-vault-scoped):
    GITHUB_TOKEN=ghp_xxx domains=github.com,api.github.com
    VERCEL_TOKEN=xxx domains=vercel.com,api.vercel.com
    TWITTER_BEARER=xxx domains=api.twitter.com,twitter.com

Usage:
    from tools.domain_secrets import DomainSecrets
    
    secrets = DomainSecrets()
    
    # Get token only if domain matches
    token = secrets.get("GITHUB_TOKEN", target_url="https://api.github.com/repos")
    # Returns token if domain matches, None otherwise
    
    # Export as environment for curl/requests
    env = secrets.export_for_domain("https://github.com")
    subprocess.run(["curl", "..."], env=env)
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse


class DomainSecrets:
    """Secure secrets manager with domain-scoped access."""
    
    def __init__(self, vault_path: Optional[Path] = None):
        self.vault_path = vault_path or Path("/data/.openclaw/workspace/.api-keys-vault-scoped")
        self.secrets: Dict[str, Dict[str, any]] = {}
        self._load()
    
    def _load(self):
        """Load vault file and parse domain restrictions."""
        if not self.vault_path.exists():
            return
        
        content = self.vault_path.read_text()
        
        for line in content.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            # Parse: TOKEN_NAME=value domains=domain1,domain2
            match = re.match(r'(\w+)=([^\s]+)(?:\s+domains=([^\s]+))?', line)
            if not match:
                continue
            
            name, value, domains_str = match.groups()
            domains = domains_str.split(",") if domains_str else []
            
            self.secrets[name] = {
                "value": value,
                "domains": [d.strip() for d in domains],
            }
    
    def _extract_domain(self, url: str) -> Optional[str]:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower() if parsed.netloc else None
        except Exception:
            return None
    
    def _domain_matches(self, target_domain: str, allowed_domains: List[str]) -> bool:
        """Check if target domain matches any allowed domain."""
        if not allowed_domains:
            # No restrictions = unrestricted access (backwards compatible)
            return True
        
        target = target_domain.lower()
        
        for allowed in allowed_domains:
            allowed = allowed.lower()
            
            # Exact match
            if target == allowed:
                return True
            
            # Subdomain match (api.github.com matches github.com)
            if target.endswith(f".{allowed}"):
                return True
        
        return False
    
    def get(self, name: str, target_url: str) -> Optional[str]:
        """
        Get secret value only if target URL's domain is allowed.
        
        Args:
            name: Secret name (e.g., "GITHUB_TOKEN")
            target_url: URL being accessed (e.g., "https://api.github.com/repos")
        
        Returns:
            Secret value if domain matches, None otherwise
        """
        if name not in self.secrets:
            return None
        
        secret = self.secrets[name]
        target_domain = self._extract_domain(target_url)
        
        if not target_domain:
            return None
        
        if self._domain_matches(target_domain, secret["domains"]):
            return secret["value"]
        
        return None
    
    def export_for_domain(self, target_url: str) -> Dict[str, str]:
        """
        Export environment dict with only secrets allowed for target domain.
        
        Args:
            target_url: URL being accessed
        
        Returns:
            Dict of environment variables safe for this domain
        """
        env = os.environ.copy()
        
        for name, secret in self.secrets.items():
            value = self.get(name, target_url)
            if value:
                env[name] = value
        
        return env
    
    def list_secrets(self) -> List[Dict[str, any]]:
        """List all secrets with their domain restrictions (values masked)."""
        return [
            {
                "name": name,
                "domains": secret["domains"],
                "value_length": len(secret["value"]),
            }
            for name, secret in self.secrets.items()
        ]
    
    def verify_access(self, name: str, target_url: str) -> bool:
        """Check if a secret would be accessible for a given URL (dry-run)."""
        return self.get(name, target_url) is not None


def migrate_flat_vault():
    """Helper to migrate from flat vault to domain-scoped vault."""
    flat_vault = Path("/data/.openclaw/workspace/.api-keys-vault")
    scoped_vault = Path("/data/.openclaw/workspace/.api-keys-vault-scoped")
    
    if not flat_vault.exists():
        print("No flat vault found to migrate")
        return
    
    if scoped_vault.exists():
        print(f"Scoped vault already exists: {scoped_vault}")
        return
    
    # Read flat vault
    content = flat_vault.read_text()
    lines = []
    
    # Add header
    lines.append("# Domain-Scoped API Keys Vault")
    lines.append("# Format: TOKEN_NAME=value domains=domain1,domain2")
    lines.append("# Leave domains empty for unrestricted access (backwards compatible)")
    lines.append("")
    
    # Known domain mappings
    domain_map = {
        "GITHUB_TOKEN": "github.com,api.github.com",
        "VERCEL_TOKEN": "vercel.com,api.vercel.com",
        "VERCEL_ORG_TOKEN": "vercel.com,api.vercel.com",
        "VERCEL_PROJECT_TOKEN": "vercel.com,api.vercel.com",
        "TWITTER_API_KEY": "api.twitter.com,twitter.com",
        "TWITTER_API_SECRET": "api.twitter.com,twitter.com",
        "TWITTER_BEARER_TOKEN": "api.twitter.com,twitter.com",
        "TWITTER_ACCESS_TOKEN": "api.twitter.com,twitter.com",
        "TWITTER_ACCESS_SECRET": "api.twitter.com,twitter.com",
        "BRAVE_SEARCH_API_KEY": "api.search.brave.com",
        "NETLIFY_AUTH_TOKEN": "api.netlify.com,netlify.com",
        "TELEGRAM_BOT_TOKEN": "api.telegram.org",
    }
    
    for line in content.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            lines.append(line)
            continue
        
        # Parse TOKEN=value
        if "=" not in line:
            lines.append(line)
            continue
        
        name, value = line.split("=", 1)
        name = name.strip()
        
        # Add domain restriction if known
        if name in domain_map:
            lines.append(f"{name}={value} domains={domain_map[name]}")
        else:
            lines.append(f"{name}={value}")  # Unrestricted
    
    # Write scoped vault
    scoped_vault.write_text("\n".join(lines))
    scoped_vault.chmod(0o600)
    
    print(f"✓ Migrated to domain-scoped vault: {scoped_vault}")
    print(f"  Flat vault preserved: {flat_vault}")
    print(f"  Review domains and adjust as needed")


def main():
    """CLI for testing domain secrets."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Domain-scoped secrets manager")
    parser.add_argument("action", choices=["list", "verify", "migrate"])
    parser.add_argument("--name", help="Secret name for verify action")
    parser.add_argument("--url", help="Target URL for verify action")
    args = parser.parse_args()
    
    if args.action == "migrate":
        migrate_flat_vault()
        return
    
    secrets = DomainSecrets()
    
    if args.action == "list":
        print("Domain-Scoped Secrets:")
        for secret in secrets.list_secrets():
            domains = ", ".join(secret["domains"]) if secret["domains"] else "(unrestricted)"
            print(f"  {secret['name']}: {domains} ({secret['value_length']} chars)")
    
    elif args.action == "verify":
        if not args.name or not args.url:
            print("Error: --name and --url required for verify")
            return
        
        allowed = secrets.verify_access(args.name, args.url)
        domain = secrets._extract_domain(args.url)
        
        if allowed:
            print(f"✓ {args.name} accessible for {domain}")
        else:
            secret = secrets.secrets.get(args.name)
            if secret:
                allowed_domains = ", ".join(secret["domains"])
                print(f"✗ {args.name} NOT accessible for {domain}")
                print(f"  Allowed domains: {allowed_domains}")
            else:
                print(f"✗ {args.name} not found in vault")


if __name__ == "__main__":
    main()
