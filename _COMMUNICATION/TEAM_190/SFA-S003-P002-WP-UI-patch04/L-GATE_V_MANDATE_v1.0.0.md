---
id: L-GATE_V_MANDATE_SFA-S003-P002-WP-UI-patch04_v1.0.0
from: team_100 (Chief Architect)
to: team_190 (Constitutional cross-engine validator)
cc: team_00, team_10, team_50
date: 2026-05-29
type: validation_mandate
wp: SFA-S003-P002-WP-UI-patch04
gate: L-GATE_V
build_commit: "c7dc779"
spec_ref: _aos/work_packages/S003/SFA-S003-P002-WP-UI-patch04/LOD400_spec.md
engine_constraint: "NON-CLAUDE REQUIRED (IR#1) — builder=Claude Sonnet, QA=Claude Haiku, integrator=Claude Opus. Validator MUST be non-Claude (Cursor/Composer, Codex, GPT-5.x)."
---

# L-GATE_V MANDATE — WP-UI-patch04 (Crop-book completeness + global navigation)

## Cross-engine handoff (IR#1/#5)
Build (team_10 Claude Sonnet A∥B→C) ≠ QA (team_50 Claude Haiku) ≠ integration/deploy (team_100 Claude Opus). The constitutional L-GATE_VALIDATE verdict MUST be non-Claude. team_100 cannot self-issue.

## What shipped (commit c7dc779, deployed live to uPress sfa.nimrod.bio)
Addresses team_00's 6 defects:
1. **Broken links 72 → 0** — market↔crop-book cross-links name-resolved + gated; planned-module links disabled; dead /market/methodology CTA removed.
2. **Landing cards** — responsive `.gj-cropgrid` (auto-fill minmax); planned/coming modules render non-navigable `.is-disabled` cards.
3. **Full-width detail** — `.cb-crop-detail` central panel.
4. **All crop data** — `crops.payload_json` now embeds identity, calendar, agronomy (crop-median rollup), harvest, storage, companions, notes (public-only); rendered as sections. (`cover_crops` NOT pushed — source data is PDF-parse junk → empty-state, re-seed follow-up. `knowledge_notes` 100% internal-gated → §Notes empty by design.)
5. **Global nav** — persistent top bar (בית/ספר גידולים/שוק) + crop-book sub-nav on every page.
6. **Species-first** — detail order: identity→calendar→agronomy→harvest→storage→companions→notes→**varieties LAST**.

## Evidence on record (verify independently)
- gate_history: `_aos/roadmap.yaml` → SFA-S003-P002-WP-UI-patch04 (L-GATE_B PASS; QA QA_PASS; DEPLOY LIVE).
- team_100 re-verify: `php -l` clean; `composer test` 63 tests / 0 failures; `validate_aos.sh` 29/19/0; ingest dry-run 70 crops carry all 7 sections; final crawl 0 internal 404s.

## Acceptance criteria to disposition (LOD400 §4: AC-U4-01…12)
Crawl `/`, `/crop-book/`, `/crop-book/{slug}`, `/crop-book/table`, `/crop-book/family`, `/crop-book/questions`, `/crop-book/cover-crops`, `/market/` — expect 0 internal 404s (AC-U4-07). Verify rich sections render on arugula species-first with varieties last (AC-U4-03/04); internal notes never rendered (AC-U4-05); persistent nav on every page (AC-U4-06); full-width (AC-U4-08); landing sizing + valid slugs (AC-U4-09); php -l + composer test (AC-U4-10); validate_aos 0 FAIL + no www.nimrod.bio + MySQL faithful mirror, no schema change (AC-U4-11); live on uPress not home server (AC-U4-12).

## Known deferred / P2 (not defects to block on)
- `cover_crops` data not pushed (junk source); `/crop-book/cover-crops` is a clean empty-state.
- market→crop-book convenience cross-links resolve 0 live (name-match miss; suppressed → no 404).
- knowledge_notes all `is_internal_farm_use_only` → §Notes empty (governance gate honored).

## Deliverable
Verdict → `_COMMUNICATION/team_190/SFA-S003-P002-WP-UI-patch04/L-GATE_V_VERDICT_v1.0.0.md`. On PASS, team_100 executes ADR042 closure → LOD500_LOCKED.

— team_100 (Claude Opus 4.8) 2026-05-29
