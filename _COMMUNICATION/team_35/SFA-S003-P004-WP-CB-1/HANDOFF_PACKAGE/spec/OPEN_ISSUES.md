# DECISIONS — Crop Book v1 (LOD300) — resolved with Nimrod (team_00)

> **WP:** SFA-S003-P004-WP-CB-1 · team_35 (Design Studio)
> The 8 design questions are **resolved** (Nimrod, 2026-05-31). Build to these.

| # | Question | **Decision** |
|---|----------|--------------|
| **Q1** | AssumptionField override persistence | **Per-session only** (no migration; no account-level in v1). |
| **Q2** | Audience switch default | **Always Cards** on entry (no per-visitor stickiness). |
| **Q3** | Carmela font | **Licensed — self-host and use it.** Enforce **typographic consistency** across the app (single type system, Carmela for wordmark/display per the token spec). No SVG-wordmark fallback needed. |
| **Q4** | Confidence threshold τ | **τ ≥ 0.50** (raised from 0.40). Validated = EX/NI override or confidence ≥ 0.50. |
| **Q5** | "Request info" target | **One simple community queue.** This is a **marketing / feature-idea CTA**, not an active community-management system — Nimrod is *not* running a live online community; "community" = the real-world network of small organic growers (and home gardeners) the product serves as an open gift to the field, and a soft CTA toward the paid vision (advanced/custom calculators). **Keep it basic and simple** — a lightweight "request / suggest" capture, low-friction, no inbox/triage UI. |
| **Q6** | Calculator surfacing | **Small calculators are buttons** placed in-context on the crop page that **open as a module overlay over the page**. The **full calculator is its own page** (the dashboard, §2.3b). **Every calculator module is a self-contained basis for the future system.** |
| **Q7** | Price/revenue unit | **Main interface: normalize** (per bed-meter in the table). **Calculator + Full-detail depth: show all data / the documented unit.** |
| **Q8** | `days_in_nursery` vs `days_in_nursery_cell` | **It's a duplication — eliminate one.** Single field, Hebrew label **"ימים במשתלה"**. |

---

### New schema field — ratified
- **`needs_summer_shade`** — Israel-specific, **YES**, and modeled as **3 shade levels: 30% / 40% / 50%** (by crop sensitivity), plus "ללא הצללה". Surfaced in the crop page, as a filter, and with a full tooltip.

---

### Still open — for team_100 schema ratification (gap-analysis)
Studying the attached originals (גזר טרי / מנגולד / חסה) surfaced a **canonical 13-topic structure** every JMF sheet follows, and **7 field groups our schema does not yet carry**. The Drill-down reference sheet (§2.2) now follows the JMF order exactly; these fields are mocked as **"מוצע" (proposed)** pending team_100 ratification:

| # | Proposed field(s) | From JMF original | Where it lives | Type |
|---|---|---|---|---|
| 1 | `seeder_model` + `seeder_settings` | carrot: *JANG 3X · X-24 · F-13B · brush "0"* | topic **ציוד וכיוונון** | text (direct-sow crops) |
| 2 | `irrigation_type` (+ `drip_lines_per_bed`) | *drip tape 4/bed or sprinkler* | topic **השקיה** | enum + int |
| 3 | `root_depth_class` | *Root depth: Medium (24"-40")* | topic **השקיה** | enum {shallow/medium/deep} + range |
| 4 | `common_pests` + `foliar_feeding_program` | chard: *flea beetles → netting; monthly boron + seaweed* | topic **מזיקים ומחלות** (NEW) | text |
| 5 | `sale_unit` + `unit_size` | carrot: *8 carrots/bunch*; chard: *bouquet 6–7 stems*; size 13–18cm | topic **קציר** | enum + spec — also fixes Q7 (price unit) |
| 6 | `labor_rate_harvest` + `labor_rate_wash` (units/hr) | *1 person 60 bunches/hr harvest · 100/hr wash* | topics **קציר / שטיפה** | int — enables a labor-cost calculator |
| 7 | `plantings_per_season` + `harvest_weeks_span` | chard: *3 plantings, harvest over 14 weeks* | topic **רצף וחברה** | int — complements `succession_interval` |

**Recommended fix:**
- **a.** Adopt the **13-topic taxonomy** (`CROP_TOPICS`) as the canonical ordering for both the schema and the UI — it is the structure growers already know from JMF, and it makes every depth read as a plan.
- **b.** Add the 7 field groups above to the agronomic schema (most are PR-fillable directly from the 37 MasterClass MDs already on disk — see `load_masterclass_sheets.py`; the structured sheets carry seeder, spacing, pests, harvest rate, storage).
- **c.** `sale_unit`/`unit_size` also resolves **Q7** (price-unit normalization) — the table's per-bed-meter columns can then convert correctly.
- **d.** `labor_rate_*` unlocks a future **labor-cost calculator** (a clean hook, not built this WP).

---

### Not blocking (design proceeded on these)
- Mockup worked crops: **חסה (lettuce)** = COMPLETE, **צנונית (radish)** = PARTIAL. Swap freely; nothing depends on these specific crops.
- Watercolor coverage: lettuce / radish / parsley / dill have Devora masters; tomato & cucumber fall back to glyph/SVG until masters exist (per the ImagePrompt slot contract, COMPONENTS §15).
- Annotation language: Hebrew = production UI copy; English = design notes for cross-team routing. Production ships Hebrew-only.
