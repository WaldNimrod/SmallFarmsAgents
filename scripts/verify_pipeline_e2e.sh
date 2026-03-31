#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# E2E smoke: real HTTP fetch → parse → normalize → aggregate → publish artifacts.
#
# PublishEngine requires ≥2 distinct community sources for the report date; this
# script ingests two active community sources (default SRC002 + SRC003), then
# aggregate + publish, then checks output/public JSON.
#
# Usage (from repo root, .env with DATABASE_URL):
#   bash scripts/verify_pipeline_e2e.sh
#   COMMUNITY_SRC1=SRC002 COMMUNITY_SRC2=SRC004 bash scripts/verify_pipeline_e2e.sh
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

PY="${ROOT}/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  echo "ERROR: expected venv at $PY"
  exit 1
fi

# shellcheck disable=SC1091
[[ -f .env ]] && set -a && source .env && set +a

COMMUNITY_SRC1="${COMMUNITY_SRC1:-SRC002}"
COMMUNITY_SRC2="${COMMUNITY_SRC2:-SRC003}"

echo "▶ Ingestion + normalize: $COMMUNITY_SRC1"
"$PY" -m organic_market_agent run_ingestion --run-type manual --source-code "$COMMUNITY_SRC1" --normalize
echo "▶ Ingestion + normalize: $COMMUNITY_SRC2"
"$PY" -m organic_market_agent run_ingestion --run-type manual --source-code "$COMMUNITY_SRC2" --normalize
echo "▶ Aggregator (today UTC)"
"$PY" -m organic_market_agent run_aggregator
echo "▶ Publisher → output/public"
"$PY" -m organic_market_agent run_publisher

MAN="${ROOT}/output/public/manifest.json"
REP="${ROOT}/output/public/public_report.json"
[[ -f "$MAN" && -f "$REP" ]] || { echo "ERROR: missing publish artifacts"; exit 1; }

"$PY" - << PY
import json
from pathlib import Path
m = json.loads(Path("${MAN}").read_text(encoding="utf-8"))
r = json.loads(Path("${REP}").read_text(encoding="utf-8"))
cs = int(m.get("community_sources") or 0)
pc = int(m.get("product_count") or 0)
n = len(r.get("products") or [])
assert cs >= 2, f"expected community_sources>=2, got {cs}"
assert pc == n, f"manifest product_count {pc} != report products {n}"
assert pc > 0, "expected at least one product in public report"
print(f"OK manifest: community_sources={cs} product_count={pc} staleness={m.get('staleness_level')}")
PY

echo "✅ E2E verify_pipeline_e2e.sh passed (artifacts under output/public/)"
