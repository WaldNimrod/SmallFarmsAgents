---
id: ARCHIVE_MANIFEST_SFA-S003-P002-WP-B1-patch04-hotfix02
wp: SFA-S003-P002-WP-B1-patch04-hotfix02 — Postgres transaction-poisoning fix in _upsert_variety
status: LOD500_LOCKED
closed_at: "2026-05-26"
orchestrator: team_110 (Claude Opus 4.7)
builder: team_110 (Claude Opus 4.7 — single-engine, SMALL scope per hotfix01/patch02 precedent)
validator: team_190 (GPT-5.5 — non-Claude per IR#1)
---

# Archive Manifest — patch04-hotfix02

## 1. Gate chain

| Gate | Result | Commit |
|------|--------|--------|
| L-GATE_E | PASS (team_00 via DECISION) | — |
| L-GATE_S R1 | **PASS clean** (no findings) | `d88919f` |
| L-GATE_BUILD | BUILD_COMPLETE (single-engine team_110) | `c2a257d` |
| L-GATE_V R1 | **PASS clean** (8/8 VCs) | `4efaeb0` |

Zero R-cycles needed — cleanest WP in the EXECUTION_MANDATE extension.

## 2. Deliverables (commit `c2a257d`)

| File | Change |
|------|--------|
| `scripts/load_masterclass_sheets.py` | `_upsert_variety`: replaced `try/except: pass` with `ON CONFLICT (crop_id, name_en) DO NOTHING` |
| `tests/integration/test_load_masterclass_sheets.py` | +1 regression test (`test_load_masterclass_no_silent_try_except_around_execute`) |
| `CHANGELOG.md` | `[Unreleased]` entry |

3 files modified, +51/-11 lines.

## 3. ADR042 closure

| Step | Outcome |
|------|---------|
| 1. Archive manifest | ✓ This file |
| 2. Roadmap | status DONE / LOD500_LOCKED / current_lean_gate L-GATE_V / closed_at / archive_ref |
| 3. validate_aos.sh | 29 PASS / 19 SKIP / 0 FAIL ✓ |

## 4. Iron Rules
- IR#1 cross-engine ✅ (orchestrator-vs-validator distinction maintained)
- IR#4 single-writer roadmap ✅
- IR#11 governance untouched ✅

## 5. Lessons learned

**Python `try/except: pass` around `session.execute` is a Postgres anti-pattern.** SQLite tolerates aborted-transaction states silently; Postgres marks the transaction aborted on any constraint violation, blocking all subsequent statements until rollback. The right idioms:
- For UNIQUE conflicts: `INSERT ... ON CONFLICT (...) DO NOTHING` SQL clause (Postgres-native, works in SQLite 3.24+)
- For broader exception handling: SAVEPOINTs or explicit session.rollback() after catching
- Never silent-swallow + continue using the same session

Combined with hotfix01's int↔bool lesson: **scripts that target Postgres MUST be tested against a Postgres fixture during development, not SQLite alone.** patch04 future work should add Postgres CI fixtures.

## 6. Unblocks

- **OP-2 resume:** `python scripts/load_masterclass_sheets.py --load-db ...` against production Postgres — NOW expected to succeed
- **OP-3 resume:** `python scripts/patch06_db_cleanup.py --apply`
- **OP-4 open:** patch07 for sheet 056 M2M data load

---

*Archive manifest 2026-05-26 by team_110. SMALL hotfix WP — second in the patch04 lineage.*
