#!/usr/bin/env python3
"""
Security Monitor - Daily security log review and alerting
Created: 2026-02-15
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

class SecurityMonitor:
    """Monitor security logs and generate daily reports"""
    
    def __init__(self):
        self.workspace = Path(__file__).parent.parent.parent
        self.alerts_file = self.workspace / "memory" / "security-alerts.json"
        self.audit_file = self.workspace / "memory" / "credential-access.json"
    
    def load_alerts(self, hours=24):
        """Load security alerts from last N hours"""
        if not self.alerts_file.exists():
            return []
        
        with open(self.alerts_file) as f:
            data = json.load(f)
        
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        recent = []
        
        for alert in data.get("alerts", []):
            try:
                alert_time = datetime.fromisoformat(alert["timestamp"].replace("Z", "+00:00"))
                if alert_time > cutoff:
                    recent.append(alert)
            except:
                continue
        
        return recent
    
    def load_credential_access(self, hours=24):
        """Load credential access logs from last N hours"""
        if not self.audit_file.exists():
            return []
        
        with open(self.audit_file) as f:
            data = json.load(f)
        
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        recent = []
        
        for access in data.get("access_log", []):
            try:
                access_time = datetime.fromisoformat(access["timestamp"].replace("Z", "+00:00"))
                if access_time > cutoff:
                    recent.append(access)
            except:
                continue
        
        return recent
    
    def analyze_alerts(self, alerts):
        """Analyze security alerts for patterns"""
        stats = {
            "total": len(alerts),
            "by_type": defaultdict(int),
            "by_severity": defaultdict(int),
            "by_pattern": defaultdict(int),
            "critical_count": 0
        }
        
        for alert in alerts:
            alert_type = alert.get("type", "unknown")
            severity = alert.get("severity", "unknown")
            pattern = alert.get("pattern", "unknown")
            
            stats["by_type"][alert_type] += 1
            stats["by_severity"][severity] += 1
            stats["by_pattern"][pattern] += 1
            
            if severity == "critical":
                stats["critical_count"] += 1
        
        return stats
    
    def analyze_credential_access(self, access_logs):
        """Analyze credential access patterns"""
        stats = {
            "total": len(access_logs),
            "by_credential": defaultdict(int),
            "by_accessor": defaultdict(int),
            "failed_attempts": 0,
            "unique_credentials": set(),
            "unique_accessors": set()
        }
        
        for access in access_logs:
            cred = access.get("credential_name", "unknown")
            accessor = access.get("accessed_by", "unknown")
            success = access.get("success", True)
            
            stats["by_credential"][cred] += 1
            stats["by_accessor"][accessor] += 1
            stats["unique_credentials"].add(cred)
            stats["unique_accessors"].add(accessor)
            
            if not success:
                stats["failed_attempts"] += 1
        
        return stats
    
    def generate_report(self, hours=24):
        """Generate security report"""
        print("="*60)
        print(f"SECURITY REPORT - Last {hours} hours")
        print(f"Generated: {datetime.utcnow().isoformat()}Z")
        print("="*60)
        print()
        
        # Load data
        alerts = self.load_alerts(hours)
        access_logs = self.load_credential_access(hours)
        
        # Analyze
        alert_stats = self.analyze_alerts(alerts)
        access_stats = self.analyze_credential_access(access_logs)
        
        # Alert summary
        print("## 🚨 Security Alerts")
        print(f"Total alerts: {alert_stats['total']}")
        
        if alert_stats['total'] == 0:
            print("✅ No security alerts detected")
        else:
            print()
            print("By severity:")
            for severity in ["critical", "high", "medium", "low"]:
                count = alert_stats["by_severity"].get(severity, 0)
                if count > 0:
                    icon = "🔴" if severity == "critical" else "🟠" if severity == "high" else "🟡" if severity == "medium" else "⚪"
                    print(f"  {icon} {severity.capitalize()}: {count}")
            
            print()
            print("By type:")
            for alert_type, count in alert_stats["by_type"].items():
                print(f"  - {alert_type}: {count}")
            
            if alert_stats["critical_count"] > 0:
                print()
                print(f"⚠️  WARNING: {alert_stats['critical_count']} CRITICAL alerts!")
                print("Recent critical alerts:")
                for alert in alerts[-5:]:
                    if alert.get("severity") == "critical":
                        print(f"  - {alert.get('pattern', 'unknown')}: {alert.get('context', '')[:50]}...")
        
        print()
        print("-" * 60)
        print()
        
        # Credential access summary
        print("## 🔑 Credential Access")
        print(f"Total accesses: {access_stats['total']}")
        
        if access_stats['total'] == 0:
            print("✅ No credential accesses")
        else:
            print(f"Unique credentials: {len(access_stats['unique_credentials'])}")
            print(f"Unique accessors: {len(access_stats['unique_accessors'])}")
            print(f"Failed attempts: {access_stats['failed_attempts']}")
            
            print()
            print("Top accessed credentials:")
            top_creds = sorted(access_stats["by_credential"].items(), key=lambda x: x[1], reverse=True)[:5]
            for cred, count in top_creds:
                print(f"  - {cred}: {count}x")
            
            print()
            print("Top accessors:")
            top_accessors = sorted(access_stats["by_accessor"].items(), key=lambda x: x[1], reverse=True)[:5]
            for accessor, count in top_accessors:
                print(f"  - {accessor}: {count}x")
            
            if access_stats['failed_attempts'] > 0:
                print()
                print(f"⚠️  WARNING: {access_stats['failed_attempts']} failed access attempts!")
        
        print()
        print("="*60)
        print()
        
        # Return status
        has_critical = alert_stats["critical_count"] > 0
        has_failed = access_stats["failed_attempts"] > 0
        
        if has_critical or has_failed:
            print("🚨 ACTION REQUIRED: Critical alerts or failed access attempts detected")
            return 1
        elif alert_stats['total'] > 0:
            print("⚠️  Review recommended: Non-critical alerts detected")
            return 0
        else:
            print("✅ All clear: No security issues detected")
            return 0
    
    def check_suspicious(self):
        """Check for suspicious patterns"""
        print("="*60)
        print("SUSPICIOUS PATTERN CHECK")
        print("="*60)
        print()
        
        # Load recent data (last 24 hours)
        alerts = self.load_alerts(24)
        access_logs = self.load_credential_access(24)
        
        suspicious = []
        
        # Check for repeated credential leaks (same pattern multiple times)
        leak_patterns = defaultdict(int)
        for alert in alerts:
            if alert.get("type") == "leak_detected":
                pattern = alert.get("pattern", "unknown")
                leak_patterns[pattern] += 1
        
        for pattern, count in leak_patterns.items():
            if count >= 3:
                suspicious.append(f"⚠️  Repeated credential leak: {pattern} detected {count}x in 24h")
        
        # Check for high frequency credential access (>20 in 24h)
        access_freq = defaultdict(int)
        for access in access_logs:
            cred = access.get("credential_name", "unknown")
            access_freq[cred] += 1
        
        for cred, count in access_freq.items():
            if count > 20:
                suspicious.append(f"⚠️  High frequency access: {cred} accessed {count}x in 24h")
        
        # Check for failed access attempts
        failed_by_cred = defaultdict(int)
        for access in access_logs:
            if not access.get("success", True):
                cred = access.get("credential_name", "unknown")
                failed_by_cred[cred] += 1
        
        for cred, count in failed_by_cred.items():
            if count >= 3:
                suspicious.append(f"⚠️  Multiple failed access: {cred} failed {count}x in 24h")
        
        # Report
        if suspicious:
            print(f"🚨 Found {len(suspicious)} suspicious pattern(s):")
            print()
            for item in suspicious:
                print(item)
            print()
            print("Recommendation: Review security logs and investigate")
            return 1
        else:
            print("✅ No suspicious patterns detected")
            return 0


def main():
    """CLI interface"""
    if len(sys.argv) < 2:
        print("Usage: python security_monitor.py <report|check|daily|weekly>")
        print()
        print("Commands:")
        print("  report [hours]  - Generate security report (default: 24 hours)")
        print("  check           - Check for suspicious patterns")
        print("  daily           - Daily report (last 24 hours)")
        print("  weekly          - Weekly report (last 168 hours)")
        sys.exit(1)
    
    command = sys.argv[1]
    monitor = SecurityMonitor()
    
    if command == "report":
        hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
        return monitor.generate_report(hours)
    
    elif command == "check":
        return monitor.check_suspicious()
    
    elif command == "daily":
        return monitor.generate_report(24)
    
    elif command == "weekly":
        return monitor.generate_report(168)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())
