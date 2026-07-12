---
id: BUILD_FEASIBILITY_BLOCKER_SFA-S003-P002-WP-C6_v1.0.0
from: team_100 (Chief Architect — orchestrator)
to: team_00 (Principal)
cc: team_10, team_80
date: 2026-05-28
type: feasibility_assessment
wp: SFA-S003-P002-WP-C6 (Sparse Crops Future Expansion)
verdict: NOT BUILDABLE IN-SESSION — blocked on external inputs
status: REMAINS PROPOSED
---

# WP-C6 build feasibility — blocked on external inputs

During the 5-WP closure batch, team_00 requested a "full build + close now" of
WP-C6. A Sonnet research pass over the crop_book pipeline establishes that
**C6 cannot be built in a Claude Code session** — it is blocked on external
inputs no agent can synthesize locally. The WP remains **PROPOSED** (its own
LOD200 already says "not for execution now").

## Hard blockers
1. **WP-C5 not yet LOD500_LOCKED at assessment time** — now cleared this
   session (C5 Phase A closed). C5 Phase B (team_00 manual) determines the
   final sparse-crop list, so the target set is not yet stable.
2. **No in-repo source data for the ~17 target crops.** No NI importer under
   `organic_market_agent/crop_book/importer/ni/` covers Sage, Thyme, Tarragon,
   Mint, Lemon balm, Oregano, Rosemary, Turmeric, Jerusalem artichoke, Pak choi,
   etc. Existing WR research files (`data/external_sources/web/openai_tier1_research/`,
   `.../gemini_il_research/`) cover common vegetables already ingested by WP-C4.
3. **WR:* synthesis requires external LLM API calls.** Tier-D sources (weight
   0.60) must be generated via team_80 multi-engine scout (OpenAI + Perplexity +
   Gemini); `data/external_sources/web/team80_crop_expansion_16_crops/` holds
   only session ack `.md` files, no structured extract. Needs API budget.

## What IS in place (pipeline mechanics work)
- `enrichment_runner.run_enrichment(session, variety_ids=[...])` — `organic_market_agent/crop_book/importer/enrichment_runner.py`
- Source registry auto-resolves any `WR:<label>` prefix — `organic_market_agent/crop_book/source_registry.py` (no registry change needed)
- `crop_source_weights` table (WP-C5) already carries `WR:*`@0.60 — C6 just adds rows

## Exact build sequence (for when unblocked)
1. WP-C5 Phase B (team_00 manual) complete → data state stable.
2. Author a coverage-count script (does not exist) + run `python scripts/validate_enrichment.py` → final sparse-crop list.
3. Commission team_80 multi-engine WR synthesis per sparse crop → structured JSON to `data/external_sources/web/<crop>_research/extract.json`. **[external API]**
4. Author a new NI/WR importer module mapping each JSON → `CropVarietySourceValue` rows.
5. Seed DB rows (via API — DB online, ADR034).
6. `run_enrichment(session)` to recompute `crop_field_enrichment`.
7. Re-run coverage check → confirm ≥6 enriched fields per crop.

## Recommendation
Keep WP-C6 PROPOSED. Activate only after: (a) C5 Phase B done, (b) team_00
prioritization signal, (c) LLM/API budget allocated for WR synthesis. Steps
3 (and the step-2 coverage script) are the irreducible external dependencies.

— team_100 (Claude Opus 4.7) 2026-05-28
