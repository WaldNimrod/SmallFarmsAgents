---
id: MANDATE_SFA-S003-P002-WP-C4_L-GATE_V_v1.0.0
from: team_00 (via team_10 spec-author session)
to: team_190
date: "2026-05-26"
type: L-GATE_VALIDATE_MANDATE
wp: "SFA-S003-P002-WP-C4"
project: smallfarmsagents
gate: L-GATE_V
required_engine: "NON-Claude (GPT-5+, Gemini, etc.) per Iron Rule #1"
reviewed_commit: "27f6152"
spec_ref: "_aos/work_packages/S003/SFA-S003-P002-WP-C4/LOD400_spec.md"
build_report_ref: "_COMMUNICATION/team_10/SFA-S003-P002-WP-C4/BUILD_REPORT_v1.0.0.md"
url_audit_ref: "_COMMUNICATION/team_10/SFA-S003-P002-WP-C4/URL_AUDIT_v1.0.0.md"
license_audit_ref: "_COMMUNICATION/team_10/SFA-S003-P002-WP-C4/LICENSE_AUDIT_v1.0.0.md"
authorization_basis: "team_00 in-session grant 2026-05-26 (program-level for WP-C)"
prior_gates:
  - "L-GATE_E PASS 2026-05-26 by team_00"
  - "L-GATE_S PASS 2026-05-26 by team_10 (spec authoring, post-consolidated team_80 multi-engine FEEDBACK)"
  - "L-GATE_B PASS 2026-05-26 by sfa_build (Claude Sonnet 4.7, separate session) at commit 27f6152"
status: ACTIVE
related_validations:
  - "WP-C1 R2 PASS at commit ccd14d2 (sister wave; same gate cohort)"
---

# L-GATE_V Validation Mandate — SFA-S003-P002-WP-C4 (Wave 4: Web Sources)

> **IR#1**: team_190 (you) must use a non-Claude engine. Builder was Claude
> Sonnet 4.7. Validator engine MUST differ.

> **Engine v1.1 inheritance note**: WP-C1 R2 introduced
> `collect_source_values_with_inheritance` helper in `reconciler.py`. This is
> NOW part of the engine and applies to WP-C4 enrichment too. Expect
> production enrichment to reflect variety→species inheritance throughout.

---

## §1 Scope

Validate WP-C4 build (Wave 4: 8 web sources from multi-engine team_80 scout)
at commit `27f6152`. Issue verdict: PASS / PASS_WITH_FINDINGS / FAIL.

This is the **standard post-build L-GATE_V** pattern.

---

## §2 What was built (summary from BUILD_REPORT)

**Deliverables per LOD400 spec:**

- Migration **051** `crop_companion_matrix` (renumbered from spec's 050 — head was already 050 from WP-C1)
- Migration **052** `crop_postharvest_storage`
- 2 ORM modules: `companion_matrix.py`, `postharvest_storage.py`
- 8 new web importers under `organic_market_agent/crop_book/importer/web/`:
  - `uc_anr_germination.py` (CW-01)
  - `osu_frost_tolerance.py` (CW-02)
  - `umd_soil_ph.py` (CW-03)
  - `ne_veg_guide_nutrients.py` (CW-04)
  - `il_moa_calendar.py` (CW-05 — **CRITICAL** Israeli source from multi-engine win)
  - `seeds_per_gram.py` (CW-06)
  - `uf_ifas_companion.py` (CW-07)
  - `uc_davis_postharvest.py` (CW-08)
- `scripts/download_web_sources.py` (one-time downloader, 10/14 URLs cached = 71%)
- 14 source_registry.py entries + `EN_CROP_MAP` + `resolve_en_crop()` in constants.py
- CLI: `--c4-only`, `--no-c4`, `_run_c4_ingestion()` in seed.py
- 27 new test_c4_* tests

**Build report metrics (live DB):**
- 56 IL NI calendar rows
- 29 companion pairs
- 32 postharvest rows
- 98+ new `crop_variety_source_values` rows (PR/OP sources)

**URL audit (4 blocked sources documented):**
- IL MoA, Shaham, UF/IFAS, Osborne — used committed extract.json fallbacks
- All 4 fallbacks documented in `URL_AUDIT_v1.0.0.md`

---

## §3 Verification commands

```bash
cd /Users/nimrod/Documents/SmallFarmsAgents

# 1. AOS validation
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
# Expect: 29 PASS / 19 SKIP / 0 FAIL

# 2. Focused C4 tests
python3 -m pytest tests/crop_book/test_c4_*.py
# Expect: 27 passed

# 3. Full suite (post-C4 + post-WP-C1-R2 stable DB)
python3 -m pytest tests/ -q --no-header 2>&1 | tail -10
# Expect: ~700 passed, 1 pre-existing fail (test_admin_routes from WP-B era)

# 4. Live DB sanity per AC targets (BUILD_REPORT cites these counts)
python3 -c "
import sys; sys.path.insert(0,'.')
import sqlalchemy as sa
from organic_market_agent.db.session import SessionFactory
import organic_market_agent.crop_book.enrichment_models  # noqa
import organic_market_agent.crop_book.companion_matrix  # noqa
import organic_market_agent.crop_book.postharvest_storage  # noqa
with SessionFactory() as s:
    print('crop_companion_matrix:', s.execute(sa.text('SELECT COUNT(*) FROM crop_companion_matrix')).scalar())
    print('crop_postharvest_storage:', s.execute(sa.text('SELECT COUNT(*) FROM crop_postharvest_storage')).scalar())
    il = s.execute(sa.text(\"SELECT COUNT(*) FROM crop_planting_calendar WHERE source LIKE 'NI:il_%' OR source = 'NI:shaham_extension'\")).scalar()
    print(f'IL MoA + Shaham calendar rows: {il}  (AC-C4-07 requires >= 30)')
    for src in ['PR:uc_anr_germination', 'PR:osu_frost_tolerance', 'PR:umd_soil_ph',
                'PR:ne_veg_guide', 'OP:vital_seeds_count', 'OP:osborne_seed_count']:
        n = s.execute(sa.text(f\"SELECT COUNT(*) FROM crop_variety_source_values WHERE source = '{src}'\")).scalar()
        print(f'  {src}: {n} rows')
"

# 5. CW-05 IL MoA Hebrew preservation (AC-C4-08)
python3 -c "
import sys; sys.path.insert(0,'.')
import sqlalchemy as sa
from organic_market_agent.db.session import SessionFactory
with SessionFactory() as s:
    rows = s.execute(sa.text(\"\"\"
        SELECT notes FROM crop_planting_calendar
        WHERE source LIKE 'NI:il_%'
        AND notes IS NOT NULL
        LIMIT 5
    \"\"\")).fetchall()
    for r in rows:
        if r[0]:
            # No JSON-escaped unicode (\\uXXXX) in stored Hebrew
            assert '\\\\u05' not in r[0], f'Hebrew escape detected: {r[0]!r}'
    print('AC-C4-08: Hebrew preserved (no \\\\uXXXX escapes in IL MoA notes)')
"

# 6. URL audit + LICENSE audit committed
ls _COMMUNICATION/team_10/SFA-S003-P002-WP-C4/{URL_AUDIT,LICENSE_AUDIT,BUILD_REPORT}_v1.0.0.md
# Expect: 3 files

# 7. validate_enrichment.py — confirm engine v1.1 still works with WP-C4 sources
python3 scripts/validate_enrichment.py 2>&1 | tail -10
# Expect: CALIBRATED >= 5 (engine v1.1 inheritance still in play)

# 8. LOD500_LOCKED inventory check (no violations in commit 27f6152)
git show --name-only 27f6152 | grep -E 'views\.py|publisher/wp_upload|publisher/upload_dispatch|db/versions/00[1-9]_|db/versions/0[1-3][0-9]_|db/versions/04[0-9]_|db/versions/050_|mu-plugin|tend\.py$|crop_book/models\.py'
# Expect: NO output

# 9. IR#4 — no roadmap mutation by builder commit
git show --name-only 27f6152 | grep '^_aos/'
# Expect: NO output (builder commit; spec-author commits roadmap separately)

# 10. Engine attribution (IR#1)
git log -1 --format='%B' 27f6152 | grep -i 'claude'
# Expect: Co-Authored-By line found
```

---

## §4 AC matrix (20 ACs from LOD400 §8)

For each AC, mark PASS / FAIL / NOTE with evidence:

| AC | Description | Expected |
|----|-------------|----------|
| AC-C4-01 | Migrations 051+052 apply cleanly fwd+bwd on PG + SQLite (was 051/052/053 in original spec; renumbered because head=050) | PASS |
| AC-C4-02 | `download_web_sources.py --source all` succeeds for ≥10 of 14 URLs (≥70%) | PASS (10/14 = 71% per URL_AUDIT) |
| AC-C4-03 | CW-01 UC ANR germination: ≥20 crops with °F→°C conversion verified | Sample-check 3 crops |
| AC-C4-04 | CW-02 frost tolerance: 3-source cross-validation; ≥15 crops single class | Inspect |
| AC-C4-05 | CW-03 UMD pH: ≥30 crops with `soil_ph_target` | Live DB query |
| AC-C4-06 | CW-04 NPK removal: ≥15 crops with `nutrient_removal_n/p/k_kg_ha` + `assumed_yield_t_ha` context | Live DB query |
| **AC-C4-07** | **CW-05 IL MoA + Shaham: ≥30 crop-month entries** | **CRITICAL — multi-engine win** |
| AC-C4-08 | Hebrew preservation (no `\uXXXX` escapes) | Run command 5 |
| AC-C4-09 | CW-06 seeds-per-gram: ≥10 crops; ≥3 cross-validated | Live DB query |
| AC-C4-10 | CW-07 companion: ≥20 pair-rows; all `evidence_strength='weak'` | Live DB query (29 rows per BUILD_REPORT) |
| AC-C4-11 | CW-08 postharvest: ≥30 crops in `crop_postharvest_storage` | Live DB query (32 rows per BUILD_REPORT) |
| AC-C4-12 | Reconciler blends new PR-tier sources; ≥5 (variety, field) pairs CALIBRATED | Run command 7 |
| AC-C4-13 | `NI:il_moa_*` + `NI:shaham_extension` hard-override correctly | Inspect crop_planting_calendar |
| AC-C4-14 | `seed.py --c4-only/--no-c4/--all` flow works | Code inspection |
| AC-C4-15 | Tests ≥20 passing; existing tests 0 regressions | Run commands 2+3 |
| AC-C4-16 | `validate_aos.sh` 29/19/0 | Run command 1 |
| AC-C4-17 | No LOD500_LOCKED file modified | Run command 8 |
| AC-C4-18 | URL_AUDIT_v1.0.0.md filed | Run command 6 |
| AC-C4-19 | LICENSE_AUDIT_v1.0.0.md filed | Run command 6 |
| AC-C4-20 | BUILD_REPORT filed | Run command 6 |

---

## §5 Constitutional checks (Iron Rules)

| IR | What to verify |
|----|----------------|
| **IR#1** | Builder Claude Sonnet 4.7 (commit 27f6152 trailer). You are non-Claude. |
| **IR#4** | Builder commit 27f6152 does NOT touch `_aos/roadmap.yaml`. Verify command 9. |
| **IR#6** | All artifacts in `_COMMUNICATION/team_10/SFA-S003-P002-WP-C4/`. |
| **IR#7** | DB schema mutations via alembic 051+052 only. |
| **IR#11** | No `_aos/governance/`, `_aos/lean-kit/`, `_aos/project_identity.yaml` changes. |
| **IR#12** | No `/AOS_gov-update` or `/AOS_gov-sync` invocations. |

---

## §6 Known notes (advisory — NOT findings)

1. **Migration renumbering**: LOD400 spec said 050/051/052; builder used
   051/052 because WP-C1 took 050. Documented in BUILD_REPORT. Not a finding.
2. **4 URLs blocked**: IL MoA, Shaham, UF/IFAS, Osborne. Used committed
   extract.json fallbacks per URL_AUDIT. AC-C4-02 explicitly allows ≥70%
   accessibility (10/14 = 71%, just clears bar).
3. **WP-C4 inherits engine v1.1 inheritance helper** from WP-C1 R2 (commit
   ccd14d2). This is by design — production reconciler now uses
   variety→species inheritance. Not a finding.

---

## §7 Verdict file

Write to: `_COMMUNICATION/team_190/SFA-S003-P002-WP-C4/L-GATE_V_VERDICT_v1.0.0.md`

Frontmatter:
```yaml
---
id: SFA-S003-P002-WP-C4-L-GATE_V-VERDICT
type: l_gate_v_verdict
validator: team_190
date: 2026-05-26
wp: SFA-S003-P002-WP-C4
gate: L-GATE_V
round: 1
verdict: PASS | FAIL | PASS_WITH_FINDINGS
reviewed_commit: 27f6152
phase_owner: team_190
---
```

Body:
- 0. Verdict summary
- 1. Independent command evidence (raw output, all 10 commands)
- 2. AC-by-AC verification (20 ACs from §4)
- 3. Constitutional checks (§5)
- 4. Findings (if any)
- 5. Final recommendation
- 6. Engine identity footer (non-Claude)

---

*Mandate issued 2026-05-26 by team_10 (spec-author session) on behalf of
team_00 program grant. Activation prompt:
`_COMMUNICATION/team_190/SFA-S003-P002-WP-C4/ACTIVATION_PROMPT.md`*
