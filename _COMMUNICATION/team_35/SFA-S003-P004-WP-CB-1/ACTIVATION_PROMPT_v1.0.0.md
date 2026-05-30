# ACTIVATION PROMPT — SFA-S003-P004-WP-CB-1 — team_100 → team_35 — v1.0.0

**Date:** 2026-05-30
**Author:** team_100 (Chief System Architect, Claude Code)
**To:** team_35 (Design Studio)
**WP:** SFA-S003-P004-WP-CB-1 (Crop Book v1 — calculator-driven)
**Type:** ACTIVATION_PROMPT (design routing)
**Routing:** team_35 LOD300 → team_100 → embedded in LOD400 §10 → L-GATE_S (team_190, non-Claude)

---

## 0. TL;DR

Design the **Crop Book v1** UI: the live read-only book at `sfa.nimrod.bio/crop-book/` becomes a **planning tool** driven by **14 calculators** (attached, APPROVED by team_00). Deliver an LOD300 design package covering: two-audience layout (Cards/Table), per-crop Simple/Full/Drill-down, the **calculator panel**, the new **`AssumptionField`** component, and the **complete/partial** crop states. Anchor on the LOCKED nimrod.bio AOS Design System v3.4 + the watercolor brand system already in production.

---

## 1. Context (read first)

1. **Approved Calculator Catalog** (attached, §6 below): `_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-1/CALCULATOR_CATALOG_v1.0.0.md` — the 14 calculators, audiences, fields, AssumptionFields.
2. **Mandatory Field Schema:** `_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-1/MANDATORY_FIELD_SCHEMA_v1.0.0.md` — what data each crop carries.
3. **Gap-Fill Plan:** `_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-1/GAP_FILL_PLAN_v1.0.0.md` — the complete/partial state machine you must visualize.
4. **LOD400 (draft):** `_aos/work_packages/S003/SFA-S003-P004-WP-CB-1/LOD400_spec.md` — §7 UI contract; your mockups embed into §10.
5. **Your existing design kit:** `_COMMUNICATION/TEAM_100/SFA_UI_DESIGN_PHASE_2_CHATGPT_HANDOFF/03_NIMROD_BIO_STYLE_ANCHORS/brand_system/sfa_team35_handoff/` — `COMPONENTS.md` (incl. §11 `CalcField`), `DESIGN_TOKENS.md`, `TEMPLATES.md`, `MODULES_REGISTRY.yaml`. **Extend these; do not restyle from scratch.**
6. **Live site:** `https://sfa.nimrod.bio/crop-book/` (current read-only book, WP-UI-patch04) — this is what you are evolving.
7. **Brand:** LOCKED nimrod.bio AOS Design System v3.4 + watercolor heroes (Devora masters, deterministic) + Carmela font. RTL Hebrew.

---

## 2. What to design (LOD300 deliverables)

### 2.1 Two-audience layout (small diff, switchable)
- **Cards** (home gardener / course student) — default for `/crop-book/`. Visual, per-crop, surfaces calculators #1,#2,#4,#5,#8,#10,#11.
- **Table** (small farmer) — dense, sortable; exposes calculators #6,#7,#9,#12,#13 inline per row.
- A clear, persistent **audience switch**. Same data, different density — NOT two different products.

### 2.2 Per-crop page — three depths
- **Simple** — headline values + 3–4 key calculators.
- **Full** — all mandatory fields + all *enabled* calculators.
- **Drill-down** — per-variety values, **source provenance + confidence** (the "one winning value" is shown up front; the hierarchy lives here).

### 2.3 Calculator panel
- A reusable calculator card: title, the book values it uses (with the ↗ ספר cross-link, per your `CalcField` §11), the user inputs, the result. Show units. Handle the **disabled state** (a required field is MISSING): explain which field is missing + a **"request info"** CTA.
- Layout for grouped calculators (e.g. seed→sow→nursery flow #1→#3→#4 reads as a sequence).

### 2.4 `AssumptionField` component — NEW, first-class (team_00 directive)
A planning assumption the user can adjust. Four parts, all visible/accessible:
1. **Default value** (e.g. germination **90%**, bed width **80 cm**).
2. **Inline override** input.
3. A **clear, attractive explainer** — *when/why/how* to change it (e.g. "seeds lose viability with age…").
4. A **"read more →" link** to a full nimrod.bio blog post.
Design the collapsed (just default + edit affordance) and expanded (explainer + link) states. First instances to mock: **germination_rate (90%)** and **bed_width (80 cm)**.

### 2.5 Complete vs Partial crop states
- **Complete** — trustworthy: clean values, all calculators enabled.
- **Partial** — honest degraded: **asterisk** on unvalidated/web-sourced values (with tooltip), **"—" + "request info"** on missing values, calculators that need a missing field shown **disabled with explanation**. Design the asterisk, the tooltip, the request-info CTA, and the disabled-calc treatment.

### 2.6 Family rotation hint
A small informational chip (not a calculator): "don't follow {family} in this bed for 3 seasons." Derived from botanical family.

---

## 3. Constraints (locked — do not relitigate)
- Brand: AOS Design System v3.4 + watercolor system; RTL Hebrew; Carmela.
- One winning value up front; provenance only in Drill-down.
- Module boundary: agronomic knowledge + calculators ONLY. No Planner/Tasks/POS/Tend UI (future modules) — but leave obvious, stable hooks where their entry points will live.
- Delivery tier is Slim4/PHP on uPress — design must be implementable as server-rendered templates + light JS for interactive calculators.

## 4. Deliverable format
LOD300 design package, extending your existing kit:
- Annotated mockups (or high-fidelity component specs) for §2.1–§2.6.
- New/changed entries in `COMPONENTS.md` (AssumptionField, calculator panel, partial-state treatments) + `DESIGN_TOKENS.md` deltas + `TEMPLATES.md` route map updates.
- An 8-question open-issues list for team_100/team_00 if any.
Route the package back to **team_100** for embedding into LOD400 §10 and team_00 approval before L-GATE_S.

## 5. Out of scope
Calculator math (owned by team_100 LOD400 §5), data/schema, deploy. You design the experience; the formulas and field semantics are fixed by the attached catalog.

---

## 6. ATTACHED — Approved Calculator Catalog (the 14)

> Full source: `_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-1/CALCULATOR_CATALOG_v1.0.0.md`. Summary for design:

| # | Calculator | Audience | Key shown values | User inputs |
|---|-----------|----------|------------------|-------------|
| 1 | Seed quantity to buy | Both | seeds/g, spacing, rows · *germ 90%* | bed-length, seeds/hole |
| 2 | Transplants needed | Both | spacing, rows | bed-length |
| 3 | Nursery trays + sow date | Farmer | days_in_nursery · *tray cells* | plants, field-set date |
| 4 | Sow date (from harvest) | Both | DTM, nursery, method | target harvest date |
| 5 | Harvest date + window | Both | DTM, harvest window, method | sow date |
| 6 | Succession schedule | Farmer | interval weeks, season | first sow, # successions |
| 7 | Beds for target yield | Farmer | yield/m · *bed length* | target kg |
| 8 | Expected yield | Both | yield/m | bed-length |
| 9 | Expected revenue | Farmer | yield/m, price | area |
| 10 | Plant population / layout | Both | spacing, rows · *bed width 80cm* | — |
| 11 | Frost / planting window | Both | frost class, DTM | last/first frost dates |
| 12 | Fertilizer / compost rate | Farmer | N/P/K removal · *compost N%* | bed area |
| 13 | Crop profit comparison | Farmer | yield/m, price across crops | bed-meters |
| 14 | Seed / input cost | Farmer | grams (from #1) | seed price |

*Italic = `AssumptionField` (default + override + explainer + nimrod.bio link). Companions = family rotation hint, informational only.*

---

*Issued by team_100, 2026-05-30. team_35: confirm receipt and your LOD300 plan, then design. Questions → `_COMMUNICATION/team_100/`.*
