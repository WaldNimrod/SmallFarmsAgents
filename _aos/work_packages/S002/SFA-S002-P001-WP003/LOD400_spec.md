# LOD400 — SFA-S002-P001-WP003 — Server Scraping Verification

**Date:** 2026-05-07
**Author:** team_100
**WP:** SFA-S002-P001-WP003
**Type:** LOD400_SPEC
**Status:** STUB — full LOD400 authoring pending (next phase)

---

## Scope (carried from program package §4)

- Confirm production scraping schedule on `waldhomeserver`: cron jobs / systemd timers, log integrity, freshness SLA.
- Verify FTPS publish pipeline parity (referenced in 2026-04 sign-offs).
- Output: `_COMMUNICATION/TEAM_60/reports/2026-05-XX_SCRAPING_VERIFICATION_TEAM60.md`.

## Pending sections (to be authored in LOD400 phase)

- Freshness SLA target (e.g., last successful scrape < 24h for each source)
- Log integrity criteria (no fatal/error within last 7d, or documented exceptions)
- Verification commands per source
- Acceptance Criteria
- Failure recovery runbook references

## Engine

Team 60 (server-side authority per ADR-049, just propagated 2026-05-06).

## References

- Program package: [`PROGRAM_PACKAGE_LOD200_v1.0.0.md`](../../../../_COMMUNICATION/TEAM_100/SFA-S002-P001/PROGRAM_PACKAGE_LOD200_v1.0.0.md)
- Operations doc: [`documentation/05-admin-and-operations/WALD_HOME_SERVER_AGENT_COMMUNICATION.md`](../../../../documentation/05-admin-and-operations/WALD_HOME_SERVER_AGENT_COMMUNICATION.md)

*Stub. Full LOD400 spec required before L-GATE_S verdict.*
