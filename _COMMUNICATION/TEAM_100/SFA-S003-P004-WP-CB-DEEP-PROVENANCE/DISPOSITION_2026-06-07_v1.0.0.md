# DISPOSITION — SFA-S003-P004-WP-CB-DEEP-PROVENANCE — Deep-view source provenance

**WP:** `SFA-S003-P004-WP-CB-DEEP-PROVENANCE` · **Tier:** REGISTER (SMALL)
**Date:** 2026-06-07 · **Author:** team_100 · **Engine:** Claude Code (Opus)
**Branch:** `claude/cb-followups-2026-06-07`
**Spec ref:** `_COMMUNICATION/team_100/REPORT_WP-CB-MOBILE_FOLLOWUPS_calc-and-deep-provenance_2026-06-07.md` (§ ITEM 2)
**Builder:** team_10 · **Validator:** team_50

> Re-verified against the working tree at `f3e693c`. This item was REASSESSED from a suspected pipeline gap down to a **doc-cleanup + data-coverage** task.

## 0. team_00 decision (RESOLVED 2026-06-07)
**Scope = comment fix (§2.1) + fallback robustness (§2.3).** Both build in this WP, on `claude/cb-followups-2026-06-07`. **Data-coverage (§2.2) splits to a separate crop-enrichment data WP** (related to `WP-CB-CROPDATA-DATES` — same SSoT enrichment lever). No-leak intent for `OP/MK/WB/UC` is retained as-is (not re-litigated).

---

## 1. Finding: provenance works in production
The earlier "Deep source pills are omitted" concern was **overstated**. Live check 2026-06-07 (`/crop-book/lettuce/?depth=deep`): **32 `srcpill` + 8 `srcline` rows render**. The EX/PR/WR pipeline is wired end-to-end and functioning wherever enrichment data exists.

**How it works (verified):**
- Pills need ≥1 field with a non-empty `winning_source_class`; `buildSourceClasses()` (`CropBookViewController.php:1010-1031`) maps `EXPERT→EX`, `NI/PROFESSIONAL→PR`, `WEB/NET→WR`, dedups, ranks `EX>PR>WR`, drops anything unrecognised (no-leak by design).
- **Path A (works):** the mirror **does** have `crop_field_enrichment` + `crop_attribute`; `detail()` queries them (`CropBookViewController.php:666-668`, `681-683`) → real pills (lettuce proves it).
- **Path B (fallback, strips provenance):** fields with no enrichment row fall back to the variety payload and **hard-code `winning_source_class => ''`** (`CropBookViewController.php:879,887,912`) → no pill for that field.

## 2. The actual (smaller) gaps

### 2.1 Stale/false code comment — CONFIRMED (S, do now)
`CropBookViewController.php:693-696` states: *"the MySQL mirror has no crop_field_enrichment / crop_attribute tables."* This is **false** and **self-contradicting**: the same method queries exactly those two tables 25 lines above (L666-668, L681-683), and pills render live. **Fix:** correct the comment to describe the real two-path model (dedicated enrichment tables **plus** a variety-payload fallback). Pure doc change, zero behavior risk.

### 2.2 Data coverage (the real lever — DATA, ongoing)
Crops/fields **without `crop_field_enrichment` rows** hit Path B and show no pills. This is **data-completeness**, not a pipeline defect. Lever: enrich more crops in the PG SSoT, then push `sfa_ingest_push.py --table crop_field_enrichment,crop_attribute`. Owned by the crop-book enrichment team. **Shared concern with WP-CB-CALC §7d** (the same sparse enrichment also starves the date calcs).

### 2.3 Fallback robustness (S, OPTIONAL ~1d)
Path B could *also* surface provenance if the per-variety payload carried a `source_class{}` map. The producer already has `winning_source_class` in `enrichment_meta` (`sfa_ingest_push.py:411-415`) but emits only `field_state`. Adding `source_class{}` + reading it in the 3 fallback branches (`:879,887,912`) would yield pills even without a dedicated enrichment row. **If built:** namespace any new template locals (the `$notes`-clobber 500 lesson — `feedback_shared_include_scope_var_clobber`); push is idempotent + covered by `IngestEnrichmentMirrorTest`.

## 3. Confirmed robust (no action)
Ranges (`.rng`) render iff ≥2 varieties carry distinct numeric values (`crop_topics.php:41,46`; `buildVarietyRanges` `CropBookViewController.php:974-998`). Backing per-variety numerics are reliably in `crop_varieties.payload_json`. No gap.

## 4. Build plan (per decision §0)
- **Task 1 — comment fix (§2.1):** correct `CropBookViewController.php:693-696` to describe the real two-path model. Pure doc, zero behavior risk.
- **Task 2 — fallback robustness (§2.3):** add `source_class{}` to the per-variety payload in the producer (`sfa_ingest_push.py` — it already has `winning_source_class` in `enrichment_meta` L411-415) and read it in the 3 fallback branches (`CropBookViewController.php:879,887,912`). **Namespace any new template locals** (the `$notes`-clobber 500 lesson). Push is idempotent + covered by `IngestEnrichmentMirrorTest` — extend it to assert the new key round-trips.
- **Verify (S):** confirm `SELECT COUNT(*) FROM crop_field_enrichment` on the live uPress mirror + survey which crops lack rows (ask Nimrod / authorized path) to size the residual coverage gap.
- **Acceptance:** PHP suite green (217/217) + a route test seeding a **RICH** payload that has *no* dedicated enrichment row for a field, asserting the fallback now emits a pill from `source_class{}`. Smoke the LIVE deep view post-deploy.

## 5. Out of scope (split out)
- **Data-coverage (§2.2)** → separate crop-enrichment data WP (related to `WP-CB-CROPDATA-DATES`). The real lever for "more pills" is enriching more crops in the PG SSoT.
- **No-leak intent** for `OP/MK/WB/UC` → retained as-is.
