# Scope skip seed + public/admin data_quality — closure (Team 10)

**Date:** 2026-03-31  
**Reference:** Nimrod approval (סבון → `cleaning`, חליטה lines → `dry_grocery`; remainder of numbered catalog approved). Migration `026_seed_catalog_scope_skip_rules.py` applied (`alembic upgrade head`).

## Delivered surfaces

| Surface | What was added |
|---------|----------------|
| **Admin dashboard** | Card “תמונת איכות צינור” — same counts as publish (`compute_raw_pipeline_counts`). |
| **`public_report.json`** | Top-level `data_quality` object (raw status breakdown, resolution %, active scope-skip rule count). |
| **`manifest.json`** | Same `data_quality` block for lightweight consumers. |
| **`public_report.html`** | Hebrew transparency section above the price table, aligned with JSON keys. |
| **Documentation** | `documentation/01-overview/PROJECT_VISION_AND_SYSTEM_MAP.md` — vision, boundaries, repo map, pipeline diagram; linked from `documentation/01-overview/README.md`. |
| **Doc hub** | Fixed broken relative link in `documentation/README.md` (`external-references/`). |

## Improvement vs `data/normalizer_baseline.json` (local DB snapshot)

Baseline captured: `2026-03-31T17:32:59.042672+00:00`  
Current snapshot: `2026-03-31T19:03:37.642463+00:00` (post-migration; **catalog renormalize not re-run** in this measurement window).

| Metric | Baseline | Current | Delta | Relative (vs baseline) |
|--------|----------|---------|-------|-------------------------|
| Resolution % (norm / norm+unres) | 32.52% | 32.93% | **+0.41 pp** | +1.26% of baseline rate |
| `unresolvable` row count | 332 | 332 | 0 | 0% |
| `normalized` row count | 160 | 163 | **+3** | +1.88% |
| `ignored` row count | 0 | 0 | 0 | — |
| Distinct unresolved raw names | 322 | 322 | 0 | 0% |
| `ignored_approved_scope_skip` | — | **0** | — | Rules seeded (**13** active); rows gain this flag **after** lines are re-processed through the normalizer with the new rules. |

**Action for stronger “after” metrics:** run maintenance **catalog renormalize** (or full refresh per ops playbook), then re-publish; recompute snapshot vs baseline. Expect `ignored` / `ignored_approved_scope_skip` to rise where patterns match, and resolution % / unres counts to move accordingly.

## Blockers

None.
