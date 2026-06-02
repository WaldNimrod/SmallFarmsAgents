#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# SmallFarmsAgents — PostgreSQL (Docker) — fixed dev ports
#
# Canonical dev DB (see docker-compose.yml):
#   Host:     127.0.0.1
#   Port:     5433  (host) → 5432 (container) — DO NOT change without updating
#             .env / .env.example / this script / Team docs.
#   Database: organic_market_agent
#   User:     oma
#   Password: oma
#
# Usage:
#   ./scripts/docker_postgres.sh start    # docker compose up -d postgres
#   ./scripts/docker_postgres.sh stop     # docker compose stop postgres
#   ./scripts/docker_postgres.sh down     # docker compose down (removes container)
#   ./scripts/docker_postgres.sh restart
#   ./scripts/docker_postgres.sh status   # ps + pg_isready inside container
#   ./scripts/docker_postgres.sh wait     # block until DB accepts connections
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

COMPOSE=(docker compose)
if ! docker compose version &>/dev/null; then
  COMPOSE=(docker-compose)
fi

SERVICE="postgres"
CONTAINER="oma-postgres"
HOST_PORT="5433"

cmd="${1:-status}"

case "$cmd" in
  start)
    echo "▶  Starting PostgreSQL ($CONTAINER) on host port $HOST_PORT ..."
    if ! out="$("${COMPOSE[@]}" up -d "$SERVICE" 2>&1)"; then
      echo "$out"
      if echo "$out" | grep -q 'port is already allocated'; then
        echo ""
        echo "✗  Host port $HOST_PORT is already bound (another Postgres or old container)."
        echo "    Check:  docker ps    and    lsof -nP -iTCP:$HOST_PORT -sTCP:LISTEN"
        echo "    If a stale $CONTAINER exists:  docker rm -f $CONTAINER  then retry."
        echo "    Or point DATABASE_URL at the instance that already owns :$HOST_PORT."
      fi
      exit 1
    fi
    echo "$out"
    "$0" wait
    echo "✓  Ready. DATABASE_URL:"
    echo "   postgresql://oma:oma@127.0.0.1:${HOST_PORT}/organic_market_agent"
    ;;
  stop)
    echo "▶  Stopping $SERVICE ..."
    "${COMPOSE[@]}" stop "$SERVICE" || true
    ;;
  down)
    echo "▶  docker compose down (postgres volume kept unless -v) ..."
    "${COMPOSE[@]}" down
    ;;
  restart)
    "$0" stop
    "$0" start
    ;;
  wait)
    echo "▶  Waiting for Postgres on :$HOST_PORT ..."
    for i in $(seq 1 60); do
      if command -v pg_isready &>/dev/null; then
        if pg_isready -h 127.0.0.1 -p "$HOST_PORT" -U oma -d organic_market_agent &>/dev/null; then
          echo "✓  pg_isready OK"
          exit 0
        fi
      elif docker exec "$CONTAINER" pg_isready -U oma -d organic_market_agent &>/dev/null; then
        echo "✓  pg_isready (inside container) OK"
        exit 0
      fi
      sleep 1
    done
    echo "✗  Timeout waiting for database"
    exit 1
    ;;
  status)
    echo "══ Docker / $CONTAINER ══"
    docker ps -a --filter "name=^/${CONTAINER}$" --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' 2>/dev/null || true
    if docker exec "$CONTAINER" pg_isready -U oma -d organic_market_agent &>/dev/null; then
      echo "✓  pg_isready: accepting connections"
    else
      echo "✗  pg_isready: not ready (start with: $0 start)"
    fi
    ;;
  *)
    echo "Usage: $0 {start|stop|down|restart|status|wait}"
    exit 1
    ;;
esac
