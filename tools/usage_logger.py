#!/usr/bin/env python3
"""
Usage Logger - Centralized tool usage tracking

Provides decorator and helper functions to log tool usage for effectiveness analysis.

Usage:
    from usage_logger import log_usage, log_action
    
    @log_usage
    def main():
        # Your tool logic
        pass
        
    # Or manually:
    log_action("tool_name", "action", success=True, details={"foo": "bar"})
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from functools import wraps
import traceback

USAGE_LOG = Path("/data/.openclaw/workspace/memory/tool-usage.log")

def ensure_log_exists():
    """Create log file if it doesn't exist"""
    USAGE_LOG.parent.mkdir(parents=True, exist_ok=True)
    if not USAGE_LOG.exists():
        USAGE_LOG.touch()

def log_action(tool_name: str, action: str = "main", success: bool = True, 
               details: dict = None, error: str = None):
    """
    Log a tool action to the usage log
    
    Args:
        tool_name: Name of the tool (e.g., "checkpoint", "mistake_logger")
        action: Action performed (e.g., "check", "log", "promote")
        success: Whether the action succeeded
        details: Optional dict with additional context
        error: Optional error message if failed
    """
    ensure_log_exists()
    
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "tool": tool_name,
        "action": action,
        "success": success,
        "details": details or {},
    }
    
    if error:
        entry["error"] = error
    
    # Append as JSON lines
    with USAGE_LOG.open("a") as f:
        f.write(json.dumps(entry) + "\n")

def log_usage(func):
    """
    Decorator to automatically log tool usage
    
    Usage:
        @log_usage
        def main():
            # Your tool logic
            pass
    
    Captures tool name from __file__, logs start/success/failure
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Extract tool name from stack frame
        frame = sys._getframe(1)
        tool_file = frame.f_globals.get("__file__", "unknown")
        tool_name = Path(tool_file).stem if tool_file else "unknown"
        
        # Extract action from sys.argv if available
        action = "main"
        if len(sys.argv) > 1:
            action = sys.argv[1]
        
        try:
            result = func(*args, **kwargs)
            log_action(tool_name, action, success=True)
            return result
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            log_action(tool_name, action, success=False, error=error_msg)
            raise
    
    return wrapper

def get_usage_stats(tool_name: str = None, hours: int = 24) -> dict:
    """
    Get usage statistics for a tool or all tools
    
    Args:
        tool_name: Optional tool name to filter by
        hours: Number of hours to look back (default 24)
    
    Returns:
        dict with usage stats
    """
    if not USAGE_LOG.exists():
        return {"total": 0, "success": 0, "failure": 0}
    
    cutoff = datetime.now().timestamp() - (hours * 3600)
    stats = {"total": 0, "success": 0, "failure": 0, "by_tool": {}}
    
    with USAGE_LOG.open() as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                
                # Parse timestamp
                ts = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
                if ts.timestamp() < cutoff:
                    continue
                
                # Filter by tool if specified
                if tool_name and entry["tool"] != tool_name:
                    continue
                
                stats["total"] += 1
                if entry["success"]:
                    stats["success"] += 1
                else:
                    stats["failure"] += 1
                
                # Per-tool stats
                tool = entry["tool"]
                if tool not in stats["by_tool"]:
                    stats["by_tool"][tool] = {"total": 0, "success": 0, "failure": 0}
                
                stats["by_tool"][tool]["total"] += 1
                if entry["success"]:
                    stats["by_tool"][tool]["success"] += 1
                else:
                    stats["by_tool"][tool]["failure"] += 1
                    
            except (json.JSONDecodeError, KeyError):
                continue
    
    return stats

def print_usage_report(hours: int = 24):
    """Print a formatted usage report"""
    stats = get_usage_stats(hours=hours)
    
    print(f"📊 Tool Usage Report (last {hours}h)")
    print(f"Total actions: {stats['total']}")
    print(f"Success: {stats['success']} ({stats['success']/stats['total']*100:.1f}%)" if stats['total'] > 0 else "Success: 0")
    print(f"Failure: {stats['failure']} ({stats['failure']/stats['total']*100:.1f}%)" if stats['total'] > 0 else "Failure: 0")
    print()
    
    if stats["by_tool"]:
        print("By tool:")
        for tool, tool_stats in sorted(stats["by_tool"].items(), 
                                       key=lambda x: x[1]["total"], 
                                       reverse=True):
            success_rate = tool_stats["success"] / tool_stats["total"] * 100 if tool_stats["total"] > 0 else 0
            print(f"  • {tool}: {tool_stats['total']} calls ({success_rate:.0f}% success)")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Tool usage logging and reporting")
    parser.add_argument("--report", action="store_true", help="Print usage report")
    parser.add_argument("--hours", type=int, default=24, help="Hours to look back (default 24)")
    parser.add_argument("--tool", help="Filter by tool name")
    
    args = parser.parse_args()
    
    if args.report:
        print_usage_report(hours=args.hours)
    else:
        # Show usage stats as JSON
        stats = get_usage_stats(tool_name=args.tool, hours=args.hours)
        print(json.dumps(stats, indent=2))
