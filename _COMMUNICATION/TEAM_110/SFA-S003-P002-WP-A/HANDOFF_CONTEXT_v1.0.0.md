---
id: HANDOFF_CONTEXT_SFA-S003-P002-WP-A_v1.0.0
type: HANDOFF_CONTEXT
gate: GATE_1 (architecture spec authoring) → GATE_2 (architecture approval)
from: team_100 (smallfarmsagents Chief Architect)
to: team_110 (AOS Domain Architect)
date: 2026-05-23
project: smallfarmsagents
wp: SFA-S003-P002-WP-A
program: SFA-S003-P002 (Crop Book Enrichment & Consolidation)
mandate_branch: claude/gallant-elbakyan-727a60
team_00_directive: "Enrich crop book with multi-source data + validate weight/trust policy per data type, before advancing to S004 calculator."
next_step: "team_110 to author LOD200 architecture spec defining: (1) source taxonomy + canonical schema fields per source; (2) ingestion pipeline per source class; (3) weight/trust policy framework with reconciliation rules; (4) reconciler architecture; (5) quality gates / acceptance criteria. Then advance to LOD400 with detailed AC matrix. Hand back to team_100 at GATE_2 PASS for builder dispatch."
handoff_to: team_110
handoff_context_pointer: _COMMUNICATION/TEAM_110/SFA-S003-P002-WP-A/HANDOFF_CONTEXT_v1.0.0.md
---

# Handoff Context — SFA-S003-P002-WP-A — Crop Book Data Enrichment Architecture

## §1 Purpose of this handoff

team_00 (Principal) opened a follow-up program SFA-S003-P002 to **enrich and refine** the crop book before advancing to the calculator milestone (S004). WP-A is the data-enrichment leg of that program.

**Your role (team_110, AOS Domain Architect):** author the LOD200 architecture spec for multi-source data enrichment of the existing crop book, including a weight/trust policy framework that ensures the data the user sees on `https://www.nimrod.bio/crop-book/` has principled source provenance and merge semantics.

This is NOT an implementation WP. You produce the spec; team_10 (sfa_build) implements after GATE_2 PASS.

## §2 What already exists (the baseline you must understand before designing)

### §2.1 The crop book module — production state

- **Live URL:** https://www.nimrod.bio/crop-book/ (uPress WordPress, `[sfagent_crop_book]` shortcode + SPA)
- **DB:** PostgreSQL (alembic head=040), 52 crops + 242 varieties seeded
- **Code surface:**
  - `organic_market_agent/crop_book/models.py` (LOD500_LOCKED) — 6 ORM tables
  - `organic_market_agent/crop_book/views.py` (LOD500_LOCKED) — Flask admin `/crop-book/` (3 routes, 8 detail tabs)
  - `organic_market_agent/crop_book/publisher/engine.py` (LOD500_LOCKED) — SPA publisher
  - `organic_market_agent/crop_book/importer/{tend,jmf,reconciler,seed}.py` (LOD500_LOCKED) — current importer chain
- **Tests:** 115 passing (`tests/crop_book/`)
- **Production validated:** team_190 L-GATE_V PASS on WP002 (DB+seed), WP003 (Flask UI), WP004 (WP integration), WP003-patch02 (test harness)

### §2.2 Current schema (the 6 tables — full canonical definitions in models.py)

| Table | Purpose | Key fields |
|-------|---------|-----------|
| `crop_families` | Botanical family taxonomy | `id`, `scientific_name`, `name_he` |
| `crops` | Crop entity (52 rows) | `id`, `name_he`, `name_en`, `scientific_name`, `family_id`, `category`, `growth_cycle`, `harvest_unit_default`, `description`, `oma_product_id` (FK to existing market) |
| `crop_varieties` | Variety per crop (242 rows) | 38 columns; `is_default`, `planting_method`, `days_to_maturity`, `harvest_window_min/max_days`, `in_row_spacing_cm`, `rows_per_bed`, `planting_season`, `documented_price`, `avg_yield_per_bed_m`, `pricebook_product_id`, seeder details, notes |
| `crop_variety_source_values` | **AUDIT TRAIL — per-field per-source values** | `variety_id`, `field_name` (English DB column name), `source` (e.g. "Tend 2022", "JMF", "team_00_override"), `value_text`, `value_numeric`, `unit`, `note` |
| `crop_conversion_groups` | Unit conversion groupings (e.g. baby_leaves) | `id`, `name`, `description` |
| `crop_unit_conversions` | kg ↔ bunch / case / unit per group OR crop | mutual-exclusion CHECK on (`conversion_group_id` XOR `crop_id`) |

### §2.3 Critical: the source_values table IS the source provenance infrastructure

`crop_variety_source_values` already exists and is the canonical audit trail for "which value came from which source per field per variety". Today it stores Tend + JMF + team_00 overrides. **WP-A extends THIS, not replaces it.** The current reconciler (`importer/reconciler.py`) implements a "winning source" rule per field — your spec must define the new rule set as multi-source enrichment widens the inputs.

### §2.4 Production reads (where data flows out)

- Flask admin `/crop-book/<crop_id>/` → 8-tab UI (varieties, description, economics, care, equipment, sources, timeline, field data)
  - The **"מקורות" tab** explicitly surfaces `sources_by_field` from `crop_variety_source_values`
- Public SPA at `nimrod.bio/crop-book/` → embeds the same DB data as JSON, client-side filtering
- `crop_book/publisher/entity_registry_data.py` — entity tags (pest/disease/equipment/input/technique/crop) embedded in JSON, used for `<span class="etag">` tooltips in descriptions

## §3 Current source landscape (what feeds the crop book today)

| Source | Status | Storage | Notes |
|--------|--------|---------|-------|
| **Tend operational data (2018–2022)** | PARTIALLY INGESTED — 14 tables × 5 years exist on disk at `_COMMUNICATION/TEAM_80/Tend Data/Tend_[YEAR]/` but ONLY current importer reads CROP_PLAN+PRODUCT_SOLD+HARVESTS subset for crop_book seed. See `_COMMUNICATION/TEAM_100/SFA-S003-DISCOVERY-SUMMARY_2026-05-07_v1.0.0.md` for full inventory. | CSV (raw_material — read-only per Iron Rule guardrails) | Already validated; ~2,600 planting records across 5 years; ~3,000 harvest events; longitudinal yield data possible |
| **JMF (MasterClass) XLSX** | PARTIALLY INGESTED — `crop_book/importer/jmf.py` reads price/yield benchmarks per crop | XLSX at `/Users/nimrod/Documents/Market Gardening/MasterClass/Crops Data/` | External published benchmarks |
| **team_00 manual overrides** | INTEGRATED — `constants.py::TEAM00_DTM_OVERRIDES` etc. | Python dict literals | High-trust corrections by Principal |
| **Market index (OrganicMarketAgent)** | LINKED — `crops.oma_product_id` FK to existing market-domain products. crop_book reads market prices from the OMA pipeline | PostgreSQL `products` + `ingestion_runs` tables (same DB) | Live community-sourced price feed; crop_book displays `documented_price` (historical) + currently has placeholder market-price card |
| **Web sources** | NOT YET INGESTED — placeholder for WP-A | — | team_00 will name specific sources; some discovery work expected from team_110 |

## §4 The data-weight problem — what team_00 wants you to solve

team_00's directive: *"include validation that the weight we give each data type is correct."*

**Current behavior** (per `importer/reconciler.py`): a single "winning source" per field, with priority order defined ad-hoc per field. Example: `documented_price` prefers Tend > JMF > default; `days_to_maturity` prefers TEAM00_OVERRIDES > Tend > JMF.

**Problem space team_110 must address:**

1. **Source taxonomy** — formal classes of source (e.g. operational/empirical, academic/published, community/curated, principal/override, web/scraped), each with default trust tier
2. **Per-field weighting policy** — does the weight depend on the FIELD (e.g. price = community-curated > operational > academic; yield = operational > academic > community), or on the SOURCE alone? Probably both.
3. **Reconciliation rules** — when sources disagree, what's the canonical resolution?
   - Single-winner (current)
   - Weighted average (where numeric and sensible)
   - Confidence interval / range surfacing (e.g. "DTM: 60-72 days, median 65")
   - Manual review queue (for high-disagreement cases)
4. **Quality gates** — what's the AC matrix that proves the policy is "right"?
   - Backtesting against team_00 overrides (treat overrides as ground truth, score reconciler accuracy)
   - Source-coverage metrics (% of fields with ≥2 sources)
   - Confidence audit visible in UI (the "sources" tab already shows raw — extend with quality signal)
5. **UI surfacing** — currently the 8-tab "מקורות" tab shows sources per field; how does the new policy show *confidence* not just *presence*?

## §5 Base-layer data sources map (what team_00 will or may add)

These are the families of source team_110 should design for. team_00 will name specific sources later; the architecture must be source-extensible.

| Class | Examples (illustrative, not committed) | Trust tier hint |
|-------|---------------------------------------|-----------------|
| Principal override | team_00 manual corrections | HIGHEST |
| Operational empirical | Tend (own farm history), partner farms exports, MyPIPS scrapers' sales data | HIGH for fields they observe |
| Academic / institutional | Volcani / משרד החקלאות / extension service / university research | HIGH for crop-biology fields, MEDIUM for prices |
| Community curated | nimrod.bio community submissions (future), forum discussions | MEDIUM with moderation |
| Commercial published | MasterClass / JMF / books / paid databases | MEDIUM-HIGH for production benchmarks |
| Web scraped | seed catalogs (Hazera, Genesis, Hishtil), suppliers' product pages, government databases | LOW-MEDIUM depending on site |
| Internal heuristics | reconciler defaults, fallbacks | LOWEST |

team_110 should:
- propose a canonical field for "source_class" on each `crop_variety_source_values` row (currently only the free-text `source` field exists)
- propose a `crop_source_registry` table OR a Python registry that maps `source` strings → source_class + default trust tier + URL/reference

## §6 Constraints + invariants

### Iron Rules (binding)
1. **#1 Cross-engine:** your spec will be validated by team_190 (non-Claude). You're on Cursor Composer per your governance — compliant.
2. **#4 Single roadmap writer:** team_100 owns `_aos/roadmap.yaml`. Your spec lives in `_aos/work_packages/S003/SFA-S003-P002-WP-A/`. You author LOD200/LOD400 there; team_100 records gate transitions in roadmap.
3. **#5 Final validation owned by team_190.**
4. **#6 Inter-team comms via canonical artifact in `_COMMUNICATION/`.**

### LOD500_LOCKED constraints
- `crop_book/models.py` — extending OK (additive migrations 041+); modifying existing columns NOT OK without GCR
- `crop_book/views.py` — read-only views; the "מקורות" tab is the canonical render of source provenance; extending the rendering is OK if backward-compatible
- `crop_book/publisher/*` — engine + entity_registry + templates LOD500_LOCKED; new data shapes need to be additive in `sfagent-crop-book-data.json` schema
- The existing 115 tests must continue to pass; new tests are encouraged

### Raw material guard (per Iron Rule + repo CLAUDE.md)
Tend exports + MasterClass + other source files at their `/Users/nimrod/Documents/.../` paths are **READ-ONLY**. Importers may not write/move/delete source files.

### Data weight policy itself MUST be testable
team_00 specifically said "include validation that the weight is correct". The spec MUST define how to measure the policy's correctness — likely a backtesting harness against team_00 overrides as ground truth, with target metrics (e.g. ≥80% reconciler agreement with team_00 on overlap fields).

## §7 Deliverables expected from team_110

### Phase 1 (GATE_1 / LOD200) — Architecture
- Source taxonomy (formal class list + trust-tier defaults)
- Schema deltas (proposed columns on `crop_variety_source_values`, new tables, registries)
- Reconciler architecture (single-winner vs weighted vs range — possibly mixed per field)
- Validation harness design (backtesting framework + metrics)
- UI surfacing strategy (how the public crop book communicates confidence)
- Effort estimate (the WP currently has `effort: TBD`)

### Phase 2 (GATE_2 PASS) → LOD400 — Detailed implementation spec
- Concrete migration sequence (041+)
- New importer modules per source class
- Reconciler implementation contract
- AC matrix (testable acceptance criteria)
- 5-step build sequence with effort estimates per step
- Risk register

### Format for both phases
- LOD200 at `_aos/work_packages/S003/SFA-S003-P002-WP-A/LOD200_spec.md`
- LOD400 at `_aos/work_packages/S003/SFA-S003-P002-WP-A/LOD400_spec.md` (after GATE_1 PASS)
- Bundle to team_190 for L-GATE_S (after LOD400 lock by team_100)

## §8 References (recommended read order)

1. `CLAUDE.md` (project root) — Iron Rules, AOS spoke rules
2. `_aos/governance/team_110.md` — your governance contract
3. `_aos/roadmap.yaml` — confirm WP-A registered (status: ELIGIBLE, current_lean_gate: L-GATE_E)
4. `_aos/work_packages/S003/SFA-S003-P001-WP002/LOD400_spec.md` (LOD500_LOCKED) — DB schema canon for crop_book
5. `_aos/work_packages/S003/SFA-S003-P001-WP003/LOD400_spec.md` (LOD500_LOCKED) — UI canon (8 tabs incl. "מקורות")
6. `_aos/work_packages/S003/SFA-S003-P001-WP004/LOD400_spec.md` (LOD500_LOCKED) — WordPress publisher canon
7. `_COMMUNICATION/TEAM_100/SFA-S003-DISCOVERY-SUMMARY_2026-05-07_v1.0.0.md` — full Tend + MasterClass inventory + raw-material guard
8. `organic_market_agent/crop_book/importer/reconciler.py` — current reconciler (the thing your spec will replace/extend)
9. `organic_market_agent/crop_book/importer/seed.py` — current seed-driver invoking the reconciler
10. `_aos/governance/directives/ADR034_DATA_AUTHORITY_DB_SSOT_ALL_PROFILES.md` (snapshot) — data authority canon
11. `_aos/governance/directives/ADR043_TEAM_MESSAGING_PROTOCOL_v1.5.0.md` (snapshot) — inter-team comm

## §9 Working environment

| Item | Value |
|------|-------|
| Recommended worktree | `/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/gallant-elbakyan-727a60` |
| Branch | `claude/gallant-elbakyan-727a60` (current orchestration branch; main HEAD is canonical S003 close commit `d2a61a1`) |
| DB | Online (PostgreSQL 16.13, alembic head=040) — for inspection only; no mutations from spec phase |
| Hub API | http://100.125.98.56:8090 (waldhomeserver Tailscale) — your team_110 key may already be provisioned; check `AOS_ACTOR_API_KEY` env |
| Production site | https://www.nimrod.bio/crop-book/ (HTTP 200 verified pre-merge) |
| `validate_aos.sh` | 0 FAIL expected — run before any commit |

## §10 Routing after your work

- team_110 LOD200 spec → team_00 approval (in-session or via /AOS_decide)
- team_110 LOD400 spec → team_100 packages into L-GATE_S bundle
- team_190 L-GATE_S → team_10 (sfa_build) L-GATE_B → team_190 L-GATE_V → LOD500_LOCKED → team_191 archive
- Final step: team_100 canonical merge (per F-LV-01 §2)

---

*Handoff prepared 2026-05-23 by team_100 (smallfarmsagents).*
*Worktree: `gallant-elbakyan-727a60` · Branch: `claude/gallant-elbakyan-727a60`*
