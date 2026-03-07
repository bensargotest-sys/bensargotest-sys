#!/usr/bin/env python3
"""Self-Improvement analyzer: find gaps, patterns, and recommendations."""
import json, os, re, glob
from datetime import datetime, timedelta
from collections import Counter

WORKSPACE = "/data/.openclaw/workspace"

def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return None

def load_jsonl(path):
    items = []
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    items.append(json.loads(line))
    except:
        pass
    return items

def analyze_mistakes():
    data = load_json(f"{WORKSPACE}/memory/mistakes.json")
    if not data or not isinstance(data, list):
        return {"count": 0, "categories": {}, "top": "none"}
    cats = Counter()
    for m in data:
        cat = m.get("category", m.get("type", "unknown"))
        cats[cat] += 1
    top = cats.most_common(1)[0] if cats else ("none", 0)
    return {"count": len(data), "categories": dict(cats), "top": top[0]}

def analyze_worklog():
    path = f"{WORKSPACE}/memory/work-log.md"
    if not os.path.exists(path):
        return {"entries": 0, "recent_7d": 0}
    with open(path) as f:
        content = f.read()
    lines = [l for l in content.split("\n") if l.strip().startswith("- ") or l.strip().startswith("* ")]
    cutoff = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
    recent = [l for l in lines if cutoff <= l[:10] if re.match(r"\d{4}-\d{2}-\d{2}", l.strip("- *")[:10])]
    return {"entries": len(lines), "recent_7d": len(recent)}

def analyze_self_reviews():
    path = f"{WORKSPACE}/memory/self-review.md"
    if not os.path.exists(path):
        return {"reviews": 0, "themes": []}
    with open(path) as f:
        content = f.read()
    reviews = re.findall(r'^## \d{4}-\d{2}-\d{2}', content, re.MULTILINE)
    themes = []
    sections = content.split("###")
    for s in sections:
        if "pattern" in s.lower() or "recurring" in s.lower() or "issue" in s.lower():
            first_line = s.strip().split("\n")[0][:80]
            themes.append(first_line)
    return {"reviews": len(reviews), "themes": themes[:5]}

def generate_gaps(mistakes, worklog, reviews):
    gaps = []
    if mistakes["count"] > 5:
        gaps.append({"area": "error rate", "severity": "high" if mistakes["count"] > 10 else "medium",
                      "suggestion": f"Top mistake category: {mistakes['top']}. Create a checklist to prevent."})
    if worklog["entries"] == 0:
        gaps.append({"area": "work logging", "severity": "high",
                      "suggestion": "No work log entries. Start logging completed items."})
    if reviews["reviews"] == 0:
        gaps.append({"area": "self-review", "severity": "medium",
                      "suggestion": "No self-reviews found. Self-review cron may not be running."})
    if not gaps:
        gaps.append({"area": "none", "severity": "low", "suggestion": "No major gaps detected."})
    return gaps

def main():
    mistakes = analyze_mistakes()
    worklog = analyze_worklog()
    reviews = analyze_self_reviews()
    gaps = generate_gaps(mistakes, worklog, reviews)
    result = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "metrics": {
            "total_mistakes": mistakes["count"],
            "top_mistake_category": mistakes["top"],
            "worklog_entries": worklog["entries"],
            "worklog_recent_7d": worklog["recent_7d"],
            "self_reviews": reviews["reviews"]
        },
        "gaps": gaps,
        "recommendations": [g["suggestion"] for g in gaps]
    }
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
