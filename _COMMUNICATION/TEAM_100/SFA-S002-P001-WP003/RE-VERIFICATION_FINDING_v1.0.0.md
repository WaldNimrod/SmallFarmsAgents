---
id: RE-VERIFICATION_FINDING_SFA-S002-P001-WP003_v1.0.0
from: team_100 (Chief Architect — orchestrator)
to: team_00 (Principal), team_99 (OPS builder)
cc: team_60, team_190
date: 2026-05-28
type: verification_finding
wp: SFA-S002-P001-WP003 (Server Scraping Verification)
verdict: FAIL (live re-attestation 2026-05-28)
status: REGRESSION — DO NOT CLOSE
---

# WP-S002-WP003 live re-attestation — REGRESSION FOUND

While orchestrating the 5-WP closure batch, team_100 ran a live re-attestation
of the publicly verifiable acceptance criteria (AC-04, AC-05). **The state
verified at Pass-2 (2026-05-07) no longer holds.** This WP must NOT be closed.

## Findings

| AC | Pass-2 (2026-05-07) | Live (2026-05-28) | Result |
|----|---------------------|-------------------|--------|
| AC-04 artifact freshness | artifact_version `20260506_233451`, product_count **32**, report_date `2026-05-06` | artifact_version `20260417_004822`, product_count **1**, report_date `2099-08-12` (placeholder) | **FAIL — regressed to pre-WP007 broken state** |
| AC-05 public page | `https://www.nimrod.bio/SmallFarmsAgent` → 200 | → **HTTP 404** | **FAIL** |

manifest source: `https://www.nimrod.bio/wp-content/uploads/market/manifest.json`
(`staleness_level` self-reports `current`, but the underlying values are the
documented pre-WP007 broken snapshot — product_count=1, 2099 placeholder date).

## Interpretation
- The market publish pipeline (daily cron + WP REST API upload) appears to have
  stopped producing fresh artifacts sometime after the 2026-05-07 Pass-2. The
  public manifest reverted to the April-17 stale version — the exact symptom
  class of the original F-01 (HIGH) that WP007 closed. **F-01 may have recurred.**
- The `/SmallFarmsAgent` WP page now 404s. Note the S003 crop-book UI moved to
  `https://sfa.nimrod.bio/`; this 404 is on the **separate** S002 market-report
  page and is an independent break to confirm.

## Caveats (honesty)
- WebFetch may hit an ezCache/CDN copy; LOD400 §8 allows ≤60 min propagation
  lag. However product_count=1 + the 2099 placeholder are *genuine stale-data*
  signatures, not cache jitter (a cached-but-fresh copy would show the May-6
  values). Recommend host-side confirmation.
- AC-01/02/03/06 (scheduler, per-collector freshness, logs, index gate) are
  server-internal and require SSH to `waldhomeserver` — not attestable from
  this Claude session.

## Recommended action (team_00 / team_99)
1. SSH to `waldhomeserver` `/data/projects/smallfarmsagents/`: check the
   ingest+publish cron/scheduler (`scheduler_config.upload_enabled`), last
   successful run timestamps, and `pipeline_alerts`.
2. Confirm whether the WP REST API upload (WP007 fix) is still functioning or
   has re-broken (F-01 recurrence).
3. Investigate the `/SmallFarmsAgent` 404 (page deleted/renamed vs. server error).
4. Re-run the full WP003 verification (Pass-3) after remediation; only then
   reconcile the roadmap status.

## Roadmap disposition
Status left as `BUILDING` (NOT closed). team_100 has NOT altered the WP003
roadmap block. A regression finding note may be added to gate_history once
team_00/team_99 confirm root cause.

— team_100 (Claude Opus 4.7) 2026-05-28
