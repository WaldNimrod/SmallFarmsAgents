---
id: MANDATE_CHECK15-ARCHIVE-HOUSEKEEPING_v1.0.0
from: Team 100 (Chief System Architect — smallfarmsagents spoke)
to: Team 191 (Git / Files / Archive governance)
date: 2026-05-27
type: OPS_TASK
scope: archive_housekeeping
project: smallfarmsagents
priority: NORMAL (non-blocking; affects validate_aos.sh Check 15 cleanliness only)
status: ACTIVE
verdict: PENDING
engine_constraint: "Any engine — this is a git/file ops task, no validation logic. Per IR#1 the COMMIT need not be cross-engine since no spec/code is being authored. Recommend Claude (you already in inventory) for consistency."
---

# Check 15 Housekeeping — archive 2 stale WP artifact dirs

**Track:** ops/governance | **Profile:** L0 | **Risk:** LOW (additive moves only; no deletions)

---

## 2. Context

`bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` reports **1 FAIL on Check 15** (Iron Rule #15 — completed WP artifacts must live under `_archive/`, not in `_COMMUNICATION/team_*/`).

2 stale artifact dirs identified:

| Path | WP status | When closed | Why stale |
|------|-----------|-------------|-----------|
| `_COMMUNICATION/team_35/SFA-S003-P002-WP-UI/` | COMPLETE (LOD500_LOCKED 2026-05-27) | bb00e5f | team_35 LOD300 design package + handoff (548 KB / 33 files / 7 markdown + design canvas + 7 CSS + 14 JSX). team_190 R2 PASS closure 2026-05-27. |
| `_COMMUNICATION/team_99/SFA-S002-P001-WP008/` | COMPLETE long ago | 5b80c60 | DEPLOY_LOG_v1.0.0 from S002-P001-WP008 deploy. Pre-dates this session entirely. |

Per Iron Rule #15 + Directory Authority (CLAUDE.md), team_191 owns `_archive/` moves.

---

## 3. Scope

**Move both stale dirs to `_archive/` with full git history preservation.** Verify `validate_aos.sh` returns 0 FAIL after each move.

**Out of scope:**
- Any active WP (sfa_delivery/, current LOD400 spec, recent mandates/verdicts)
- Deletions of any kind
- Cross-spoke moves
- `_aos/` content (read-only snapshot — don't touch)

---

## 4. Acceptance Criteria

| # | AC | How to verify |
|---|----|----|
| AC-1 | `_COMMUNICATION/team_35/SFA-S003-P002-WP-UI/` no longer exists on disk under `_COMMUNICATION/` | `ls _COMMUNICATION/team_35/SFA-S003-P002-WP-UI/ 2>&1 \| grep -c 'No such'` returns 1 |
| AC-2 | `_archive/SFA-S003-P002-WP-UI/` (or equivalent path per `_archive/` convention) contains the moved files with intact git log (git mv, not delete+re-add) | `ls _archive/SFA-S003-P002-WP-UI/` shows the handoff files; `git log --follow _archive/SFA-S003-P002-WP-UI/_handoff/HANDOFF_LOD300.md` shows the original add commit |
| AC-3 | `_COMMUNICATION/team_99/SFA-S002-P001-WP008/` similarly moved to `_archive/` | parallel check to AC-1 + AC-2 |
| AC-4 | `validate_aos.sh` returns **0 FAIL** after the moves | `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh . \| grep RESULT` shows `0 FAIL` |
| AC-5 | One commit (or 2 — one per move) on the working branch with clear message | `git log --oneline -2` shows e.g. `ops(team_191): archive ...` |
| AC-6 | Branch pushed to origin | `git push origin <branch>` succeeds |

---

## 5. Recommended approach

```bash
# 0. Verify branch + state
cd /Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/gallant-elbakyan-727a60
git status -s | grep -v '^??'   # should be clean

# 1. Check _archive/ conventions used in this repo
ls _archive/ | head
# Existing patterns: SFA-S002-P001/, SFA-S003-P001/, S001-P001-WP001/
# Suggest: _archive/SFA-S003-P002-WP-UI/team_35/   and   _archive/SFA-S002-P001-WP008/team_99/

# 2. Move stale dir #1 (team_35 WP-UI handoff package)
mkdir -p _archive/SFA-S003-P002-WP-UI
git mv _COMMUNICATION/team_35/SFA-S003-P002-WP-UI _archive/SFA-S003-P002-WP-UI/team_35

# 3. Move stale dir #2 (team_99 WP008 deploy log)
mkdir -p _archive/SFA-S002-P001-WP008
git mv _COMMUNICATION/team_99/SFA-S002-P001-WP008 _archive/SFA-S002-P001-WP008/team_99

# 4. Validate before commit
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
# Expect: 0 FAIL

# 5. Commit (one combined or two)
git commit -m "ops(team_191): archive WP-UI + WP008 completed artifacts per IR#15 / Check 15"

# 6. Push
git push origin claude/gallant-elbakyan-727a60

# 7. File closure report
# Write _COMMUNICATION/TEAM_191/ARCHIVE_COMPLETE_CHECK15_HOUSEKEEPING_2026-05-27_v1.0.0.md
# Mirror existing pattern: ARCHIVE_COMPLETE_SFA-S002-P001_2026-05-07_v1.0.0.md
```

**Alternative:** use `/AOS_archive` skill if you prefer the API-driven path (hub endpoint `POST /api/artifacts/archive` with dry_run + execute). The skill instructions are in `/Users/nimrod/Documents/agents-os/lean-kit/modules/...`. Either approach is acceptable; the git mv approach above is more transparent for L0 spokes.

---

## 6. Output Format

Write closure report to:
`_COMMUNICATION/TEAM_191/ARCHIVE_COMPLETE_CHECK15_HOUSEKEEPING_2026-05-27_v1.0.0.md`

Mirror the existing pattern (see `ARCHIVE_COMPLETE_SFA-S002-P001_2026-05-07_v1.0.0.md` + `ARCHIVE_COMPLETE_SFA-S003-P001_2026-05-22_v1.0.0.md` in same dir for format).

Minimum content:
1. **Outcome** — single line ARCHIVED + which 2 WPs
2. **Moves** — table of from→to paths with file counts
3. **Verification** — `validate_aos.sh` output (expect 0 FAIL)
4. **Commits + push** — git refs

---

## 7. Constraints + reminders

- **Directory Authority (CLAUDE.md):** team_191 may write to `_COMMUNICATION/team_191/`, `_archive/`, `_aos/` (bootstrap/propagation under mandate). The moves here are within authority — no escalation needed.
- **IR#1:** Not strictly cross-engine-required for ops; if you want to be conservative, use a non-Claude session. Practically, Claude is fine.
- **IR#4:** Do NOT mutate `_aos/roadmap.yaml`. team_100 already updated it (WP-UI = COMPLETE). Your moves don't change WP status.
- **No content edits:** all archive moves are `git mv` only. Do not edit file content; do not delete; do not re-create.
- **Branch:** work on `claude/gallant-elbakyan-727a60` (current head: bb00e5f). After commit, push to origin.

---

*Mandate filed 2026-05-27 by team_100. Awaiting your closure report.*
