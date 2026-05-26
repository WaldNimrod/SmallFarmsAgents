---
id: DECISION_WP-B1-patch07-patch08_2026-05-26_v1.0.0
from: team_00 (Principal — in-session)
to: [team_110, team_190, team_100]
date: 2026-05-26
type: DECISION
scope: SFA-S003-P002-WP-B1-patch07 (sheet 056 M2M data load) + SFA-S003-P002-WP-B1-patch08 (variety-parser cleanup) — opened in parallel
status: AUTHORIZED
trigger: "OP-2 successfully loaded NotebookLM data to production Postgres (62→54 notes, 15 new varieties, 5 new crops, junction still 0). Two follow-ups identified: (1) sheet 056 storage/washing M2M data not loaded (junction empty); (2) variety parser extracted ~11 noise rows (URLs, bullets, section headers) alongside ~4 real cultivars."
---

# DECISION — patch07 + patch08 (open in parallel)

## §1. patch07 scope (M2M sheet 056 data load)

### §1.1 The need
Sheet 056 ("WASHING ITINERARY FOR CROPS IN THE MASTERCLASS") contains storage + handling guidance grouped by procedural category, where each group references multiple crops. Junction table `crop_knowledge_notes_crops` (from Migration 047) is the canonical schema for this M2M relation. Currently empty.

### §1.2 Schema change required
`crop_knowledge_notes.crop_id` is currently `NOT NULL`. M2M-only notes (storage procedure that applies to N crops) cannot fit this constraint. **Migration 048 makes `crop_id` nullable.**

Semantics post-migration:
- `crop_id IS NOT NULL` + junction empty for that note → 1-to-1 (existing pattern)
- `crop_id IS NULL` + junction has rows → pure M2M (new pattern for sheet 056)
- Both NOT NULL + junction rows → hybrid (allowed but discouraged)

### §1.3 Parser scope
- New parser for sheet 056 specifically (structurally different from per-crop sheets)
- Output: per-procedure note + crop linkages via junction
- Expected: ~6-10 procedure notes + ~30-50 junction rows

### §1.4 Builder
Sonnet sub-agent (MEDIUM scope: schema migration + parser + DB writes + tests).

## §2. patch08 scope (variety-parser cleanup)

### §2.1 The defect
`_extract_cultivar_names` in `scripts/load_masterclass_sheets.py` is too permissive. After OP-2, the 15 new variety rows include:
- ~4 real cultivars: Carmen, Ace, Sprinter, Escamillo
- ~11 noise rows: URLs (`marketgardenerinstitute.com`), bullets (`●`), single chars (`1`), section headers (`Intensive Spacing`), spacing instructions, sentence fragments (`food store. Any cultivar works.`)

### §2.2 Fix scope
1. **Filter logic** in `_extract_cultivar_names`:
   - Skip lines containing URLs (`http://`, `://`, `.com`, `.org`)
   - Skip pure-bullet lines (`●`, `-`, `*`, only-numeric strings)
   - Skip lines longer than 50 chars (likely sentences, not cultivar names)
   - Skip lines with `:` followed by space (section headers like "Intensive Spacing:")
   - Skip lines ending with `.` (sentence-like)
   - Accept: short alphanumeric strings (cultivar names usually 1-3 words)
2. **DELETE** the 11+ noise variety rows from production crop_varieties
3. **Re-run OP-2** (idempotent via `_upsert_variety` ON CONFLICT) — won't duplicate real cultivars, won't re-insert noise

### §2.3 Builder
Sonnet sub-agent (MEDIUM scope: filter logic + cleanup script + tests + re-run OP-2 in build verification).

## §3. Sequencing
patch07 + patch08 are **independent** — different code paths (sheet 056 vs cultivar extraction). LOD200 + LOD400 + L-GATE_S can run in parallel. BUILDs can run sequentially or in parallel (no shared LOCKED files except `_aos/roadmap.yaml` lifecycle).

Recommended: patch07 builds first (introduces Migration 048 which patch08 doesn't depend on but is structurally larger), then patch08.

## §4. EXECUTION_MANDATE
team_110 EXECUTION_MANDATE extension continues for both. After patch08 closes, the mandate naturally ends (10 WPs cumulative).

---

*DECISION recorded 2026-05-26. Approved schema choice: nullable crop_id (Migration 048). Approved cleanup choice: DELETE noise + filter. Both WPs opened in parallel.*
