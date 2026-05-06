# LOD400 — SFA-S002-P001-WP004 — Mobile UI Parity

**Date:** 2026-05-07
**Author:** team_100
**WP:** SFA-S002-P001-WP004
**Type:** LOD400_SPEC
**Status:** STUB — full LOD400 authoring pending (next phase)

---

## Scope (carried from program package §4)

- Audit `[sfagent_market_report]` rendering on iOS/Android viewports.
- Fix responsive issues in `public_report_body.html` + `sfagent-base.css`.
- Lighthouse mobile score target ≥ 85.
- Smoke evidence: screenshots at 375px / 414px / 768px.

## Pending sections (to be authored in LOD400 phase)

- Specific viewport breakpoints + behavior matrix
- RTL Hebrew rendering verification (per `docs/RTL_DEVELOPMENT_GUIDE.md`)
- Acceptance Criteria
- Test devices (real-device or BrowserStack-equivalent)
- Lighthouse audit thresholds breakdown (perf / a11y / SEO / best-practices)

## Constraints

- WordPress/uPress hosting environment (cannot change theme infrastructure)
- Shortcode interface stability (no breaking changes to `[sfagent_market_report]` API)

## References

- Program package: [`PROGRAM_PACKAGE_LOD200_v1.0.0.md`](../../../../_COMMUNICATION/TEAM_100/SFA-S002-P001/PROGRAM_PACKAGE_LOD200_v1.0.0.md)
- Hosting spec: [`docs/UPRESS_WORDPRESS_STANDARD_v2.md`](../../../../docs/UPRESS_WORDPRESS_STANDARD_v2.md)
- 2026-04 production parity sign-off: [`_COMMUNICATION/TEAM_190/reports/2026-04-22_VALIDATION_RESULT_PRODUCTION_DATA_PARITY_TEAM190.md`](../../../../_COMMUNICATION/TEAM_190/reports/2026-04-22_VALIDATION_RESULT_PRODUCTION_DATA_PARITY_TEAM190.md)

*Stub. Full LOD400 spec required before L-GATE_S verdict.*
