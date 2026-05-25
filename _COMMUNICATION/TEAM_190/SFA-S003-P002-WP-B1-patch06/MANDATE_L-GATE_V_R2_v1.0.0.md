---
id: MANDATE_SFA-S003-P002-WP-B1-patch06_L-GATE_V_R2_v1.0.0
from: team_110
to: team_190
date: 2026-05-26
type: GATE_MANDATE
gate: L-GATE_V
wp: SFA-S003-P002-WP-B1-patch06
round: R2
status: ACTIVE
verdict: PENDING
orchestrator: team_110 (Claude Opus 4.7)
builder: team_10 (Claude Sonnet) + team_110 fix commit
validator: team_190 (GPT-5.5, non-Claude per IR#1)
engine_chain: "team_110 ≠ team_10 ≠ team_190"
spec_ref: _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch06/LOD400_spec.md
spec_version: v1.0.3
build_commit_initial: 113b47d
build_commit_incremental: 8920269
fix_commit: fb3d6aa
prior_round_ref: _COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1-patch06/LGATEV-VERDICT_v1.0.0.md
prior_round_result: FAIL (1 BLOCKER — context-manager misuse in patch06_db_cleanup.py)
---

# L-GATE_V R2 — patch06

## 1. R1 Disposition

FAIL with 1 BLOCKER on AC-12/AC-13: `scripts/patch06_db_cleanup.py --dry-run` failed at runtime because `get_session()` was treated as a raw Session instead of a `@contextmanager`. Correct find by team_190.

Root cause: builder copied a pattern that pre-supposed raw session API. `get_session` in this repo is decorated `@contextmanager`, so the return value is a CM, not a Session.

A second latent issue was uncovered during fix verification: SQLAlchemy mapper registry was incomplete — `CropFieldEnrichment` (referenced by `Crop` via relationship) was not imported before `session.query(Crop)` triggered mapper initialization. This would have surfaced as the next error after the CM fix.

## 2. Fix (commit `fb3d6aa`)

Single file changed: `scripts/patch06_db_cleanup.py`.

| Change | Detail |
|--------|--------|
| `main()` body | Restructured to `with _get_session_cm() as session:` + dry-run path explicitly rolls back any speculative changes; `--apply` path commits inside the block |
| `_get_session_cm()` | Pre-imports `models` + `enrichment_models` + `crop_knowledge_notes_crops` (junction) so SQLAlchemy mapper registry is complete before any query; renamed from `_get_session` for clarity (return value is a context manager, not a session) |
| Docstring update | Notes the @contextmanager constraint explicitly |

Diff: 1 file, 37+/17- lines.

## 3. VC-V-R2 (single revised VC)

| # | Criterion | What to Check |
|---|-----------|---------------|
| VC-V-R2 | **AC-12/AC-13 patch06_db_cleanup.py operational** | `PYTHONPATH=. python3 scripts/patch06_db_cleanup.py --dry-run` exits 0 + reports "DRY-RUN complete. Planned changes" + idempotent (2 consecutive dry-runs both exit 0). No `KeyError: 'CropFieldEnrichment'`. No "AttributeError: ... 'session'". |

15 carry-forward VCs (VC-V1..VC-V11, VC-V13..VC-V16 — same as R1, none invalidated by the fix).

## 4. Commands

```bash
cd /Users/nimrod/Documents/SmallFarmsAgents

# 1. Verify fix commit
git show --stat fb3d6aa | head -10

# 2. Dry-run + idempotency
PYTHONPATH=. python3 scripts/patch06_db_cleanup.py --dry-run
echo "exit: $?"
PYTHONPATH=. python3 scripts/patch06_db_cleanup.py --dry-run >/dev/null
echo "second exit: $?"
# Expected: both exit 0, both report idempotent "No orphan crops found" (assuming DB clean)

# 3. Carry-forward checks (sanity — should still hold)
python3 -c "
from organic_market_agent.crop_book.constants import JMF_CROP_MAP
from collections import Counter
c = Counter(JMF_CROP_MAP.values())
print(f'len={len(JMF_CROP_MAP)} groups={sum(1 for n in c.values() if n>1)} sum={sum(n for n in c.values() if n>1)}')
"
# Expected: len=60 groups=6 sum=12

python3 -m pytest tests/crop_book/ -q | tail -3
# Expected: 350 passed + 1 OOS publisher

bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
# Expected: 0 FAIL

# 4. Confirm fix commit scope is narrow (1 file only)
git show --name-only fb3d6aa
# Expected: scripts/patch06_db_cleanup.py (only)
```

## 5. Output

`_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1-patch06/LGATEV-VERDICT_R2_v1.0.0.md`

Commit: `gate(WP-B1-patch06/L-GATE_V R2): team_190 verdict — <RESULT>` Co-Authored-By GPT-5.5.

PASS/PWF → team_110 closes patch06 → **EXECUTION_MANDATE SFA-S003-P002-WP-B NATURALLY ENDS**.
FAIL → R3.

---
