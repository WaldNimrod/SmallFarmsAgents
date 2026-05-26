---
id: SFA-S003-P002-WP-C5-LOD200
wp: SFA-S003-P002-WP-C5 — Manual Data Cleanup & Refinement
gate: L-GATE_S (LOD200)
status: PROPOSED_PENDING_C2_C3_CLOSURE
author: team_10 (Claude Sonnet 4.7) under team_00 grant 2026-05-26
date: 2026-05-26
version: v1.0.0
parent_wp_chain:
  - SFA-S003-P002-WP-A (engine SSoT + engine v1.1 inheritance)
  - SFA-S003-P002-WP-B (LOD500_LOCKED)
  - SFA-S003-P002-WP-C1 (LOD500_LOCKED) ✅
  - SFA-S003-P002-WP-C4 (LOD500_LOCKED) ✅
  - SFA-S003-P002-WP-C2 (pending — Hebrew narrative NI)
  - SFA-S003-P002-WP-C3 (pending — Curtis OCR + backlog)
depends_on: [SFA-S003-P002-WP-C2, SFA-S003-P002-WP-C3]
activation_condition: "C2 + C3 both LOD500_LOCKED"
mode: "team_00 manual refinement — NOT a builder mandate"
---

# LOD200 — WP-C5: Manual Data Cleanup & Refinement (team_00 phase)

## 1. Mission

After all ingestion waves complete (C1+C2+C3+C4), team_00 reviews the
consolidated DB and provides manual refinements:

1. **EX overrides** — Where team_00 has confident knowledge that the auto
   reconciliation produced wrong value, add EX-tier override.
2. **Crop name mapping fixes** — Resolve any remaining unmapped Hebrew names
   that the importers couldn't auto-map (UNMAPPED_CROPS files from C1+C2).
3. **Outlier marking** — Manually mark specific source values as
   `is_outlier_rejected=TRUE` if team_00 determines they're not representative.
4. **Cultivar disambiguation** — For varieties with conflicting OP data
   across years/farms, team_00 picks the canonical value or adds note.
5. **Knowledge note review** — Spot-check LLM-extracted NI narrative for
   accuracy; reject/edit/replace any incorrect entries.
6. **Field-level decisions** — For (variety, field) combos still showing
   MARGINAL/MISALIGNED in `validate_enrichment.py`, team_00 either:
   - Accepts current auto-value (no action)
   - Provides EX override
   - Documents why divergence is acceptable (e.g., different cultivar genetics)
7. **Gap-fill via team_00 knowledge** — Where team_00 has domain expertise
   that no source captured, add NI rows (e.g., specific Israeli microclimate
   adaptations).

## 2. In-scope

- **NO new tables, NO new importers, NO code changes**
- **Team_00-driven data mutations** via:
  - `scripts/team_00/add_ex_override.py` (helper to insert EX rows safely)
  - `scripts/team_00/mark_outlier.py` (helper to flag is_outlier_rejected)
  - `scripts/team_00/review_calibration.py` (interactive review of MARGINAL pairs)
- Decision artifacts under `_COMMUNICATION/team_00/SFA-S003-P002-WP-C5/`:
  - `EX_OVERRIDES_v1.0.0.md` (list of EX values team_00 added)
  - `OUTLIER_DECISIONS_v1.0.0.md` (rows marked as outliers + reason)
  - `KNOWLEDGE_NOTE_REVIEW_v1.0.0.md` (NI narrative spot-checks)
  - `UNMAPPED_RESOLUTIONS_v1.0.0.md` (Hebrew name fixes)
- Re-run `enrichment_runner` after each batch of team_00 changes
- Final `validate_enrichment.py` snapshot
- `crop_field_enrichment` final state archived to JSON snapshot

## 3. Out-of-scope

- Code changes (no new importers, no engine changes — engine v1.1 is final)
- New data sources (those went into C1-C4)
- UI work (separate WP, e.g., future WP-D for OMA frontend)
- Bulk imports (manual = small, targeted refinements only)

## 4. Activation

Triggered manually by team_00 after C2+C3 close. Not a builder mandate;
no L-GATE_B/L-GATE_V cycle. Closure is when team_00 signals "data ready
for production use" via:
- `_COMMUNICATION/team_00/SFA-S003-P002-WP-C5/DATA_FROZEN_v1.0.0.md`

## 5. Data model summary

**Mutations only — no schema changes**:
- New rows in `crop_variety_source_values` with `source='team_00'`, `trust_tier='EX'`
- Updates to `is_outlier_rejected` flag on existing rows
- New rows in `crop_knowledge_notes` with `source='NI:team_00_manual'`
- Re-run `enrichment_runner` regenerates `crop_field_enrichment`

## 6. Trust-layer placement

All team_00 manual entries → **EX tier** (hard override, weight=NULL).
This is by definition: team_00 = the Principal authority, equivalent to
domain truth for the SFA project.

## 7. Dependencies

- Hard: C2 + C3 LOD500_LOCKED (all ingestion done; data state stable)
- Soft: UI/dashboard available to surface refinements (optional)

## 8. LOD500_LOCKED untouched

- Same protected list as C1/C4
- ALSO: `reconciler.py`, `enrichment_runner.py`, `validate_enrichment.py`
  are post-engine-v1.1 frozen. No engine changes in C5.

## 9. GCR requirements

**NONE.** team_00 manual operations use existing tables + sources.

## 10. Success criteria (loose — team_00 owns)

- All UNMAPPED_CROPS items from C1/C2 resolved
- All CALIBRATION MISALIGNED pairs either: have EX override, OR have
  documented "acceptable divergence" note
- Knowledge note coverage ≥80% of crops (post-C2) reviewed for accuracy
- `DATA_FROZEN_v1.0.0.md` filed by team_00

## 11. Open questions (for team_00 to answer during execution)

- Which crops most urgently need EX overrides beyond ארוגולה DTM?
- Threshold for "acceptable divergence" between auto and team_00 knowledge?
- Are there crops where team_00 wants to OVERRIDE the JMF cultivar
  recommendations with Israeli-adapted choices?

---

*Authored by team_10 (Claude Sonnet 4.7) 2026-05-26 under team_00 grant.
Will activate after C2+C3 LOD500_LOCKED. No code; pure data discipline phase.*
