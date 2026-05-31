#!/usr/bin/env bash
# wc_derivatives.sh — build 720px web derivatives of the watercolor crop masters.
# Recipe verified byte-for-byte against the shipped wc-radish.png derivative:
#   `sips -Z 720` (long-edge clamp, alpha preserved). No magick/pngquant needed.
#
# Usage: scripts/wc_derivatives.sh [slug ...]
#   no args → rebuild all known masters
#   args    → rebuild only the named slugs (e.g. `tomato cucumber`)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-1/HANDOFF_PACKAGE/design/assets"
DST="$ROOT/sfa_delivery/public_assets/img/crops"

slugs=("$@")
if [ ${#slugs[@]} -eq 0 ]; then
  slugs=(lettuce radish parsley dill tomato cucumber)
fi

mkdir -p "$DST"
for slug in "${slugs[@]}"; do
  master="$SRC/wc-$slug.png"
  out="$DST/wc-$slug.png"
  if [ ! -f "$master" ]; then
    echo "SKIP  wc-$slug — master missing ($master)"
    continue
  fi
  sips -Z 720 "$master" --out "$out" >/dev/null
  sz=$(stat -f%z "$out")
  dims=$(sips -g pixelWidth -g pixelHeight "$out" | awk '/pixelWidth|pixelHeight/{printf "%s ",$2}')
  echo "OK    wc-$slug.png → ${dims}(${sz} bytes)"
done
