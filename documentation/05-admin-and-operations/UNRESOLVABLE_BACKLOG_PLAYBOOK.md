# Unresolvable backlog — four-phase playbook

English SOP for reducing `raw_extracted_items` rows stuck in `extraction_status = 'unresolvable'`.  
Canonical terms: [`docs/GLOSSARY.md`](../../docs/GLOSSARY.md).

## Tools (admin + CLI)

| Step | Location |
|------|----------|
| Reason buckets, top raw strings, 30d per-source rates | Admin: `/diagnostics/normalizer` — [`diagnostics.py`](../../organic_market_agent/admin/routes/diagnostics.py) |
| JSON export | GET `/diagnostics/normalizer/export.json?raw_limit=80` (login required) |
| Top unresolved list + add alias | `/unresolved`, `/unresolved/<raw>` — [`unresolved.py`](../../organic_market_agent/admin/routes/unresolved.py) |
| Re-queue after alias / catalog DB change | `python3 -m organic_market_agent catalog_renormalize` |
| Full replay (destructive for community normalized+unres rows) | `python3 -m organic_market_agent full_data_refresh` |
| Forward gate metrics | `python3 -m organic_market_agent run_normalizer --metrics` |
| Baseline file | `data/normalizer_baseline.json` — refresh via `baseline_snapshot` / `write_baseline_snapshot_file` in [`baseline_metrics.py`](../../organic_market_agent/admin/baseline_metrics.py) |

## Phase 1 — Diagnose

1. Open `/diagnostics/normalizer`; record `unresolvable_total`, each **reason_bucket** %, and **recommendations**.
2. Open `/unresolved`; capture top distinct raw strings (Pareto).
3. Note **sources_30d** with highest unresolvable count or rate.
4. **Consult project lead** if two sources compete for the same sprint or buckets are ambiguous.

**Deliverable:** Short written snapshot (dominant bucket, top strings, priority sources, Phase 2 focus: alias vs parser vs scope).

## Phase 2 — Remediate

Match work to the dominant bucket:

- **`no_alias_match`** — add `product_aliases` (global `source_id` NULL or per-source); map only to **existing** V1 products unless catalog change is approved.
- **Price / empty price** — parser and normalizer price handling per source.
- **`empty raw_product_name`** — parser field mapping.
- **Out-of-scope lines** — new rows in `catalog_scope_skip_rules` **require explicit lead approval** (same governance as prior scope-skip catalog).

After DB rule changes: run **`catalog_renormalize`** (default). Use **`full_data_refresh`** only when a full replay is justified.

**Deliverable:** Change list + after metrics (unresolvable count, distinct unresolved names, resolution %, normalizer counts from last run).

## Phase 3 — Measure

1. Run `run_normalizer --metrics`; compare **unresolvable_rate** to the printed 30% line (price_grid, non-quarantined).
2. Compare live snapshot to `data/normalizer_baseline.json` (admin dashboard shows deltas).
3. **Consult project lead** before overwriting the baseline file (new floor vs long-term trend).

**Deliverable:** Metrics table + pass/fail vs agreed target.

## Phase 4 — Guardrails

1. Parser changes: prove on **one source** first; re-check diagnostics / source detail unresolved list.
2. Aliases: **small batches** (e.g. 5–15); `catalog_renormalize` after each batch; watch for collisions.
3. Scope rules: document approvals (Team 10 report or numbered table).

**Deliverable:** Short retro (what was tried, mini before/after, next Phase 1 date).

## Suggested cadence

- **Weekly:** Phases 1 → small Phase 2 batch → Phase 3 snapshot.
- **Monthly / milestone:** Phase 4 retro + optional baseline update (with sign-off).

## Related

- **Baseline versioning (dated snapshots):** [`BASELINE_VERSIONING.md`](BASELINE_VERSIONING.md)
- **Pre-publish review:** [`PUBLISH_CHECKLIST.md`](PUBLISH_CHECKLIST.md)
- **Catalog inbox (suggestions + pending aliases):** admin nav **תור קטלוג** → `/catalog/suggestions`, `/catalog/pending-aliases`

---

*Aligned with Team 10 execution report under `_COMMUNICATION/TEAM_10/reports/`.*
