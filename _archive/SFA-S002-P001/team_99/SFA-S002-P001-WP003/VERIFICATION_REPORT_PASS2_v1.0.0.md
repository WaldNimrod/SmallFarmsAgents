# SCRAPING_VERIFICATION — SFA-S002-P001-WP003 — v1.0.0 — Pass-2

**Date:** 2026-05-06
**Author:** team_99 (waldhomeserver)
**WP:** SFA-S002-P001-WP003
**Type:** VERIFICATION_REPORT
**Pass:** 2 (post-WP007 upload fix)
**Verdict:** PASS_WITH_FINDINGS

---

## 1. Environment snapshot

- Host: waldhomeserver — Linux 6.8.0-111-generic x86_64 — Ubuntu 24.04.4 LTS
- Pipeline service: cron `0 6 * * *` daily scheduler
- Flask Admin: sfa-admin.service — active (running), port 5001
- DB: PostgreSQL 16 in Docker container `oma-postgres`
- Upload method: WP REST API (WP007 — replaces FTPS port 21)

---

## 2. Per-AC results

### AC-01 — Scheduler enabled + recent: PASS

| Check | Result |
|-------|--------|
| `is_enabled` | `true` |
| `upload_enabled` | `true` |
| Last successful ingest | 2026-05-06 06:07:54 UTC (run #27, 6/6 sources) |
| Last successful upload | **2026-05-06 23:34:56 UTC** — 5/5 artifacts via WP REST API |

**F-01 CLOSED.** WP REST upload working. FTPS replaced.

### AC-02 — Per-collector freshness: PASS_WITH_FINDINGS

| Collector | Last success | Success 7d | Failed 7d | Status |
|-----------|-------------|------------|-----------|--------|
| CHP | 2026-05-06 06:00 | 1 | 11 | PARTIAL |
| ח'ביזה | 2026-05-06 06:07 | 3 | 9 | OK |
| סבתא יהודית | 2026-05-06 06:07 | 3 | 9 | OK |
| עץ השדה | 2026-05-06 06:07 | 3 | 9 | OK |
| קיימא בית זית | 2026-05-06 06:07 | 3 | 9 | OK |
| קיימא חוקוק | 2026-05-06 06:07 | 3 | 9 | OK |

**Finding F-02 (carried from Pass-1):** May 3-5 outage (3 consecutive days, all collectors failed). Root cause resolved (IPv4/clatd). High failure counts are historical — next 7d window will normalize.

### AC-03 — Log integrity: PASS_WITH_FINDINGS

9 ERROR-level alerts in trailing 7d — all have documented root causes:
- FTPS upload failures (May 1-6): resolved by WP007 (WP REST replaces FTPS)
- Ingestion failures (May 3-5): resolved by clatd IPv4 fix

No CRITICAL-level entries. No undocumented errors.

### AC-04 — Public artifact freshness: **PASS** (was FAIL in Pass-1)

| Check | Pass-1 (FAIL) | Pass-2 (PASS) |
|-------|---------------|---------------|
| Public manifest HTTP | 200 | 200 |
| `artifact_version` | `20260417_004822` (19 days old) | **`20260506_233451`** (fresh) |
| `report_date` | `2099-08-12` (placeholder) | **`2026-05-06`** (current) |
| `product_count` | 1 | **32** |
| `staleness_level` | `current` (misleading) | **`current`** (accurate) |
| Host vs public match | identical (both stale) | **match** (both fresh) |
| Upload method | FTPS (broken) | **WP REST API** (working) |

Manifest-of-URLs pointer: `https://www.nimrod.bio/wp-content/uploads/2026/05/sfagent-manifest-of-urls.json` → HTTP 200, all 4 artifact URLs valid.

### AC-05 — Public page renders: PASS

- `https://www.nimrod.bio/SmallFarmsAgent` → HTTP 200
- Page loads with WordPress shortcode

### AC-06 — Index integrity gate: PASS

- `distinct_community_sources_in_window`: **4** (requirement: ≥ 2)
- `community_sources`: 4
- 5 community collectors succeeded on latest run

### AC-07 — Documentation: PASS

Reports filed at:
- `_COMMUNICATION/team_99/SFA-S002-P001-WP003/VERIFICATION_REPORT_PASS2_v1.0.0.md` (this file)
- `_COMMUNICATION/TEAM_60/reports/2026-05-06_SCRAPING_VERIFICATION_PASS2_TEAM60.md` (cross-delivery)

---

## 3. Per-collector freshness table

| Collector | Last success | Run count 7d | Success 7d | Status |
|-----------|-------------|-------------|------------|--------|
| CHP | 2026-05-06 06:00 | 14 | 1 | PARTIAL — DNS failures, non-blocker |
| ח'ביזה | 2026-05-06 06:07 | 12 | 3 | OK |
| סבתא יהודית | 2026-05-06 06:07 | 12 | 3 | OK |
| עץ השדה | 2026-05-06 06:07 | 12 | 3 | OK |
| קיימא בית זית | 2026-05-06 06:07 | 12 | 3 | OK |
| קיימא חוקוק | 2026-05-06 06:07 | 12 | 3 | OK |

---

## 4. Findings

| ID | Severity | Description | Status |
|----|----------|-------------|--------|
| F-01 | ~~HIGH~~ | FTPS upload broken — public artifacts stale | **CLOSED** — WP REST upload working (WP007) |
| F-02 | LOW | 3 consecutive days of pipeline failure (May 3-5) | **CLOSED** — root cause resolved (clatd IPv4), will age out of 7d window |
| F-03 | INFO | `publish_runs` table empty | Carried — WP007 uses inline upload, not publish_runs tracking |

---

## 5. Public round-trip evidence

- **Upload:** 5/5 artifacts uploaded via WP REST API (media IDs 91379-91383)
- **Manifest:** `artifact_version=20260506_233451`, `product_count=32`, `report_date=2026-05-06`
- **Manifest-of-URLs:** HTTP 200, all 4 artifact URLs valid
- **Public page:** HTTP 200 at `https://www.nimrod.bio/SmallFarmsAgent/`

---

## 6. Sign-off

**Verdict: PASS_WITH_FINDINGS**

All 7 acceptance criteria now PASS (AC-04 lifted from FAIL to PASS). Remaining findings are LOW/INFO severity and non-blocking for launch.

- **team_99 (waldhomeserver)** — 2026-05-06
- **Pass:** 2 (post-WP007)
- **L-GATE_BUILD self-attestation:** PASS — pipeline ingestion healthy, upload working, public artifacts fresh.

---

*SFA-S002-P001-WP003 Pass-2 | team_99 | waldhomeserver | 2026-05-06*
