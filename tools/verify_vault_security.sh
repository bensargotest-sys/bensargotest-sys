#!/bin/bash
# Verify API keys vault security
# Created: 2026-02-11 19:37 UTC

set -e

VAULT="/data/.openclaw/workspace/.api-keys-vault"
BACKUP="/data/.openclaw/workspace/backups/.api-keys-vault.backup"
GITIGNORE="/data/.openclaw/workspace/.gitignore"

echo "🔒 API Keys Vault Security Check"
echo "================================="
echo ""

# Check vault exists
if [ -f "$VAULT" ]; then
    echo "✅ Vault exists: $VAULT"
else
    echo "❌ Vault missing: $VAULT"
    exit 1
fi

# Check permissions (should be 600)
PERMS=$(stat -c "%a" "$VAULT")
if [ "$PERMS" = "600" ]; then
    echo "✅ Permissions correct: 600 (owner read/write only)"
else
    echo "⚠️  Permissions incorrect: $PERMS (should be 600)"
    echo "   Fixing..."
    chmod 600 "$VAULT"
    echo "✅ Fixed: chmod 600 $VAULT"
fi

# Check backup exists
if [ -f "$BACKUP" ]; then
    echo "✅ Backup exists: $BACKUP"
    BACKUP_PERMS=$(stat -c "%a" "$BACKUP")
    if [ "$BACKUP_PERMS" = "600" ]; then
        echo "✅ Backup permissions correct: 600"
    else
        echo "⚠️  Backup permissions incorrect: $BACKUP_PERMS"
        chmod 600 "$BACKUP"
        echo "✅ Fixed backup permissions"
    fi
else
    echo "⚠️  Backup missing: $BACKUP"
    echo "   Creating backup..."
    mkdir -p "$(dirname $BACKUP)"
    cp "$VAULT" "$BACKUP"
    chmod 600 "$BACKUP"
    echo "✅ Backup created"
fi

# Check .gitignore
if grep -q ".api-keys-vault" "$GITIGNORE"; then
    echo "✅ Protected by .gitignore"
else
    echo "⚠️  Not in .gitignore"
    echo "   Adding..."
    echo ".api-keys-vault" >> "$GITIGNORE"
    echo ".api-keys-vault.backup" >> "$GITIGNORE"
    echo "✅ Added to .gitignore"
fi

# Check if in git
cd /data/.openclaw/workspace
if git ls-files --error-unmatch "$VAULT" 2>/dev/null; then
    echo "❌ DANGER: Vault is tracked by git!"
    echo "   Run: git rm --cached $VAULT"
    exit 1
else
    echo "✅ Not tracked by git"
fi

# Count keys
KEY_COUNT=$(grep -c "^[A-Z_]*=" "$VAULT" || true)
echo ""
echo "📊 Vault Statistics"
echo "-------------------"
echo "Keys stored: $KEY_COUNT"
echo "Vault size: $(du -h "$VAULT" | cut -f1)"
echo "Backup age: $(stat -c "%y" "$BACKUP" | cut -d' ' -f1)"
echo ""
echo "✅ All security checks passed!"
