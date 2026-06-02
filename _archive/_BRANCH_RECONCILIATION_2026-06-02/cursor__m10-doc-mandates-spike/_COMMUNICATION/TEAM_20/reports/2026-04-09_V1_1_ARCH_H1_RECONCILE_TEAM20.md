# H1 / ARCH reconciliation — v1.1.0 migrations 072–073

**Date:** 2026-04-09  
**From:** Team 20 (Infrastructure)  
**To:** Team 100, Team 10, Team 50  
**Refs:** ARCH-20260408-TEAM20-RESPONSE-V1-1 §3.7; `_COMMUNICATION/TEAM_20/reports/2026-03-30_V1_1_MIGRATION_072_REQUEST_TEAM10.md`

## Supersession of 2026-03-30 Team 10 H1

The 2026-03-30 request assigned **migration 072 = SRC_WA only** (with fetch/normalizer stubs) and deferred **A2** batch SQL.

**Team 100 (ARCH §3.7) supersedes that numbering:**

| Revision | ARCH purpose | 2026-03-30 H1 |
|----------|----------------|---------------|
| **072** | CQ-P01 — `catalog_scope_skip_rules` + `product_aliases` (A2) | Had SRC_WA here |
| **073** | SRC_WA + `pending_manual` CHECK on `raw_extracted_items` | (content moves to 073) |

**Operational parity:** Fetch profile + `normalizer_profiles` rows for SRC_WA (from the 2026-03-30 SQL pattern) are included in **073** after the source seed, per ARCH-20260408-TEAM20-RESPONSE-V1-1 §3.6 and the infrastructure plan note on profiles.

## A2 data (072)

No updated Team 10 H1 with row-level CQ-P01 triage (scope-skip + alias tuples) was present in-repo at authoring time. **072** ships with **empty** `scope_skip_rules`, `global_aliases`, and `scoped_aliases` lists using the **corrected ARCH templates** (confidence, `ON CONFLICT` targets, no `updated_at` on aliases). Team 10 should file a follow-up H1 with `display_order` band + rows when A2 triage is complete; Team 20 can add **074+** or amend per gate.

## SRC_WA source row (073)

Canonical seed fields follow **ARCH §3.6** (name `WhatsApp Community Submissions`, `priority` 3, `ON CONFLICT (code) DO NOTHING`). This replaces the 2026-03-30 draft name/priority for the **sources** row only.
