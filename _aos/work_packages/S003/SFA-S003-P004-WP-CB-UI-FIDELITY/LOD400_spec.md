---
id: SFA-S003-P004-WP-CB-UI-FIDELITY-LOD400
wp: SFA-S003-P004-WP-CB-UI-FIDELITY — Crop-book + market UI fidelity & Hebrew localization remediation (pre-launch)
gate: L-GATE_S — team_100 has REVIEWED + IMPROVED this DRAFT (root causes pinned to source); the executing session MUST route it to team_190 (non-Claude) for external L-GATE_S BEFORE any build (IR#1/#5)
status: LOD400 — team_100 REVIEWED (v1.1.0). Characterization (אפיון) is build-ready; pending external L-GATE_S.
author: team_100 (Claude Opus, Chief Architect)
date: 2026-06-04
revision: v1.1.0 — team_100 review pass: every blocker pinned to exact file:line; +2 new sub-defects (D-1b double-unit, D-4b mis-routed leading-questions); +1 regression guard (#identity anchor); design questions decided.
trigger: team_00 — live site "far from the mockups; raw numbers, English text, broken interfaces" — confirmed by a team_100 CDP audit
scope: DELIVERY TIER ONLY (sfa_delivery/ — controllers in app/, templates/, public_assets/css|js). NO DB/Python/migration: every fix is render-layer (PHP map/format + template + CSS + one JS asset-gate). If a finding looks like it needs a DB/data change, STOP and scope it as a separate data WP — do not fold silently (see §7).
evidence: _COMMUNICATION/team_100/SFA-S003-P004-WP-CB-UI-FIDELITY/audit_evidence/ (live screenshots, Board-A/B mockups, cdp_facts.json)
design_ssot:
  - Board-A (crop book + calculator): _archive/SFA-S003-P004-WP-CB-UI-CLASSB/team_35/SFA-S003-P004-WP-CB-UI-CLASSB/HANDOFF/design/Board-A-Book-and-Calculator.html
  - Board-B (hub/market/search/community/about/account): _archive/.../HANDOFF/design/Board-B-Hub-Market-Search-Community-About-Account.html
---

# LOD400 — WP-CB-UI-FIDELITY: crop-book + market fidelity & Hebrew localization

## 0. Why this WP exists (read first)
team_00 reported the live site (sfa.nimrod.bio) is **far from the approved team_35 mockups**: raw numbers, English
text, and interactions that "don't really work." team_100 ran a **CDP browser audit** (real rendering, not curl — the
prior code gates check structure/markers, NOT rendered formatting/localization/fidelity, which is exactly why these
passed composer/validate and even L-GATE_V). The audit **confirmed** launch-blocking defects on the CORE product pages,
alongside several surfaces that are actually fine. This WP remediates the confirmed defects to **pixel + functional
fidelity vs Board-A/B**, with a **repeat visual-validation round** and **team_35 design completions where needed**.

**Process note for the executing session:** the previous internal QA (team_50, Haiku) was UNRELIABLE on this work
(false verdicts, mis-read CSS, missed rendered defects). Do **visual/functional verification with the CDP harness
yourself (or a capable model) + external team_190 (non-Claude)** — do not rely on a low-tier QA pass.

**What team_100's v1.1.0 review added** (so the build needs zero re-discovery): exact `file:line` for every defect; the
single shared render path; two newly-found sub-defects (a **double-unit** render and **mis-routed leading-question
links**); a regression guard for the in-page section nav anchor; and architect rulings on the open design questions.

## 1. Confirmed defect inventory (team_100 CDP audit + source trace, 2026-06-04)
> Evidence screenshots in `audit_evidence/`. "WORKS" items are listed so the executing session does NOT regress them.
> All paths are under `sfa_delivery/`. Line numbers are as of build SHA on branch `claude/ui-polish-hub-cropbook-2026-06-03`;
> re-confirm by symbol if they drift.

### BLOCKERS (must fix before launch)

- **D-1 — Crop/calc pages show raw database floats.** `/crop-book/{slug}` renders e.g. "ימים להבשלה **59.043478**",
  "**30.000000** cm", "**8.000000** weeks", "**9.000000** count", "**72.000000** days". The `DECIMAL(14,6)`
  `value_best` is printed verbatim.
  **Pinned render path (the crop page does NOT use the `prov_value.php` macro — it uses an inline closure):**
  - `templates/pages/book_crop.php:47-70` — the `$pv()` closure. Line 63 computes `$display = FieldRegistry::enumLabel(...)`
    then lines 67/69 print `$fn($display)` with NO numeric formatting. For numeric fields `$value` is the raw float.
  - `templates/macros/prov_value.php:66,80,84` — same pattern (`<?= $h((string)$value) ?>`); used by other macros, so
    fix it here too for parity.
  **Required:** a single PHP number-format helper (e.g. `FieldRegistry::fmtNumber()` or a `sfa_fmt_number()` shared fn).
  Rule: integers where whole; otherwise ≤1–2 significant decimals; strip trailing zeros; locale-neutral digits
  (59.043478→**59**, 30.000000→**30**, 8.000000→**8**, 2.10→**2.1**, 0.5→**0.5**). Apply ONLY when `is_numeric($value)`
  (so enum/text values still flow through `enumLabel()` untouched). Apply at EVERY numeric render on crop/variety pages
  **and the calculator dashboard** (`templates/pages/calc_dash.php`, `templates/macros/calc_panel.php`,
  `templates/macros/calc_seq.php` — verify each; same value/unit render path).

- **D-1b — Double unit render (NEW, found in v1.1.0 review).** In the simple-depth topic cards the template hardcodes a
  Hebrew unit AND `$pv()` also appends the field's raw `unit`, producing e.g. "**72.000000 days ימ׳**" and
  "**30.000000 cm ס״מ**":
  - `book_crop.php:208` `…<?= $pv('days_in_nursery') ?><small> ימ׳</small>` (pv already emits unit)
  - `book_crop.php:215` `…<?= $pv('spacing_in_row_cm') ?><small> ס״מ</small>`
  - `book_crop.php:227` `…<?= $pv('succession_interval_weeks') ?><small> שבועות</small>`
  **Required (single-unit rule):** the value renderer (`$pv()` / `prov_value`) is the **sole** emitter of the unit, via
  the D-2 Hebrew unit map. **Remove** the three hardcoded `<small> … </small>` unit suffixes above. The headline-value
  row (`book_crop.php:185-200`) already relies on `$pv()` for the unit (its `$hv_fields['unit']` key is unused) — leave
  it to the renderer. Net effect: each value shows exactly one Hebrew unit.

- **D-2 — English unit codes inline with Hebrew.** Values show `cm`, `days`, `weeks`, `count` (the canonical
  `unit` tokens from the enrichment row) rendered raw next to Hebrew labels. `FieldRegistry` has Hebrew **field-name**
  LABELS and an `ENUM_LABELS` map, but **no unit-token→Hebrew map**.
  **Pinned:** the unit string originates from `crop_field_enrichment.unit` (carried through `CropBookViewController::buildCb1Fields()`
  at `app/Controllers/CropBookViewController.php:683` via `array_merge($row,…)`) and is printed by `$pv()`/`prov_value`.
  **Required:** add a canonical **unit-token → Hebrew** map (new `FieldRegistry::unitLabel(string $unit): string`), used
  by the value renderer. Cover ALL canonical units (authoritative per-field unit list:
  `organic_market_agent/crop_book/canon/field_registry.py`): cm→`ס״מ`, days→`ימים` (or `ימ׳`), weeks→`שבועות`,
  count→(omit — bare number), kg_per_bed_m→`ק״ג/מ׳`, kg_per_ha→`ק״ג/דונם` *(confirm dunam vs hectare with team_35 — see
  §4 Q3)*, °C→`°C`, pct/%→`%`, pH→`pH`, seeds_per_g→`זרעים/גר׳`, units_per_hr→`יח׳/שעה`, … Unknown token → return as-is
  (never crash). Where the field LABEL already implies the unit, the map MAY return `''` to omit it.

- **D-3 — Market category filter chips are raw English DB keys.** `/market/` shows chips `root_vegetables`,
  `legumes_fresh`, `leafy_greens`, `fruits`, `fruiting_vegetables`, `eggs`, `cucurbits`, `brassicas`, `baskets`,
  `alliums`. **This is the "menus in English" team_00 saw.**
  **Pinned ROOT CAUSE:** `app/Controllers/MarketViewController.php:354-371` `fetchCategories()` builds
  `['slug' => $cat, 'name_he' => $cat]` — `name_he` is set to the **raw category slug**. `market_list.php:53` then renders
  `$cat['name_he']` faithfully → raw English. (`market_list.php` itself is correct; do not change its render.)
  **Required:** map each category slug → Hebrew in `fetchCategories()` via `FieldRegistry::enumLabel('category', $cat)`,
  and **extend** `FieldRegistry::ENUM_LABELS['category']` (currently `app/Lib/FieldRegistry.php:260-275`) to cover the
  three market keys it lacks: `legumes_fresh`→`קטניות טריות`, `eggs`→`ביצים`, `baskets`→`סלים` (confirm wording §4 Q2).
  The other seven keys are already mapped — verify the rendered Hebrew matches Board-B. Keep `slug` as the raw key (it is
  the query param). Same map must apply anywhere a product/crop category renders to a user.

- **D-4 — Crop-book filters return wrong/zero results.** TWO independent root causes:
  - **D-4a — Season filter token mismatch.** `/crop-book/?season=…` → 0 crops. The season filter is a free-text input
    (`book_entry.php:158`, placeholder "קיץ / חורף / אביב") whose value is matched with
    `season LIKE ?` at `CropBookViewController.php:54`. If the value the user/UI sends does not match the token format
    actually stored in `crops.season` (English `summer` vs Hebrew `קיץ` vs a month/range string), every match is empty.
    **Required:** FIRST determine the real stored token format — query `SELECT DISTINCT season FROM crops` on the **live
    mirror** (or trace the ingest that populates it) — then make the filter consistent with the data. Strongly preferred:
    convert the free-text season box to a `<select>` with a small canonical option set whose **values match the stored
    data** (mirroring how `sow`/`frost` selects already work — they store/query English tokens, which is why they
    succeed). Provide a season map if a display/stored split is needed.
  - **D-4b — Leading-question links mis-routed to the `category` column (NEW, found in v1.1.0 review).** The "שאלות
    מובילות" links are built at `CropBookViewController.php:124-128` as `/crop-book/table?category=summer|winter|fast|
    beginner|small-space`. `tableView()` filters `WHERE category = ?` (`CropBookViewController.php:157`) — but the
    `category` column holds **botanical** categories (vegetables, leafy_greens, …), so `category = 'summer'` (and the
    other four) **always returns 0**. These tokens are season/dtm/difficulty/space facets crammed into the wrong param.
    **Required:** route each leading-question to the correct filter — `summer`/`winter` → season filter; `fast` →
    `dtm_max` threshold; `beginner` / `small-space` → an appropriate attribute IF data exists (if not, see §4 Q4 / WI-7,
    do NOT silently ship a 0-result link). Easiest correct implementation: point the `href` at `/crop-book/?…` with the
    right param, OR teach `tableView()` to interpret these semantic tokens. Every leading-question link must return a
    correct, non-empty set (or be removed/deferred with a team_35 decision).
  - **Verify EVERY filter end-to-end** (family, season, dtm_max, sow, frost, and all five leading-questions) via CDP:
    baseline vs filtered counts must differ sensibly; none erroneously 0.

- **D-5 — Broken / oversized / duplicated crop hero.** The crop page renders **two** hero sections, both emitting the
  breadcrumb + the `<h1>` crop name + an art element → the identity ("חסה") appears twice; one art element is a giant
  green blob.
  **Pinned ROOT CAUSE (both sections in `book_crop.php`):**
  - `book_crop.php:154-172` — `<section class="crophero">` (the **new** WP-CB-1 hero: art + breadcrumb + h1 + state
    badge; depth-tabs follow it). Its art is correctly sized (`crop-book-v1.css:158-159`, 96×96 `object-fit:contain`).
  - `book_crop.php:467-527` — `<section class="cb-crop-hero" id="identity">` (the **legacy** patch04 hero: a SECOND
    breadcrumb + a SECOND `<h1>`, an icon box, the description lede, and family/dtm meta pills). The "green blob" is
    `.cb-crop-hero__icon` (`crop-book-deep.css:522-528` — an 80×80 green-tinted rounded box) wrapping a sprite
    `<svg><use href="#icon-…"></svg>` that renders at **zero bbox** (cdp_facts `svg_zero: 2`) → just the empty green box
    shows.
  **team_100 ruling (see §4 Q1):** keep the **new `.crophero`** as the single visual hero. From the legacy
  `.cb-crop-hero` section **remove** the duplicate breadcrumb + duplicate `<h1>` + the `.cb-crop-hero__icon` art box, but
  **PRESERVE** (a) the description lede (`cb-crop-hero__lede`, `book_crop.php:495-502`) and (b) the family/dtm meta pills
  (`book_crop.php:504-526`) — re-home them as a small lede/meta block directly under the single hero or into the
  identity-facts section. Result: one hero, one crop name, no green blob, description + pills retained, matching Board-A.

- **D-5b — Section-nav anchor regression guard (NEW).** The in-page section nav links to `#identity`
  (`book_crop.php:126` builds `['id'=>'identity']`; `:535` renders the anchor link). The ONLY element with
  `id="identity"` today is the legacy hero being edited (`book_crop.php:468`). **Required:** when removing/refactoring the
  legacy hero, **retarget `id="identity"`** onto the surviving identity block (the new `.crophero` or the
  `#identity-facts` section at `:548`) so the "מינים" nav link still scrolls correctly. CDP-verify the anchor resolves.

### MAJOR
- **M-1 — Interaction JS coverage.** cdp_facts confirms `classb.js` loads on hub/market/search/community/about but **NOT**
  on `/crop-book/*` or `/calc/` (only `sfa.js` + `crop-book-v1.js` load there) — asset-load gate in
  `templates/_layout.php`. **Required:** confirm which script owns each crop-book/calc interaction and ensure it is
  loaded where used. Verify via CDP click tests: the **table⇄cards toggle** (`audience_switch.php` / `mkt-aud-head`), the
  **audience switch**, the **depth tabs** (`depth_tabs.php`), the **advanced-filter toggle** (`book_entry.php:137`), the
  **market detail graph range buttons** (7י/28י) actually re-render/fetch (the detail graph exists — 48 SVG paths — but
  the audit found `window.fetchHistory` undefined, so range switching may be inert; the API endpoint
  `MarketViewController::productHistoryApi` at `:94` DOES exist, so this is a JS-binding gap, not a backend gap), and
  `/calc/` calculators + book-chip binding + AssumptionField recompute + export all work.
- **M-2 — English `<small>` eyebrow labels.** Hub tiles / audience cards carry English sub-labels (CALC, MARKET,
  CROP-BOOK, FARMER, GARDENER, FIELD-LOG, planner). These exist in Board-B as intentional bilingual mono eyebrows, but
  team_00 reads them as "English menus." **team_100 ruling (§4 Q5):** Hebraize/soften the ones that read as nav/menu
  items; this is a team_35 design-authority call → file as a DESIGN_REQUEST (WI-7), does NOT block the structural fixes.
- **M-3 — Full design-vs-mockup fidelity sweep.** Beyond the above, compare EVERY surface to Board-A/B (spacing, type
  scale, icons, watercolor art, component shapes, graph styling) at desktop 1440 + mobile 375; list every divergence with
  severity; remediate BLOCKER/MAJOR, design-approve or defer MINOR.

### WORKS — do NOT regress (audit-confirmed)
Hub (4 tiles + icons + audience cards, clean); market **list** (cards, ₪ prices, freshness pills, disclaimer, cards/table
toggle present); global **search** returns results (3 for "עגבנייה"); market **detail graph** present; app-shell +
white-green palette (#f8fbf8, no cream); no console errors; no broken icon-sprite `<use>` refs (`icon_broken: 0`).

## 2. Pinned code-location map (single source for the build)

| Defect | File | Symbol / line | Change |
|--------|------|---------------|--------|
| D-1, D-2 | `templates/pages/book_crop.php` | `$pv()` closure L47-70 (value L63; unit L67,69) | number-format numeric values; emit Hebrew unit via `unitLabel()` |
| D-1, D-2 | `templates/macros/prov_value.php` | L66, L80, L84 | same helpers for macro parity |
| D-1b | `templates/pages/book_crop.php` | L208, L215, L227 | remove hardcoded `<small> unit </small>` (renderer owns unit) |
| D-1, D-2 | `templates/pages/calc_dash.php`, `templates/macros/calc_panel.php`, `templates/macros/calc_seq.php` | value/unit renders | apply shared number-format + unitLabel |
| D-2 | `app/Lib/FieldRegistry.php` | new `unitLabel()` + (optional) `fmtNumber()` | add unit-token→Hebrew map |
| D-3 | `app/Controllers/MarketViewController.php` | `fetchCategories()` L354-371 | `name_he => enumLabel('category',$cat)` |
| D-3 | `app/Lib/FieldRegistry.php` | `ENUM_LABELS['category']` L260-275 | add `legumes_fresh`,`eggs`,`baskets` |
| D-4a | `app/Controllers/CropBookViewController.php` + `templates/pages/book_entry.php` | season filter L54 / input L158 | reconcile token to stored `crops.season`; prefer `<select>` |
| D-4b | `app/Controllers/CropBookViewController.php` | `questions()` L124-128 + `tableView()` L152-187 | route leading-questions to correct filter (not `category`) |
| D-5 | `templates/pages/book_crop.php` | legacy hero L467-527 (+ `.crophero` L154-172) | collapse to one hero; keep lede+pills; drop green icon box |
| D-5 | `public_assets/css/crop-book-deep.css` | `.cb-crop-hero__icon` L522-528 | remove/repurpose once art box is dropped |
| D-5b | `templates/pages/book_crop.php` | `id="identity"` L468 (nav L126,535) | retarget anchor to surviving identity block |
| M-1 | `templates/_layout.php` | per-route JS asset gate | load the script each interaction needs |

## 3. Work items
- **WI-1 — Number formatting helper** (D-1): one shared PHP formatter; numeric-only; used by `book_crop.php` `$pv()`,
  `prov_value.php`, variety renders, and the calc dashboard. Define + unit-test the rounding rule.
- **WI-2 — Unit-token → Hebrew label map** (D-2) + **single-unit rule** (D-1b): add `FieldRegistry::unitLabel()`; use it
  in the value renderer; remove the three duplicate hardcoded `<small>` units in `book_crop.php`.
- **WI-3 — Category Hebrew labels** (D-3): map in `fetchCategories()` + extend `ENUM_LABELS['category']`.
- **WI-4 — Crop hero fix** (D-5/D-5b): de-duplicate to one hero, drop the green icon box, preserve lede+pills, retarget
  `#identity` anchor, constrain any art to a sane size; match Board-A.
- **WI-5 — Filter correctness** (D-4a + D-4b): reconcile season token; re-route leading-questions; verify all filters
  end-to-end via CDP (counts non-zero/sensible).
- **WI-6 — Interaction E2E** (M-1): verify/repair toggle, audience switch, depth tabs, adv-filter toggle, market graph
  range, calc (14 calcs + book-chips + AssumptionField + export), search — CDP click tests + fix the `_layout.php` JS gate
  where a needed script is absent.
- **WI-7 — team_35 design-completion request (conditional, BLOCKS only its own items):** file a `DESIGN_REQUEST` for the
  §4 decisions that need design authority (Q2 category wording, Q3 yield-area unit, Q4 beginner/small-space backing, Q5
  eyebrow Hebraization). Never guess a missing design — block those items until team_35 + team_00 respond; the structural
  fixes proceed in parallel.
- **WI-8 — Design-vs-mockup fidelity sweep + remediation** (M-3) for all surfaces, desktop 1440 + mobile 375.
- **WI-9 — Fold patch01 mobile-overflow fix (carry-over).** `SFA-S003-P004-WP-CB-UI-patch01` WI-9 (`/crop-book/table`
  mobile horizontal overflow, ROOT CAUSE responsive table toggle) is **committed (e798bc8) but not yet deployed +
  L-GATE_V'd**. Re-verify it at 375 in this WP's CDP round and let this WP's single deploy + L-GATE_V cover it, so it
  reaches LOD500 with the rest rather than dangling.

## 4. Design questions — team_100 rulings + escalations
team_100 (architect) decides where it has authority; genuine design-authority items go to team_35 via WI-7.

- **Q1 — Which crop hero to keep? → DECIDED by team_100.** Keep the new `.crophero` (Board-A-aligned, precedes depth
  tabs). Strip the legacy `.cb-crop-hero` duplicate breadcrumb/h1/icon-box; preserve its description lede + family/dtm
  pills; retarget `#identity`. (See D-5 / D-5b.) No team_35 input required — this is a bug-level dedup.
- **Q2 — Hebrew wording for `legumes_fresh` / `eggs` / `baskets` chips. → team_35 (WI-7).** Proposed defaults
  `קטניות טריות` / `ביצים` / `סלים`; ship the defaults if team_35 is silent past the build window, but request confirmation.
- **Q3 — Yield/removal area unit: `kg_per_ha` → `ק״ג/דונם` (dunam) or `ק״ג/הקטר`? → team_35 (WI-7).** The audience is
  Israeli small farms (dunam is the working unit); default to `ק״ג/דונם` **only if** the stored value is already
  per-dunam — otherwise keep `ק״ג/הקטר` to avoid a silent 10× unit error. Confirm the stored basis before mapping.
- **Q4 — `beginner` / `small-space` leading-questions backing data. → team_35 + data (WI-7).** If no attribute backs
  these, do not ship 0-result links: either remove the two questions for launch or have team_35/data define the backing
  facet. `summer`/`winter`/`fast` are fixable now (season + dtm).
- **Q5 — English eyebrow Hebraization (M-2). → team_35 (WI-7).** Recommendation: Hebraize/soften eyebrows that read as
  menu items; keep purely-decorative mono eyebrows only where Board-B clearly intends them. Non-blocking.

## 5. Acceptance criteria (visual + functional, vs Board-A/B — all CDP-checkable)
- **AC-1** No raw multi-decimal numbers anywhere user-facing. CDP text scan of crop/variety/calc pages matches no
  `\d+\.\d{3,}` and no `\.\d*0\b` trailing-zero artifacts (59, 30, 8, 2.1 — never 59.043478 / 30.000000).
- **AC-2** No English unit codes and no raw English enum/category keys rendered to users. CDP text scan: no `cm|days|
  weeks|count` units beside Hebrew; market chips + crop filters all Hebrew; exactly ONE unit per value (no "days ימ׳").
- **AC-3** Every filter (market category; crop-book family/season/dtm_max/sow/frost; all 5 leading-question links)
  returns a correct, non-empty set. CDP: baseline vs filtered counts differ sensibly; none erroneously 0 (or the link is
  removed/deferred per Q4).
- **AC-4** Crop hero renders ONCE, correctly sized, matching Board-A: a single `<h1>` crop name, a single breadcrumb, no
  empty green icon box; description lede + family/dtm pills present; CDP bbox of any art ≤ its CSS box.
- **AC-4b** `#identity` section-nav link resolves to a live element (CDP: anchor target exists and scrolls).
- **AC-5** table⇄cards toggle, audience switch, depth tabs, adv-filter toggle, market graph range buttons, calc (14 calcs
  + book-chips + AssumptionField recompute + export), and search all function (CDP interaction tests pass; no console
  errors introduced).
- **AC-6** Per-surface design-vs-live screenshot pairs (CDP, desktop 1440 + mobile 375) reviewed; no open BLOCKER/MAJOR
  divergence from Board-A/B (or design-approved by team_35/team_00). Includes WI-9 `/crop-book/table` 375 no-overflow.
- **AC-7** No regression of the "WORKS" list; no horizontal overflow at 375 on any route; palette #f8fbf8 / no cream;
  composer green; `php -l` clean on every edited file; `validate_aos.sh` 0 FAIL; delivery-tier scope; IR#4 honored.

## 6. Validation flow (MANDATORY — executing session)
1. **Review + improve** this LOD — DONE by team_100 (v1.1.0; root causes pinned, design questions decided). The executing
   session may add findings but must not weaken the ACs.
2. **External L-GATE_S** — route this improved LOD to **team_190 (non-Claude, IR#1/#5)** for spec review BEFORE build.
   (team_100 NEVER self-issues L-GATE_S/V.) Address findings; re-route if BLOCKED. **No build before PASS.**
3. **Build** (team_10 Sonnet) per WI; **team_100 independent L-GATE_B** with **CDP visual verification** (screenshots vs
   Board-A/B + the AC CDP scans) — NOT a low-tier QA pass.
4. **Deploy** (team_99, FTPS→uPress; this Mac session is auth-gated for the SSH/deploy — route to team_99/team_00) —
   verify served assets (`?v=` advanced + markers present).
5. **External L-GATE_V + repeat visual round** — team_190 (non-Claude) per-surface design-vs-live vs Board-A/B + the AC
   matrix on the LIVE site. On PASS → LOD500_LOCKED. **This is the launch gate.**
6. **team_35** completions resolved (WI-7) before declaring GO.

## 7. Risks / notes / scope guards
- **Render-layer only.** Every fix is a PHP map/format, a template edit, a CSS tweak, or one JS asset-gate. Do NOT mutate
  the DB. The MySQL mirror stays a faithful mirror of Postgres.
- **D-4 data caveat.** The season fix RECONCILES the filter to existing data; it does NOT edit data. If the stored
  `crops.season` tokens are themselves wrong/inconsistent (a genuine data defect, not a render mismatch), STOP and scope a
  separate data WP — flag it to team_100/team_00, do not fold silently.
- **Single-unit discipline.** After WI-2, audit the whole crop page for any other place a unit is hardcoded next to a
  `$pv()` call (grep `<small>` near pv) to avoid a second double-unit.
- **Calc parity.** The calculator dashboard shares the value/number/unit path — D-1/D-2 apply to `/calc/` too; verify by
  CDP, don't assume.
- **Language policy.** User-facing UI Hebrew; code/docs/inter-team English. The brand token "SFA" in the nav logo is
  acceptable (not a localization defect).
- **Regression budget.** The WORKS list (§1) and the patch01 WI-9 mobile fix must both still pass at the end.
