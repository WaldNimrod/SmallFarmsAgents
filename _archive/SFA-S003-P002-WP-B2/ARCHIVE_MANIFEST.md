# ARCHIVE_MANIFEST — SFA-S003-P002-WP-B2

**ספר גידולים: JMF NI Extraction Layer — AI-assisted (text-file input)**

| Field | Value |
|-------|-------|
| **wp_id** | SFA-S003-P002-WP-B2 |
| **closure_type** | WP_COMPLETE — **completes the WP-B program** (B1 + patch01 + B3 + this WP all LOD500_LOCKED) |
| **lifecycle_state_at_archive** | `status: DONE` / `lod_status: LOD500_LOCKED` / `current_lean_gate: L-GATE_V` |
| **closed_at** | 2026-05-25 |
| **archived_by** | team_110 (ADR045 R2 #4 closure authority) |
| **authority** | ADR042 3-step closure under ADR045 EXECUTION_MANDATE SFA-S003-P002-WP-B |
| **mandate_ref** | `_COMMUNICATION/TEAM_110/SFA-S003-P002-WP-B/EXECUTION_MANDATE_v1.0.0.md` |
| **team_00 DECISION** | `_COMMUNICATION/team_00/DECISION_WP-B-OPEN-QUESTIONS_2026-05-25_v1.0.0.md` (Q1 text-file input + Q5 6-source scope expansion) |
| **branch** | main |
| **file moves** | NONE (B2 closes the program; future WPs in the SFA-S003-P002-WP-B namespace are out of scope per the EXECUTION_MANDATE) |

---

## 1. Gate timeline — most-iterated WP in the program (4 L-GATE_S + 2 L-GATE_V rounds)

| # | Gate | Result | Date | Validator | Commit / Artifact |
|---|------|--------|------|-----------|-------------------|
| 1 | L-GATE_E | PASS | 2026-05-24 | team_00 | `f61c1da` in-session authorization |
| 2 | L-GATE_S R1 | FAIL | 2026-05-25 | team_190 (GPT-5.5) | spec `91972bc` (v1.0.0); verdict `9db86b7`. 4 findings: BLOCKER NiSourceBase hallucination + 2 MAJOR (scope inconsistency; _upsert_source_value signature) + MINOR (profile drift) |
| 3 | L-GATE_S R2 | FAIL | 2026-05-25 | team_190 | spec `fa11662` (v1.1.0); verdict `89460bc`. 3 BLOCKERS: stale literal token + ni_registry.load_all incompatibility + non-operative licensing prohibition |
| 4 | L-GATE_S R3 | FAIL | 2026-05-25 | team_190 | spec `786b1cf` (v1.1.1); verdict `df26c40`. 2 internal-inconsistency BLOCKERS: bypass-vs-registry + seed.py helper scope contradictions |
| 5 | L-GATE_S R4 | **PASS_WITH_FINDINGS** | 2026-05-25 | team_190 | spec `ddadae3` (v1.1.2) + v1.1.3 cleanup `d195b75`; verdict `cdc3a87`. 0 BLOCKER / 0 MAJOR / 2 MINOR cleanups (closed in v1.1.3) |
| 6 | L-GATE_B | BUILD_COMPLETE | 2026-05-25 | team_10 (Sonnet sub-agent) | 8 build commits `6e9d92d..b6ecb6e`. 37 new tests; 288 total; LOD500_LOCKED CLEAN |
| 7 | L-GATE_V R1 | FAIL | 2026-05-25 | team_190 | verdict `245fd7e`. 1 BLOCKER F-LV-B2-01 (`--ni-only` not NI-only + dup call-site) + 1 MINOR (BUILD_REPORT test-file inventory) |
| 8 | L-GATE_V R2 | **PASS_WITH_FINDINGS** | 2026-05-25 | team_190 | builds `18f8671` + `69966be` (remediation); verdict `c20119b`. 0 BLOCKER / 0 MAJOR / 2 MINOR (probe-wording, not build defects) |
| — | ADR042 closure | — | 2026-05-25 | team_110 | this commit |

**Total rounds:** 6 distinct team_190 reviews (4 L-GATE_S + 2 L-GATE_V). The most iterated WP in the WP-B program — driven by genuine architectural complexity (LLM extraction + WP-A engine reuse subtleties + cross-cycle scope expansion).

---

## 2. Cross-engine separation (Iron Rule #1 audit)

| Role | Engine |
|------|--------|
| Orchestrator + spec author + closure | team_110 (Claude Opus 4.7) |
| Builder (original + R1 remediation) | team_10 (Claude Sonnet 4.6 sub-agent) |
| Validator (4 L-GATE_S + 2 L-GATE_V rounds) | team_190 (GPT-5.5) |

Three distinct engines maintained across the entire chain `f61c1da..c20119b`.

---

## 3. Spec evolution

| Version | Commit | Notes |
|---------|--------|-------|
| v1.0.0 | `91972bc` | Initial authoring. FAILed R1 with NiSourceBase hallucination + 3 other findings. |
| v1.1.0 | `fa11662` | Remediation: 4 R1 findings + Q1 text-file input + Q5 6-source scope (per team_00 DECISION 2026-05-25) |
| v1.1.1 | `786b1cf` | Stale literal token removed; ni_registry.load_all bypass design; operative §3.1 licensing |
| v1.1.2 | `ddadae3` | Internal-inconsistency cleanup (bypass-vs-registry contradictions in §2.1/§7 intro/AC-03/AC-19/Step 8/§15) |
| v1.1.3 | `d195b75` | LOD400_LOCKED: 2 MINOR cleanups closed inline; round-chain footer added |

The spec went from 3 PDF sources to 6 (Q5 expansion); from PDF→pdftotext to text-file input (Q1 redesign); from `crop_knowledge_notes` table with deep-shape rows to clean variety-source-value + crop_knowledge_notes separation; from auto-registered NIImporter subclasses to a bypass-of-registry pattern (validate() drops rows missing variety_id).

---

## 4. Acceptance Criteria summary (21 ACs)

All 21 ACs PASS at L-GATE_V R2. Critical ones:

| AC | Description | Result |
|----|-------------|--------|
| AC-03/AC-03b | NI_IMPORTER_CLASSES has 6 entries; B2 subclasses absent from ni_registry.registered_labels (bypass proof) | PASS |
| AC-04a | body_text length CHECK ≤ 2000 enforced at DB level (advisory #1 fair-use snippet bound) | PASS |
| AC-05 | is_internal_farm_use_only=True default + immutable in _upsert_knowledge_note | PASS |
| AC-12 | cultivar_recommendation via existing `_upsert_source_value(session, variety_id, sv)` (no signature invention) | PASS |
| AC-13 | `--ni-only` truly NI-only (R1 BLOCKER fix; regression test added) | PASS at R2 (failed at R1; fixed by sub-agent commit `18f8671`) |
| AC-15 | .gitkeep skeleton + .gitattributes linguist-vendored | PASS |
| AC-19 | seed.py diff = 2 CLI flags + 1 call-site block (`_run_ni_ingestion` helper); NO forbidden resolver helpers | PASS at R2 (R1 had dup blocks; sub-agent factored to single helper) |
| AC-20 | _aos/governance/ + _aos/lean-kit/ CLEAN | PASS (sub-agent never touched those paths) |
| AC-21a/b/c | §3.1 OPERATIVE LICENSING — publisher + views.py CLEAN + test_ni_publisher_isolation.py | PASS |

**Test totals at closure HEAD `90a2e77`:** 37 new B2 tests (Step 9) + 1 additional regression test added during R1 remediation (`test_ac13_ni_only_dry_run_suppresses_jmf_and_tend`) = 38 net new. 341 total passing (B1 + patch01 + B2 + B3 cumulative). 1 pre-existing publisher failure (out-of-scope; predates WP-B).

---

## 5. Findings disposition (final)

| ID | Severity | Status |
|----|----------|--------|
| F-S-B2-01 (R1) NiSourceBase hallucination | BLOCKER | RESOLVED in spec v1.1.0 |
| F-S-B2-02 (R1) §2.2/§15 scope inconsistency + governance/lean-kit not listed | MAJOR | RESOLVED in v1.1.0 |
| F-S-B2-03 (R1) _upsert_source_value signature hallucinated | MAJOR | RESOLVED in v1.1.0 |
| F-S-B2-04 (R1) lean-kit profile drift | MINOR | CARRY — non-blocking |
| 3× R2 BLOCKERS (stale token + ni_registry.load_all + non-operative licensing) | BLOCKER ×3 | All RESOLVED in v1.1.1 |
| 2× R3 BLOCKERS (bypass-vs-registry + seed.py helper-scope inconsistency) | BLOCKER ×2 | All RESOLVED in v1.1.2 |
| 2× R4 MINOR cleanups (literal token in §7.1; historical labels in code snippets) | MINOR ×2 | F-R4-01 CLOSED in v1.1.3; F-R4-02 accepted as historical context |
| F-LV-B2-01 (L-GATE_V R1) --ni-only not NI-only + dup call-site | BLOCKER | RESOLVED at sub-agent commit `18f8671` |
| F-LV-B2-02 (L-GATE_V R1) BUILD_REPORT test-file inventory | MINOR | RESOLVED at sub-agent commit `69966be` |
| F-LV-B2-R2-01 (L-GATE_V R2) probe expected 2 _run_ni_ingestion calls, actual 4 entry-points | MINOR | CARRY — probe-wording issue (mine), NOT a build defect |
| F-LV-B2-R2-02 (L-GATE_V R2) broad audit range catches B3 interleaved commits | MINOR | CARRY — probe-wording issue, NOT a build defect; team_190 ran per-commit audit and confirmed all 10 B2 commits CLEAN |

**Final score at WP closure: 0 BLOCKER · 0 MAJOR · 4 MINOR (all CARRY) · 0 ADVISORY.**

---

## 6. Iron Rules audit (final)

| Iron Rule | Status |
|-----------|--------|
| **IR#1** cross-engine | ✅ Opus / Sonnet / GPT-5.5 maintained |
| **IR#4** single-writer roadmap | ✅ only team_110 wrote lifecycle fields |
| **IR#5** team_190 validation independence | ✅ team_190 owned all 6 rounds |
| **IR#6** _COMMUNICATION/ routing | ✅ |
| **IR#7** API-only when DB online | ✅ spoke-native per ADR034 R9 |
| **IR#11** governance source→snapshot | ✅ |
| **LOD500_LOCKED** | ✅ 16-17 paths CLEAN; ni_importer.py append-only +65 lines (single helper, no class change); seed.py additive (CLI flags + 1 call-site block + `_run_ni_ingestion` factor) |
| **GCR scope** | ✅ NO GCR required for B2 (all changes were additive or scoped to the permitted ni_importer.py append) |

---

## 7. Lessons learned (most-iterated WP)

WP-B2 went through 6 team_190 rounds (4 L-GATE_S + 2 L-GATE_V). Captured for future reference:

1. **Cross-cycle scope changes** (Q1 + Q5 mid-LOD400) require careful spec-internal consistency. v1.0.0 → v1.1.0 was too coarse; v1.1.1 → v1.1.2 → v1.1.3 chased internal inconsistencies.

2. **API contract verification BEFORE spec drafting** — my v1.0.0 hallucinated `NiSourceBase`/`source_label`/`cache_dir` instead of reading WP-A's actual `NIImporter`/`name`/inheritance. Lesson: when subclassing WP-A skeletons, read the source-of-truth file first.

3. **Operative invariants must be in §1-9 (the operative spec), not §11-12 (advisory)** — my v1.1.0 had the publication prohibition in §11 advisory only; team_190 R2 correctly flagged this as non-operative. v1.1.1 elevated to §3.1 OPERATIVE.

4. **Probe wording must be functional, not literal** — my R1+R2 mandate probes were too strict (literal "0 NiSourceBase mentions" then later "2 _run_ni_ingestion calls"). team_190 R4+R2 correctly noted that strict literal counts mismatch functional correctness. Lesson: probes should assert behavior, not implementation details.

5. **Builder sub-agents handle complex remediations cleanly** — the R1 L-GATE_V remediation (extract helper + reorder fast-path) was a non-trivial refactor that the Sonnet sub-agent executed precisely. Worth the engine-chain ceremony.

---

## 8. WPs unblocked by this closure

B2 LOD500_LOCKED **completes the WP-B program** (all 4 WPs + patch01 closed):

| WP | Status |
|----|--------|
| WP-A | LOD500_LOCKED ✅ (2026-05-23) |
| WP-B1 | LOD500_LOCKED ✅ (2026-05-24) |
| WP-B1-patch01 | LOD500_LOCKED ✅ (2026-05-25) |
| WP-B3 | LOD500_LOCKED ✅ (2026-05-25) |
| **WP-B2** | **LOD500_LOCKED ✅ (this closure, 2026-05-25)** |
| WP-B1-patch02 | now ELIGIBLE (was waiting for B2+B3 closure per team_00 sequencing) |

**WP-B1-patch02 next** — Hebrew terminology per team_00 DECISION Q4 (Parsnips → "שורש פטרוזילה"; Shallots → "בצלצלי שאלוט"; Tomatillos confirmed as-is). Small SMALL-effort patch WP.

---

## 9. ⚠️ Open operational items (carried forward)

1. **Live JMF text-file extraction** (Q1) — team_00 to provide PDF→text conversions at `data/jmf/raw_text/<source>/<crop>.txt` and run `python scripts/extract_jmf_ni.py --source <X> --all` for each of the 6 sources to populate the real cache. Currently empty per BUILD_REPORT Step 10 nuance (builder committed `.gitkeep` + fixtures only).

2. **Live Postgres `alembic upgrade 045`** — migration 045 (`crop_knowledge_notes`) needs to be applied to production Postgres. Same pattern as B3's migration 046. The migration is SQLite-tested; live deployment is team_00's manual action.

3. **WP-B1-patch02 (Q4 Hebrew)** — separate small WP scheduled next per team_00 DECISION sequencing.

---

## 10. validate_aos.sh at archive time

```
RESULT: 29 PASS / 19 SKIP / 0 FAIL
L-GATE_BUILD EXIT CRITERION: SATISFIED
```

Lean-kit profile drift (F-S-B2-04 carry) acknowledged. Gate criterion (0 FAIL) holds.

---

*Archive manifest authored 2026-05-25 by team_110 (Claude Opus 4.7) under ADR042 / ADR045 R2 #4. B2 LOD500_LOCKED completes WP-B program execution.*
