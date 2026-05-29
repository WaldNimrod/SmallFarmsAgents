---
id: INCIDENT_SFA-S003-CROPBOOK-PROD-DATA-GAP_v1.0.0
from: team_100 (Chief Architect)
to: team_00 (Principal)
cc: team_99, team_190
date: 2026-05-29
type: incident
severity: HIGH (production crop-book empty; systemic delivery gap)
status: DIAGNOSED — fix needs live s1240 MySQL access
---

# INCIDENT — sfa.nimrod.bio crop-book is empty (data never reached production)

## Symptom
`https://sfa.nimrod.bio/crop-book/` (and table/search/detail) render the shell
but **no crop data**. Confirmed a real empty DB read (fresh unique search returns
no results; Cloudflare = DYNAMIC, not a CDN cache).

## Root cause #1 (systemic — the big one)
**The S003 crop-book data was never propagated to the production pipeline.**
- The production data source is the **server** oma-postgres (the 06:30 `sfa_ingest_push` cron reads it). It is at **alembic head 034** with **NO `crops`/`crop_varieties` tables** (only `products`/market S002).
- All S003 crop-book work (C1–C6, 70 crops, enrichment, head 057) lives **only on the Mac dev oma-postgres**.
- So the cron's crops push has always failed (`relation "crops" does not exist`) → uPress MySQL crop-book never populated.
- **Implication:** every S003 LOD500 closure was validated on the **dev** DB but never delivered to **production**.

## Attempted direct fix (team_100, 2026-05-29) — did NOT resolve the symptom
Pushed crop-book data from the Mac (which has it) via the designed ingest API:
- `sfa_ingest_push --table crops` → HTTP 200, **accepted 70 / rejected 0** (txn committed).
- `--table crop_varieties` → HTTP 200, **accepted 364 / rejected 0**.
- Verified the payload↔allowlist contract MATCHES (slug, hebrew_name, …).
- **Yet the live crop-book still reads empty.** Ingest commits, app reads 0.

## Root cause #2 (unresolved — needs live access)
The ingest endpoint (`/api/v1/ingest`) accepts+commits, but the crop-book read
sees nothing — on the same host. Candidate explanations, NOT distinguishable
without live s1240 MySQL/app access:
1. ingest write and crop-book read hit **different DBs/environments** on s1240;
2. an **app-level cache** (APCu/opcache/file) serving a stale empty crop list;
3. a uPress **origin ezCache** independent of Cloudflare.

## Required to resolve (s1240 — team_99 / uPress panel / phpMyAdmin)
1. `SELECT COUNT(*) FROM crops;` on the LIVE MySQL — did the 70 ingested rows land?
2. The crop-book app's actual DB DSN vs the ingest endpoint's DSN — same store?
3. Clear app/origin cache (or restart PHP) and re-check.

## Canonical fix (the real "finish")
Complete the production crop-book pipeline so the cron maintains it:
- Bring the crop-book schema+data to the **server** oma-postgres (migrate 034→057 + load the 70 crops / 364 varieties / enrichment / notes), OR designate the Mac as the crop ingest source on a schedule;
- Ensure `/api/v1/ingest` writes to the same store the live crop-book reads;
- Then re-run the crops/crop_varieties push and verify live.

## Honest status
The crop-book is **NOT fixed**. The media (heroes/og/favicon) IS live. team_100
stopped further blind prod writes pending live-DB visibility.

— team_100 (Claude Opus 4.7) 2026-05-29

---
## RESOLUTION 2026-05-29 — data IS live; my intermediate "still empty" was a diagnostic error
In-app diagnostic (read-only script via FTPS, using the app's own Db::create()):
- Live MySQL `sfanms2u_SFAUserUiDB`: **crops=70, crop_varieties=367** (correct slugs+Hebrew names); `ingest_log` shows my pushes `status: ok`.
- The app's EXACT listing query returns 70 rows; search for עגבנייה returns tomatoes; all columns present.
- Server-side render of `book_table` with live rows == the LIVE `/crop-book/table/` page: arugula ×6, **142 `<tr>` rows, ~140KB** — identical.

**Conclusion: the Mac→ingest push WORKED. The crop-book is populated** (`/crop-book/table/`, `/family/`, `/search/` show all 70 crops). My earlier "still empty" calls were a **diagnostic error** — my `grep` markers (`gj-cropcard`, a slug-link regex) didn't match the table view's row markup, so I misread populated pages as empty. The `/crop-book/` LANDING (`entry` → `book_entry`) is an intentional **hub** (no crop grid) — that's the "empty" appearance.

## STILL OPEN (durability — root cause #1 stands)
This was a **manual one-off push from the Mac**. The production server oma-postgres is still at head 034 with **no crop schema**, so the daily 06:30 cron **cannot maintain/refresh** crop-book data. If the MySQL is reset or a cron does a replace, it empties again. Canonical fix still required: align the server DB (migrate + load crop data) OR schedule the Mac push.
