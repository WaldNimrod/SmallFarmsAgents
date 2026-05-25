---
id: DECISION_WP-B1-patch03_TAXONOMY_2026-05-25_v1.0.0
from: team_00 (Principal — in-session, recorded by team_110)
to: [team_110, team_190, team_100]
date: 2026-05-25
type: DECISION
scope: SFA-S003-P002-WP-B1-patch03 — JMF_CROP_MAP taxonomic expansion
status: AUTHORIZED
parent_decision: _COMMUNICATION/team_00/DECISION_WP-B-OPEN-QUESTIONS_2026-05-25_v1.0.0.md
parent_decision_section: "§Q4 (Hebrew terminology) — patch02 closed Parsnips + Shallots; this DECISION amends Q4 with 11 additional corrections"
---

# DECISION — WP-B1-patch03 Taxonomic Expansion

## Background

After patch02 closure (Parsnips + Shallots Hebrew corrections), team_00 conducted a full review of all 86 JMF_CROP_MAP entries + 25 by-design duplicate-target groups. The review surfaced 18 additional observations of which 11 require value changes and 7 are status-quo confirmations.

This DECISION amends DECISION_WP-B-OPEN-QUESTIONS §Q4 to authorize the 11 corrections as a single follow-up patch (patch03).

## §1. Value changes authorized (11)

### §1.1 New baseline crop: "עלי בייבי"

A new baseline `crops.name_he` is introduced. Three existing JMF_CROP_MAP entries are remapped:

| Key | Before (post-patch02) | After |
|-----|----------------------|-------|
| `Mesclun` | `"תערובת סלט"` | **`"עלי בייבי"`** |
| `Salad Mix` | `"תערובת סלט"` | **`"עלי בייבי"`** |
| `Baby kale` | `"קייל"` | **`"עלי בייבי"`** |

**Rationale:** "עלי בייבי" is the colloquial Israeli market category for tender young-leaf greens (kale-baby, mustard mixes, salad mixes). The variant detail (mustard mix vs. salad mix vs. kale) lives in `crop_varieties`, not in the baseline `crops` table. This creates a new duplicate-target group of 3 keys (`עלי בייבי`) while collapsing the existing 2-key group `תערובת סלט` and shrinking the 2-key group `קייל` to 1.

### §1.2 Tomato sub-species split

| Key | Before | After |
|-----|--------|-------|
| `Greenhouse Cherry Tomato` | `"עגבנייה"` | **`"עגבניית שרי"`** |
| `Greenhouse Heirloom Tomato` | `"עגבנייה"` | **`"עגבניות מורשת"`** |
| `Roma Tomato` | `"עגבנייה"` | `"עגבנייה"` (unchanged — cultivar of עגבנייה) |
| `Tomatoes` | `"עגבנייה"` | `"עגבנייה"` (unchanged) |

**Rationale:** Cherry and Heirloom tomatoes are commercially distinct produce categories in Israel even though botanically they are cultivars of *Solanum lycopersicum*. Cherry is treated as a separate growth and gets its own baseline name_he. Heirloom (מורשת) is similarly distinct enough to merit its own name_he — though it's conceptually a cultivar concept, the heritage-variety marketing requires the separate label. Roma is a true cultivar with no distinct Hebrew name — stays grouped under "עגבנייה" with the baseline `Tomatoes` entry.

### §1.3 Other baseline splits (3)

| Key | Before | After |
|-----|--------|-------|
| `Greenhouse Libanese Cucumber` | `"מלפפון"` | **`"מלפפון חממה"`** |
| `Chinese Cabbage` | `"כרוב"` | **`"כרוב סיני"`** |
| `Hot Pepper` | `"פלפל"` | **`"פלפל חריף"`** |

**Rationale:** Libanese (sic — source typo preserved as JMF_CROP_MAP key) cucumber and Chinese cabbage are commercially distinct in Israel (separate produce categories with distinct shopping behavior). Hot pepper is botanically a different species (*Capsicum chinense* / *C. frutescens* vs *C. annuum*) and culinarily distinct from sweet bell peppers.

### §1.4 Hebrew refinements (4)

| Key | Before | After |
|-----|--------|-------|
| `Beans (Bush)` | `"שעועית"` | **`"שעועית שיחית"`** |
| `Snow Peas` | `"אפונת שלגים"` | **`"אפונת שלג"`** |
| `Basil` | `"בזיל"` | **`"בזיליקום"`** |

**Rationale:**
- `שעועית שיחית` is the precise Israeli agronomic term for bush beans (vs. climbing — `שעועית מטפסת`).
- `אפונת שלג` is the standard singular form; `שלגים` (plural) was incorrect.
- `בזיליקום` is the standard Israeli Hebrew name; `בזיל` was an English-influenced transliteration.

## §2. Status-quo confirmations (no action needed)

These items in the team_00 review were observations that the existing map already handles correctly:

| Item | Status quo | Confirmed |
|------|-----------|-----------|
| `Salanova Lettuce` → `"חסה"` | Cultivar of חסה; variety detail in `crop_varieties` | ✓ |
| `Mini Celery Root` → `"סלרי שורש"` | Cultivar of סלרי שורש | ✓ |
| `Mini Fennel` → `"שומר"` | Cultivar of שומר | ✓ |
| `Tomatillos` → `"תומאטיו"` | Confirmed; cross-link to עגבנייה family via `crops.family`/`genus` field (out-of-scope for JMF_CROP_MAP) | ✓ |
| `NZ Spinach` → `"תרד ניו-זילנד"` | Already correctly maps the Israeli summer-spinach concept | ✓ |
| `Summer Cabbage`, `Savoy Cabbage`, `Fall Cabbage` → `"כרוב"` | Cultivars of כרוב; stay grouped | ✓ |

## §3. Effect on duplicate-target allowlist

Current 25-group allowlist → projected **24-group** allowlist after patch03:

| Change | Detail |
|--------|--------|
| `תערובת סלט` group | **DISAPPEARS** (Mesclun + Salad Mix both leave for "עלי בייבי") |
| `קייל` group | **DISAPPEARS** (Baby kale leaves; Kale alone) |
| `עלי בייבי` group | **NEW** — 3 keys (Mesclun, Salad Mix, Baby kale) |
| `כרוב` group | shrinks 5 → 4 (Chinese Cabbage leaves) |
| `עגבנייה` group | shrinks 4 → 2 (Cherry + Heirloom leave; Roma + Tomatoes stay) |
| `פלפל` group | shrinks 3 → 2 (Hot Pepper leaves) |
| `מלפפון` group | shrinks 3 → 2 (Libanese key leaves) |
| 18 other groups | unchanged |

**Net:** 25 − 2 + 1 = **24 groups.**

## §4. LOD500_LOCKED scope exception authorization

This patch requires modifying **four** LOD500_LOCKED test functions across two files (extended in-session 2026-05-25 after Sonnet builder STOP at AC-18 surfaced the second file):

**File 1 — `tests/crop_book/test_jmf_crop_map.py`** (original DECISION scope):
- `test_jmf_crop_map_duplicate_target_allowlist` — update the 25-group dict literal to the new 24-group dict.
- `test_ac03_duplicate_group_count` — change the constant `25` to `24`.

**File 2 — `tests/crop_book/test_jmf_crop_map_aliases.py`** (added 2026-05-25 amendment):
- `test_alias_spot_check_five_samples` (line 20): update the spot-check entry `"Greenhouse Cherry Tomato": "עגבנייה"` → `"עגבניית שרי"` to reflect patch03 §1.2 Cherry split.
- `test_hebrew_value_collision_set_has_25_pairs` — change the constant `25` to `24` AND rename the function to `test_hebrew_value_collision_set_has_24_groups` (or update docstring + assertion message to say 24). The 3rd function in this file (`test_alias_entry_count_grew_by_34`) is NOT modified — `len(JMF_CROP_MAP)` remains 86.

team_00 authorizes a **narrowly-scoped LOD500_LOCKED exception** limited to these 4 test functions for the purpose of regression-allowlist alignment. The exception is NOT a hub-level GCR; it is a project-internal scope exception following the pattern established at patch01 (constants.py value edits) and B3 (crop_task_templates.py TASK_TYPE_VALUES append).

## §5. Builder engine

Effort is MEDIUM (11 value changes + 2 LOD500_LOCKED test updates + new baseline crops + ~11 new regression tests). **Sub-agent build required** — single-engine builder pattern (used in patch02) does NOT apply. team_110 spawns a Sonnet sub-agent (team_10) for the build per LOD200 §10 standard pattern. IR#1 separation orchestrator-vs-builder restored.

## §6. Sequencing

patch03 is authorized to begin spec drafting (LOD200 + LOD400) immediately after patch02 LOD500_LOCK. Builder dispatch follows team_190 L-GATE_S verdict.

## §7. NotebookLM dependency

patch03 is INDEPENDENT of the NotebookLM JMF extraction work. The 11 value changes are pure constants.py edits + test updates; they do not require JMF NI cache content. patch03 can proceed in parallel with NotebookLM processing.

## §8. Production DB consequences (operational follow-up)

The 11 value changes will likely create old-value orphan rows in production Postgres if `seed.py --all` has already been run. Operational data-fix SQL is OUT-OF-SCOPE for the patch03 spec; team_00 to run post-merge if needed:

```sql
-- Sample (verify scope before running):
UPDATE crops SET name_he = 'עלי בייבי' WHERE name_he IN ('תערובת סלט', 'קייל') AND id IN (...);
UPDATE crops SET name_he = 'עגבניית שרי' WHERE id = ... AND english_name = 'Greenhouse Cherry Tomato';
-- ... etc.
```

A full operational data-fix script may be drafted post-build as a separate deliverable (NOT a code-modifying patch).

---

*DECISION recorded 2026-05-25 by team_110 transcribing team_00 in-session directives. Authorization basis: team_00 explicit message 2026-05-25 listing the 18 items + clarification Q&A confirming Tomato/Cabbage/עלי בייבי architectural model.*
