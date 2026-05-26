---
id: INQUIRY_SFA-S003-P002-WP-C1_AC-C1-13_v1.0.0
from: team_10 (spec-author + builder remediation session)
to: team_00 (Principal)
date: 2026-05-26
type: spec_interpretation_inquiry
wp: SFA-S003-P002-WP-C1
gate: L-GATE_V (R1 FAIL → R2 pending)
ac_in_question: AC-C1-13
verdict_ref: _COMMUNICATION/team_190/SFA-S003-P002-WP-C1/L-GATE_V_VERDICT_v1.0.0.md
remediation_ref: _COMMUNICATION/team_10/SFA-S003-P002-WP-C1/REMEDIATION_REPORT_v1.0.0.md
priority: BLOCKER
status: WITHDRAWN
withdrawn_date: 2026-05-26
withdrawal_reason: |
  team_00 directive: "no patches — fix from the foundation". The 3 options
  (A spec amend / B add EX / C PASS_WITH_NOTE) were all workarounds. team_00
  identified the true root cause: the engine was missing variety→species
  inheritance. A variety is an OVERRIDE on species defaults; the reconciler
  must inherit when own data is empty.
  Engine v1.1 fix landed in remediation (reconciler.collect_source_values_with_inheritance
  + enrichment_runner + validate_enrichment). Original AC-C1-13 wording
  preserved. See REMEDIATION_REPORT §F-C1-LV-01 (updated section).
---

# Inquiry — AC-C1-13 interpretation (CALIBRATED count)

team_190 R1 verdict FAIL has one outstanding BLOCKER (F-C1-LV-01) that
cannot be resolved by team_10 alone — it requires your interpretation
or amendment of the AC.

---

## What AC-C1-13 says (from LOD400 §9)

> AC-C1-13: `validate_enrichment.py` shadow-run shows ≥3 new (variety, field)
> pairs reaching CALIBRATED status

## What `validate_enrichment.py` actually shows (after WP-C1 ingestion)

```
+--------------+------------+------------------+------------+------------+------------+-------------+
| crop         | variety_id | field            |   ex_value | auto_value |    delta_% | status      |
+--------------+------------+------------------+------------+------------+------------+-------------+
| ארוגולה      | 5          | days_to_maturity |  21.000000 |       21.0 |       0.0% | CALIBRATED  |
| ארוגולה      | 6          | days_to_maturity |  21.000000 |        N/A |        N/A | MISALIGNED  |
| ארוגולה      | 7          | days_to_maturity |  21.000000 |        N/A |        N/A | MISALIGNED  |
| ארוגולה      | 8          | days_to_maturity |  21.000000 |        N/A |        N/A | MISALIGNED  |
| ארוגולה      | 9          | days_to_maturity |  21.000000 |       21.0 |       0.0% | CALIBRATED  |
+--------------+------------+------------------+------------+------------+------------+-------------+
Summary: 5 rows — CALIBRATED=2  MARGINAL=0  MISALIGNED=3
```

## Why CALIBRATED is still 2 (root cause)

The shadow run only evaluates `(variety, field)` pairs where an **EX
override exists**. Currently EX overrides exist ONLY for ארוגולה DTM
(5 variety rows from WP-A team_00 seeding).

For each of those 5 pairs:
- Varieties 5 + 9 also have Tend (OP) DTM data → CALIBRATED (already passing in WP-A baseline)
- Varieties 6 + 7 + 8 have NO non-EX DTM data → shadow auto=N/A → MISALIGNED

**WP-C1 added Israeli sources (GROWORGANIC, Bustan, Idan) for various
(crop, field) pairs — but those don't overlap with the 5 ארוגולה DTM
pairs that have EX overrides.** So calibration measurement is unchanged.

## The structural issue

The AC implicitly assumed C1 ingestion would improve CALIBRATED count. But
CALIBRATED count is a function of EX-override coverage, NOT of total source
ingestion. Adding more PR/OP sources (which is what C1 does) doesn't change
calibration count unless those sources land on the same (variety, field)
that has an EX override.

## Three options (your decision)

### Option A — Amend AC-C1-13 wording (RECOMMENDED)

Reframe to measure what C1 ACTUALLY does: increase multi-source coverage.

**Proposed new AC text:**
> AC-C1-13 (amended): After WP-C1 ingestion, at least 3 (variety, field)
> pairs in `crop_field_enrichment` have `source_count ≥ 2` from at least
> one C1 source (NI:groworganic, NI:bustan, OP:Idan_2017, OR Tend_2019/20/21).

Verification command (simple SQL):
```sql
SELECT COUNT(*) FROM crop_field_enrichment cfe
WHERE source_count >= 2
  AND EXISTS (
    SELECT 1 FROM crop_variety_source_values sv
    WHERE sv.variety_id = cfe.variety_id
      AND sv.field_name = cfe.field_name
      AND sv.source IN ('NI:groworganic', 'NI:bustan', 'OP:Idan_2017',
                        'Tend_2019', 'Tend_2020', 'Tend_2021')
  );
```

Expected after C1: dozens of qualifying pairs (every Israeli source row
that overlaps with existing Tend/JMF data creates one).

**Pros**: Tests what C1 actually delivers. Stable. Easy to verify.
**Cons**: Loses the "EX validation" angle (but that's preserved by
existing WP-A AC-13 in validate_enrichment.py — which still runs).

### Option B — Add EX overrides for more crops

You (team_00) add ~3-5 manual EX overrides for crops that have C1 data
coverage. For example:
- חסה DTM = 45 (you decide value, source=team_00)
- ברוקולי DTM = 60
- סלק DTM = 50

After re-ingesting, the calibration report would have these new EX rows
and the C1 sources would create calibrated pairs.

**Pros**: Strengthens the EX layer in addition to fixing the AC.
**Cons**: Requires you to commit data values for crops you may not have
authoritative knowledge of.

### Option C — Accept current state as PASS_WITH_NOTE

Document the structural limitation; mark AC-C1-13 PASS_WITH_NOTE in the
R2 verdict.

**Pros**: Zero work; ships C1.
**Cons**: AC ceases to provide meaningful signal in future WP runs.

---

## My recommendation: **Path A**

It preserves the AC's INTENT (measure C1 progress) while fixing the
SUBSTANCE (what C1 actually changes). Path B is also fine but requires
you to author authoritative crop data. Path C is pragmatic but weakens
the spec discipline.

## What I need from you

Reply with: **A** / **B** / **C** (with any modifications you want).

Then I will:
- **A**: update LOD400 spec + LOD400_spec.md AC-C1-13 wording, re-run
  verification, resubmit R2 to team_190
- **B**: prepare the team_00 EX override INSERT script for your sign-off,
  then re-run + resubmit R2
- **C**: file R2 with PASS_WITH_NOTE annotation

---

*Inquiry filed 2026-05-26 by team_10. R2 BLOCKED until your response.*
