# EXTERNAL_VALIDATION_BUNDLE — SFA-S002-P001 (Phased Release) — TEAM_100 — v1.0.0

**Date:** 2026-05-07
**Author:** team_100 (sfa_arch / Claude Opus 4.7)
**Type:** EXTERNAL_VALIDATION_BUNDLE
**Program:** SFA-S002-P001 — Public Index Launch Readiness
**Phase:** 1 (phased release — Phase 2 = SFA-S003-P001 covering WP001+WP002 deferred)
**Cross-engine constraint (Iron Rule #1):** External validator engine ≠ team_100 (Opus). Authorized engines: Cursor / Claude Sonnet / Claude Haiku / non-Anthropic. Validator session is dispatched by team_00.

---

## 1. Bundle scope

| WP | Title | Outcome |
|----|-------|---------|
| **SFA-S002-P001-WP003** | Server Scraping Verification | L-GATE_B PASS (Pass-2). 7/7 AC pass; F-01 closed via WP007. |
| **SFA-S002-P001-WP004** | Mobile UI Parity | L-GATE_B PASS. 47/47 unit tests; structural ACs met. AC-05 (Lighthouse) + AC-06 (cross-device smoke) deferred to operator-with-live-site. |
| **SFA-S002-P001-WP006** | FTPS Upload Remediation (TLS hypothesis) | L-GATE_B PASS_CODE_CORRECT — code was already correct; hypothesis disproven. SUPERSEDED_BY_WP007. |
| **SFA-S002-P001-WP007** | HTTP Upload Migration via WP REST API | L-GATE_B PASS (production-validated). Replaces FTPS as primary; FTPS retained as defensive fallback under `UPRESS_FALLBACK_FTPS=1`. |

### Out of scope for THIS bundle (deferred to SFA-S003-P001)
- **SFA-S002-P001-WP001** — M10 Thaw + Completion (mandate published in git, builder dispatch deferred per team_00 directive 2026-05-07)
- **SFA-S002-P001-WP002** — MyPIPS Source Integration (mandate published in git, dispatch deferred)

These two WPs are NOT part of Phase 1 launch. They remain valid and will be the substance of Phase 2 (SFA-S003-P001) in a subsequent session.

---

## 2. Production state (verified 2026-05-07)

| Metric | Value | Status |
|--------|-------|--------|
| `https://www.nimrod.bio/SmallFarmsAgent` | HTTP 200 | LIVE ✓ |
| `manifest.artifact_version` | `20260506_233451` | FRESH (was stale `20260417_004822` for 19 days) |
| `manifest.staleness_level` | `fresh` | PASS |
| `manifest.report_date` | `2026-05-06` | REAL (was placeholder `2099-08-12`) |
| `manifest.product_count` | `32` | OK (was `1`) |
| `community_sources` (rolling window) | `4` | ≥2 minimum (PASS) |
| `validate_aos.sh` on offline branch | 29 PASS / 17 SKIP / 0 FAIL | PASS |

---

## 3. Per-WP folders

- [`WP003/`](WP003/) — LOD400, Pass-1 + Pass-2 verification reports
- [`WP004/`](WP004/) — LOD400, build report
- [`WP006/`](WP006/) — LOD400, build evidence (code-correct + supersession note)
- [`WP007/`](WP007/) — LOD400, build report, DEPLOY_HANDOFF, deploy log, Pass-2 production deploy commit reference

---

## 4. Bundle artifacts (this directory)

| File | Purpose |
|------|---------|
| `MANIFEST.md` | This file — index + sign-off matrix |
| `PROGRAM_SUMMARY.md` | 1-page executive summary |
| `RISK_REGISTER.md` | Known issues, deferred items, waivers |
| `ROLLBACK_PLAN.md` | Explicit revert procedure if external validator finds blocker |
| `VALIDATE_AOS_OUTPUT.txt` | `validate_aos.sh` output (29/17/0) |
| `AOS_MAIL_PROMPT.md` | Self-contained activation prompt for external validator session |

---

## 5. Sign-off matrix

| Team | Role | Status | Date | Evidence |
|------|------|--------|------|----------|
| team_100 | Architect | ✓ SIGNED | 2026-05-07 | LOD400 specs, L-GATE_S verdicts, WP005 authored |
| team_10 (sfa_build) | Builder | ✓ SIGNED | 2026-05-07 | Build commits 30399a3 (WP004), 55ac306 (WP006), 73eaf3e (WP007) |
| team_50 | QA | ⚠ PARTIAL | 2026-05-07 | Test runs (47/47 WP004 + 14/14 WP006 + 20/20 WP007) confirmed by builder. Lighthouse + cross-device smoke for WP004 deferred to Team 50 with live site access. |
| team_60 | Server | — N/A | — | Cross-delivered via team_99 |
| team_99 | Server-side ops | ✓ SIGNED | 2026-05-07 | Pass-1 (1e24f33), DEPLOY_LOG (3754050), Pass-2 + WP007 deploy (42026f3) |
| team_00 | Principal | ⚠ PENDING | — | Awaiting external validator verdict |
| **external** | Cross-engine validator | ⏳ PENDING | — | This bundle is the validation request |

---

## 6. External validator: where to file the verdict

`_COMMUNICATION/team_190/SFA-S002-P001/EXTERNAL_VERDICT_v1.0.0.md`

Verdict format (PASS / PASS_WITH_FINDINGS / FAIL) per Team 190 contract. Use the AC matrix from each WP's LOD400 as the structured evaluation framework. See `AOS_MAIL_PROMPT.md` for the full prompt.

---

*End of MANIFEST.*
