# VALIDATION_MANDATE — SFA-S003-P004-WP-CB-SRC-SWEEP — team_100 → team_190 — v1.0.0

**Date:** 2026-06-11
**From:** team_100 (Claude Code, builder)
**To:** team_190 (constitutional validator) — **MUST run on a non-Claude engine** (Cursor / Codex / Desktop) per Iron Rule #1/#5
**WP:** SFA-S003-P004-WP-CB-SRC-SWEEP
**Gate:** L-GATE_VALIDATE
**Branch / HEAD:** `feat/wp-cb-src-sweep` @ `0e0edbd`

## Why this mandate
team_100 (Claude Code) is the builder and CANNOT issue the constitutional L-GATE_VALIDATE verdict for its own
work. Build + deploy + integrity are complete (see `COMPLETION_REPORT_2026-06-11_v1.0.0.md`); the only
remaining canonical step is an independent cross-engine PASS → then archive + roadmap `LOD500_LOCKED`.

## Verification cases (re-execute independently at HEAD)
1. **VC-1** `python -m pytest tests/crop_book -q` → 779 pass / 1 skip / **1 known-fail**
   (`test_wp_upload_crop_book::test_dispatch_upload_crop_book_profile` — PRE-EXISTING, retired www tier; prove
   identical on clean `main`).
2. **VC-2** `cd sfa_delivery && php vendor/bin/phpunit` (copied vendor) → 233 pass / 0 fail.
3. **VC-3** `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` → 0 FAIL.
4. **VC-4** L39: crop #31 (`עלי בייבי`) has variety `חסה בייבי` (name_en set) + cultivar source value (`NI:jmf_ft_mesclun_v1`) + 4 internal species notes.
5. **VC-5** L45: `OP:il_farm_2017_l45` source-values for days_to_maturity/spacing_in_row_cm/rows_per_bed (62 rows) + 22 internal notes / 22 crops; the cannabis/price/budget/trees/calendar sheets are NOT integrated (`scripts/extract_l45_basedata.py` documents the exclusion).
6. **VC-6** License firewall: `crop_knowledge_notes` is NOT in `sfa_ingest_push.py` allowlist; internal notes ("Salanova", L45 cultural text) absent from production HTML.
7. **VC-7** Publisher scoping: `--crop-ids` filters crop-keyed tables only; products/cover_crops excluded; ambiguous slug raises.
8. **VC-8** Production: `https://sfa.nimrod.bio/crop-book/salad-mix` variety count = 13; qa_probe overflow=false mobile+desktop; `https://sfa.nimrod.bio/api/v1/crops` count = 70 (no stale crops deployed).

## Out of scope for this verdict (separate follow-up, do NOT block on)
- Production is behind a full seed (70 vs 77 crops); the full seed creates duplicate crop #95 + 6 others.
  Tracked separately (catch-up deploy + duplicate-crop resolution fix). See COMPLETION_REPORT §5.

## On PASS
team_100 closure protocol: archive mandate (team_191 `ARCHIVE_MANIFEST.md`) → roadmap `LOD500_LOCKED`.
