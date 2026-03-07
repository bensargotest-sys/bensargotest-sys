#!/usr/bin/env python3
"""Extract key content from session JSONL files for analysis."""
import json, sys, os, glob, re
from datetime import datetime

sessions_dir = "/data/.openclaw/agents/main/sessions"
output_dir = "/data/.openclaw/workspace/history-extract"
os.makedirs(output_dir, exist_ok=True)

# Get all JSONL files sorted by size (biggest first)
files = glob.glob(f"{sessions_dir}/*.jsonl")
files = [(f, os.path.getsize(f)) for f in files if not f.endswith('sessions.json')]
files.sort(key=lambda x: -x[1])

print(f"Total files: {len(files)}")
print(f"Total size: {sum(s for _,s in files) / 1024/1024:.1f}MB")

# Extract from each file
all_user_messages = []
all_links = []
all_ideas = []
all_decisions = []
all_errors = []

link_re = re.compile(r'https?://[^\s\)\"\'>\]]+')
idea_keywords = re.compile(r'idea|concept|pivot|build|product|what if|should we|could we|lets|let\'s|prototype|MVP', re.I)
decision_keywords = re.compile(r'decision|decided|kill|ship|go with|chose|picked|confirmed|approved|rejected', re.I)

processed = 0
for filepath, size in files:
    fname = os.path.basename(filepath)
    try:
        with open(filepath) as f:
            for line in f:
                try:
                    d = json.loads(line)
                except:
                    continue
                
                # Handle both formats: flat (role at top) and nested (type=message, role inside message)
                if d.get('type') == 'message':
                    msg = d.get('message', {})
                    role = msg.get('role', '')
                    ts = msg.get('timestamp', d.get('timestamp', 0))
                    content = msg.get('content', '')
                else:
                    role = d.get('role', '')
                    content = d.get('content', '')
                    msg = d
                ts = d.get('timestamp', 0)
                try:
                    ts = float(ts) if ts else 0
                    if ts > 1000000000000:
                        ts = ts / 1000
                    date_str = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M') if ts > 0 else '?'
                except:
                    date_str = '?'
                
                # Get text content
                text = ''
                if isinstance(content, str):
                    text = content
                elif isinstance(content, list):
                    for c in content:
                        if isinstance(c, dict) and c.get('type') == 'text':
                            text += c.get('text', '') + '\n'
                
                if not text.strip():
                    continue
                
                # Extract links
                links = link_re.findall(text)
                for link in links:
                    all_links.append((date_str, link.rstrip('.,;:'), fname[:8]))
                
                # User messages from AB (not system, not compaction prompts)
                if role == 'user' and len(text) > 20:
                    # Skip system messages
                    if text.startswith('Pre-compaction') or text.startswith('GatewayRestart') or text.startswith('Heartbeat'):
                        continue
                    all_user_messages.append((date_str, text[:500], fname[:8]))
                    
                    # Check for ideas
                    if idea_keywords.search(text):
                        all_ideas.append((date_str, text[:300], fname[:8]))
                    
                    # Check for decisions
                    if decision_keywords.search(text):
                        all_decisions.append((date_str, text[:300], fname[:8]))
                
                # Compaction summaries (gold — these ARE the distilled history)
                is_compaction = d.get('__openclaw', {}).get('kind') == 'compaction'
                if not is_compaction and d.get('type') == 'summary':
                    is_compaction = True
                if not is_compaction and 'summary' in str(d.get('type','')).lower():
                    is_compaction = True
                # Also catch compaction summaries in user messages
                if not is_compaction and role == 'user' and '<summary>' in text[:50]:
                    is_compaction = True
                if is_compaction:
                    summary_file = f"{output_dir}/compaction_{fname[:8]}_{date_str.replace(' ','_').replace(':','-')}.txt"
                    with open(summary_file, 'w') as sf:
                        sf.write(text[:50000])
                
    except Exception as e:
        all_errors.append(f"{fname}: {e}")
    
    processed += 1
    if processed % 100 == 0:
        print(f"Processed {processed}/{len(files)} files...")

print(f"\nExtracted:")
print(f"  User messages: {len(all_user_messages)}")
print(f"  Links: {len(all_links)}")
print(f"  Ideas: {len(all_ideas)}")
print(f"  Decisions: {len(all_decisions)}")
print(f"  Errors: {len(all_errors)}")

# Write outputs
with open(f"{output_dir}/user_messages.jsonl", 'w') as f:
    for date, text, src in all_user_messages:
        f.write(json.dumps({"date": date, "text": text, "src": src}) + '\n')

with open(f"{output_dir}/links.txt", 'w') as f:
    seen = set()
    for date, link, src in sorted(set(all_links)):
        if link not in seen:
            f.write(f"{date} | {link}\n")
            seen.add(link)

with open(f"{output_dir}/ideas.jsonl", 'w') as f:
    for date, text, src in all_ideas:
        f.write(json.dumps({"date": date, "text": text, "src": src}) + '\n')

with open(f"{output_dir}/decisions.jsonl", 'w') as f:
    for date, text, src in all_decisions:
        f.write(json.dumps({"date": date, "text": text, "src": src}) + '\n')

if all_errors:
    with open(f"{output_dir}/errors.txt", 'w') as f:
        for e in all_errors:
            f.write(e + '\n')

print(f"\nOutput written to {output_dir}/")
print("Files: user_messages.jsonl, links.txt, ideas.jsonl, decisions.jsonl, compaction_*.txt")
