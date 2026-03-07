#!/usr/bin/env bash
# MELD Network Health Monitor
# Runs hourly via cron, logs to memory/meld-health-log.md

LOG="/data/.openclaw/workspace/memory/meld-health-log.md"
TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M UTC")

# Bootstrap nodes (always check)
BOOTSTRAP_IPS="147.93.72.73 72.61.53.248 76.13.198.23 187.77.177.78"

# Discover registered agents from meld-2's registry
REGISTERED=$(ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@147.93.72.73 'cd /root/meld-install && node -e "const D=require(\"better-sqlite3\");const db=new D(require(\"os\").homedir()+\"/.meld/meld.db\");const r=db.prepare(\"SELECT agent_id,host,port FROM registry_peers WHERE status=\\\"active\\\"\").all();console.log(JSON.stringify(r));"' 2>/dev/null)

TOTAL=0
UP=0
DOWN_LIST=""

# Check bootstrap nodes
for ip in $BOOTSTRAP_IPS; do
  TOTAL=$((TOTAL+1))
  if curl -s --connect-timeout 5 "http://$ip:9377/v1/health" | grep -q '"ok"' 2>/dev/null; then
    UP=$((UP+1))
  else
    DOWN_LIST="$DOWN_LIST $ip:9377"
  fi
done

# Check non-bootstrap registered nodes
if [ -n "$REGISTERED" ] && [ "$REGISTERED" != "[]" ]; then
  EXTRA_HOSTS=$(echo "$REGISTERED" | node -e "
    const d=require('fs').readFileSync('/dev/stdin','utf8');
    const peers=JSON.parse(d);
    const bootstrap=['147.93.72.73','72.61.53.248','76.13.198.23','187.77.177.78'];
    peers.filter(p=>!bootstrap.includes(p.host)).forEach(p=>console.log(p.host+':'+p.port));
  " 2>/dev/null)
  
  for hp in $EXTRA_HOSTS; do
    TOTAL=$((TOTAL+1))
    if curl -s --connect-timeout 5 "http://$hp/v1/health" | grep -q '"ok"' 2>/dev/null; then
      UP=$((UP+1))
    else
      DOWN_LIST="$DOWN_LIST $hp"
    fi
  done
fi

# Log result
ENTRY="| $TIMESTAMP | $UP/$TOTAL |"
if [ -n "$DOWN_LIST" ]; then
  ENTRY="$ENTRY down:$DOWN_LIST |"
else
  ENTRY="$ENTRY all healthy |"
fi

# Create log file if needed
if [ ! -f "$LOG" ]; then
  echo "# MELD Health Log" > "$LOG"
  echo "" >> "$LOG"
  echo "| Timestamp | Nodes | Status |" >> "$LOG"
  echo "|-----------|-------|--------|" >> "$LOG"
fi

echo "$ENTRY" >> "$LOG"

# Output for cron job
if [ -n "$DOWN_LIST" ]; then
  echo "ALERT: $DOWN_LIST down ($UP/$TOTAL healthy)"
else
  echo "OK: $UP/$TOTAL healthy"
fi
