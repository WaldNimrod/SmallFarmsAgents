---
id: DEPLOY_MANDATE_SFA-S003-P002-WP-UI-patch02_v1.0.0
from: team_100 (Chief Architect)
to: team_99 (OPS — allowlisted network)
cc: team_00, team_10
date: 2026-05-29
type: deploy_mandate
wp: SFA-S003-P002-WP-UI-patch02 (+ WP-UI-patch01 media)
status: MANDATED
---

# Deploy Mandate — sfa.nimrod.bio (UI media + icon system)

team_100 cannot deploy from this machine: uPress FTPS (`ftp.s887.upress.link:21`)
**rejects this IP** (allowlist; lftp → "max-retries exceeded"). Per the same
constraint behind the prior patch01 deploy mandate, **team_99 deploys from an
allowlisted network**.

## What to deploy
Current `main` `sfa_delivery/` tree (build `08a0f9e`) — carries BOTH:
- WP-UI-patch01 brand media: 8 module heroes + hub-hero + og-default + favicon-32 + apple-touch-icon (wired in `modules.php` + `_layout.php`).
- WP-UI-patch02 icon system: `crop_card.php` + `book_crop.php` render `crops.icon_url` (watercolor) with SVG-sprite fallback.

## How
```
cd /path/to/SmallFarmsAgents && git checkout main && git pull
bash scripts/ftp_deploy_sfa_ui.sh        # Option B: composer install --no-dev + lftp mirror
```
Then smoke:
- `https://sfa.nimrod.bio/` 200; `/crop-book/` 200 (cards show SVG icons — watercolors are Phase 2).
- `https://sfa.nimrod.bio/public_assets/img/heroes/crop-book.webp` 200; `og-default.webp` 200; `favicon-32.png` 200.

## DB note
Migration `057` (crops.icon_url) is applied to the canonical oma-postgres. The
sfa.nimrod.bio app reads crops via the ingest API/MySQL mirror — `icon_url` is
NOT yet in that contract (Phase-2 plumbing). Phase-1 deploy renders SVG fallback,
so no DB/ingest change is required for this deploy.

## Report
Confirm deploy + smoke results → notify team_100 (closes AC-U2-06) and team_190
(live-deploy evidence for L-GATE_V).

— team_100 (Claude Opus 4.7) 2026-05-29
