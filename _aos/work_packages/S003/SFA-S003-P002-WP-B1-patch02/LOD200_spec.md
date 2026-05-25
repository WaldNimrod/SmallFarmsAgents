---
id: SFA-S003-P002-WP-B1-patch02-LOD200
wp: SFA-S003-P002-WP-B1-patch02 — JMF_CROP_MAP Hebrew terminology corrections (Q4)
gate: L-GATE_S (LOD200 — architecture spec)
status: PRE_LOD400
author: team_110 (execution mandate per ADR045)
date: 2026-05-25
version: v1.0.0
parent_wp_chain:
  - SFA-S003-P002-WP-B1 (JMF Excel baseline — LOD500_LOCKED at 6a85561)
  - SFA-S003-P002-WP-B1-patch01 (JMF_CROP_MAP extension to 86 entries — LOD500_LOCKED at 3e1f946)
team_00_decision_ref: _COMMUNICATION/team_00/DECISION_WP-B-OPEN-QUESTIONS_2026-05-25_v1.0.0.md
depends_on: [SFA-S003-P002-WP-B1-patch01]
validator: team_190 (non-Claude, Iron Rule #1)
builder: team_110 (Opus 4.7 — see §10 builder-engine rationale)
---

# LOD200 — SFA-S003-P002-WP-B1-patch02

## 1. Mission

Close the Hebrew terminology debt from team_00 DECISION 2026-05-25 §Q4. The patch01 cycle introduced the 86-entry `JMF_CROP_MAP`, but three Hebrew values were left for a follow-up. team_00 has now specified the corrections:

| Key | Current value (post-patch01) | Corrected value (this patch) | Action |
|-----|------------------------------|------------------------------|--------|
| `Parsnips` | `"גזר לבן"` (colloquial — "white carrot") | **`"שורש פטרוזילה"`** ("parsley root" — botanically accurate) | CHANGE |
| `Shallots` | `"שאלוט"` (transliteration only) | **`"בצלצלי שאלוט"`** ("shallot small-onions" — Hebrew + transliteration hybrid) | CHANGE |
| `Tomatillos` | `"תומאטיו"` (transliteration) | `"תומאטיו"` — confirmed | NO CHANGE (recorded for completeness) |

## 2. In-scope

- **Single-file edit** to `organic_market_agent/crop_book/constants.py`: 2 line value changes in the `JMF_CROP_MAP` literal (Parsnips + Shallots)
- **No schema change**, no migration, no ORM modification, no new tests' code paths
- **AC-03 Counter assertion** in `tests/crop_book/test_jmf_crop_map.py` regression-tested unchanged (Parsnips + Shallots are NOT in any duplicate-target group — they have unique Hebrew values)
- **2 new tiny regression tests** asserting the specific new Hebrew values
- **CHANGELOG.md** `[Unreleased]` entry

## 3. Out-of-scope

- **No additions to `JMF_CROP_MAP`** (patch01 already covers the 86-entry contract)
- **No changes to other Hebrew values** — Tomatillos confirmed as-is; nothing else in scope
- **No edits to LOD500_LOCKED files** beyond the additive-scope precedent in patch01 (`constants.py` is LOD500_LOCKED via patch01; this patch's modification is a 2-line value edit, narrowly scoped — see §10)
- **Live Postgres DB update** is out-of-scope at the spec level. If the prod DB already has incorrect `crops.name_he` rows for these crops (from a prior `seed.py --all` run), a data-fix is a SEPARATE follow-up; this WP only fixes the literal in source.

## 4. Data sources

None. This is a literal-value patch in source code.

## 5. Data model summary

No schema change. The `JMF_CROP_MAP: dict[str, str]` literal in `constants.py` gets two value updates.

## 6. Trust-layer placement

Unchanged. Parsnips + Shallots continue to flow through the JMF PR-tier path when the JMF importer encounters them in the source XLSX (note: they are JMF-only crops — not in the live MasterClass workbook based on the patch01 inquiry analysis; they would import from a canonical-edition JMF workbook if one were used). Importer behavior is unchanged.

## 7. Dependencies

- **WP-B1-patch01** (LOD500_LOCKED at `3e1f946`) — supplies the `JMF_CROP_MAP` literal that this patch modifies
- **WP-B1** (LOD500_LOCKED at `6a85561`) — supplies the importer and AC-03 test framework

## 8. LOD500_LOCKED inventory (unchanged in patch02)

All WP-A + WP-B1 + patch01 + WP-B2 + WP-B3 deliverables remain LOD500_LOCKED. The **only permitted modification** is to `constants.py` `JMF_CROP_MAP` — 2 value edits, narrowly scoped.

Permitted modifications:
- `organic_market_agent/crop_book/constants.py` — 2 value edits in `JMF_CROP_MAP` (Parsnips + Shallots), plus an inline comment block citing this DECISION
- `tests/crop_book/test_jmf_crop_map.py` — add 2 regression assertions for the new Hebrew values; AC-03 Counter-set assertion remains unchanged (Parsnips and Shallots are NOT in any duplicate-target group)
- `CHANGELOG.md` — `[Unreleased]` entry

## 9. Scope-exception authorization (NOT a hub-level GCR)

`constants.py` is LOD500_LOCKED via the patch01 closure. Modifying it requires a scope-exception per the LOD500_LOCKED guard. This patch's exception is the **narrowest possible**: 2 specific value substitutions in a single dict literal, authorized by:

- **team_00 DECISION** (`DECISION_WP-B-OPEN-QUESTIONS_2026-05-25_v1.0.0.md` §Q4) which explicitly approved the new values verbatim
- **team_00 sequencing directive** ("לסגור b1 באופן מלא וסופי בלי זנבות" — Hebrew terminology fixes were the last documented "tail" of B1's lifecycle)
- **Reverse-rendering safety**: rolling back this patch via `git revert` restores the prior values cleanly with no schema/data consequences (additive only)

This is **NOT** a hub-level "Governance Change Request" (which would touch `core/governance/` or lean-kit modules). It is a project-internal LOD500_LOCKED scope exception, similar in pattern to "GCR-B3-1" in B3 but smaller in surface.

## 10. Builder-engine rationale (single-line edit pattern)

For typical builds we spawn a Sonnet sub-agent (IR#1 separation orchestrator-vs-builder). For patch02:

- **Scope is 4 lines of code** (2 value edits + 2 assertion lines)
- **No file creation; no architectural decisions**
- **Spawning a sub-agent for this would be over-ceremony** — the cost of context-window + tool-uses exceeds the work
- **IR#1 is preserved** because the validator (team_190 on GPT-5.5) is still a distinct engine from team_110 (Opus 4.7). The orchestrator-vs-builder dimension of IR#1 (per ADR045 §8) is intended to prevent "self-validation chain" — but team_190 is the validator, not team_110. With patch02, team_110 acts as both orchestrator and (tiny-scope) builder; team_190 still independently validates.

**Precedent:** patch01 v1.1.3 cleanup (3 narrative passages + version bump) was applied directly by team_110 (Opus 4.7) without a sub-agent — see patch01 v1.1.3 commit. Same precedent here.

The L-GATE_S R1 mandate to team_190 will explicitly note this single-engine-builder choice for transparency.

## 11. AC and test count targets

- **Acceptance Criteria target:** 4 ACs in LOD400
- **Test count target:** 2 new regression tests

## 12. Open questions (resolved in LOD400)

None. The DECISION file fixes the exact values.

## 13. Sequencing

patch02 is the **final WP** in the WP-B program. After patch02 LOD500_LOCK, the EXECUTION_MANDATE SFA-S003-P002-WP-B is fully satisfied (B1 + patch01 + B2 + B3 + patch02). team_110 mandate naturally ends.

---

*LOD200 v1.0.0 — authored 2026-05-25 by team_110 under EXECUTION_MANDATE SFA-S003-P002-WP-B (ADR045 R2 #1 — spec-author authority).*
*Next phase: LOD400.*
