---
document_type: QA_REVIEW_REQUEST
version: "1.0"
---

# QA Review Request — M13-PRE combined gate G-PRE-1..7

**Request ID:** QA-REQ-20260405-M13-PRE-GPRE  
**From:** Team 10  
**To:** Team 50 (QA)  
**Date:** 2026-04-05  
**Gate:** G-PRE-1..7 — M13-PRE Data Foundation (`_COMMUNICATION/TEAM_10/MANDATE_M13_PRE_DATA_FOUNDATION_TEAM10.md` §4)  
**Milestone:** M13-PRE (prerequisite to M13-B)  
**Priority:** CRITICAL  

---

## 1. What was completed

| Team | Mandate | Completion / evidence |
|------|---------|------------------------|
| Team 10 | `MANDATE_M13_PRE_DATA_FOUNDATION_TEAM10.md` | `_COMMUNICATION/TEAM_10/reports/2026-04-05_M13_PRE_DATA_FOUNDATION_TEAM10.md` |
| Team 10 | M10.4 (headless mypips) | Same report §3; prior R3 docs referenced in `QA_REQUEST_M10_4_TEAM10.md` |
| Team 10 | M10.5 (CSA + Teva) | Same report §§1–2; prior M10.5 QA request `QA_REQUEST_M10_5_TEAM10.md` |

---

## 2. Preconditions (Team 10 verified on dev DB)

- [x] `python3 -m alembic upgrade head` → revision **066** (`066_csa_shekel_line_template_and_aliases`)
- [x] `python3 -m organic_market_agent.db.check` → **PASS**
- [x] `python3 -m pytest tests/ -q` → **180 passed**, 0 failed (5 skipped)
- [x] Mandate §3.1 CSA SQL — SRC033 & SRC034 with `raw_rows > 0` (2 of 3); SRC035 documented 0 SKU by parser policy
- [x] Mandate §3.2 SRC036 resolution SQL — **≥85%** (local: 100% on normalized+unresolvable set)
- [x] G-PRE-1 — ≥5 of 9 priority mypips codes with `normalized_observations` > 0
- [x] G-PRE-2 — PRE-D9 resolution ≥85% for sources that have (normalized+unresolvable) rows

**G-PRE-5:** Published product count **76** after renormalize + publish — **below 90**. Team 10 requests QA classification with **Team 100 G-PRE-5 waiver** path documented in completion report. Self-check: `M13_PRE_GPRE5_WAIVED=1 ./scripts/verify_m10_4_gate.sh`.

**G-PRE-7:** `run_publisher --upload` not executed from this environment; Team 50 or operator to run per mandate §3.5 when credentials/network allow.

---

## 3. Known issues

| Issue | Impact | Expected QA behavior |
|-------|--------|----------------------|
| Four mypips stores (042,055,062,069) still 0 `normalized_observations` | MEDIUM | G-PRE-1 still met at 5/9; flag if stricter coverage required |
| `public_report.json` product count 76 | HIGH for literal G-PRE-5 | FAIL unless Team 100 issues G-PRE-5 waiver or accepts rolling-window ceiling |
| SRC035 0 basket SKUs | LOW for §3.1 | Acceptable if 2-of-3 rule read as SRC033+SRC034 |

---

## 4. Request to Team 50

**Canonical executor document (scoped):** `_COMMUNICATION/TEAM_50/QA_MANDATE_M13_PRE_GPRE_TEAM50.md` — run **only** G-PRE-1..7 with verbatim SQL; **out-of-scope** items are explicit (legacy M10.4 T03≥7, SRC035-only FAIL, SRC075 audit, etc.).

Execute validation per that QA mandate. File findings using `_COMMUNICATION/TEMPLATES/QA_FINDINGS_REPORT.md` (new dated report under `_COMMUNICATION/TEAM_50/reports/`).

**Team 50 findings (executed 2026-04-05):** `_COMMUNICATION/TEAM_50/reports/2026-04-05_M13_PRE_GPRE_QA_FINDINGS_TEAM50.md` — **gate CONDITIONAL PASS** (G-PRE-5: Team 100 waiver `_COMMUNICATION/TEAM_100/reports/2026-04-05_ARCH_DECISION_GPRE5_PUBLISHED_PRODUCT_COUNT_WAIVER_TEAM100.md`).

---

## 5. SQL / commands reference (verbatim from mandate)

Team 10 executed the mandate §3.1 and §3.2 verification queries; Team 50 should re-run on the QA target database. PRE-D9 SQL is in mandate §2.3.

---

**Related QA requests (context):** `QA_REQUEST_M10_4_TEAM10.md`, `QA_REQUEST_M10_5_TEAM10.md` — superseded for **G-PRE** scope by this combined request.
