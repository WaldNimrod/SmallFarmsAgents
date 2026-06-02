# COMPONENTS.md — delta for Crop Book v1 (calculator-driven)

> **WP:** SFA-S003-P004-WP-CB-1 · **From:** team_35 → team_100 → LOD400 §10
> **Rule:** these entries **extend** the canonical `COMPONENTS.md`. Class prefixes stay strict:
> `.cb-*` = book, `.cv-*` = calculator, `.af` = AssumptionField. Mobile `.gj-*` / desktop `.dt-*` shells unchanged.
> Mockup of every entry: `LOD300 Crop Book v1.html` (section ids `#s-audience … #s-rotation`).

---

## 18. AssumptionField — `<AssumptionField k="germination_rate" />`  **(NEW · team_00 directive)**

A planning assumption the user may adjust. **Never** a silent constant. Four mandatory parts; two states.

```html
<div class="af" data-assume-key="germination_rate">           <!-- add .is-open for expanded -->
  <div class="af__bar">                                       <!-- collapsed = this row only -->
    <span class="af__tag">◇ הנחה</span>
    <div class="af__lbl">נביטה<small>germination_rate</small></div>
    <div class="af__value">
      <div class="af__default">90<small>%</small></div>     <!-- (1) DEFAULT, always visible -->
      <button class="af__edit" aria-label="ערוך">✎</button>  <!-- toggles .is-open -->
    </div>
  </div>
  <div class="af__body"><div class="af__panel">
    <div class="af__override">                                <!-- (2) INLINE OVERRIDE -->
      <label>ערך מותאם</label>
      <span class="af__input"><input type="number" data-assume="germination_rate"
            data-scale="0.01" data-suffix="%" value="90" min="40" max="100"/><span>%</span></span>
      <button class="af__reset" data-reset data-default="90">↺ ברירת מחדל 90%</button>
    </div>
    <div class="af__explain">                                 <!-- (3) EXPLAINER: when / why / how -->
      <span class="when">מתי ולמה לשנות?</span>
      <h5>זרעים מאבדים חיוניות עם הגיל</h5>
      <p>…</p>
      <a class="af__more" href="https://nimrod.bio/seed-aging">קראו עוד · …</a>  <!-- (4) READ MORE → -->
    </div>
  </div></div>
</div>
```

**Contract**
- **Data:** reads `default · unit · explainer_he · post_url` from the `ASSUMPTIONS` registry (`assumptions.py`). The component is generic; only the key changes.
- **Behavior:** `.af__bar` click toggles `.is-open`. `[data-assume]` input writes the live value (× `data-scale`) and triggers recompute of every dependent calculator. `[data-reset]` restores `data-default`.
- **Echo:** any `[data-assume-echo="<key>"]` element mirrors the current value (e.g. the default shown inside a calc panel that consumes it).
- **An AssumptionField NEVER disables a calculator** — it always carries a default.
- **Launch-blocking content:** `germination_rate` and `bed_width` MUST have a non-null `post_url` (the `.af__more` link) at launch. Others may render `.af__more.is-soon` ("בקרוב") until published.
- **States to implement:** collapsed (bar only) · expanded (`.is-open`). No third state.

---

## 19. Calculator panel — `<CalcPanel no="1" calc="seed" />`  **(NEW)**

The reusable calculator card. Header (number + title + audience badge) → book-value chips it reads → optional inline AssumptionField(s) → user inputs → result + formula.

```html
<div class="cv" data-calc="seed">
  <div class="cv__head">
    <span class="cv__no">1</span>
    <div class="cv__title">כמה זרעים לקנות<small>seed quantity to buy</small></div>
    <span class="tier tier--leaf cv__aud">● שני הקהלים</span>     <!-- audience: leaf=both/gardener, sun=farmer -->
  </div>
  <div class="cv__body">
    <div class="cv__uses">book values it reads</div>
    <div class="bvrow">
      <span class="bv" data-book="rows" data-val="4">שורות/ערוגה <b>4</b>
        <a class="bv__link" href="…">↗ ספר</a></span>          <!-- CalcField §11 cross-link -->
      <!-- .bv--ast = value is unvalidated · .bv--missing = field missing (→ disabled) -->
    </div>
    <!-- optional inline AssumptionField(s) here (component 18) -->
    <div class="cv__uses">your inputs</div>
    <div class="cv__inputs">
      <label class="ipt"><label>אורך ערוגה</label>
        <span class="ipt__box"><input type="number" data-k="bed_len" value="30"/><span class="u">מ׳</span></span></label>
    </div>
    <div class="cv__result"><span class="lbl">לקנות</span><span class="big" data-result>—</span></div>
    <div class="cv__formula" data-formula></div>
    <div data-extra></div>
  </div>
</div>
```

**Contract**
- **`data-calc`** keys the pure formula (`CALC[kind]` in `cropbook-v1.js`; mirrors the catalog formula). Server pre-renders the default result; light JS recomputes on input.
- **`[data-book]` + `[data-val]`** = book operands (green chips). **`[data-k]`** = user inputs. AssumptionFields supply the rest from the shared registry.
- **Result targets:** `[data-result]`, `[data-formula]`, `[data-extra]`, and (for #10) `[data-popgrid]`.
- **Audience badge:** `tier--leaf` (both / gardener-facing) · `tier--sun` (farmer-only, e.g. #3·6·7·9·12·13·14).
- **Units always shown** on every operand, input, and result.

### 19a. Disabled calculator — `.cv.is-disabled`
A required **book** field is MISSING. Render the card greyed, name the field, promise re-enable, and offer request-info. Inputs locked (`.cv__inputs.is-locked`).

```html
<div class="cv is-disabled"> …head… 
  <div class="cv__disabled">
    <span class="ic">🔒</span>
    <div><h5>חסר שדה אחד</h5>
      <p>המחשבון יידלק כש־<code>seeds_per_gram</code> יתמלא.</p>
      <a class="reqinfo">◐ בקשו השלמת נתון</a></div>
  </div>
</div>
```
Only a **MISSING** field disables — never UNVALIDATED, an AssumptionField, or a user input.

### 19b. Grouped sequence — `.cv-seq`
Calculators whose outputs feed each other (seed→sow→nursery **#1 → #3 → #4**) stack with no gap; dark `.cv-seq__link` connectors name the carried value. Maps to the typed-output contract (Catalog §8 → Planner/Tasks).

### 19c. Population layout — `data-calc="pop"` + `[data-popgrid]`
#10 renders a spacing **grid** (`.popgrid i` circles, `repeat(rows, …)`), not only a number. Driven by `rows_per_bed` and the `bed_width` AssumptionField.

---

## 20. Provenance / confidence cues  **(NEW · §2.5)**

The three field-states from the Gap-Fill Plan, as reusable inline cues. Used in `.hv`, `.fg`, `.ptable` cells, and calc chips.

| Cue | Markup | When |
|-----|--------|------|
| **VALIDATED** | plain value | `winning_source_class ∈ {EX,NI}` or `confidence ≥ τ` |
| **UNVALIDATED** | `<span class="tip">2.1<span class="ast">*</span><span class="tip__pop">…</span></span>` | low-confidence / WR·WB·UC source |
| **MISSING** | `<span class="val--missing">— <a class="reqinfo">◐ בקשו נתון</a></span>` | no enrichment row |

- **`.ast`** asterisk (amber) **propagates**: a calculator that consumes an unvalidated value shows `*` on its output/pill.
- **`.tip__pop`** = hover/focus tooltip (keyboard accessible via `:focus-within`).
- **`.reqinfo`** = request-info CTA → `POST /api/v1/contribute` with `kind="request-info"`.
- **Drill-down hierarchy** — `.prov` rows show every source (`.prov__cls--ex/ni/pr/wr`), the winner (`.is-winner`), and a `.confbar`. Surfaced **only** in Drill-down; Simple/Full show the single winning value.

---

## 21. Audience switch — `<AudienceSwitch />`  **(NEW · §2.1)**

Persistent Cards⇄Table toggle in the book header. Same data, different density.

```html
<div class="aud" data-aud-switch="<scope-id>">
  <button class="aud__opt is-active is-cards" data-view="cards">▦ כרטיסים<small>גנן/לומד</small></button>
  <button class="aud__opt is-table" data-view="table">▤ טבלה<small>חקלאי</small></button>
</div>
```
JS shows/hides `[data-aud-view="cards|table"]` within `#<scope-id>`; selection persisted client-side. Cards is the default for `/crop-book/`.

## 22. Depth tabs — `<DepthTabs />`  **(NEW · §2.2)**

Simple / Full / Drill-down toggle on the crop page (one route). Same pattern: `[data-depths]` → `[data-depth-view]`.

## 22. Per-crop depths — topic taxonomy  **(NEW · revision · all three depths)**

All three depths are organised by a single **13-topic taxonomy** (`CROP_TOPICS`), matching the canonical structure of the JMF MasterClass sheets so the page reads as a growing plan, not a flat field list. Topics are colour-coded (`--t-nursery/grow/harvest/yield/inputs/pest`):

`זנים · מרווח ופריסה · ציוד וכיוונון · קרקע ודישון · הכנת ערוגה · זריעה/שתילה · השקיה · טיפוח ועישוב · מזיקים ומחלות · קציר · שטיפה ואחסון · רצף וחברה` (+ יבול/הכנסה for the calc-facing values).

- **Simple** — `.tsum` grid of `.tcard` topic-summary cards (1–2 key numbers each) + headline values + live yield calc.
- **Full** — collapsible `.topic` sections, one per subject; every mandatory field sits under its topic. New JMF-derived fields are tagged **"מוצע"** pending schema ratification.
- **Drill-down** — (a) `.vtable` **variety-comparison table** with an averages `<tfoot>`; (b) `.refsheet` **per-source reference sheet** at JMF depth (source tabs EX/PR/WR → `.reftopic` rows in canonical JMF order, each with per-topic provenance + key/values + step bullets). This is the "a full page at least as detailed as the JMF original" requirement.

## 23. Rotation hint chip — `.rothint`  **(NEW · §2.6)**

Informational chip derived from `crop_families`. Not a calculator. Gap = `rotation_gap_seasons` AssumptionField (default 3).

```html
<div class="rothint"><span class="rothint__icon">⟳</span>
  <div>אל תעקבו אחרי <b>חסתיים</b> באותה ערוגה במשך <b>3 עונות</b>.</div>
  <span class="meta">family: Asteraceae</span></div>
```

---

## 24. Main nav — `.sh__nav` / `.sh__nav--mobile`  **(NEW · revision)**

Persistent top-level switch across the four product surfaces. Lives in every `.sh__bar`.

```html
<nav class="sh__nav">
  <a class="is-active" href="/book/">▤ ספר גידולים</a>
  <a class="is-calc"   href="/calc/">∑ מחשבון</a>
  <a class="is-market" href="/market/">₪ מחירון</a>
</nav>
<span class="sh__nav__sp"></span>
<button class="sh__acct"><span class="av">נ</span>החשבון שלי</button>
```
- `.is-active` colors by surface: book = leaf, `.is-calc` = sun, `.is-market` = tomato.
- **Mobile** uses `.sh__nav--mobile` — a 4-item bottom tab bar (ספר · מחשבון · מחירון · חשבון).
- Account (`.sh__acct`) is the entry point to the future user-account module (stable hook).

## 25. Field info — `.finfo` + Hebrew dictionary  **(NEW · revision — "every field, a designed tooltip")**

**The entire UI is Hebrew, including field names.** No raw DB key is ever shown to the user. Each field is marked `data-field="<key>"`; `cropbook-v1.js::FIELD_INFO` holds `[שם עברי, הסבר מלא, db_key]`. `injectFieldInfo()` fills the Hebrew label (if empty) and appends a `.finfo` ⓘ affordance with a designed tooltip (Hebrew name + full explainer + the technical key in mono, for dev reference only).

```html
<dt data-field="seeds_per_gram"></dt>   <!-- JS → "זרעים לגרם" + ⓘ tooltip -->
```
Used on: the Full-depth field grid (all 16), Simple headline values, search filter labels, and calculator book chips. The raw snake_case key survives **only** inside the tooltip and the spec docs — never as product chrome.

## 26. Card season — `.ccard__season`  **(NEW · revision)**

`planting_season` is a fundamental datum and now appears on the **compact card**, not only the crop page.

```html
<div class="ccard__season"><span class="g">☀</span>סתיו · אביב</div>
```

## 27. Editable book value — `.bv.is-editable` / `.is-overridden`  **(NEW · revision)**

Calculator book chips can be made user-editable (e.g. #10 population). The user overrides the reconciled value inline; the chip is **clearly marked** as deviating from the book and offers a one-tap restore.

```html
<span class="bv is-editable" data-book="rows" data-val="4">
  <span data-field="rows_per_bed">שורות</span>
  <input class="bv__in" type="number" value="4" data-orig="4"/>
  <span class="bv__flag">שונה מהספר</span>            <!-- shown only when .is-overridden -->
  <a class="bv__link" href="#">↗ ספר</a>
  <button class="bv__restore">↺ ספר</button>           <!-- shown only when .is-overridden -->
</span>
```
On override: chip gets `.is-overridden` (dashed tomato border + "שונה מהספר" flag), the book cross-link hides, the restore button appears, and the calculator recomputes from the user value. The book's own `value_best` is never mutated.

## 28. Multi-parameter filter bar — `.ftop`  **(NEW · revision · top of the list page)**

Filters live **at the top of the book list page**, above the results (not a sidebar, not a separate screen). A search row (free text + **mandatory reset** `[data-filter-reset]` + live result count) над a horizontal row of filter groups: **family** · **growing season** (season chips *or* a specific **sow date** input) · **sow vs transplant** (`זריעה ישירה / שתילה`, single) · **summer-shade — Israel** (`needs_summer_shade`, single) · frost tolerance · **DTM range** · book completeness.

- **Default = search all** — multi-select groups start empty; single-select groups start on "הכל"; the count shows the full set. Nothing is pre-narrowed.
- **Reset** restores every group to its `data-default-on` chip and clears the text + date inputs.
- Results update **in place** (Cards or Table). Every filter label carries the field tooltip (component 25).

## 29. Calculator dashboard — `.calc-page` / `.calc-dash` / `.modcard`  **(NEW · revision · §2.3b)**

The `/calc/` module is a **dashboard**, not a wizard: a shared dark **context** strip (`.calc-context`: crop + area + target date) drives every calculator; each calculator is an independent **module card** (`.modcard`, keyed by number) laid out in a grid and grouped by `.dash-group`. Modules are **wired** — outputs flow between cards (`.modcard__feed` "→ מזין מודול 3" / "← מ‑מודול 1") and into a sticky **summary** (`.calc-summary`, each row tagged with its source module) — and one **export** block (`.calc-export` → PDF / CSV) serializes the whole plan. Disabled modules follow the §2.5 partial rule in place.

> **Architecture contract (for the build teams):** this composition is the code structure too — **one calculator = one module** (a self-contained partial/service keyed by `data-calc`), and the `/calc/` page is a **dashboard** that mounts those modules and aggregates the summary. The same module embeds standalone inside a crop page (§2.3). Modules + dashboard, 1:1 between design and code.

---

## Brand note — system logo

The hand-painted garden/radish logo is **not** used for the app. The product ships a **system mark** (`#sfa-logo` SVG symbol): a sprout rising from three planting beds with a seed-bud — agriculture + planning, reads on both paper and dark chrome. Defined once, referenced via `<use href="#sfa-logo"/>`.


---

## Extended existing components

- **§3 Crop card (`.gj-cropcard` → `.ccard`)** gains a corner `state` dot (✓ complete / ! partial) and a row of calculator pips (lit = enabled).
- **§4 Pro table (`.cb-table` → `.ptable`)** gains `calc-col` header + `.calc-cell` columns exposing farmer calculators (#1/#7/#9) inline, with `.ast` / `.val--missing` cues.
- **§11 CalcField** is now the `↗ ספר` `.bv__link` inside every CalcPanel book chip (unchanged contract, re-housed).
