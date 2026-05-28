---
id: L-GATE_V_MANDATE_SFA-S003-P002-WP-C2_v1.0.0
from: team_10 (Claude Sonnet 4.7 — builder)
to: team_190 (cross-engine validator — MUST be non-Claude per IR#1)
date: 2026-05-28
type: validation_mandate
wp: SFA-S003-P002-WP-C2
gate: L-GATE_V
build_commit: "4d79856"
status: AWAITING_VALIDATION
---

# L-GATE_V Validation Mandate — WP-C2 (Hebrew Narrative NI)

## Cross-engine requirement (IR#1)

team_10 built + deepened WP-C2 using **Claude Sonnet 4.7**. The validator
MUST run a **non-Claude** engine (as for C1/C3/C4).

## What to validate

WP-C2 ingests 6 Hebrew NI narrative sources into `crop_knowledge_notes`
(trust_tier NI, hard override, `is_internal_farm_use_only=True`). After a
team_00-directed depth-first closure (2026-05-28), all sources were brought
to ≥3 notes. Final coverage = **40 notes** across 6 sources at commit
`4d79856`:

| source | notes | note |
|--------|-------|------|
| `NI:aosnot_v1` | 10 | deepened 4→10 (אוסנה/blackberry deep-dive) |
| `NI:sham_hydro_guide_v1` | 8 | original |
| `NI:jmf_ft_nurseryseeding_ext_v1` | 8 | original |
| `NI:zacks_leafy_survey_v1` | 6 | recovered 0→6 (52-slide image deck) |
| `NI:sham_variety_trials_v1` | 5 | deepened 1→5 (L11 lettuce NFT trial) |
| `NI:jmf_ft_seedingincellflats_v1` | 3 | original |

### Deepening method (disclosed)
The 3 shallow sources were re-extracted **in-session by Claude vision**
($0 — no separate Anthropic API spend, within the $20 cap). The deepened
JSON caches live under `data/external_sources/extracted/{aosnot,
zacks_leafy_survey,sham_variety_trials}/`. The 3 importers' `_SOURCE_NOTE_TYPES`
tuples were expanded (all values within the migration-053 note_type CHECK).

## Acceptance criteria (proposed — team_190 confirm/extend)

| # | Criterion | How to check |
|---|-----------|--------------|
| AC-C2V-01 | 17/17 C2 tests pass | `pytest tests/crop_book/test_c2_*.py` |
| AC-C2V-02 | 6 NI sources present, each ≥3 notes, total ≥40 | SQL GROUP BY source |
| AC-C2V-03 | All C2 notes trust_tier='NI', is_internal_farm_use_only=TRUE | SQL filter |
| AC-C2V-04 | All body_text ≤2000 chars (fair-use bound) | SQL `max(length(body_text))` |
| AC-C2V-05 | All note_types within migration-053 CHECK constraint | insert succeeded → satisfied; spot-check |
| AC-C2V-06 | Hebrew RTL preserved, no \uXXXX escapes in JSON caches | inspect cache files |
| AC-C2V-07 | Migration 049/053 note_type extension applied | `alembic current` ≥ 056 |
| AC-C2V-08 | Deepened content faithful to source (no fabrication) | spot-check אוסנה.json vs raw_text; חסה L11 vs PDF tables |
| AC-C2V-09 | Enrichment unaffected (notes are narrative, not source_values) | re-run; consensus rows stable at 5,291 |
| AC-C2V-10 | validate_aos.sh 0 FAIL | run validator |

## Known caveats (disclosed by builder)

1. **AOSNOT** "1.3MB encyclopedia" in the LOD400 mission text was a
   misread — the docx is a single-crop (אוסנה/blackberry) document; ~1.2MB
   is cultivar photos, ~6.4KB is prose. 10 notes is full coverage of that text.
2. **Zacks (L10)** original extraction produced 0 notes (scanned 52-slide
   deck; text extraction got only the 209-byte title page). Recovered via
   vision: lettuce (חסה) DWC variety trial + NFT/DWC parameters + diseases;
   plus a thin strawberry (תות שדה) vertical-hydroponics note.
3. **sham_variety_trials (L11)** is lettuce-only (single-crop NFT trial),
   not multi-crop — deepened to 5 notes for חסה.
4. Strawberry note (תות שדה) is intentionally thin — source content is one
   slide; flagged in the note body for future PR/WR top-up.

## Verdict location

team_190 → `_COMMUNICATION/team_190/SFA-S003-P002-WP-C2/L-GATE_V_VERDICT_v1.0.0.md`

On PASS → team_10 ADR042 3-step closure → LOD500_LOCKED.
On FINDINGS → team_10 remediates in an R2 round.

---

*Mandate by team_10 (Claude Sonnet 4.7) 2026-05-28. Cross-engine validation
required per IR#1; final authority team_190 per IR#5. Pairs with the
WP-C5 Phase A mandate — both await the same team_190 session.*
