---
id: DECISION_WP-UI-followup_2026-05-28_v1.0.0
from: team_00 (Principal — in-session)
to: [team_100]
date: 2026-05-28
type: DECISION
scope: SFA-S003-P002-WP-UI follow-up items A/B/C/D (post-closure cleanup)
status: AUTHORIZED
trigger: "team_100 surfaced 2 decisions per WP-UI follow-up handoff: (1) vendor/ deploy strategy; (2) hero-image generation priority."
---

# DECISION — WP-UI follow-up (vendor/ strategy + hero priority)

## §1. vendor/ deploy strategy → Option B

**Ruling:** `vendor/` stays gitignored; the deploy script runs
`composer install --no-dev` before the lftp mirror so every upload carries a
complete production-only dependency tree.

- Rejected Option A (commit vendor/ to main) — +50 MB repo footprint.
- Rejected Option C (sister `sfa-deploy` branch) — extra workflow surface.
- **Why:** smaller repo; avoids the WP-UI closure failure mode where
  "re-mirror from main" produced a vendor-less tree and broke prod ~60s.

Implemented: `scripts/ftp_deploy_sfa_ui.sh` (runs `composer install --no-dev
--optimize-autoloader`, verifies `vendor/`, then mirrors). Documented:
`documentation/05-admin-and-operations/UI_DEPLOY_RUNBOOK.md`.

## §2. Hero-image priority → both now

**Ruling:** team_100 authors prompts for **both** og-default (Item A) and the 8
module heroes (Item D) this session. team_00 runs them in an image-gen session.

- og-default prompt: `_COMMUNICATION/TEAM_100/MEDIA_PROMPT_og-default_v1.0.0.md`
  (3 variants) → routed via `MSG-team100-to-team_00-MEDIA-og-default-PROMPT-2026-05-28.md`
- module heroes prompt: `_COMMUNICATION/TEAM_100/MEDIA_PROMPT_module_heroes_v1.0.0.md`
  (8 prompts, slug-exact) → routed via
  `MSG-team100-to-team_00-MEDIA-module-heroes-PROMPT-2026-05-28.md`

## §3. Execution status (this session)

| Item | Type | Status |
|------|------|--------|
| A og-default prompt | prompt-routing | DONE (3 variants + MSG) |
| B CommunityFeed + sidebar | code | DONE (lint + render verified) |
| C deploy script + runbook | code/docs | DONE (Option B, syntax OK) |
| D hero img support + 8 prompts | code + prompt-routing | DONE (macro + CSS + render verified) |

Media generation pending team_00 (IR#1: team_100 does not generate media).
Visual deploy of A+D images deferred to a single bundled L-GATE_V pass once
images land (per IR#1/IR#3).
