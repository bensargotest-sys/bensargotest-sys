
import datetime
import json
import os

def read_file(filepath):
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return None

def load_jsonl(filepath):
    data = []
    try:
        with open(filepath, 'r') as f:
            for line in f:
                data.append(json.loads(line))
    except FileNotFoundError:
        pass
    return data

def consolidate_memory():
    # 1. Read daily files from the past 7 days
    today = datetime.date.today()
    daily_files = []
    for i in range(7):
        date = today - datetime.timedelta(days=i)
        filepath = f"memory/{date.strftime('%Y-%m-%d')}.md"
        content = read_file(filepath)
        if content:
            daily_files.append(content)

    # 2. Read observations.md
    observations = read_file("memory/observations.md")

    # 3. Read episodes.jsonl if it exists
    episodes = load_jsonl("memory/episodes.jsonl")

    # 4. Extract key decisions, lessons, patterns, and ongoing context
    # This is where you'd put your NLP or extraction logic
    # For now, let's just concatenate the content
    all_content = "\n".join(daily_files)
    if observations:
        all_content += "\n" + observations
    if episodes:
        all_content += "\n" + str(episodes) # JSON serialize if needed

    # 5. Output a consolidated summary to stdout
    print("Consolidated Memory Summary:\n")
    print(all_content)

    # 6. Track what was already consolidated
    # This could be a file that stores the dates of the daily files that were consolidated
    # Or it could update a section in MEMORY.md
    # This implementation is left as an exercise for the user

if __name__ == "__main__":
    consolidate_memory()
