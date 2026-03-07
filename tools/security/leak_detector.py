#!/usr/bin/env python3
"""
Leak Detection System - Scans outputs for credential exposure
Author: Praxis (built for AB)
Created: 2026-02-14
Inspired by: IronClaw's request/response leak scanning

Scans text for API keys, tokens, passwords, and other secrets
before they're exposed to LLM context or logs.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class LeakDetection:
    """Represents a detected credential leak"""
    pattern_name: str
    matched_text: str
    severity: str
    description: str
    position: int
    context: str  # 20 chars before and after

@dataclass
class ScanResult:
    """Result of scanning text for leaks"""
    clean: bool
    detections: List[LeakDetection]
    sanitized_text: Optional[str] = None
    
    def __bool__(self):
        """True if clean (no leaks), False if leaks detected"""
        return self.clean

class LeakDetector:
    """Scans text for credential leaks using pattern matching"""
    
    def __init__(self, patterns_file: Optional[str] = None):
        """Initialize with patterns from JSON file"""
        if patterns_file is None:
            patterns_file = Path(__file__).parent / "patterns" / "secrets.json"
        
        self.patterns_file = Path(patterns_file)
        self.patterns = []
        self.allowlist = []
        self._load_patterns()
    
    def _load_patterns(self):
        """Load patterns from JSON file"""
        with open(self.patterns_file) as f:
            data = json.load(f)
        
        for pattern_def in data["patterns"]:
            flags = re.IGNORECASE if pattern_def.get("case_insensitive", False) else 0
            self.patterns.append({
                "name": pattern_def["name"],
                "pattern": re.compile(pattern_def["pattern"], flags),
                "severity": pattern_def["severity"],
                "description": pattern_def["description"]
            })
        
        # Compile allowlist patterns
        for allowed in data.get("allowlist", []):
            self.allowlist.append(re.compile(allowed["pattern"]))
    
    def scan(self, text: str, sanitize: bool = False) -> ScanResult:
        """
        Scan text for credential leaks.
        
        Args:
            text: Text to scan
            sanitize: If True, return sanitized version with redactions
        
        Returns:
            ScanResult with detections and optional sanitized text
        """
        detections = []
        
        for pattern_def in self.patterns:
            for match in pattern_def["pattern"].finditer(text):
                matched_text = match.group(0)
                
                # Check allowlist
                if self._is_allowed(matched_text):
                    continue
                
                # Extract context (20 chars before/after)
                start = max(0, match.start() - 20)
                end = min(len(text), match.end() + 20)
                context = text[start:end]
                
                detections.append(LeakDetection(
                    pattern_name=pattern_def["name"],
                    matched_text=matched_text,
                    severity=pattern_def["severity"],
                    description=pattern_def["description"],
                    position=match.start(),
                    context=context
                ))
        
        # Sanitize if requested
        sanitized_text = None
        if sanitize and detections:
            sanitized_text = self._sanitize(text, detections)
        
        return ScanResult(
            clean=len(detections) == 0,
            detections=detections,
            sanitized_text=sanitized_text
        )
    
    def _is_allowed(self, text: str) -> bool:
        """Check if text matches allowlist (e.g., documentation examples)"""
        for allowed_pattern in self.allowlist:
            if allowed_pattern.search(text):
                return True
        return False
    
    def _sanitize(self, text: str, detections: List[LeakDetection]) -> str:
        """
        Sanitize text by redacting detected secrets.
        Replaces secrets with [REDACTED: {type}]
        """
        # Sort detections by position (reverse order for stable string replacement)
        sorted_detections = sorted(detections, key=lambda d: d.position, reverse=True)
        
        sanitized = text
        for detection in sorted_detections:
            # Find the matched text in the string
            start = detection.position
            end = start + len(detection.matched_text)
            
            # Replace with redaction
            redaction = f"[REDACTED: {detection.pattern_name}]"
            sanitized = sanitized[:start] + redaction + sanitized[end:]
        
        return sanitized
    
    def scan_file(self, file_path: str) -> ScanResult:
        """Scan a file for credential leaks"""
        with open(file_path, 'r') as f:
            return self.scan(f.read())
    
    def log_detection(self, detection: LeakDetection, source: str = "unknown"):
        """Log a detection to security audit log"""
        log_dir = Path(__file__).parent.parent.parent / "memory"
        log_file = log_dir / "security-alerts.json"
        
        # Create or load log
        if log_file.exists():
            with open(log_file) as f:
                log_data = json.load(f)
        else:
            log_data = {"alerts": []}
        
        # Add detection
        log_data["alerts"].append({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": source,
            "pattern": detection.pattern_name,
            "severity": detection.severity,
            "description": detection.description,
            "context": detection.context[:50] + "..." if len(detection.context) > 50 else detection.context
        })
        
        # Write back
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)


def scan_text(text: str, sanitize: bool = False) -> ScanResult:
    """Convenience function: scan text for leaks"""
    detector = LeakDetector()
    return detector.scan(text, sanitize=sanitize)


def scan_command_output(command: str, output: str, sanitize: bool = True) -> Tuple[bool, str]:
    """
    Scan command output for credential leaks.
    
    Args:
        command: The command that was run
        output: The command output
        sanitize: If True and leaks found, return sanitized version
    
    Returns:
        (is_safe, text) - text is original or sanitized depending on leaks
    """
    detector = LeakDetector()
    result = detector.scan(output, sanitize=sanitize)
    
    if not result.clean:
        # Log all detections
        for detection in result.detections:
            detector.log_detection(detection, source=f"command: {command}")
        
        # Return sanitized if requested
        if sanitize:
            return False, result.sanitized_text
        else:
            return False, output
    
    return True, output


def scan_web_content(url: str, content: str, sanitize: bool = True) -> Tuple[bool, str]:
    """
    Scan web content for credential leaks (e.g., from web_fetch).
    
    Args:
        url: The URL fetched
        content: The content retrieved
        sanitize: If True and leaks found, return sanitized version
    
    Returns:
        (is_safe, text) - text is original or sanitized depending on leaks
    """
    detector = LeakDetector()
    result = detector.scan(content, sanitize=sanitize)
    
    if not result.clean:
        # Log all detections
        for detection in result.detections:
            detector.log_detection(detection, source=f"web: {url}")
        
        # Return sanitized if requested
        if sanitize:
            return False, result.sanitized_text
        else:
            return False, content
    
    return True, content


def main():
    """CLI interface for testing"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python leak_detector.py <text|file> [value]")
        print("Examples:")
        print("  python leak_detector.py text 'sk-or-v1-abc123...'")
        print("  python leak_detector.py file /path/to/file.txt")
        sys.exit(1)
    
    mode = sys.argv[1]
    
    detector = LeakDetector()
    
    if mode == "text":
        text = sys.argv[2] if len(sys.argv) > 2 else sys.stdin.read()
        result = detector.scan(text, sanitize=True)
    elif mode == "file":
        file_path = sys.argv[2]
        result = detector.scan_file(file_path)
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)
    
    # Print results
    if result.clean:
        print("✅ CLEAN - No credential leaks detected")
        sys.exit(0)
    else:
        print(f"🚨 LEAKS DETECTED - {len(result.detections)} credential(s) found")
        print()
        for i, detection in enumerate(result.detections, 1):
            print(f"Detection #{i}:")
            print(f"  Pattern: {detection.pattern_name}")
            print(f"  Severity: {detection.severity.upper()}")
            print(f"  Description: {detection.description}")
            print(f"  Context: ...{detection.context}...")
            print()
        
        if result.sanitized_text:
            print("Sanitized output:")
            print("-" * 60)
            print(result.sanitized_text)
        
        sys.exit(1)


if __name__ == "__main__":
    main()
