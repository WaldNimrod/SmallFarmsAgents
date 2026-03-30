# Execution Mandate — Team 50: QA Gate G1, then Gate G2 (sequential)

**From:** Project Lead (Nimrod)  
**To:** Team 50 (QA)  
**Date:** 2026-03-30  
**Priority:** Critical — **G1 first**; **G2 only after G1 is formally open.**

---

## 1. Objective

1. **Open Gate G1** by executing `_COMMUNICATION/TEAM_50/QA_MANDATE_G1.md` on Team 20’s **compliant** environment and filing formal sign-off.  
2. **Only after G1 is open**, execute `_COMMUNICATION/TEAM_50/QA_MANDATE_G2.md` on the **same class of environment** (Python 3.11+, PostgreSQL 15+ **direct install**) and file a **new** G2 QA report.

This mandate does **not** replace the QA mandates; it defines **order**, **environment rules**, and **deliverable filenames**.

---

## 2. Hard rules (non-negotiable)

| Rule | Detail |
|------|--------|
| **Order** | Do **not** declare **G2 PASS** until `_COMMUNICATION/TEAM_50/reports/*_QA_G1_TEAM50.md` exists with **PASS** or **approved CONDITIONAL PASS** per G1 scoring. |
| **Environment** | G1 and G2 evidence must be produced with **Python ≥ 3.11** and **PostgreSQL ≥ 15** **direct install**. Runs on Python **below** 3.11 or **Docker-hosted Postgres** are **out of band** (may be noted as informal signal only) and **must not** satisfy T01 environment requirements. |
| **Independence** | Team 10’s evidence appendix and completion reports are **supplementary**. Team 50 **must** run mandate commands and capture **verbatim** CLI and SQL output on the validation host. |
| **Traceability** | Every PASS/FAIL/CONDITIONAL must map to mandate test IDs (G1: T01–T13; G2: per `QA_MANDATE_G2.md`). |

---

## 3. Phase A — Gate G1 only (start here)

### 3.1 Prerequisites

- [ ] Team 20 handoff received (`MANDATE_G1_GATE_UNBLOCK_TEAM20.md` completion report + connection details).  
- [ ] Environment preflight per `QA_MANDATE_G1.md` (“Environment Requirements”) — **stop and FAIL** if Docker Postgres is in use for the gate DB or Python is below 3.11.

### 3.2 Execution

Run **every** test **T01 through T13** in `_COMMUNICATION/TEAM_50/QA_MANDATE_G1.md` exactly as written (commands, SQL, pass criteria).

### 3.3 Deliverable

File:

`_COMMUNICATION/TEAM_50/reports/{date}_QA_G1_TEAM50.md`

Use the QA report structure in `_COMMUNICATION/TEAM_50/ONBOARDING.md`. Include:

- Dated environment block (Python, PostgreSQL, direct-install confirmation).  
- Pasted outputs for each T01–T13 (or explicit excerpt policy if outputs are huge — but Critical tests must be **fully** evidenced).  
- **Decision:** PASS / FAIL / CONDITIONAL PASS with conditions.  
- Explicit statement: **“Gate G1 is open”** or **“Gate G1 is not open”** and why.

**Scoring:** Per `QA_MANDATE_G1.md` — all **Critical** tests must PASS for a clean PASS.

---

## 4. Phase B — Gate G2 (only after §3.3 opens G1)

### 4.1 Prerequisites

- [ ] `*_QA_G1_TEAM50.md` on file with **PASS** or approved **CONDITIONAL PASS**.  
- [ ] Same environment class as §2 (3.11+, Postgres 15+ direct).  
- [ ] Team 10 completion report available: `_COMMUNICATION/TEAM_10/reports/2026-03-30_M2_COMPLETE_TEAM10.md` (or newer superseding report).

### 4.2 Execution

Run **full** `_COMMUNICATION/TEAM_50/QA_MANDATE_G2.md` (all test IDs listed there, including live ingestion and SQL checks). Do **not** stop at static/unit tests only.

**Note:** Ingestion summary lines may include `skipped=` counts (dedup). Evaluate pass/fail against the **mandate’s** criteria, not against outdated log excerpts in older Team 10 documents.

### 4.3 Deliverable

File a **new** dated report (do not overwrite the 2026-03-30 G2 archive):

`_COMMUNICATION/TEAM_50/reports/{date}_QA_G2_TEAM50.md`

Include:

- Reference to the **G1** report filename that unlocked G2.  
- Full mandate traceability (T01–T… per G2 mandate).  
- **Decision:** PASS / FAIL / CONDITIONAL for **Gate G2**.  
- If re-requesting implementation fixes, point to specific mandate IDs.

**Optional template** for the *review request* cycle (Team 10): `_COMMUNICATION/TEAM_10/reports/2026-03-30_G2_RERequest_AFTER_G1_TEMPLATE_TEAM10.md` — Team 50 does not file that; it is for Team 10 after G1 exists.

---

## 5. Escalation

| Issue | Route |
|-------|--------|
| Environment not stack-compliant | Team 20 (`MANDATE_G1_GATE_UNBLOCK_TEAM20.md`) |
| Spec / mandate ambiguity (e.g. dedup vs SQL counts) | Team 100 |
| Implementation defect with clear repro | Team 10 (with mandate ID and logs) |

---

## 6. References

| Document | Purpose |
|----------|---------|
| `_COMMUNICATION/TEAM_50/QA_MANDATE_G1.md` | G1 test definitions |
| `_COMMUNICATION/TEAM_50/QA_MANDATE_G2.md` | G2 test definitions |
| `_COMMUNICATION/ROADMAP.md` | Gate order and acceptance criteria |
| `_COMMUNICATION/TEAM_20/MANDATE_G1_GATE_UNBLOCK_TEAM20.md` | Team 20 obligation parallel to this mandate |
| `_COMMUNICATION/TEAM_10/reports/2026-03-30_M2_G2_EVIDENCE_APPENDIX_TEAM10.md` | Supplementary evidence only |

---

## 7. Acceptance (Project Lead)

- **G1 portion complete** when `*_QA_G1_TEAM50.md` is filed and **Gate G1** status is explicit.  
- **G2 portion complete** when `*_QA_G2_TEAM50.md` is filed **after** G1 open and **Gate G2** status is explicit.
