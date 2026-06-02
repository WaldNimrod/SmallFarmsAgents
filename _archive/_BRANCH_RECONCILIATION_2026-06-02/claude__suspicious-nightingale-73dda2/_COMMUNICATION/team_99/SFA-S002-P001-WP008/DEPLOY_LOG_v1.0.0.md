# DEPLOY_LOG — SFA-S002-P001-WP008 — team_99

**Date:** 2026-05-07
**Author:** team_99 (waldhomeserver)
**WP:** SFA-S002-P001-WP008
**Type:** DEPLOY_LOG
**Verdict:** PASS

---

## 1. Pre-deploy state

- sfa-admin.service: active (running) — OLD code (FTPS-only on admin/scheduler paths)
- Today's 06:00 UTC cron (run #28): ingest completed (5/5 sources), BUT `[FTPS:upload_fail] FTPS upload FAILED: timed out` — confirms F-190-01 (scheduler still used FTPS)
- Code on disk: WP008 `dispatch_upload` already pulled to main

## 2. Deploy actions

1. `git pull github main` — WP008 code in place (commit `53af3eb`)
2. `sudo systemctl restart sfa-admin` — active (running), PID 991522
3. Note: no `sfa-pipeline.service` exists — scheduler runs via crontab (`0 6 * * *`). Code is read from disk at runtime, so tomorrow's cron will pick up the new `dispatch_upload` path automatically.

## 3. Smoke results

### Smoke 1 — Config verification

```
upress_configured: True
```

### Smoke 2 — CLI upload (dispatch_upload path)

```
WP REST upload OK: 5 artifacts uploaded
  sfagent-manifest.json → media_id=91384
  sfagent-public-report.json → media_id=91385
  sfagent-public-report.html → media_id=91386
  sfagent-public-report-body.html → media_id=91387
  sfagent-manifest-of-urls.json → media_id=91388
```

Delete-before-upload worked (previous media IDs 91379-91383 cleaned up).

### Smoke 3 — Public manifest

```
artifact_version: 20260507_093945
report_date: 2026-05-07
product_count: 32
staleness_level: current
```

### Code path verification

| Entry point | File | Uses `dispatch_upload` |
|-------------|------|----------------------|
| CLI `run_publisher --upload` | `__main__.py` | YES |
| Scheduler `pipeline.py` | `pipeline.py:307` | YES |
| Admin "Upload Now" | `runs.py:790` | YES |

All three paths route through `dispatch_upload()` → WP REST primary (FTPS fallback disabled).

## 4. Verdict: PASS

- F-190-01 resolved: scheduler + admin now use `dispatch_upload` → WP REST
- Tomorrow's 06:00 UTC cron will use the new code path
- No FTPS attempts (UPRESS_FALLBACK_FTPS unset)
- L-GATE_BUILD self-attestation: PASS

---

*team_99 | waldhomeserver | 2026-05-07*
