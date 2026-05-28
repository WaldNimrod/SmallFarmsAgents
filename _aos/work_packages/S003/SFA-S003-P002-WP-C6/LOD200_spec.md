---
id: SFA-S003-P002-WP-C6-LOD200
wp: SFA-S003-P002-WP-C6 — Sparse Crops Future Expansion
gate: L-GATE_S (LOD200)
status: PROPOSED
author: team_10 (Claude Sonnet 4.7) under team_00 grant 2026-05-28
date: 2026-05-28
version: v1.0.0
parent_wp_chain:
  - SFA-S003-P002-WP-C1 (LOD500_LOCKED) ✅
  - SFA-S003-P002-WP-C2 (Hebrew NI)
  - SFA-S003-P002-WP-C3 (LOD500_LOCKED) ✅
  - SFA-S003-P002-WP-C4 (LOD500_LOCKED) ✅
  - SFA-S003-P002-WP-C5 (cleanup phase — Phase A code, Phase B team_00 manual)
depends_on: [SFA-S003-P002-WP-C5]
activation_condition: "WP-C5 LOD500_LOCKED (data state stable post-cleanup)"
mode: "future expansion — registered as PROPOSED; not for execution now"
---

# LOD200 — WP-C6: Sparse Crops Future Expansion

## 1. Mission

After WP-C1..C5 close, ~20 crops in the catalog remain **sparse** —
defined as ≤2 enriched fields (CALIBRATED + auto-blended combined).
WP-C6 captures the future plan to bring these crops up to coverage
parity with the well-covered set (≥6 enriched fields).

This WP is **registered now (PROPOSED) so the roadmap reflects intent**.
No execution until team_00 prioritizes it after WP-C5 closure and any
intervening waves (e.g., UI work).

## 2. Sparse crops in-scope (post-WP-C5 snapshot)

### 2.1 Herbs (~12 crops, mostly Mediterranean)

- מרווה (Sage, *Salvia officinalis*)
- טימין (Thyme, *Thymus vulgaris*)
- טרגון (Tarragon, *Artemisia dracunculus*)
- נענע (Mint, *Mentha spicata*)
- לימון בלם / מליסה (Lemon balm, *Melissa officinalis*)
- אורגנו (Oregano, *Origanum vulgare*)
- רוזמרין (Rosemary, *Salvia rosmarinus*)
- כוסברה (Coriander, *Coriandrum sativum*) — if coverage <6 fields
- שמיר (Dill, *Anethum graveolens*) — if coverage <6 fields
- פטרוזיליה (Parsley, *Petroselinum crispum*) — if coverage <6 fields
- בזיל variants (post-WP-C5 merge — surviving sub-varieties)
- חמין / שטבת (any remaining sparse herb genus)

### 2.2 Specialty / niche (~5 crops)

- ג'ינג'ר (Ginger, *Zingiber officinale*)
- כורכום (Turmeric, *Curcuma longa*)
- ארטישוק ירושלמי (Jerusalem artichoke, *Helianthus tuberosus*)
- פאק צ'וי (Pak choi, *Brassica rapa* subsp. *chinensis*)
- תפוז (Citrus, *Citrus sinensis*) — sparse if only orchard data

### 2.3 New vegetables surfacing post-WP-C5

- Any post-merge sub-variety still sparse after WP-C5 cleanup
- TBD list — finalize by `validate_enrichment.py` snapshot after WP-C5

## 3. Sources to investigate

**Tier A — high-confidence published research** (PR weight = 0.70):
- ICARDA (International Center for Agricultural Research in the Dry Areas)
  — Mediterranean herbs + drought-adapted crops
- CIHEAM (International Centre for Advanced Mediterranean Agronomic Studies)
- USDA NRCS PLANTS database
- University extension sources not yet harvested (UC Davis specialty crops,
  Cornell Mediterranean varieties, Purdue herbs)

**Tier B — operational / observational** (OP weight = 0.55):
- Israeli MoA "Plants Annual" (specialty crops chapter)
- Shaham extension herb-specific bulletins

**Tier C — narrative / NI** (NI hard override):
- Wikipedia Hebrew (עשבי תיבול) — for cultural / culinary / regional context
- JMF book chapters not yet extracted (post-WP-C2 backlog)
- team_00 EX overrides for confident-knowledge fields (final fallback)

**Tier D — AI-synthesized research** (WR weight = 0.60, via WP-C5 architecture):
- For crops where no IL/PR source exists, fall back to WR:* sources
  generated via team_80 multi-engine scout (OpenAI + Perplexity + Gemini)

## 4. Out-of-scope

- Engine changes (engine v1.1 is final; inheritance helper covers all cases)
- New trust tiers (WR added in WP-C5 closes the tier ladder)
- UI work (separate WPs)
- Bulk re-import of WP-C1..C4 sources (re-run only if new schema needed)

## 5. Activation

Triggered by team_00 after **all** of:
- WP-C5 LOD500_LOCKED (data state stable post-cleanup)
- `validate_enrichment.py` snapshot shows N sparse crops (final count TBD)
- team_00 prioritization signal (no auto-trigger)

## 6. Estimated effort

- LOD400 spec authoring: 2-4 hours
- Per-crop research + import: ~30-60 min each (×20 crops = 10-20 hours)
- Engine re-run + validation: ~1 hour
- Total: **MEDIUM** (similar to WP-C4 effort envelope)

## 7. Success criteria (preliminary — refine at LOD400)

- All sparse crops reach ≥6 enriched fields (CALIBRATED or PR-backed)
- No crop in catalog has <3 enriched fields post-C6
- Coverage gap analysis: <5% of crops remain "sparse" (vs. ~13% post-C5)
- `validate_enrichment.py` snapshot committed as baseline for future waves

## 8. Dependencies

- Hard: WP-C5 LOD500_LOCKED
- Soft: WR tier weight tuning (Decision #5) — if farmer feedback adjusts WR=0.60,
  WP-C6 may need re-run with new weights
- Soft: UI (WP-D?) for surfacing low-coverage crops to end users

## 9. LOD500_LOCKED untouched

Same protected list as C1-C5. WP-C6 ingests data only — no engine, schema,
or reconciler changes anticipated.

## 10. GCR requirements

**NONE anticipated**. WP-C5 added the `crop_source_weights` table; WP-C6
just adds rows (new WR:* labels for the sparse-crop research outputs).

## 11. Open questions (resolve at LOD400)

- Which sparse crops are highest priority for SFA users? (farmer survey?)
- Budget for ICARDA / CIHEAM source acquisition?
- LLM budget for WR:* synthesis on sparse crops (Anthropic API)?
- Should WP-C6 split by botanical family (Lamiaceae herbs separate from
  specialty roots)?

---

*Authored by team_10 (Claude Sonnet 4.7) 2026-05-28 under team_00 approval
in DECISION_RECORD_SFA-S003-P002-WP-C5_v1.0.0 §Decision 4. Registered as
PROPOSED — not for execution now.*
