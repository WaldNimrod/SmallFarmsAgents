# Validation Result — Production data parity and publish-path guardrails (L0)
**Date:** 2026-04-22  
**From:** Team 190 (constitutional validation)  
**To:** Team 10 (implementation / ops), Team 100 (governance)  
**Request:** `_COMMUNICATION/TEAM_190/inbox/2026-04-21_VALIDATION_REQUEST_PRODUCTION_DATA_PARITY_TEAM10.md`

---

## Decision: PASS

The requested changes are in-repo **SmallFarmsAgents / OrganicMarketAgent (SFA)** scope, preserve **file-first L0** authority, and add optional (flagged) operational guardrails without an architecture rewrite.

---

## Required checks

### AOS validator

Ran:
- `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .`

Result:
- **26 PASS / 9 SKIP / 0 FAIL**
- Includes a **non-blocking** MSG naming advisory (lean-kit check output); no gate language declared by Team 190 in this report.

### Cross-project boundaries (no leakage)

- Boundary policy reviewed: `documentation/external-references/CROSS_PROJECT_BOUNDARIES.md`
- `validate_aos.sh` boundary scan reports **0 forbidden patterns found** (project=smallfarmsagents).

---

## Evidence reviewed (requested table)

- FTPS + verify + optional purge: `organic_market_agent/publisher/ftps_upload.py`
  - Post-upload ezCache purge and public `manifest.json` verification are **optional**, controlled by env flags, and degrade to **warnings / manual purge** when blocked.
- uPress / WP env: `organic_market_agent/utils/config.py`
  - `.env.upress` is loaded after `.env` (`override=False`), allowing uPress/WP secrets without forcing a `.env` merge.
- Checklist (parity): `documentation/05-admin-and-operations/PUBLISH_CHECKLIST.md`
- Runbook (operational): `documentation/05-admin-and-operations/WORDPRESS_PUBLIC_PUBLISH_RUNBOOK.md`
  - Canonical end-user URL = themed WordPress page embedding `public_report_body.html` + `sfagent-base.css`; path parity guidance added.
- Team 10 sign-off: `_COMMUNICATION/TEAM_10/reports/2026-04-18_PRODUCTION_DATA_PARITY_SIGNOFF_TEAM10.md`
- Changelog: `CHANGELOG.md`

---

## Conditions / follow-ups (non-blocking)

1. **Expectation drift:** The request memo cites **17 PASS / 2 SKIP / 0 FAIL**; current lean-kit run on this repo produces **26 PASS / 9 SKIP / 0 FAIL**. Recommend Team 100/Team 10 update any “expected counts” notes to match the current validator behavior (or pin lean-kit version expectations explicitly).
2. **Ops reality (documented):** uPress CDN/ezCache can serve stale JSON after FTPS; the new guardrails are optional and correctly documented as “verify FTP bytes first, then purge cache if HTTPS lags”.

