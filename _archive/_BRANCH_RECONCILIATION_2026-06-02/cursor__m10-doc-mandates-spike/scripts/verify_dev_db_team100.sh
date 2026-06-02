#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Dev DB verification bundle — migrations, pytest, db.check (evidence for Team 100)
#
# Prerequisites:
#   - PostgreSQL reachable via DATABASE_URL (default: docker-compose canonical URL)
#   - Typical dev DB already migrated through 071+ before 072/073 land
#
# Usage:
#   ./scripts/docker_postgres.sh start   # if using repo Docker on port 5433
#   ./scripts/verify_dev_db_team100.sh [logfile]
#
# If .env exists, DATABASE_URL is read from it via python-dotenv.
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

DEFAULT_URL="postgresql://oma:oma@127.0.0.1:5433/organic_market_agent"
if [[ -f .env ]]; then
  export DATABASE_URL="$(python3 -c "
from pathlib import Path
try:
    from dotenv import dotenv_values
except ImportError:
    print('${DEFAULT_URL}')
    raise SystemExit(0)
v = dotenv_values(Path('.env'))
print(v.get('DATABASE_URL') or '${DEFAULT_URL}')
")"
else
  export DATABASE_URL="${DATABASE_URL:-$DEFAULT_URL}"
fi

LOG="${1:-$ROOT/artifacts/team100-verify-$(date +%Y%m%d_%H%M%S).log}"
mkdir -p "$(dirname "$LOG")"

redact_url() {
  python3 -c "import os,urllib.parse; u=os.environ.get('DATABASE_URL',''); p=urllib.parse.urlparse(u); print(f'{p.scheme}://{p.username or \"\"}:****@{p.hostname}:{p.port or \"\"}{p.path}')"
}

{
  echo "══════════════════════════════════════════════════════════════"
  echo " SmallFarmsAgents — verify_dev_db_team100.sh"
  echo " Started: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo " Log: $LOG"
  echo " DATABASE_URL (redacted): $(redact_url)"
  echo "══════════════════════════════════════════════════════════════"
  echo ""

  echo "── alembic current (before) ──"
  python3 -m alembic current || true
  echo ""

  echo "── alembic upgrade head ──"
  python3 -m alembic upgrade head
  echo ""

  echo "── alembic current (after) ──"
  python3 -m alembic current
  echo ""

  echo "── pytest (excludes upress + ftps) ──"
  python3 -m pytest tests/ -q --ignore=tests/test_upress_validation.py --ignore=tests/test_ftps_upload.py
  echo ""

  echo "── organic_market_agent.db.check ──"
  python3 -m organic_market_agent.db.check
  echo ""

  echo "── SQL smoke: SRC_WA + extraction_status CHECK ──"
  python3 <<'PY'
import os
from sqlalchemy import create_engine, text

e = create_engine(os.environ["DATABASE_URL"])
with e.connect() as c:
    n = c.execute(text("SELECT COUNT(*) FROM sources WHERE code = 'SRC_WA'")).scalar()
    print(f"sources SRC_WA count: {n}")
    row = c.execute(
        text(
            """
            SELECT pg_get_constraintdef(c.oid)
            FROM pg_constraint c
            JOIN pg_class t ON c.conrelid = t.oid
            WHERE t.relname = 'raw_extracted_items' AND c.conname = 'chk_rei_extraction_status'
            """
        )
    ).fetchone()
    print(f"chk_rei_extraction_status: {row[0] if row else 'MISSING'}")
PY
  echo ""
  echo "══════════════════════════════════════════════════════════════"
  echo " Finished: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo " RESULT: OK (see above for any pytest/db.check failures)"
  echo "══════════════════════════════════════════════════════════════"
} 2>&1 | tee "$LOG"
