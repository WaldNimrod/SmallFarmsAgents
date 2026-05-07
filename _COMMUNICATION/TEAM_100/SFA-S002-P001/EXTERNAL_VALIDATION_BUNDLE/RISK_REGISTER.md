# RISK REGISTER — SFA-S002-P001 Phase 1

## Open risks (to be acknowledged by validator)

| ID | Severity | Description | Owner | Mitigation |
|----|----------|-------------|-------|------------|
| R-01 | LOW | WP004 Lighthouse + cross-device smoke (AC-05/06) deferred — structural prerequisites met but operator must run live tests with WP REST URLs | Team 50 with live site access | Lighthouse CLI command documented in QA scaffold; can be run any time post-launch |
| R-02 | LOW | mu-plugin `sfagent-allow-json.php` is a manual install — if it's deleted from uPress filesystem, all uploads fail with HTTP 500 | team_00 / team_99 | Documented in runbook §4; daily pipeline alerts will detect within 24h; manual reinstall is a 2-minute panel task |
| R-03 | LOW | WP option `sfagent_manifest_of_urls_url` must remain registered via theme `functions.php` or mu-plugin (REST API rejects unregistered settings) | team_00 / theme owner | Documented in runbook §5; if theme is replaced, the `register_setting` snippet must be re-added |
| R-04 | LOW | WP application password attached to user `agent` — if revoked from WP Admin, all REST uploads fail with HTTP 401 | team_00 | Rotation procedure documented in runbook §3; auth smoke command provided |
| R-05 | INFO | shaked-wg-agent's `wp_upload.py` is reference-only (not actively used by their pipeline). SFA's implementation is independent and verified standalone | team_100 | No mitigation needed; documented for clarity |
| R-06 | LOW | FTPS code retained as defensive fallback (`UPRESS_FALLBACK_FTPS=1`). If accidentally enabled in production where Bezeq blocks port 21, upload fails silently to FTPS (and primary WP REST is bypassed) | team_99 | Default is OFF; pipeline_alerts logs which protocol was used per upload |

## Closed during the program

| ID | Severity | Description | Resolution |
|----|----------|-------------|------------|
| F-01 | HIGH | FTPS upload broken; public artifacts 19 days stale | RESOLVED via WP007 (WP REST API migration) |
| F-02 | MEDIUM | May 3-5 outage (3-day total pipeline failure) | RESOLVED 2026-05-06 via clatd IPv4 restoration (Tailscale exit-node removed) |

## Deferred items (next program — SFA-S003-P001)

- WP001 — M10 Thaw + Completion (LARGE, MEDIUM 3-5 days estimated)
- WP002 — MyPIPS Source Integration + Branch Cleanup (LARGE, 5-8 days estimated)
- WP-A1 — Moderated user submissions (deferred per team_00 ruling)
- WP-A2 — Farmer economics calculator (deferred per team_00 ruling)
- Tend farm exports + MasterClass PDFs ingestion (raw material)

## Architectural assumptions (validator should test)

- **A-01:** Bezeq's port 21 egress block is permanent for this host. *Test:* `nc -z ftp.s887.upress.link 21` from waldhomeserver should fail. If it succeeds — environmental change has occurred and FTPS could be reactivated as primary if desired.
- **A-02:** uPress mu-plugin survives uPress core/plugin updates. *Test:* re-run smoke (curl POST JSON) after any uPress maintenance window.
- **A-03:** WP application password does not auto-expire. *Test:* run auth smoke periodically; rotate annually as policy.
