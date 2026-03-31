# Normalizer / pipeline success improvements — report to Team 100

**Date:** 2026-03-31  
**From:** Team 10 (implementation)  
**To:** Team 100 (architecture)  
**Subject:** Outcomes of the Nimrod-approved backlog (grocery scope, admin UX, measurement discipline) and the four-phase unresolvable improvement process — with **completed full data replay** and **updated success metrics**.

---

## 1. Executive summary

Following project-lead decisions (grocery classified out of V1 scope, catalog inbox UX, source-level unit transparency, baseline/publish governance), we **implemented** schema and admin changes, **replayed** community `raw_extracted_items` through `NormalizerEngine` (scope-skip first), and **re-published** local artifacts.

**Headline metrics vs frozen file baseline** [`data/normalizer_baseline.json`](../../../data/normalizer_baseline.json) (captured `2026-03-31T17:32:59.042672+00:00`):

| Metric | Baseline | After `full_data_refresh` (this run) | Delta |
|--------|----------|--------------------------------------|-------|
| Resolution % (normalized / normalized+unresolvable) | 32.52% | **94.71%** | **+62.19 pp** |
| `unresolvable` row count | 332 | **9** | **−323** (−97.3%) |
| Distinct unresolved raw names | 322 | **9** | **−313** (−97.2%) |
| `normalized` row count | 160 | **161** | +1 |
| `ignored` (incl. approved scope-skip) | 0 | **325** | +325 |

**Interpretation for architecture review:** The step-change is **policy-aligned**: grocery and other retail lines are **not failures** — they are **`ignored` + `approved_scope_skip`** with explicit category codes. The residual **9** `unresolvable` rows are **`no_alias_match`** on in-scope strings and deserve the four-phase playbook (aliases / parser / narrow scope), not broad retail patterns.

**`run_normalizer` lifetime CLI gate** (`python3 -m organic_market_agent run_normalizer --metrics`) still aggregates **all historical** price_grid rows; it is **not** equivalent to the **current-table** snapshot above. Dashboard and `data_quality` in publish artifacts use the **current** definition.

---

## 2. Process completion (mandatory replay)

| Step | Command / artifact | Result |
|------|-------------------|--------|
| Full community replay | `python3 -m organic_market_agent full_data_refresh` | **OK** (2026-03-31 local run) |
| Normalizer (same run) | `resolved=161`, `unresolvable=9`, `scope_skipped=0` | Rows reset in this pass were already in `normalized`/`unresolvable`; lines already **`ignored`** (grocery) were **not** reset — by design in [`full_data_refresh.py`](../../../organic_market_agent/maintenance/full_data_refresh.py). |
| Aggregator | `daily_groups=61`, `updated=61` | OK |
| Publisher | `output/public` — **21 products** rolling 7d | OK |

---

## 3. Scope-skip inventory (ignored, `approved_scope_skip`)

| `category_code` (from `unresolvable_reason`) | Row count |
|---------------------------------------------|----------:|
| `grocery` | 257 |
| `dry_grocery` | 39 |
| `donation` | 16 |
| `cleaning` | 13 |
| **Total ignored (approved scope-skip)** | **325** |

Active rules in DB by `category_code` (includes **mined exact** `grocery` seeds from migration **028**): `grocery` **289**, `dry_grocery` **9**, `donation` **2**, `cleaning` **2** — **302** active rows total in `catalog_scope_skip_rules` (matches `data_quality.active_scope_skip_rules` at snapshot time).

---

## 4. Reference documents (repo)

| Topic | Path |
|------|------|
| Four-phase unresolvable SOP | [`documentation/05-admin-and-operations/UNRESOLVABLE_BACKLOG_PLAYBOOK.md`](../../../documentation/05-admin-and-operations/UNRESOLVABLE_BACKLOG_PLAYBOOK.md) |
| Baseline snapshot convention (dated files) | [`documentation/05-admin-and-operations/BASELINE_VERSIONING.md`](../../../documentation/05-admin-and-operations/BASELINE_VERSIONING.md) |
| Pre-publish checklist | [`documentation/05-admin-and-operations/PUBLISH_CHECKLIST.md`](../../../documentation/05-admin-and-operations/PUBLISH_CHECKLIST.md) |
| Grocery category + rules + mined seeds | Alembic [`028_grocery_scope_category_and_rules.py`](../../../organic_market_agent/db/versions/028_grocery_scope_category_and_rules.py) |
| Catalog inbox (suggestions + pending aliases) | Alembic [`029_catalog_inbox_suggestions_and_pending_aliases.py`](../../../organic_market_agent/db/versions/029_catalog_inbox_suggestions_and_pending_aliases.py); admin `/catalog/suggestions`, `/catalog/pending-aliases` |
| Source raw vs normalized units | [`organic_market_agent/admin/routes/sources.py`](../../../organic_market_agent/admin/routes/sources.py) + template `source_detail.html` |
| Prior four-phase execution log | [`2026-03-30_unresolvable_four_phase_execution_TEAM_10.md`](../../TEAM_10/reports/2026-03-30_unresolvable_four_phase_execution_TEAM_10.md) |
| Scope-skip draft / approval pattern | [`2026-03-31_scope_skip_catalog_DRAFT_FOR_NIMROD_APPROVAL.md`](../../TEAM_10/reports/2026-03-31_scope_skip_catalog_DRAFT_FOR_NIMROD_APPROVAL.md) |
| Glossary | [`docs/GLOSSARY.md`](../../../docs/GLOSSARY.md) |

---

## 5. Public / admin surfaces (transparency)

- **`public_report.json` / `manifest.json`:** `data_quality` block (raw pipeline counts, resolution %, active scope-skip rule count) — see [`publisher/engine.py`](../../../organic_market_agent/publisher/engine.py).
- **Admin dashboard:** same snapshot card + link to publish checklist path.
- **Scope-skip numbered catalog:** `/catalog/scope-skip`.

---

## 6. Risks and architecture follow-ups (for Team 100)

1. **Global `contains` grocery rules + mined `exact` rules** can drift when new retail strings appear; operational owner should run **Phase 1 diagnostics** periodically and extend rules via governed migration or future UI.
2. **False positives:** any future vegetable line that accidentally matches a grocery pattern must be caught via QA sampling or source-scoped rules if we introduce `source_id` on rules later.
3. **Baseline file:** project lead chose **not** to overwrite [`data/normalizer_baseline.json`](../../../data/normalizer_baseline.json) yet; large positive deltas vs that file are **expected** after policy change. Use [`BASELINE_VERSIONING.md`](../../../documentation/05-admin-and-operations/BASELINE_VERSIONING.md) for dated snapshots when resetting the reference floor.

---

## 7. Blockers

None for Team 100 review.

---

*Snapshot captured UTC: `2026-03-31T19:32:29Z` (immediately after `full_data_refresh` in the same environment used for this report).*
