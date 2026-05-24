---
id: SFA-S003-P002-WP-B1-patch01-LOD200
wp: SFA-S003-P002-WP-B1-patch01 — JMF_CROP_MAP alias extension + Rutabaga Hebrew correction
gate: L-GATE_S (LOD200 — architecture spec)
status: PRE_LOD400
author: team_110 (execution mandate per ADR045 — same mandate as parent WP-B1)
date: 2026-05-25
version: v1.0.0
parent_wp: SFA-S003-P002-WP-B1
parent_archive_ref: _archive/SFA-S003-P002-WP-B1/ARCHIVE_MANIFEST.md
parent_completion_report_ref: _COMMUNICATION/team_110/SFA-S003-P002-WP-B1/COMPLETION_REPORT_SFA-S003-P002-WP-B1_v1.0.0.md
parent_disposition_ref: _COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B1/DISPOSITION_FINDING-01_v1.0.0.md
parent_locked_commit: 6a85561        # WP-B1 LOD500_LOCKED closure commit (no reopen — sibling patch only)
depends_on: [SFA-S003-P002-WP-B1, SFA-S003-P002-WP-A]
validator: team_190 (non-Claude, Iron Rule #1)
builder: sfa_build (separate session per IR#1)
---

# LOD200 — SFA-S003-P002-WP-B1-patch01

## 1. Mission

Close the two deferred MINOR findings from WP-B1's lifecycle (FINDING-01
farm-workbook alias gap, and a Hebrew-data correction caught by team_00)
in a tight, additive follow-up patch that lifts the operational gate on
`seed.py --all` against the production workbook.

This WP is **explicitly sequenced before WP-B2** per team_00 directive
2026-05-25 ("אני רוצה לעבוד מסודר — לסגור b1 באופן מלא וסופי בלי זנבות
ואז לממש b2").

## 2. In-scope

- **Hebrew correction** — single-cell value fix for `Rutabaga` in
  `JMF_CROP_MAP`:
  - Before: `"Rutabaga": "ברוקקואר"` (team_110 hallucination during
    LOD400 v1.0.0 authoring; "ברוקקואר" is not a recognized Hebrew word
    in any horticultural or general dictionary)
  - After: `"Rutabaga": "רוטבגה"` (phonetic transliteration per team_00
    directive 2026-05-25)
- **~28 alias entries** added to `JMF_CROP_MAP` to cover the farm-specific
  JMF MasterClass workbook variant on Nimrod's disk. All aliases map to
  existing `crops.name_he` values already used by canonical entries
  (typos, synonyms, storage/season qualifiers, greenhouse variants). See
  §5 for the categorized list (resolved in LOD400 §5).
- **AC-03 Counter assertion update** to reflect the new duplicate-target
  set. The post-patch assertion will enumerate ~6–8 by-design duplicate
  pairs (e.g., `{Cabbage, Fall Cabbage, Savoy Cabbage, Summer Cabbage,
  Chinese Cabbage} → "כרוב"`).
- **Lift operational gate** — `seed.py --all` against the live workbook
  becomes safe to run on production DB after this patch lands.
- **Tests** ≥ 6 new (Counter assertion update; Rutabaga regression;
  alias coverage spot-checks; live-workbook coverage assertion).

## 3. Out-of-scope

- **No re-open of WP-B1 LOD500_LOCKED.** Parent is locked at commit
  `6a85561` and stays locked. This is a sibling patch WP, not a
  re-validation of B1.
- **Tomatillos / Parsnips / Shallots Hebrew alternatives** — Task #10
  flagged these as potential corrections, but team_00 did not direct
  changing them (only Rutabaga was called out). Out-of-scope.
- **VV-15 changelog narrative cleanup** — team_190 L-GATE_V verdict §6
  accepted the historical `int | None` wording in the WP-B1 LOD400
  changelog as by-design (changelog narrative MUST cite prior wording
  to explain a fix). Out-of-scope.
- **No new tables, migrations, models, or importer changes.** Patch is
  data-only: `constants.py` + test files + this spec.
- **No CLI flag changes.** Existing `--jmf-only`/`--no-jmf`/
  `--jmf-masterclass-dir` flags continue to work unchanged.

## 4. Data sources

Same as WP-B1 §4 (canonical reference):
- Master JMF MasterClass workbook at
  `/Users/nimrod/Documents/old Mac BackUpp/Market Gardening/MasterClass/Crop Planning/CROPPLANNINGTOOLMASTERCLASS-1515735991193 (from macBook Air - nimrod).XLSX`
- Plus the live coverage gap inventory from
  `INQUIRY_AC04_CROP_CHART_MISMATCH_v1.0.0.md` §Findings (50 CROP CHART
  rows; 14 matched canonical JMF_CROP_MAP; 36 unmapped).

No new files or sources.

## 5. Data model summary

**No schema change.** This patch only modifies the literal contents of
`JMF_CROP_MAP` (a `dict[str, str]` in `constants.py`).

Post-patch, the map's contract is:

- **Total entries:** ~80 (52 baseline + ~28 alias additions). Exact final
  count fixed in LOD400 §5.
- **Duplicate-target pairs (AC-03 allow-list):** widened from 2 (B1) to
  ~6–8 (each existing `crops.name_he` species may now have multiple
  English keys pointing at it). Exact set fixed in LOD400 §5.
- **Rutabaga value:** `"רוטבגה"` (phonetic transliteration).

## 6. Trust-layer placement

Inherits unchanged from WP-B1: `source='JMF'`, `trust_tier='PR'`,
`confidence_weight=0.70`. Engine reuse via WP-A `reconcile_field()` path
remains intact (no change to source registry / field policy /
reconciler / enrichment runner).

## 7. Dependencies

- **WP-B1** (LOD500_LOCKED at `6a85561`) — supplies the
  `crop_task_templates` schema, `jmf_masterclass.py` importer, baseline
  `JMF_CROP_MAP`, and the WARN+skip miss-handling contract this patch
  builds on.
- **WP-A** (LOD500_LOCKED at `594cbc8`) — engine SSoT (transitive).

## 8. LOD500_LOCKED inventory (unchanged scope)

Same as WP-B1 §14. **Permitted modifications (additive only):**
`organic_market_agent/crop_book/constants.py` (the `JMF_CROP_MAP` dict
literal — same convention as B1 §15 permitted-modify scope).
`CHANGELOG.md` (append `[Unreleased]` entry).
**`tests/crop_book/`** (new test file +/or extension of
`test_jmf_crop_map.py` to update AC-03 assertion).

**Notably untouchable in this patch:**
- All WP-A engine SSoT modules
- `organic_market_agent/crop_book/crop_task_templates.py`
- `organic_market_agent/crop_book/importer/jmf_masterclass.py`
- `organic_market_agent/db/versions/044_crop_task_templates.py`
- `_aos/work_packages/S003/SFA-S003-P002-WP-B1/LOD400_spec.md` (LOD500_LOCKED)

## 9. GCR requirements

**None.** Pure data extension within `constants.py`; no schema, model,
or interface change.

## 10. AC and test count targets

- **Acceptance Criteria target:** ≥ 6 ACs in LOD400
  - AC-01: `JMF_CROP_MAP` entry count is the new authoritative total
  - AC-02: `"Rutabaga"` maps to `"רוטבגה"` (NOT `"ברוקקואר"`)
  - AC-03: Counter assertion of by-design duplicate-target set is
    updated to enumerate every new pair exactly
  - AC-04: Live-workbook coverage ≥ 42/50 crops mapped (vs. 14/50
    pre-patch)
  - AC-05: All 22 WP-B1 ACs still PASS (regression — no breakage)
  - AC-06: validate_aos.sh 29 PASS / 17 SKIP / 0 FAIL

- **Test count target:** ≥ 6 new tests, broken down (preliminary):
  - 1× Rutabaga Hebrew regression (the specific known-bad value
    `"ברוקקואר"` must be absent; the new value `"רוטבגה"` must be
    present)
  - 1× Counter-set assertion (new exhaustive duplicate-target set)
  - 1× live-workbook coverage probe (parse the actual master XLSX,
    assert ≥ 42/50 crops map)
  - 1× alias-resolution spot check (sample 5-10 of the new aliases
    actually resolve to the expected `crops.name_he`)
  - 1× back-compat: all 56 prior WP-B1 tests still PASS
  - 1× operational-gate-lift smoke test (`seed.py --all` dry-run on
    fixture succeeds without ERROR-level log lines for the previously
    unmapped crops)

Final inventory fixed in LOD400 §10.

## 11. Open questions (resolved in LOD400)

1. **Exact alias list of ~28 entries** — proposed inventory in
   `DISPOSITION_FINDING-01_v1.0.0.md` §4.1. LOD400 §5 nails down the
   exact list with the Hebrew target for each.
2. **Final by-design duplicate-target set** — depends on the exact
   alias list. LOD400 §5 enumerates the post-patch
   `dict[Hebrew, list[English]]` mapping for AC-03.
3. **AC-04 coverage threshold** — set at ≥ 42/50 in §10 above
   (covers the 14 baseline + 28 aliases). LOD400 §9 confirms.

## 12. Sequencing into the program

```
WP-B1 (LOD500_LOCKED at 6a85561)
   ↓ unblocks
WP-B1-patch01 (this WP)  ← MUST close before B2 (team_00 directive)
   ↓ unblocks
WP-B2 (JMF PDF NI) + WP-B3 (Tend overlay) — parallel-eligible
```

WP-B2 and WP-B3 remain `PROPOSED` until patch01 reaches LOD500_LOCKED.

---

*LOD200 v1.0.0 — authored 2026-05-25 by team_110 under EXECUTION_MANDATE
SFA-S003-P002-WP-B (ADR045 R2 #1 — spec-author authority extends to
WPs nested under the mandate's program, of which this patch is part).*
*Next phase: LOD400 spec.*
