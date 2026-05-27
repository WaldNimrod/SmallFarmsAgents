# L-GATE_V VERDICT — SFA-S003-P002-WP-C3 — TEAM_190 — v1.0.0

**Date:** 2026-05-27  
**Author:** team_190  
**WP:** SFA-S003-P002-WP-C3  
**Type:** L-GATE_V verdict  
**Gate:** L-GATE_V  
**Reviewed commit:** 99c1971  
**Engine:** GPT-5.5 / Cursor (non-Claude)  

## 0. Verdict Box

**VERDICT:** BLOCKED  
**WP / Gate:** SFA-S003-P002-WP-C3 / L-GATE_V  
**Reviewed commit:** 99c1971  
**One-line next step:** Return to build/remediation for AC-C3-08 enrichment regression and tighten the C3 source-count acceptance evidence before re-submission.

## 1. Verdict Summary

SFA-S003-P002-WP-C3 is **BLOCKED** at L-GATE_V. The focused C3 test suite passes and most source-ingestion targets are present in the live DB, but the final gate cannot close because independent execution of `scripts/validate_enrichment.py` shows an enrichment calibration regression: `CALIBRATED=1`, `MARGINAL=4`, `MISALIGNED=0`, while AC-C3-08 requires no regression versus the C1+C2 baseline.

Two additional non-blocking but material specification-evidence discrepancies remain: AC-C3-02's locked threshold says at least 30 OCR JSONs from 34 images, but the repo contains 27 image files and 27 chart JSONs; AC-C3-05 says 29 FRANCHI variety references inserted, but the live DB has 9 aggregate rows and 21 pipe-separated variety entries observed in `value_text`.

## 2. Parameters

| Field | Value |
|---|---|
| Validator | team_190 |
| Engine | GPT-5.5 / Cursor, non-Claude |
| Builder | team_10 / sfa_build / Claude Sonnet 4.6 per build report |
| Reviewed commit | `99c1971` |
| Current workspace HEAD observed | `3c4d1a5` |
| Files read | `CLAUDE.md`; `_aos/governance/team_190.md`; `_aos/roadmap.yaml` C3 entry; `_aos/work_packages/S003/SFA-S003-P002-WP-C3/LOD400_spec.md`; `BUILD_REPORT_v1.0.0.md`; `L49_DIFF_REPORT.md`; `TEND_2018_INVESTIGATION.md`; `OCR_RUN_LOG.md`; `scripts/validate_enrichment.py` |
| Commands run | `pytest tests/crop_book/test_c3_*.py`; C3 DB count queries; Curtis OCR file counts; LOD500_LOCKED commit diff check; `validate_aos.sh`; `scripts/validate_enrichment.py` |

## 3. Acceptance Criteria Table

| AC | Result | Evidence |
|---|---|---|
| AC-C3-01 | PASS | Live DB query: `OP:CurtisStone rows: 38` (target >=20). |
| AC-C3-02 | PASS_WITH_FINDING | File count: `curtis_ocr_chart_json_count: 27`, `curtis_image_count: 27`. This is 100% of available repo images, but does not meet the locked text of ">=30 cached JSONs (out of 34 images)"; see finding F-C3-LV-02. |
| AC-C3-03 | PASS | Live DB query: `NI:curtis_stone_book notes: 10` (target >=10). OCR log confirms tesseract fallback and keyword-scan compensation. |
| AC-C3-04 | PASS | Live DB query: `OP:Idan_seedlings rows: 11` (target >=8). |
| AC-C3-05 | PASS_WITH_FINDING | Live DB query: `OP:FRANCHI_catalog rows: 9`; observed pipe-separated variety entries total 21. This does not match the locked "29 variety references inserted"; see finding F-C3-LV-03. |
| AC-C3-06 | PASS | Live DB query: `OP:Idan_2018 rows: 16`, `OP:Idan_2018 duplicate keys: 0`; `L49_DIFF_REPORT.md` filed. |
| AC-C3-07 | PASS | `TEND_2018_INVESTIGATION.md` filed; live DB has `Tend_2018 source rows: 14`, `Tend_2018 task rows: 37`; investigation explains 0 harvest stats because HARVESTS file is header-only. |
| AC-C3-08 | FAIL | Independent `python3 scripts/validate_enrichment.py` returned `Summary: 5 rows — CALIBRATED=1  MARGINAL=4  MISALIGNED=0`. This is a regression from the accepted C1/C2 calibration behavior and blocks final validation. |
| AC-C3-09 | PASS | `python3 -m pytest tests/crop_book/test_c3_*.py` collected 12 items and returned `12 passed, 7 warnings in 0.41s`. |
| AC-C3-10 | PASS | `validate_aos.sh` returned `29 PASS / 19 SKIP / 0 FAIL`. |

## 4. Independent Command Evidence

### Focused C3 tests

```text
collected 12 items
tests/crop_book/test_c3_curtis_ocr.py ..                                 [ 16%]
tests/crop_book/test_c3_curtis_profiles.py ...                           [ 41%]
tests/crop_book/test_c3_franchi.py .                                     [ 50%]
tests/crop_book/test_c3_idan_2018_diff.py .                              [ 58%]
tests/crop_book/test_c3_idan_seedlings.py ..                             [ 75%]
tests/crop_book/test_c3_integration.py .                                 [ 83%]
tests/crop_book/test_c3_tend_2018.py ..                                  [100%]
======================== 12 passed, 7 warnings in 0.41s ========================
```

### Live DB count checks

```text
OP:CurtisStone rows: 38
NI:curtis_stone_book notes: 10
OP:Idan_seedlings rows: 11
OP:FRANCHI_catalog rows: 9
OP:Idan_2018 rows: 16
Tend_2018 source rows: 14
Tend_2018 task rows: 37
OP:Idan_2018 duplicate keys: 0
```

### Curtis OCR file counts

```text
curtis_ocr_chart_json_count: 27
curtis_ocr_log_present: True
curtis_image_count: 27
```

### LOD500_LOCKED inventory check

```text
LOCKED_MATCH_COUNT:0
```

### Enrichment validation

```text
| ארוגולה      | 6          | days_to_maturity |  21.000000 |       28.0 |      33.3% | MARGINAL    |
| ארוגולה      | 7          | days_to_maturity |  21.000000 |       28.0 |      33.3% | MARGINAL    |
| ארוגולה      | 8          | days_to_maturity |  21.000000 |       28.0 |      33.3% | MARGINAL    |
| ארוגולה      | 9          | days_to_maturity |  21.000000 |       28.0 |      33.3% | MARGINAL    |

Summary: 5 rows — CALIBRATED=1  MARGINAL=4  MISALIGNED=0
```

### AOS validation

```text
RESULT: 29 PASS / 19 SKIP / 0 FAIL
L-GATE_BUILD EXIT CRITERION: SATISFIED
```

## 5. Findings

### F-C3-LV-01 — BLOCKER — AC-C3-08 enrichment calibration regressed

**Evidence:** `python3 scripts/validate_enrichment.py` returns `CALIBRATED=1`, `MARGINAL=4`, `MISALIGNED=0`. The marginal rows are arugula `days_to_maturity` calibrations where EX value is 21.0 and the shadow auto value is 28.0.

**Why this blocks:** AC-C3-08 requires reconciler blend stability and no regression versus the C1+C2 baseline. This check is specifically designed to catch non-EX source additions shifting auto-reconciled values away from expert overrides. WP-C3's added secondary source data appears to have shifted the shadow consensus enough to degrade four of five calibration rows.

**Additional trace:** Direct source-value inspection shows an added `OP:CurtisStone` `days_to_maturity=35` row for arugula variety id 9 alongside the existing `Tend=21` and `team_00=21` rows. The current persisted `crop_field_enrichment` rows still show EX-winning value 21, but the required shadow calibration harness excludes EX by design and now reports the regression.

**Required remediation:** Adjust WP-C3 ingestion/reconciliation treatment so new Curtis Stone values do not regress the accepted calibration harness. Candidate approaches include field/source-specific moderation, outlier handling, or source weighting policy consistent with existing `FIELD_POLICY`; do not patch the validation script.

### F-C3-LV-02 — MAJOR — AC-C3-02 locked threshold not met as written

**Evidence:** LOD400 AC-C3-02 requires `>=30 cached JSONs (out of 34 images; >=88% success)`. Independent file counts show 27 chart JSONs and 27 source images. `OCR_RUN_LOG.md` documents the source inventory discrepancy and 100% processing of available images.

**Disposition:** This is not the blocking defect because all available repo images were processed and AC-C3-03 still reaches 10 notes, but the LOD400 acceptance text and build evidence no longer align. Team 100/team_10 should either amend the acceptance record to "27/27 available images" or supply the missing source images before closure.

### F-C3-LV-03 — MAJOR — AC-C3-05 evidence does not prove 29 FRANCHI references inserted

**Evidence:** LOD400 AC-C3-05 requires 29 FRANCHI variety references inserted. `BUILD_REPORT_v1.0.0.md` says the actual file has 27 rows and the implementation stores 9 per-crop aggregate rows. Independent DB checks show `OP:FRANCHI_catalog rows: 9`; counting pipe-separated entries in `value_text` produced 21 observed entries, not 27 or 29.

**Disposition:** This may be an implementation shape decision constrained by `uq_cvsv_variety_field_source`, but it is not yet evidence-equivalent to the locked AC. Re-submission should include a deterministic source-row-to-DB-preservation audit showing every actual FRANCHI source row is preserved exactly once, or revise the AC through the proper spec path.

## 6. Constitutional Checks

| Check | Result | Evidence |
|---|---|---|
| IR#1 cross-engine | PASS | Builder is Claude Sonnet 4.6 per `BUILD_REPORT_v1.0.0.md`; validator is GPT-5.5 / Cursor, non-Claude. |
| IR#4 roadmap writer | PASS | This verdict does not mutate `_aos/roadmap.yaml`; Team 190 routes status changes to Team 100. |
| IR#6 artifact comms | PASS | Build artifacts are filed under `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-C3/`; verdict is filed under Team 190 communication scope. |
| IR#7 data authority | PASS | No new DB tables or migrations in reviewed commit; live validation used read-only queries. |
| LOD500_LOCKED integrity | PASS | Reviewed commit `99c1971` produced `LOCKED_MATCH_COUNT:0` for the protected file set. |

## 7. Disposition and Next Step

**Disposition:** RETURN_TO_BUILD / REMEDIATION_REQUIRED.

Team 10 should remediate F-C3-LV-01 first, then re-submit with updated evidence for AC-C3-02 and AC-C3-05. Team 190 should re-run the focused C3 tests, DB counts, `validate_enrichment.py`, and `validate_aos.sh` before any LOD500_LOCKED close.

