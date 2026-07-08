# COMPLETION_REPORT — SFA-S003-P004-WP-CB-SRC-SWEEP — team_100 — v1.0.0

**Date:** 2026-06-11
**Author:** team_100
**WP:** SFA-S003-P004-WP-CB-SRC-SWEEP
**Type:** COMPLETION_REPORT (build + deploy done; L-GATE_VALIDATE pending)
**Branch:** `feat/wp-cb-src-sweep`

## 1. Outcome

Source-data tail integrated, deployed (scoped), integrity-verified. The "verify ALL info was integrated
before the next research round" directive is **satisfied**: the audit confirmed the DB was already
comprehensively integrated (~50 sources); the genuine remaining value (L39 + L45 cherry-pick) is now in,
and the non-integrable tail (L43/L44/L26/L38/jmf_book_alt) is explicitly deprioritized via DECISION.

## 2. Built

| Item | Result |
|------|--------|
| L39 variety `חסה בייבי` under crop #31 + cultivar SV + 4 internal species notes | ✓ variety id 586 |
| L45 `נתוני בסיס` cherry-pick → `OP:il_farm_2017_l45` | ✓ 62 source-values (all accepted) + 22 internal notes, 22 crops |
| L45 cannabis/price/budget/trees/calendar sheets excluded | ✓ (extractor documents exclusions) |
| `jmf_masterclass._default_variety_id` robustness fix | ✓ (unblocks `seed --all`) |
| `sfa_ingest_push --crop-ids/--slugs` scoping | ✓ (crop-keyed tables only) |
| New tests (L45, L39, masterclass) + updated NI count 6→7 | ✓ |

## 3. Integrity

- **Backend** `pytest tests/crop_book`: **780 pass / 1 skip / 1 fail** (after R2 remediation). The 1 fail
  (`test_wp_upload_crop_book::test_dispatch_upload_crop_book_profile`) is **pre-existing** (mock.patch of
  `organic_market_agent.utils.config.Config` under py3.9 — tests the retired www WP-upload tier; severed
  2026-05-28). Proven identical on clean `main` (stash test). Not introduced by this WP; out of scope.
  **R2 (2026-06-11):** first validation FAILED `test_ac05_derived_fields` — `seed --all` (run to land deltas)
  reintroduced forbidden DERIVED fields; the canon strip (`canon.migrate phase4`) was not run. Fixed by
  stripping 77 source-values + 695 enrichment rows; AC-05 now passes. Production never affected (derived
  fields not in the publish whitelist).
- **Delivery** `vendor/bin/phpunit`: **233 pass / 0 fail** (1 PHPUnit deprecation warning only).
- **validate_aos.sh**: **31 PASS / 21 SKIP / 0 FAIL**.
- **License firewall**: `crop_knowledge_notes` not in ingest allowlist; "Salanova"/L45 cultural-note text
  confirmed ABSENT from production pages. Internal notes stay internal.

## 4. Deploy (scoped — team_00 approved "only this WP's crops")

- Pushed via HMAC ingest (HTTPS/Cloudflare, from the Mac) **scoped to 23 crop_ids** (crop #31 + the
  L45-touched existing crops): `crops` (23), `crop_varieties` (207), `crop_field_enrichment` (264),
  `crop_attribute` (78) — all **HTTP 200, 0 rejected**.
- **Production smoke PASS** (qa_probe, mobile 375 + desktop): salad-mix / carrots / lettuce
  `overflow=false`, `pass=true`. Salad-mix variety count **12 → 13** (חסה בייבי live).
- Production crop count **still 70** — the 7 stale crops were NOT deployed (scoping verified).
- Content tables (`crop_content`/`crop_content_source`) not pushed — unchanged by this WP.

## 5. ⚠ Findings (NOT this WP — flagged for follow-up)

1. **Production is stale vs a full seed.** Production = 70 crops; a full `seed --all` now yields **77**
   crops / 9,486 enrichment / 3,148 source-values — i.e. accumulated, never-deployed data from PRIOR WPs.
   This WP deliberately did NOT deploy that catch-up (team_00 chose scoped). A separate, validated
   catch-up deploy is needed to bring production current.
2. **Duplicate crop bug.** The full seed creates crop #95 `תערובת סלט` with the SAME `name_en`
   ("Lettuce: Salad Mix") as crop #31 — a slug collision (`salad-mix`). An importer's crop-resolution
   mints a duplicate. Must be fixed before any full catch-up deploy (and 6 other unvalidated new crops
   #89-94 reviewed). This is why the publisher now requires `--crop-ids` (slugs are ambiguous here).
3. **Masterclass re-seed fragility** — fixed in this WP (was blocking `seed --all`).
4. **`seed --all` produces a non-canonical, AC-05-violating DB.** Importers emit DERIVED fields
   (`yield_per_m2_kg`, oxide P2O5/K2O, `plants_per_m2`); the canonical state requires `seed` THEN
   `canon.migrate phase4` to strip them. Running `seed --all` alone (as this session did) leaves forbidden
   rows that fail `test_ac05_derived_fields` — and caused the first L-GATE_VALIDATE FAIL. The deploy is
   protected (those fields aren't in the publish whitelist), but the build pipeline gap should be closed —
   e.g. `seed --all` auto-runs the canon strip at the end, or hard-fails if derived fields remain. Belongs
   with the duplicate-crop seed fix (same root: `seed --all` alone is incomplete). Strongly reinforces the
   go-forward rule: NEVER full re-seed against the deploy baseline; add incrementally + scoped push.

## 6. Cross-engine L-GATE_VALIDATE handoff (team_190, validator ≠ Claude Code — IR#1/#5)

team_100 (Claude Code, builder) CANNOT self-issue the constitutional verdict. Proposed verification cases
for an independent (non-Claude) validator, re-executing at HEAD of `feat/wp-cb-src-sweep`:

- **VC-1** `pytest tests/crop_book` → 779 pass / 1 skip / 1 (pre-existing wp_upload) fail.
- **VC-2** delivery `vendor/bin/phpunit` (copied vendor) → 233 pass / 0 fail.
- **VC-3** `validate_aos.sh .` → 0 FAIL.
- **VC-4** L39: crop #31 has variety `חסה בייבי` (name_en set) + cultivar source value + 4 internal notes.
- **VC-5** L45: `OP:il_farm_2017_l45` has source-values for days_to_maturity/spacing_in_row_cm/rows_per_bed
  + internal notes; cannabis/price/budget/trees sheets NOT integrated.
- **VC-6** License firewall: `crop_knowledge_notes` excluded from `sfa_ingest_push`; internal notes absent
  from production HTML.
- **VC-7** Scoped publisher: `--crop-ids` filters crop-keyed tables only; products/cover_crops excluded;
  ambiguous slug raises.
- **VC-8** Production smoke: salad-mix variety count 13; qa_probe overflow=false on mobile+desktop;
  production crop count = 70 (no stale crops deployed).

## 7. Status

Build PASS · Deploy LIVE (scoped) · Integrity PASS · **L-GATE_VALIDATE PENDING** (cross-engine, team_190)
→ on PASS: archive + roadmap LOD500_LOCKED.
