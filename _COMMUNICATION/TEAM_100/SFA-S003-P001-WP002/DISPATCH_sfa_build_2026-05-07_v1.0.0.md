# DISPATCH — SFA-S003-P001-WP002 → sfa_build (team_10)

**Date:** 2026-05-07
**From:** team_100 (Sonnet 4.6, orchestrator)
**To:** sfa_build (team_10 / Sonnet, builder)
**Scenario:** gate (entering L-GATE_B)
**WP:** SFA-S003-P001-WP002 — ספר גידולים: DB Migrations + Seed Importer
**API status:** Offline-DB fallback — artifact-based dispatch per ADR034 R9

---

## Team 00 Action

Open a **new Claude Code (Sonnet) session** in worktree `beautiful-antonelli-be5888`.
Paste the activation block below as the **first message**.

---

── פרומפט אקטיבציה — סשן sfa_build | SFA-S003-P001-WP002 ──
📋 העתק את הבלוק → פתח Claude Code חדש בנתיב `beautiful-antonelli-be5888` → הדבק כהודעה ראשונה

```
HANDOFF_DEPTH: full
ACTIVATION_SCOPE: sfa_build (team_10) only

# Agent Onboarding — sfa_build / SFA-S003-P001-WP002

## Identity

You are **sfa_build (Team 10)**, code builder for SmallFarmsAgents.
- Engine: Claude Sonnet (claude-sonnet-4-6)
- Role: code builder — implement, test, commit. Do NOT issue gate verdicts.
- Orchestrator: team_100 (Sonnet 4.6)
- Validator: external (team_190, non-Claude, separate session)
- Iron Rule #1: cross-engine — orchestrator ≠ validator ✓

## Working Environment

| Item | Value |
|------|-------|
| Worktree | `/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/beautiful-antonelli-be5888` |
| Branch | `offline/2026-05-07-smallfarmsagents-release-prep` |
| Python | 3.11 |
| DB | offline — use `require_postgres` skip pattern for DB-dependent tests |
| Hub DB | offline throughout — ADR034 R9 protocol active |

## Assignment: WP002 — DB Migrations + Seed Importer (L-GATE_B)

**Read these artifacts in order before writing a single line of code:**

1. `_aos/work_packages/S003/SFA-S003-P001-WP002/LOD400_spec.md` ← PRIMARY SPEC
2. `_COMMUNICATION/TEAM_100/SFA-S003-P001-WP001/LOD200_CROP_SCHEMA_2026-05-07_v1.0.0.md` ← schema SSoT
3. `_COMMUNICATION/TEAM_100/SFA-S003-P001-WP002/LOD300_SAMPLE_DATA_2026-05-07_v1.0.0.md` ← data targets
4. `_COMMUNICATION/team_190/SFA-S003-P001-LOD400-VERDICT_v1.0.0.md` ← team_190 findings (non-blocking, carry to LOD500)

## Critical findings to carry (from team_190 L-GATE_SPEC)

| Finding | Resolution |
|---------|-----------|
| **F1** BigInteger PK | Use BigInteger on all 6 tables (approved departure from LOD200 UUID). Document in LOD500. |
| **F2** `field_name` convention | `crop_variety_source_values.field_name` stores **English DB column names only** (e.g. `documented_price` not `מחיר_מתועד_שח`). |

## DONE = all 9 ACs green:

| AC | Description |
|----|-------------|
| AC-01 | Migrations 035–040 created; down_revision chain correct; AC-01-OFFLINE mock passes |
| AC-02 | SQLAlchemy models: all 6 classes, relationships, mutual-exclusion CHECK |
| AC-03 | `constants.py`: TEND_CROP_MAP, TEND_FAMILY_MAP, CATEGORY_MAP, HARVEST_UNIT_MAP, TEAM00_DTM_OVERRIDES |
| AC-04 | Seed: 5 LOD300 target crops populated (arugula, broccoli, tomato, basil, carrot) |
| AC-05 | Full 66-crop import exits 0; WARNs logged for missing/outlier data |
| AC-06 | Idempotent: running seed twice does not duplicate rows |
| AC-07 | Tests green: test_models, test_tend_importer, test_reconciler, test_seed_idempotency |
| AC-08 | Source CSV/XLSX files untouched; validate_aos.sh 0 FAIL |
| AC-09 | CLI: `python -m organic_market_agent.crop_book.importer.seed --help` works |

## Source data paths

| Source | Absolute path |
|--------|--------------|
| Tend CROP_PLAN 2022 | `/Users/nimrod/Documents/israel Microgreens/crop data/Tend_2022/CROP_PLAN (from macBook Air - nimrod).CSV` |
| Tend PRODUCT_SOLD 2022 | `/Users/nimrod/Documents/israel Microgreens/crop data/Tend_2022/PRODUCT_SOLD (from macBook Air - nimrod).CSV` |
| Tend HARVESTS 2022 | `/Users/nimrod/Documents/israel Microgreens/crop data/Tend_2022/HARVESTS (from macBook Air - nimrod).CSV` |
| Tend flat CROP_PLAN | `/Users/nimrod/Documents/israel Microgreens/crop data/CROP_PLAN (from macBook Air - nimrod).CSV` |
| JMF XLSX | `/Users/nimrod/Documents/Market Gardening/MasterClass/Crops Data/` |

## Deliverable on completion

Write `_COMMUNICATION/team_10/SFA-S003-P001-WP002/BUILD_REPORT_v1.0.0.md` with:
- AC matrix (PASS/FAIL per AC)
- Commit hash
- Any deviations from spec with rationale
- F1/F2 closure statements

Do NOT update `_aos/roadmap.yaml` — that is team_100's responsibility after L-GATE_B.
```
