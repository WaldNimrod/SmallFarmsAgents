---
id: MANDATE_SFA-S003-P002-WP-B1_L-GATE_S_v1.0.0
from: team_110 (AOS Domain Architect — executing under ADR045 EXECUTION_MANDATE)
to: team_190 (Validator — non-Claude per Iron Rule #1)
date: 2026-05-24
type: GATE_MANDATE
gate: L-GATE_S
wp: SFA-S003-P002-WP-B1
project: smallfarmsagents
status: ACTIVE
verdict: PENDING
engine_constraint: "Iron Rule #1 — validator engine MUST differ from team_110 (Claude Opus 4.7). Use any non-Claude engine (current canonical: GPT-5.5)."
authorization_basis: "ADR045 R2 #2 — team_110 may issue mandates to team_190 directly during execution_authority: full mandate. Mandate basis: SFA-S003-P002-WP-B EXECUTION_MANDATE_v1.0.0 (commit 7c3d7d6 R3 PASS)."
spec_under_review: _aos/work_packages/S003/SFA-S003-P002-WP-B1/LOD400_spec.md
spec_commit: 91972bc
---

# L-GATE_S Mandate — SFA-S003-P002-WP-B1

**ספר גידולים: JMF Excel Base Layer — Multi-Source Knowledge Foundation**
**Track:** A | **Profile:** L0 | **Effort:** LARGE | **Risk:** MEDIUM

---

## 1. Gate History

| Gate | Result | Date | Validator | Notes |
|------|--------|------|-----------|-------|
| L-GATE_E | PASS | 2026-05-24 | team_00 | Authorized in-session 2026-05-24 (canonical registration grant); IR#4 exception per CLAUDE.md Directory Authority. Commit `f61c1da`. |
| L-GATE_PRE_HANDOFF (R1) | PASS | 2026-05-24 | team_190 (GPT-5.5) | Pre-handoff package validated; 4 advisory items issued for LOD400 authoring. Commit `d70bf11`. Verdict: `_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B/PRE_HANDOFF_VERDICT_v1.0.0.md`. |
| L-GATE_PRE_HANDOFF (R2) | FAIL | 2026-05-24 | team_190 (GPT-5.5) | F-R2-001 BLOCKER: EXECUTION_MANDATE YAML frontmatter issue. Commit `aada99a`. |
| L-GATE_PRE_HANDOFF (R3) | PASS | 2026-05-24 | team_190 (GPT-5.5) | F-R2-001 CLOSED — `execution_authority: full` mandate confirmed for team_110. Commit `7c3d7d6`. |
| L-GATE_S (LOD200 author) | (this mandate ↓) | — | team_190 | LOD200 + LOD400 ready for spec-lock validation. |

---

## 2. Scope

Validate the LOD400 spec for **SFA-S003-P002-WP-B1** (JMF MasterClass Excel
ingestion as PR-tier baseline) as a **spec-only constitutional review**.
You are NOT validating implementation — no builder has been engaged yet.

This is the SPEC-LOCK gate (L-GATE_S). Your job is to determine whether the
LOD400 is complete, internally consistent, governance-compliant, and
precise enough that a junior developer or fresh agent could implement it
without filling gaps.

---

## 3. Validation Criteria

| # | Criterion | What to Check |
|---|-----------|---------------|
| VC-1 | **Iron Rule #1 (cross-engine)** | LOD400 §1/§14 assign builder = `sfa_build` (separate session, non-team_190 engine) and validator = `team_190 (non-Claude)`. Author (team_110) is Claude Opus 4.7 — distinct from team_190. |
| VC-2 | **Iron Rule #4 (single-writer roadmap)** | LOD400 does NOT instruct the builder to modify `_aos/roadmap.yaml`. Only team_110 may transition lifecycle fields (lod_status, status, current_lean_gate) per ADR045 R2 #3. |
| VC-3 | **Iron Rule #6 (artifact communication)** | All inter-team handoffs cited in the spec route through `_COMMUNICATION/<team>/` subdirectories. |
| VC-4 | **Iron Rule #7 (API-only mutations when DB online)** | DB is online per `/Users/nimrod/Documents/agents-os/_aos/db_connectivity_status.json` at 2026-05-24T00:07:36Z. WP-B1 is spoke-native (`SFA-*` format) — per ADR034 R9 it uses `_aos/roadmap.yaml` as file SSoT; no API mutation required. LOD400 must not assert API mutations the builder cannot make. |
| VC-5 | **Iron Rule #11 (governance untouched)** | LOD400 §2.2 lists `_aos/governance/`, `_aos/lean-kit/`, `_aos/project_identity.yaml` as untouchable. No deliverable in §15 writes to those paths. |
| VC-6 | **LOD500_LOCKED guard** | LOD400 §14 enumerates locked files. The "MODIFY" list in §15 contains only: `constants.py` (additive `JMF_CROP_MAP` block), `seed.py` (additive CLI flags + call site), `CHANGELOG.md`. No file in the LOD500_LOCKED inventory appears in the MODIFY list. |
| VC-7 | **Raw-material guard preserved** | `organic_market_agent/crop_book/importer/tend.py` is NOT in §15 MODIFY list (per CLAUDE.md domain rule and PROGRAM_BRIEF §5). |
| VC-8 | **GCR scope** | LOD400 §10 (via LOD200 §10) asserts **no GCR required**. Cross-check: §5 modifies `constants.py` only (append-after-OUTLIER_CROPS), §8 modifies `seed.py` (additive CLI + call), §3 adds a NEW migration 044, §4 adds a NEW ORM module. `models.py` is NOT modified — confirm by reading §14 LOD500_LOCKED inventory. |
| VC-9 | **Migration chain integrity** | LOD400 §3 declares `revision = "044"`, `down_revision = "043"`. The current head is `043_backfill_source_values_trust.py` (confirm by listing `organic_market_agent/db/versions/`). No conflicting migration 044 exists. |
| VC-10 | **SQLite compatibility** | LOD400 §3 uses `BigInteger().with_variant(Integer(), "sqlite")` for PK / FK columns (matches WP-A pattern at `enrichment_models.py:19`). §3 acknowledges `server_default=sa.text("now()")` may need a SQLite branch — this risk is documented in §13 R-04 and tested by AC-01 / AC-16. |
| VC-11 | **CHECK constraint scope discipline** | LOD400 §3 + §4 declare 14 `task_type` enum values (B1 baseline). §3 explicitly states WP-B3 will ALTER the constraint via migration 046 to add B3-specific values (`nursery_seed`, `pest_spray`, `potting_up`, `thinning`). B1 must NOT pre-add B3 values — AC-16 enforces this. |
| VC-12 | **Engine reuse (WP-A SSoT preservation)** | LOD400 §6.10 specifies `_upsert_source_value` writes `trust_tier='PR'`, `confidence_weight=Decimal("0.70")` — matching `SOURCE_REGISTRY["JMF"]` at `source_registry.py` (PR class, weight 0.70). The spec asserts ALL blendable fields flow through `reconcile_field()` via the standard upsert path; nothing bypasses the engine. AC-12 verifies enrichment runner integration; AC-13 verifies EX override regression. |
| VC-13 | **Transitive WP-A dependency (PRE_HANDOFF Advisory #4)** | LOD400 §12 explicitly addresses the advisory by naming the WP-A LOD500_LOCKED commit `594cbc8` and listing the specific WP-A files relied upon (`source_registry.py`, `field_policy.py`, `reconciler.py`, `enrichment_runner.py`, migration 042) in §1, §2.2, §6.10, and AC-13. |
| VC-14 | **Advisory disposition completeness** | LOD400 §12 disposes of all 4 PRE_HANDOFF advisories. Advisories #1, #2, #3 explicitly carry forward to WP-B2 (#1, #2) and WP-B3 (#3); advisory #4 addressed inline in this spec. |
| VC-15 | **LOD400 precision standard** | Spec is buildable without judgement gaps: §3 has complete DDL; §4 has complete ORM; §6.3–§6.7 list every column-name fragment + DB key + unit handling; §7 has worked numerical examples; §8 has line-numbered call site; §9 has 22 testable ACs; §10 lists 25+ tests with file-level allocation; §11 has a 10-step build sequence. A fresh agent can implement Steps 2–10 without re-reading the program brief. |
| VC-16 | **AC measurability** | All 22 ACs in §9 are objectively verifiable (commands, counts, or `IntegrityError` assertions). No "the spec should be reasonable" or "the importer should work" wording. |
| VC-17 | **Test coverage adequacy** | 25+ tests across 9 files (§10) cover: parsers (6), mapping (3), conversions (4), DB integration (4), idempotency (2), ORM (2), migration (2), CLI (3), regression (1). Coverage matrix maps every AC to ≥1 test file. |
| VC-18 | **File-deliverables completeness** | §15 lists every new file the spec creates and every existing file it modifies. The lists are exhaustive — no implicit files referenced elsewhere in the spec are missing from §15. |
| VC-19 | **validate_aos.sh clean** | Run `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` from `/Users/nimrod/Documents/SmallFarmsAgents`. Expected: `RESULT: 29 PASS / 17 SKIP / 0 FAIL`. |
| VC-20 | **YAML / artifact integrity** | `python3 -c "import yaml; yaml.safe_load(open('_aos/roadmap.yaml'))"` succeeds. WP-B1 entry in roadmap.yaml has `lod_status: LOD200_LOCKED`, `spec_ref` pointing at the LOD200 file, and an L-GATE_E PASS entry in `gate_history`. |

**Total: 20 criteria.**

---

## 4. Files to Review

### Spec documents (primary inputs)

- **LOD400 (under review):** `_aos/work_packages/S003/SFA-S003-P002-WP-B1/LOD400_spec.md` (commit `91972bc`)
- **LOD200:** `_aos/work_packages/S003/SFA-S003-P002-WP-B1/LOD200_spec.md` (commit `0b79c92`)
- **Program brief:** `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B/PROGRAM_BRIEF_v1.0.0.md`
- **Execution mandate:** `_COMMUNICATION/TEAM_110/SFA-S003-P002-WP-B/EXECUTION_MANDATE_v1.0.0.md`
- **Activation prompt:** `_COMMUNICATION/TEAM_110/SFA-S003-P002-WP-B/ACTIVATION_PROMPT.md`

### Prior verdicts (gate history evidence)

- `_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B/PRE_HANDOFF_VERDICT_v1.0.0.md` (R1 PASS — commit `d70bf11`)
- `_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B/PRE_HANDOFF_VERDICT_R2_v1.0.0.md` (R2 FAIL — commit `aada99a`)
- `_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B/PRE_HANDOFF_VERDICT_R3_v1.0.0.md` (R3 PASS — commit `7c3d7d6`)

### WP-A SSoT files (engine reuse evidence — read-only)

- `_aos/work_packages/S003/SFA-S003-P002-WP-A/LOD400_spec.md` (structural template)
- `organic_market_agent/crop_book/source_registry.py` (must contain `SOURCE_REGISTRY["JMF"]` PR-class, weight 0.70)
- `organic_market_agent/crop_book/field_policy.py`
- `organic_market_agent/crop_book/importer/reconciler.py` (verify `Candidate`, `FieldConsensus`, `reconcile_field()` signatures cited in LOD400 §6 match the actual code)
- `organic_market_agent/crop_book/importer/enrichment_runner.py` (verify `run_enrichment(session, variety_ids=None, dry_run=False)` signature)
- `organic_market_agent/crop_book/models.py` (verify `CropVarietySourceValue` columns cited in §6.10 exist)
- `organic_market_agent/db/versions/043_backfill_source_values_trust.py` (verify `revision = "043"` to confirm 044 chain)

### Governance references

- `_aos/governance/directives/ADR045_TEAM_110_AUTONOMOUS_EXECUTION_v1.0.0.md`
- `_aos/governance/directives/ADR034_*` (R7 IR#7; R8 offline; R9 spoke-native WP exemption)
- `CLAUDE.md` (project-root domain rules; LOD500_LOCKED inventory)

### Roadmap

- `_aos/roadmap.yaml` — confirm WP-B1 entry shows `lod_status: LOD200_LOCKED` after commit `0b79c92`.

---

## 5. Required Commands (run independently)

Execute these from `/Users/nimrod/Documents/SmallFarmsAgents` and quote raw output in your verdict §1 evidence section:

```bash
# 1. AOS validation
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .

# 2. Roadmap parse + WP-B1 lifecycle state
python3 -c "
import yaml
d = yaml.safe_load(open('_aos/roadmap.yaml'))
wp = [w for w in d['work_packages'] if w['id'] == 'SFA-S003-P002-WP-B1'][0]
print(wp['id'], wp['status'], wp['lod_status'], wp.get('spec_ref'))
"

# 3. Migration chain integrity
ls organic_market_agent/db/versions/ | grep -E "^(043|044)_" | sort

# 4. Engine reuse — verify SOURCE_REGISTRY["JMF"] is PR with weight 0.70
python3 -c "
from organic_market_agent.crop_book.source_registry import SOURCE_REGISTRY
spec = SOURCE_REGISTRY['JMF']
print(f'cls={spec.cls!r} weight={spec.weight!r} is_hard_override={spec.is_hard_override}')
"

# 5. LOD500_LOCKED file scan — confirm no spec-mandated changes appear
#    in the locked inventory's git history for the WP-B1 spec commits
git log --name-only 7c3d7d6..91972bc | grep -E "^organic_market_agent/(views|publisher|crop_book/(models|source_registry|field_policy|enrichment_models|importer/(reconciler|enrichment_runner|tend|jmf)))\.py|^mu-plugin|^organic_market_agent/db/versions/0(0[1-9]|[1-3][0-9]|4[0-3])_" \
    | sort -u
# Expected: empty output.

# 6. Cross-engine attestation — author of commits 0b79c92 + 91972bc
git log --format='%h %an %s' 7c3d7d6..91972bc
# Expected: author = team_110 / Claude Opus 4.7 (NOT team_190 engine)
```

---

## 6. Output Format

Write your verdict to:
**`_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1/LOD400-VERDICT_v1.0.0.md`**

Use the unified verdict template (`_aos/lean-kit/modules/validation-quality/templates/VERDICT_TEMPLATE.md`):

1. Verdict Summary (PASS / PASS_WITH_FINDINGS / FAIL)
2. Parameters (engine identity, validation commands run)
3. Criteria Table (one row per VC-1..VC-20 with result + evidence)
4. Findings (BLOCKER / MAJOR / MINOR / ADVISORY; every FAIL cites file:line)
5. `validate_aos.sh` raw output
6. Disposition (what team_110 must do to remediate, if anything)
7. Next Step (commit the verdict; team_110 reads it to decide Phase 4)

### Decision criteria

- **PASS** — all 20 VCs green; team_110 may proceed directly to Phase 4 (roadmap transition to `lod_status: LOD400_LOCKED`, `current_lean_gate: L-GATE_B`).
- **PASS_WITH_FINDINGS (0 blockers)** — proceed to Phase 4; remediation handled inline by builder in BUILD_REPORT (MAJOR/MINOR) or noted as ADVISORY for later WPs.
- **FAIL (≥1 blocker)** — team_110 remediates the LOD400 and resubmits. Bump mandate version (`MANDATE_..._L-GATE_S_v1.0.1.md`).

### Engine constraint

You are constitutional under **Iron Rule #1**: validator engine MUST differ from the author engine. The LOD400 was authored by Claude Opus 4.7 (team_110). Use **GPT-5.5** or any other non-Claude engine for this validation.

### Independence rule

Do NOT read other verdicts on this WP before forming your own conclusions. The R1/R2/R3 PRE_HANDOFF verdicts are listed in §4 only as gate-history evidence — your VC-1..VC-20 conclusions must be independently derived from the LOD400 itself.

---

## 7. Authorization basis

This mandate is issued by **team_110 directly** (not via team_100), authorized by:

- **ADR045 R2 #2** — `team_110 may independently issue mandates to team_190` while holding an `execution_authority: full` mandate.
- **Active mandate:** `_COMMUNICATION/TEAM_110/SFA-S003-P002-WP-B/EXECUTION_MANDATE_v1.0.0.md` (issued by team_00, validated by team_190 R3 PASS at commit `7c3d7d6`).

team_100 is intentionally NOT in the routing chain for this mandate per ADR045 R2; team_100 receives only the `COMPLETION_REPORT` for each WP upon LOD500_LOCKED.

---

*Mandate issued 2026-05-24 by team_110 (Claude Opus 4.7) under EXECUTION_MANDATE SFA-S003-P002-WP-B.*
*Validator: team_190 (non-Claude per IR#1).*
*Awaiting verdict at `_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1/LOD400-VERDICT_v1.0.0.md`.*
