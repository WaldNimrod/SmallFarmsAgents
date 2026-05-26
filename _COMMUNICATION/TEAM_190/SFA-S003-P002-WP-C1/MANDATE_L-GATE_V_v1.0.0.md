---
id: MANDATE_SFA-S003-P002-WP-C1_L-GATE_V_v1.0.0
from: team_00 (via team_10 spec-author session)
to: team_190
date: "2026-05-26"
type: L-GATE_VALIDATE_MANDATE
wp: "SFA-S003-P002-WP-C1"
project: smallfarmsagents
gate: L-GATE_V
required_engine: "NON-Claude (GPT-5+, Gemini, etc.) per Iron Rule #1"
reviewed_commit: "72323aa"
spec_ref: "_aos/work_packages/S003/SFA-S003-P002-WP-C1/LOD400_spec.md"
build_report_ref: "_COMMUNICATION/team_10/SFA-S003-P002-WP-C1/BUILD_REPORT_v1.0.0.md"
unmapped_crops_ref: "_COMMUNICATION/team_10/SFA-S003-P002-WP-C1/UNMAPPED_CROPS_v1.0.0.md"
authorization_basis: "team_00 in-session grant 2026-05-26 (program-level for WP-C)"
prior_gates:
  - "L-GATE_E PASS 2026-05-26 by team_00"
  - "L-GATE_S PASS 2026-05-26 by team_10 (spec authoring)"
  - "L-GATE_B PASS 2026-05-26 by sfa_build (Claude Sonnet 4.7, separate session)"
status: ACTIVE
---

# L-GATE_V Validation Mandate — SFA-S003-P002-WP-C1

> **Iron Rule #1**: team_190 (you) must use a non-Claude engine. The builder
> was Claude Sonnet 4.7 (sfa_build). Validator engine MUST differ.

---

## §1 Scope

Validate the build of WP-C1 (Wave 1: Israeli Structured Data + Tend Multi-Year
Backfill) at commit `72323aa`. Issue verdict: PASS / PASS_WITH_FINDINGS / FAIL.

This is a **post-build constitutional + functional validation** — the standard
L-GATE_V pattern. Same kind of work you did on WP-A and WP-B successfully.

---

## §2 What was built (summary from BUILD_REPORT)

**Deliverables (per LOD400 spec):**
- Migration 049: `crop_planting_calendar` table (with TIMESTAMPTZ on created_at)
- Migration 050: `crop_cover_crops` table
- 2 ORM modules: `planting_calendar.py`, `cover_crops.py`
- 5 new importers:
  - `israeli/groworganic_importer.py` (L01, 86×26 sheet with seasonal markers)
  - `israeli/bustan_importer.py` (L36 1-page PDF via pdftotext -layout)
  - `israeli/idan_planning_importer.py` (L03 winter + L04 summer)
  - `jmf/cover_crops_importer.py` (L12 1-page PDF chart)
  - `tend_overlay.py` extended for years 2019/2020/2021
- `IL_CROP_MAP` + `resolve_il_crop()` in `constants.py`
- `source_registry.py` extended with NI/OP/PR entries
- CLI: `--c1-only`, `--no-c1` flags + `_run_c1_ingestion()` in `seed.py`
- 7 new test files (25 tests total)

**Note on migration numbering**: LOD400 §3 specified migrations 047/048,
but head was already 048 (from WP-B2/B1 patches). Builder reasonably
renumbered to 049/050. AC-C1-01/02 should be verified against actual filenames.

**Note on new `jmf/` package**: re-exports legacy `parse_jmf_dir` from the
flat `jmf.py` module to avoid import shadowing.

---

## §3 Verification commands (run all independently)

```bash
cd /Users/nimrod/Documents/SmallFarmsAgents

# 1. AOS validation
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
# Expect: 29 PASS / 19 SKIP / 0 FAIL

# 2. Focused C1 tests
python3 -m pytest \
  tests/crop_book/test_planting_calendar.py \
  tests/crop_book/test_cover_crops.py \
  tests/crop_book/test_groworganic_importer.py \
  tests/crop_book/test_bustan_importer.py \
  tests/crop_book/test_idan_planning_importer.py \
  tests/crop_book/test_cover_crops_importer.py \
  tests/crop_book/test_tend_multi_year.py
# Expect: 25 passed

# 3. Full test suite (no new failures)
python3 -m pytest tests/ -q --no-header 2>&1 | tail -10
# Expect: 673 PASS / 1 pre-existing fail (test_admin_routes)

# 4. Live DB sanity (PostgreSQL — `oma-postgres` on 5433)
python3 -c "
import sys; sys.path.insert(0,'.')
import sqlalchemy as sa
from organic_market_agent.db.session import SessionFactory
import organic_market_agent.crop_book.planting_calendar
import organic_market_agent.crop_book.cover_crops
with SessionFactory() as s:
    print('crop_planting_calendar:', s.execute(sa.text('SELECT COUNT(*) FROM crop_planting_calendar')).scalar())
    print('  NI:groworganic     :', s.execute(sa.text(\"SELECT COUNT(*) FROM crop_planting_calendar WHERE source = 'NI:groworganic'\")).scalar())
    print('  NI:bustan          :', s.execute(sa.text(\"SELECT COUNT(*) FROM crop_planting_calendar WHERE source = 'NI:bustan'\")).scalar())
    print('crop_cover_crops   :', s.execute(sa.text('SELECT COUNT(*) FROM crop_cover_crops')).scalar())
    print('Idan_2017 source vals:', s.execute(sa.text(\"SELECT COUNT(*) FROM crop_variety_source_values WHERE source = 'OP:Idan_2017'\")).scalar())
    for y in (2019, 2020, 2021):
        c = s.execute(sa.text(f\"SELECT COUNT(*) FROM crop_harvest_stats WHERE source = 'Tend_{y}'\")).scalar()
        print(f'crop_harvest_stats Tend_{y}: {c}')
"
# Expect counts to match BUILD_REPORT: 113 / 41 / 44 / 35 / 155 / 111 / 128 / 119

# 5. Migration reversibility (smoke test on SQLite in-memory or test PG)
alembic downgrade 048 && alembic upgrade head
# Expect: clean fwd/bwd

# 6. LOD500_LOCKED inventory check (no violations in commit 72323aa)
git show --name-only 72323aa | grep -E 'views\.py|publisher/wp_upload|publisher/upload_dispatch|db/versions/00[1-9]_|db/versions/0[1-3][0-9]_|db/versions/04[0-8]_|mu-plugin|tend\.py$|crop_book/models\.py'
# Expect: NO output

# 7. Roadmap NOT mutated by builder commit (IR#4)
git show --name-only 72323aa | grep -E '_aos/'
# Expect: NO output

# 8. Engine attribution preserved (IR#1)
git log -1 --format='%B' 72323aa | grep -i 'claude'
# Expect: Co-Authored-By line found

# 9. validate_enrichment.py — calibration improvement check
python3 scripts/validate_enrichment.py
# Expect: ≥3 new CALIBRATED pairs vs WP-B baseline (AC-C1-13)
```

---

## §4 Validation checklist (AC-by-AC, 20 ACs per LOD400 §9)

For each AC, mark PASS / FAIL / NOTE with evidence:

| AC | Description | Verify by |
|----|-------------|-----------|
| AC-C1-01 | Migration 049 (was 047) cleanly fwd/bwd PG + SQLite | Run command 5 |
| AC-C1-02 | Migration 050 (was 048) cleanly fwd/bwd PG + SQLite | Run command 5 |
| AC-C1-03 | `groworganic_importer` parses L01 → ≥30 rows | Live DB count = 41 ≥ 30 ✅ |
| AC-C1-04 | S+X both → 2 rows | Inspect importer logic + tests |
| AC-C1-05 | `IL_CROP_MAP` resolves ≥80% | BUILD_REPORT cites 90.7% (107 labels) |
| AC-C1-06 | `bustan_importer` ≥20 crops with month booleans | Live DB count = 44 ≥ 20 ✅ |
| AC-C1-07 | `idan_planning_importer` round-trips L03+L04 | Live DB OP:Idan_2017 = 155 |
| AC-C1-08 | `cover_crops_importer` ≥10 rows incl. germ temp + hardiness zone | Live DB count = 35 ≥ 10 ✅ |
| AC-C1-09 | Tend 2019: 442 CROP_PLAN + 1,884 HARVESTS aggregated | Live DB Tend_2019 stats = 111 |
| AC-C1-10 | Tend 2020: 724 CROP_PLAN + 3,720 HARVESTS aggregated | Live DB Tend_2020 stats = 128 |
| AC-C1-11 | Tend 2021: 552 CROP_PLAN + 1,723 HARVESTS aggregated | Live DB Tend_2021 stats = 119 |
| AC-C1-12 | Reconciler picks up new sources | `reconcile_field` integration test |
| AC-C1-13 | `validate_enrichment.py` ≥3 new CALIBRATED pairs | Run command 9 |
| AC-C1-14 | CLI: `--c1-only`, `--no-c1`, `--all` flow | Inspect seed.py + smoke test |
| AC-C1-15 | All importers idempotent | Re-run + check no duplicates |
| AC-C1-16 | `validate_aos.sh` 29/19/0 | Run command 1 |
| AC-C1-17 | ≥25 new tests; existing 0 regressions | Run commands 2+3 |
| AC-C1-18 | No LOD500_LOCKED file modified | Run command 6 |
| AC-C1-19 | UNMAPPED_CROPS filed if any | File exists with 10 unmapped labels |
| AC-C1-20 | BUILD_REPORT filed | File exists at `_COMMUNICATION/team_10/...` |

---

## §5 Constitutional checks (Iron Rules)

| IR | What to verify |
|----|----------------|
| **IR#1** | Builder is Claude Sonnet 4.7 (per commit 72323aa co-author trailer). You are non-Claude. Engine separation preserved. |
| **IR#4** | Builder commit 72323aa does NOT touch `_aos/roadmap.yaml` (IR#4 violation if it does). Verify via command 7. |
| **IR#6** | All artifacts in `_COMMUNICATION/team_10/SFA-S003-P002-WP-C1/`. |
| **IR#7** | DB schema mutations via alembic migrations 049+050 only (not raw DDL). |
| **IR#11** | No `_aos/governance/`, `_aos/lean-kit/`, `_aos/project_identity.yaml` mutations. Verify via command 7. |
| **IR#12** | No `/AOS_gov-update` or `/AOS_gov-sync` invocations (verify commit message). |

---

## §6 Verdict file

Write your verdict to:
`_COMMUNICATION/team_190/SFA-S003-P002-WP-C1/L-GATE_V_VERDICT_v1.0.0.md`

Frontmatter:
```yaml
---
id: SFA-S003-P002-WP-C1-L-GATE_V-VERDICT
type: l_gate_v_verdict
validator: team_190
date: 2026-05-26
wp: SFA-S003-P002-WP-C1
gate: L-GATE_V
round: 1
verdict: PASS | FAIL | PASS_WITH_FINDINGS
reviewed_commit: 72323aa
phase_owner: team_190
---
```

Body sections:
0. Verdict summary (1 paragraph)
1. Independent command evidence (raw output of all 9 commands)
2. AC-by-AC verification (20 ACs from §4) — PASS/FAIL/NOTE per row with evidence
3. Constitutional checks (IR#1/4/6/7/11/12) — PASS/FAIL per row
4. Findings (BLOCKER / MAJOR / MINOR + remediation route)
5. Final recommendation: roadmap transition to LOD500_LOCKED / further remediation
6. Engine identity footer (your engine name — must NOT be Claude)

### Decision rules
- All ACs PASS + all IRs PASS + 0 findings → verdict=PASS → LOD500_LOCKED authorized
- Any BLOCKER → verdict=FAIL → remediation cycle required
- Any MAJOR → verdict=PASS_WITH_FINDINGS → team_00 decides
- MINOR/NOTE only → verdict=PASS

---

## §7 Known notes (advisory — not findings)

1. **Migration numbering drift**: LOD400 spec said 047/048; builder used 049/050
   because head was already 048 (WP-B2/B1 patches). This is acceptable and
   documented in BUILD_REPORT. Should validate downward-compatibility but
   not flag as finding.
2. **10 unmapped Hebrew crops** in `UNMAPPED_CROPS_v1.0.0.md` — builder
   documented as worksheet artifacts + no DB baseline (acceptable per AC-C1-19).
3. **jmf/ package re-export**: legacy `parse_jmf_dir` re-exported from new
   `jmf/__init__.py` to avoid import shadowing. Backward-compatible.

---

*Mandate issued 2026-05-26 by team_10 (spec-author session) on behalf of
team_00 program grant. Activation prompt at:
`_COMMUNICATION/team_190/SFA-S003-P002-WP-C1/ACTIVATION_PROMPT.md`*
