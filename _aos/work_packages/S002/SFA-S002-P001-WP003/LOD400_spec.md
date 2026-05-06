# LOD400 — SFA-S002-P001-WP003 — Server Scraping Verification

**Date:** 2026-05-07
**Author:** team_100
**WP:** SFA-S002-P001-WP003
**Type:** LOD400_SPEC
**Status:** READY for L-GATE_S
**Builder:** Team 60 (Sonnet)
**QA:** Team 50 (Haiku)
**Validator:** external (cross-engine via aos_mail)

---

## 1. Goal

Confirm that the production scraping pipeline on `waldhomeserver` is **healthy, fresh, and reliably feeding** the public price index — as a launch precondition. **No code changes** are expected unless verification reveals a defect; in that case, defect is filed as a follow-up issue and remediated under WP005's rollback discipline.

This is a **read-only audit WP** — it produces a verification report, not new functionality.

---

## 2. Production environment (authoritative facts)

| Item | Value |
|------|-------|
| Production host | `waldhomeserver` (per [`WALD_HOME_SERVER_AGENT_COMMUNICATION.md`](../../../../documentation/05-admin-and-operations/WALD_HOME_SERVER_AGENT_COMMUNICATION.md)) |
| Project path on server | `/data/projects/smallfarmsagents/` |
| Server-side env file | `/data/projects/smallfarmsagents/.env` (contains `UPRESS_SFTP_*`) |
| Pipeline trigger | Daily cron + scheduler config in admin UI (`upload_enabled=true`) |
| Ingest entry point | `python -m organic_market_agent run_ingestion` |
| Publish entry point | `python -m organic_market_agent run_publisher --upload` |
| Existing collectors | [`easyfarm.py`](../../../../organic_market_agent/collectors/easyfarm.py), [`govt_benchmark.py`](../../../../organic_market_agent/collectors/govt_benchmark.py), [`html_page.py`](../../../../organic_market_agent/collectors/html_page.py) (+ [`base.py`](../../../../organic_market_agent/collectors/base.py), [`engine.py`](../../../../organic_market_agent/collectors/engine.py)) |
| Public artifact tree | `https://www.nimrod.bio/wp-content/uploads/market/` |
| Public WP page | `https://www.nimrod.bio/SmallFarmsAgent` |

---

## 3. Acceptance Criteria

### AC-01 — Scheduler is enabled and recent
- `scheduler_config.upload_enabled == true` on production host.
- Last successful ingest run within **24 hours** of the verification timestamp.
- Last successful publish run within **24 hours** of the verification timestamp.

### AC-02 — Per-collector freshness
For each active collector currently enabled in production (default: `easyfarm`, `govt_benchmark`, `html_page` + any added on the M10 branch / WP002 — see §6):
- At least one successful run within the last **24 hours**.
- `raw_extracted_items` count per collector ≥ baseline minus 20% (baseline = trailing 7-day median).
- No collector has > **3 consecutive failures** in the trailing 7 days.

### AC-03 — Log integrity
- No `level=ERROR`/`level=CRITICAL` log entries in the trailing 7 days that are not already documented in [`UNRESOLVABLE_BACKLOG_PLAYBOOK.md`](../../../../documentation/05-admin-and-operations/UNRESOLVABLE_BACKLOG_PLAYBOOK.md).
- `pipeline_alerts` table on production DB shows no open alerts older than 7 days.

### AC-04 — Public artifact freshness (FTPS round-trip)
- `https://www.nimrod.bio/wp-content/uploads/market/manifest.json` returns HTTP 200.
- `manifest.artifact_version` matches the latest `output/public/manifest.json` on the production host (≤ 60 minutes lag tolerated for ezCache propagation).
- `manifest.staleness_level` ∈ {`fresh`, `acceptable`} — NOT `stale`.
- `manifest.product_count` ≥ baseline minus 20%.

### AC-05 — Public page renders
- `https://www.nimrod.bio/SmallFarmsAgent` returns HTTP 200.
- `[sfagent_market_report]` shortcode renders without PHP errors (browser DevTools Console, plus `wp-content/debug.log` if WP_DEBUG enabled).
- At least one product row visible on first paint.

### AC-06 — Index integrity gate
- The "two distinct community sources" gate from [`PUBLISH_CHECKLIST.md`](../../../../documentation/05-admin-and-operations/PUBLISH_CHECKLIST.md) §2 holds in the latest publish window.

### AC-07 — Documentation
- Verification evidence is filed at `_COMMUNICATION/TEAM_60/reports/2026-05-XX_SCRAPING_VERIFICATION_TEAM60.md` per the canonical AOS artifact header (see team_60 contract).

---

## 4. File-level deliverables

| Path | Action |
|------|--------|
| `_COMMUNICATION/TEAM_60/reports/2026-05-XX_SCRAPING_VERIFICATION_TEAM60.md` | CREATE — full report (see §5 schema) |
| `_COMMUNICATION/TEAM_60/reports/2026-05-XX_SCRAPING_VERIFICATION_TEAM60.evidence/` | CREATE — directory holding raw cron output, manifest snapshots, log excerpts |
| `documentation/05-admin-and-operations/PUBLISH_CHECKLIST.md` | NO CHANGE expected |
| `documentation/05-admin-and-operations/UNRESOLVABLE_BACKLOG_PLAYBOOK.md` | UPDATE only if AC-03 surfaces new known-issue documentation |

**No changes to application code (`organic_market_agent/**`) under this WP.** If a defect is discovered, file an issue and surface in the report; remediation is out-of-scope here.

---

## 5. Verification report schema (AC-07 deliverable)

```markdown
# SCRAPING_VERIFICATION — SFA-S002-P001-WP003 — TEAM_60 — v1.0.0

**Date:** YYYY-MM-DD
**Author:** team_60
**WP:** SFA-S002-P001-WP003
**Type:** VERIFICATION_REPORT
**Verdict:** PASS | PASS_WITH_FINDINGS | FAIL

## 1. Environment snapshot
- Host: waldhomeserver (uname -a, uptime, disk free)
- Pipeline service: <systemd unit name + status> OR <crontab excerpt>
- DB version + connection string redacted

## 2. Per-AC results
For each AC-01..AC-07: PASS / FAIL + evidence reference

## 3. Per-collector freshness table
| Collector | Last success | Run count 7d | raw_extracted_items 7d | Status |

## 4. Findings (if any)
| Severity | Description | Evidence | Recommendation |

## 5. Public round-trip evidence
- manifest.json HTTP 200 + first 30 lines
- artifact_version match (host vs public)
- public page HTTP 200 + screenshot reference

## 6. Sign-off
- Team 60: <handle> <date>
```

---

## 6. Inputs from upstream WPs

- **WP001 (M10 thaw):** May add new collectors. WP003 verification re-runs once WP001 lands; AC-02 list updates accordingly.
- **WP002 (MyPIPS):** Adds new collectors. WP003 final verification runs after WP002 is deployed to production.
- **Sequencing rule:** WP003's PASS verdict is captured **twice**:
  - **Pass-1:** baseline state (current production, current collectors). Establishes the "before" line.
  - **Pass-2:** post-WP001+WP002 (full collector roster). Required for WP005 launch package.

---

## 7. Non-goals

- **No code changes** to collectors, pipeline, scheduler.
- **No configuration changes** to production cron/systemd.
- **No DB schema changes.**
- **No public URL changes.**
- **No restart of services** unless explicitly authorized by team_00 (avoid disrupting active pipeline).

---

## 8. Risks and mitigations

| Risk | Mitigation |
|------|-----------|
| Reading production state may require SSH that's currently locked | Coordinate with team_00 before run; document required permissions in report |
| Scraping may be transiently failing for a known-non-blocker reason (e.g., source site rate-limit) | Cross-reference [`UNRESOLVABLE_BACKLOG_PLAYBOOK.md`](../../../../documentation/05-admin-and-operations/UNRESOLVABLE_BACKLOG_PLAYBOOK.md); document waivers explicitly |
| ezCache lag may cause AC-04 false-failure | Wait up to 60 min and re-check; document timing in evidence |

---

## 9. References

- Program package: [`PROGRAM_PACKAGE_LOD200_v1.0.0.md`](../../../../_COMMUNICATION/TEAM_100/SFA-S002-P001/PROGRAM_PACKAGE_LOD200_v1.0.0.md)
- Publish checklist (production parity): [`PUBLISH_CHECKLIST.md`](../../../../documentation/05-admin-and-operations/PUBLISH_CHECKLIST.md)
- WordPress publish runbook: [`WORDPRESS_PUBLIC_PUBLISH_RUNBOOK.md`](../../../../documentation/05-admin-and-operations/WORDPRESS_PUBLIC_PUBLISH_RUNBOOK.md)
- Server comms: [`WALD_HOME_SERVER_AGENT_COMMUNICATION.md`](../../../../documentation/05-admin-and-operations/WALD_HOME_SERVER_AGENT_COMMUNICATION.md)
- 2026-04 production parity sign-off: [`_COMMUNICATION/TEAM_190/reports/2026-04-22_VALIDATION_RESULT_PRODUCTION_DATA_PARITY_TEAM190.md`](../../../../_COMMUNICATION/TEAM_190/reports/2026-04-22_VALIDATION_RESULT_PRODUCTION_DATA_PARITY_TEAM190.md)
- ADR-049 (server-side push authority for team_60): hub `governance/directives/ADR-049_*`

---

*LOD400 ready for L-GATE_S verdict.*
