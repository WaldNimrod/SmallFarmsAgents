---
document_type: QA_FINDINGS_REPORT
version: "1.0"
---

# QA Findings Report — M13-PRE gate G-PRE-1..7 (scoped)

**Report ID:** QA-RPT-20260405-M13-PRE-GPRE  
**QA Review Request:** `_COMMUNICATION/TEAM_50/reports/2026-04-05_QA_REQUEST_M13_PRE_GPRE_TEAM10.md`  
**From:** Team 50 (QA)  
**To:** Team 100 (Architecture)  
**CC:** Team 10 (Feature Dev), Nimrod (project lead)  
**Date:** 2026-04-05  
**Gate:** G-PRE-1..7 — data-readiness for M13-B only  
**QA Mandate executed:** `_COMMUNICATION/TEAM_50/QA_MANDATE_M13_PRE_GPRE_TEAM50.md`

---

## 1. Environment Verified

| Check | Result |
|-------|--------|
| Alembic | **066 (head)** — PASS (P1) |
| `db.check` | **RESULT: PASS** (P2) |
| `pip install -r requirements.txt` | **PASS** on `.venv` interpreter (P3) |
| Coordinated pipeline | `catalog_renormalize` + `run_publisher` executed **2026-04-04** session log (UTC timestamps in evidence) before G-PRE-5 count (P4) |
| Interpreter | `.venv/bin/python` used for pytest, publisher, SQL (consistent with deps) |

**Out of scope (§3) observed:** No full `QA_MANDATE_M10_4_TEAM50` re-run; no SRC075 audit; no legal/performance work beyond pytest.

---

## 2. Test Results (G-PRE-1..7)

| Test ID | Description | Result | Weight | Notes |
|---------|-------------|--------|--------|-------|
| G-PRE-1 | ≥5/9 mypips with `normalized_observations` | ✅ PASS | Critical | Exactly **5** codes with `norm_obs > 0`; PRE-D4 alignment **9/9** active |
| G-PRE-2 | Resolution ≥85% per evaluated source | ✅ PASS | Critical | All rows with `(norm+unres)>0` have `pct >= 85`; **SRC042, SRC055, SRC062, SRC069** absent from join → **N/A** (no extract rows in history), not FAIL |
| G-PRE-3 | ≥2 of SRC033–035 basket rows (latest run) | ✅ PASS | Critical | SRC033=3, SRC034=2, SRC035=0 — **INFO** SRC035=0 acceptable per §3 |
| G-PRE-4 | SRC036 resolution ≥85% | ✅ PASS | Critical | 100% (75 norm, 0 unres) |
| G-PRE-5 | Published products ≥90 | ✅ CONDITIONAL PASS | Critical | **76** products; **Team 100 written waiver:** `_COMMUNICATION/TEAM_100/reports/2026-04-05_ARCH_DECISION_GPRE5_PUBLISHED_PRODUCT_COUNT_WAIVER_TEAM100.md` (**ARCH-20260405-GPRE5-PRODUCT-COUNT-WAIVER**) — per `QA_MANDATE_M13_PRE_GPRE_TEAM50.md` §8 |
| G-PRE-6 | `pytest tests/ -q` | ✅ PASS | Critical | **183 passed, 5 skipped**, 0 failures |
| G-PRE-7 | `run_publisher --upload` + live HTTP 200 | ✅ PASS | Critical | FTPS **8 files** OK; `curl` **200** on `https://www.nimrod.bio/smallfarmsagent/` |

**Critical failures:** **0** (G-PRE-5 satisfied via Team 100 waiver on file).

---

## 3. Evidence (verbatim SQL + commands)

### Preconditions

```text
.venv/bin/python -m alembic current
066 (head)

.venv/bin/python -m organic_market_agent.db.check
RESULT: PASS

.venv/bin/pip install -r requirements.txt -q
(exit 0)
```

### G-PRE-1 — SQL (verbatim)

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

**Output:**

```text
('SRC041', 124)
('SRC042', 0)
('SRC053', 113)
('SRC055', 0)
('SRC060', 56)
('SRC061', 61)
('SRC062', 0)
('SRC069', 0)
('SRC070', 116)
```

**Count with `norm_obs > 0`:** **5** (passes **≥5**).

**PRE-D4 alignment SQL:**

```sql
SELECT code, is_active, status FROM sources WHERE code IN (
  'SRC041', 'SRC042', 'SRC053', 'SRC055', 'SRC060',
  'SRC061', 'SRC062', 'SRC069', 'SRC070'
) ORDER BY code;
```

**Output:** all nine rows `(code, True, 'active')` — **9 ≥ 5**.

---

### G-PRE-2 — SQL (verbatim)

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

**Output:**

```text
('SRC041', 124, 0, 100.0)
('SRC053', 113, 0, 100.0)
('SRC060', 56, 0, 100.0)
('SRC061', 61, 2, 96.8)
('SRC070', 116, 0, 100.0)
```

**Evaluation:** Every returned row has `pct >= 85`.  
**N/A (not FAIL):** **SRC042, SRC055, SRC062, SRC069** do not appear (no `raw_extracted_items` rows via join) — excluded per mandate **G-PRE-2** N/A rule.

---

### G-PRE-3 — SQL (verbatim)

```sql
SELECT s.code, COUNT(rei.id) AS raw_rows
FROM sources s
LEFT JOIN source_fetch_runs sfr ON sfr.source_id = s.id
  AND sfr.id = (SELECT MAX(id) FROM source_fetch_runs WHERE source_id = s.id)
LEFT JOIN raw_extracted_items rei ON rei.source_fetch_run_id = sfr.id
WHERE s.code IN ('SRC033','SRC034','SRC035')
GROUP BY s.code ORDER BY s.code;
```

**Output:**

```text
('SRC033', 3)
('SRC034', 2)
('SRC035', 0)
```

**Pass:** **2** codes with `raw_rows > 0` (meets **≥2**). **SRC035=0** documented as **INFO** only (§3).

---

### G-PRE-4 — SQL (verbatim)

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

**Output:**

```text
(75, 0, 100.0)
```

**Pass:** `pct >= 85` and `unres = 0`.

---

### G-PRE-5 — publish + count

**Command log (abridged):**

```text
.venv/bin/python -m organic_market_agent catalog_renormalize
... PublishEngine: wrote 76 products to output/public ...
```

**Count command:**

```bash
.venv/bin/python -c "import json; d=json.load(open('output/public/public_report.json')); print(len(d['products']))"
```

**Output:**

```text
76
```

**Pass criterion (literal):** **≥90** — **not met** (count **76**).  
**Waiver (binding):** Team 100 issued `_COMMUNICATION/TEAM_100/reports/2026-04-05_ARCH_DECISION_GPRE5_PUBLISHED_PRODUCT_COUNT_WAIVER_TEAM100.md` (**ARCH-20260405-GPRE5-PRODUCT-COUNT-WAIVER**). Per `QA_MANDATE_M13_PRE_GPRE_TEAM50.md` §8, **G-PRE-5** = **CONDITIONAL PASS**.

---

### G-PRE-6 — pytest

```bash
.venv/bin/python -m pytest tests/ -q
```

**Output:**

```text
183 passed, 5 skipped, 3 warnings in 17.38s
```

---

### G-PRE-7 — upload + live HTTP (M13-PRE §3.5 pattern)

**Upload log (abridged):**

```text
.venv/bin/python -m organic_market_agent run_publisher --upload
... FTPS upload OK: 8 files uploaded
```

**Live check:**

```bash
curl -sL -o /dev/null -w "%{http_code}" "https://www.nimrod.bio/smallfarmsagent/"
```

**Output:**

```text
200
```

---

## 4. Findings Summary

### Passed

- G-PRE-1, G-PRE-2 (with explicit N/A handling), G-PRE-3 (with SRC035 INFO), G-PRE-4, G-PRE-6, G-PRE-7.

### Failed

**None** — G-PRE-5 addressed by Team 100 waiver (see §5).

### Skipped tests (pytest)

| Count | Notes |
|-------|-------|
| 5 | Documented in pytest summary; no failures |

---

## 5. Gate Decision

### CONDITIONAL PASS — GATE G-PRE-1..7

**Reason:** All checks **G-PRE-1..4, G-PRE-6, G-PRE-7** **PASS**. **G-PRE-5** meets **CONDITIONAL PASS** per `QA_MANDATE_M13_PRE_GPRE_TEAM50.md` §8 with written Team 100 waiver:

- `_COMMUNICATION/TEAM_100/reports/2026-04-05_ARCH_DECISION_GPRE5_PUBLISHED_PRODUCT_COUNT_WAIVER_TEAM100.md`  
- **Decision ID:** `ARCH-20260405-GPRE5-PRODUCT-COUNT-WAIVER`

**Effect:** **M13-B** may proceed per QA mandate §9.

### 5.1 Historical note (audit)

Initial filing on **2026-04-05** recorded **FAIL** on G-PRE-5 because no Team 100 waiver was on file. **Same day**, Team 100 issued the waiver above; this report’s gate section is **authoritative** as revised.

---

## 6. Appendix (optional, non-gating)

- `len([p for p in products if 'grower' in (p.get('source_types') or [])])` = **76** on the same `public_report.json` used for G-PRE-5.

---

*Filed by: Team 50 (QA)*  
*Date: 2026-04-05*

---

## 7. Post-filing update — Team 100 G-PRE-5 waiver (2026-04-06)

**Binding waiver:** `_COMMUNICATION/TEAM_100/reports/2026-04-05_ARCH_DECISION_GPRE5_PUBLISHED_PRODUCT_COUNT_WAIVER_TEAM100.md` — **Decision ID:** **ARCH-20260405-GPRE5-PRODUCT-COUNT-WAIVER**.

**Effect:** **G-PRE-5** numeric floor (**≥90** published products) is **waived** per Team 100 architecture. **G-PRE-5** is satisfied via the **waiver path** in `QA_MANDATE_M13_PRE_GPRE_TEAM50.md` §3 (Waiver path) when this decision is cited in findings (see also CHANGELOG `[Unreleased]`).

**Recommended:** Team 50 may file a short **supplemental** findings row or re-run the scoped mandate once for a clean **CONDITIONAL PASS** / **PASS** artifact; **G11** may proceed referencing this waiver for **T06** product-count alignment.

*Recorded by: Team 10 (coordination) on behalf of process closure — 2026-04-06*  
*Gate decision revised: 2026-04-05 — Team 100 G-PRE-5 waiver (ARCH-20260405-GPRE5-PRODUCT-COUNT-WAIVER)*
