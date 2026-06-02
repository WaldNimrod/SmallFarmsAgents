#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# SmallFarmsAgents — verify canonical local TCP ports (AOS standard)
#
# Expected: Postgres 5433 (Docker), Admin 5001 (optional), Viewer 8081 (optional)
# See: documentation/08-troubleshooting/DOCKER_SHARED_WORKSTATION.md
#
# Usage: ./scripts/check_canonical_local_ports.sh
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON="${ROOT}/.venv/bin/python3"
[[ -x "$PYTHON" ]] || PYTHON="$(command -v python3)"

check_port() {
  local port="$1"
  local name="$2"
  if "$PYTHON" -c "import socket; s=socket.socket(); s.settimeout(2); s.connect(('127.0.0.1',$port)); s.close()" 2>/dev/null; then
    echo "✓  $name (127.0.0.1:$port) — accepting connections"
    return 0
  fi
  echo "✗  $name (127.0.0.1:$port) — not reachable"
  return 1
}

echo "══ Canonical port check (SmallFarmsAgents) ══"
echo ""

PG_OK=0
check_port 5433 "PostgreSQL (Docker)" && PG_OK=1 || true

if [[ "$PG_OK" -eq 0 ]]; then
  echo ""
  echo "If using repo Docker Postgres, start with:"
  echo "  ./scripts/docker_postgres.sh start"
  echo "Then set DATABASE_URL per .env.example (port 5433)."
fi

echo ""
check_port 5001 "Admin UI (Flask)" || true
check_port 8081 "Public viewer" || true

echo ""
if [[ "$PG_OK" -eq 1 ]]; then
  echo "RESULT: Postgres OK — run: python -m alembic current && python -m organic_market_agent.db.check"
  exit 0
fi
echo "RESULT: Postgres not listening — fix environment before certified QA."
exit 1
