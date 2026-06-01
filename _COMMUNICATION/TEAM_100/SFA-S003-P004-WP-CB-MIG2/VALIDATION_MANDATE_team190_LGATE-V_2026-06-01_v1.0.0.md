# VALIDATION MANDATE + PROMPT — SFA-S003-P004-WP-CB-MIG2 (L-GATE_V) — team_100 → team_190 — v1.0.0

**Date:** 2026-06-01
**From:** team_100 (Chief System Architect, Claude Opus)
**To:** team_190 (Independent Validator)
**Routed by:** team_00
**Repo:** `/Users/nimrod/Documents/SmallFarmsAgents` · branch `claude/wp-cb-mig2-2026-06-01` · HEAD `c083cc3`
**Gate:** **L-GATE_V** (final constitutional validation) of WP-CB-MIG2 — Crop Data Model Expansion, after team_10 build + team_100 independent L-GATE_B verification + team_50 QA correctives.

---

## 0. Cross-engine constraint (IR#1/#5 — MANDATORY)
Builder = Claude Sonnet (team_10). Independent L-GATE_B verifier + QA correctives = Claude Opus (team_100). Therefore this L-GATE_V **MUST run on a NON-CLAUDE engine** (Cursor Composer / GPT-5.x / Codex). Confirm engine in the verdict header. team_100 NEVER self-issues L-GATE_V.

## 1. What this validates — and the data-application boundary (READ)
The build is **code + migration + tests complete** and **SQLite-verified**, but it was **not** applied to the live `oma-postgres` (no `alembic upgrade` on live, no PR backfill run, no console NI cycle). Accordingly:
- **In L-GATE_V scope:** code/spec fidelity to LOD400 **v1.0.1** + Canon **v1.3.0** (§15–§20, §16a); the Alembic **060** migration up/down (SQLite + dry PG inspection); the 4 L-GATE_S remediations present in code; constitutional checks; the test suite + validate_aos.
- **OUT of L-GATE_V scope (operational, post-gate, team_00/team_99):** applying 060 to live PG; running the PR backfill; running the manual-validation **console** + NI importer to populate the narrative-only / Israel-specific fields. Until that runtime cycle runs, those fields are legitimately EMPTY (UI shows "מוצע") — **not a defect**. Validate that the *mechanisms* are correct, not that live data exists.

## 2. Artifacts
- **LOD400 (LOCKED):** `_aos/work_packages/S003/SFA-S003-P004-WP-CB-MIG2/LOD400_spec.md` v1.0.1 (AC-01..AC-17 incl. AC-06b/AC-08b; §6 remediation matrix)
- **Canon (v1.3.0 LOD200_LOCKED):** `_aos/work_packages/S003/SFA-S003-P004-WP-CB-0/LOD200_CROP_DATA_MODEL_CANON.md` §15–§20 + §16a
- **L-GATE_S verdict:** `_COMMUNICATION/team_190/SFA-S003-P004/WP-CB-MIG2/WP-CB-MIG2_LGATE-S_VERDICT_v1.0.0.md`
- **Build report:** `_COMMUNICATION/TEAM_10/SFA-S003-P004-WP-CB-MIG2/BUILD_REPORT_v1.0.0.md`
- **QA report:** `_COMMUNICATION/TEAM_50/SFA-S003-P004-WP-CB-MIG2/QA_REPORT_v1.0.0.md`
- **Key commits:** builder `f4bee60`; team_100 integration `dded7b1`; Canon lock + roadmap L-GATE_B; QA correctives `c083cc3`.

## 3. Constitutional checks (all must PASS)
```bash
# C1 — Canon amendment additive (locked v1.2.0 body §1–§14 untouched)
git diff 8795b8a..HEAD -- _aos/work_packages/S003/SFA-S003-P004-WP-CB-0/LOD200_CROP_DATA_MODEL_CANON.md
#   PASS iff all hunks are below the v1.2.0 closing line (additive §15–§20 + §16a only).

# C2 — IR#4: builder commit made NO roadmap edit
git show f4bee60 -- _aos/roadmap.yaml | wc -l        # expect 0

# C3 — Only DDL is migration 060 (nullable seeder_settings); no other new table/column
sed -n '1,60p' organic_market_agent/db/versions/060_seeder_settings.py
ls organic_market_agent/db/versions/ | tail -3       # head is 060

# C4 — Locked reconciliation engine untouched
git diff 8795b8a..HEAD -- organic_market_agent/crop_book/importer/enrichment_runner.py | wc -l   # 0
git diff 8795b8a..HEAD -- organic_market_agent/crop_book/importer/reconciler.py | wc -l          # 0
```

## 4. Layer-ownership / no-duplicate-storage (the D2 guard)
```bash
# sale_unit + seeder_model are ALIASES only — no independent storage / no resolver entry
grep -n "sale_unit\|seeder_model" organic_market_agent/crop_book/canon/field_registry.py
grep -n "sale_unit" organic_market_agent/crop_book/importer/attribute_resolver.py   # expect NONE
python3 -c "from organic_market_agent.crop_book.canon.field_registry import get_canonical as g; print(g('sale_unit'), g('seeder_model'))"
#   expect: harvest_unit seeder

# planting_season REMOVED from FIELD_POLICY (T2/attribute, not a T1 enrichment fact)
grep -n "planting_season" organic_market_agent/crop_book/field_policy.py   # only the comment, no policy key
```

## 5. AC fidelity — verify each independently (LOD400 §2, 17 ACs)
- **AC-01 / 060:** `python3 -m pytest tests/crop_book/test_mig2_migration.py -q` (up+down, 5 tests). `seeder_settings` column added/dropped.
- **AC-02 (CROP_TOPICS↔PHP parity):** `python3 -m pytest tests/crop_book/test_crop_topics.py::TestCropTopics::test_php_parity -q` — must **RUN and PASS** (team_50 caught + team_100 fixed a dead-skip here; confirm it is no longer skipped and the regex matches exactly the 13 `$topics` entries, ordered).
- **AC-03 enums:** `test_mig2_enums.py` — closed-enum rejection (`irrigation_type/root_depth_class/needs_summer_shade`) + open-vocab normalization (`common_pests/foliar_feeding_program/unit_size`).
- **AC-04/AC-05 resolver:** `test_mig2_attribute_resolver.py` — 6 new attrs in `_SOURCE_VALUES_ATTRS`; `sale_unit` has NO entry.
- **AC-06/AC-06b units+policy:** `test_mig2_units.py` + `test_field_policy.py` — new T1 policies; `UNIT_REGISTRY['labor_rate']=='units_per_hr'`; every new T1 unit ∈ registry.
- **AC-07 renames+removal:** 3 keys renamed; `planting_season` absent (above).
- **AC-08/AC-08b delivery:** `_AGRONOMY_FIELD_WHITELIST` has the 5 new T1; `_CATEGORICAL_ATTRS_WHITELIST` drives the per-variety `agronomy` payload for the 6 new attrs (mirrors `planting_method`). Inspect `sfa_ingest_push.py` `_fetch_crop_varieties`.
- **AC-17 field_registry:** `test_mig2_field_registry.py` (15 tests) — every §16 field registered with type/layer/disposition/unit.
- **AC-09/AC-10 UI:** `php -l` on `FieldRegistry.php`, `CropBookViewController.php`, `book_crop.php` (clean). 7 newly-wired fields in `isProposed()`+`LABELS`; controller provisions PROPOSED; מזיקים topic renders `crop_knowledge_notes`.
- **AC-11 PR backfill:** read the `load_masterclass_sheets.py` MIG2 additions — emits ONLY PR-parseable groups + `season_window` (PR class, idempotent); does NOT fabricate `labor_rate_*`/`plantings_per_season`/`needs_summer_shade`/`unit_size`.
- **AC-12/AC-13 console + NI importer:** inspect `scripts/build_crop_gap_console.py` (self-contained HTML, per-gap records, best-effort defaults, confirm/edit/skip, clipboard-JSON + download) and `scripts/ingest_nimrod_validation.py` (NI class `NI:nimrod_validation`, idempotent, dry-run, re-resolve).

## 6. Tests + validate (AC-14)
```bash
python3 -m pytest tests/crop_book/ -q
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
```
PASS iff pytest = **720 passed / 1 skipped / 2 pre-existing failures** (`test_uc_prefix_requires_moderation`, `test_ni_publisher_isolation::test_ac21b_publisher_dir_clean` — both predate this WP) / **0 new**; validate_aos **0 FAIL**.

## 7. Known gaps / deviations — report as NOTEs, not defects (carried from QA)
- **N-1 (QA C-2):** NI importer `dry_run=False` DB-write + re-resolve path is structurally correct but only dry-run-tested (live-DB e2e pending the operational cycle).
- **N-2:** `seeder_settings` ORM uses `deferred()` so live PG does not `UndefinedColumn` before 060 is applied; intended to be removed after the live migration runs.
- **N-3 (data application):** §1 boundary — live 060 apply + PR backfill + console NI cycle are post-gate operational steps owned by team_00/team_99; the new fields are legitimately "מוצע"/empty until then.

## 8. Verdict format → `_COMMUNICATION/team_190/SFA-S003-P004/WP-CB-MIG2/WP-CB-MIG2_LGATE-V_VERDICT_v1.0.0.md`
```yaml
wp: SFA-S003-P004-WP-CB-MIG2
gate: L-GATE_V
validator_engine: <non-Claude>
result: PASS | PASS_WITH_FINDINGS | FAIL
constitutional_checks: <n/4>
ac_checks: <n/17>
findings:
  - id: F-190-MIG2-V-NN
    severity: BLOCKER | MAJOR | MINOR | INFO
    summary: ...
    evidence: ...
notes: [N-1 NI write path, N-2 deferred(), N-3 data-application boundary]
summary: <one paragraph>
```
- **PASS / PASS_WITH_FINDINGS** → team_100 advances WP-CB-MIG2 to **LOD500_LOCKED**; ADR042 archive mandate → team_191; the live data-application cycle (060 apply + backfill + console) proceeds operationally.
- **FAIL/BLOCKER** → team_100 remediates and routes R2.

Notify via `_COMMUNICATION/team_100/` (MSG, ADR043 naming).

---
*Self-contained L-GATE_V package for non-Claude execution. team_00: route to a non-Claude validator. Validate code/migration/spec fidelity per §1 — live-DB data application is an explicit post-gate operational step.*
