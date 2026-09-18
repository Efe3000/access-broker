#!/bin/bash
echo "=== SIMULATED AGENT REQUEST PATTERN ==="
echo "(This script issues the request sequence a prompt-injected AI agent"
echo " would produce. It uses curl to stand in for the agent's HTTP calls —"
echo " the control plane enforces on requests regardless of their origin,"
echo " so this validates the actual security boundary without requiring"
echo " a live LLM loop.)"
echo

echo "[1] Agent tries an unlisted path directly (no auth at all)"
curl -s -w "\nHTTP %{http_code}\n" localhost:8000/secrets
echo "--> Caught by: gateway whitelist (default-deny)"
echo

echo "[2] Agent tries a real resource with no token"
curl -s -w "\nHTTP %{http_code}\n" localhost:8000/records
echo "--> Caught by: gateway authentication (missing JWT)"
echo

echo "[3] Agent obtains a legitimately-scoped token (records:read only)..."
TOKEN=$(curl -s -X POST localhost:8001/token | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
echo "Token acquired. Now attempting a destructive action outside its scope:"
curl -s -w "\nHTTP %{http_code}\n" -H "Authorization: Bearer $TOKEN" localhost:8000/delete-records
echo "--> Caught by: OPA policy (routed to human approval; not auto-denied outright, not auto-allowed either)"
echo

echo "[4] No human approves in time..."
echo "(waiting out the approval timeout — proving fail-closed)"
sleep 35
echo "--> Result: denied by default, since silence is not consent"
echo

echo "[5] Agent, undeterred, hammers denied paths rapidly..."
for i in 1 2 3; do
  curl -s -o /dev/null -w "attempt $i: HTTP %{http_code}\n" localhost:8000/secrets
done
echo
echo "[6] Checking ITDR for the resulting alert..."
curl -s localhost:8003/alerts
echo
echo "=== Even though every individual request was already blocked,"
echo "    ITDR independently flags the repeated pattern. ==="
