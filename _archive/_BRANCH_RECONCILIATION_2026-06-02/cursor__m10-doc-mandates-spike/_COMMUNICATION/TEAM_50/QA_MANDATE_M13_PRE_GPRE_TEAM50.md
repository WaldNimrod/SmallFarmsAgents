---
document_type: QA_MANDATE
version: "1.0"
---

# QA Mandate — M13-PRE gate G-PRE-1..7 (scoped)

**Mandate ID:** `QA-MANDATE-M13-PRE-GPRE-TEAM50`  
**From:** Project coordination (Team 10 handoff + Team 100 criteria in `MANDATE-20260404-M13-PRE-DATA-FOUNDATION`)  
**To:** Team 50 (QA) — **agent-executable**  
**CC:** Team 100 (Architecture), Team 10 (Feature Dev), Nimrod (project lead)  
**Date:** 2026-04-06  
**Priority:** CRITICAL  
**Gate:** **G-PRE-1..7** only — data-readiness for **M13-B** (public product details UI that depends on real pipeline data)  
**Status:** ACTIVE  

---

## 1. Purpose (why this document exists)

M13-B development is **waiting on a single, unambiguous data-readiness signal**. Team 50 must validate **only** the **seven** criteria in Team 100’s M13-PRE mandate §4 (`G-PRE-1`..`G-PRE-7`).  

This QA mandate **narrows scope** so QA does **not** re-execute legacy M10.4/M10.5 test matrices unless a check below explicitly requires it.

**Authoritative product criteria:** `_COMMUNICATION/TEAM_10/MANDATE_M13_PRE_DATA_FOUNDATION_TEAM10.md` §2–§4 (especially §4 combined gate table).  
**Team 10 evidence pack (non-binding):** `_COMMUNICATION/TEAM_10/reports/2026-04-05_M13_PRE_DATA_FOUNDATION_TEAM10.md`, `_COMMUNICATION/TEAM_50/reports/2026-04-05_QA_REQUEST_M13_PRE_GPRE_TEAM10.md`.

---

## 2. Binding rules for Team 50

1. **PASS / FAIL / CONDITIONAL PASS** are decided **only** on the **G-PRE-1..7** table in §5 below, using **verbatim SQL** and **commands** given here.  
2. **Team 10 self-signoff does not substitute** for Team 50 — re-run checks on the **QA target DB** and **artifact tree** you certify.  
3. If a check is **BLOCKED** (no DB, no FTPS, no network), record **BLOCKED** with reason; overall gate is **FAIL** or **CONDITIONAL PASS** per `_COMMUNICATION/TEMPLATES/QA_FINDINGS_REPORT.md` (project convention).  
4. **One** primary deliverable: a new **QA findings report** under `_COMMUNICATION/TEAM_50/reports/` using the canonical template, filename pattern `YYYY-MM-DD_M13_PRE_GPRE_QA_FINDINGS_TEAM50.md`.

---

## 3. Scope — IN (must execute)

| Area | What to validate |
|------|------------------|
| **G-PRE-1..7** | Each row in §5 — **once** per QA cycle |
| **Preconditions** | §4 — before SQL counts |
| **Waiver path** | **G-PRE-5** only — **CONDITIONAL PASS** allowed if **Team 100** has issued a **written** waiver for the **≥90 published products** criterion (reference document ID + path in findings). No informal verbal waiver. |

---

## 4. Scope — OUT (do not spend QA time here)

**Unless a G-PRE check below explicitly fails and root-cause needs it, do **not**:**

1. Re-run the full **`QA_MANDATE_M10_4_TEAM50.md`** suite (e.g. legacy **T03 ≥7** raw-row threshold for mypips — **not** a G-PRE criterion; G-PRE-1 uses **`normalized_observations`**).  
2. **FAIL** the gate solely because **SRC035** has **0** basket rows if **G-PRE-3** is met (**≥2** of SRC033–035 with `raw_rows > 0` on **latest** fetch run). SRC035 may remain 0 per CSA analysis policy §4.5 — document as **INFO**, not **FAIL** for G-PRE-3.  
3. Re-open **M10.5 AC2** organic **SKU count ≥20** — **waived** in M13-PRE §3.4 to **≥12**; **no further QA work** on AC2 beyond what’s needed to keep **SRC036** data sane for **G-PRE-4**.  
4. Audit **SRC075** (CSA template / `shekel_line_baskets`) — **candidate/inactive** by design; **not** part of G-PRE-3 unless Team 100 expands scope.  
5. **Product catalog philosophy** reviews, new farm discovery, or legal review of third-party sites — **out of scope**.  
6. **Performance / load** testing beyond **`pytest tests/ -q`**.  
7. **M13-A** publisher schema work — may proceed in parallel; **do not** block G-PRE on M13-A features.

---

## 5. Preconditions (execute first)

| ID | Check | Command / action | Pass |
|----|--------|------------------|------|
| P1 | Alembic at expected head | `python3 -m alembic current` | Revision **066** or **later** Team 20 head documented in findings if newer |
| P2 | DB health | `python3 -m organic_market_agent.db.check` | `RESULT: PASS` |
| P3 | Python deps | `pip install -r requirements.txt` (same interpreter as pytest) | No blocking errors |
| P4 | Coordinated pipeline (as needed) | If counts are stale, ops/Team 10 run `catalog_renormalize` + `run_publisher` before **G-PRE-5** / **G-PRE-12**-style JSON checks | Document timestamps in findings |

---

## 6. G-PRE checks (verbatim — PASS/FAIL each)

### G-PRE-1 — mypips: ≥5 of 9 with normalized observations

**Priority codes:** `SRC041`, `SRC042`, `SRC053`, `SRC055`, `SRC060`, `SRC061`, `SRC062`, `SRC069`, `SRC070`.

```sql
SELECT s.code, COUNT(DISTINCT no.id) AS norm_obs
FROM sources s
LEFT JOIN normalized_observations no ON no.source_id = s.id
WHERE s.code IN (
  'SRC041', 'SRC042', 'SRC053', 'SRC055', 'SRC060',
  'SRC061', 'SRC062', 'SRC069', 'SRC070'
)
GROUP BY s.code
ORDER BY s.code;
```

**Pass:** **≥5** rows with `norm_obs > 0`.  
**Also record:** `SELECT code, is_active, status FROM sources WHERE code IN (...)` — **≥5** with `is_active = true` AND `status = 'active'` (M13-PRE PRE-D4 alignment).

---

### G-PRE-2 — mypips: resolution ≥85% per **evaluated** source

```sql
SELECT s.code,
  COUNT(*) FILTER (WHERE rei.extraction_status = 'normalized') AS norm,
  COUNT(*) FILTER (WHERE rei.extraction_status = 'unresolvable') AS unres,
  ROUND(100.0 * COUNT(*) FILTER (WHERE rei.extraction_status = 'normalized') /
    NULLIF(COUNT(*) FILTER (WHERE rei.extraction_status IN ('normalized','unresolvable')), 0), 1) AS pct
FROM sources s
JOIN source_fetch_runs sfr ON sfr.source_id = s.id
JOIN raw_extracted_items rei ON rei.source_fetch_run_id = sfr.id
WHERE s.code IN (
  'SRC041', 'SRC042', 'SRC053', 'SRC055', 'SRC060',
  'SRC061', 'SRC062', 'SRC069', 'SRC070'
)
GROUP BY s.code
ORDER BY s.code;
```

**Pass:** For **every** `code` where `(norm + unres) > 0`, **`pct >= 85`**.  
**N/A (not FAIL):** If a source appears **only** with `norm = 0` and `unres = 0` (no rows in join), mark **N/A — no extract rows in history** and **exclude** from G-PRE-2 denominator for that source. Do **not** fail the gate for “no data” on an inactive or never-ingested code unless **G-PRE-1** already failed.

---

### G-PRE-3 — CSA: ≥2 of SRC033–035 with basket rows (latest run)

```sql
SELECT s.code, COUNT(rei.id) AS raw_rows
FROM sources s
LEFT JOIN source_fetch_runs sfr ON sfr.source_id = s.id
  AND sfr.id = (SELECT MAX(id) FROM source_fetch_runs WHERE source_id = s.id)
LEFT JOIN raw_extracted_items rei ON rei.source_fetch_run_id = sfr.id
WHERE s.code IN ('SRC033','SRC034','SRC035')
GROUP BY s.code ORDER BY s.code;
```

**Pass:** **≥2** codes with **`raw_rows > 0`**.  
**Note:** SRC035 = 0 alone is **not** a failure if pass is met (see §3 scope).

---

### G-PRE-4 — SRC036 resolution ≥85%

```sql
SELECT
  COUNT(*) FILTER (WHERE rei.extraction_status = 'normalized') AS norm,
  COUNT(*) FILTER (WHERE rei.extraction_status = 'unresolvable') AS unres,
  ROUND(100.0 * COUNT(*) FILTER (WHERE rei.extraction_status = 'normalized') /
    NULLIF(COUNT(*) FILTER (WHERE rei.extraction_status IN ('normalized','unresolvable')), 0), 1) AS pct
FROM raw_extracted_items rei
JOIN source_fetch_runs sfr ON sfr.id = rei.source_fetch_run_id
JOIN sources s ON s.id = sfr.source_id
WHERE s.code = 'SRC036';
```

**Pass:** `pct >= 85` **or** `norm > 0` and `unres = 0` (100%).  
**FAIL:** `pct < 85` when `(norm + unres) > 0`.

---

### G-PRE-5 — published product count ≥90

After `python3 -m organic_market_agent run_publisher` on the QA-certified workspace:

```bash
python3 -c "import json; d=json.load(open('output/public/public_report.json')); print(len(d['products']))"
```

**Pass:** **≥90** products.  
**CONDITIONAL PASS (only with Team 100 waiver):** If **<90**, cite **Team 100** written waiver for **G-PRE-5** / publish threshold in findings; otherwise **FAIL**.

---

### G-PRE-6 — regression tests

```bash
python3 -m pytest tests/ -q
```

**Pass:** **0 failures** (skipped tests allowed; document count).

---

### G-PRE-7 — live publish

**Pass:** `python3 -m organic_market_agent run_publisher --upload` completes successfully **and** HTTP **200** on the live public page check defined in M13-PRE §3.5 (or project publish runbook).  
**BLOCKED:** If FTPS/env missing — document; gate **FAIL** or **CONDITIONAL PASS** per template.

---

## 7. Optional informational checks (non-gating)

Record in findings appendix **only if time permits** — **must not** change PASS/FAIL:

- `len([p for p in d['products'] if 'grower' in (p.get('source_types') or [])])` (mypips visibility smoke).  
- SRC003 / `basket_only` row counts (extra basket signal — **not** G-PRE-3).

---

## 8. Gate outcome

| Outcome | Condition |
|---------|-----------|
| **PASS** | All **G-PRE-1..7** pass per §6, or **G-PRE-5** meets **CONDITIONAL PASS** with Team 100 waiver on file |
| **FAIL** | Any **G-PRE** hard fail without approved waiver |
| **CONDITIONAL PASS** | **G-PRE-5** only, with explicit Team 100 waiver reference |

---

## 9. After QA

- File findings under `_COMMUNICATION/TEAM_50/reports/` using `QA_FINDINGS_REPORT.md`.  
- On **PASS** / eligible **CONDITIONAL PASS**: Team 10 may file Team 100 **M13-PRE completion** notice per M13-PRE §5 step 5–6.  
- **M13-B** frontend work may proceed only after **PASS** (or approved **CONDITIONAL PASS** per above).

---

*This QA mandate is scoped to unblock **M13-B**; it does not replace Team 100’s full M13-PRE mandate for Team 10/20 implementation work.*
