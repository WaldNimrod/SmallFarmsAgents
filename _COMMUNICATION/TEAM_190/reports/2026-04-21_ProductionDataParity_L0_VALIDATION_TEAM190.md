---
document_type: validation_result
version: "1.0"
---

# L0 / ops validation result — production data parity and uPress path

**Validation request:** [`../inbox/2026-04-21_VALIDATION_REQUEST_PRODUCTION_DATA_PARITY_TEAM10.md`](../inbox/2026-04-21_VALIDATION_REQUEST_PRODUCTION_DATA_PARITY_TEAM10.md)  
**From:** Team 190 (Constitutional / validation)  
**Date:** 2026-04-21  
**Subject:** `UPRESS_PUBLIC_BASE` / `UPRESS_UPLOAD_PATH` alignment, optional `ftps_upload` verify and ezCache hooks, documentation — **in-repo scope only** (not a new LOD200 product package).

---

## 1. Checks performed

| # | Requirement | Outcome |
|---|-------------|---------|
| 1 | AOS lean-kit: `validate_aos.sh .` — 0 FAIL | **PASS** — 26 PASS / 9 SKIP / 0 FAIL (this spoke; 0 FAIL satisfies L-GATE_BUILD criterion) |
| 2 | No cross-product leakage; SFA-only changes | **PASS** — `validate_aos` cross-project check PASS; request scope is `organic_market` / uPress / docs |
| 3 | File-first L0 / ADR034 — no hand-edited AOS DB as SSoT | **PASS** — no change in this work to contravent; roadmap intent unchanged (spot-check) |
| 4 | Inbox / package hygiene | **PASS** — request is filed in `TEAM_190/inbox/` with clear scope boundary |

**Parallel QA:** Team 50 ops parity report: [`../../TEAM_50/reports/2026-04-21_ProductionParity_QA_FINDINGS_TEAM50.md`](../../TEAM_50/reports/2026-04-21_ProductionParity_QA_FINDINGS_TEAM50.md).

---

## 2. Conditions (operational, not governance defects)

- **Public HTTPS** may lag **FTP** or host artifacts due to **CDN/ezCache** — outside strict repo control. Remediation: **uPress site cache purge** (or optional env-driven ezCache POST as documented). This does not invalidate the FTPS path alignment.  
- **No** repo change to publish “gates” or `INDEX_WINDOW_DAYS` is required for validation acceptance.

---

## 3. Outcome

**CONDITIONAL ACCEPT**

- **Governance / procedure:** **ACCEPT** for L0/ops parity: changes stay within SFA, `validate_aos` passes, ADR intent preserved.  
- **Condition:** Operators accept **cache purge** (or optional automation) when public HTTPS lags confirmed FTP.

**Team 100 escalation:** **Not required** for this item — no ADR conflict or cross-product boundary breach identified.

---

*Recorded by: Team 190*  
*Date: 2026-04-21*  
*Language: English (inter-team artifacts)*
