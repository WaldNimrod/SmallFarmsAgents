# L-GATE_V R2 VERDICT — SFA-S003-P002-WP-C3 — TEAM_190 — v1.0.1

**Date:** 2026-05-27  
**Author:** team_190  
**WP:** SFA-S003-P002-WP-C3  
**Type:** L-GATE_V R2 verdict  
**Gate:** L-GATE_V  
**Reviewed commit:** ffbc7fa  
**Engine:** GPT-5.5 / Cursor (non-Claude)  

## 0. Verdict Box

**VERDICT:** PASS  
**WP / Gate / Round:** SFA-S003-P002-WP-C3 / L-GATE_V / Round 2  
**Reviewed commit:** ffbc7fa  
**One-line next step:** Team 100 may close WP-C3 as LOD500_LOCKED and carry the documented source-inventory notes forward as non-blocking provenance.

## 1. Verdict Summary

SFA-S003-P002-WP-C3 passes L-GATE_V Round 2. The R1 BLOCKER F-C3-LV-01 is resolved: `scripts/validate_enrichment.py` now returns `CALIBRATED=5 MARGINAL=0 MISALIGNED=0`, and the Curtis Stone `days_to_maturity` rows are preserved with `confidence_weight=0` so they no longer shift the Israeli-context calibration harness.

The two R1 MAJOR evidence discrepancies are now sufficiently documented for closure: Curtis OCR processed 27/27 available images, and the FRANCHI audit explains 27 source rows with 21 reachable rows preserved and 6 source rows mapped to crops absent from the DB. No new blocking findings were identified.

## 2. Parameters

| Field | Value |
|---|---|
| Validator | team_190 |
| Engine | GPT-5.5 / Cursor, non-Claude |
| Builder/remediator | team_10 / Claude Sonnet 4.6 |
| Original blocked commit | `99c1971` |
| Remediation commit reviewed | `ffbc7fa` |
| R1 verdict | `_COMMUNICATION/TEAM_190/VERDICT_SFA-S003-P002-WP-C3_L-GATE_V_v1.0.0.md` |
| R2 remediation report | `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-C3/REMEDIATION_REPORT_v1.0.0.md` |
| Files read | `CLAUDE.md`; `_aos/governance/team_190.md`; `_aos/roadmap.yaml`; R1 verdict; remediation report; `curtis_profiles_importer.py` at `ffbc7fa` |
| Commands run | `git show --stat ffbc7fa`; `git show --name-only ffbc7fa`; `python3 scripts/validate_enrichment.py`; `python3 -m pytest tests/crop_book/test_c3_*.py`; `validate_aos.sh`; LOD500_LOCKED diff check; Curtis DTM DB confidence-weight query |

## 3. Criteria Table

| Check | Result | Evidence |
|---|---|---|
| F-C3-LV-01 remediation | PASS | `validate_enrichment.py` returned `Summary: 5 rows — CALIBRATED=5  MARGINAL=0  MISALIGNED=0`. |
| Curtis DTM moderation code | PASS | `curtis_profiles_importer.py:153` documents DTM field-specific moderation; `:160-161` upserts `days_to_maturity` with `confidence_weight=Decimal("0")`. |
| Curtis DTM live DB state | PASS | DB query: `Curtis DTM rows: 10`; `Curtis DTM rows with confidence_weight=0: 10`. |
| F-C3-LV-02 documentation | PASS | `REMEDIATION_REPORT_v1.0.0.md` states the repo contains 27 JPGs, so 27/27 available images were processed; the impossible ">=30 from 34" spec wording is documented as a source-inventory discrepancy. |
| F-C3-LV-03 audit | PASS | `REMEDIATION_REPORT_v1.0.0.md` provides a deterministic FRANCHI table: 27 source rows, 21 reachable rows preserved, 6 map misses for crops absent from DB. |
| Remediation commit scope | PASS | `git show --name-only ffbc7fa` lists only `_COMMUNICATION/TEAM_10/.../REMEDIATION_REPORT_v1.0.0.md` and `organic_market_agent/crop_book/importer/urban_farmer/curtis_profiles_importer.py`. Application-code scope is limited to the Curtis importer. |
| LOD500_LOCKED integrity | PASS | Protected-file diff check returned `LOCKED_MATCH_COUNT:0`. |
| Focused C3 tests | PASS | `python3 -m pytest tests/crop_book/test_c3_*.py` returned `12 passed, 7 warnings in 0.42s`. |
| AOS validation | PASS | `validate_aos.sh` returned `29 PASS / 19 SKIP / 0 FAIL`. |

## 4. Independent Command Evidence

### Remediation commit stat

```text
ffbc7fa fix(WP-C3/AC-C3-08): zero CurtisStone DTM blend weight — F-C3-LV-01 remediation
 .../REMEDIATION_REPORT_v1.0.0.md                   | 107 +++++++++++++++++++++
 .../urban_farmer/curtis_profiles_importer.py       |  12 ++-
 2 files changed, 115 insertions(+), 4 deletions(-)
```

### Remediation commit file list

```text
_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-C3/REMEDIATION_REPORT_v1.0.0.md
organic_market_agent/crop_book/importer/urban_farmer/curtis_profiles_importer.py
```

### Curtis DTM moderation evidence

```text
153:         # DTM — confidence_weight=0 so North American context does not shift
160:             _upsert(session, variety_id, "days_to_maturity", Decimal(dtm), unit="days",
161:                     note=note_str, confidence_weight=Decimal("0"))
```

```text
Curtis DTM rows: 10
Curtis DTM rows with confidence_weight=0: 10
```

### Enrichment calibration

```text
| ארוגולה      | 5          | days_to_maturity |  21.000000 |       21.0 |       0.0% | CALIBRATED  |
| ארוגולה      | 6          | days_to_maturity |  21.000000 |       21.0 |       0.0% | CALIBRATED  |
| ארוגולה      | 7          | days_to_maturity |  21.000000 |       21.0 |       0.0% | CALIBRATED  |
| ארוגולה      | 8          | days_to_maturity |  21.000000 |       21.0 |       0.0% | CALIBRATED  |
| ארוגולה      | 9          | days_to_maturity |  21.000000 |       21.0 |       0.0% | CALIBRATED  |

Summary: 5 rows — CALIBRATED=5  MARGINAL=0  MISALIGNED=0
```

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
======================== 12 passed, 7 warnings in 0.42s ========================
```

### AOS validation

```text
RESULT: 29 PASS / 19 SKIP / 0 FAIL
L-GATE_BUILD EXIT CRITERION: SATISFIED
```

### LOD500_LOCKED check

```text
LOCKED_MATCH_COUNT:0
```

## 5. R1 Findings Disposition

| Finding | R2 disposition | Evidence |
|---|---|---|
| F-C3-LV-01 — AC-C3-08 enrichment calibration regression | CLOSED | `validate_enrichment.py` is back to `CALIBRATED=5`; all Curtis DTM rows have `confidence_weight=0`. |
| F-C3-LV-02 — OCR source-count mismatch | CLOSED_AS_DOCUMENTED | The locked spec threshold is impossible against the repo's 27-image inventory; 27/27 available images were processed and the discrepancy is documented for provenance/spec cleanup. |
| F-C3-LV-03 — FRANCHI reference evidence mismatch | CLOSED_AS_AUDITED | The remediation report provides source-row accounting: 21 reachable rows preserved exactly once, 6 rows map to crops not present in DB, and the original "29" was a stale spec/source count. |

## 6. Constitutional Checks

| Check | Result | Evidence |
|---|---|---|
| IR#1 cross-engine | PASS | Builder/remediator is Claude-family; validator is GPT-5.5 / Cursor, non-Claude. |
| IR#4 roadmap writer | PASS | This verdict does not mutate `_aos/roadmap.yaml`; Team 100 owns status transition. |
| IR#6 artifact comms | PASS | R2 remediation is filed under `_COMMUNICATION/TEAM_10/...`; verdict is filed under Team 190 communication scope. |
| IR#7 data authority | PASS | R2 validation used read-only DB queries; remediation did not add migrations or new tables. |
| LOD500_LOCKED integrity | PASS | Remediation commit touched no protected application/governance files. |

## 7. Disposition and Next Step

**Disposition:** CLOSE_WP / LOD500_LOCKED.

Team 100 may close SFA-S003-P002-WP-C3. The only remaining action is provenance cleanup outside this gate: carry the Curtis 27-image inventory note and FRANCHI 27-row/21-preserved audit into any future spec/source-inventory reconciliation.

