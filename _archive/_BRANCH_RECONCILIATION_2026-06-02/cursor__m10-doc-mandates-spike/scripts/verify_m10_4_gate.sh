#!/usr/bin/env bash
# Team 10 self-check before Team 50 re-QA (M10.4 + M13-PRE) — mirrors QA_MANDATE_M10_4_TEAM50 T03/T05/T06/T08 subset.
# T04 is not asserted here; run mandate SQL by hand. M13-PRE G-PRE-1 aligns with >=5 priority sources
# having raw rows (this script) and normalized_observations (printed below). Expect Alembic head 066+ after upgrade.
# G-PRE-5: published product count default min 90; if Team 100 waives structural shortfall, run with
#   M13_PRE_GPRE5_WAIVED=1 to allow counts below 90 (script still prints the actual count).
# Usage: from repo root, with DATABASE_URL in .env or env:
#   chmod +x scripts/verify_m10_4_gate.sh
#   ./scripts/verify_m10_4_gate.sh
# Optional: PYTHON=python3.11  CURL_LIVE=1

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PYTHON="${PYTHON:-python3}"
export PYTHONPATH="${ROOT}${PYTHONPATH:+:$PYTHONPATH}"

echo "=== M10.4 gate self-check (Python: $PYTHON) ==="

if [[ ! -f "${ROOT}/.env" ]] && [[ -z "${DATABASE_URL:-}" ]]; then
  echo "WARN: No .env and DATABASE_URL unset — SQL and publish steps may skip."
fi

echo ""
echo ">>> T06 / AC6: full pytest"
"$PYTHON" -m pytest tests/ -q

echo ""
echo ">>> T07 / AC7: mypips parser unit tests"
"$PYTHON" -m pytest tests/test_mypips_parser.py -q

echo ""
echo ">>> T03: priority sources raw_extracted_items counts (SQL)"
"$PYTHON" <<PY
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv(Path("${ROOT}") / ".env")
url = os.environ.get("DATABASE_URL")
if not url:
    print("SKIP: DATABASE_URL not set")
    sys.exit(0)

sql = text(
    """
SELECT s.code, COUNT(rei.id) AS raw_rows
FROM raw_extracted_items rei
JOIN source_fetch_runs sfr ON sfr.id = rei.source_fetch_run_id
JOIN sources s ON s.id = sfr.source_id
WHERE s.code IN (
  'SRC041', 'SRC042', 'SRC053', 'SRC055', 'SRC060',
  'SRC061', 'SRC062', 'SRC069', 'SRC070'
)
GROUP BY s.code
ORDER BY s.code;
"""
)
eng = create_engine(url)
sql_gpre1 = text(
    """
SELECT s.code, COUNT(DISTINCT no.id) AS norm_obs
FROM sources s
LEFT JOIN normalized_observations no ON no.source_id = s.id
WHERE s.code IN (
  'SRC041', 'SRC042', 'SRC053', 'SRC055', 'SRC060',
  'SRC061', 'SRC062', 'SRC069', 'SRC070'
)
GROUP BY s.code
ORDER BY s.code
"""
)
with eng.connect() as conn:
    rows = conn.execute(sql).fetchall()
    for r in rows:
        print(f"  {r[0]}: {r[1]}")
    with_gt0 = sum(1 for r in rows if r[1] > 0)
    print(f"T03 distinct_with_rows_gt0 = {with_gt0} (M13-PRE / PRE-D5 need >= 5)")
    if with_gt0 < 5:
        sys.exit(1)

    rows2 = conn.execute(sql_gpre1).fetchall()
    for r in rows2:
        print(f"  G-PRE-1 {r[0]}: normalized_observations={r[1]}")
    gpre1_ok = sum(1 for r in rows2 if r[1] > 0)
    print(f"G-PRE-1 sources_with_normalized_observations = {gpre1_ok} (need >= 5)")
    if gpre1_ok < 5:
        sys.exit(1)
PY

echo ""
echo ">>> T05: catalog_renormalize (no publish) + run_publisher + product count"
"$PYTHON" -m organic_market_agent catalog_renormalize --skip-publish
"$PYTHON" -m organic_market_agent run_publisher
COUNT=$("$PYTHON" -c "import json; d=json.load(open('output/public/public_report.json')); print(len(d.get('products',[])))")
echo "T05 products_count = $COUNT (G-PRE-5 mandate >= 90)"
if [[ "$COUNT" -lt 90 ]]; then
  if [[ "${M13_PRE_GPRE5_WAIVED:-}" == "1" ]]; then
    echo "WARN: M13_PRE_GPRE5_WAIVED=1 — continuing despite count < 90 (Team 100 waiver on file for QA)."
  else
    echo "FAIL: product count below 90 — fix publish buckets, relax rolling window, or obtain Team 100 G-PRE-5 waiver and re-run with M13_PRE_GPRE5_WAIVED=1."
    exit 1
  fi
fi

if [[ "${CURL_LIVE:-}" == "1" ]]; then
  echo ""
  echo ">>> T08: live HTTP (optional)"
  curl -sL -o /dev/null -w "www: %{http_code}\n" "https://www.nimrod.bio/smallfarmsagent/" || true
  curl -sL -o /dev/null -w "apex: %{http_code}\n" "https://nimrod.bio/smallfarmsagent/" || true
fi

echo ""
echo "=== Self-check finished ==="
