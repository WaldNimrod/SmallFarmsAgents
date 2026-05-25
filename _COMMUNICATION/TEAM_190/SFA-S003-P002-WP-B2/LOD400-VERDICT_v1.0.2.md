---
id: LOD400_VERDICT_SFA-S003-P002-WP-B2_v1.0.2
from: team_190
to: team_110
date: 2026-05-25
gate: L-GATE_S
wp: SFA-S003-P002-WP-B2
spec_under_review: _aos/work_packages/S003/SFA-S003-P002-WP-B2/LOD400_spec.md
spec_version: v1.1.1
resubmission_round: 3
engine: GPT-5.5
result: FAIL
blockers: 2
major: 0
minor: 1
---

# LOD400 Verdict v1.0.2 — SFA-S003-P002-WP-B2

## 1. Executive Verdict

**Result: FAIL.**

R3 surface remediation is partially successful: the obsolete class-name token is absent, the direct B2 bypass rationale exists in §7.1 / §8, and the operative licensing invariant plus AC-21 are now present.

However, LOD400 v1.1.1 still contains two BLOCKER-level internal contradictions in operative build and acceptance content. A builder cannot satisfy both sides of the spec without choosing which authoritative section to ignore.

## 2. Mandate Compliance

- Engine constraint: **PASS** — validator is GPT-5.5, non-Claude.
- Independence: **PASS** — R2 verdict file was not read before forming this R3 verdict.
- Scope: **PASS** — reviewed `_aos/work_packages/S003/SFA-S003-P002-WP-B2/LOD400_spec.md` v1.1.1 against the R3 mandate and original 20 VCs.
- Output path: **PASS** — verdict written to `_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B2/LOD400-VERDICT_v1.0.2.md`.

## 3. R3 Evidence Probes

Mandate §3 probes were run with equivalent text checks:

| Probe | Result | Evidence |
|---|---:|---|
| B1 stale token absent | PASS | `No NiSourceBase in spec: True` |
| B2 bypass language present | PASS | Hits for `NOT registered with ni_registry`, `B2 bypasses ni_registry.load_all()`, and `B2 does NOT call ni_registry.register` |
| B3 operative licensing present | PASS | §3.1 header, `OPERATIVE LICENSING INVARIANT`, AC-21a/b/c present |
| Cumulative counts | PASS | `NIImporter=18`, `data/jmf/raw_text=13`, Q5 identifiers `=54` |

Executable context checks:

| Check | Result |
|---|---|
| `NIImporter` API exists and is abstract | PASS |
| `NIImporter.load` signature | `(self) -> list[dict[str, Any]]` |
| Initial `ni_registry.registered_labels` | `[]` |
| `JMF_CROP_MAP` size | `86` |
| Migration 043-045 inventory | `043`, `044` only; no existing `045` |
| Roadmap WP-B2 state | `ELIGIBLE / LOD200_LOCKED / L-GATE_E` |
| `validate_aos.sh .` | `29 PASS / 19 SKIP / 0 FAIL` |

## 4. Findings

### BLOCKER B1 — B2 bypass fix is contradicted by remaining registry/load_all requirements

**VCs affected:** VC-15, VC-17, VC-18, VC-19  
**Spec locations:** §2.1, §7 intro, §7.1, §8, AC-03

v1.1.1 correctly adds a B2-specific bypass path:

- §7.1 says B2 does **not** use `ni_registry.load_all()`.
- §7.1 says B2 subclasses are **not** registered with `ni_registry`.
- §8 shows seed.py iterating `NI_IMPORTER_CLASSES` directly and passing `session` into `load(session)` / `load_knowledge_notes(session)`.

But operative content still requires the opposite:

- §2.1 describes `ni/__init__.py` as "re-export 6 subclasses + register on import".
- §7 intro says seed.py invokes `ni_registry.load_all()` and iterates `ni_registry.registered_labels`.
- AC-03 requires `ni_registry.registered_labels` to contain all 6 B2 importer labels after import.

This is not cosmetic. If the builder follows AC-03, the importers must register with `ni_registry` and the R2 architectural failure path is reintroduced or AC-03 becomes the wrong test. If the builder follows §7.1/§8, AC-03 necessarily fails. The acceptance suite is therefore not objectively satisfiable.

### BLOCKER B2 — seed.py modification scope is internally inconsistent

**VCs affected:** VC-5, VC-18, AC-19  
**Spec locations:** §2.3, §8, AC-19, Build Step 8, §15

v1.1.1’s intended fix places resolution logic in the subclasses and keeps seed.py limited:

- §2.3 permits seed.py changes only for 2 CLI flags plus 1 call-site block.
- §8 says "No additional helper functions are added to seed.py" and resolution lives in subclasses.

But later operative acceptance/build content still requires helper additions:

- AC-19 says seed.py diff must show "2 CLI flag additions + 1 call-site block + 2 helper function additions".
- Build Step 8 instructs the builder to add `_resolve_default_variety_for_jmf_crop` and `_resolve_crop_id_for_jmf_crop` helpers.
- §15 MODIFY summary also lists seed.py as "+2 CLI flags + 1 call-site block + 2 helper functions".

This breaks the LOD500_LOCKED guard and diff-audit contract. A builder cannot both avoid seed.py helper functions and satisfy AC-19 / Step 8 / §15.

### MINOR M1 — stale metadata and version text remain

**VC affected:** VC-18  
**Spec locations:** frontmatter, title, section labels

The spec frontmatter still says `status: PRE_LOD400_LOCK — awaiting team_190 L-GATE_S R2 verdict`, the H1 title still says v1.1.0, and several section labels/docstrings still cite v1.1.0 after the v1.1.1 patch. This is not independently blocking, but it increases review ambiguity and should be cleaned in R4.

## 5. VC Summary

| VC | Status | Notes |
|---:|---|---|
| 1 | PASS | Cross-engine roles present; validator non-Claude. |
| 2 | PASS | No instruction to mutate `_aos/roadmap.yaml`. |
| 3 | PASS | BUILD_REPORT path remains under `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B2/`. |
| 4 | PASS | `_aos/governance/` and `_aos/lean-kit/` listed untouchable. |
| 5 | FAIL | seed.py modify scope contradiction in §2.3 / §8 vs AC-19 / Step 8 / §15. |
| 6 | PASS | `ni_importer.py` append-only `_upsert_knowledge_note`; obsolete class token absent. |
| 7 | PASS | Migration 045 / down_revision 044 specified; no current 045 file exists. |
| 8 | PASS | SQLite/Postgres-compatible PK and CHECK patterns specified. |
| 9 | PASS | Q5-expanded 13 note types consistently specified in migration/ORM sections. |
| 10 | PASS | `length(body_text) <= 2000` specified and tested. |
| 11 | PASS | Internal-only flag and helper hardcoding specified. |
| 12 | PASS | Cache schema keys and validation AC present. |
| 13 | PASS | Cache commit policy and `.gitattributes` rule present. |
| 14 | PASS | Extraction runner remains script/manual path, not runtime path. |
| 15 | FAIL | Engine reuse path contradicted by remaining `ni_registry.load_all()` / registration acceptance content. |
| 16 | PASS | Operative §3.1 and AC-21 now ban publisher/public-display paths. |
| 17 | FAIL | WP-A dependency handling is still internally inconsistent around registry bypass. |
| 18 | FAIL | Acceptance criteria are not objectively satisfiable due AC-03 and AC-19 contradictions. |
| 19 | FAIL | Test/AC plan still requires mutually exclusive registry and seed.py-helper behavior. |
| 20 | PASS | AOS validation 0 FAIL; roadmap parse succeeded. |

## 6. Required R4 Remediation

1. Rewrite §7 intro, §2.1 `ni/__init__.py` description, AC-03, and any test requirements so B2 consistently uses `NI_IMPORTER_CLASSES` direct iteration and explicitly asserts that B2 importers are **not** registered with `ni_registry`.
2. Rewrite AC-19, Build Step 8, and §15 MODIFY summary so seed.py scope consistently allows only 2 CLI flags plus the NI call-site block, with crop/variety resolution helpers living in subclasses.
3. Clean stale v1.1.0 / R2 status text in frontmatter, H1, docstrings, and section labels.

## 7. Decision

Because there are 2 BLOCKER findings, L-GATE_S R3 does **not** pass.

**Decision:** `FAIL` — team_110 must remediate and resubmit for R4.
