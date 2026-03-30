# Team 10 — G3 remediation execution pack (T02 / T03 / T09)

**Date:** 2026-03-30  
**Reference plan:** G3 QA remediation (Phase A–E).  
**Context:** After full QA reset to `extracted`, normalizer reported `resolved=4`, ~1635 `unresolvable`, failing T02/T03 (`≥40` observations). T09 count drift suggests non-isolated DB or parallel M2.

**Executed verification (same date):** Team 10 ran `pytest tests/`, `scripts/run_g3_phase_a_diagnosis.py`, `run_normalizer`, and T03/T09 count queries on the configured dev DB; results and re-review request for Team 50 are in [_COMMUNICATION/TEAM_50/reports/2026-03-30_G3_TEAM10_EXECUTED_EVIDENCE_REREVIEW_TEAM50.md](../../TEAM_50/reports/2026-03-30_G3_TEAM10_EXECUTED_EVIDENCE_REREVIEW_TEAM50.md).

---

## Phase A — Diagnosis (mandatory before seed/code bets)

### Automated run

```bash
cd /path/to/SmallFarmsAgents
set -a && source .env && set +a
python3.11 scripts/run_g3_phase_a_diagnosis.py | tee /tmp/g3_phase_a.txt
```

Paste **`/tmp/g3_phase_a.txt`** (or equivalent) into the Team 50 G3 evidence bundle.

### Manual SQL (same queries as script)

```sql
SELECT LEFT(COALESCE(unresolvable_reason, '(null)'), 120) AS reason_prefix,
       COUNT(*) AS cnt
FROM raw_extracted_items
WHERE extraction_status = 'unresolvable'
GROUP BY 1
ORDER BY cnt DESC
LIMIT 30;
```

```sql
SELECT raw_product_name, COUNT(*) AS cnt
FROM raw_extracted_items
WHERE extraction_status = 'unresolvable'
GROUP BY 1
ORDER BY cnt DESC
LIMIT 50;
```

```sql
SELECT s.code, COUNT(*) AS unresolvable_cnt
FROM raw_extracted_items rei
JOIN source_fetch_runs sfr ON sfr.id = rei.source_fetch_run_id
JOIN sources s ON s.id = sfr.source_id
WHERE rei.extraction_status = 'unresolvable'
GROUP BY s.code
ORDER BY unresolvable_cnt DESC;
```

### Exit criterion

One short paragraph: dominant failure mode (alias vs price_parse vs missing `display_unit` / `product_id`), backed by Q1–Q3. The diagnosis script prints a **draft** mix — **verify** against the Q1 table before signing.

---

## Phase B — Remediation tracks

### B1 — Data / seed (full backlog)

1. Use Q2 **top `raw_product_name`** values.  
2. Map to catalog products per `docs/PRODUCT_CATALOG_V1.md`; add `product_aliases` (global `source_id IS NULL` or per-source) via Team 20 migration or controlled SQL. SQL shape examples: [`scripts/g3_alias_backfill_template.sql`](../../../scripts/g3_alias_backfill_template.sql).  
3. Set affected rows to `extracted`, re-run normalizer; iterate until **`resolved ≥ 40`** and T03 passes.

### B2 — Scoped normalizer (cohort)

After an ingestion that yields **≥ 40** valid `raw_extracted_items`:

```bash
python3.11 -m organic_market_agent run_normalizer --ingestion-run-id <ID>
```

If Team 50 accepts **cohort-scoped** T02/T03, document the chosen `ingestion_run_id` in the QA report. If mandate stays **DB-wide**, B1 (or governance below) is required.

### B3 — Code changes

Only if Phase A proves a specific parser/normalizer gap. **Normalizer matching semantics** changes need Team 100 sign-off.

### Governance

If the project **will not** backfill aliases for the entire historical backlog, **G3 cannot pass** on “reset all rows to `extracted`” without **mandate amendment** (scoped T02/T03) or **archival / exclusion** of old rows. Escalate Nimrod / Team 100.

---

## Phase C — T09 on a quiet database

1. **Dedicated QA DB** or single writer; **no** parallel `run_ingestion`, cron, or second tester.  
2. Run T09 SQL **immediately before** the G3 action under test (e.g. normalizer-only pass).  
3. Run T09 **immediately after**; if ingestion is part of the scenario, baseline **before** ingestion and **document expected deltas** on `raw_assets` / `raw_extracted_items`.  
4. **M3 does not insert** into those tables — unexplained `+2` rows imply **concurrent M2** or wrong baseline timing.

---

## Phase D — ORM alignment (applied in repo)

`raw_extracted_items.unresolvable_reason` is **TEXT** in DB (revision **008**). SQLAlchemy model updated to **`Text`** in `organic_market_agent/models/runs.py`. Team 20 notified in a dated report (cosmetic consistency).

---

## Phase E — Verification checklist

| Step | Command / artifact | Pass |
|------|-------------------|------|
| 1 | Phase A output attached | Yes |
| 2 | B1 and/or B2 (and B3 if any) applied | |
| 3 | `python3.11 -m pytest tests/ -q` | 46 passed, 0 skipped |
| 4 | T02 | `resolved ≥ 40` (per mandate wording) |
| 5 | T03 SQL | `total ≥ 40`, integrity |
| 6 | T09 | Quiet-DB protocol, explained deltas |
| 7 | Team 50 | `2026-03-30_G3_REVIEW_REQUEST_RERUN_TEAM50.md` |

---

## QA attachment placeholder (operator fills after run)

**Classification paragraph:**  
_(paste after Phase A)_

**Phase A raw output:**  
_(paste script tee or SQL results)_
