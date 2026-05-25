---
id: MANDATE_SFA-S003-P002-WP-B2_L-GATE_S_v1.0.1
from: team_110 (AOS Domain Architect — ADR045 execution_authority: full)
to: team_190 (Constitutional Validator — non-Claude per Iron Rule #1)
date: 2026-05-25
type: RESUBMISSION
gate: L-GATE_S
wp: SFA-S003-P002-WP-B2
project: smallfarmsagents
status: ACTIVE
verdict: PENDING
engine_constraint: "Iron Rule #1 — validator engine MUST differ from team_110 (Claude Opus 4.7). Canonical non-Claude: GPT-5.5."
authorization_basis: "ADR045 R2 #2."
spec_under_review: _aos/work_packages/S003/SFA-S003-P002-WP-B2/LOD400_spec.md
spec_version: v1.1.0
spec_commit: TBD   # this commit
resubmission_round: 2
supersedes: MANDATE_SFA-S003-P002-WP-B2_L-GATE_S_v1.0.0
prior_verdict: _COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B2/LOD400-VERDICT_v1.0.0.md
team_00_decision_ref: _COMMUNICATION/team_00/DECISION_WP-B-OPEN-QUESTIONS_2026-05-25_v1.0.0.md
---

# L-GATE_S Mandate (R2) — SFA-S003-P002-WP-B2

Supersedes `MANDATE_..._v1.0.0`. Validate LOD400 **v1.1.0** — substantial remediation of all 4 R1 findings + 2 team_00-authorized scope changes.

---

## 1. Resolved Findings from R1

| # | Prior Finding | Sev. | Fix Applied in v1.1.0 |
|---|---|------|------------------------|
| F-S-B2-01 | LOD400 referenced non-existent `NiSourceBase` class; actual WP-A class is `NIImporter`. | BLOCKER | §6/§7/§14/§15: all references corrected to `NIImporter`. Subclasses now extend the correct base. Subclass attribute is `name` (per WP-A docstring) rather than the invented `source_label`/`cache_dir`. `load()` returns variety-source-value rows per the actual WP-A contract; the B2-specific `crop_knowledge_notes` path uses a sibling method `load_knowledge_notes()`. §7.1 + §7.2 spell out the full pattern. |
| F-S-B2-02 | §2.2 vs §15 inconsistent on `ni_importer.py` modifiability; `_aos/governance/` + `_aos/lean-kit/` missing from explicit DO NOT TOUCH list. | MAJOR | §2.2 LOD500_LOCKED table now explicitly lists `_aos/governance/`, `_aos/lean-kit/`, `_aos/project_identity.yaml`. §2.3 NEW section formalizes the MODIFY scope: `ni_importer.py` allows APPEND-ONLY of a single helper function (no class change). AC-20 NEW enforces governance/lean-kit cleanliness. |
| F-S-B2-03 | §8 call-site used hallucinated `_upsert_source_value(session, **row["payload"])`; actual signature is `_upsert_source_value(session, variety_id, sv)`. | MAJOR | §8 rewritten to use the EXACT existing signature. Spec explicitly references `seed.py:169-180` as the source-of-truth. Two new resolver helpers in seed.py (`_resolve_default_variety_for_jmf_crop`, `_resolve_crop_id_for_jmf_crop`) bridge the JMF crop name → variety_id / crop_id translation. AC-12a + AC-12b updated accordingly. |
| F-S-B2-04 | Profile drift in validate_aos.sh (28/20 vs mandated 29/18). | MINOR | AC-18 rephrased as "exit code 0 (`0 FAIL`)" with explicit acknowledgment of lean-kit profile drift (28/20, 29/18, 29/19 all valid). Gate-relevant criterion is 0 FAIL only. |

---

## 2. Scope changes per team_00 DECISION (2026-05-25)

The DECISION file `_COMMUNICATION/team_00/DECISION_WP-B-OPEN-QUESTIONS_2026-05-25_v1.0.0.md` formally authorizes these v1.1.0 architectural changes:

### Q1: Text-file input architecture

`extraction_runner.py` reads **text files** (provided by team_00 at `data/jmf/raw_text/<source>/<crop>.txt`), NOT raw PDFs. The pdftotext step is eliminated. Risk register R-01 (pdftotext install) is OBSOLETE.

### Q5: Scope expansion 3 → 6 JMF sources

All JMF MasterClass PDF sources are now in scope:
1. `jmf_book` (240pp main edition) — already in scope
2. **`jmf_book_alt` (209pp alternate edition)** — Q5 ADDITION
3. `jmf_ft_flameweed` — already in scope
4. `jmf_ft_biopesticide` — already in scope
5. **`jmf_ft_phytoprotection`** — Q5 ADDITION
6. **`jmf_ft_nurseryseeding`** — Q5 ADDITION

3 new `note_type` enum values added: `phytoprotection_substance`, `phytoprotection_application`, `nursery_seeding_process`. Total: 13 values.

---

## 3. Validation criteria

Re-run all 20 VCs from `MANDATE_..._v1.0.0.md` §3. Additional R2-specific evidence checks:

- **VC-6.R2** — `NIImporter` correctness probe:
  ```bash
  python3 -c "
  from organic_market_agent.crop_book.importer.ni_importer import NIImporter
  import inspect
  print('NIImporter is abstract:', inspect.isabstract(NIImporter))
  print('No NiSourceBase in spec:',
    'NiSourceBase' not in open('_aos/work_packages/S003/SFA-S003-P002-WP-B2/LOD400_spec.md').read())
  "
  ```
  Expected: `NIImporter is abstract: True` and `No NiSourceBase in spec: True`.

- **VC-5.R2** — LOD500_LOCKED scope explicit:
  ```bash
  grep -c "_aos/governance/" _aos/work_packages/S003/SFA-S003-P002-WP-B2/LOD400_spec.md
  grep -c "_aos/lean-kit/" _aos/work_packages/S003/SFA-S003-P002-WP-B2/LOD400_spec.md
  ```
  Expected: ≥1 each (both explicitly listed in §2.2 DO NOT TOUCH table).

- **VC-3.R2** — `_upsert_source_value` signature correctness:
  ```bash
  grep -n "_upsert_source_value(session, variety_id" _aos/work_packages/S003/SFA-S003-P002-WP-B2/LOD400_spec.md
  grep -n "_upsert_source_value(session, \*\*row\[" _aos/work_packages/S003/SFA-S003-P002-WP-B2/LOD400_spec.md
  ```
  Expected: first ≥1 hit; second = 0 hits (no hallucinated signature remains).

- **VC-Q5** — Q5 scope expansion verified:
  ```bash
  grep -c "jmf_book_alt\|jmf_ft_phytoprotection\|jmf_ft_nurseryseeding" _aos/work_packages/S003/SFA-S003-P002-WP-B2/LOD400_spec.md
  ```
  Expected: ≥20 hits (3 new source identifiers referenced throughout §2/§3/§6/§7/§10/§15).

- **VC-Q1** — Q1 text-file input verified:
  ```bash
  grep -n "data/jmf/raw_text" _aos/work_packages/S003/SFA-S003-P002-WP-B2/LOD400_spec.md
  ```
  Expected: ≥10 hits documenting the text-file input architecture.

Independence rule: do NOT read the R1 verdict before forming R2 conclusions. The R1 verdict is referenced in §1 of this mandate ONLY as fix-traceability evidence.

---

## 4. Output Format

Write verdict to: **`_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B2/LOD400-VERDICT_v1.0.1.md`**

Commit with:
```
gate(WP-B2/L-GATE_S): team_190 R2 verdict — <RESULT>
Co-Authored-By: GPT-5.5 <noreply@anthropic.com>
```

Decision criteria:
- **PASS / PASS_WITH_FINDINGS (0 blockers)** → team_110 proceeds to Phase 4 (B2 roadmap transition) + Phase 5 (B2 L-GATE_B mandate to builder)
- **FAIL (≥1 blocker)** → team_110 remediates + R3

---

## 5. Authorization basis

ADR045 R2 #2. Mandate root `_COMMUNICATION/TEAM_110/SFA-S003-P002-WP-B/EXECUTION_MANDATE_v1.0.0.md`. Q1 + Q5 scope changes pre-authorized via team_00 DECISION file (cited in §2). team_100 NOT in routing chain.

---

*R2 resubmission mandate issued 2026-05-25 by team_110 (Claude Opus 4.7).*
*Validator: team_190 (non-Claude). Independence rule applies.*
*Awaiting verdict at `_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B2/LOD400-VERDICT_v1.0.1.md`.*
