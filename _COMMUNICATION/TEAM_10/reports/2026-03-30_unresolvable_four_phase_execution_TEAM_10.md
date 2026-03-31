# Unresolvable backlog — four-phase execution (Team 10)

**Date:** 2026-03-30  
**Plan reference:** Four-phase operational playbook (diagnose → remediate → measure → guardrails).  
**SOP in repo:** [`documentation/05-admin-and-operations/UNRESOLVABLE_BACKLOG_PLAYBOOK.md`](../../../documentation/05-admin-and-operations/UNRESOLVABLE_BACKLOG_PLAYBOOK.md)

---

## Phase 1 — Diagnosis (results)

**Snapshot time (UTC):** 2026-03-31T19:09:52 (from `normalizer_diagnostics_v1` payload).

| Metric | Value |
|--------|------:|
| `unresolvable_total` | 265 |
| Dominant bucket | **`no_alias_match`** — 100% of unresolvable rows |

**Top concentration (Pareto):** Most distinct raw strings appear **once**; largest row-count in sample was **2** (`מלח אטלנטי אפור לח`). The backlog is **high cardinality** (many unique retail strings), not a single typo.

**Sources (30d window, unresolvable > 0):**

| Source code | Name | Unresolvable | Total rows 30d | Rate % |
|-------------|------|-------------:|---------------:|-------:|
| SRC004 | קיימא בית זית | 254 | 398 | 63.8 |
| SRC002 | סבתא יהודית | 11 | 94 | 11.7 |

**Interpretation:** Phase 2 focus should be **SRC004** first (parser + alias + scope policy for mixed retail grids), plus **`no_alias_match`** work (aliases only where strings map to **existing** V1 vegetables; otherwise **scope_skip** after lead approval).

**Automated recommendations (from diagnostics engine):**  
`no_alias_match dominates: add global or source-scoped product_aliases and re-run catalog_renormalize; use /unresolved for top raw strings.`

**[USER ACTION REQUIRED] — prioritization:** Confirm whether the next sprint deep-dives **SRC004** HTML/selectors and product mix vs. a **global alias** campaign. Mixed grids likely need both **narrow aliases** for in-catalog vegetables and **approved scope_skip** rows for cleaning / dry grocery noise.

**Phase 2 focus chosen for this execution (without waiting on reply):** Safe **global bare aliases** for three strings that clearly map to existing products (see Phase 2). Broader SRC004 and new **scope_skip** patterns are **deferred for your approval**.

---

## Phase 2 — Remediation (results)

### Implemented (engineering)

- **Alembic `027_bare_aliases_zucchini_potato_clementine`:** global `product_aliases` (source_id NULL), `ON CONFLICT DO NOTHING`:
  - `קישוא` → PRD007 (קישוא)
  - `תפוח אדמה אדום` → PRD056 (תפוח אדמה)
  - `קלמנטינה` → PRD055 (קלמנטינה) — bare form; longer alias already existed.

### Not implemented (requires your approval)

- **New `catalog_scope_skip_rules`** for high-volume retail noise from SRC004 (e.g. salt, shampoo, dish liquid, deodorant) — **per playbook, always consult before adding.**
- **Parser changes** for SRC004 — engineering task; consult if unit/price semantics are ambiguous.

### Post-change pipeline

- Ran: `python3 -m organic_market_agent catalog_renormalize` after `alembic upgrade head`.

**Normalizer counts from that run:** `resolved=3 unresolvable=262 scope_skipped=0 skipped=0`  
**Re-queued rows:** 265 (`unresolvable` → `extracted` then processed).

### Metrics after Phase 2 batch

Current DB snapshot (same moment as Phase 3): `normalized=165`, `unresolvable=262`, `extracted=7`, `ignored=68`, resolution **38.64%**, distinct unresolved names **261**.

---

## Phase 3 — Rhythm and quality gate (results)

### `run_normalizer --metrics` (price_grid, non-quarantined)

**Note:** This CLI aggregates **all historical** `raw_extracted_items` for price_grid / non-quarantined sources — not only the current open backlog. After this cycle it printed:

- `unresolvable_rate`: **55.7%** → threshold **`unresolvable_rate <= 30%`**: **FAIL**
- `resolved`: 11009, `unresolvable`: 20588 (lifetime row counts)

For **current** backlog health, use admin **`/diagnostics/normalizer`** or `compute_normalizer_snapshot` (table below).

### Snapshot vs `data/normalizer_baseline.json`

| Metric | Baseline (file) | Current DB (after Phase 2) | Delta |
|--------|-----------------|----------------------------|-------|
| Resolution % (norm / norm+unres) | 32.52% | **38.64%** | **+6.12 pp** |
| `unresolvable` rows | 332 | **262** | **−70** |
| `normalized` rows | 160 | **165** | **+5** |
| `ignored` | 0 | 68 | unchanged this batch |
| Distinct unresolved raw names | 322 | **261** | **−61** |

**Gate (baseline file comparison):** resolution and unresolvable counts **improved** vs the frozen baseline; the **30%** CLI gate remains **failed** on lifetime data.

**[USER ACTION REQUIRED] — baseline:** Whether to **refresh** `data/normalizer_baseline.json` to this post-cycle snapshot (new floor) or keep the 2026-03-31 17:32 baseline for long-term % tracking.

---

## Phase 4 — Regression prevention (retro)

- **This cycle:** Applied a **small alias batch (3)** per guardrails; avoided scope_skip and parser edits pending policy/parser ownership.
- **Next cycle:** Re-run Phase 1 diagnostics; if SRC004 still dominates, schedule **source-scoped** investigation (sample HTML + top 50 strings export) before large alias seeding.
- **Consult lead** before any change that alters how **community-visible** prices aggregate (parser unit fixes, ambiguous aliases).

---

## Appendix — how to reproduce

```bash
alembic upgrade head
python3 -m organic_market_agent catalog_renormalize
python3 -m organic_market_agent run_normalizer --metrics
```

Diagnostics payload: `from organic_market_agent.admin.routes.diagnostics import _collect_payload` + `SessionFactory()` (see [`diagnostics.py`](../../../organic_market_agent/admin/routes/diagnostics.py)).
