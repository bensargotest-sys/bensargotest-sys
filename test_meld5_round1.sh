#!/bin/bash
set -e
API_KEY="AIzaSyD-WuWBX8BpuKL1gHdLkFAlF3fR2W8dGYA"
MODEL="gemini-2.0-flash"
PROMPT="What are the biggest risks of restaking protocols like EigenLayer, and how should a risk-averse fund evaluate them?"

echo "Running SOLO..."
curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/models/$MODEL:generateContent?key=$API_KEY" \
 -H "Content-Type: application/json" \
 -d '{
  "system_instruction": {"parts":[{"text": "You are a blockchain and DeFi expert with comprehensive knowledge of restaking protocols."}]},
  "contents": [{"parts":[{"text": "'"$PROMPT"'"}]} ],
  "generationConfig": {"temperature": 0.3, "maxOutputTokens": 2048}
}' | jq -r '.candidates[0].content.parts[0].text // empty' > solo.txt
echo "Solo done."

echo "Running R1 Researcher..."
curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/models/$MODEL:generateContent?key=$API_KEY" \
 -H "Content-Type: application/json" \
 -d '{
  "system_instruction": {"parts":[{"text": "You are a seasoned DeFi researcher specializing in liquid staking and restaking protocols like EigenLayer. Provide in-depth analysis on risks from a market, protocol interaction, and ecosystem perspective."}]},
  "contents": [{"parts":[{"text": "'"$PROMPT"'"}]} ],
  "generationConfig": {"temperature": 0.3, "maxOutputTokens": 2048}
}' | jq -r '.candidates[0].content.parts[0].text // empty' > r1_researcher.txt
echo "R1 Researcher done."

echo "Running R1 Auditor..."
curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/models/$MODEL:generateContent?key=$API_KEY" \
 -H "Content-Type: application/json" \
 -d '{
  "system_instruction": {"parts":[{"text": "You are an expert smart contract auditor with experience auditing restaking protocols such as EigenLayer. Focus on technical, security, smart contract risks, and potential exploits."}]},
  "contents": [{"parts":[{"text": "'"$PROMPT"'"}]} ],
  "generationConfig": {"temperature": 0.3, "maxOutputTokens": 2048}
}' | jq -r '.candidates[0].content.parts[0].text // empty' > r1_auditor.txt
echo "R1 Auditor done."

echo "Running R1 Tokenomics..."
curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/models/$MODEL:generateContent?key=$API_KEY" \
 -H "Content-Type: application/json" \
 -d '{
  "system_instruction": {"parts":[{"text": "You are a tokenomics designer who has worked on incentive-aligned DeFi projects including LSTs and restaking. Analyze economic risks, incentive misalignments, tokenomics sustainability, and governance."}]},
  "contents": [{"parts":[{"text": "'"$PROMPT"'"}]} ],
  "generationConfig": {"temperature": 0.3, "maxOutputTokens": 2048}
}' | jq -r '.candidates[0].content.parts[0].text // empty' > r1_tokenomics.txt
echo "R1 Tokenomics done."

echo "Round 1 complete. Files: solo.txt r1_*.txt"
