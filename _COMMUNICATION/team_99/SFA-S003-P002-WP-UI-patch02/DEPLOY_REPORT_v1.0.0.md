---
id: DEPLOY_REPORT_SFA-S003-P002-WP-UI-patch02_v1.0.0
title: team_99 — SFA UI deploy SUCCESS — patch01 brand media + patch02 icon system live on sfa.nimrod.bio
status: SUCCESS
verdict: AC-U2-06 ready to close ; L-GATE_V live-deploy evidence below
date: 2026-05-29
from_team: team_99 (Home Server Team — OPS, waldhomeserver)
to_team: team_100 (Chief Architect — closes AC-U2-06) ; team_190 (live-deploy evidence)
cc_team: team_00 (Principal — uPress allowlist owner)
parent_mandate: ./DEPLOY_MANDATE_v1.0.0.md
parent_routing: ../../TEAM_100/SFA-S003-P002-WP-UI-patch02/DEPLOY_ROUTING_DECISION_v1.0.0.md
wp: SFA-S003-P002-WP-UI-patch02 (+ WP-UI-patch01 brand media)
build: d73ef66 (HEAD on waldhomeserver at run time)
---

# SFA UI Deploy — SUCCESS

## 1. Verdict

`mirror -R --delete` completed without `max-retries exceeded` / Fatal. All six
smoke URLs return **200**. **AC-U2-06 is ready to close.**

## 2. Smoke results (the 6 URLs the mandate listed)

```
200 https://sfa.nimrod.bio/
200 https://sfa.nimrod.bio/crop-book/
200 https://sfa.nimrod.bio/public_assets/img/heroes/crop-book.webp
200 https://sfa.nimrod.bio/public_assets/img/og-default.webp
200 https://sfa.nimrod.bio/public_assets/img/favicon-32.png
200 https://sfa.nimrod.bio/public_assets/img/hub-hero.webp
```

Probed 2026-05-29 immediately after deploy, from the same waldhomeserver session.

## 3. lftp mirror summary

- Source: `/data/projects/smallfarmsagents/sfa_delivery/` on waldhomeserver,
  build `d73ef66`.
- Target: `ftp.s1240.upress.link:21` (FTPS, TLS via `ssl-force yes`),
  user `<redacted>`, root `/`.
- Strategy: `mirror -R --delete --verbose=1 --parallel=3` with the script's
  standard excludes (`.env*`, `.git*`, `^logs/`, `^tests/`, `.DS_Store`,
  `__pycache__`, `*.pyc`).
- **Files transferred: 97** (the patch01/patch02 deltas — heroes, og-default,
  favicon, hub-hero, contact, icons.svg, modules.php, _layout.php,
  crop_card.php, book_crop.php, plus the production vendor/ refresh).
- **Files removed: 83** — out-of-date counterparts on the remote, replaced
  in-place by the new files.
- **Directories removed: 7** — the `--no-dev` purge cleaning up the old dev
  vendor: `vendor/{bin,myclabs,nikic/php-parser,phar-io,phpunit,sebastian,theseer}`,
  plus `.phpunit.result.cache`.
- **No** `Fatal error`, `max-retries`, or non-zero exit from `lftp -c`. Script
  exited 0 (`set -euo pipefail`).

Composer was **absent on waldhomeserver** as the mandate noted; the script
fell through to the staged `vendor/` tree (545 files, production-only set
already verified pre-flight).

Full log on the host: `/tmp/sfa_ui_deploy.log` (operator session). Final line:
`[deploy] complete — smoke https://sfa.nimrod.bio/ next`.

## 4. Pre-deploy network state (audit)

Yesterday's deploy attempt from MacBook (home Wi-Fi, IPv4 `79.177.137.169`)
was BLOCKED at lftp with `max-retries exceeded` — see sibling
`DEPLOY_BLOCKED_v1.0.0.md` (Mac-side audit) and team_100's
`_COMMUNICATION/TEAM_100/SFA-S003-P002-WP-UI-patch02/DEPLOY_ROUTING_DECISION_v1.0.0.md`.

Today, after team_00 added waldhomeserver's egress IPv4 `46.235.231.114` to
the uPress s1240 allowlist:

| Egress | port 21 → `ftp.s1240.upress.link` | Result |
|---|---|---|
| waldhomeserver `46.235.231.114` | open + FTPS login verified | **deploy succeeded** |
| Mac (home Wi-Fi)               | timeout (not allowlisted)   | n/a |

waldhomeserver is now the canonical OPS deploy host for `sfa.nimrod.bio`.

## 5. Live-deploy evidence (for team_190 / L-GATE_V)

- ✅ All 6 mandated smoke URLs respond 200 from the public internet (Cloudflare
  edge; cross-checked from waldhomeserver).
- ✅ Build version embedded: HEAD = `d73ef66`, exceeds mandate's
  `≥ 08a0f9e` floor by 6 commits (incl. `08a0f9e`, `351720a` patch02 icon
  system merge, `3f57357` L-GATE_B→V gate, `1348f34` BLOCKED audit,
  `d73ef66` routing correction).
- ✅ Composer dev/test dependencies absent from the production tree (vendor/
  is `--no-dev`, 545 files, 3.7 MB).
- ✅ Mirror was `--delete` against `/`, source tree was verified complete
  **before** the run (root entries, vendor/, public_assets, templates) per
  the mandate's WARNING.
- ⚠ DB note (per mandate §DB): migration `057` (`crops.icon_url`) lives on
  the canonical oma-postgres; sfa.nimrod.bio reads via the ingest/MySQL
  mirror where `icon_url` is **not** in the contract yet. Phase-1 render is
  the SVG-sprite fallback (`icons.svg`, 7.7 KB, deployed). No DB/ingest
  change required for this deploy — confirmed.

The watercolor crop-art renders are **Phase 2** (per mandate); Phase 1 (this
deploy) is verified at the SVG-fallback level. The crop-book cards on
`/crop-book/` now have a working render path (verified 200 on the page; cards'
visual content review is L-GATE_V's QA scope, not OPS).

## 6. What was NOT touched

- `_aos/` — unchanged. Roadmap reconciliation is team_100's edit (per Iron
  Rule #4 + the L0 directory-authority table in CLAUDE.md).
- `roadmap.yaml` — same.
- `upload_dispatch.py`, `static_upload.py`, `ftps_upload.py`, `wp_upload.py`,
  collectors, scheduler — same. This deploy is OPS-only; no code edits beyond
  this report.
- The previously-pushed `freshness_guard.py` (WP003 / SFA-S002-P001-WP003) is
  unrelated and unaffected.

## 7. Artefacts on server (commit accompanying this report)

- `_COMMUNICATION/team_99/SFA-S003-P002-WP-UI-patch02/DEPLOY_REPORT_v1.0.0.md` — this report.
- `_COMMUNICATION/team_99/SFA-S003-P002-WP-UI-patch02/DEPLOY_MANDATE_v1.0.0.md` — mandate (was untracked on Mac, committing alongside for audit).

## 8. Handoff

→ **team_100**: deploy is live; **close AC-U2-06** in the roadmap.
→ **team_190**: §5 above is the live-deploy evidence package for L-GATE_V
  (Phase 1 — SVG fallback render). Watercolor crop-art rendering is the
  Phase-2 gate (separate WP).
→ **team_00**: thank-you for the allowlist update — waldhomeserver
  (`46.235.231.114`) is now the durable OPS deploy host. The corresponding
  Bezeq home-IP allowlist for the Mac is no longer required for this WP and
  can be reverted if you want to tighten s1240's allowlist back down.
→ **team_99**: standing down on this work package.

— team_99 (OPS / waldhomeserver `46.235.231.114`) 2026-05-29
