# AUDIT — SFA-S002-P001-WP001 — M10 Spike Branch Integration

**Date:** 2026-05-07
**Author:** team_100 (Explore subagent)
**Source branch:** `cursor/m10-doc-mandates-spike` (3 unique commits, 58 commits behind main)
**Type:** WP_AUDIT_REPORT

---

## Commits

| SHA | Title | Files |
|-----|-------|-------|
| `bb981ed` | M10 doc mandates spike v1.1 — LOD400 comms, migrations 072/073, basket tier resolver, QA remediation, dev stack docs | 80+ |
| `9177d9f` | docs: promote CQ-P01–CQ-P09 to LOD 200 with arch approval, mandate, and roadmap v5.7 | 70+ (incl. migrations 031–071) |
| `113ede2` | Add M10 mandates and source spike planning docs | 5 (docs only) |

---

## Substantive content (by category)

### Code (production)
- **Migrations 072–073** in `organic_market_agent/db/versions/`:
  - `072_cq_p01_alias_batch.py` — CQ-P01: SCOPE_SKIP_RULES, GLOBAL_ALIASES, SCOPED_ALIASES (CQ mandate §3.1–3.2). Empty template awaiting Team 10 H1 data.
  - `073_src_wa_pending_manual.py` — extend `raw_extracted_items.extraction_status` CHECK to include `'pending_manual'`; seed SRC_WA source with canonical profiles (ARCH-20260408-TEAM20-RESPONSE §3.6–3.7).
- **Migrations 031–071** (41 total) from `9177d9f` — M10.2-5, M13 pre-stage, CSA/retail sources, parser activations, scope/alias refinements, cache busting.
- **Normalizer** — `basket_tier_resolver.py`: CSA basket → PRD025/026/027 (small/medium/large) tier resolver. Item-count priority over price; fallback PRD026.
- **Publisher** — `rolling_aggregate.py` updated (CONFLICT-LIKELY vs main).
- **Models** — `runs.py` extended (CONFLICT-LIKELY vs main).
- **Admin routes** — `products.py`, `runs.py`, `db/check.py`.

### Tests
- `test_basket_tier_resolver.py` — tier resolution + edge cases.
- `test_extraction_status_pending_manual.py` — constraint validation.
- `test_db_health.py` — connectivity, conditional skip via `require_postgres` fixture.
- `test_admin_routes.py`, `test_publisher_local.py` — admin + publisher coverage.

### Docs / specs (selected)
- `CHANGELOG.md` (+320 lines), `CLAUDE.md` (+44 lines, new), `_COMMUNICATION/ROADMAP.md` (+478 lines, v5.7).
- Team 10 mandates M10.2–5, M13 pre, CQ catalog quality, source spike, headless mypips, CSA retail.
- Team 10/20/100 handoffs/reports (10+ artifacts, ~3500 lines).

### Config / dev tooling
- `.python-version` (3.11), `.env.example` (+28 lines), `.claude/settings.json` (+36 lines), `scripts/docker-compose*.yml`, `scripts/verify_env.sh`, 16 SQL audit scripts in `scripts/g_v1_1_*.sql`.

### Generated / output (NOISE)
- `output/public/{manifest,public_report}.*` HTML/JSON samples — discard.
- `.run/admin_server.pid` — discard.

---

## Conflict surface map

| File | Status | Notes |
|------|--------|-------|
| `db/versions/072_cq_p01_alias_batch.py` | CLEAN | New on branch |
| `db/versions/073_src_wa_pending_manual.py` | CLEAN | Depends on 072 |
| `normalizer/basket_tier_resolver.py` | CLEAN | New on branch |
| `db/versions/031–071` | **NUMBERING-CONFLICT** | Main has its own `031_deactivate_src017_pricez.py` (Apr 21). Branch's 031 (`mypips_candidate_sources_workbook`, Apr 5) collides — must renumber on apply |
| `publisher/rolling_aggregate.py` | CONFLICT-LIKELY | Main touched (75e1fcb "1.2") |
| `models/runs.py` | CONFLICT-LIKELY | Main has 3 commits (07b49bc, 1f83142, 36a0cec) |
| `utils/config.py` | CONFLICT-LIKELY | Main touched |
| `publisher/{ftps_upload,templates}` | CONFLICT-LIKELY | UI overlap |
| `.env.example` | CONFLICT-LIKELY (low) | 3 main commits |
| `CHANGELOG.md` | CONFLICT-LIKELY | append-only helps; markers may clash |
| `CLAUDE.md` | ADD/ADD CONFLICT | both branches create |
| `_COMMUNICATION/ROADMAP.md` | CONTENT CONFLICT | v5.7 vs parallel main updates |
| `output/public/*` | CONFLICT (NOISE) | discard |
| `.claude/settings.json` | ADD/ADD (NOISE) | prefer main |

**Summary:** 14 conflicts. Production code at risk: 3 files (rolling_aggregate, runs, config). Migrations 072–073 0-risk after renumber. Tests clean. Docs resolvable manually.

---

## Migration safety

- **Main head:** `031_deactivate_src017_pricez.py` (Apr 21).
- **Branch chain:** 031–073, but **branch's 031 ≠ main's 031**.
- **BLOCKER:** Numbering collision. Strategy: keep main's 031, renumber branch's 031–073 to start at 032 and shift down_revision pointers accordingly.
- **Estimated migration count after integration:** 1 (main) + 43 (branch, renumbered 032–074) = 44 migrations on main.

---

## Recommended integration strategy

**STRATEGY C — Extract files + reapply** (modified cherry-pick).

### Rationale
58 commits behind main + migration 031 numbering collision rules out clean rebase. Cherry-picking 3 commits would still hit the renumber boundary. Extract intent, drop generated outputs, renumber migrations, manually resolve 3-file CONFLICT-LIKELY surface.

### Steps
1. Stage extraction directory.
2. Copy `072–073` → rename to `032–033`; adjust `down_revision`.
3. Copy `basket_tier_resolver.py` + tests; copy `db/check.py` + test.
4. Copy `.python-version`; manual-merge `.env.example`.
5. Reconcile `rolling_aggregate.py` (75e1fcb baseline + branch delta).
6. Reconcile `models/runs.py` (3-commit baseline + branch delta).
7. Reconcile `utils/config.py`.
8. Skip generated outputs and `.claude/settings.json` (use main).
9. Merge `CLAUDE.md` (branch version superior).
10. Consolidate `ROADMAP.md` (v5.7 + main parallel content).
11. Land Team 10 mandates async to `_COMMUNICATION/` (non-blocking).
12. Run full test suite. Run alembic upgrade head against fresh DB.

### Sprint estimate
**MEDIUM (3–5 days)** — extraction (1d), conflict reconciliation (2d), testing + docs (1–2d).

### Branch lifecycle
**Do NOT delete `cursor/m10-doc-mandates-spike` post-integration.** Tag as `archive/m10-spike-bb981ed` for audit-trail / future M13 pre-stage reference.

---

*End of audit.*
