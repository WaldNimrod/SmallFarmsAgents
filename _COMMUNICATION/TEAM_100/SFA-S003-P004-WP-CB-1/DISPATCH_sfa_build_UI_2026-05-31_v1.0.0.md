# DISPATCH — SFA-S003-P004-WP-CB-1 (UI slice) — team_100 → build slice — v1.0.0

**Date:** 2026-05-31
**From:** team_100 (Chief Architect / orchestrator)
**To:** build slice (team_10 stand-in — Claude sub-agent; IR#1: builder ≠ team_100 Opus architect ≠ team_190 non-Claude validator)
**Gate:** L-GATE_B (UI slice) · **WP:** SFA-S003-P004-WP-CB-1 · **Branch:** `claude/wp-cb-1-ui-2026-05-31`

---

## 1. Assignment

Recreate the **team_35 LOD300 design** into the **Slim4/PHP delivery tier** (`sfa_delivery/`). The design files
are a visual/behavior **contract**, not code to ship verbatim — rebuild in the tier's plain-PHP template idiom
(`Template::render('pages/x',[...])` / `Template::partial('macros/x',[...])`, thin routes → controllers →
`App\Lib\Db` static methods → array data passed to templates).

**Backend is LOCKED — consume, never edit:** `organic_market_agent/crop_book/{calculators.py, assumptions.py,
calculator_meta.py, field_policy.py}`. The UI reads the ingest payload (per-field `field_state` + `ASSUMPTIONS`,
already emitted by `sfa_ingest_push.py`).

## 2. Read first (binding)

1. `_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-1/FIELD_INTERFACE_MAP_v1.0.0.md` — **the binding field contract**
   (design key → canonical name → layer; the §1 alias resolver; τ=0.40 prov rule). Obey it exactly.
2. `_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-1/HANDOFF_PACKAGE/` — `design/{tokens.css, cropbook-v1.css,
   cropbook-v1.js, LOD300 Crop Book v1.html}`, `spec/{TEMPLATES,COMPONENTS,DESIGN_TOKENS}-delta.md`, `README.md`.
3. `_aos/work_packages/S003/SFA-S003-P004-WP-CB-1/LOD400_spec.md` §5 (calc contracts), §7 (UI contract), §10 (mockups), §11 (ACs).
4. Existing tier: `sfa_delivery/{app/routes.php, app/Controllers/CropBookViewController.php, app/Lib/{Db,Template}.php,
   templates/{_layout.php, shell/*, macros/*, pages/book_*}.php, public_assets/{css/*,js/sfa.js}}`.

## 3. Scope (build, in this order)

1. **Design system port** → `public_assets/css/tokens.css` (merge the v2 white-green `--gj-*` + `--cb-*` tokens +
   Carmela `@font-face`; keep existing tokens that other pages use), add `public_assets/css/crop-book-v1.css`
   (component layer from `cropbook-v1.css`, adapted to our class structure), and `public_assets/js/crop-book-v1.js`
   (port `cropbook-v1.js`; keep ES5-ish, no framework). Place Carmela + the 4 `wc-*.png` into `public_assets/`
   (fonts/, img/crops/ — web-optimized; see Phase 3 note). Wire the new CSS/JS into the crop-book pages' `<head>`/footer.
2. **Macros** (`templates/macros/`): `assumption_field.php`, `calc_panel.php`, `calc_seq.php`, `prov_value.php`,
   `prov_table.php`, `audience_switch.php`, `depth_tabs.php`, `rotation_hint.php` — contracts in `spec/TEMPLATES-delta.md §2`
   + `spec/COMPONENTS-delta.md`. `prov_value` is the single cue authority (validated/`*`unvalidated/`—`missing); only
   MISSING required field → `.cv.is-disabled`.
3. **Pages:** `book_index` (Cards default ⇄ Table density via `?view=`; multi-param filter rail beside results;
   pagination) — may extend existing `book_entry.php`/`book_table.php`; `book_crop.php` three depths (`?depth=simple|full|drill`,
   13-topic ordering, headline values, calc panels, AssumptionField, rotation hint, drill provenance);
   `/calc/` dashboard page (modules grid + sticky summary + export hooks) — extend `hub_calc.php` / add `pages/calc_dash.php`.
   Calculator **modal overlay** for in-context small calcs on the crop page.
4. **Endpoints** (`app/routes.php` + a controller, e.g. `AssumptionsController`/extend `CropsController`):
   `GET /api/v1/assumptions` (serve the `assumptions.py` registry as JSON — read via a small bridge or a generated
   static JSON refreshed by ingest; default+unit+explainer_he+post_url per key); `POST /api/v1/contribute` with
   `kind="request-info"` `{field_name, crop_slug}` — lightweight capture (append to a log/table; no triage UI, per Q5).
5. **Data plumbing:** extend `App\Lib\Db` so crop/variety reads expose, per field, `value_best` + `field_state` +
   `winning_source_class` (from the ingest payload/mirror) and the categorical `crop_attribute` values
   (`planting_method`, `frost_tolerance_class`, `sowing_months[]`). Resolve names through the FIELD_INTERFACE_MAP §1
   alias map. `field_label()` helper resolves `field_name → (Hebrew label, explainer)`; never print a raw DB key.
6. **JS↔Python calc parity:** the 6 interactive calcs (#1,#7,#8,#9,#10,#12) recompute client-side via the ported
   `CALC[kind]`; server still renders the default result. Add a parity check (AC-11).
7. **Tests** (`sfa_delivery/tests/`): macro render tests (prov_value 3 states; calc_panel disabled when required
   MISSING; assumption_field renders default+override+link), route smoke for the new routes, and a JS↔Python parity
   fixture. Keep `composer test` green; `php -l` clean.

## 4. Acceptance criteria (= LOD400 §11, UI subset)

- **AC-10** UI present: audience switch (Cards/Table), Simple/Full/Drill, AssumptionField (default+override+explainer+link),
  complete/partial rendering via `prov_value`.
- **AC-11** JS calc mirror (#1,7,8,9,10,12) parity-tested vs Python outputs.
- **AC-13 (local proxy)** a COMPLETE crop shows enabled calcs with correct numbers; a PARTIAL crop shows `*`/`—` +
  a disabled calc + request-info CTA. (Live smoke is post-deploy; here verify against the local mirror / fixtures.)
- **AC-12** `validate_aos.sh` 0 FAIL; `composer test` + `pytest tests/crop_book/` green; **no LOD500_LOCKED file touched**
  (do NOT edit the locked backend modules or migrations).

## 5. Authority limits

- MAY write under `sfa_delivery/`, `public_assets/`, `tests/` (delivery), and commit to `claude/wp-cb-1-ui-2026-05-31`.
- MAY NOT edit `_aos/`, `_aos/roadmap.yaml`, the LOCKED Python backend (`crop_book/calculators.py|assumptions.py|
  calculator_meta.py|field_policy.py`), or any migration. MAY NOT push/merge or issue gate verdicts. MAY NOT deploy.
- If a backend gap blocks the UI (e.g. a field has no live data), render "מוצע/proposed" or MISSING per the field map —
  do NOT patch the backend. Log it for team_100.

## 6. Output

Write `_COMMUNICATION/TEAM_10/SFA-S003-P004-WP-CB-1/BUILD_REPORT_UI_v1.0.0.md` (§1 summary · §2 params/branch ·
§3 AC table w/ evidence · §4 findings · §5 `validate_aos.sh` + `composer test` output · §6 artifacts created/modified ·
§7 next step). Reference the LOD300 board for visual fidelity.

*Dispatched by team_100 · 2026-05-31 · IR#1 cross-engine (build = Claude sub-agent; L-GATE_V = non-Claude, Nimrod-run).*
