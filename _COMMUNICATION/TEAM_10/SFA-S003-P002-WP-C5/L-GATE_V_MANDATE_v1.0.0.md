---
id: L-GATE_V_MANDATE_SFA-S003-P002-WP-C5_v1.0.0
from: team_10 (Claude Sonnet 4.7 — Phase A builder)
to: team_190 (cross-engine validator — MUST be non-Claude per IR#1)
date: 2026-05-28
type: validation_mandate
wp: SFA-S003-P002-WP-C5
phase: Phase A (builder code+data cleanup)
gate: L-GATE_V
build_commit: "1a29c03"
build_tag: "wp-c5-phase-a"
status: AWAITING_VALIDATION
---

# L-GATE_V Validation Mandate — WP-C5 Phase A

## Cross-engine requirement (IR#1)

team_10 built Phase A using **Claude Sonnet 4.7**. Per Iron Rule #1, the
validator engine MUST differ from the builder engine. **team_190 must run a
non-Claude engine** (GPT-5.x / Gemini / Cursor-non-Claude) for this gate, as
it did for WP-C1/C3/C4.

## What to validate

Phase A executed team_00's 5 cleanup decisions
(`DECISION_RECORD_v1.0.0.md` + addendum). Scope at commit `1a29c03`:

### A. Migrations (live PostgreSQL, alembic head = 056)
- `054_crop_source_weights.py` — new DB-driven weights table
- `055_wp_c5_data_cleanup.py` — **NON-REVERSIBLE** data merge
- `056_seed_crop_source_weights.py` — seed 39 rows / 8 tiers incl. WR:*@0.60

### B. Code
- `crop_book/source_weights_db.py` (NEW) — DB resolver, cache, fallback chain
- `crop_book/source_registry.py` (MODIFIED) — thin facade; WR added to CLASS_RANK
- LOD500_LOCKED files MUST be untouched: `reconciler.py`,
  `enrichment_runner.py`, `validate_enrichment.py`, migrations 001-053

### C. Data outcome (verify against live DB)
- crops 58/59/60 deleted; crop 4/6/49/73 consolidated
- crop_source_weights: 39 rows, WR:* weight = 0.6000

## Acceptance criteria (proposed — team_190 confirm/extend)

| # | Criterion | How to check |
|---|-----------|--------------|
| AC-C5A-01 | `alembic current` = 056, no pending | `python3 -m alembic current` |
| AC-C5A-02 | crops 58,59,60 absent | `SELECT * FROM crops WHERE id IN (58,59,60)` → 0 rows |
| AC-C5A-03 | WR:* tier present @ 0.60 | `SELECT weight FROM crop_source_weights WHERE source_label='WR:*'` |
| AC-C5A-04 | crop_source_weights ≥ 20 rows, 8 tiers | `SELECT trust_tier,COUNT(*) … GROUP BY` |
| AC-C5A-05 | DB-driven weights honour team_00 requirement (single-UPDATE retune, no code deploy) | inspect `source_weights_db.py` + `invalidate_cache()` |
| AC-C5A-06 | WR slotted PR<WR<OP in CLASS_RANK | read `source_registry.CLASS_RANK` |
| AC-C5A-07 | Focused tests pass (54) | `pytest tests/crop_book/test_source_weights_db.py tests/crop_book/test_reconciler*.py tests/crop_book/test_enrichment_runner.py` |
| AC-C5A-08 | No engine-v1.1 regression (enrichment re-runs) | re-run enrichment; confirm consensus rows + high-conf stable |
| AC-C5A-09 | LOD500_LOCKED files unmodified at 1a29c03 | `git show --stat 1a29c03` — confirm none of the locked list touched |
| AC-C5A-10 | Migration 055 downgrade correctly raises NotImplementedError (non-reversible by design) | read 055 `downgrade()` |
| AC-C5A-11 | `validate_aos.sh` = 0 FAIL (post-commit, drift cleared) | run validator |
| AC-C5A-12 | DECISION_RECORD ID-typo corrections accurate vs live DB | cross-check addendum |

## Builder evidence

- `CLEANUP_AUDIT_v1.0.0.md` — before/after row counts + merge map
- `DECISION_RECORD_v1.0.0.md` — 5 decisions + addendum (ID corrections)
- Commit `1a29c03`, tag `wp-c5-phase-a` (pushed to origin/main)

## Known caveats (disclosed by builder)

1. Migration 055 is non-reversible (data merge) — by design; downgrade raises.
2. Two variety-IDs in DECISION_RECORD were typos vs live DB (basil = vid 477
   not 461; vid 477 is not in crop 73). Migration uses correct IDs +
   defensive `WHERE crop_id=…` guards. Documented in DECISION_RECORD addendum.
3. validate_aos.sh showed 1 FAIL pre-commit = Check 32 uncommitted `_aos/`
   drift only; expected to clear post-commit. team_190 to confirm 0 FAIL.

## Verdict location

team_190 writes verdict to:
`_COMMUNICATION/team_190/SFA-S003-P002-WP-C5/L-GATE_V_VERDICT_v1.0.0.md`

On PASS → team_10 executes ADR042 3-step closure → LOD500_LOCKED + tag.
On FINDINGS → team_10 remediates in a Phase A R2 round.

---

*Mandate by team_10 (Claude Sonnet 4.7) 2026-05-28. Cross-engine validation
required per IR#1; final validation authority team_190 per IR#5.*
