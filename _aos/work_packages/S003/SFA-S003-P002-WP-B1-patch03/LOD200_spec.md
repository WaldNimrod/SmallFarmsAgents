---
id: SFA-S003-P002-WP-B1-patch03-LOD200
wp: SFA-S003-P002-WP-B1-patch03 — JMF_CROP_MAP taxonomic expansion (11 value changes)
gate: L-GATE_S (LOD200 — architecture spec)
status: PRE_LOD400
author: team_110 (execution mandate per ADR045)
date: 2026-05-25
version: v1.0.0
parent_wp_chain:
  - SFA-S003-P002-WP-B1 (LOD500_LOCKED at 6a85561)
  - SFA-S003-P002-WP-B1-patch01 (LOD500_LOCKED at 3e1f946)
  - SFA-S003-P002-WP-B1-patch02 (LOD500_LOCKED at 3d78007)
team_00_decision_ref: _COMMUNICATION/team_00/DECISION_WP-B1-patch03_TAXONOMY_2026-05-25_v1.0.0.md
depends_on: [SFA-S003-P002-WP-B1-patch02]
validator: team_190 (non-Claude, Iron Rule #1)
builder: team_10 (Sonnet sub-agent — see §10)
---

# LOD200 — SFA-S003-P002-WP-B1-patch03

## 1. Mission

Apply 11 taxonomic corrections to `JMF_CROP_MAP` per team_00 DECISION 2026-05-25 §§1.1-1.4. Introduces 5 new baseline `crops.name_he` values, splits 2 tomato cultivars off the עגבנייה umbrella, refines 4 existing Hebrew terms.

Net effect on duplicate-target allowlist: 25 → 24 groups (2 disappear, 1 new, 4 shrink).

## 2. In-scope

### 2.1 `JMF_CROP_MAP` value changes (11 lines)

| Key | Current | New |
|-----|---------|-----|
| `Mesclun` | `"תערובת סלט"` | `"עלי בייבי"` |
| `Salad Mix` | `"תערובת סלט"` | `"עלי בייבי"` |
| `Baby kale` | `"קייל"` | `"עלי בייבי"` |
| `Greenhouse Cherry Tomato` | `"עגבנייה"` | `"עגבניית שרי"` |
| `Greenhouse Heirloom Tomato` | `"עגבנייה"` | `"עגבניות מורשת"` |
| `Greenhouse Libanese Cucumber` | `"מלפפון"` | `"מלפפון חממה"` |
| `Chinese Cabbage` | `"כרוב"` | `"כרוב סיני"` |
| `Hot Pepper` | `"פלפל"` | `"פלפל חריף"` |
| `Beans (Bush)` | `"שעועית"` | `"שעועית שיחית"` |
| `Snow Peas` | `"אפונת שלגים"` | `"אפונת שלג"` |
| `Basil` | `"בזיל"` | `"בזיליקום"` |

`len(JMF_CROP_MAP) == 86` unchanged.

### 2.2 LOD500_LOCKED test updates (2 functions — scope-exception authorized)

Per DECISION §4, narrowly-scoped LOD500_LOCKED exception authorizes:
- `tests/crop_book/test_jmf_crop_map.py::test_jmf_crop_map_duplicate_target_allowlist` — replace 25-group dict literal with new 24-group dict (DECISION §3 spec).
- `tests/crop_book/test_jmf_crop_map.py::test_ac03_duplicate_group_count` — `25` → `24`.

### 2.3 New regression tests (11)

One test per value change, asserting:
- New value present
- Old value absent (or absent-as-this-key-value where the old value is still used by other keys)

### 2.4 CHANGELOG.md entry

`[Unreleased]` entry summarizing the 11 changes + group count transition.

## 3. Out-of-scope

- **Live Postgres data-fix** (DECISION §8) — operational concern; team_00 runs SQL post-merge if needed.
- **`crops` table seed-data changes** — `seed.py` is LOD500_LOCKED untouched; the new baseline name_he values (`עלי בייבי`, `עגבניית שרי`, `עגבניות מורשת`, `מלפפון חממה`, `כרוב סיני`) will be created lazily by `JMF_CROP_MAP[crop_jmf_en] → crops.name_he → crops.id` resolution at next import.
- **`crop_varieties` table population** — variant details (mustard mix, salad mix, baby kale under "עלי בייבי"; cultivar names under existing baselines) are populated separately; not in this patch.
- **Hebrew name normalization across other constants** (TEND_CROP_MAP, etc.) — the Tend overlay map is independent and stays as-is.
- **Cross-reference fields** (e.g., `crops.family`/`genus` for the Tomatillos↔עגבנייה suggestion in DECISION §2) — schema doesn't currently support; out-of-scope.

## 4. Data sources

None. This is a literal-value patch in source code.

## 5. Data model summary

`JMF_CROP_MAP: dict[str, str]` literal in `constants.py` gets 11 value updates.

`crops.name_he` resolution chain remains: English key → JMF_CROP_MAP value (Hebrew) → `crops.name_he` row → `crops.id`. Five new baseline rows will be created lazily.

## 6. Trust-layer placement

Unchanged. All affected crops continue to flow through the JMF PR-tier path. The new baseline crops (עלי בייבי etc.) inherit the standard JMF importer trust contract.

## 7. Dependencies

- **WP-B1-patch02** (LOD500_LOCKED at `3d78007`) — supplies the post-Q4 baseline state of `JMF_CROP_MAP`.
- **WP-B1-patch01** (LOD500_LOCKED at `3e1f946`) — supplies the 34 farm-workbook aliases and 25-group duplicate allowlist baseline.
- **WP-B1** (LOD500_LOCKED at `6a85561`) — supplies the importer, AC-03 framework, and `crops` schema.

## 8. LOD500_LOCKED inventory (this patch touches a narrow exception)

All WP-A + WP-B1 + patch01 + B2 + B3 + patch02 deliverables remain LOD500_LOCKED. Per DECISION §4, the **only permitted modifications** are:

1. `organic_market_agent/crop_book/constants.py` — 11 value edits in `JMF_CROP_MAP` (additive scope)
2. `tests/crop_book/test_jmf_crop_map.py` — **scope-exception**: update 2 LOCKED test functions (`test_jmf_crop_map_duplicate_target_allowlist`, `test_ac03_duplicate_group_count`) + append 11 new regression tests
3. `CHANGELOG.md` — `[Unreleased]` entry

## 9. Scope-exception authorization (NOT a hub-level GCR)

Per DECISION §4: the 2 LOCKED tests must reflect the new 24-group allowlist post-patch03. This is a regression-allowlist alignment, not a logic change. The exception is **narrower than B3's GCR-B3-1** (which appended 6 entries to a production tuple); patch03's exception only updates test code to match the new spec.

Authorization sources:
- team_00 DECISION §4 (explicit scope-exception grant)
- Pattern precedent: patch01 (`constants.py` edits as additive scope) + B3 (`crop_task_templates.py` GCR-B3-1 with per-commit team_190 audit)

## 10. Builder-engine rationale (sub-agent required)

Unlike patch02 (single-engine builder for a 4-line patch), patch03 is **MEDIUM effort**:
- 11 value edits + 2 LOCKED test rewrites + 11 new regression tests + CHANGELOG
- ~70-100 effective LOC touched
- Touches LOCKED test code (requires care)
- Introduces 5 new baseline `crops.name_he` concepts (creates downstream operational implications)

**Decision: Sonnet sub-agent (team_10) builds.** team_110 (Opus 4.7) orchestrates. team_190 (GPT-5.5) validates. IR#1 orchestrator-vs-builder separation restored (no longer the single-engine pattern of patch02).

## 11. AC and test count targets

- **Acceptance Criteria target:** 18 ACs in LOD400 (one per value change + 4 structural + 3 hygiene)
- **Test count target:** 13 (11 new regression tests + 2 updated LOCKED tests)

## 12. Open questions (resolved in DECISION)

None. DECISION §§1-3 enumerate all 11 changes with explicit Hebrew values + architectural rationale.

## 13. Sequencing

patch03 is the **next WP after the WP-B program closure**. team_110 EXECUTION_MANDATE remains active for this single follow-up before naturally ending.

Build can proceed in parallel with NotebookLM JMF extraction (no shared resources).

---

*LOD200 v1.0.0 — authored 2026-05-25 by team_110 under EXECUTION_MANDATE SFA-S003-P002-WP-B (ADR045 R2 #1 — spec-author authority).*
*Next phase: LOD400.*
