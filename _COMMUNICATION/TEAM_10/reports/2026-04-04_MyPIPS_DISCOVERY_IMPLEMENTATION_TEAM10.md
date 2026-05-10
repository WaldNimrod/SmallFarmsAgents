# MyPIPS discovery — Team 80 handoff review and implementation (Team 10)

**Date:** 2026-04-04  
**Team:** 10 (Feature Dev)  
**Input:** `_COMMUNICATION/TEAM_80/mypips_discovery_package/`

---

## 1. Objective

Discover likely **active public** pages under `https://mypips.app/<slug>` to identify candidate **storefronts** for later promotion to OrganicMarketAgent **`Source`** rows (see Phase A in Team 100 onboarding). This tool does **not** ingest prices; it only probes URLs and writes CSV/TXT.

---

## 2. Review of Team 80 script (parity and fixes)

| Topic | Team 80 (`mypips_discover.py`) | Implemented |
|-------|--------------------------------|-------------|
| TLS | `ssl=False` on aiohttp connector (insecure) | **httpx** default **verified** TLS |
| HTTP stack | `aiohttp` | **`httpx.AsyncClient`** (matches [requirements.txt](../../../requirements.txt)) |
| User-Agent | `example.invalid` | **`OrganicMarketAgent-mypips-discovery/1.0 (+https://nimrod.bio; …)`** |
| “Not found” detection | Substring `404` in body → many false negatives | **Title-based** short error titles + **phrase** list in body snippet; **no** bare `404` in body |
| Result order | Completion order | **Sorted by URL** before save |
| Outputs | CWD defaults | **Default** `output/discovery/mypips_scan.csv` and `mypips_active.txt` (**gitignored**) |
| Ethics | README only | **Stderr reminder** (suppress with `--no-ethics-reminder`) |
| CLI | argparse flags | **Same surface** as Team 80 (`--seeds`, `--hebrew`, `--english`, `--workers`, `--delay`, `--years`, `--max`, `--out`, `--out-active`) |
| Generic 200 shell | All guessed slugs marked “active” (~5.8kB, same SPA) | **Reject** if `<title>` contains `מערכת ההזמנות של העסקים העצמאיים והקהילתיים בישראל` (real stores use a distinct middle segment, e.g. nimrod → “מהגינה של נימרוד”) |

---

## 3. Repository layout

* **Library:** `organic_market_agent/discovery/mypips_scan.py` — slugify, candidate build, `is_likely_active`, async scan, `save_results`.
* **CLI:** `scripts/mypips_discover.py` — prepends repo root to `sys.path`, runs scan.
* **Seeds (canonical):** `data/mypips_seeds.txt` (from Team 80 example list).
* **Reference slugs (calibration):** `data/mypips_reference_slugs.txt` — known tenant slugs (nimrod, fruit4soul, mypips, …) for smoke tests and documentation.
* **Tests:** `tests/test_mypips_discover.py` (no network).

---

## 4. How to run

```bash
cd /path/to/SmallFarmsAgents
python3 scripts/mypips_discover.py \
  --seeds data/mypips_seeds.txt --hebrew --english \
  --workers 4 --delay 1.0 --years --max 3000
```

Outputs:

* `mypips_scan.csv` — all attempts (`url`, `status`, `body_len`, `active`, `title`).
* `mypips_active.txt` — lines `URL | title` for rows marked active.

---

## 5. Handoff to Team 100 / Nimrod

* **Legal / policy:** Confirm **robots.txt** and **Terms of Use** for `mypips.app` before production-scale scans; large runs need Nimrod or Team 100 approval.
* **Source onboarding:** Active URLs feed **manual** triage → new `Source` + `source_fetch_profile` per [Team 100 source onboarding](../../TEAM_100/reports/2026-04-04_SOURCE_ONBOARDING_PHASES_A_B_TEAM100.md) (Phase A community stores unless classified otherwise).
* **Out of scope (this deliverable):** DB table for candidates, admin import UI, automatic `Source` creation.

---

## 6. Documentation

* [documentation/06-scripts-and-cli/README.md](../../../documentation/06-scripts-and-cli/README.md) — section “MyPIPS discovery”.

---

**Blockers:** None. **Team 50:** optional smoke test with small `--max` against live `mypips.app` in an approved environment.
