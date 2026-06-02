# M13-PRE Data Foundation — Team 10 completion summary

**Date:** 2026-04-05  
**Task:** `MANDATE-20260404-M13-PRE-DATA-FOUNDATION` execution (aligned with M10.4 + M10.5)  
**Alembic head:** `065` (`065_m13_pre_mypips_cache_bust_dup_skip`)

---

## 1. Scope alignment (SRC036)

Per mandate §3.2, Teva (SRC036) lines are normalized via **product_aliases** and **`pantry_dry`** products rather than broad **ignored** scope-skip. Prior work (migrations **059–063**) deactivated M10.5 rules **3501–3514**, resolved conflicting global rules (**061–062**), and fixed Unicode apostrophe matching for residual pasta (**063**).

**G-PRE-4 verification (mandate SQL, all historical rows for SRC036):** normalized=75, unresolvable=0, **pct=100%** (local DB after migrations + renormalization).

---

## 2. CSA extraction (G-PRE-3)

| Source | Latest-run `raw_rows` (mandate §3.1 SQL) | Notes |
|--------|----------------------------------------|--------|
| SRC033 | 3 | OK |
| SRC034 | 2 | **064** adds `?_oma=m13_pre` on basket `entry_url` so fetches are not dropped as duplicate checksum skips; parser already extracts two baskets |
| SRC035 | 0 | **Policy:** `CsaBasketParser` `meshek_yosef` returns 0 SKUs (no stable basket prices on FAQ-style entry URL). Live HTML shows delivery/minimum fee copy, not priced CSA SKUs. **Acceptance:** 2 of 3 sources with `raw_rows > 0` (SRC033 + SRC034). |

---

## 3. M10.4 / mypips (G-PRE-1, G-PRE-2)

- **G-PRE-1:** Five of nine priority sources have **`normalized_observations` > 0** (SRC041, SRC053, SRC060, SRC061, SRC070). Threshold **≥5** met.
- **PRE-D9 (sources with extract rows):** SRC041, SRC053, SRC060, SRC061, SRC070 all **≥85%** normalized vs (normalized+unresolvable). SRC061 **96.8%** (2 unresolvable: `נבטים , תערובת`, `מיקס בייבי`).
- **065:** Cache-bust `?_oma=m10_4e` → `?_oma=m13_pre` for SRC042, SRC055, SRC062, SRC069 to avoid duplicate-asset skips. Post-bust live fetches for SRC042/055/062 returned HTML but **MypipsParser reported 0 product rows** (site/shell drift — separate parser follow-up). SRC069 fetch still hit duplicate checksum (byte-identical body vs prior asset).
- **E2E:** `BaseCollector` appends unique HTML comment when `RUN_MYPIPS_E2E` for **`mypips` and `sellio`** (T09).

---

## 4. Publish / G-PRE-5

After `catalog_renormalize` + `run_publisher`, **`len(public_report.json['products'])` = 76** (rolling window, 2-source community rule). **Below mandate 90.** Per execution plan, **Team 100 waiver** is required for G-PRE-5 unless aggregation window or source mix later reaches 90. Self-check: `M13_PRE_GPRE5_WAIVED=1 ./scripts/verify_m10_4_gate.sh`.

---

## 5. PRE-F4 scope-skip audit (real columns)

Mandate PRE-F4b referenced non-existent `source_scope`. Audited `catalog_scope_skip_rules` with **`id`, `display_order`, `category_code`, `match_type`, `pattern`, `notes`, `is_active`**.

- Rules **3501–3514** (Teva packaged / search remediation from **058**) are **`is_active = false`** with notes citing **059 M13-PRE**.
- Active tail of table is dominated by **M10.4 R2 SRC070** store-scoped `contains` patterns (e.g. seeds, checkout notes) — no new global vegetable suppression observed in sampled `ORDER BY id DESC LIMIT 22`.

---

## 6. Tests and DB health

- `python3 -m pytest tests/ -q` → **180 passed**, 5 skipped (local run).
- `python3 -m organic_market_agent.db.check` → **PASS**.

---

## 7. Deliverables

| Artifact | Path |
|----------|------|
| Combined QA request (G-PRE-1–7) | `_COMMUNICATION/TEAM_50/reports/2026-04-05_QA_REQUEST_M13_PRE_GPRE_TEAM10.md` |
| Gate self-check script | `scripts/verify_m10_4_gate.sh` (T03≥5, G-PRE-1 printout, optional G-PRE-5 waiver env) |
| Migrations | `064` SRC034 cache bust; `065` mypips cache bust (042/055/062/069) |

**Not filed (mandate §5 step 5):** Team 100 M13-PRE completion notice — **only after Team 50 QA PASS.**

---

## 8. Operator follow-ups

1. **G-PRE-7:** Run `python3 -m organic_market_agent run_publisher --upload` when ready to validate live site (HTTP 200).
2. **G-PRE-5:** Obtain written **Team 100 waiver** if 76 products is accepted for this window, or extend data breadth / window until ≥90.
3. **SRC042/055/062/069:** Parser or selector remediation if Team 50 requires more than five mypips contributors with live rows.
