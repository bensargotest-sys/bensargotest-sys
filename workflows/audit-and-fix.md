# Audit and Fix Workflow

**Pattern:** Closed-loop problem detection and resolution

**Use when:** System health checks, quality audits, automated maintenance

## Overview

This workflow implements a detect → fix → verify cycle for automated problem resolution. Use this pattern for periodic maintenance, security audits, code quality checks, or any task that requires identifying issues and automatically attempting fixes.

## Workflow Steps

### 1. Audit Phase
- Run diagnostic/scan
- Collect findings
- Categorize issues by severity
- Log all findings

### 2. Triage Phase
- Filter for auto-fixable issues
- Prioritize by severity and impact
- Flag issues requiring human intervention
- Create blocked items for manual work

### 3. Fix Phase
- Apply automated fixes
- Log each fix attempt
- Capture errors/failures
- Track what was changed

### 4. Verify Phase
- Re-run audit/checks
- Compare before/after
- Confirm fixes worked
- Document any remaining issues

### 5. Report Phase
- Summary of changes
- Remaining issues
- Recommendations
- Next steps

## Implementation Template

```bash
#!/usr/bin/env bash
# audit-and-fix-example.sh

set -e

WORKSPACE="/data/.openclaw/workspace"
AUDIT_LOG="$WORKSPACE/memory/audit-$(date +%Y%m%d-%H%M%S).log"

echo "=== AUDIT PHASE ===" | tee -a "$AUDIT_LOG"

# Run your audit/scan
# Example: security scan, code lint, dependency check, etc.
audit_output=$(your_audit_command 2>&1)
echo "$audit_output" | tee -a "$AUDIT_LOG"

# Parse findings
critical_count=$(echo "$audit_output" | grep -c "CRITICAL" || true)
high_count=$(echo "$audit_output" | grep -c "HIGH" || true)

echo "Found: $critical_count critical, $high_count high severity issues" | tee -a "$AUDIT_LOG"

echo "=== TRIAGE PHASE ===" | tee -a "$AUDIT_LOG"

# Identify auto-fixable issues
fixable=$(echo "$audit_output" | grep "AUTO_FIX_AVAILABLE" || true)

if [ -z "$fixable" ]; then
    echo "No auto-fixable issues found" | tee -a "$AUDIT_LOG"
    exit 0
fi

echo "=== FIX PHASE ===" | tee -a "$AUDIT_LOG"

# Apply fixes
fix_count=0
while IFS= read -r issue; do
    echo "Fixing: $issue" | tee -a "$AUDIT_LOG"
    
    # Your fix logic here
    if apply_fix "$issue"; then
        echo "  ✓ Fixed" | tee -a "$AUDIT_LOG"
        ((fix_count++))
    else
        echo "  ✗ Failed" | tee -a "$AUDIT_LOG"
        # Log as blocked item
        python3 "$WORKSPACE/tools/blocked_items.py" add \
            "Manual fix needed: $issue" \
            "Auto-fix failed" \
            --category=technical \
            --priority=high
    fi
done <<< "$fixable"

echo "Applied $fix_count fixes" | tee -a "$AUDIT_LOG"

echo "=== VERIFY PHASE ===" | tee -a "$AUDIT_LOG"

# Re-run audit
verify_output=$(your_audit_command 2>&1)
echo "$verify_output" | tee -a "$AUDIT_LOG"

# Compare results
remaining_critical=$(echo "$verify_output" | grep -c "CRITICAL" || true)
remaining_high=$(echo "$verify_output" | grep -c "HIGH" || true)

echo "After fixes: $remaining_critical critical, $remaining_high high" | tee -a "$AUDIT_LOG"

echo "=== REPORT PHASE ===" | tee -a "$AUDIT_LOG"

echo "Summary:" | tee -a "$AUDIT_LOG"
echo "  Issues found: $((critical_count + high_count))" | tee -a "$AUDIT_LOG"
echo "  Auto-fixed: $fix_count" | tee -a "$AUDIT_LOG"
echo "  Remaining: $((remaining_critical + remaining_high))" | tee -a "$AUDIT_LOG"

# Log work
python3 "$WORKSPACE/tools/heartbeat_enforcer.py" log \
    "Audit-and-fix completed: $fix_count fixes applied, $((remaining_critical + remaining_high)) issues remain"

echo "Full log: $AUDIT_LOG"
```

## Python Example

```python
#!/usr/bin/env python3
"""audit_and_fix.py - Generic audit and fix workflow"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

WORKSPACE = Path(__file__).parent.parent

def run_audit():
    """Run audit and return findings"""
    # Your audit logic
    findings = {
        "critical": [],
        "high": [],
        "medium": [],
        "low": []
    }
    
    # Example: check for common issues
    # findings["high"].append("Issue X detected")
    
    return findings

def triage_findings(findings):
    """Separate auto-fixable from manual issues"""
    auto_fix = []
    manual = []
    
    for severity, issues in findings.items():
        for issue in issues:
            if can_auto_fix(issue):
                auto_fix.append((severity, issue))
            else:
                manual.append((severity, issue))
    
    return auto_fix, manual

def can_auto_fix(issue):
    """Determine if issue can be automatically fixed"""
    # Your logic here
    return False

def apply_fix(severity, issue):
    """Apply automated fix"""
    try:
        # Your fix logic
        print(f"  ✓ Fixed: {issue}")
        return True
    except Exception as e:
        print(f"  ✗ Failed: {issue} - {e}")
        return False

def log_blocked_item(severity, issue, error):
    """Log item that couldn't be auto-fixed"""
    priority_map = {
        "critical": "critical",
        "high": "high",
        "medium": "medium",
        "low": "low"
    }
    
    subprocess.run([
        "python3",
        str(WORKSPACE / "tools" / "blocked_items.py"),
        "add",
        f"Manual fix needed: {issue}",
        f"Auto-fix failed: {error}",
        f"--priority={priority_map.get(severity, 'medium')}",
        "--category=technical"
    ])

def main():
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    log_file = WORKSPACE / "memory" / f"audit-{timestamp}.log"
    
    print("=== AUDIT PHASE ===")
    findings = run_audit()
    
    total_issues = sum(len(v) for v in findings.values())
    print(f"Found {total_issues} issues")
    
    print("\n=== TRIAGE PHASE ===")
    auto_fix, manual = triage_findings(findings)
    
    print(f"Auto-fixable: {len(auto_fix)}")
    print(f"Manual: {len(manual)}")
    
    if not auto_fix:
        print("No auto-fixable issues")
        return 0
    
    print("\n=== FIX PHASE ===")
    fixed = 0
    failed = 0
    
    for severity, issue in auto_fix:
        if apply_fix(severity, issue):
            fixed += 1
        else:
            failed += 1
            log_blocked_item(severity, issue, "Fix failed")
    
    print(f"\nFixed: {fixed}, Failed: {failed}")
    
    print("\n=== VERIFY PHASE ===")
    new_findings = run_audit()
    new_total = sum(len(v) for v in new_findings.values())
    
    print(f"Remaining issues: {new_total}")
    
    print("\n=== REPORT PHASE ===")
    print("Summary:")
    print(f"  Initial: {total_issues}")
    print(f"  Fixed: {fixed}")
    print(f"  Failed: {failed}")
    print(f"  Remaining: {new_total}")
    
    # Log work
    subprocess.run([
        "python3",
        str(WORKSPACE / "tools" / "heartbeat_enforcer.py"),
        "log",
        f"Audit-and-fix: {fixed} fixes, {new_total} issues remain"
    ])
    
    return 0 if new_total == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
```

## Use Cases

### Security Audit
```bash
# Scan for vulnerabilities, auto-patch where possible
bash workflows/security-audit-fix.sh
```

### Code Quality
```bash
# Run linter, auto-fix formatting/style issues
bash workflows/code-quality-fix.sh
```

### Dependency Updates
```bash
# Check for outdated deps, update non-breaking
bash workflows/dependency-update.sh
```

### System Health
```bash
# Check disk/memory/services, clean up as needed
python3 workflows/system-health-fix.py
```

## Integration with Heartbeats

Add to HEARTBEAT.md rotation:

```markdown
**Every 5th heartbeat:**
- Run audit-and-fix on workspace
- Clean up old logs
- Update documentation
```

## Best Practices

1. **Always verify** - Never assume fix worked, re-run audit
2. **Log everything** - Fixes, failures, blockers
3. **Human in the loop** - Block critical issues for review
4. **Idempotent** - Safe to run multiple times
5. **Rollback ready** - Keep backups before applying fixes
6. **Rate limit** - Don't spam fix attempts, back off on failure

## Related Tools

- `blocked_items.py` - Track manual intervention needed
- `mistake_logger.py` - Learn from failed fixes
- `heartbeat_enforcer.py` - Log completed audits
- `checkpoint.py` - Backup before risky fixes

## Example Output

```
=== AUDIT PHASE ===
Found 12 issues (2 critical, 4 high, 6 medium)

=== TRIAGE PHASE ===
Auto-fixable: 8
Manual: 4 (logged as blocked items)

=== FIX PHASE ===
  ✓ Fixed: Outdated dependency X
  ✓ Fixed: Insecure permission on file Y
  ✗ Failed: Complex config issue Z (logged)

=== VERIFY PHASE ===
Remaining: 5 issues (1 critical, 1 high, 3 medium)

=== REPORT PHASE ===
Summary:
  Initial: 12
  Fixed: 7
  Failed: 1
  Remaining: 5

Next steps: Review 4 blocked items requiring manual intervention
```

---

**Pattern Status:** Stable  
**Last Updated:** 2026-02-10  
**Maintainer:** Main agent
