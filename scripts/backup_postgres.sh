#!/usr/bin/env bash
# Full PostgreSQL backup (custom format) using DATABASE_URL from .env.
# Prefers Homebrew libpq pg_dump when not on PATH.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p backups
set -a
# shellcheck disable=SC1091
[ -f .env ] && . ./.env
set +a
if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "DATABASE_URL missing (.env)" >&2
  exit 1
fi
TS="$(date +%Y%m%d_%H%M%S)"
OUT="backups/oma_full_${TS}.dump"
PGDUMP=""
if command -v pg_dump >/dev/null 2>&1; then
  PGDUMP="pg_dump"
elif [[ -x "/opt/homebrew/opt/libpq/bin/pg_dump" ]]; then
  PGDUMP="/opt/homebrew/opt/libpq/bin/pg_dump"
else
  CAND="$(find /opt/homebrew/Cellar/libpq -name pg_dump -type f 2>/dev/null | head -1)"
  if [[ -n "$CAND" ]]; then
    PGDUMP="$CAND"
  fi
fi
if [[ -z "$PGDUMP" ]]; then
  echo "pg_dump not found. Install: brew install libpq && brew link --force libpq" >&2
  exit 1
fi
"$PGDUMP" "$DATABASE_URL" -Fc -f "$OUT"
echo "Wrote $OUT ($(du -h "$OUT" | cut -f1))"
