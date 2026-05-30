# GAP-FILL PLAN — SFA-S003-P004-WP-CB-1 — team_100 — v1.0.0

**Date:** 2026-05-30
**Author:** team_100 (Chief System Architect, Claude Code)
**WP:** SFA-S003-P004-WP-CB-1 (Crop Book v1)
**Type:** GAP_FILL_PLAN
**Status:** Derived from MANDATORY_FIELD_SCHEMA_v1.0.0. Locked input to LOD400.
**Deliverable:** 3 of 6

---

## 1. Goal

Define how every **shown** crop reaches 100% coverage on its mandatory fields, and the exact rule that separates a **COMPLETE book** crop (full calculator features) from a **PARTIAL** one (asterisks + disabled calculators + "request info"). "Shown" = the launch-set of crops surfaced in the v1 UI (the C1–C6 enriched set, ~52 core + sparse expansion).

---

## 2. Complete vs Partial — the state machine

Per crop, per mandatory field, read the existing `crop_field_enrichment` consensus:

| Field state | Condition | UI rendering |
|-------------|-----------|--------------|
| **VALIDATED** | `winning_source_class ∈ {EX, NI}` **OR** `confidence_score ≥ τ` (with `source_count ≥ 1`) | plain value, calculators enabled |
| **UNVALIDATED** | row exists but `confidence_score < τ` **or** `winning_source_class ∈ {WR, WB, UC}` | value **with asterisk** + tooltip "web/low-confidence source"; calculators enabled but flagged |
| **MISSING** | no `crop_field_enrichment` row for the field | "—" + **"request info"** CTA; calculators needing it **disabled** (Catalog §7) |

**Crop-level state:**
- **COMPLETE** ⟺ every mandatory field is VALIDATED.
- **PARTIAL** ⟺ at least one mandatory field is UNVALIDATED or MISSING.

A PARTIAL crop still shows everything it has; it just carries asterisks, the "request info" CTA on missing fields, and disabled calculators where a required field is MISSING (not merely unvalidated).

### Threshold τ
**Proposed τ = 0.40** (≈ the MK class floor — i.e., anything resolved purely from market/low tiers without corroboration reads as unvalidated). Rationale: EX/NI hard overrides always validate (they bypass τ); PR(0.70)/OP(0.55) corroborated values clear 0.40; lone WB(0.30)/UC(0.15) do not. **τ is a single tunable config constant**, finalized with team_00 after the first coverage snapshot (§4) shows the COMPLETE/PARTIAL split it produces.

---

## 3. Coverage path — how a field gets filled (priority order)

For any MISSING or UNVALIDATED mandatory field on a shown crop:

1. **Nimrod EX / NI override** — highest trust, hard winner. The minimal, highest-leverage fills (the "Nimrod fill-list", §5) go here. EX = direct expert override; NI = a file/link Nimrod provides (`ni_importer`).
2. **JMF + Tend ingestion (already loaded)** — PR(0.70) / OP(0.55). Most core fields are already covered this way (C1–C6 waves). No new work; this is the baseline.
3. **WR (Web-Research) fallback** — WR(0.60), the in-session $0 Claude synthesis method proven in WP-C6 (`ni/claude_*_research.py`, web-grounded structured JSON, idempotent). Fills remaining gaps for shown crops. **WR values render UNVALIDATED (asterisk)** until corroborated/overridden — explicit honesty in the UI.

A crop reaches COMPLETE when steps 1–2 (and EX/NI promotion of WR values where Nimrod confirms them) clear every mandatory field above τ.

---

## 4. Coverage snapshot (the per-crop matrix) — methodology + query

The actual matrix is **generated against the live PostgreSQL** (oma-postgres, head ~057) at build time — not hand-authored — using the same approach as `COVERAGE_SNAPSHOT` from WP-C6. The build/data agent runs:

```sql
-- Per shown crop × mandatory field: state classification
WITH mandatory(field_name) AS (VALUES
  ('days_to_maturity'),('harvest_window_min_days'),('harvest_window_max_days'),
  ('in_row_spacing_cm'),('rows_per_bed'),('avg_yield_per_bed_m'),
  ('documented_price'),('planting_season'),('planting_method'),
  ('frost_tolerance_class'),('seeds_per_gram'),
  ('nutrient_removal_n_kg_ha'),('nutrient_removal_p_kg_ha'),('nutrient_removal_k_kg_ha'),
  ('days_in_nursery_cell'),('succession_interval_weeks')
)
SELECT c.id AS crop_id, c.name_he, m.field_name,
       e.value_best, e.confidence_score, e.winning_source_class, e.source_count,
       CASE
         WHEN e.id IS NULL THEN 'MISSING'
         WHEN e.winning_source_class IN ('EX','NI') OR e.confidence_score >= 0.40 THEN 'VALIDATED'
         ELSE 'UNVALIDATED'
       END AS field_state
FROM crops c
JOIN crop_varieties v ON v.crop_id = c.id AND v.is_default = TRUE
CROSS JOIN mandatory m
LEFT JOIN crop_field_enrichment e ON e.variety_id = v.id AND e.field_name = m.field_name
ORDER BY c.name_he, m.field_name;
```
(Default variety = crop-scoped baseline; per-variety completeness is a drill-down extension.)

**Output artifact (build time):** `COVERAGE_SNAPSHOT_CB1_v1.0.0.md` — a crop × field grid marking VALIDATED / UNVALIDATED / MISSING, plus per-crop COMPLETE/PARTIAL rollup and a global completeness count (mirrors WP-C6's "5291→5780" style).

> **Note:** `days_in_nursery_cell` and `succession_interval_weeks` will read MISSING for most crops until the §3.1/§3.2 wirings of the Mandatory Field Schema run `run_enrichment`. The first snapshot is taken **after** those wirings so the matrix reflects true post-wiring coverage.

---

## 5. The Nimrod fill-list (minimal EX/NI set)

After the first post-wiring snapshot, team_100 produces a **ranked fill-list**: the smallest set of EX/NI entries that moves the launch-set of crops from PARTIAL → COMPLETE. Ranking heuristic:
- Prioritize fields that are MISSING (block calculators) over UNVALIDATED (asterisk only).
- Prioritize crops closest to COMPLETE (1–2 gaps) for fastest COMPLETE-count gains.
- Prioritize fields used by the most calculators (Catalog §6: `in_row_spacing_cm`, `rows_per_bed`, `avg_yield_per_bed_m`, `days_to_maturity`, `days_in_nursery_cell`).

Delivery format for Nimrod: a checklist of `(crop, field, current_value?, proposed_value, unit)` rows he confirms/edits, ingested as EX (`source="team_00"`) or NI overrides — same mechanism as `TEAM00_DTM_OVERRIDES`.

---

## 6. "Complete book" vs "partial" — product meaning

- **COMPLETE crop** → full v1 experience: all 14 calculators enabled, no asterisks, the book is a trustworthy planning tool for that crop.
- **PARTIAL crop** → honest degraded experience: shows what we know, asterisks the uncertain, disables only the calculators whose required field is MISSING, and invites the user to "request info" (a future community/Nimrod feedback loop → UC/NI sources). **No silent gaps — every missing value is visibly marked.**

The launch bar (team_00 to confirm): which crops must be COMPLETE for v1 launch vs. acceptable-PARTIAL. Default proposal: the **core ~52** must be COMPLETE on the calculator-critical fields (the 5 high-use fields above + price + frost); sparse-expansion crops may launch PARTIAL.

---

## 7. Dependencies & sequencing

1. Mandatory Field Schema §3.1/§3.2 wirings land (build) → `run_enrichment`.
2. First COVERAGE_SNAPSHOT_CB1 generated → defines actual PARTIAL set + validates τ=0.40.
3. WR fallback fills shown-crop gaps (in-session, $0) → second snapshot.
4. Nimrod fill-list (EX/NI) closes the launch-critical PARTIAL crops → COMPLETE.
5. τ finalized with team_00 from the snapshot split.

Steps 1–4 are **build/data work for WP-CB-1**, not this spec session. This plan defines the rules and the generator; the matrices are produced against the live DB during the build.

---

*Locked input to the LOD400 (Deliverable 4). The complete/partial state machine here is the contract the team_35 mockups (Deliverable 5) must visualize.*
