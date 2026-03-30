#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# MyFarmAgents — Public Viewer Server
# Usage:
#   ./scripts/viewer_server.sh start
#   ./scripts/viewer_server.sh stop
#   ./scripts/viewer_server.sh restart
#   ./scripts/viewer_server.sh status
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

PORT=8765
HOST=127.0.0.1
OUTPUT_DIR="$PROJECT_ROOT/output/public"
PID_FILE="$PROJECT_ROOT/.run/viewer_server.pid"
LOG_FILE="$PROJECT_ROOT/.run/viewer_server.log"
VENV="$PROJECT_ROOT/.venv/bin/python"
URL="http://$HOST:$PORT/public_report.html"

mkdir -p "$PROJECT_ROOT/.run"

# ── helpers ──────────────────────────────────────────────────────────────────

is_running() {
  [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null
}

print_status() {
  if is_running; then
    echo "✅  Public Viewer — בפעולה (pid $(cat "$PID_FILE"))  →  $URL"
  else
    echo "⛔  Public Viewer — כבוי"
  fi
}

do_start() {
  if is_running; then
    echo "⚠️  Public Viewer כבר רץ (pid $(cat "$PID_FILE")). השתמש ב-restart להפעלה מחדש."
    return 0
  fi
  STALE=$(lsof -ti :"$PORT" 2>/dev/null || true)
  [[ -n "$STALE" ]] && { echo "🔪  מסיר תהליך ישן על פורט $PORT ($STALE)"; kill $STALE 2>/dev/null; sleep 1; }

  if [[ ! -d "$OUTPUT_DIR" ]]; then
    echo "⚠️  תיקיית הפלט לא קיימת: $OUTPUT_DIR"
    echo "    מריץ run_publisher ליצירת דוח ראשוני..."
    cd "$PROJECT_ROOT"
    [[ -f .env ]] && set -a && source .env && set +a
    "$VENV" -m organic_market_agent run_publisher --output-dir "$OUTPUT_DIR" \
      >> "$LOG_FILE" 2>&1 || true
  fi

  cd "$PROJECT_ROOT"
  [[ -f .env ]] && set -a && source .env && set +a

  nohup "$VENV" -m organic_market_agent run_viewer \
    --host "$HOST" --port "$PORT" --dir "$OUTPUT_DIR" \
    >> "$LOG_FILE" 2>&1 &
  echo $! > "$PID_FILE"
  sleep 2

  if is_running; then
    echo "🟢  Public Viewer הופעל (pid $(cat "$PID_FILE"))  →  $URL"
    echo "    לוג: $LOG_FILE"
  else
    echo "❌  הפעלת Public Viewer נכשלה — בדוק לוג: $LOG_FILE"
    tail -20 "$LOG_FILE" 2>/dev/null || true
    exit 1
  fi
}

do_stop() {
  if is_running; then
    PID=$(cat "$PID_FILE")
    kill "$PID" 2>/dev/null && echo "🔴  Public Viewer הופסק (pid $PID)" || true
    rm -f "$PID_FILE"
  else
    STALE=$(lsof -ti :"$PORT" 2>/dev/null || true)
    if [[ -n "$STALE" ]]; then
      kill $STALE 2>/dev/null
      echo "🔴  תהליך ישן על פורט $PORT הופסק ($STALE)"
    else
      echo "ℹ️   Public Viewer כבר כבוי"
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
