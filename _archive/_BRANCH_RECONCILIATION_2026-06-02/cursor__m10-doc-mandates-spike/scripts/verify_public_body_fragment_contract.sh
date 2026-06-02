#!/usr/bin/env bash
# Fail if local publish output is missing the WordPress body fragment UI contract
# (combined-stats checkbox + per-filter stats wiring). Run after `run_publisher`.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BODY="${ROOT}/output/public/public_report_body.html"

if [[ ! -f "$BODY" ]]; then
  echo "Missing ${BODY}"
  echo "Run: python3 -m organic_market_agent run_publisher [--output-dir output/public]"
  exit 1
fi

needles=(
  sfaShowCombinedStats
  sfa-filter-row
  sfa-combined-option
  statsByFilter
  SFAGENT_COMBINED_ONLY
)
for n in "${needles[@]}"; do
  if ! grep -q "$n" "$BODY"; then
    echo "FAIL: ${BODY} missing expected marker: ${n}"
    echo "Your templates are newer than publish output. Regenerate:"
    echo "  python3 -m organic_market_agent run_publisher"
    exit 1
  fi
done

echo "OK: body fragment contract satisfied ($(wc -c < "$BODY" | tr -d ' ') bytes)"

# Optional: compare live fragment (bypass page cache). Example:
#   VERIFY_BODY_URL='https://www.nimrod.bio/wp-content/uploads/market/public_report_body.html?nocache=1' \
#     ./scripts/verify_public_body_fragment_contract.sh
if [[ -n "${VERIFY_BODY_URL:-}" ]]; then
  if ! command -v curl >/dev/null 2>&1; then
    echo "WARN: curl not installed; skipping remote check"
    exit 0
  fi
  tmp="$(mktemp)"
  trap 'rm -f "$tmp"' EXIT
  if ! curl -sfL "$VERIFY_BODY_URL" -o "$tmp"; then
    echo "FAIL: could not fetch VERIFY_BODY_URL=${VERIFY_BODY_URL}"
    exit 1
  fi
  for n in "${needles[@]}"; do
    if ! grep -q "$n" "$tmp"; then
      echo "FAIL: remote body missing: ${n}"
      echo "Re-upload: python3 -m organic_market_agent run_upload --output-dir output/public"
      echo "Then purge CDN/page cache and retry with a ?nocache= query on the fragment URL."
      exit 1
    fi
  done
  echo "OK: remote body at VERIFY_BODY_URL matches contract"
fi
