# TEMPLATES.md — delta for Crop Book v1

> **WP:** SFA-S003-P004-WP-CB-1 · extends canonical `TEMPLATES.md` (Flask/Jinja2 → Slim4/PHP tier).
> Delivery tier is **Slim4 / PHP on uPress**: every screen is a **server-rendered template + light JS** for the interactive calculators. No client routing; depth & audience are query params, not new routes.

---

## 1. Route map — additions / changes

| Route | Template | New params | Notes |
|-------|----------|-----------|-------|
| `/crop-book/` | `book_index` | `?view=cards\|table` | **Cards default.** `view` persisted client-side; server honors it on first paint. Same query, two density templates. |
| `/crop-book/<slug>/` | `book_crop` | `?depth=simple\|full\|drill` | One route, three depths. Server may default `depth` by audience cookie (gardener→simple, farmer→full). |
| `/crop-book/<slug>/variety/<vslug>/` | `book_variety` | — | Drill-down deep link (per-variety provenance). |
| `POST /api/v1/contribute` | — | `kind="request-info"` | New `kind` value emitted by every `.reqinfo` CTA on a MISSING field. Body adds `{ field_name, crop_slug }`. |
| `GET /api/v1/assumptions` | — | — | **NEW.** Serves the `ASSUMPTIONS` registry (default · unit · explainer_he · post_url) so the UI renders AssumptionFields without per-crop data. CORS-open. |

No change to the `/market/*`, `/calc/*`, hub, or community routes.

---

## 2. New partials / macros

```
templates/macros/
├── assumption_field.html   {{ assumption_field('germination_rate') }}   ← reads ASSUMPTIONS registry
├── calc_panel.html         {{ calc_panel(crop, no=1, calc='seed') }}    ← renders book chips + inputs + default result
├── calc_seq.html           {{ calc_seq([1,3,4], crop) }}                ← grouped sequence wrapper
├── prov_value.html         {{ prov_value(field) }}                      ← validated / *unvalidated / —missing cue
├── prov_table.html         {{ prov_table(field) }}                      ← drill-down source hierarchy
├── audience_switch.html
├── depth_tabs.html
└── rotation_hint.html      {{ rotation_hint(crop.family) }}
```

### `prov_value(field)` — the single cue authority
Given a `crop_field_enrichment` row, emits exactly one of:
- **validated** → plain `{{ value }} {{ unit }}`
- **unvalidated** → `… <span class="ast" title="…">*</span>` (+ `prov_tooltip`)
- **missing** → `— <a class="reqinfo" …>◐ בקשו נתון</a>`

Every value rendered anywhere on the crop page / table / cards goes through this macro. The complete/partial rollup is `all(prov_value == validated for field in MANDATORY)`.

### `calc_panel(crop, no, calc)`
1. Resolves each book operand via `prov_value`. If any required operand is **missing**, renders `.cv.is-disabled` (19a) instead of inputs.
2. Pulls AssumptionField defaults from the registry, embeds `assumption_field()` inline where the catalog lists one.
3. Server computes the **default** result (so the page is useful with JS off); `cropbook-v1.js` re-computes on input.

---

## 3. Page contract — `book_crop` (the three depths)

```
book_crop(crop, depth):
  crop_hero(crop, state=complete|partial)        # state badge from rollup
  depth_tabs(active=depth)
  ── depth == simple ──
     headvals(crop, 4 fields)                    # all via prov_value
     calc_panel × {key calcs: 1,2,4,5,8,10,11 ∩ enabled}   # 3–4 surfaced
     rotation_hint(crop.family)
  ── depth == full ──
     field_grid(crop, MANDATORY 16)              # every mandatory field, each prov_value
     calc_panel × {all enabled}                  # grouped where catalog groups (calc_seq)
  ── depth == drill ──
     variety_cards(crop.varieties)
     prov_table(field) per surfaced field        # source hierarchy + confidence
  contrib_strip(context="book.<slug>")           # community surface (unchanged)
```

`view`/`depth`/`audience` never change the data query — only which template + density renders the same `value_best` set. This keeps the SSoT promise from the prior LOD300 (§3 of `HANDOFF_LOD300.md`).

---

## 4. JS surface (light, per delivery tier)

`cropbook-v1.js` (vanilla, ~9 KB) handles only: AssumptionField expand/override/reset, calculator recompute (`CALC[kind]` mirrors catalog formulas), audience switch, depth tabs, tooltip focus, **field-info injection** (`FIELD_INFO` → Hebrew label + tooltip from `data-field`), **editable book-value override** (`.bv__in` → `.is-overridden` + recompute), and **filter chips**. No framework. Mirrors the existing `sfagent-crop-book.js` pattern (Q6 of prior handoff = vanilla).

---

## 5. Revision additions (from review)

- **Global nav (`.sh__nav`)** ships in `shell/*.html` base — ספר / מחשבון / מחירון + account. Active state per the current route. Mobile = bottom tab bar. The account link is the stable hook to the future user-account module.
- **Filters on the list page (`book_index`)** — the multi-parameter rail (family · season · sow-vs-transplant · frost · DTM range · completeness) renders **beside the results**, not as a separate screen. Same query, filtered; switches between Cards and Table density. (An optional full-width `/crop-book/search/` may reuse the same filter partial, but it is not the default path.)
- **`/calc/` (hub_calc) is a dashboard** that composes calculator **modules**. Each calculator is its own partial/service (`calc/<name>.html` + a pure function keyed by `data-calc`); the page mounts them in a grid under a shared context and aggregates a sticky summary. Export endpoints:
  - `GET /calc/export.pdf?plan=<state>` — server-rendered PDF of the whole plan.
  - `GET /calc/export.csv?plan=<state>` — CSV for re-import to season planning.
- **Architecture (modules + dashboard) is the build contract** — design and code share one shape: one calculator = one module; `/calc/` = the dashboard; the same module embeds inside a crop page. Define this to the teams so the code structure mirrors the design.
- **Hebrew-only field labels** — no template ever prints a raw `field_name` to the user. The `field_label()` helper resolves `field_name → (Hebrew name, explainer)` from the same registry the UI's `FIELD_INFO` mirrors; the DB key appears only in the tooltip (dev reference) and these spec docs. Field micro-labels use the body face (not mono/uppercase) so Hebrew is legible.
