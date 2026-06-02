# CQ-P01 — Alias backlog triage table (A2)

**Date:** 2026-04-08  
**Team:** Team 10  
**Spec:** `SPEC-20260408-PHASE-A-LOD400` §A2  
**Baseline (LOD400):** 92 distinct unresolvable names; SRC021 historically dominant

## Export prerequisite (binding)

Full classification of **all 92** names requires a live DB export (spec §A2.2 Step 1):

```bash
curl -s "http://127.0.0.1:5000/unresolved/export.json?limit=500" | python3 -m json.tool
```

This session **could not** run the export (PostgreSQL unreachable — see env verification report).

## Registry cross-reference (2026-04-05 exceptions register)

| raw_name / theme | source | bucket | action / status |
|------------------|--------|--------|-----------------|
| מיקס בייבי | SRC061 | (a) | **fixed** — migration `071` |
| נבטים , תערובת | SRC061 | (a) | **fixed** — migration `071` |
| Passion fruit unit semantics | multiple | (open) | C2 / units — post Phase B |
| Pantry PRD087–PRD100 | SRC036 / retail | (c) / research | C3 + Team 100 D1 |
| Gadi CSA baskets | TBD | (d) | Escalate / architecture — not auto-mapped |
| New unresolvable backlog | SRC021, … | **pending export** | Run Step 1; map to (a)/(b)/(c)/(d) |

## Placeholder rows for remaining names (92 − documented above)

All remaining slots are **`PENDING_LIVE_EXPORT`**. Team 10 will complete the matrix in the same file (or a dated addendum) immediately after the export is available and before filing **final** G-V1.1 completion.

## Bucket legend

| Bucket | Meaning |
|--------|---------|
| (a) | Alias → migration 072 batch (`GLOBAL_ALIASES` / `SCOPED_ALIASES`) |
| (b) | New product → Team 100 approval first |
| (c) | Scope-skip → `SCOPE_SKIP_RULES` in 072 batch |
| (d) | Ambiguous → Team 100 escalation with evidence |
