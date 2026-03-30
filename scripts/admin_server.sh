#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# MyFarmAgents — Admin Dashboard Server
# Usage:
#   ./scripts/admin_server.sh start
#   ./scripts/admin_server.sh stop
#   ./scripts/admin_server.sh restart
#   ./scripts/admin_server.sh status
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

PORT=5001
HOST=127.0.0.1
PID_FILE="$PROJECT_ROOT/.run/admin_server.pid"
LOG_FILE="$PROJECT_ROOT/.run/admin_server.log"
VENV="$PROJECT_ROOT/.venv/bin/python"
URL="http://$HOST:$PORT"

mkdir -p "$PROJECT_ROOT/.run"

# ── helpers ──────────────────────────────────────────────────────────────────

is_running() {
  [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null
}

print_status() {
  if is_running; then
    echo "✅  Admin Dashboard — בפעולה (pid $(cat "$PID_FILE"))  →  $URL"
  else
    echo "⛔  Admin Dashboard — כבוי"
  fi
}

do_start() {
  if is_running; then
    echo "⚠️  Admin Dashboard כבר רץ (pid $(cat "$PID_FILE")). השתמש ב-restart להפעלה מחדש."
    return 0
  fi
  # Kill any stale process occupying the port
  STALE=$(lsof -ti :"$PORT" 2>/dev/null || true)
  [[ -n "$STALE" ]] && { echo "🔪  מסיר תהליך ישן על פורט $PORT ($STALE)"; kill $STALE 2>/dev/null; sleep 1; }

  cd "$PROJECT_ROOT"
  # shellcheck disable=SC1091
  [[ -f .env ]] && set -a && source .env && set +a

  nohup "$VENV" -m organic_market_agent run_admin --host "$HOST" --port "$PORT" \
    >> "$LOG_FILE" 2>&1 &
  echo $! > "$PID_FILE"
  sleep 2

  if is_running; then
    echo "🟢  Admin Dashboard הופעל (pid $(cat "$PID_FILE"))  →  $URL"
    echo "    לוג: $LOG_FILE"
  else
    echo "❌  הפעלת Admin Dashboard נכשלה — בדוק לוג: $LOG_FILE"
    tail -20 "$LOG_FILE" 2>/dev/null || true
    exit 1
  fi
}

do_stop() {
  if is_running; then
    PID=$(cat "$PID_FILE")
    kill "$PID" 2>/dev/null && echo "🔴  Admin Dashboard הופסק (pid $PID)" || true
    rm -f "$PID_FILE"
  else
    # Kill any process still on the port even without a pid file
    STALE=$(lsof -ti :"$PORT" 2>/dev/null || true)
    if [[ -n "$STALE" ]]; then
      kill $STALE 2>/dev/null
      echo "🔴  תהליך ישן על פורט $PORT הופסק ($STALE)"
    else
      echo "ℹ️   Admin Dashboard כבר כבוי"
    fi
    rm -f "$PID_FILE"
  fi
}

# ── dispatch ─────────────────────────────────────────────────────────────────

CMD="${1:-status}"

case "$CMD" in
  start)   do_start ;;
  stop)    do_stop ;;
  restart) do_stop; sleep 1; do_start ;;
  status)  print_status ;;
  *)
    echo "שימוש: $0 {start|stop|restart|status}"
    exit 1
    ;;
esac
