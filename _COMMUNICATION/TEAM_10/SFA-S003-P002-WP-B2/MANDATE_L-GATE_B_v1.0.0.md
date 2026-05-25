---
id: MANDATE_SFA-S003-P002-WP-B2_L-GATE_B_v1.0.0
from: team_110 (AOS Domain Architect — ADR045 execution_authority: full)
to: team_10 (sfa_build — Builder — separate session per IR#1)
date: 2026-05-25
type: GATE_MANDATE
gate: L-GATE_B
wp: SFA-S003-P002-WP-B2
project: smallfarmsagents
status: ACTIVE
verdict: PENDING
engine_constraint: "Iron Rule #1 — builder engine MUST differ from team_190 (GPT-5.5). Recommended: Claude Code (Sonnet) in a SEPARATE session from team_110 (Claude Opus 4.7)."
authorization_basis: "ADR045 R2 #2 — same EXECUTION_MANDATE as B1 / patch01 / B3."
spec_ref: _aos/work_packages/S003/SFA-S003-P002-WP-B2/LOD400_spec.md
spec_version: v1.1.3
spec_lock_commit: "TBD"   # this commit's hash; team_10 references at build time
parent_wp_b1_lod500_commit: "6a85561"
parent_wp_b1_patch01_lod500_commit: "3e1f946"
lgate_s_verdict_ref: _COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B2/LOD400-VERDICT_v1.0.3.md
team_00_decision_ref: _COMMUNICATION/team_00/DECISION_WP-B-OPEN-QUESTIONS_2026-05-25_v1.0.0.md
sequencing_unblocks: SFA-S003-P002-WP-B3 (migration 046 depends on 045 produced by this build)
---

# L-GATE_B Mandate — SFA-S003-P002-WP-B2

**ספר גידולים: JMF NI Extraction Layer (AI-assisted, text-file input)**
**Track:** A | **Profile:** L0 | **Effort:** LARGE | **Risk:** MEDIUM (LLM extraction + licensing surface)

---

## 1. Gate History

| Gate | Result | Validator |
|------|--------|-----------|
| L-GATE_E | PASS | team_00 |
| L-GATE_S R1/R2/R3/R4 | FAIL/FAIL/FAIL/**PASS_WITH_FINDINGS** | team_190 (GPT-5.5) — 4 rounds; spec evolved v1.0.0 → v1.1.3 |
| L-GATE_B | (this mandate ↓) | team_10 |

Spec is LOD400_LOCKED at v1.1.3. team_00 DECISION authorized Q1 (text-file input) + Q5 (6-source scope).

---

## 2. Scope

Implement LOD400 v1.1.3 per the 10-step build sequence at §11. LARGE effort with 6 NIImporter subclasses + LLM extraction harness.

**Sequencing note:** B2's migration 045 (`crop_knowledge_notes`) is a precondition for B3's migration 046 (`alembic upgrade 046` has `down_revision = "045"`). Completing this build unblocks the B3 builder spawn. team_110 holds the B3 builder spawn until this BUILD_REPORT lands.

---

## 3. Acceptance Criteria

Spec §9 defines 21 ACs (AC-01..AC-21 with sub-letter parts). Critical:

- **AC-03/AC-03b** — NI_IMPORTER_CLASSES has 6 entries; B2 subclasses absent from ni_registry.registered_labels (proves bypass)
- **AC-04a** — body_text length CHECK enforced at DB level (advisory #1)
- **AC-05** — is_internal_farm_use_only TRUE default (licensing)
- **AC-10/AC-12** — DB integration end-to-end + cultivar_recommendation engine reuse via existing `_upsert_source_value(session, variety_id, sv)` signature
- **AC-15** — Cache .gitkeep + .gitattributes
- **AC-19** — seed.py diff = exactly +2 CLI flags + 1 call-site block (NO helper additions; resolution lives in subclasses)
- **AC-20** — `_aos/governance/` + `_aos/lean-kit/` CLEAN
- **AC-21a/b/c** — §3.1 OPERATIVE LICENSING INVARIANT: publisher + views.py CLEAN; `test_ni_publisher_isolation.py` asserts no publisher/views file references `crop_knowledge_notes`

---

## 4. LOD500_LOCKED files (DO NOT modify beyond §2.3 scope)

See spec §2.2 + §14 for the full list. The ONLY permitted exceptions:
- `ni_importer.py` — APPEND `_upsert_knowledge_note` helper function (single module-level function; no class change)
- `seed.py` — add `--ni-only`, `--no-ni` flags + 1 new call-site block (NO helper functions)
- `CHANGELOG.md` — append [Unreleased] entry

---

## 5. Required Files to Read FIRST

1. This mandate (§1-§8)
2. Spec v1.1.3: `_aos/work_packages/S003/SFA-S003-P002-WP-B2/LOD400_spec.md`
3. L-GATE_S R4 verdict (2 MINOR carries — F-R4-01 closed in v1.1.3; F-R4-02 historical labels accepted): `_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B2/LOD400-VERDICT_v1.0.3.md`
4. team_00 DECISION (Q1 + Q5): `_COMMUNICATION/team_00/DECISION_WP-B-OPEN-QUESTIONS_2026-05-25_v1.0.0.md`
5. WP-A `ni_importer.py` — **VERIFY** the class is named `NIImporter`, the abstract method is `load()`, the validate() method drops rows missing variety_id (B2 bypasses load_all() for this reason)
6. Existing `_upsert_source_value(session, variety_id, sv)` signature in `seed.py` — use EXACTLY this shape; do NOT invent variants

---

## 6. Iron Rule constraints

- **IR#1** — Sonnet ≠ Opus 4.7 (team_110) ≠ GPT-5.5 (team_190)
- **IR#4** — Do NOT touch `_aos/roadmap.yaml`
- **IR#5** — L-GATE_V is team_190's
- **IR#6** — BUILD_REPORT in `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B2/`
- **IR#11** — Never touch `_aos/governance/`, `_aos/lean-kit/`

---

## 7. Build outputs

Step 10 nuance per spec §11: builder commits ONLY:
- All new code/test files (per §15 CREATE list)
- `.gitkeep` placeholders for `data/jmf/raw_text/<6 source dirs>/` and `data/jmf/extracted/<6 source dirs>/`
- `.gitattributes` entry for `data/jmf/extracted/** linguist-vendored`
- Fixture JSONs at `tests/crop_book/fixtures/ni/<source>/<crop>.json` (12+ files — 6 sources × 2+ crops; builder hand-generates these)

Builder does NOT:
- Run live Anthropic API calls
- Read real PDFs (Q1 — input is text files which team_00 supplies post-merge)
- Commit real (non-fixture) cache JSONs

team_00 will run `scripts/extract_jmf_ni.py --source <X> --all` post-merge against text files they provide.

---

## 8. Commit policy

Separate commits per build step (§11 Steps 2-10). Prefix: `build(WP-B2/...):`. End with:
```
Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

After each commit, run `validate_aos.sh` — expect 0 FAIL (PASS/SKIP totals may be 28/20 or 29/18/19 — F-S-B2-04 carry).

---

## 9. Output — BUILD_REPORT

Write to: `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B2/BUILD_REPORT_v1.0.0.md` per the canonical 8-section pattern.

Final agent response to team_110: ≤200 words. Include commit range, test counts, validate_aos.sh, BUILD_REPORT path, inquiries.

---

## 10. Authorization basis

ADR045 R2 #2. Mandate root `_COMMUNICATION/TEAM_110/SFA-S003-P002-WP-B/EXECUTION_MANDATE_v1.0.0.md`. team_00 DECISION authorizes Q1 + Q5. team_100 NOT in routing chain.

---

*Mandate issued 2026-05-25 by team_110 (Claude Opus 4.7).*
*Builder: sfa_build (Claude Sonnet sub-agent — to be spawned by team_110 in background).*
*Awaiting BUILD_REPORT at `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B2/BUILD_REPORT_v1.0.0.md`.*
