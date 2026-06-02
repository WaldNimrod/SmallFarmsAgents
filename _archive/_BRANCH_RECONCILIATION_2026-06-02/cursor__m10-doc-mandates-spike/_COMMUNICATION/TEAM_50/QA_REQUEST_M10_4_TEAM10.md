# QA Review Request — M10.4 Headless browser and mypips

**From:** Team 10  
**To:** Team 50 (QA)  
**Date (original):** 2026-04-04  
**Updated:** 2026-04-06 — **M13-PRE combined G-PRE gate:** use `_COMMUNICATION/TEAM_50/reports/2026-04-05_QA_REQUEST_M13_PRE_GPRE_TEAM10.md` for G-PRE-1..7 (Alembic **066**, gate script + waiver path). Prior Round-3 (R3) remediation; 2026-03-31 — P1/P2 evidence; 2026-03-30 — Round-2 handoff  
**Mandate:** `MANDATE-20260404-M10-4-HEADLESS-MYPIPS`

---

## Migration status (Team 10 — for Team 50 P1/P2)

Full migration was applied on the connected database; **no revisions pending** after `upgrade head`.

| Check | Command | Result |
|--------|---------|--------|
| P1 | `python3 -m alembic upgrade head` | Completed through **066** (CSA expansion **066** atop M13-PRE chain) |
| P1 | `python3 -m alembic current` | **`066 (head)`** |
| P2 | `python3 -m organic_market_agent.db.check` | **`RESULT: PASS`** |

Team 50 should run the same commands on the **QA target DB** before T01–T08 so P1 matches repo head **066** (or current tip).

---

## Round-3 re-review request (Team 50)

Team 10 requests a **fourth-pass** full execution of the M10.4 QA mandate after **Round-3** remediation:

- **Latest FAIL findings (re-review):** `_COMMUNICATION/TEAM_50/reports/2026-04-05_M10_4_QA_FINDINGS_TEAM50_R2.md` (QA-RPT-20260405-M10_4-R2)  
- **Prior remediation:** `_COMMUNICATION/TEAM_10/reports/2026-04-05_M10_4_QA_REMEDIATION_COMPLETE_TEAM10.md`, `_COMMUNICATION/TEAM_10/reports/2026-03-30_M10_4_QA_REMEDIATION_R2_TEAM10.md`  
- **Round-3 remediation (this submission):** `_COMMUNICATION/TEAM_10/reports/2026-04-05_M10_4_QA_REMEDIATION_R3_TEAM10.md`

**Please file a new findings report** (do not overwrite prior reports), for example:

`_COMMUNICATION/TEAM_50/reports/YYYY-MM-DD_M10_4_QA_FINDINGS_TEAM50.md`  
using `_COMMUNICATION/TEMPLATES/QA_FINDINGS_REPORT.md`.

**Preconditions for QA agent:** `python3 -m alembic current` → revision **066** or later; `pip install -r requirements.txt` on the **same** interpreter used for `python3 -m pytest`. Run coordinated ingestion as needed. Self-check: `scripts/verify_m10_4_gate.sh` (T03 **≥5** raw-row sources; G-PRE-1 printed; T05 **≥90** products unless **`M13_PRE_GPRE5_WAIVED=1`**).

---

## Validation ownership

Per project procedure, **M10.4 acceptance (AC1–AC8) is validated only by Team 50** using the canonical QA mandate below — typically an **autonomous QA agent**, not ad-hoc human checks and not Team 10 self-signoff.

Team 10 delivers implementation + evidence; **gate PASS / FAIL** is determined from the Team 50 findings report.

---

## Deliverables (Team 10)

1. Original completion: `_COMMUNICATION/TEAM_10/reports/2026-04-04_M10_4_COMPLETION_TEAM10.md`  
2. Round-1 QA remediation: `_COMMUNICATION/TEAM_10/reports/2026-04-05_M10_4_QA_REMEDIATION_COMPLETE_TEAM10.md`  
3. **Round-2 QA remediation:** `_COMMUNICATION/TEAM_10/reports/2026-03-30_M10_4_QA_REMEDIATION_R2_TEAM10.md`  
4. **Round-3 QA remediation:** `_COMMUNICATION/TEAM_10/reports/2026-04-05_M10_4_QA_REMEDIATION_R3_TEAM10.md`  
5. Forensics: `_COMMUNICATION/TEAM_10/reports/2026-04-05_M10_4_QA_REMEDIATION_FORENSICS_TEAM10.md`; R3 shell forensics: `_COMMUNICATION/TEAM_10/reports/2026-04-05_M10_4_R3_SHELL_FORENSICS_TEAM10.md`  
6. Code: `collectors/base.py`, `collectors/headless_browser.py`, `collectors/mypips.py`, `parsers/mypips.py`, collectors/parser engines as prior  
7. Tests: `tests/test_mypips_parser.py`, `tests/test_mypips_integration.py`; `tests/test_admin_routes.py` (`test_t09`)  
8. Migrations: head **`066_csa_shekel_line_template_and_aliases`** (see **065** mypips cache bust, **064** SRC034)  
9. Self-check script: `scripts/verify_m10_4_gate.sh`

---

## Canonical execution (Team 50 agent — required)

1. Open and execute **`_COMMUNICATION/TEAM_50/QA_MANDATE_M10_4_TEAM50.md`** (v1.1+; P1 expects Alembic **066** or current head) end to end.  
2. Produce a **new** `QA_FINDINGS_REPORT` under `_COMMUNICATION/TEAM_50/reports/`.  
3. Include **verbatim SQL outputs** and **command logs** for T01–T08 (and T09 if run) as evidence.  
4. If **T03** or **T05** depend on fresh ingestion, document whether a coordinated `run_ingestion` (nine priority sources) was run before SQL/count checks.

---

## After Team 50 PASS

Team 10 files or updates **`_COMMUNICATION/TEAM_100/reports/YYYY-MM-DD_M10_4_COMPLETION_NOTICE_TEAM10.md`** for architectural closure per M10.4 mandate §8. Human confirmation of live UIs remains with the project lead **after** artifacts and QA report are current.

---

## Note

`RUN_MYPIPS_E2E=1` integration tests require Chromium and live network; default CI skips E2E. Mandate **T09** is optional supplementary evidence.
