# System status — development workstation vs waldhomeserver (SFA)

| Field | Value |
|-------|--------|
| **Date** | 2026-04-10 |
| **Report type** | Operational snapshot + today’s ingestion runs |
| **Team** | Team 10 (Feature Dev) |
| **Scope** | Local dev environment (Nimrod workstation), home server **waldhomeserver** (`nimrodw@10.100.102.2`), OrganicMarketAgent admin + PostgreSQL |

---

## 1. Executive summary

- **waldhomeserver** is healthy: disk and memory are fine, **`sfa-admin`** is **active**, Flask admin responds **HTTP 200** on `/`, `/runs`, `/products`, `/sources`. The `/runs` Jinja fix (`2ec3f47`) is deployed; the server repo is **one commit behind** `origin/main` (documentation-only: `5f6f306` Team 61 communication doc).
- **Today (Asia/Jerusalem calendar date 2026-04-10)** there was **one scheduled ingestion run** (cron): **`daily`**, status **`partial`**, **`triggered_by=cron`**, started **09:00:02 IL**, finished **09:06:13 IL**. Six sources succeeded; **SRC017 (Pricez)** failed three fetch attempts (**HTTP 403 Forbidden** from `https://www.pricez.co.il/`), consistent with **`retry_attempts=2`** in `scheduler_config` (three observed `source_fetch_runs` rows for the same source).
- **Pipeline / product signals:** Two **`pipeline_alerts`** rows were written for run `#1`: an **aggregation price-dispersion** warning (`[AGG_PRICE_RULE:two_source_price_spread_gt_100pct]`, product **PRD035**), and a **scheduler outcome** warning noting partial completion with one failed source.
- **Catalog / publishable data (server DB):** **67** products, **20** sources, **193** normalized observations — aligned with what the admin UI is designed to show at this scale.
- **Local development PostgreSQL** (`oma-postgres`, `localhost:5433`, database `organic_market_agent`) on the workstation has **no application tables** (empty schema). To mirror server-backed UI work locally, run **`alembic upgrade head`** (and seed if required) against that DSN.

---

## 2. Development workstation (local)

| Check | Result |
|-------|--------|
| **Git branch / HEAD** | `main` @ **`5f6f306`** (includes docs commit after server) |
| **Recent commits** | `5f6f306` Team 61 communication doc; `2ec3f47` `/runs` template fix; prior `c3fc864`, `8362119`, … |
| **Working tree** | Clean except untracked Team 100 mandate files (not part of app) |
| **Docker: `oma-postgres`** | Running, port **5433**, DB **`organic_market_agent`** — **`0` relations** in `public` (migrations not applied) |
| **`.env` `DATABASE_URL`** | Points to `127.0.0.1:5433/organic_market_agent` |

**Implication:** The **admin UI cannot be meaningfully exercised against real pipeline data on this machine** until migrations populate the local DB. This is an environment gap, not an application regression on the server.

---

## 3. waldhomeserver — host and services

| Check | Result |
|-------|--------|
| **Hostname / uptime** | `waldhomeserver`, ~5h uptime at collection time (load ~0) |
| **Disk** | `/` ~11% used (~9.7G / 98G); **`/data`** ~1% used (~1.2G / 916G) |
| **Git (SFA)** | `/data/projects/smallfarmsagents` @ **`2ec3f47`** (matches `/runs` fix; **not** yet at `5f6f306`) |
| **`systemctl sfa-admin`** | **active** / **running** (MainPID observed) |
| **HTTP (loopback)** | `/` **200**, `/runs` **200**, `/products` **200**, `/sources` **200** |
| **Docker** | `oma-postgres` **Up**, **5433→5432**; `tiktrack-phoenix-postgres-dev` also running |

**Scheduler (from server crontab):**  
`0 6 * * *` UTC → **09:00 Israel** (DST) — `python -m organic_market_agent.scheduler.runner` with log append to `/data/backups/sfa-scheduler.log`.  
Daily DB dump: `0 8 * * *` → `pg_dump` of `organic_market_agent` to `/data/backups/sfa-YYYYMMDD.sql.gz`.

---

## 4. Ingestion runs on 2026-04-10 (deep dive)

**Filter:** `(timezone('Asia/Jerusalem', started_at))::date = '2026-04-10'`

### 4.1 `ingestion_runs`

| id | run_type | status | triggered_by | Started (IL) | Finished (IL) |
|----|----------|--------|--------------|--------------|---------------|
| 1 | daily | **partial** | cron | 2026-04-10 09:00:01.97 | 2026-04-10 09:06:12.67 |

**Counts:** `runs_today = 1`, `runs_all_time = 1` (database still young on this host).

### 4.2 `source_fetch_runs` (same ingestion run)

| sfr.id | status | Source | Notes |
|--------|--------|--------|--------|
| 1–3 | **failed** | **SRC017** (Pricez) | Three rows: same **403 Forbidden** on `https://www.pricez.co.il/`; `retry_count = 2` on each |
| 4–9 | **success** | SRC018, SRC002, SRC004, SRC005, SRC006, SRC003 | — |

**Total `source_fetch_runs` linked to today’s run:** **9** (explained by retries on SRC017).

### 4.3 `scheduler_config` (active row)

| is_enabled | run_hour (UTC) | run_minute | retry_attempts | upload_enabled |
|------------|------------------|------------|----------------|----------------|
| true | 6 | 0 | 2 | false |

This matches the observed **06:00 UTC** cron and **three** fetch attempts for the failing source.

### 4.4 `pipeline_alerts` (ingestion_run_id = 1)

| id | level | Summary |
|----|-------|---------|
| 1 | warning | `[AGG_PRICE_RULE:two_source_price_spread_gt_100pct]` — `product_id=35` (**PRD035**), `date=2026-04-10`, `market_scope=community` (message truncated in query) |
| 2 | warning | `[SCHEDULER:run_outcome]` — run #1 **partial**: 1 source failed, 6 succeeded |

Both rows were still **unread** (`is_read = f`) at query time — consistent with the dashboard alert panel.

---

## 5. UI vs database (what operators should see)

| Surface | Server DB source | Value / note |
|---------|------------------|----------------|
| **Products** | `COUNT(*)` from `products` | **67** |
| **Sources** | `COUNT(*)` from `sources` | **20** |
| **Normalized observations** | `COUNT(*)` from `normalized_observations` | **193** |
| **Runs list** | Latest `ingestion_runs` | Single row today: **partial**, **cron**, ~6 min duration |
| **Run detail / per-source** | `source_fetch_runs` | Pricez **failed** with 403; others **success** |
| **Alerts** | `pipeline_alerts` | Price dispersion warning + scheduler partial warning |

No discrepancy was found between these aggregates and the intended admin UI semantics.

---

## 6. Recommended follow-ups

| Priority | Action |
|----------|--------|
| Low | On waldhomeserver: `git pull` to **`5f6f306`** when convenient (documentation only). |
| Medium | **SRC017 / Pricez:** investigate **403** (blocking, User-Agent, rate limit, or site policy). Expect continued **`partial`** daily runs until collector succeeds or source is deactivated. |
| Medium | **PRD035** price-dispersion rule: review if warning is expected for community scope; aligns with product rules in `docs/DATA_MODEL_AND_PUBLISH_DECISIONS_HE.md` / aggregator spec. |
| High (local dev) | Run **`alembic upgrade head`** against local `oma-postgres` so dev matches schema; optionally restore a dump from server **only** if approved for privacy/size (follow `PRIVACY_POLICY.md`). |

---

## 7. Evidence commands (repeatable)

**Server — today’s runs (Jerusalem date):**

```sql
SELECT id, run_type, status, triggered_by,
  timezone('Asia/Jerusalem', started_at) AS started_il,
  timezone('Asia/Jerusalem', finished_at) AS finished_il
FROM ingestion_runs
WHERE (timezone('Asia/Jerusalem', started_at))::date = DATE '2026-04-10'
ORDER BY id DESC;
```

**Local — schema empty check:**

```bash
docker exec oma-postgres psql -U oma -d organic_market_agent -c "\dt"
```

---

*End of report.*
