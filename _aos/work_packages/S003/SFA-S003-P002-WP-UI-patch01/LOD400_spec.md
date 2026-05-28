# LOD400 Spec — SFA-S003-P002-WP-UI-patch01

**WP-UI post-closure follow-up wave (items A/B/C/D)**
Track: A | Profile: L0 | Effort: SMALL | Risk: LOW

- **Author:** team_100 (Chief System Architect)
- **Version:** v1.0.0
- **Date:** 2026-05-28
- **Parent:** SFA-S003-P002-WP-UI (LOD500_LOCKED, archived) — this patch addresses
  the 4 known follow-ups (B1 og-default, sidebar feed hook, deploy-script
  codification, module hero slot) deferred at closure.
- **team_00 authorization:** in-session 2026-05-28 + DECISION_WP-UI-followup
  (`_COMMUNICATION/team_00/DECISION_WP-UI-followup_2026-05-28_v1.0.0.md`)
  - vendor/ deploy strategy = **Option B** (composer install at deploy)
  - hero priority = **both** (og-default + 8 module heroes)
  - build ownership = **Sonnet adopts team_100 draft** as L-GATE_B build
  - WP registration = **yes**

## §0. Orchestration model (team_00 directive 2026-05-28)

| Role | Team | Engine | Gate |
|------|------|--------|------|
| Build | team_10 (sfa_build) | Claude **Sonnet** | L-GATE_B |
| QA / functional acceptance | team_50 | Claude **Haiku** | QA pass (pre-V) |
| Constitutional validation | team_190 | **non-Claude** (GPT-5.5/Cursor/Codex) | L-GATE_V |

IR#1 cross-engine: builder (Sonnet) ≠ L-GATE_V validator (non-Claude). Haiku QA
is an intermediate functional-acceptance pass, not the constitutional gate.

## §1. Reference draft (binding starting point)

team_100 authored + verified a complete draft of items B/C/D in-session.
Captured at `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-UI-patch01/team100_draft.diff`
(also present in the working tree). The builder **adopts, reviews, refines, and
produces the canonical L-GATE_B commit** — it is NOT a from-scratch build.

## §2. Scope

### Item A — og-default Open Graph image (prompt-routing + integration)
- `_layout.php` already references `og:image =
  https://sfa.nimrod.bio/public_assets/img/og-default.webp` with `$og_image_url`
  override. The default file is missing.
- team_100 prompt artifacts (DONE):
  `_COMMUNICATION/TEAM_100/MEDIA_PROMPT_og-default_v1.0.0.md` (3 variants) +
  routing MSG to team_00.
- **Image generation is team_00's (external).** Integration (placing the WebP +
  deploy) is deferred until the asset lands → tracked as a deferred sub-item, not
  a blocker for this patch's code closure.

### Item B — Community feed read hook (CODE)
- New `sfa_delivery/app/Lib/CommunityFeed.php` — `SFA\Lib\CommunityFeed::recent(int $limit = 3): array`
  returning feed_item-shaped rows (kind/author_he/region_he/date_he/text_he/
  tag_he/upvotes).
- Source: `sfa_delivery/data/community_feed.json` (team_00 maintained), with a
  curated static fallback if the file is missing/invalid.
- Wire into `sfa_delivery/templates/shell/desktop.php` `dt-acc--comm` block:
  loop `recent(3)` → `macros/feed_item.php`. **Desktop only** (mobile has no sidebar).
- **READ-ONLY.** No POST, no DB write, no `community_contributions` table, no
  `CommunityController`. This is consistent with the parent WP-UI "no community
  write surfaces" constraint — it is a curated read feed, explicitly authorized
  by team_00 in the follow-up handoff (Item B).

### Item C — Deploy-script codification (CODE/DOCS)
- New `scripts/ftp_deploy_sfa_ui.sh` per **Option B**: load `.env` → `composer
  install --no-dev --optimize-autoloader` in source tree → verify `vendor/`
  present → `lftp mirror -R --delete` to `SFA_FTP_ROOT`. Uses real env vars
  `SFA_FTP_HOST/PORT/USER/PASS/ROOT` (`.env.example` lines 75-87).
- `vendor/` stays gitignored (Option B). Never "re-mirror from main".
- Document in `documentation/05-admin-and-operations/UI_DEPLOY_RUNBOOK.md`.

### Item D — Module hero image slot (CODE) + prompt-routing
- `sfa_delivery/templates/macros/module_card.php`: accept `$module['hero_url']`,
  emit `<img class="mod-card__hero" loading="lazy" decoding="async">` when set.
- `sfa_delivery/public_assets/css/hub.css`: add `.mod-card__hero` cover rule
  (full-bleed `object-fit:cover`). Existing `:has()` rule already reverts the
  icon to a corner badge when an image is present.
- team_100 prompt artifacts (DONE):
  `_COMMUNICATION/TEAM_100/MEDIA_PROMPT_module_heroes_v1.0.0.md` (8 slug-exact
  prompts) + routing MSG.
- Setting `hero_url` per module in `modules.php` + image deploy deferred until
  the 8 WebP assets land (team_00 external) → deferred sub-item.

## §3. Out of scope / locked files

- No changes to LOD500_LOCKED parent WP-UI files beyond the 5 listed code files.
- No roadmap edits by builder (IR#4 — team_100 owns roadmap).
- No `vendor/` commit, no community write surface, no DB schema change.
- Do not touch other teams' `_COMMUNICATION/team_XX/` (XX ∉ {10, 00}).
- Do not touch the unrelated parallel-session working-tree changes (jmf_book/*,
  data/external_sources/*, .env.example, CHANGELOG.md) — those belong to other WPs.

## §4. Acceptance Criteria

| AC | Item | Check | Pass condition |
|----|------|-------|----------------|
| AC-01 | B | `php -l app/Lib/CommunityFeed.php` | no syntax errors |
| AC-02 | B | `CommunityFeed::recent(3)` returns array of ≤3 normalized rows with all 7 keys | structural assert |
| AC-03 | B | Invalid/missing JSON → fallback returns ≥1 curated row | render not empty |
| AC-04 | B | Render `shell/desktop.php` → `.dt-side__feed` present + 3 `.feed-item` | substring/count assert |
| AC-05 | B | `data/community_feed.json` is valid JSON, all items have required keys | `json_decode` ≠ null |
| AC-06 | B | No POST route / no DB write / no `community_contributions` introduced | grep clean |
| AC-07 | C | `bash -n scripts/ftp_deploy_sfa_ui.sh` | syntax OK |
| AC-08 | C | Script runs `composer install --no-dev` before lftp + verifies `vendor/` | grep present |
| AC-09 | C | Script uses `SFA_FTP_HOST/PORT/USER/PASS/ROOT` + `SFA_DELIVERY_SRC` | grep present |
| AC-10 | C | Script is executable (`-x`) | `test -x` |
| AC-11 | C | `UI_DEPLOY_RUNBOOK.md` documents Option B + smoke + rollback | sections present |
| AC-12 | D | `php -l templates/macros/module_card.php` | no syntax errors |
| AC-13 | D | `hero_url` set → `<img class="mod-card__hero">` with that src emitted | render assert |
| AC-14 | D | `hero_url` unset → no `.mod-card__hero` (icon-only fallback) | render assert |
| AC-15 | D | `hub.css` has `.mod-card__hero` cover rule + `:has()` icon-revert intact | grep present |
| AC-16 | A | og-default prompt artifact (3 variants) + routing MSG exist | files present |
| AC-17 | D | module-heroes prompt artifact (8 slug-exact prompts) + routing MSG exist | files present |
| AC-18 | all | `validate_aos.sh .` | 0 FAIL |
| AC-19 | all | `composer test` (phpunit, once `vendor/` installed) | 0 new failures vs baseline |

**AC-16/AC-17 are prompt-routing ACs (team_100 already satisfied).** Image
placement (og-default.webp + 8 heroes) and `modules.php` `hero_url` wiring are
**deferred sub-items** gated on team_00 media delivery — not part of this patch's
code-closure AC set, but must be re-validated on the eventual asset deploy.

## §5. Build phases (builder)
1. B.0 — apply/adopt `team100_draft.diff`; review every hunk for correctness + style parity.
2. B.1 — `composer install` (dev) so phpunit runs; run baseline `composer test`.
3. B.2 — add phpunit coverage for `CommunityFeed` (recent/limit/fallback/normalize) + module_card hero render.
4. B.3 — verify AC-01..AC-17 locally (lint + render harness + grep + file checks).
5. B.4 — `validate_aos.sh` (AC-18); `composer test` (AC-19).
6. B.5 — write BUILD_REPORT to `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-UI-patch01/BUILD_REPORT_v1.0.0.md`; commit on builder branch; flag QA readiness.

## §6. Notes
- DB online (PostgreSQL 16.13) — but this patch touches no structured DB state;
  CommunityFeed reads a JSON file, no API mutation needed.
- Deploy is NOT part of L-GATE_B for this patch (gated on media + bundled L-GATE_V).
