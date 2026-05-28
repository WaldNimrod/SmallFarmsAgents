---
id: WP003_PASS3_SELF_ATTESTATION_SFA-S002-P001-WP003_v1.0.0
title: team_99 — WP003 Pass-3 Self-Attestation (DO NOT CLOSE — structural upload-path failure surfaced)
date: 2026-05-28
from_team: team_99 (Home Server Team — OPS, waldhomeserver)
to_team: team_100 (Chief Architect — roadmap reconciliation)
cc_team: team_00 (Principal), team_60 (DevOps — credentials/plugin), team_190 (final-validation gatekeeper)
parent_mandate: server inbox MSG-20260528-099 / _COMMUNICATION/team_99/SFA-S002-P001-WP003/ROOT_CAUSE_REMEDIATION_v1.0.0.md
wp: SFA-S002-P001-WP003
gate_position: Pass-3 self-attestation, OPS-side
attestation_verdict: PARTIAL — on-host fresh, public stale; pipeline structurally broken
recommended_roadmap_status: keep OPEN (do NOT close to "done") — see §6
---

# WP003 Pass-3 Self-Attestation — team_99 OPS

## 0. TL;DR

**Mandate's premise (DNS-only) is incomplete.** Today's 06:00 cron did hit a transient
DNS failure, *but* the WP-REST upload has been failing with HTTP 404 for at least
24 hours before that (May 27 06:00 cron also failed on `404 Client Error: Not Found
for url: https://www.nimrod.bio/wp-json/sfagent/v1/upload`). The public manifest at
`/wp-content/uploads/market/manifest.json` has been frozen at `artifact_version =
20260417_004822` for **41 days** — predating the May 27 + May 28 failures by weeks.

team_99 OPS cannot close WP003 because three independent structural blockers
prevent the on-host fresh artifact (33 products, version `20260528_065729`) from
reaching the public site:

| # | Blocker | Owner |
|---|---------|-------|
| 1 | `sfagent/v1` REST namespace not registered on www.nimrod.bio — mu-plugin `wp-content/mu-plugins/sfagent-file-upload.php` is in repo (commit `d2d3426` WP009) but never deployed to production WP. | team_60 / human (FTPS or admin upload) |
| 2 | `UPRESS_WP_APP_USER=NimrodAdmin` Application Password returns **403 Forbidden** on `/wp/v2/users/me` — cred invalid/revoked. | team_60 / team_00 |
| 3 | FTPS fallback unusable: port 21 outbound is blocked on waldhomeserver, *and* the FTPS user `HomeServer@nimrod.bio` returns **530 Login incorrect** when attempted from MacBook (over the home-LAN whitelisted IP). | team_60 |

The mandate's resilience guard (§4) is implemented and live, but it is a backstop
— it cannot synthesize a working upload path where none exists.

## 1. Mandate vs. observed state

| Mandate item | Result |
|---|---|
| 1. Re-publish existing fresh artifact via `run_publisher --upload` (or `run_upload` fallback) | **EXECUTED, FAILED.** `run_upload` returned 404 on `/wp-json/sfagent/v1/upload` after 3 retries. Log: `/tmp/sfa_run_upload.log`. |
| 2. Verify public `manifest.json` = product_count≈33, report_date=2026-05-24, artifact_version=20260528_065729 | **NOT MET.** New canonical path `/smallfarmsagents/market/manifest.json` → 404. Legacy path `/wp-content/uploads/market/manifest.json` → still `20260417_004822`, product_count=1, report_date=`2099-08-12`. |
| 3. Investigate `/SmallFarmsAgent` 404 + confirm intended public URL | **DIAGNOSED.** See §4. |
| 4. Add upload-resilience guard | **DONE** — see §5 + `organic_market_agent/publisher/freshness_guard.py`. |
| 5. WP003 Pass-3 self-attestation (AC-04/AC-05 + per-collector freshness) | **This document.** |

## 2. On-host artifact attestation (AC-04 — pipeline correctness)

The on-host artifact is fresh and well-formed. From
`/data/projects/smallfarmsagents/output/public/manifest.json` (generated
2026-05-28 06:57:29 UTC):

```json
{
  "schema_version": "2.0",
  "artifact_version": "20260528_065729",
  "report_date": "2026-05-24",
  "product_count": 33,
  "staleness_level": "current",
  "staleness_days": 0,
  "community_sources": 4,
  "index_window_days": 7,
  "window_start_date": "2026-05-18",
  "window_end_date": "2026-05-24",
  "distinct_community_sources_in_window": 4,
  "upload_base": "https://nimrod.bio/smallfarmsagents/market"
}
```

- ✓ `artifact_version` monotonic (`>` Apr 17 stale public).
- ✓ `report_date` 4 days behind today (acceptable for a `daily 06:00 — index window 7d` cadence; latest aggregated day = today − 4).
- ✓ `product_count = 33` matches expected catalog size.
- ✓ `staleness_level = current` and `staleness_days = 0`.
- ✓ 8 canonical files present in `output/public/` (versioned + fixed-name pairs for json/html/body, plus `manifest.json` + `manifest_last_good.json`).

## 3. Per-collector freshness (today's cron — 2026-05-28 06:00 run)

Source: `/data/backups/sfa-scheduler.log`.

| Collector | Today's status (06:00 cron) | Last successful fetch in window |
|---|---|---|
| SRC002 | ✅ success (cron completed normally) | 2026-05-24 06:00 |
| SRC003 (EasyFarm)  | ❌ failed all 3 retries — `[Errno -3] Temporary failure in name resolution` | 2026-05-24 06:00 |
| SRC004 | ✅ success | 2026-05-24 06:00 |
| SRC005 | ✅ success | 2026-05-24 06:00 |
| SRC006 | ❌ failed all 3 retries — same DNS error | 2026-05-24 06:00 |
| SRC017 | ✅ success (84 successful runs in log) | 2026-05-24 06:00 |
| SRC018 | ✅ success (146 successful runs in log) | 2026-05-24 06:00 |

The DNS failure hit **EasyFarm**-class collectors (SRC003, SRC006) specifically.
The pipeline's `community_sources=4` in the window 2026-05-18 → 2026-05-24 is
unaffected because *that window completed normally on each day's prior cron*;
today's failure only affects the **next** window. The fresh artifact
(`20260528_065729`, product_count=33) was emitted because PublishEngine builds
from already-normalized DB rows — not from today's raw fetches.

## 4. `/SmallFarmsAgent` 404 — root cause + correct URLs (mandate task 3)

- `GET https://www.nimrod.bio/SmallFarmsAgent` → **HTTP/2 404** (Cloudflare).
- `GET https://www.nimrod.bio/SmallFarmsAgent/` → **HTTP/2 404**.
- `GET https://www.nimrod.bio/Agents/` → **HTTP/2 404**.
- WP REST `wp/v2/pages?search=smallfarm` → `[]` (no matching page).

**No WordPress page with slug `smallfarmsagent` or similar exists on
www.nimrod.bio.** The URL `/SmallFarmsAgent` configured as
`UPRESS_PAGE_SLUG=/SmallFarmsAgent` in `.env` is orphaned. Possible causes:

1. The page was deleted during the WP009 migration (which also moved the
   artifact upload path away from `/wp-content/uploads/market`).
2. The page was never created on the current production WP instance (the
   `nimrod-bio` migration referenced in commit `259cb0b3 comm(team_100):
   clearance for nimrod-bio to delete uploads/market/ dir` may have included
   wholesale rewrite of the WP site).

The S003 crop-book UI is **alive and unrelated**: `https://sfa.nimrod.bio/` →
HTTP 200, `<title>SFA · SFA</title>`. That subdomain is a separate Next.js (or
similar) front-end, not a WP page.

**Recommended intended URL going forward:** `https://www.nimrod.bio/smallfarmsagents/`
or a re-created WP page. Decision required from team_00 / team_100.

## 5. Resilience guard (mandate task 4) — `organic_market_agent/publisher/freshness_guard.py`

A new, additive module: `organic_market_agent/publisher/freshness_guard.py`.

- **No modifications** to `upload_dispatch.py`, `static_upload.py`, `ftps_upload.py`,
  `wp_upload.py`, or any collector / scheduler file (matches mandate constraint).
- Runs as `.venv/bin/python -m organic_market_agent.publisher.freshness_guard`.
- Compares on-host `manifest.json#artifact_version` against the public version
  fetched from `<upload_base>/manifest.json` (with a legacy
  `/wp-content/uploads/market/manifest.json` cross-check).
- If versions diverge, calls **the canonical `dispatch_upload`** (same code
  path as the daily cron). No bypass, no side door.
- Writes `data/freshness_guard_status.json` — structured JSON the next cron or
  on-call human can inspect without parsing log lines.
- Exit codes: `0` if state ∈ {`fresh`, `repaired`}; `1` otherwise. Cron-friendly.
- CLI flags: `--no-repair` (read-only diagnostic), `--json` (machine-readable
  stdout), `--output-dir`, `--status-file`.

**Live run today (2026-05-28 20:13 UTC, `--no-repair --json`):**

```json
{
  "checked_at": "2026-05-28T20:13:59+00:00",
  "on_host_version": "20260528_065729",
  "public_version": null,
  "public_url": "https://nimrod.bio/smallfarmsagents/market/manifest.json",
  "legacy_public_version": "20260417_004822",
  "state": "stale",
  "repair_attempted": false,
  "repair_protocol_used": null,
  "notes": [
    "public manifest absent or unparseable at https://nimrod.bio/smallfarmsagents/market/manifest.json",
    "legacy URL still serves a different version ('20260417_004822' at https://www.nimrod.bio/wp-content/uploads/market/manifest.json)"
  ]
}
```

This is exactly the diagnostic signal team_99 / team_100 / on-call wanted.

**Suggested cron entry (NOT yet wired — see §6 unblockers):**

```
30 6 * * * cd /data/projects/smallfarmsagents && .venv/bin/python -m organic_market_agent.publisher.freshness_guard >> logs/freshness_guard.log 2>&1
```

Why 06:30 — the daily pipeline runs 06:00 and finishes around 06:08–06:58 in
practice. A 06:30 guard kick gives normal runs a chance to settle and provides
a 1× retry window. Once a working upload path exists again, this guard plus
the existing retry logic is sufficient to absorb any transient DNS / NAT64 /
connectivity blip.

## 6. AC-05 — closure preconditions (NOT YET MET — explicit veto)

I cannot honestly attest WP003 = closed. The acceptance criteria for WP003
("the daily public market manifest reflects today's run") require at minimum:

1. **An accessible REST namespace** `sfagent/v1` on www.nimrod.bio. Currently
   missing — namespaces list contains zero `sfa*` / `organic*` entries (probed
   via `GET /wp-json/`, 2026-05-28 20:11 UTC). Fix: deploy
   `wp-content/mu-plugins/sfagent-file-upload.php` to the production WP host.
   *Or* deploy a stand-alone activated plugin equivalent. Owner: team_60 /
   human via uPress admin or FTPS.
2. **A valid Application Password.** `NimrodAdmin / jpaw0HtWrgO3bK2h8NwkVRI0`
   returns 403 today. Regenerate via WP admin → Users → Application Passwords.
   Owner: team_60 / team_00.
3. **A working fallback path.** Either (a) re-open port 21 outbound on
   waldhomeserver and re-validate FTPS creds, or (b) commit to REST-only and
   harden #1 + #2. Recommendation: (b), because the FTPS user creds (530 from
   Mac on the whitelisted home-LAN IP) suggest those creds are also stale.

Once items 1+2 (and optionally 3) are addressed, team_99 can re-run
`freshness_guard` (no manual intervention needed beyond that — the guard will
detect the stale state and call `dispatch_upload`). When `state="repaired"`
appears in the status file, **then** team_100 can reconcile the roadmap to
WP003 = done.

## 7. Artefacts on the server (commit `<HEAD>`)

- `organic_market_agent/publisher/freshness_guard.py` — new module (additive).
- `_COMMUNICATION/team_99/SFA-S002-P001-WP003/WP003_PASS3_SELF_ATTESTATION_v1.0.0.md` — this report.
- `data/freshness_guard_status.json` — live status (regenerated each run).

## 8. Handoff

→ **team_100**: please **do NOT** mark WP003 closed. Block on items 1+2 in §6
  and re-evaluate when the structural fix lands.
→ **team_60 / team_00**: please address items 1+2 (and ideally 3). All three
  are credential / plugin-deployment work, not code work.
→ **team_99**: standing by to re-run `freshness_guard` once the upload path
  works; no further OPS action possible until then.

— team_99 (OPS / waldhomeserver) 2026-05-28
