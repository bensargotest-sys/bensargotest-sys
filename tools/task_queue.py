#!/usr/bin/env python3
"""
task_queue.py - Pull-based task coordination for subagents

Maintains a shared task queue that subagents can pull from, update status,
and report results. Enables async/parallel work coordination without direct
coupling between agents.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

TASK_QUEUE_FILE = Path(__file__).parent.parent / "memory" / "task-queue.json"


def load_queue() -> Dict:
    """Load task queue from JSON file"""
    if not TASK_QUEUE_FILE.exists():
        return {
            "tasks": [],
            "next_id": 1
        }
    
    try:
        with open(TASK_QUEUE_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {
            "tasks": [],
            "next_id": 1
        }


def save_queue(queue: Dict) -> None:
    """Save task queue to JSON file"""
    TASK_QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(TASK_QUEUE_FILE, 'w') as f:
        json.dump(queue, f, indent=2)


def add_task(
    title: str,
    description: str,
    priority: str = "medium",
    tags: Optional[List[str]] = None,
    assigned_to: Optional[str] = None
) -> int:
    """
    Add a new task to the queue
    
    Args:
        title: Short task title
        description: Detailed task description
        priority: Priority level (low, medium, high, critical)
        tags: Optional list of tags for categorization
        assigned_to: Optional agent/session to assign to
    
    Returns:
        Task ID
    """
    queue = load_queue()
    
    task_id = queue["next_id"]
    
    task = {
        "id": task_id,
        "title": title,
        "description": description,
        "priority": priority,
        "tags": tags or [],
        "status": "pending",
        "assigned_to": assigned_to,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "started_at": None,
        "completed_at": None,
        "result": None,
        "error": None
    }
    
    queue["tasks"].append(task)
    queue["next_id"] += 1
    
    save_queue(queue)
    
    print(f"✓ Task added (ID: {task_id})")
    print(f"  Title: {title}")
    print(f"  Priority: {priority}")
    
    return task_id


def claim_task(agent_id: str, task_id: Optional[int] = None) -> Optional[Dict]:
    """
    Claim a task for work (pull-based)
    
    Args:
        agent_id: Identifier for the claiming agent
        task_id: Optional specific task ID to claim
    
    Returns:
        Task dict if claimed, None if no tasks available
    """
    queue = load_queue()
    
    # Filter to pending tasks
    pending = [t for t in queue["tasks"] if t.get("status") == "pending"]
    
    if not pending:
        print("No pending tasks available")
        return None
    
    # If specific task requested
    if task_id is not None:
        task = next((t for t in pending if t.get("id") == task_id), None)
        if not task:
            print(f"Task {task_id} not found or not pending")
            return None
    else:
        # Sort by priority and take highest
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        pending.sort(key=lambda t: (
            priority_order.get(t.get("priority", "medium"), 2),
            t.get("created_at", "")
        ))
        task = pending[0]
    
    # Update task status
    for t in queue["tasks"]:
        if t.get("id") == task["id"]:
            t["status"] = "in_progress"
            t["assigned_to"] = agent_id
            t["started_at"] = datetime.utcnow().isoformat() + "Z"
            break
    
    save_queue(queue)
    
    print(f"✓ Task claimed (ID: {task['id']})")
    print(f"  Title: {task['title']}")
    print(f"  Assigned to: {agent_id}")
    
    return task


def complete_task(task_id: int, result: str, agent_id: Optional[str] = None) -> None:
    """
    Mark a task as completed with result
    
    Args:
        task_id: Task ID
        result: Result/output description
        agent_id: Optional agent identifier
    """
    queue = load_queue()
    
    task = next((t for t in queue["tasks"] if t.get("id") == task_id), None)
    
    if not task:
        print(f"⚠️  Task {task_id} not found")
        return
    
    if task.get("status") == "completed":
        print(f"⚠️  Task {task_id} already completed")
        return
    
    task["status"] = "completed"
    task["completed_at"] = datetime.utcnow().isoformat() + "Z"
    task["result"] = result
    
    if agent_id and not task.get("assigned_to"):
        task["assigned_to"] = agent_id
    
    save_queue(queue)
    
    print(f"✓ Task completed (ID: {task_id})")
    print(f"  Title: {task['title']}")
    print(f"  Result: {result}")


def fail_task(task_id: int, error: str, agent_id: Optional[str] = None) -> None:
    """
    Mark a task as failed with error
    
    Args:
        task_id: Task ID
        error: Error description
        agent_id: Optional agent identifier
    """
    queue = load_queue()
    
    task = next((t for t in queue["tasks"] if t.get("id") == task_id), None)
    
    if not task:
        print(f"⚠️  Task {task_id} not found")
        return
    
    task["status"] = "failed"
    task["completed_at"] = datetime.utcnow().isoformat() + "Z"
    task["error"] = error
    
    if agent_id and not task.get("assigned_to"):
        task["assigned_to"] = agent_id
    
    save_queue(queue)
    
    print(f"⚠️  Task failed (ID: {task_id})")
    print(f"  Title: {task['title']}")
    print(f"  Error: {error}")


def list_tasks(
    status_filter: Optional[str] = None,
    priority_filter: Optional[str] = None,
    tag_filter: Optional[str] = None
) -> None:
    """
    List tasks with optional filters
    
    Args:
        status_filter: Filter by status (pending, in_progress, completed, failed)
        priority_filter: Filter by priority
        tag_filter: Filter by tag
    """
    queue = load_queue()
    tasks = queue.get("tasks", [])
    
    # Apply filters
    if status_filter:
        tasks = [t for t in tasks if t.get("status") == status_filter]
    
    if priority_filter:
        tasks = [t for t in tasks if t.get("priority") == priority_filter]
    
    if tag_filter:
        tasks = [t for t in tasks if tag_filter in t.get("tags", [])]
    
    if not tasks:
        print("No tasks found")
        return
    
    # Sort by priority and creation time
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    tasks.sort(key=lambda t: (
        {"pending": 0, "in_progress": 1, "completed": 2, "failed": 3}.get(t.get("status", "pending"), 0),
        priority_order.get(t.get("priority", "medium"), 2),
        t.get("created_at", "")
    ))
    
    print(f"\n{'='*70}")
    print(f"Task Queue ({len(tasks)} tasks)")
    print(f"{'='*70}\n")
    
    for task in tasks:
        status_icons = {
            "pending": "⏳",
            "in_progress": "⚙️",
            "completed": "✅",
            "failed": "❌"
        }
        priority_icons = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢"
        }
        
        status_icon = status_icons.get(task.get("status", "pending"), "⚪")
        priority_icon = priority_icons.get(task.get("priority", "medium"), "⚪")
        
        print(f"{status_icon} {priority_icon} ID: {task.get('id')} | {task.get('status', 'unknown').upper()}")
        print(f"   Title: {task.get('title')}")
        
        if task.get("description"):
            desc = task.get("description", "")
            if len(desc) > 80:
                desc = desc[:77] + "..."
            print(f"   Description: {desc}")
        
        if task.get("assigned_to"):
            print(f"   Assigned: {task.get('assigned_to')}")
        
        if task.get("tags"):
            print(f"   Tags: {', '.join(task.get('tags'))}")
        
        if task.get("result"):
            result = task.get("result", "")
            if len(result) > 80:
                result = result[:77] + "..."
            print(f"   Result: {result}")
        
        if task.get("error"):
            error = task.get("error", "")
            if len(error) > 80:
                error = error[:77] + "..."
            print(f"   Error: {error}")
        
        print()


def summary() -> None:
    """Print summary statistics"""
    queue = load_queue()
    tasks = queue.get("tasks", [])
    
    if not tasks:
        print("No tasks in queue")
        return
    
    status_counts = {}
    priority_counts = {}
    
    for task in tasks:
        status = task.get("status", "unknown")
        priority = task.get("priority", "medium")
        
        status_counts[status] = status_counts.get(status, 0) + 1
        priority_counts[priority] = priority_counts.get(priority, 0) + 1
    
    print(f"\n{'='*70}")
    print("Task Queue Summary")
    print(f"{'='*70}\n")
    
    print(f"Total tasks: {len(tasks)}")
    print(f"Next ID: {queue.get('next_id', 1)}")
    print()
    
    print("By Status:")
    for status in ["pending", "in_progress", "completed", "failed"]:
        count = status_counts.get(status, 0)
        print(f"  {status.replace('_', ' ').capitalize()}: {count}")
    
    print()
    print("By Priority:")
    for priority in ["critical", "high", "medium", "low"]:
        count = priority_counts.get(priority, 0)
        print(f"  {priority.capitalize()}: {count}")


def main():
    """CLI interface"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  task_queue.py add <title> <description> [--priority=X] [--tags=X,Y] [--assign=agent]")
        print("  task_queue.py claim <agent_id> [task_id]")
        print("  task_queue.py complete <task_id> <result> [--agent=X]")
        print("  task_queue.py fail <task_id> <error> [--agent=X]")
        print("  task_queue.py list [--status=X] [--priority=X] [--tag=X]")
        print("  task_queue.py summary")
        print()
        print("Statuses: pending, in_progress, completed, failed")
        print("Priorities: low, medium, high, critical")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "add":
        if len(sys.argv) < 4:
            print("Error: add requires <title> and <description>")
            sys.exit(1)
        
        title = sys.argv[2]
        description = sys.argv[3]
        
        priority = "medium"
        tags = []
        assigned_to = None
        
        for arg in sys.argv[4:]:
            if arg.startswith("--priority="):
                priority = arg.split("=", 1)[1]
            elif arg.startswith("--tags="):
                tags = arg.split("=", 1)[1].split(",")
            elif arg.startswith("--assign="):
                assigned_to = arg.split("=", 1)[1]
        
        add_task(title, description, priority, tags, assigned_to)
    
    elif action == "claim":
        if len(sys.argv) < 3:
            print("Error: claim requires <agent_id>")
            sys.exit(1)
        
        agent_id = sys.argv[2]
        task_id = None
        
        if len(sys.argv) > 3:
            try:
                task_id = int(sys.argv[3])
            except ValueError:
                print("Error: task_id must be a number")
                sys.exit(1)
        
        claim_task(agent_id, task_id)
    
    elif action == "complete":
        if len(sys.argv) < 4:
            print("Error: complete requires <task_id> and <result>")
            sys.exit(1)
        
        try:
            task_id = int(sys.argv[2])
        except ValueError:
            print("Error: task_id must be a number")
            sys.exit(1)
        
        result = sys.argv[3]
        agent_id = None
        
        for arg in sys.argv[4:]:
            if arg.startswith("--agent="):
                agent_id = arg.split("=", 1)[1]
        
        complete_task(task_id, result, agent_id)
    
    elif action == "fail":
        if len(sys.argv) < 4:
            print("Error: fail requires <task_id> and <error>")
            sys.exit(1)
        
        try:
            task_id = int(sys.argv[2])
        except ValueError:
            print("Error: task_id must be a number")
            sys.exit(1)
        
        error = sys.argv[3]
        agent_id = None
        
        for arg in sys.argv[4:]:
            if arg.startswith("--agent="):
                agent_id = arg.split("=", 1)[1]
        
        fail_task(task_id, error, agent_id)
    
    elif action == "list":
        status_filter = None
        priority_filter = None
        tag_filter = None
        
        for arg in sys.argv[2:]:
            if arg.startswith("--status="):
                status_filter = arg.split("=", 1)[1]
            elif arg.startswith("--priority="):
                priority_filter = arg.split("=", 1)[1]
            elif arg.startswith("--tag="):
                tag_filter = arg.split("=", 1)[1]
        
        list_tasks(status_filter, priority_filter, tag_filter)
    
    elif action == "summary":
        summary()
    
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)


if __name__ == "__main__":
    main()
