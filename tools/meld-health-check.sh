#!/bin/bash
# MELD Network Health Check — pure bash, no LLM
# Cron: */30 * * * * bash /data/.openclaw/workspace/tools/meld-health-check.sh

LOG="/data/.openclaw/workspace/memory/meld-health-log.jsonl"
TS=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
SSH_OPTS="-o ConnectTimeout=5 -o StrictHostKeyChecking=no -o BatchMode=yes"

NODES=("meld-2:147.93.72.73" "meld-3:72.61.53.248" "meld-4:76.13.198.23")
ALERTS=""
RESULTS="[]"

for entry in "${NODES[@]}"; do
  NAME="${entry%%:*}"
  IP="${entry##*:}"

  # SSH + PM2 + ledger + health in one call
  RAW=$(ssh $SSH_OPTS "root@$IP" 'bash -s' 2>/dev/null <<'REMOTE'
pm2_status="unknown"; balance="0"; earned="0"; spent="0"; txns="0"; health="fail"; agent_id=""
# PM2
pm2_json=$(pm2 jlist 2>/dev/null) && \
  pm2_status=$(echo "$pm2_json" | python3 -c "
import sys,json
try:
 d=json.load(sys.stdin)
 ms=[x for x in d if 'meld' in x.get('name','')]
 print(ms[0]['pm2_env']['status'] if ms else 'no_process')
except: print('error')" 2>/dev/null)
# Ledger
python3 -c "
import json,os,glob
p=os.path.expanduser('~/.meld/ledger.json')
d=json.load(open(p))
print(f\"{d['balance']:.4f}|{d['totalEarned']:.4f}|{d['totalSpent']:.4f}|{len(d.get('transactions',[]))}|{d['agentId']}\")
" 2>/dev/null | {
  IFS='|' read -r balance earned spent txns agent_id
  # Health
  h=$(curl -s --max-time 5 http://127.0.0.1:9377/v1/health 2>/dev/null)
  health=$(echo "$h" | python3 -c "import sys,json;print(json.load(sys.stdin).get('status','fail'))" 2>/dev/null || echo "fail")
  echo "${pm2_status}|${health}|${balance}|${earned}|${spent}|${txns}|${agent_id}"
}
REMOTE
  )

  if [[ -z "$RAW" || "$RAW" == *"SSH_FAIL"* ]]; then
    PM2="unreachable"; HEALTH="unreachable"; BAL="0"; EARN="0"; SPEND="0"; TXN="0"; AID=""
    ALERTS+="🔴 $NAME ($IP): SSH unreachable\n"
  else
    IFS='|' read -r PM2 HEALTH BAL EARN SPEND TXN AID <<< "$RAW"
    [[ "$PM2" != "online" ]] && ALERTS+="🟡 $NAME: PM2=$PM2\n"
    [[ "$HEALTH" != "ok" ]] && ALERTS+="🔴 $NAME: /health=$HEALTH\n"
  fi

  # Build JSON node object
  NODE_JSON="{\"name\":\"$NAME\",\"ip\":\"$IP\",\"pm2\":\"$PM2\",\"health\":\"$HEALTH\",\"balance\":$BAL,\"earned\":$EARN,\"spent\":$SPEND,\"txns\":$TXN,\"agent\":\"$AID\"}"
  if [[ "$RESULTS" == "[]" ]]; then
    RESULTS="[$NODE_JSON"
  else
    RESULTS="$RESULTS,$NODE_JSON"
  fi
done

RESULTS="$RESULTS]"
HAS_ALERT=$([[ -n "$ALERTS" ]] && echo "true" || echo "false")

# Append JSONL
echo "{\"ts\":\"$TS\",\"alert\":$HAS_ALERT,\"nodes\":$RESULTS}" >> "$LOG"

# Stdout for cron pickup (alerts go via OpenClaw delivery)
echo -e "[$TS] nodes=$(echo "$RESULTS" | python3 -c "
import sys,json
for n in json.load(sys.stdin):
  s='✅' if n['pm2']=='online' and n['health']=='ok' else '❌'
  print(f\"  {s} {n['name']} pm2={n['pm2']} health={n['health']} bal={n['balance']}\")" 2>/dev/null)"
[[ -n "$ALERTS" ]] && echo -e "ALERTS:\n$ALERTS"
exit 0
