# Team 50 — Gate G3: Team 10 executed verification + re-review request

**Date:** 2026-03-30  
**From:** Team 10 (Feature Dev)  
**To:** Team 50 (QA)

Team 10 ran the commands below on the project workspace (with `source .env` / `DATABASE_URL` as configured). **Please re-run your mandate checks** using this evidence as supplementary; call **FAIL/BLOCKED** or **CONDITIONAL** with explicit test IDs.

---

## 1. T01 / regression — `pytest tests/`

**Command:**

```bash
cd /Users/nimrod/Documents/SmallFarmsAgents
set -a && source .env && set +a
python3.11 -m pytest tests/ -q
```

**Result (this run):**

```text
..............................................                           [100%]
46 passed in 0.51s
```

**Pass criterion:** 46 passed, 0 skipped — **met** on this host.

---

## 2. T02 — Normalizer CLI (current DB state)

**Command:**

```bash
python3.11 -m organic_market_agent run_normalizer
```

**Result (this run):**

```text
NormalizerEngine: resolved=0 unresolvable=0 skipped=0
```

**Interpretation:** There were **no** rows with `extraction_status='extracted'` at run time (pipeline already drained). This **does not** satisfy the mandate’s historical scenario where a full backlog was reset to `extracted`; it shows **idle** normalizer behavior only.

For **volume** criterion (`resolved ≥ 40`), Team 10 still observes **`normalized_observations` below 40** after prior full-normalizer passes (see §3). **T02/T03 critical thresholds remain at risk** until either:

- **B1:** sufficient `product_aliases` (and/or parser cleanup) so a **full** `extracted` backlog yields ≥ 40 resolutions, or  
- **B2 + governance:** QA accepts a **cohort-scoped** normalizer run (`--ingestion-run-id`) after a fresh ingestion that produces ≥ 40 resolvable rows, documented in the QA report.

---

## 3. T03 — `normalized_observations` + `raw_extracted_items` status

**Command:**

```bash
python3.11 -c "
from organic_market_agent.db.session import get_session
from sqlalchemy import text
with get_session() as s:
    n = s.execute(text('SELECT COUNT(*) FROM normalized_observations')).scalar()
    e = s.execute(text(\"SELECT COUNT(*) FROM raw_extracted_items WHERE extraction_status='extracted'\")).scalar()
    u = s.execute(text(\"SELECT COUNT(*) FROM raw_extracted_items WHERE extraction_status='unresolvable'\")).scalar()
    m = s.execute(text(\"SELECT COUNT(*) FROM raw_extracted_items WHERE extraction_status='normalized'\")).scalar()
    print('normalized_observations:', n)
    print('raw_extracted extracted:', e)
    print('raw_extracted unresolvable:', u)
    print('raw_extracted normalized:', m)
"
```

**Result (this run, ~2026-03-30):**

```text
normalized_observations: 6
raw_extracted extracted: 0
raw_extracted unresolvable: 1634
raw_extracted normalized: 6
```

**vs mandate T03:** `total ≥ 40` for `normalized_observations` — **not met** (6 rows).

**T07 alignment:** `extracted = 0` (all rows processed); large `unresolvable` cohort remains.

---

## 4. Phase A diagnosis — unresolvable root cause (executed)

**Command:**

```bash
python3.11 scripts/run_g3_phase_a_diagnosis.py
```

**Classification (from Q1 top prefixes on this DB):**

- **`empty raw_price_text`:** 128 rows (~22% of sampled top reasons) → **price / extraction** gap.  
- **Dominant remainder:** `no alias match for '…'` → **alias_resolver** / **non-product noise** in `raw_product_name` (course dates, cart UI chrome, blog text).  
- **Per-source (Q3):** heaviest `unresolvable` counts on **SRC013, SRC008, SRC009** (663 / 454 / 316) — **HTML / discovery** sources, not vegetable price grids.

**Verdict for remediation:** G3 **volume** failure is **data + source fitness**, not normalizer crash. Fixes are **aliases + parser/ignore rules + optional source gating**, or **mandate scoping** to a vegetable-ingestion cohort.

**Full script output** (Q1–Q3 tables) is long; Team 10 retains it in session logs. Re-run the same script on your QA host to reproduce verbatim files for the official QA report.

---

## 5. T09 — regression counts (snapshot, this run)

**Query:** per `QA_MANDATE_G3.md` T09 union.

**Result (this run):**

```text
measurement_units 11
products 29
sources 20
raw_assets 21
raw_extracted_items 1640
```

**Note:** M3 does not insert into `raw_assets` / `raw_extracted_items`. Any **delta** during a “normalizer-only” window implies **parallel ingestion** or **wrong baseline timing**. Team 10 recommends T09 on a **quiet DB** per `_COMMUNICATION/TEAM_10/reports/2026-03-30_G3_T09_QUIET_DB_PROTOCOL_TEAM10.md`.

---

## 6. ORM note (`unresolvable_reason`)

`RawExtractedItem.unresolvable_reason` is mapped to **`Text`** in `organic_market_agent/models/runs.py` to match migration **008**. DB remains source of truth.

---

## 7. Outcome requested from Team 50

1. Re-execute **QA_MANDATE_G3.md** (or **QA_MANDATE_G3_RERUN.md**) and file **`_COMMUNICATION/TEAM_50/reports/{date}_QA_G3_TEAM50.md`**.  
2. Explicitly score **T02, T03, T09** with reference to this attachment where helpful.  
3. If **CONDITIONAL PASS** is considered for G3 pending alias/selector work, state conditions and owners (Team 10 / Team 20 / Team 100).

---

## References (Team 10)

- Remediation procedures: `_COMMUNICATION/TEAM_10/reports/2026-03-30_G3_REMEDIATION_EXECUTION_PACK_TEAM10.md`  
- T09 protocol: `_COMMUNICATION/TEAM_10/reports/2026-03-30_G3_T09_QUIET_DB_PROTOCOL_TEAM10.md`  
- Diagnosis script: `scripts/run_g3_phase_a_diagnosis.py`
