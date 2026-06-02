#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# SmallFarmsAgents — verify (and optionally bring up) canonical dev interfaces
#
# Checks: Postgres 5433, Admin 5001, Viewer 8081, db.check when DB reachable
# See: documentation/05-admin-and-operations/DEV_ENVIRONMENT_BRINGUP.md
#
# Usage:
#   ./scripts/verify_dev_stack.sh              # verify only
#   ./scripts/verify_dev_stack.sh --start-ui   # start admin + viewer if not listening, then verify
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

PYTHON="${ROOT}/.venv/bin/python3"
[[ -x "$PYTHON" ]] || PYTHON="$(command -v python3)"

export DATABASE_URL="${DATABASE_URL:-postgresql://oma:oma@127.0.0.1:5433/organic_market_agent}"

probe_tcp() {
  local port="$1"
  "$PYTHON" -c "import socket; s=socket.socket(); s.settimeout(2); s.connect(('127.0.0.1',$port)); s.close()" 2>/dev/null
}

http_code() {
  local port="$1"
  local path="${2:-/}"
  curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 "http://127.0.0.1:${port}${path}" 2>/dev/null || echo "000"
}

echo "══════════════════════════════════════════════════════════════"
echo " SmallFarmsAgents — verify_dev_stack.sh"
echo " DATABASE_URL (host/port only): postgresql://…@127.0.0.1:5433/…"
echo "══════════════════════════════════════════════════════════════"
echo ""

PG_OK=0
if probe_tcp 5433; then
  echo "✓  PostgreSQL listener on 127.0.0.1:5433"
  PG_OK=1
else
  echo "✗  PostgreSQL not reachable on 127.0.0.1:5433"
  echo "   Run: ./scripts/docker_postgres.sh start && ./scripts/docker_postgres.sh wait"
fi

if [[ "$PG_OK" -eq 1 ]]; then
  echo ""
  echo "── alembic current (before) ──"
  "$PYTHON" -m alembic current 2>&1 || true
  echo ""
  echo "── alembic upgrade head ──"
  if "$PYTHON" -m alembic upgrade head 2>&1; then
    echo "✓  migrations applied"
  else
    echo "✗  alembic upgrade failed — see DEV_ENVIRONMENT_BRINGUP.md"
  fi
  echo ""
  echo "── alembic current (after) ──"
  "$PYTHON" -m alembic current 2>&1 || true
  echo ""
  echo "── organic_market_agent.db.check ──"
  if "$PYTHON" -m organic_market_agent.db.check 2>&1; then
    echo "✓  db.check reported success"
  else
    echo "✗  db.check failed — seed data or Team 20 guidance may be required after migrations"
  fi
fi

if [[ "${1:-}" == "--start-ui" ]] && ! probe_tcp 5001; then
  echo ""
  echo "▶  Starting Admin (5001) …"
  bash "$SCRIPT_DIR/admin_server.sh" start || true
fi
if [[ "${1:-}" == "--start-ui" ]] && ! probe_tcp 8081; then
  echo "▶  Starting Viewer (8081) …"
  bash "$SCRIPT_DIR/viewer_server.sh" start || true
fi

echo ""
echo "── HTTP interfaces ──"
if probe_tcp 5001; then
  c=$(http_code 5001 /)
  echo "   Admin 5001  → HTTP $c  (expect 200 or 302 to /login)"
else
  echo "   Admin 5001  → not listening (./scripts/admin_server.sh start)"
fi

if probe_tcp 8081; then
  c=$(http_code 8081 /public_report.html)
  echo "   Viewer 8081 → HTTP $c  (/public_report.html)"
else
  echo "   Viewer 8081 → not listening (./scripts/viewer_server.sh start)"
fi

echo ""
if [[ "$PG_OK" -eq 1 ]] && probe_tcp 5001 && probe_tcp 8081; then
  echo "RESULT: All canonical TCP ports active — confirm HTTP codes above."
  exit 0
fi
echo "RESULT: Incomplete — follow DEV_ENVIRONMENT_BRINGUP.md"
exit 1
