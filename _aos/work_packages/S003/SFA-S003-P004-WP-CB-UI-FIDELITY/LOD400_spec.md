---
id: SFA-S003-P004-WP-CB-UI-FIDELITY-LOD400
wp: SFA-S003-P004-WP-CB-UI-FIDELITY — Crop-book + market UI fidelity & Hebrew localization remediation (pre-launch)
gate: L-GATE_S (DRAFT by team_100) → the executing session MUST route this to team_190 (non-Claude) for external L-GATE_S BEFORE any build
status: LOD400_DRAFT — characterization (אפיון) for handoff; executing session reviews + improves + externally validates before build
author: team_100 (Claude Opus, Chief Architect)
date: 2026-06-04
trigger: team_00 — live site "far from the mockups; raw numbers, English text, broken interfaces" — confirmed by a team_100 CDP audit
scope: DELIVERY TIER (sfa_delivery/ templates + CSS + the PHP render/label layer) + a possible team_35 design-completion request. No DB/Python/migration unless a finding requires data correction (then scope it explicitly).
evidence: _COMMUNICATION/team_100/SFA-S003-P004-WP-CB-UI-FIDELITY/audit_evidence/ (live screenshots, Board-A/B mockups, cdp_facts.json)
design_ssot:
  - Board-A (crop book + calculator): _archive/SFA-S003-P004-WP-CB-UI-CLASSB/team_35/SFA-S003-P004-WP-CB-UI-CLASSB/HANDOFF/design/Board-A-Book-and-Calculator.html
  - Board-B (hub/market/search/community/about/account): _archive/.../HANDOFF/design/Board-B-Hub-Market-Search-Community-About-Account.html
---

# LOD400 — WP-CB-UI-FIDELITY: crop-book + market fidelity & Hebrew localization

## 0. Why this WP exists (read first)
team_00 reported the live site (sfa.nimrod.bio) is **far from the approved team_35 mockups**: raw numbers, English
text, and interactions that "don't really work." team_100 ran a **CDP browser audit** (real rendering, not curl —
the prior code gates check structure/markers, NOT rendered formatting/localization/fidelity, which is exactly why
these passed composer/validate and even L-GATE_V). The audit **confirmed** launch-blocking defects on the CORE
product pages, alongside several surfaces that are actually fine. This WP remediates the confirmed defects to
**pixel + functional fidelity vs Board-A/B**, with a **repeat visual-validation round** and **team_35 design
completions where needed**.

**Process note for the executing session:** the previous internal QA (team_50, Haiku) was UNRELIABLE on this work
(false verdicts, mis-read CSS, missed rendered defects). Do **visual/functional verification with the CDP harness
yourself (or a capable model) + external team_190 (non-Claude)** — do not rely on a low-tier QA pass.

## 1. Confirmed defect inventory (team_100 CDP audit, 2026-06-04)
> Evidence screenshots in `audit_evidence/`. "WORKS" items are listed so the executing session does NOT regress them.

### BLOCKERS (must fix before launch)
- **D-1 — Crop pages show raw database floats.** `/crop-book/{slug}` renders e.g. "ימים להבשלה **59.043478**",
  "**30.000000** cm", "**8.000000** weeks", "**9.000000** count". The DECIMAL(14,6) `value_best` is printed raw.
  *Render site:* `sfa_delivery/templates/pages/book_crop.php` (and macro `templates/macros/prov_value.php`):
  `$value = $field['value_best']` printed directly. *Required:* a number-format helper — integers where whole,
  ≤1–2 significant decimals otherwise, no trailing zeros, locale-appropriate (e.g. 59.043478→**59**, 30.000000→**30**,
  2.10→**2.1**). Apply to EVERY numeric value rendered on crop/variety pages + the calculator dashboard.
- **D-2 — English unit codes inline with Hebrew.** Values show `cm`, `days`, `weeks`, `count` (the canonical
  `FIELD_REGISTRY.unit` tokens) rendered raw next to Hebrew labels. *Note:* `FieldRegistry.php` has Hebrew **field-name**
  LABELS (so the row label is "ימים להבשלה") but **no unit-token→Hebrew map**. *Required:* add a canonical
  unit-token → Hebrew label map (cm→`ס״מ`, days→`ימים`, weeks→`שבועות`, count→ (count, often omittable),
  kg_per_bed_m→`ק״ג/מ׳`, kg_per_ha→`ק״ג/דונם` or the agreed unit, °C→`°C`, pct→`%`, pH→`pH`, seeds_per_g→`זרעים/גר׳`,
  units_per_hr→`יח׳/שעה`, …). Render the Hebrew unit (or omit when the field label already implies it). Cover ALL
  whitelisted T1 fields (see `organic_market_agent/crop_book/canon/field_registry.py` for the canonical unit per field).
- **D-3 — Market category filter chips are raw English DB keys.** `/market/` shows chips `root_vegetables`,
  `legumes_fresh`, `leafy_greens`, `fruits`, `fruiting_vegetables`, `eggs`, `cucurbits`, `brassicas`, `baskets`,
  `alliums`. **This is the "menus in English" team_00 saw.** *Required:* a category-key → Hebrew label map for the
  market filter UI (and anywhere a category renders). *Render site:* `market_list.php` / the market controller.
- **D-4 — Crop-book filters return wrong/zero results.** `/crop-book/?season=summer` → **0 crops** (baseline 70).
  Root cause: the filter VALUE token (English `summer`) mismatches the data in the `season` column (`season LIKE ?`,
  `CropBookViewController.php:54`). *Required:* make filter values consistent with the stored data (Hebrew tokens or
  a canonical mapping) so each filter returns the correct, non-empty result set. Verify EVERY filter (family, season,
  dtm, sow-method, frost) end-to-end. Same applies to the `/crop-book/table?category=…` "leading question" links.
- **D-5 — Broken / oversized / duplicated crop hero.** The crop page top shows a giant green blob/oversized hero,
  and the crop identity ("חסה") appears to render twice. *Render site:* `book_crop.php` has BOTH `.crophero` (L154)
  and `.cb-crop-hero #identity` (L468) — likely a duplicate + an unsized art/logo (same unsized-`<svg>`/`<img>` class
  as prior bugs). *Required:* one correct, properly-sized crop hero matching Board-A; no duplicate; art/icon constrained.

### MAJOR
- **M-1 — Interaction JS coverage.** `classb.js` loads on hub/market/search/community/about but NOT on
  `/crop-book/*` or `/calc/` (asset-load gate in `_layout.php`). Confirm NO crop-book/calc interaction depends on it;
  if it does, load it there. Verify the **table⇄cards toggle** and the **audience switch** actually toggle the view
  (CDP click test), the **graph range buttons** (7י/28י) re-render/fetch (the market detail graph EXISTS — 48 SVG
  paths — but `window.fetchHistory` is undefined, so range switching may be inert), and `/calc/` calculators + book-chip
  binding + AssumptionField recompute + export all work.
- **M-2 — English `<small>` labels.** Hub tiles / audience cards carry English sub-labels (CALC, MARKET, CROP-BOOK,
  FARMER, GARDENER, FIELD-LOG, planner). These exist in Board-B as bilingual eyebrows, but team_00 reads them as
  "English menus." DESIGN DECISION (route to team_35 if needed): keep as styled eyebrows, soften, or Hebraize.
- **M-3 — Full design-vs-mockup fidelity sweep.** Beyond the above, compare EVERY surface to Board-A/B (spacing,
  type scale, icons, watercolor art, component shapes, graph styling) and list every divergence with severity.

### WORKS — do NOT regress (audit-confirmed)
Hub (4 tiles + icons + audience cards, clean); market **list** (cards, ₪ prices, freshness pills, disclaimer,
cards/table toggle present); global **search** returns results (3 for "עגבנייה"); market **detail graph** present;
app-shell + white-green palette; no console errors; no broken icon-sprite `<use>` refs.

## 2. Work items
- **WI-1 — Number formatting helper** (D-1): a single PHP formatter used by `prov_value.php` + `book_crop.php` +
  the calc dashboard + variety pages. Define + test the rounding rule.
- **WI-2 — Unit-token → Hebrew label map** (D-2): cover all canonical units; use at every value render; omit redundant
  units when the field label implies them.
- **WI-3 — Category/enum Hebrew labels** (D-3) + **filter-value consistency** (D-4): one source-of-truth map; market
  chips + crop-book filters render Hebrew AND query the correct data → non-empty, correct results.
- **WI-4 — Crop hero fix** (D-5): de-duplicate + correctly size the crop hero/art per Board-A.
- **WI-5 — Interaction E2E** (M-1): verify/repair toggle, audience switch, graph range, calc, filters, search (CDP).
- **WI-6 — Design-vs-mockup fidelity sweep + remediation** (M-3) for all surfaces.
- **WI-7 — team_35 design-completion request (conditional):** if any surface lacks an approved v2 design, or a label/
  token/enum-Hebraization decision (M-2) or a missing-icon set requires design authority, the executing session files
  a `DESIGN_REQUEST` to team_35 and BLOCKS those items until team_35 + team_00 respond — never guess a missing design.

## 3. Acceptance criteria (visual + functional, vs Board-A/B)
- **AC-1** No raw multi-decimal numbers anywhere user-facing (CDP scan of crop/variety/calc pages: no `\.\d{3,}`).
- **AC-2** No English unit codes / no raw English enum or category keys rendered to users (CDP text scan; market
  chips + crop filters all Hebrew).
- **AC-3** Every filter (market category; crop-book family/season/dtm/sow/frost; leading-question links) returns the
  correct, non-empty result set (CDP: baseline vs filtered counts differ sensibly, none erroneously 0).
- **AC-4** Crop hero renders once, correctly sized, matching Board-A (CDP bbox sane; no duplicate identity).
- **AC-5** table⇄cards toggle, audience switch, graph range buttons, calc (14 calcs + book-chips + AssumptionField +
  export), and search all function (CDP interaction tests pass).
- **AC-6** Per-surface design-vs-live screenshot pairs (CDP, desktop 1440 + mobile 375) reviewed; no BLOCKER/MAJOR
  divergence from Board-A/B remains open (or is design-approved by team_35/team_00).
- **AC-7** No regression of the "WORKS" list; no horizontal overflow at 375; palette #f8fbf8 / no cream; composer
  green; validate_aos 0 FAIL; delivery-tier scope; IR#4.

## 4. Validation flow (MANDATORY — executing session)
1. **Review + improve** this LOD (it is a DRAFT characterization): refine WIs, add any defects this spec missed,
   pin exact code locations, decide the team_35 design questions to ask.
2. **External L-GATE_S** — route the improved LOD to **team_190 (non-Claude, IR#1/#5)** for spec review BEFORE build.
   (team_100 NEVER self-issues L-GATE_S/V.) Address findings; re-route if BLOCKED.
3. **Build** (team_10 Sonnet) per WI; **team_100 independent L-GATE_B** with **CDP visual verification** (screenshots
   vs mockups + the AC CDP scans) — NOT a low-tier QA pass.
4. **Deploy** (team_99, FTPS) — verify served assets (`?v=` advanced + markers present).
5. **External L-GATE_V + repeat visual round** — team_190 (non-Claude) per-surface design-vs-live vs Board-A/B +
   the AC matrix on the LIVE site. On PASS → LOD500_LOCKED. **This is the launch gate.**
6. **team_35** completions resolved (WI-7) before declaring GO.

## 5. Risks / notes
- Some "raw value" fixes are pure render-layer (safe). Filter-value fixes may touch how the query maps to data —
  verify against the live data (do NOT change the DB unless a genuine data defect is found; if so, scope a separate
  data WP, don't fold silently).
- The calculator dashboard shares the value/number/unit render path — fix it there too (D-1/D-2 apply to /calc/).
- Keep all source/labels in Hebrew for user-facing UI per the language policy; code/docs English.
