#!/usr/bin/env bash
# wc_derivatives.sh — build 720px web derivatives of the watercolor crop masters.
# Recipe: `sips -Z 720` (long-edge clamp, alpha preserved). No magick/pngquant needed.
#
# Master source order: CROP_ART_MASTERS/masters/ (new art) → HANDOFF_PACKAGE assets (original 4).
# Usage: scripts/wc_derivatives.sh [slug ...]
#   no args → rebuild all masters found in masters/ + the original 4
#   args    → rebuild only the named slugs (e.g. `tomato cucumber`)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_NEW="$ROOT/_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-1/CROP_ART_MASTERS/masters"
SRC_ORIG="$ROOT/_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-1/HANDOFF_PACKAGE/design/assets"
DST="$ROOT/sfa_delivery/public_assets/img/crops"

slugs=("$@")
if [ ${#slugs[@]} -eq 0 ]; then
  # all masters present in either source (basename wc-<slug>.png → slug)
  slugs=()
  for d in "$SRC_NEW" "$SRC_ORIG"; do
    [ -d "$d" ] || continue
    for f in "$d"/wc-*.png; do
      [ -f "$f" ] || continue
      b="$(basename "$f")"; s="${b#wc-}"; s="${s%.png}"
      case " ${slugs[*]:-} " in *" $s "*) ;; *) slugs+=("$s") ;; esac
    done
  done
fi

mkdir -p "$DST"
for slug in "${slugs[@]}"; do
  master="$SRC_NEW/wc-$slug.png"
  [ -f "$master" ] || master="$SRC_ORIG/wc-$slug.png"
  out="$DST/wc-$slug.png"
  if [ ! -f "$master" ]; then
    echo "SKIP  wc-$slug — master not found in masters/ or handoff"
    continue
  fi
  sips -Z 720 "$master" --out "$out" >/dev/null
  # Knock a filled cream ground out to alpha so the icon floats under mix-blend-mode:multiply
  # (no pasted square). Idempotent + no-op on already-transparent masters. Best-effort.
  python3 "$ROOT/scripts/wc_knockout.py" "$out" >/dev/null 2>&1 || true
  sz=$(stat -f%z "$out")
  echo "OK    wc-$slug.png (${sz} bytes)"
done
