#!/usr/bin/env python3

import json
import glob
import os
import datetime
import re


def parse_date(filename):
    match = re.search(r"20\d{2}-\d{2}-\d{2}", filename)
    if match:
        return match.group(0)
    return None

def load_existing_episodes(filepath):
    episodes = []
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            for line in f:
                try:
                    episodes.append(json.loads(line))
                except json.JSONDecodeError:
                    print(f"Warning: Skipping invalid JSON line: {line.strip()}")
    return episodes


def extract_episodes(filepath, date_str):
    episodes = []
    with open(filepath, 'r') as f:
        content = f.read()

    # Simple regex-based extraction (adjust as needed)
    episode_matches = re.finditer(r"---.*?---", content, re.DOTALL)
    for match in episode_matches:
        episode_text = match.group(0)
        
        # Extract fields using more robust regex or splitting
        type_match = re.search(r"type:\s*([a-zA-Z]+)", episode_text)
        type_value = type_match.group(1) if type_match else None

        participants_match = re.search(r"participants:\s*(.+)", episode_text)
        participants_value = participants_match.group(1).strip() if participants_match else None

        topics_match = re.search(r"topics:\s*\[(.*?)\]", episode_text)
        topics_value = [topic.strip() for topic in topics_match.group(1).split(',')] if topics_match else []

        importance_match = re.search(r"importance:\s*(\d+)", episode_text)
        importance_value = int(importance_match.group(1)) if importance_match else None

        decisions_match = re.search(r"decisions:\s*\[(.*?)\]", episode_text)
        decisions_value = [decision.strip() for decision in decisions_match.group(1).split(',')] if decisions_match else []

        learnings_match = re.search(r"learnings:\s*\[(.*?)\]", episode_text)
        learnings_value = [learning.strip() for learning in learnings_match.group(1).split(',')] if learnings_match else []

        emotional_valence_match = re.search(r"emotional_valence:\s*([a-zA-Z]+)", episode_text)
        emotional_valence_value = emotional_valence_match.group(1) if emotional_valence_match else None


        episodes.append({
            "date": date_str,
            "type": type_value,
            "participants": participants_value,
            "topics": topics_value,
            "importance": importance_value,
            "decisions": decisions_value,
            "learnings": learnings_value,
            "emotional_valence": emotional_valence_value
        })
    return episodes


def main():
    today = datetime.date.today()
    date_str = today.strftime("%Y-%m-%d")
    
    memory_files = glob.glob(os.path.join("/data/.openclaw/workspace/memory", f"{date_str}*.md"))
    observations_file = os.path.join("/data/.openclaw/workspace/memory", "observations.md")
    if os.path.exists(observations_file):
      memory_files.append(observations_file)

    episodes_filepath = os.path.join("/data/.openclaw/workspace/memory", "episodes.jsonl")
    existing_episodes = load_existing_episodes(episodes_filepath)
    last_episode_timestamp = None
    if existing_episodes:
        last_episode_timestamp = existing_episodes[-1].get("date")

    new_episodes = []
    for file in memory_files:
        file_date = parse_date(file)
        if not file_date:
            continue

        if last_episode_timestamp and file_date <= last_episode_timestamp:
            print(f"Skipping {file} - no new content since last run.")
            continue

        new_episodes.extend(extract_episodes(file, file_date))

    if new_episodes:
        with open(episodes_filepath, 'a') as f:
            for episode in new_episodes:
                f.write(json.dumps(episode) + '\n')

        print(f"Recorded {len(new_episodes)} new episodes.")
    else:
        print("No new episodes to record.")

if __name__ == "__main__":
    main()
