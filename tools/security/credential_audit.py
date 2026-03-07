#!/usr/bin/env python3
"""
Credential Audit System - Tracks which tools access which secrets
Author: Praxis (built for AB)
Created: 2026-02-14
Inspired by: IronClaw's full audit log

Logs all credential access attempts to detect suspicious patterns
and provide accountability for secret usage.
"""

import json
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime
import hashlib

class CredentialAudit:
    """Tracks credential access for security auditing"""
    
    def __init__(self, log_file: Optional[str] = None):
        """Initialize audit system"""
        if log_file is None:
            log_file = Path(__file__).parent.parent.parent / "memory" / "credential-access.json"
        
        self.log_file = Path(log_file)
        self._ensure_log_exists()
    
    def _ensure_log_exists(self):
        """Create log file if it doesn't exist"""
        if not self.log_file.exists():
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_file, 'w') as f:
                json.dump({"accesses": []}, f, indent=2)
    
    def log_access(
        self,
        credential_name: str,
        accessed_by: str,
        purpose: str = "unknown",
        success: bool = True,
        metadata: Optional[Dict] = None
    ):
        """
        Log a credential access attempt.
        
        Args:
            credential_name: Name of the credential (e.g., "GITHUB_TOKEN")
            accessed_by: Tool/script/agent that accessed it
            purpose: Why the credential was accessed
            success: Whether access was granted
            metadata: Additional context
        """
        # Load existing log
        with open(self.log_file) as f:
            log_data = json.load(f)
        
        # Add access record
        record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "credential": credential_name,
            "accessed_by": accessed_by,
            "purpose": purpose,
            "success": success,
            "metadata": metadata or {}
        }
        
        log_data["accesses"].append(record)
        
        # Write back
        with open(self.log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
    
    def get_accesses(
        self,
        credential_name: Optional[str] = None,
        accessed_by: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get credential access records with optional filtering.
        
        Args:
            credential_name: Filter by credential
            accessed_by: Filter by accessor
            limit: Maximum records to return
        
        Returns:
            List of access records
        """
        with open(self.log_file) as f:
            log_data = json.load(f)
        
        accesses = log_data["accesses"]
        
        # Filter
        if credential_name:
            accesses = [a for a in accesses if a["credential"] == credential_name]
        if accessed_by:
            accesses = [a for a in accesses if a["accessed_by"] == accessed_by]
        
        # Return most recent first
        return list(reversed(accesses[-limit:]))
    
    def get_stats(self) -> Dict:
        """Get summary statistics of credential usage"""
        with open(self.log_file) as f:
            log_data = json.load(f)
        
        accesses = log_data["accesses"]
        
        # Count by credential
        by_credential = {}
        by_accessor = {}
        
        for access in accesses:
            cred = access["credential"]
            accessor = access["accessed_by"]
            
            by_credential[cred] = by_credential.get(cred, 0) + 1
            by_accessor[accessor] = by_accessor.get(accessor, 0) + 1
        
        return {
            "total_accesses": len(accesses),
            "unique_credentials": len(by_credential),
            "unique_accessors": len(by_accessor),
            "by_credential": by_credential,
            "by_accessor": by_accessor,
            "last_access": accesses[-1]["timestamp"] if accesses else None
        }
    
    def detect_suspicious_patterns(self) -> List[Dict]:
        """
        Detect suspicious credential access patterns.
        
        Returns:
            List of suspicious patterns found
        """
        with open(self.log_file) as f:
            log_data = json.load(f)
        
        accesses = log_data["accesses"]
        alerts = []
        
        # Pattern 1: High frequency access (>10 accesses in 1 hour)
        recent = [a for a in accesses[-50:]]  # Last 50 accesses
        if len(recent) > 10:
            timestamps = [datetime.fromisoformat(a["timestamp"].replace('Z', '')) for a in recent]
            if timestamps:
                time_span = (timestamps[-1] - timestamps[0]).total_seconds() / 3600
                if time_span < 1:
                    alerts.append({
                        "type": "high_frequency",
                        "severity": "medium",
                        "description": f"{len(recent)} accesses in {time_span:.1f} hours",
                        "credentials": list(set(a["credential"] for a in recent))
                    })
        
        # Pattern 2: Failed access attempts
        failed = [a for a in accesses if not a.get("success", True)]
        if len(failed) > 5:
            alerts.append({
                "type": "failed_access",
                "severity": "high",
                "description": f"{len(failed)} failed access attempts",
                "credentials": list(set(a["credential"] for a in failed))
            })
        
        # Pattern 3: Unusual accessor (not in common tools list)
        common_tools = ["exec", "web_fetch", "browser", "github", "vercel", "deploy"]
        unusual = [a for a in accesses if not any(tool in a["accessed_by"] for tool in common_tools)]
        if len(unusual) > 3:
            alerts.append({
                "type": "unusual_accessor",
                "severity": "low",
                "description": f"{len(unusual)} accesses from unusual tools",
                "accessors": list(set(a["accessed_by"] for a in unusual))
            })
        
        return alerts


# Convenience wrapper for vault access
class AuditedVaultAccess:
    """Wrapper for vault access that logs all reads"""
    
    def __init__(self, vault_path: str = "/data/.openclaw/workspace/.api-keys-vault"):
        self.vault_path = vault_path
        self.audit = CredentialAudit()
    
    def get(self, key_name: str, accessed_by: str, purpose: str = "general") -> Optional[str]:
        """
        Get a credential from the vault with audit logging.
        
        Args:
            key_name: Name of the key (e.g., "GITHUB_TOKEN")
            accessed_by: Tool/script accessing it
            purpose: Why it's being accessed
        
        Returns:
            Credential value or None if not found
        """
        try:
            # Read vault
            with open(self.vault_path) as f:
                content = f.read()
            
            # Extract the specific key (simple bash variable format)
            for line in content.split('\n'):
                if line.startswith(f"{key_name}="):
                    # Remove KEY= and quotes
                    value = line.split('=', 1)[1].strip().strip('"').strip("'")
                    
                    # Log access
                    self.audit.log_access(
                        credential_name=key_name,
                        accessed_by=accessed_by,
                        purpose=purpose,
                        success=True
                    )
                    
                    return value
            
            # Key not found
            self.audit.log_access(
                credential_name=key_name,
                accessed_by=accessed_by,
                purpose=purpose,
                success=False,
                metadata={"error": "Key not found"}
            )
            return None
        
        except Exception as e:
            # Log failed access
            self.audit.log_access(
                credential_name=key_name,
                accessed_by=accessed_by,
                purpose=purpose,
                success=False,
                metadata={"error": str(e)}
            )
            return None


def main():
    """CLI interface for credential audit"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python credential_audit.py <command> [args]")
        print("Commands:")
        print("  log <name> <tool> <purpose>  - Log a credential access")
        print("  list [credential]            - List recent accesses")
        print("  stats                        - Show usage statistics")
        print("  suspicious                   - Check for suspicious patterns")
        sys.exit(1)
    
    command = sys.argv[1]
    audit = CredentialAudit()
    
    if command == "log":
        if len(sys.argv) < 5:
            print("Usage: credential_audit.py log <name> <tool> <purpose>")
            sys.exit(1)
        
        cred_name = sys.argv[2]
        tool = sys.argv[3]
        purpose = sys.argv[4]
        
        audit.log_access(cred_name, tool, purpose)
        print(f"✅ Logged access to {cred_name} by {tool}")
    
    elif command == "list":
        cred_name = sys.argv[2] if len(sys.argv) > 2 else None
        accesses = audit.get_accesses(credential_name=cred_name, limit=20)
        
        print(f"Recent credential accesses (last {len(accesses)}):")
        print()
        for access in accesses:
            print(f"[{access['timestamp']}] {access['credential']}")
            print(f"  Accessed by: {access['accessed_by']}")
            print(f"  Purpose: {access['purpose']}")
            print(f"  Success: {'✅' if access['success'] else '❌'}")
            print()
    
    elif command == "stats":
        stats = audit.get_stats()
        print("Credential Access Statistics")
        print("=" * 60)
        print(f"Total accesses: {stats['total_accesses']}")
        print(f"Unique credentials: {stats['unique_credentials']}")
        print(f"Unique accessors: {stats['unique_accessors']}")
        print(f"Last access: {stats['last_access']}")
        print()
        print("By credential:")
        for cred, count in sorted(stats['by_credential'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {cred}: {count}")
        print()
        print("By accessor:")
        for accessor, count in sorted(stats['by_accessor'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {accessor}: {count}")
    
    elif command == "suspicious":
        patterns = audit.detect_suspicious_patterns()
        
        if not patterns:
            print("✅ No suspicious patterns detected")
        else:
            print(f"🚨 {len(patterns)} suspicious pattern(s) detected:")
            print()
            for pattern in patterns:
                print(f"Type: {pattern['type']}")
                print(f"Severity: {pattern['severity'].upper()}")
                print(f"Description: {pattern['description']}")
                if 'credentials' in pattern:
                    print(f"Credentials: {', '.join(pattern['credentials'])}")
                if 'accessors' in pattern:
                    print(f"Accessors: {', '.join(pattern['accessors'])}")
                print()
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
