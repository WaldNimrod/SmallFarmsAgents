---
id: SFA-S003-P002-WP-B2-LOD200
wp: SFA-S003-P002-WP-B2 — JMF PDF NI Extraction Layer (AI-assisted)
gate: L-GATE_S (LOD200 — architecture spec)
status: PRE_LOD400
author: team_110 (execution mandate per ADR045)
date: 2026-05-25
version: v1.0.0
lod200_supersedes: PLACEHOLDER_PENDING_TEAM_110 (committed in f61c1da)
program_brief_ref: _COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B/PROGRAM_BRIEF_v1.0.0.md
execution_mandate_ref: _COMMUNICATION/TEAM_110/SFA-S003-P002-WP-B/EXECUTION_MANDATE_v1.0.0.md
parent_wp_chain:
  - SFA-S003-P002-WP-A (engine SSoT — LOD500_LOCKED at 594cbc8)
  - SFA-S003-P002-WP-B1 (crops + JMF_CROP_MAP — LOD500_LOCKED at 6a85561)
  - SFA-S003-P002-WP-B1-patch01 (extended JMF_CROP_MAP — LOD500_LOCKED at 3e1f946)
depends_on: [SFA-S003-P002-WP-B1-patch01, SFA-S003-P002-WP-B1, SFA-S003-P002-WP-A]
validator: team_190 (non-Claude, Iron Rule #1)
builder: sfa_build (separate session per IR#1)
---

# LOD200 — SFA-S003-P002-WP-B2: JMF PDF NI Extraction Layer

## 1. Mission

Extract per-crop narrative knowledge from the JMF MasterClass PDF library
into the structured DB, as the **first concrete `NIImporter` subclass**
materializing the WP-A skeleton. NI (Nimrod-Input) is a **hard-override**
trust tier — NI values win over JMF PR (B1) and Tend OP (B3) blends.

Sources processed (all under `/Users/nimrod/Documents/old Mac BackUpp/Market Gardening/MasterClass/`):

- **`THEMARKETGARDENEREBOOK.PDF`** (240 pages) — per-crop chapters with narrative on pest/disease, harvest markers, storage, rotation, cultivar recommendations
- **`FT_FINALE_FLAMEWEEDING*.PDF`** (3 pages) — flame-weed timing per crop
- **`FT_FINALE_TABLEAUAPPLICATIONBIOPESTICIPE*.PDF`** (5 pages) — biopesticide application table (structured per crop)

(The 209-page alternate edition, the 3-page phytoprotection PDF, and the
13-page nursery seeding PDF are out-of-scope for B2 — see §3.)

Extraction is a **one-time prepare step**, not runtime: `pdftotext` →
LLM-assisted chunking + structured extraction → JSON cache →
deterministic DB upsert by importer. The runtime importer reads only the
cached JSON, never the PDFs directly.

## 2. In-scope

- **Migration 045** — new table `crop_knowledge_notes` (per-crop narrative, type-classified)
- **New ORM module** `organic_market_agent/crop_book/crop_knowledge_notes.py` (separate from `models.py` per WP-A/B1 precedent)
- **NIImporter subclass framework** — 3 concrete subclasses:
  - `ni/jmf_book.py` (Market Gardener ebook — primary content)
  - `ni/jmf_ft_flameweed.py` (FT_FLAMEWEEDING PDF)
  - `ni/jmf_ft_biopesticide.py` (FT_TABLEAUAPPLICATIONBIOPESTICIPE PDF)
- **LLM-assisted extraction harness** — Anthropic API (Claude) chunking + structured JSON output, with caching to `data/jmf/extracted/`
- **Cache governance** — `data/jmf/extracted/` strategy (committed-vs-gitignored decision; advisory #2 disposition; see §11)
- **Licensing language** — explicit `internal_farm_use_only` flag and copyright provenance in every NI row (advisory #1 disposition)
- **CLI integration:** `seed.py --ni-only`, `--no-ni`; `--all` invokes NI ingestion after B1 JMF + B3 Tend (NI hard-override comes last)
- **Tests** ≥15 (parser tests + LLM-stub tests + DB integration + cache schema + per-FT-PDF coverage)
- **WP-A engine reuse only** — NI rows go through the same `_upsert_source_value` contract as B1, with `trust_tier='NI'`, `confidence_weight=NULL`, `is_hard_override=True`

## 3. Out-of-scope

- **Alternate-edition ebook** (`THE MARKET GARDENER_*.PDF`, 209 pages) — same content as the 240-page edition; risk of double-extraction noise. Use the 240-page canonical edition only.
- **`FT_FINALE_PHYTOPROTECTION*.PDF`** (3 pages) — overlaps with biopesticide PDF; integrate later if biopesticide proves insufficient.
- **`FT_FINALE_NURSERYSEEDING*.PDF`** (13 pages) — overlaps with B1 CROP CHART + NURSERY CHART; defer.
- **Re-extraction at runtime** — out of scope and forbidden. The runtime importer ONLY reads cached JSON.
- **No edits to LOD500_LOCKED files** (see §9).
- **`crop_varieties.notes` enrichment** — out-of-scope; B2 introduces a NEW per-crop table.
- **Publication of extracted narrative prose** — out-of-scope per advisory #1 (internal farm-use only).

## 4. Data sources

| File | Pages | Content type | Extraction strategy |
|------|-------|--------------|----------------------|
| `THEMARKETGARDENEREBOOK (from macBook Air - nimrod).PDF` | 240 | Per-crop chapters | chapter-locate heuristic + LLM extract 5 note-types per crop |
| `FT_FINALE_FLAMEWEEDING*.PDF` | 3 | Flame-weed timing per crop | structured table parse + LLM verify |
| `FT_FINALE_TABLEAUAPPLICATIONBIOPESTICIPE*.PDF` | 5 | Biopesticide application table | structured table parse + LLM verify |

All paths confirmed on disk by PROGRAM_BRIEF §1 + team_190 PRE_HANDOFF VERDICT R1.

## 5. Data model summary

### 5.1 New table — `crop_knowledge_notes` (migration 045)

| Column | Type | Notes |
|--------|------|-------|
| `id` | `BIGSERIAL` PK | autoincrement; SQLite variant `Integer` |
| `crop_id` | `BIGINT` FK → `crops.id` ON DELETE CASCADE | not null |
| `source` | `VARCHAR(50)` | e.g. `'NI:jmf_book_v1'`, `'NI:jmf_ft_flameweed_v1'` |
| `trust_tier` | `VARCHAR(20)` | always `'NI'` for this table |
| `note_type` | `VARCHAR(40)` | enum, CHECK constraint |
| `body_text` | `TEXT` | extracted prose snippet — bounded length (see §5.4) |
| `provenance_pdf` | `VARCHAR(200)` | filename of source PDF (audit + licensing) |
| `provenance_pages` | `VARCHAR(40)` | e.g. `"42-45"` |
| `is_internal_farm_use_only` | `BOOLEAN` default `TRUE` | per advisory #1 |
| `extraction_model` | `VARCHAR(50)` | e.g. `'claude-sonnet-4.6'` (audit) |
| `extracted_at` | `TIMESTAMP` | when the cache JSON was produced |
| `created_at` | `TIMESTAMP` default `now()` | when this row was upserted |
| `UNIQUE(crop_id, source, note_type)` | idempotency key |
| `idx_ckn_crop(crop_id)`, `idx_ckn_type(note_type)` |

### 5.2 `note_type` enum (CHECK constraint values)

`pest_disease`, `harvest_marker`, `storage_handling`, `rotation_companion`,
`cultivar_recommendation`, `growing_tip`, `irrigation`, `nursery_specific`,
`flame_weed_timing`, `biopesticide_spray`

10 values. First 8 from the JMF book; last 2 from FT PDFs.

### 5.3 No `Crop` back-reference (no GCR)

Like B1's `crop_task_templates`, queried explicitly via `session.query(...)` — no `Crop.knowledge_notes` relationship added to `models.py`. If ever needed, file GCR-B2-1.

### 5.4 Body text length

`body_text` is bounded: ≤ 2000 characters per row (4-5 sentences). Keeps extracted prose well within fair-use snippet length (advisory #1).

## 6. Trust-layer placement

| Field | Value |
|-------|-------|
| `source` | `'NI:<source_name>'` |
| `trust_tier` | `'NI'` |
| `confidence_weight` | `NULL` (hard override) |
| `is_hard_override` | `True` (via `SOURCE_REGISTRY` prefix-match — already supported by WP-A) |

NI knowledge notes are authoritative for `(crop_id, note_type)`. They don't compete with PR/OP because those tiers carry scalar field values, while NI carries narrative notes (different tables, different UI surfaces).

**Exception:** NI may also write to `crop_variety_source_values` for the field `cultivar_recommendation` (when the ebook recommends a specific cultivar by name). Normal hard-override path applies.

## 7. Engine + cache architecture diagram

```
JMF PDFs (3 files)
   │
   ▼
pdftotext  (one-time, manual)
   │
   ▼
extraction_runner.py  (one-time, manual; calls Anthropic API)
   │   per crop_chapter or per FT row:
   │     LLM(text_chunk) → structured JSON dict
   │
   ▼
data/jmf/extracted/<source_name>/<crop_name_en>.json
   │  (reviewable; commit policy decided in §11)
   │
   ▼
ni/<source>.py  (runtime importer subclass)
   │   reads cached JSON; upserts to DB
   │
   ▼
crop_knowledge_notes  (per-crop narrative)
crop_variety_source_values  (cultivar recommendations only)
```

**Runtime path NEVER touches PDFs.**

## 8. Dependencies

### 8.1 Direct

- **WP-B1-patch01** (LOD500_LOCKED at `3e1f946`) — supplies extended `JMF_CROP_MAP` (86 entries) for crop-name resolution from ebook ToC / chapter headings.
- **WP-B1** (LOD500_LOCKED at `6a85561`) — supplies the importer pattern for variety resolution (`_default_variety_id`, `_upsert_source_value`).
- **WP-A** (LOD500_LOCKED at `594cbc8`) — supplies:
  - `source_registry.py::SOURCE_REGISTRY` — NI prefix-match already supported
  - `ni_importer.py::NiSourceBase` — the abstract class B2 subclasses
  - `_upsert_source_value` semantics (for `cultivar_recommendation` field)

### 8.2 External

- Python: `pdftotext` (system binary)
- Anthropic SDK: `anthropic >= 0.45` (verify in requirements.txt; add if needed)
- ANTHROPIC_API_KEY available in extraction-runner env (NOT runtime)

### 8.3 Tooling

- Builder engine: any non-team_190 engine (sfa_build sub-agent, recommended Claude Sonnet)
- Validator: team_190 (GPT-5.5, non-Claude)

## 9. LOD500_LOCKED inventory (unchanged in B2)

All WP-A + WP-B1 + patch01 deliverables remain locked. See LOD400 §14 for the exhaustive 16-path list. Headline items:

- All WP-A engine SSoT modules (source_registry, field_policy, reconciler, enrichment_runner, enrichment_models, models)
- `organic_market_agent/crop_book/importer/tend.py` (raw-material guard)
- `organic_market_agent/crop_book/importer/jmf.py` (legacy stub)
- All B1 + patch01 deliverables (`crop_task_templates.py`, `jmf_masterclass.py`, migration 044, extended `constants.py`, B1 `seed.py` lines)
- `views.py`, `publisher/`, `mu-plugin/`
- Migrations 001..044

**Permitted additive modifications:**
- `organic_market_agent/crop_book/importer/ni_importer.py` — EXTEND only (subclass it; no base changes)
- `organic_market_agent/crop_book/importer/seed.py` — add `--ni-only` + `--no-ni` flags + 1 new call-site block
- `CHANGELOG.md` — `[Unreleased]` entry

## 10. GCR requirements

**None planned for B2.** All additions are pure-additive:
- Migration 045 (NEW table)
- 3 NEW NI importer subclasses
- 1 NEW extraction-runner script (CLI tool, separate from production code)
- Additive `seed.py` CLI flags + 1 new call-site block

If LOD400 review surfaces a hidden need to add a `Crop.knowledge_notes` relationship, file `GCR-B2-1` to team_00 BEFORE locking LOD400.

## 11. PRE_HANDOFF advisory disposition

| # | Advisory | B2 disposition |
|---|---|---|
| 1 | JMF PDF licensing — internal farm-use only | **Addressed in LOD400.** Every NI row carries `is_internal_farm_use_only=TRUE` + `provenance_pdf` + `provenance_pages`. `body_text` bounded to ≤2000 chars (snippet length). Spec adds explicit prose: "Extracted narrative may be displayed to logged-in farm operators ONLY; never to public WordPress visitors". B2 does NOT publish NI prose to WordPress. |
| 2 | LLM extraction cache strategy (`data/jmf/extracted/`) | **Proposal:** the cache directory is **committed** (gitignored: NO), in a reviewable per-crop-per-source JSON structure. Reasoning: (a) reproducibility — same DB without re-paying LLM costs; (b) review — each extraction is code-reviewable; (c) cache invalidation — explicit `extraction_runner --rebuild --crop <name>`. JSON files contain ONLY structured extracted fields, never raw PDF snippets > 2000 chars. *Alternatives considered:* gitignored (rejected — breaks reproducibility); redacted fixtures (rejected — B2 IS the canonical extraction). |
| 3 | Tend task whitelist | **N/A for B2** — Tend handling is WP-B3. |
| 4 | Transitive WP-A dependency | **Addressed** in §8.1 (named WP-A commit + specific surfaces: `SOURCE_REGISTRY`, `ni_importer.py::NiSourceBase`, `_upsert_source_value`). |

## 12. AC and test count targets

- **Acceptance Criteria target:** ≥ 10 ACs in LOD400 (PROGRAM_BRIEF §3.5)
- **Test count target:** ≥ 15 tests, preliminary breakdown:
  - 3× per-FT-PDF parser tests
  - 4× LLM-stub tests for ebook extractor (chapter location, per-note-type extraction, mock-Anthropic, rebuild flag)
  - 3× DB integration on SQLite in-memory (upsert; UNIQUE; idempotent re-import)
  - 2× cache schema tests (JSON shape; reproducibility)
  - 2× CLI behavior (`--ni-only`, `--no-ni`)
  - 1× per-crop spot-check (5 crops manually verified — uses recorded LLM responses)

Final inventory fixed in LOD400 §10.

## 13. Open questions (resolved in LOD400)

1. **Cache commit policy** — propose: committed (§11). LOD400 confirms.
2. **Chapter-locate heuristic** — propose: per-crop heading-pattern matcher with fuzzy fallback. LOD400 specifies.
3. **LLM model + version** — propose: Claude Sonnet 4.6 for extraction. LOD400 confirms + temperature.
4. **`extraction_runner.py` location** — propose: `scripts/extract_jmf_ni.py` (NOT in `organic_market_agent/` — it's a one-time CLI tool). LOD400 confirms.
5. **Display routing for NI notes** — B2 produces DB rows; the views layer (LOD500_LOCKED) does NOT display NI notes yet. Follow-up UI WP will surface them.

## 14. Sequencing

```
WP-B1 + patch01 (LOD500_LOCKED)  ──┐
                                     ├──▶ WP-B2 (this WP)
WP-A (LOD500_LOCKED)  ───────────────┘     and WP-B3 (parallel)
```

B2 and B3 are **parallel-eligible** — no inter-dependency. They share the engine and `JMF_CROP_MAP` but write to different tables.

---

*LOD200 v1.0.0 — authored 2026-05-25 by team_110 under EXECUTION_MANDATE SFA-S003-P002-WP-B (same mandate covers B1, B1-patch01, B2, B3).*
*Next phase: LOD400 spec.*
