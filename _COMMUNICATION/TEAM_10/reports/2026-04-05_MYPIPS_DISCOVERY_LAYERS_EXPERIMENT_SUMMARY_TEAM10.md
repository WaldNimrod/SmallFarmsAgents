# MyPIPS multi-layer discovery — experiment summary (Cursor IDE)

**Date:** 2026-04-05  
**Team:** Team 10 (local implementation + verification)  
**Context:** Executes the approved **MyPIPS multi-layer discovery** experiment plan (2026-04-05): Team 80 hybrid strategy — external signals → normalize slug → validate with existing probe.

---

## 1. Objective

Determine which **discovery layers** are actionable inside the **Cursor IDE / repo** (httpx, bounded `web_search`, CLI), and measure **yield** (unique slugs, `active=True` after `is_likely_active`) compared to **in-platform slug guessing**.

---

## 2. Per-layer results

| Layer | Description | Verified outcome | Production follow-up |
|-------|-------------|------------------|------------------------|
| **L4** | `robots.txt` / sitemap leakage | **No store enumeration** via sitemap on `mypips.app`. `mypips.info` WIX sitemap lists **marketing pages only** (includes `/merchants` URL, not per-store URLs). | **Baseline documented**; not a discovery channel for slugs. |
| **L3** | `mypips.info/merchants` | **SSR HTML ~652 KB** (Wix). **Zero** occurrences of `mypips.app/<slug>` in raw HTML; merchant grid is **client-rendered**. No slug list extracted without JS execution or deeper API reverse-engineering. | **Maybe** with browser automation or documented public API — **not** solved by httpx-only fetch. |
| **L1** | `site:mypips.app` queries (Hebrew terms) | **High yield** of real storefront URLs in search snippets (see appendix). | **Yes** — use **Google Custom Search JSON API** or curated manual exports; avoid scraping `google.com` HTML. |
| **L2** | `"mypips.app"` + Hebrew / web mentions | **High yield** for Hebrew queries; English `"mypips.app" order` returned **noise** (unrelated “MyPip” products). | **Yes** for Hebrew / local web index; tune query matrix. |
| **L5** | Conservative variants (`-1`, `-2`, hyphen-stripped) from known slugs | **99** candidates probed; **32** `active=True`. Variants mostly **shell**; **two useful alternates** found: `mahlevothabraun` (vs `mahlevot-habraun`), `salhagolan` (vs `sal-hagolan`). | **Maybe** — small **alias** expansion after seed slugs are known; **not** a primary discovery mechanism. |

### 2.1 Layer 4 — Evidence (abbrev.)

- **`https://mypips.app/robots.txt`** — HTTP 200; `Crawl-delay: 20`; disallows admin/auth/cart paths; **no `Sitemap:` line** in file.
- **`https://mypips.app/sitemap.xml`** — HTTP 200 but body is **SPA shell HTML**, not XML sitemap.
- **`https://mypips.info/robots.txt`** — HTTP 200; **`Sitemap: https://www.mypips.info/sitemap.xml`**.
- **`https://www.mypips.info/sitemap.xml`** — WIX sitemap index → `blog-categories-sitemap.xml`, `blog-posts-sitemap.xml`, `pages-sitemap.xml`.
- **`https://www.mypips.info/pages-sitemap.xml`** — Lists site pages (`/merchants`, `/pricing-plans`, …); **no** `mypips.app/{slug}` URLs.

### 2.2 Layer 3 — Evidence (abbrev.)

- **`https://www.mypips.info/merchants`** — Large Wix payload; `grep -c 'mypips.app/'` on downloaded HTML = **0** (no per-store links in SSR document).

---

## 3. Validation runs (existing probe)

CLI addition: **`--seeds-only`** on [`scripts/mypips_discover.py`](../../../scripts/mypips_discover.py) — same behavior as `--reference` but uses **`--seeds FILE`** (no Hebrew/English/numeric/year expansion).

| Artifact | Candidates | `active=True` | Notes |
|----------|------------|---------------|--------|
| L1+L2 deduped slug file [`output/discovery/experiments/2026-04-05_layer1_2_slugs.txt`](../../../output/discovery/experiments/2026-04-05_layer1_2_slugs.txt) (gitignored) | 31 | **30** | One slug `hilinoa` (from `hili.noa`) is **wrong** → generic shell. |
| L5 variants [`output/discovery/experiments/2026-04-05_layer5_variant_seeds.txt`](../../../output/discovery/experiments/2026-04-05_layer5_variant_seeds.txt) | 99 | **32** | Includes base + `-1`/`-2` + hyphenless variants; most suffixes are shell. |

Experiment CSV/TXT outputs under `output/discovery/experiments/` (default gitignore).

---

## 4. Combined stats

- **Unique slugs harvested from search (L1+L2 matrix):** 31 (after dedupe vs reference list overlap).
- **Confirmed active stores in that batch:** 30 / 31 (**~97%** of probed slugs; denominator excludes one bad normalization).
- **Contrast:** Broad generative slug scan (prior work) produced **~0** actives in large random samples — **search-backed discovery is orders of magnitude better** for this platform.

---

## 5. Gaps and dependencies

| Gap | Owner / next step |
|-----|-------------------|
| **No programmatic Google harvest in-repo** | Nimrod: optional **Google Custom Search API** key + quota; or periodic **manual** export of SERP URLs. |
| **`mypips.info/merchants` data** | Needs **JS-rendered DOM** or **undocumented API** — Team 80 / spike with browser Network tab; respect ToS. |
| **Crawl-delay** | `mypips.app` declares **`Crawl-delay: 20`** — experiments used **1.0 s** delay for practicality; **production** should align with policy + Team 100. |
| **Legal** | Confirm **Terms of Use** for bulk use of search-derived URL lists and probe frequency. |

---

## 6. Recommended next engineering steps

1. **Primary:** Implement a **“search harvest”** step **outside** brute-force slug generation: ingest a **text list of URLs** (from Custom Search or manual paste), normalize to slugs, run **`--seeds-only`** (or DB-backed queue) → promote to `Source` per onboarding.
2. **Secondary:** Optional **browser** pass on `/merchants` to log XHR endpoints if publicly accessible and compliant.
3. **Tertiary:** Maintain **`data/mypips_discovery_allowlist.txt`** (or similar) of **search-validated slugs** under version control — **not** the full gitignored CSV dump.
4. **Deprioritize:** Further **random slug expansion** without external seeds.

---

## Appendix A — L1 / L2 query matrix (executed via `web_search` in Cursor)

| # | Query | Useful `mypips.app` storefront URLs in results |
|---|--------|-----------------------------------------------|
| 1 | `site:mypips.app ירקות` | Yes (e.g. fruit4soul, mashtelatharoe, shaked, organicaganyarak-home, the-group) |
| 2 | `site:mypips.app משק` | Yes (meshek-herskovits, poli, brodavkameshek, barshah, mesheknaveh) |
| 3 | `site:mypips.app "הזמנות"` | Mixed (some real slugs: hagitsigal, fourminimonline, freshness; also generic shells) |
| 4 | `site:mypips.app סל` | Yes (salata, sal-hagolan, solomon, vigenbari, veghit) |
| 5 | `site:mypips.app תוצרת` | Yes (brodavkameshek, mahlevot-habraun, arava, popisrael, cohen) |
| 6 | `"mypips.app" ירקות` | Yes (overlaps + bestfruit) |
| 7 | `"mypips.app" משק` | Yes (meshek27, we-connect) |
| 8 | `"mypips.app" order` | **No** useful MyPIPS storefront URLs (irrelevant third-party sites) |

---

## Appendix B — References

- [`organic_market_agent/discovery/mypips_scan.py`](../../../organic_market_agent/discovery/mypips_scan.py) — probe logic.  
- [`_COMMUNICATION/TEAM_10/reports/2026-04-04_MYPIPS_SPIKE_ASSESSMENT_TEAM10.md`](2026-04-04_MYPIPS_SPIKE_ASSESSMENT_TEAM10.md) — prior platform notes.  
- [`_COMMUNICATION/TEAM_80/reports/2026-04-05_MYPIPS_STORE_ENUMERATION_RESEARCH_BRIEF_TEAM80.md`](../../TEAM_80/reports/2026-04-05_MYPIPS_STORE_ENUMERATION_RESEARCH_BRIEF_TEAM80.md) — research brief to Team 80.
