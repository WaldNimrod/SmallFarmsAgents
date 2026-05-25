---
id: DECISION_WP-B1-patch04-patch06_INTEGRATION-CLEANUP_2026-05-25_v1.0.0
from: team_00 (Principal — in-session, recorded by team_110)
to: [team_110, team_190, team_100]
date: 2026-05-25
type: DECISION
scope: SFA-S003-P002-WP-B1-patch04 (integration) + SFA-S003-P002-WP-B1-patch06 (cleanup) — opened in parallel
status: AUTHORIZED
parent_decisions:
  - _COMMUNICATION/team_00/DECISION_WP-B-OPEN-QUESTIONS_2026-05-25_v1.0.0.md
  - _COMMUNICATION/team_00/DECISION_WP-B1-patch03_TAXONOMY_2026-05-25_v1.0.0.md
nb: "EXECUTION_MANDATE SFA-S003-P002-WP-B extended in-session by team_00 to cover patch04 + patch06 as final follow-ups."
---

# DECISION — patch04 + patch06 (Integration + Cleanup)

## Background

After NotebookLM deliverable (37 MasterClass crop sheets) was received 2026-05-25, team_00 reviewed the full content + the entire `JMF_CROP_MAP` (86 entries post-patch03) and issued the following architectural directives.

## §1. Architectural policy (binding going forward)

### §1.1 JMF_CROP_MAP is a baselines-only lookup

`JMF_CROP_MAP` MUST contain **one entry per botanical baseline crop** (one species/sub-species per row) plus pure-synonym aliases (different English names for the same species). All other variants live in `crop_varieties`:
- **Cultivars** (e.g., Bell Pepper, Salanova Lettuce, Roma Tomato, Hakurei Turnip, Storage Onion)
- **Size variants** (Mini Fennel, Baby kale)
- **Season qualifiers** (Fall Cabbage, Summer Cabbage, Winter Radish, Leek Storage)
- **Cultivation-method qualifiers** (Greenhouse English Cucumber, Greenhouse Pepper, Greenhouse Beefsteak Tomato)
- **Marketing qualifiers** (Fresh Carrots, Storage Carrots)

### §1.2 Greenhouse is NEVER a separate baseline

Cultivation method (greenhouse / open field) is a **variety-level attribute**, not a species distinction. This means:
- Future crops surfaced from MasterClass (Greenhouse Pepper, Greenhouse Beefsteak Tomato) → cultivars under existing baselines.
- **patch03 §1.3 anomaly** — `Greenhouse Libanese Cucumber → מלפפון חממה` violates this policy. **REVERT in patch06** to `→ מלפפון`; "Libanese" + "greenhouse" stored as variety attributes.

### §1.3 The 86-entry categorization (approved)

Of the current 86 entries in JMF_CROP_MAP:
- **53 baselines (A)** — stay as-is.
- **6 synonyms (B)** — stay as aliases (Coriander, Green Onion, Pak Choi, Potato, Swiss Chard, Watermelon).
- **22 cultivars masquerading (C)** — move to `crop_varieties`, remove from MAP.
- **5 workbook typos (D)** — delete entirely.

Final MAP size after patch06: **59 entries** (53 baselines + 6 synonyms). Plus `+1 Ginger → ג'ינג'ר` from patch04 = **60 entries**.

Full row-by-row table approved 2026-05-25 by team_00. Reproducible via the categorization script committed alongside this DECISION.

## §2. patch04 scope (Integration WP — LARGE)

### §2.1 OP-01: NotebookLM MD → JSON cache → DB
Convert the 37 MasterClass crop-sheet MDs (`documentation/jmf_masterclass_crop_sheets/*.md`) into structured JSON per the WP-B2 NIImporter cache schema. Land at `data/jmf/extracted/jmf_book/<crop>.json`. Then `seed.py --ni-only` populates `crop_knowledge_notes`. Expected: 200-400 note rows.

### §2.2 OP-02: Production DB data-fix
`scripts/patch03_data_fix.py` — automated, idempotent script that runs the 11 `UPDATE crops SET name_he = ...` for patch03's Hebrew terminology corrections. Includes `--dry-run` flag. **No more manual SQL.**

### §2.3 OP-03: `crop_varieties` population from MasterClass cultivar lists
Each MD's "CULTIVARS" section enumerates specific varieties (Marnero, Marbonne, etc. for Tomatoes). Parse + insert ~150-200 variety rows tied to the baseline `crop_id`. Include Greenhouse / Season / Storage qualifiers as variety attributes.

### §2.4 OP-04 (new): Sheet 056 cross-crop knowledge
Sheet 056 ("איחסון ושטיפה" — storage + washing itinerary) is operational guidance applicable to multiple crops. Schema requires a **many-to-many** link.

**Schema decision: Junction table** (Migration 047). Junction `crop_knowledge_notes_crops` with FK to `crop_knowledge_notes` + FK to `crops`, cascading delete. Rationale matrix (junction vs JSONB) — approved 2026-05-25:
- FK integrity preserved
- Standard SQLAlchemy `relationship(secondary=...)` pattern (precedent in repo)
- Future per-link metadata possible
- Migration cost marginal (already adding NotebookLM cache + variety rows)

### §2.5 New baseline: Ginger
+1 row in JMF_CROP_MAP: `"Ginger": "ג'ינג'ר"`. cultivar "Baby Ginger" stored in `crop_varieties`. crops row created lazily.

### §2.6 patch04 does NOT modify
- The 22 cultivar entries in JMF_CROP_MAP (deferred to patch06)
- The 5 typo entries (deferred to patch06)
- LOCKED tests `test_jmf_crop_map_duplicate_target_allowlist` / `test_ac03_duplicate_group_count` (still asserting 24 groups; patch06 changes them)

## §3. patch06 scope (Cleanup WP — MEDIUM)

### §3.1 Remove from JMF_CROP_MAP (27 entries)
- 22 cultivars (C category)
- 5 typos (D category)

Net: 86 + 1 (Ginger from patch04) − 27 = **60 entries** final.

### §3.2 Revert patch03's `מלפפון חממה`
`Greenhouse Libanese Cucumber` removed from MAP (per §3.1 — it's in category C). Existing patch03 `מלפפון חממה` value is no longer referenced.

### §3.3 Update LOCKED tests
- `test_jmf_crop_map_duplicate_target_allowlist` — 24 groups → ~3 groups (just the 3 synonyms that have multiple keys: Carrots/Fresh Carrots is removed so גזר shrinks to 1; etc. — patch06 LOD400 will compute exactly)
- `test_ac03_duplicate_group_count` — 24 → expected_new_count
- `test_jmf_crop_map_aliases.py` tests — likely need full update or removal (allowlist + count + spot-check all violated)

LOD500_LOCKED scope exception authorized for these test files + any other test that asserts the post-patch03 state directly.

### §3.4 `crop_knowledge_notes` notes that referenced removed keys
patch04 populates notes under baseline `crop_id`s (e.g., notes from "Roma Tomato" MD attach to crop_id of Tomatoes via Roma's `crop_varieties.crop_id`). No data-loss in patch06.

### §3.5 `crops` table — handle orphans
If patch04's lazy crop-creation produced rows like `crops` with `name_he='מלפפון חממה'` (from patch03), patch06's data-fix updates/merges these.

## §4. Sequencing constraint

patch06 BUILD depends on patch04 BUILD. Reason: patch06 removes JMF_CROP_MAP entries that patch04 needs to look up while parsing MD sheets (e.g., the "Roma Tomato" MD needs the "Roma Tomato" key to find its parent crop_id during cultivar insertion). After patch04's varieties are populated, the lookup chain no longer needs the cultivar-keys in JMF_CROP_MAP.

**Specs (LOD200 + LOD400) for both can be authored + L-GATE_S validated in parallel.** Build sequencing: patch04 builds first → patch04 LOD500_LOCKED → patch06 builds.

## §5. EXECUTION_MANDATE extension

team_00 authorizes extension of EXECUTION_MANDATE SFA-S003-P002-WP-B to cover patch04 + patch06 as the final follow-ups. Mandate naturally ends after patch06 LOD500_LOCKED.

## §6. NotebookLM licensing posture (carry-forward)

All `crop_knowledge_notes` rows populated by patch04 inherit the WP-B2 §3.1 fair-use invariant: internal-farm-use only, `body_text` ≤ 2000 chars, `is_internal_farm_use_only=true`. patch04 LOD400 §X must include this AC.

---

*DECISION recorded 2026-05-25 by team_110 transcribing team_00 in-session directives. All decisions captured via AskUserQuestion responses + the row-by-row categorization table approved verbatim.*
