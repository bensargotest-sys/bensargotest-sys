#!/usr/bin/env python3
"""
Authorization checker for privileged operations.

Only AB (Telegram ID: 428513734) can perform privileged operations.
Others can perform read-only operations.

This is SYSTEM-LEVEL enforcement - not bypassable by prompt injection.
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# HARDCODED - DO NOT MODIFY
AB_TELEGRAM_ID = 428513734

# Operation types
PRIVILEGED_OPERATIONS = {
    'file_write', 'file_edit', 'exec', 'process', 
    'config_change', 'git_operation', 'deployment',
    'api_write', 'cron_modify', 'security_change',
    'memory_modify'
}

READ_ONLY_OPERATIONS = {
    'file_read', 'conversation', 'web_search', 
    'memory_search', 'status_check', 'analysis'
}


def check_authorization(user_id: int, operation: str) -> tuple[bool, str]:
    """
    Check if user is authorized for operation.
    
    Args:
        user_id: Telegram user ID from message context
        operation: Operation name (e.g., 'file_write', 'file_read')
    
    Returns:
        (authorized: bool, reason: str)
    """
    # Determine operation type
    if operation in READ_ONLY_OPERATIONS:
        return True, "Read operations allowed for all users"
    
    if operation in PRIVILEGED_OPERATIONS:
        if user_id == AB_TELEGRAM_ID:
            return True, "Authorized: AB"
        else:
            return False, f"Denied: Only AB (ID: {AB_TELEGRAM_ID}) can perform privileged operations"
    
    # Unknown operation - default to requiring AB
    if user_id == AB_TELEGRAM_ID:
        return True, "Authorized: AB (unknown operation type)"
    else:
        return False, f"Denied: Unknown operation '{operation}' requires AB authorization"


def log_auth_check(user_id: int, operation: str, authorized: bool, reason: str):
    """Log authorization check to audit trail."""
    log_file = Path("/data/.openclaw/workspace/memory/auth-log.jsonl")
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "user_id": user_id,
        "operation": operation,
        "authorized": authorized,
        "reason": reason
    }
    
    with open(log_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')


def require_ab(user_id: int, operation: str) -> bool:
    """
    Require AB authorization for operation.
    Logs the check and returns True if authorized.
    
    Usage:
        if not require_ab(user_id, 'file_write'):
            print("❌ Unauthorized: Only AB can write files")
            return
    
    Args:
        user_id: Telegram user ID
        operation: Operation name
    
    Returns:
        True if authorized, False if denied
    """
    authorized, reason = check_authorization(user_id, operation)
    log_auth_check(user_id, operation, authorized, reason)
    return authorized


def get_unauthorized_message() -> str:
    """Get the standard unauthorized message."""
    return """❌ Unauthorized: Only AB can perform this operation.

You can:
✅ Ask questions
✅ Read files
✅ Get information
✅ Request analysis

For privileged operations (file changes, deployments, etc.), please ask AB to execute them."""


def main():
    """CLI interface for testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Check authorization for operations')
    parser.add_argument('--user-id', type=int, required=True, help='Telegram user ID')
    parser.add_argument('--operation', required=True, help='Operation name')
    parser.add_argument('--quiet', action='store_true', help='Only output result (authorized/denied)')
    
    args = parser.parse_args()
    
    authorized, reason = check_authorization(args.user_id, args.operation)
    log_auth_check(args.user_id, args.operation, authorized, reason)
    
    if args.quiet:
        print("authorized" if authorized else "denied")
    else:
        status = "✅ AUTHORIZED" if authorized else "❌ DENIED"
        print(f"{status}: {reason}")
    
    sys.exit(0 if authorized else 1)


if __name__ == '__main__':
    main()
