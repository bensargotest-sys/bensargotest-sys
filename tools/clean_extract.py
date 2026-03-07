#!/usr/bin/env python3
"""Clean extracted messages — strip Telegram metadata wrappers, dedupe, sort by date."""
import json, re, os

input_dir = "/data/.openclaw/workspace/history-extract"
output_dir = input_dir

# Clean pattern: remove Conversation info blocks and reply context
meta_re = re.compile(r'Conversation info \(untrusted metadata\):.*?```\n\n', re.DOTALL)
reply_re = re.compile(r'Replied message \(untrusted metadata\):.*?```\n\n', re.DOTALL)
queued_re = re.compile(r'\[Queued messages while agent was busy\]\n\n---\nQueued #\d+\n', re.DOTALL)
telegram_re = re.compile(r'\[Telegram .*?\] ')

def clean_text(text):
    text = meta_re.sub('', text)
    text = reply_re.sub('', text)
    text = queued_re.sub('', text)
    text = telegram_re.sub('', text)
    text = text.strip()
    return text

# Process each file
for fname in ['user_messages.jsonl', 'ideas.jsonl', 'decisions.jsonl']:
    filepath = f"{input_dir}/{fname}"
    cleaned = []
    seen = set()
    
    with open(filepath) as f:
        for line in f:
            d = json.loads(line)
            text = clean_text(d['text'])
            if len(text) < 10:
                continue
            # Dedupe
            key = text[:100]
            if key in seen:
                continue
            seen.add(key)
            d['text'] = text
            cleaned.append(d)
    
    # Sort by date
    cleaned.sort(key=lambda x: x.get('date', '?'))
    
    outpath = f"{input_dir}/clean_{fname}"
    with open(outpath, 'w') as f:
        for d in cleaned:
            f.write(json.dumps(d) + '\n')
    
    print(f"{fname}: {len(cleaned)} entries (cleaned)")

# Clean links too
links = set()
with open(f"{input_dir}/links.txt") as f:
    for line in f:
        parts = line.strip().split(' | ', 1)
        if len(parts) == 2:
            url = parts[1].strip().rstrip('.,;:)\'">')
            # Skip internal/localhost
            if 'localhost' in url or '127.0.0.1' in url:
                continue
            if len(url) > 15:
                links.add(url)

with open(f"{input_dir}/clean_links.txt", 'w') as f:
    for link in sorted(links):
        f.write(link + '\n')

print(f"links: {len(links)} unique external URLs")
