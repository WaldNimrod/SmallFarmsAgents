---
id: VERDICT_SFA-S003-P002-WP-B2_L-GATE_S_v1.0.0
from: Team 190 (Constitutional Validator)
to: Team 110
type: CONSTITUTIONAL_VERDICT
work_package: SFA-S003-P002-WP-B2
gate: L-GATE_S
date: 2026-05-25
engine: GPT-5.5
enforcement: regular
verdict: FAIL
criteria_total: 20
criteria_pass: 17
criteria_fail: 3
findings_blocker: 1
findings_major: 2
findings_minor: 1
resubmission_round: 1
correction_cycle: R1
mandate: MANDATE_SFA-S003-P002-WP-B2_L-GATE_S_v1.0.0
spec_under_review: _aos/work_packages/S003/SFA-S003-P002-WP-B2/LOD400_spec.md
spec_version: v1.0.0
phase_owner: team_190
---

# L-GATE_S Verdict — SFA-S003-P002-WP-B2 — R1

## 1. Verdict Summary

**FAIL** — LOD400 v1.0.0 is not fit for spec lock.

The licensing controls, cache governance, migration chain, extraction-runner placement, and test strategy are mostly sound. The blocker is narrower but material: the spec repeatedly instructs B2 to subclass/import `NiSourceBase`, and the mandate's required verification command fails because the committed WP-A skeleton exports `NIImporter`, not `NiSourceBase`. A literal builder would create non-importable B2 modules and cannot satisfy AC-03 / AC-18 as written.

Decision: **1 BLOCKER / 2 MAJOR / 1 MINOR**. team_110 should remediate and resubmit L-GATE_S R2.

## 2. Command Evidence

### Command 1 — AOS validation

```bash
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
```

Result:

```text
RESULT: 28 PASS / 20 SKIP / 0 FAIL
L-GATE_BUILD EXIT CRITERION: SATISFIED
```

### Command 2 — Roadmap parse

```bash
python3 -c "import yaml; d=yaml.safe_load(open('_aos/roadmap.yaml')); wp=[w for w in d['work_packages'] if w['id']=='SFA-S003-P002-WP-B2'][0]; print(wp['id'], wp['status'], wp['lod_status'], wp['current_lean_gate']); print(wp.get('gate_history'))"
```

Result:

```text
SFA-S003-P002-WP-B2 ELIGIBLE LOD200_LOCKED L-GATE_E
[{'gate': 'L-GATE_E', 'result': 'PASS', 'date': '2026-05-24', ... 'validator': 'team_00'}]
```

### Command 3 — Mandated WP-A `NiSourceBase` signature check

```bash
python3 -c "from organic_market_agent.crop_book.importer.ni_importer import NiSourceBase; import inspect; print('NiSourceBase is abstract:', inspect.isabstract(NiSourceBase)); print('load method present:', hasattr(NiSourceBase, 'load'))"
```

Result:

```text
ImportError: cannot import name 'NiSourceBase' from 'organic_market_agent.crop_book.importer.ni_importer'
```

Supplemental check against the actual committed WP-A class:

```bash
python3 -c "from organic_market_agent.crop_book.importer.ni_importer import NIImporter; import inspect; print('NIImporter is abstract:', inspect.isabstract(NIImporter)); print('load method present:', hasattr(NIImporter, 'load'))"
```

```text
NIImporter is abstract: True
load method present: True
```

### Command 4 — JMF map coverage

```bash
python3 -c "from organic_market_agent.crop_book.constants import JMF_CROP_MAP; print(f'entries={len(JMF_CROP_MAP)}')"
```

Result:

```text
entries=86
```

### Command 5 — Migration head verification

```bash
ls organic_market_agent/db/versions/ | grep -E '^04[3-5]_' | sort
```

Result:

```text
043_backfill_source_values_trust.py
044_crop_task_templates.py
```

### Supplemental package hygiene

```bash
python3 /Users/nimrod/.codex/skills/constitutional-package-linter/scripts/lint_constitutional_package.py _COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B2/MANDATE_L-GATE_S_v1.0.0.md _aos/work_packages/S003/SFA-S003-P002-WP-B2/LOD400_spec.md
```

Result:

```text
PASS
```

## 3. VC Matrix

| VC | Criterion | Result | Evidence |
|---|---|---|---|
| VC-1 | IR#1 cross-engine | PASS | LOD400 frontmatter sets `builder: sfa_build` and `validator: team_190 (non-Claude)`; current validator engine is GPT-5.5. |
| VC-2 | IR#4 single-writer roadmap | PASS | §15 deliverables do not include `_aos/roadmap.yaml`; lifecycle transition remains outside builder scope. |
| VC-3 | IR#6 `_COMMUNICATION/` routing | PASS | §15 lists `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B2/BUILD_REPORT_v1.0.0.md`. |
| VC-4 | IR#11 governance untouched | FAIL | §2.2 does not explicitly list `_aos/governance/` or `_aos/lean-kit/` as untouchable, contrary to the mandate. |
| VC-5 | LOD500_LOCKED guard | PASS_WITH_FINDING | Locked inventory and §15 MODIFY list are mostly complete; see F-S-B2-02 for the §2.2 / §15 contradiction around `ni_importer.py`. |
| VC-6 | `ni_importer.py` append-only scope | FAIL | The append-only intent is present, but it is tied to a non-existent `NiSourceBase` class; AC-18 cannot be executed as written. |
| VC-7 | Migration chain integrity | PASS | Spec declares `revision = "045"`, `down_revision = "044"`; repository has 043 and 044 only, no 045. |
| VC-8 | SQLite + Postgres compatibility | PASS | DDL uses `BigInteger().with_variant(Integer(), "sqlite")`; `length(body_text)` and `note_type IN (...)` are portable. |
| VC-9 | `note_type` CHECK scope | PASS | Migration/ORM enum lists exactly 10 values: 8 ebook values plus 2 FT values. |
| VC-10 | Body-text DB length CHECK | PASS | §3 defines `length(body_text) <= 2000`; §4 defines `BODY_TEXT_MAX_LENGTH = 2000`; AC-04a tests DB-level `IntegrityError`. |
| VC-11 | Licensing flag schema-level | PASS | §3 declares `is_internal_farm_use_only BOOLEAN NOT NULL DEFAULT TRUE`; §4 mirrors; cache schema omits the field. |
| VC-12 | JSON cache schema completeness | PASS | §5 requires `schema_version`, `source`, `crop_jmf_en`, provenance fields, and note keys; AC-08 rejects missing/bad schema. |
| VC-13 | Cache commit policy | PASS | §5 / §11 / §12 commit the cache path and `.gitattributes`; Step 10 correctly limits builder output to fixtures and `.gitkeep` placeholders before team_00 real extraction. |
| VC-14 | Extraction runner not production path | PASS | §6 places runner at `scripts/extract_jmf_ni.py`; §11 says no live API calls during build and runtime reads JSON only. |
| VC-15 | `cultivar_recommendation` engine reuse | PASS_WITH_FINDING | §7.2 and AC-12 require both `crop_knowledge_notes` and `crop_variety_source_values` rows through `_upsert_source_value`; see F-S-B2-03 for call-site signature clarification. |
| VC-16 | PDF licensing advisory #1 | PASS | §12 forbids WordPress/public publication, bounds snippets at DB level, and carries PDF/page provenance. |
| VC-17 | Transitive WP-A dependency | FAIL | LOD200/LOD400 name `ni_importer.py::NiSourceBase`, but the committed WP-A file defines `NIImporter`; mandated import command fails. |
| VC-18 | AC measurability | PASS | AC-01..AC-18 are objective assertions, command checks, `IntegrityError` tests, and count checks. |
| VC-19 | Test coverage adequacy | PASS | §10 lists 15 tests across 9 files plus four fixture JSON files; all tests use SQLite/fixtures and no live Anthropic calls. |
| VC-20 | `validate_aos.sh` + YAML integrity | PASS_WITH_FINDING | Roadmap parse matches `ELIGIBLE / LOD200_LOCKED / L-GATE_E` with L-GATE_E PASS; `validate_aos.sh` has 0 FAIL but current lean-kit profile is `28 PASS / 20 SKIP`, not the mandate's `29 PASS / 18 SKIP`. |

## 4. Findings

| finding_id | severity | result | evidence_by_path | route_recommendation |
|---|---|---|---|---|
| F-S-B2-01 | BLOCKER | LOD400 subclasses a non-existent WP-A base class. The spec says `ni_importer.py` is the `NiSourceBase` abstract class, imports `NiSourceBase`, subclasses it in `JmfBookSource`, and tells the builder not to modify the `NiSourceBase` class. The committed file defines `NIImporter`; `from ...ni_importer import NiSourceBase` fails. | `_aos/work_packages/S003/SFA-S003-P002-WP-B2/LOD400_spec.md:23`, `:425-448`, `:512`, `:649`, `organic_market_agent/crop_book/importer/ni_importer.py:35`, command evidence §2.3 | Resubmit LOD400 using the as-built WP-A API: replace `NiSourceBase` with `NIImporter` throughout B2 LOD200/LOD400/mandate checks, or explicitly authorize a separate WP-A remediation that adds a compatibility alias. The cleanest route is spec correction only: subclass `NIImporter` and preserve the base class unchanged. |
| F-S-B2-02 | MAJOR | Scope text is internally inconsistent and misses mandated governance untouchables. §2.2 marks `ni_importer.py` as `DO NOT MODIFY` and the local "Permitted modifications" list omits it, while §7.5 / §15 later permit exactly one appended helper. §2.2 also does not explicitly list `_aos/governance/` and `_aos/lean-kit/` as untouchable. | `_aos/work_packages/S003/SFA-S003-P002-WP-B2/LOD400_spec.md:96-112`, `:491-512`, `:741-746` | In R2, make §2.2 and §15 agree: `ni_importer.py` is locked except for one module-level appended `_upsert_knowledge_note` helper. Add explicit `_aos/governance/` and `_aos/lean-kit/` DO NOT TOUCH rows. |
| F-S-B2-03 | MAJOR | The seed call-site snippet calls `_upsert_source_value(session, **row["payload"])`, but the existing seed helper signature is `_upsert_source_value(session, variety_id, sv)`. The AC correctly requires engine reuse, but the builder-facing payload contract is under-specified and likely to produce a TypeError if copied literally with field-level payload keys. | `_aos/work_packages/S003/SFA-S003-P002-WP-B2/LOD400_spec.md:541-548`, `organic_market_agent/crop_book/importer/seed.py:169-180` | Specify the exact `crop_variety_source_values` row payload shape, e.g. `{"variety_id": default_variety_id, "sv": {... field_name/source/trust_tier/confidence_weight ...}}`, or provide a small adapter function in the allowed `seed.py` scope. Keep AC-12 intact. |
| F-S-B2-04 | MINOR | The mandate expected `validate_aos.sh` profile `29 PASS / 18 SKIP / 0 FAIL`; current run is `28 PASS / 20 SKIP / 0 FAIL`. This does not block because the gate-relevant criterion is 0 FAIL and the lean-kit profile has drifted to 47 checks. | command evidence §2.1 | Update R2 expected profile or phrase VC-20 as `0 FAIL` with observed PASS/SKIP totals recorded. |

## 5. Advisory Disposition

Advisory #1 (PDF licensing) is adequately handled in the spec: DB-level `body_text <= 2000`, `is_internal_farm_use_only=True`, provenance PDF/page fields, and explicit prohibition on public WordPress display.

Advisory #2 (cache strategy) is adequately handled: the cache is committed with `.gitattributes`, while the builder commits only fixtures and empty cache directories until team_00 performs real extraction post-merge.

Advisory #4 (transitive WP-A dependency) is not adequately handled because the named base class does not match the committed WP-A API.

## 6. Required R2 Remediation

1. Replace `NiSourceBase` references with the actual WP-A `NIImporter` API, or route an explicit WP-A compatibility-alias remediation before B2 proceeds.
2. Make the LOD500_LOCKED / permitted-modification sections internally consistent and add the explicit `_aos/governance/` / `_aos/lean-kit/` untouchable rows.
3. Clarify the `_upsert_source_value` payload/call contract for `cultivar_recommendation`.
4. Refresh the command-evidence expectations for `validate_aos.sh` to match current 0-FAIL profile language.

## 7. Final Decision

Final decision: **FAIL**.

team_110 should remediate LOD400 v1.0.0 and resubmit L-GATE_S R2. team_110 should not proceed to roadmap transition or L-GATE_B builder dispatch for WP-B2 until the base-class blocker is resolved.
