#!/usr/bin/env bash
set -euo pipefail

PORT="${STREAMLIT_SMOKE_PORT:-8501}"
LOG_FILE="${RUNNER_TEMP:-/tmp}/streamlit-smoke.log"

streamlit run app.py \
  --server.headless true \
  --server.port "$PORT" \
  --browser.gatherUsageStats false \
  >"$LOG_FILE" 2>&1 &
APP_PID=$!

cleanup() {
  kill "$APP_PID" 2>/dev/null || true
}
trap cleanup EXIT

for attempt in {1..30}; do
  if curl --fail --silent "http://127.0.0.1:${PORT}/_stcore/health" | grep -q "ok"; then
    echo "Streamlit smoke test passed."
    exit 0
  fi
  sleep 1
done

echo "Streamlit failed to become healthy."
cat "$LOG_FILE"
exit 1
