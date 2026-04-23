---
document_type: VALIDATION_REQUEST
title: "SFA — Production data parity and publish-path guardrails (L0)"
from_team: "Team 10"
to_team: "Team 190"
date: "2026-04-21"
status: "pending_review"
---

# Validation request (constitutional / procedure) — Team 190

**Note:** The project’s validator role is **Team 190** (sfa_val). There is no “Team 90” in the SFA roster; this package is filed for **Team 190**.

**From:** Team 10 (OrganicMarketAgent implementation / operations)  
**To:** Team 190 (Constitutional / validation review)  
**Date:** 2026-04-21  
**Subject:** Cross-check that **AOS repo hygiene**, **uPress publish path alignment**, and **guardrails** in `ftps_upload` meet governance and do not break `validate_aos.sh` expectations for declarations.

---

## 1. Scope

1. **Production parity fix:** `UPRESS_UPLOAD_PATH=wp-content/uploads/market` and `UPRESS_PUBLIC_BASE` site origin — consistent with WordPress shortcode in [`scripts/wp_shortcode_install.py`](../../../scripts/wp_shortcode_install.py).
2. **Optional automation:** `UPRESS_VERIFY_PUBLIC_MANIFEST`, `UPRESS_EZCACHE_PURGE_AFTER_UPLOAD` with WP Application Password (see [`organic_market_agent/publisher/ftps_upload.py`](../../../organic_market_agent/publisher/ftps_upload.py), [`organic_market_agent/utils/config.py`](../../../organic_market_agent/utils/config.py)).
3. **Documentation:** [`documentation/05-admin-and-operations/PUBLISH_CHECKLIST.md`](../../../documentation/05-admin-and-operations/PUBLISH_CHECKLIST.md), [`WORDPRESS_PUBLIC_PUBLISH_RUNBOOK.md`](../../../documentation/05-admin-and-operations/WORDPRESS_PUBLIC_PUBLISH_RUNBOOK.md), [`.env.example`](../../../.env.example), `CHANGELOG.md`.
4. **Mandate to Team 50:** [`../../TEAM_50/reports/2026-04-21_QA_REVIEW_REQUEST_PRODUCTION_DATA_PARITY_TEAM10.md`](../../TEAM_50/reports/2026-04-21_QA_REVIEW_REQUEST_PRODUCTION_DATA_PARITY_TEAM10.md) (parallel track).

This is **not** a new product LOD200 package; it is a **governance and ops validation** of recent changes to the publish path and public consistency story.

---

## 2. Required checks (Team 190)

1. **AOS lean-kit (if declaring any L-gate in repo):**  
   `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .`  
   **Expected** on this spoke: **17 PASS / 2 SKIP / 0 FAIL** (per `AGENTS.md` / `CLAUDE.md`).

2. **No cross-product leakage** in this repo: changes remain within **SmallFarmsAgents / organic_market** scope only ([`AGENTS.md`](../../../AGENTS.md), [`CROSS_PROJECT_BOUNDARIES`](../../../documentation/external-references/CROSS_PROJECT_BOUNDARIES.md)).

3. **Data authority / ADR034:** AOS structured state remains **file-first L0** for this repo; no improper hand-edited AOS DB contract as SSoT (no change intended here—confirm no drift in `_aos/roadmap.yaml` intent).

4. **Optional:** Run constitutional package preflight on this file if you use `scripts/lint_constitutional_package.py` for inbox hygiene (see [`.cursor` skill constitutional-package-linter] if applicable).

---

## 3. Evidence index (read-only paths)

| Artifact | Path |
|----------|------|
| FTPS + verify + optional purge | [`organic_market_agent/publisher/ftps_upload.py`](../../../organic_market_agent/publisher/ftps_upload.py) |
| uPress / WP env (optional) | [`organic_market_agent/utils/config.py`](../../../organic_market_agent/utils/config.py) |
| Checklist (parity) | [`documentation/05-admin-and-operations/PUBLISH_CHECKLIST.md`](../../../documentation/05-admin-and-operations/PUBLISH_CHECKLIST.md) |
| Runbook (operational) | [`documentation/05-admin-and-operations/WORDPRESS_PUBLIC_PUBLISH_RUNBOOK.md`](../../../documentation/05-admin-and-operations/WORDPRESS_PUBLIC_PUBLISH_RUNBOOK.md) |
| Sign-off (Team 10) | [`../../TEAM_10/reports/2026-04-18_PRODUCTION_DATA_PARITY_SIGNOFF_TEAM10.md`](../../TEAM_10/reports/2026-04-18_PRODUCTION_DATA_PARITY_SIGNOFF_TEAM10.md) |
| Changelog | [`CHANGELOG.md`](../../../CHANGELOG.md) |

---

## 4. Outcomes requested

- **ACCEPT** — Record a short **validation result** in `_COMMUNICATION/TEAM_190/reports/` (naming per your convention) with **PASS/CONDITIONAL/FAIL** and any conditions (e.g. “HTTPS cache outside repo control; ops purge documented”).
- **or RAISE** — File findings to Team 100 if **governance** or **ADR** conflict is found (do not re-implement in Team 10 thread).

---

*Submitted by: Team 10 — 2026-04-21*
