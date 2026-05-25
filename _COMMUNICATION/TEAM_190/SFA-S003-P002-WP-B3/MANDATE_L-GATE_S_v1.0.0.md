---
id: MANDATE_SFA-S003-P002-WP-B3_L-GATE_S_v1.0.0
from: team_110 (AOS Domain Architect — ADR045 execution_authority: full)
to: team_190 (Constitutional Validator — non-Claude per Iron Rule #1)
date: 2026-05-25
type: GATE_MANDATE
gate: L-GATE_S
wp: SFA-S003-P002-WP-B3
project: smallfarmsagents
status: ACTIVE
verdict: PENDING
engine_constraint: "Iron Rule #1 — validator engine MUST differ from team_110 (Claude Opus 4.7). Canonical non-Claude: GPT-5.5."
authorization_basis: "ADR045 R2 #2 — same EXECUTION_MANDATE as B1 + patch01 + B2."
spec_ref: _aos/work_packages/S003/SFA-S003-P002-WP-B3/LOD400_spec.md
spec_version: v1.0.0
parallel_with: SFA-S003-P002-WP-B2 (validate independently — no inter-dependency)
team_00_decision_ref: _COMMUNICATION/team_00/DECISION_SFA-S003-P002-WP-B3-WHITELIST_2026-05-25_v1.0.0.md
gcr_b3_1_authorization: AUTHORIZED via DECISION file (above)
---

# L-GATE_S Mandate — SFA-S003-P002-WP-B3

**ספר גידולים: Tend Israel Adaptation Overlay**
**Track:** A | **Profile:** L0 | **Effort:** MEDIUM | **Risk:** MEDIUM (LOD500_LOCKED ORM extension via GCR-B3-1)

---

## 1. Gate History + GCR-B3-1 Authorization

| Gate | Result | Date | Notes |
|------|--------|------|-------|
| L-GATE_E | PASS | 2026-05-24 | team_00; commit `f61c1da` (B-program-wide registration) |
| L-GATE_PRE_HANDOFF R1-R3 | PASS/FAIL/PASS | 2026-05-24 | Final PASS `7c3d7d6` (program-wide) |
| L-GATE_S | (this mandate ↓) | — | LOD400 v1.0.0 |

**GCR-B3-1 PRE-AUTHORIZED:**
team_00 (Principal) on 2026-05-25 explicitly authorized GCR-B3-1: scoped exception to LOD500_LOCKED `crop_task_templates.py` allowing append of exactly 6 entries to `TASK_TYPE_VALUES` tuple (`nursery_seed`, `pest_spray`, `potting_up`, `thinning`, `trellis`, `fertilize`). DECISION record:
`_COMMUNICATION/team_00/DECISION_SFA-S003-P002-WP-B3-WHITELIST_2026-05-25_v1.0.0.md`

The same DECISION also fixes the Tend task whitelist scope (Option B — 11 categories, 95.0% coverage of TASKS.CSV).

---

## 2. Scope

Validate the LOD400 spec for **WP-B3** (Tend Israel Adaptation Overlay) as a spec-only constitutional review. MEDIUM-effort WP introducing: new table `crop_harvest_stats`; ALTER on B1's `crop_task_templates` CHECK constraint (CHECK extension); GCR-authorized ORM tuple extension; new `tend_overlay.py` importer; whitelist + blacklist + task-type mapping in `constants.py`.

Critical preconditions:
1. team_00 DECISION file (see §1) confirms whitelist scope + GCR-B3-1.
2. WP-B1 LOD500_LOCKED at `6a85561` — provides `crop_task_templates` table + `TASK_TYPE_VALUES` baseline.
3. WP-B1-patch01 LOD500_LOCKED at `3e1f946` — `JMF_CROP_MAP` (used by Tend crop-name resolution alongside existing `TEND_CROP_MAP`).
4. WP-A LOD500_LOCKED at `594cbc8` — engine SSoT.

B3 is **parallel-eligible with B2** (no inter-dependency). However, the migration chain `044 → 045 (B2) → 046 (B3)` is linear — B3's `down_revision = "045"` means B2's migration must land before B3's `alembic upgrade 046` is run (documented in B3 LOD400 §3 + risk register R-07).

---

## 3. Validation Criteria (20 VCs)

| # | Criterion | What to Check |
|---|-----------|---------------|
| VC-1 | **IR#1 cross-engine** | LOD400 frontmatter assigns builder = `sfa_build` (Sonnet recommended) and validator = `team_190 (non-Claude)`. team_110 is Opus 4.7 (orchestrator). |
| VC-2 | **IR#4 single-writer roadmap** | LOD400 does not instruct builder to mutate `_aos/roadmap.yaml`. |
| VC-3 | **IR#6 _COMMUNICATION/ routing** | BUILD_REPORT path is `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B3/BUILD_REPORT_v1.0.0.md`. team_00 DECISION at `_COMMUNICATION/team_00/`. |
| VC-4 | **IR#11 governance untouched** | LOD400 §2.2 lists `_aos/governance/`, `_aos/lean-kit/` as untouchable. |
| VC-5 | **GCR-B3-1 authorization chain valid** | Read `_COMMUNICATION/team_00/DECISION_SFA-S003-P002-WP-B3-WHITELIST_2026-05-25_v1.0.0.md`. Verify §2 explicitly authorizes the 6-entry tuple extension. LOD400 §5 implements verbatim (no extra entries, no different values). |
| VC-6 | **GCR-B3-1 scope tightness** | LOD400 §5 declares the ONLY permitted change to `crop_task_templates.py` is appending 6 string entries to `TASK_TYPE_VALUES`. NO new column, NO method change, NO class restructure. AC-19 enforces via `git diff` audit. |
| VC-7 | **LOD500_LOCKED guard (16+ paths)** | §2.2 enumerates the locked inventory including B1 + patch01 + WP-A engine SSoT + raw-material guard (`tend.py`). §15 MODIFY list contains exactly 4 files: `constants.py` (APPEND TEND_TASK_*), `crop_task_templates.py` (GCR-B3-1 scope only), `seed.py` (additive flags), `CHANGELOG.md`. |
| VC-8 | **Raw-material guard preserved** | LOD400 explicitly documents B3 uses NEW module `tend_overlay.py` (NOT modify existing `tend.py`). §2.2 confirms `tend.py` is LOD500_LOCKED. |
| VC-9 | **Migration chain integrity** | LOD400 §3 declares `revision = "046"`, `down_revision = "045"`. Note: 045 belongs to B2 (parallel WP). LOD400 §11 Step 2 + R-07 explicitly require verifying B2 045 is committed before running `alembic upgrade 046`. |
| VC-10 | **SQLite + Postgres compatibility for ALTER CHECK** | §3 ALTER CHECK constraint uses dialect-branch: Postgres `DROP CONSTRAINT` + `ADD CONSTRAINT`; SQLite `batch_alter_table(recreate="always")`. AC-01b regression-tests on both. |
| VC-11 | **task_type CHECK extension correctness** | §3 + §5 enumerate exactly 20 task_type values (14 B1 baseline + 6 B3 additions). The 6 new values match the team_00 DECISION verbatim. AC-11 regression-tests B1 baseline values still accepted post-migration. |
| VC-12 | **Whitelist + blacklist scope matches team_00 DECISION** | §6 + §12 advisory #3 disposition. The 11 whitelist entries + 10 blacklist entries match the team_00 DECISION §1 verbatim. No spec-side additions or omissions. |
| VC-13 | **HARVESTS aggregation: NEVER per-record** | §7.5 + AC-09. Aggregation is bounded `(crops × 4 seasons × 1 year)`. The 939 raw rows do NOT produce 939 DB rows — aggregation collapses them. AC-09 has an explicit assertion `emitted ≤ crops × 4 × 1`. |
| VC-14 | **Engine reuse (WP-A SSoT)** | §7.4 + §7.7 + AC-20: `days_in_gh_total` + `days_to_first_potting` flow through `_upsert_source_value` (B1 contract) → `reconcile_field()` (WP-A engine). source='Tend_<year>', trust_tier='OP', confidence_weight=0.55 (matches existing `SOURCE_REGISTRY["Tend_<year>"]` from WP-A). |
| VC-15 | **Weed / Row Cover Method disambiguation explicit** | §6 + §7.3 + AC-06 + AC-07: parser inspects `Method` for Weed rows (`Hand weed` → `hand_weed`; `Flextine` → `flextine_harrow_1`; unknown → `hand_weed` + WARN) and `Sub-method` for Row Cover (`Tarp/Cover` → `net_row_cover`; `Straw/Mulch` → `straw_mulch_topdress`; unknown → `net_row_cover` + WARN). |
| VC-16 | **Advisory disposition completeness** | §12: #1 N/A (no PDF), #2 N/A (no LLM), #3 RESOLVED (team_00 Option B DECISION), #4 ADDRESSED (transitive WP-A — §2.1 names WP-A commit `594cbc8` + specific surfaces). |
| VC-17 | **AC measurability** | All 20 ACs (§9) phrased as objective assertions, IntegrityError tests, or count checks. AC-13 explicitly verifies the Option-B additions (Trellis + Fertilize) actually produce rows. |
| VC-18 | **Test coverage adequacy** | §10 lists 20+ tests across 9 files. Whitelist + blacklist + Method disambiguation + aggregation correctness + idempotency + CHECK regression all covered. |
| VC-19 | **`validate_aos.sh` clean at HEAD** | `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` → 29 PASS / 18 SKIP / 0 FAIL. |
| VC-20 | **YAML / artifact integrity + sequencing claim** | `python3 -c "import yaml; yaml.safe_load(open('_aos/roadmap.yaml'))"` succeeds. WP-B3 entry: `lod_status: LOD200_LOCKED`, `current_lean_gate: L-GATE_E`. WP-B1 + patch01 remain `DONE / LOD500_LOCKED`. WP-B2 still `PROPOSED` if its L-GATE_S hasn't passed yet, or `ELIGIBLE` if it has — either is valid (B2 + B3 are independent at L-GATE_S). |

**Total: 20 criteria.**

---

## 4. Files to Review

### Spec documents

- **LOD400 (under review):** `_aos/work_packages/S003/SFA-S003-P002-WP-B3/LOD400_spec.md` (v1.0.0)
- **LOD200:** `_aos/work_packages/S003/SFA-S003-P002-WP-B3/LOD200_spec.md` (v1.0.0)
- **team_00 DECISION (whitelist + GCR-B3-1):** `_COMMUNICATION/team_00/DECISION_SFA-S003-P002-WP-B3-WHITELIST_2026-05-25_v1.0.0.md`

### Context

- **Parent WP-B1 LOD400** (LOD500_LOCKED — read-only reference for `crop_task_templates` schema): `_aos/work_packages/S003/SFA-S003-P002-WP-B1/LOD400_spec.md`
- **WP-B1 `crop_task_templates.py`** (LOD500_LOCKED — verify `TASK_TYPE_VALUES` current shape before B3's append): `organic_market_agent/crop_book/crop_task_templates.py`
- **Existing `TEND_CROP_MAP`** (used by B3 for crop name resolution): `organic_market_agent/crop_book/constants.py`
- **`tend.py`** (raw-material guard — verify B3 LOD400 does NOT propose modifications): `organic_market_agent/crop_book/importer/tend.py`

### Required Commands

```bash
# 1. AOS validation
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .

# 2. Roadmap parse
python3 -c "
import yaml
d = yaml.safe_load(open('_aos/roadmap.yaml'))
for wp_id in ['SFA-S003-P002-WP-B3', 'SFA-S003-P002-WP-B1', 'SFA-S003-P002-WP-B1-patch01', 'SFA-S003-P002-WP-B2']:
    wp = [w for w in d['work_packages'] if w['id'] == wp_id][0]
    print(wp['id'], wp['status'], wp['lod_status'], wp['current_lean_gate'])
"

# 3. team_00 DECISION file present + signs off
test -f _COMMUNICATION/team_00/DECISION_SFA-S003-P002-WP-B3-WHITELIST_2026-05-25_v1.0.0.md && echo "DECISION present" || echo "DECISION MISSING — BLOCKER"

# 4. B1 baseline TASK_TYPE_VALUES (pre-GCR — should be 14)
python3 -c "
from organic_market_agent.crop_book.crop_task_templates import TASK_TYPE_VALUES
print(f'baseline_count={len(TASK_TYPE_VALUES)}')
"
# Expected: baseline_count=14 (B1 baseline, before B3 GCR-B3-1 applied)

# 5. Migration chain
ls organic_market_agent/db/versions/ | grep -E "^04[3-6]_" | sort
# Expected: 043, 044. (045 belongs to B2; B3 will create 046.)
```

---

## 5. Output Format

Write verdict to: **`_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B3/LOD400-VERDICT_v1.0.0.md`**

7-section unified verdict template. **Commit the verdict** with:
```
gate(WP-B3/L-GATE_S): team_190 verdict — <RESULT>
Co-Authored-By: GPT-5.5 <noreply@anthropic.com>
```

**Decision criteria:**
- **PASS** / **PASS_WITH_FINDINGS (0 blockers)** → team_110 proceeds to Phase 4 + 5
- **FAIL (≥1 blocker)** → team_110 remediates + R2

**Independence rule:** validate VC-1..VC-20 from the spec content + commands. The team_00 DECISION file is referenced in §1 ONLY as authorization evidence — do NOT use it to skip the spec-internal-consistency checks.

---

## 6. Authorization basis

ADR045 R2 #2 — team_110 may independently mandate team_190.
GCR-B3-1 pre-authorized by team_00 (DECISION 2026-05-25).
team_100 NOT in routing chain.

---

*L-GATE_S R1 mandate issued 2026-05-25 by team_110 (Claude Opus 4.7).*
*Validator: team_190 (non-Claude). Parallel with B2 — independent validation.*
*Awaiting verdict at `_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B3/LOD400-VERDICT_v1.0.0.md`.*
