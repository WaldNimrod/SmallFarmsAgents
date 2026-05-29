---
id: AC-U2-06_CLOSED_SFA-S003-P002-WP-UI-patch02_v1.0.0
from: team_100 (Chief Architect)
to: team_00, team_190
cc: team_99
date: 2026-05-29
type: ac_closure
wp: SFA-S003-P002-WP-UI-patch02
ac: AC-U2-06 (live deploy to sfa.nimrod.bio)
status: CLOSED
---

# AC-U2-06 CLOSED — brand media live on sfa.nimrod.bio

The one deferred acceptance criterion (live deploy) is fulfilled.

## Deploy
- team_99 deployed from **waldhomeserver** (egress 46.235.231.114, now allowlisted on uPress **s1240**) — `scripts/ftp_deploy_sfa_ui.sh`, clean lftp, **97 files**, deploy commit `2d5cbbb`. Report: `_COMMUNICATION/team_99/SFA-S003-P002-WP-UI-patch02/DEPLOY_REPORT_v1.0.0.md`.
- Host correction applied this session: `ftp.s1240.upress.link` (sfa UI), not `ftp.s887.upress.link` (old market). Allowlist on s1240 unblocked it.

## team_100 independent verification (2026-05-29)
| URL | code | content-type |
|-----|------|--------------|
| sfa.nimrod.bio/ | 200 | text/html |
| sfa.nimrod.bio/crop-book/ | 200 | text/html |
| /public_assets/img/heroes/crop-book.webp | 200 | image/webp |
| /public_assets/img/heroes/market.webp | 200 | image/webp |
| /public_assets/img/og-default.webp | 200 | image/webp |
| /public_assets/img/hub-hero.webp | 200 | image/webp |
| /public_assets/img/favicon-32.png | 200 | image/png |
| /public_assets/img/apple-touch-icon.png | 200 | image/png |

All 200 with correct MIME types. Brand media (8 module heroes + hub-hero +
og-default + favicons) is **live**. /crop-book/ renders (crop cards show SVG
fallback icons — watercolor crop art is Phase 2).

## Disposition
WP-UI-patch02 was already LOD500_LOCKED (L-GATE_V PASS, Composer 2.5). AC-U2-06
was the last deferred item — now CLOSED. WP-UI-patch02 Phase 1 is fully complete
and live. team_190 may append a live-deploy confirmation per §5 of the deploy
report (optional — operational, not a gate reopen).

## Phase 2 (carried, non-blocking)
(a) `icon_url` in the sfa ingest contract + uPress MySQL schema; (b) external
image-gen of the 70 watercolors per MEDIA_PROMPT_crop_icons_v1.0.0 → backfill
`crops.icon_url` → deploy. Until then the UI renders SVG fallback for all 70.

— team_100 (Claude Opus 4.7) 2026-05-29
