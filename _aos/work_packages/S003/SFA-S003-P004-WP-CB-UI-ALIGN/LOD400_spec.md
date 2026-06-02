---
id: SFA-S003-P004-WP-CB-UI-ALIGN-LOD400
wp: SFA-S003-P004-WP-CB-UI-ALIGN — Delivery-tier visual alignment to the team_35 LOD300 (Class A)
gate: L-GATE_S (team_190, non-Claude / Cursor)
status: LOD400 — build mandate · authored 2026-06-02
author: team_100 (Chief System Architect, Claude Code)
date: 2026-06-02
class: A (crop-book + calculator + global app-shell — design already exists in team_35 v2)
design_ssot: _COMMUNICATION/team_35/SFA-S003-P004-WP-CB-1/HANDOFF_PACKAGE/design/
builder: team_10 (Claude/Sonnet sub-agent)
validator: team_190 (non-Claude, Cursor)
team_00_rule: "interface/style/structure EXACT to team_35; content/fields from code; never guess a missing template"
decisions:
  - shell_scope: SITE-WIDE / uniform (team_00, 2026-06-02) — .sh replaces .gj-shell AND .dt-shell across the whole system
  - token_cleanup: FULL reconciliation — repoint all legacy --paper/--ink/etc. to --gj-*, delete legacy cream tokens
---

# LOD400 — WP-CB-UI-ALIGN Class A: build mandate

> **Precision gate.** This spec is detailed enough to implement without further design lookups. Source-of-truth
> line numbers and verbatim blocks are inline. The build (team_10) must not guess any missing template — Class B
> surfaces are out of scope. Delivery-tier only (`sfa_delivery/`); no Python, no migrations, no `_aos/`.

## 0. Scope

**IN (Class A):** unify the palette (kill cream), build the team_35 `.sh` app-shell **site-wide**, bring
crop-book + calculator to exact visual fidelity, fix `/calc` (JS load + 14-calc surfacing + export).

**OUT:** Class B *content* styling (hub/home, market, search, community, about, account — WP-CB-UI-CLASSB,
blocked on team_35 v2 templates). Data/backend/migrations. Data findings F-STAT-001/002, F-MKT-002 (separate
data follow-up). The non-kg revenue conversion (F-50-patch01-01).

**Shell-scope decision (team_00):** the `.sh` shell is built **once, site-wide** and replaces BOTH legacy shells.
Class B pages keep functioning on the new shell with unstyled *content* until their WP — structure/template/style
are uniform across the whole system now.

---

## Deliverable 1 — Unify the palette (`sfa_delivery/public_assets/css/tokens.css`)

**Root cause:** `tokens.css:12` defines `--paper: #f5f3ec` (cream "Cool Stone") and `:86` sets
`body { background: var(--paper) }` → whole site cream. Design SSoT ground = `--gj-paper #f8fbf8`.

**Key de-risking fact:** the 7 legacy cream tokens are consumed via `var(--…)` **only inside tokens.css itself**
(its own `body`/`.card`/`.btn-ghost`/`.t-body-sm` foundation rules). **Zero** legacy-token usages exist in any
other CSS file (gj/hub/community/crop-book-deep/crop-book-v1/desktop/desktop-extras) — those were authored
against `--gj-*`. So legacy `var(--paper)` reconciliation is contained to tokens.css.

**⚠ D1 ALSO covers `--gj-*` REDEFINITIONS, not just `--paper` consumers (folds F-QA-01, per L-GATE_S
F-190-UIALIGN-01).** A leftover v1 cream `:root` in `gj.css:4–10` redefined `--gj-paper #f6f1e3` (+ `-2/-3/--gj-ink/
-soft/--gj-line`); because gj.css loads after tokens.css it overrode the v2 white ground → cream `body`. D1 must
remove every cream `--gj-*` *redefinition* across served CSS (not only `var(--paper)` consumers) so the v2 values
in tokens.css win. Verify: `grep -rnE -- '--gj-paper\s*:' sfa_delivery/public_assets/css/` returns exactly one
line (tokens.css = #f8fbf8).

**Edits (tokens.css):**

| line | from | to |
|---|---|---|
| `:86` | `body { background: var(--paper) }` | `var(--gj-paper)` |
| `:87` | `body { color: var(--ink) }` | `var(--gj-ink)` |
| `:104` | `.t-body-sm { color: var(--ink-soft) }` | `var(--gj-ink-soft)` |
| `:119` | `.card { background: var(--paper) }` | `var(--gj-paper)` |
| `:120` | `.card { border: 1px solid var(--line) }` | `var(--gj-line)` |
| `:139` | `.btn-ghost { color: var(--ink); border-color: var(--ink) }` | both → `var(--gj-ink)` |
| `:140` | `.btn-ghost:hover { background: var(--ink); color: var(--paper) }` | `var(--gj-ink)` / `var(--gj-paper)` |
| `:12–18` | legacy defs `--paper`,`--paper-2`,`--paper-3`,`--line`,`--ink`,`--ink-soft`,`--soil` | **delete the 7 lines** |
| `:5, :11, :164, :253` | "Cool Stone" mentions + the `#f5f3ec` changelog comment | **scrub** (delete/rename so served CSS has zero "Cool Stone") |

Mapping reference (already defined in tokens.css `--gj-*` block, ~lines 174–237): paper→`--gj-paper` #f8fbf8 ·
paper-2→#eef4ee · paper-3→#dde8dd · line→`--gj-line` #dce6dc · ink→`--gj-ink` #1f2a22 · ink-soft→`--gj-ink-soft`
#5d6b5e · soil→`--gj-soil` #8b5d2f.

**Build must verify** these `--gj-*` tokens already exist in served tokens.css before deleting legacy ones,
and that the nav-active tokens exist: `--gj-leaf-deep` #4d6a2c, `--gj-sun-deep` #a4711a, `--gj-tomato-deep`
#8e3018, `--gj-soil`, `--gj-r-pill`, `--gj-paper-2`. If `--gj-sun-deep` is missing (it was the one "new ramp
value" in DESIGN_TOKENS-delta), add it: `--gj-sun-deep: #a4711a;`.

`.tier--soil`/`.pill--soil` are class names (resolve via `--gj-soil*`), not token refs — leave unchanged.

**→ AC-1.**

---

## Deliverable 2 — Build the team_35 `.sh` app-shell (site-wide)

### 2a. Add the `.sh` shell CSS to `public_assets/css/crop-book-v1.css`

The served crop-book-v1.css has no `.sh` rules. Append the shell + nav rules **verbatim** from the design SSoT
`…/design/cropbook-v1.css` §1 (lines 98–118) and §11 (lines 463–484). Verbatim block to add:

```css
/* ── APP SHELL (team_35 LOD300 §1) ── */
.sh { display: flex; flex-direction: column; min-height: 100%; }
.sh__bar { display: flex; align-items: center; gap: 12px; padding: 12px 18px; border-bottom: 1px solid var(--gj-line); background: var(--gj-paper); }
.sh__mark { width: 30px; height: 30px; object-fit: contain; }
.sh__name { font-family: var(--gj-font-brand); font-size: 18px; font-weight: 700; line-height: 1; }
.sh__name small { display: block; font-family: var(--gj-font-mono); font-size: 9px; font-weight: 400; letter-spacing: .1em; color: var(--gj-ink-soft); margin-top: 3px; }
.sh__bc { font-family: var(--gj-font-mono); font-size: 11px; color: var(--gj-ink-soft); margin-inline-start: 6px; }
.sh__bc a { color: inherit; text-decoration: none; }
.sh__bc strong { color: var(--gj-ink); }
.sh__tools { margin-inline-start: auto; display: flex; gap: 8px; }
.sh__icon { width: 32px; height: 32px; border-radius: 9px; border: 1px solid var(--gj-line); background: var(--gj-paper); display: grid; place-items: center; color: var(--gj-ink-soft); cursor: pointer; font-size: 15px; }
.sh__body { padding: 18px; }
.sh__foot { margin-top: auto; display: flex; align-items: center; gap: 8px; padding: 10px 18px; border-top: 1px solid var(--gj-line); font-family: var(--gj-font-mono); font-size: 10px; color: var(--gj-ink-soft); }
.sh__foot .dot { flex: none; width: 8px; height: 8px; border-radius: 50%; background: var(--status-fresh); } /* flex:none per F-QA-03 */

/* ── MAIN NAV (team_35 LOD300 §11) ── */
.sh__nav { display: flex; align-items: center; gap: 2px; margin-inline-start: 8px; }
.sh__nav a { display: inline-flex; align-items: center; gap: 6px; padding: 7px 13px; border-radius: var(--gj-r-pill); font-size: 13px; font-weight: 700; color: var(--gj-ink-soft); text-decoration: none; white-space: nowrap; }
.sh__nav a .g { font-size: 14px; }
.sh__nav a:hover { background: var(--gj-paper-2); color: var(--gj-ink); }
.sh__nav a.is-active { background: var(--gj-leaf-deep); color: #fff; }
.sh__nav a.is-active.is-calc { background: var(--gj-sun-deep); }
.sh__nav a.is-active.is-market { background: var(--gj-tomato-deep); }
.sh__nav__sp { flex: 1; }
.sh__acct { display: inline-flex; align-items: center; gap: 7px; padding: 5px 12px 5px 6px; border: 1px solid var(--gj-line); border-radius: var(--gj-r-pill); font-size: 12px; font-weight: 700; color: var(--gj-ink); background: var(--gj-paper); cursor: pointer; }
.sh__acct .av { width: 22px; height: 22px; border-radius: 50%; background: var(--gj-soil); color: #fff; display: grid; place-items: center; font-size: 11px; }
.sh__nav--mobile { display: flex; gap: 4px; padding: 8px 12px; border-top: 1px solid var(--gj-line); background: var(--gj-paper-2); }
.sh__nav--mobile a { flex: 1; flex-direction: column; gap: 2px; font-size: 10px; padding: 6px 2px; text-align: center; }
.sh__nav--mobile a .g { font-size: 17px; }
/* mobile-nav color + active (design-gap remediation, F-QA-04 / L-GATE_S F-190-UIALIGN-03 — team_35 to confirm) */
.sh__nav--mobile a { display: flex; align-items: center; justify-content: center; color: var(--gj-ink-soft); text-decoration: none; font-weight: 700; }
.sh__nav--mobile a.is-active { color: var(--gj-leaf-deep); }
.sh__nav--mobile a.is-active.is-calc { color: var(--gj-sun-deep); }
.sh__nav--mobile a.is-active.is-market { color: var(--gj-tomato-deep); }
```

### 2b. Add the responsive toggle (NOT in SSoT — author it)

The design ships both nav variants `display:flex` with no breakpoint (they live in separate mockup frames).
Add, at the legacy 900px threshold (the prior gj↔dt toggle lived at desktop-extras.css:526):

```css
/* Responsive nav switch — desktop top bar vs mobile bottom tab bar (project-authored, not in SSoT) */
@media (max-width: 899px) { .sh__nav, .sh__acct { display: none; } }
@media (min-width: 900px)  { .sh__nav--mobile { display: none; } }
```

### 2c. Rewrite the `_layout.php` body to emit ONE `.sh` block

Today (`_layout.php:81–83`) content renders THREE chrome contexts (nav.php + mobile.php → `.gj-body` +
desktop.php → `.dt-content`) and `$body_html` is echoed TWICE into the DOM. Replace lines 81–83 with a single
`.sh` shell that echoes `$body_html` once into `.sh__body`. Use the exact LOD300 desktop structure
(`…/design/LOD300 Crop Book v1.html` lines 70–82) + mobile bar (lines 1217–1222):

```php
<div class="sh">
  <div class="sh__bar">
    <svg class="sh__mark"><use href="#sfa-logo"/></svg>
    <div class="sh__name">SFA<small><?= $h($page_sub) ?></small></div>
    <nav class="sh__nav">
      <a class="<?= $active==='crop-book' ? 'is-active' : '' ?>" href="/crop-book/"><span class="g">▤</span>ספר גידולים</a>
      <a class="is-calc <?= $active==='calc' ? 'is-active' : '' ?>" href="/calc/"><span class="g">∑</span>מחשבון</a>
      <a class="is-market <?= $active==='market' ? 'is-active' : '' ?>" href="/market/"><span class="g">₪</span>מחירון</a>
    </nav>
    <span class="sh__nav__sp"></span>
    <button class="sh__acct"><span class="av">נ</span>החשבון שלי</button>
    <a class="sh__icon" href="/search" title="חיפוש">⌕</a>
  </div>
  <div class="sh__body"><?= $body_html ?></div>
  <nav class="sh__nav--mobile">
    <a class="<?= $active==='crop-book' ? 'is-active' : '' ?>" href="/crop-book/"><span class="g">▤</span>ספר</a>
    <a class="is-calc <?= $active==='calc' ? 'is-active' : '' ?>" href="/calc/"><span class="g">∑</span>מחשבון</a>
    <a class="is-market <?= $active==='market' ? 'is-active' : '' ?>" href="/market/"><span class="g">₪</span>מחירון</a>
    <a href="/account"><span class="g">◔</span>חשבון</a>
  </nav>
  <div class="sh__foot"><span class="dot"></span><?= $h($foot_text) ?></div>
</div>
```

Notes for the build:
- The `is-active`/`is-calc`/`is-market` class composition must match the CSS: the calc link always carries
  `is-calc` and gets `is-active` added when active (so `.is-active.is-calc` fires sun-deep); same for market.
  Trim double spaces if you prefer, but keep both classes present.
- `$active` value set (confirmed across templates): `home`, `crop-book`, `market`, `calc`, `community`, `''`.
  `home`/`community`/`''` → no surface pill active (correct: those map to the brand mark / future account).
- `$page_sub` defaults to `'חקלאות קטנה'` (`_layout.php:6`) — matches the design's `<small>` subtitle.
- Account link target `/account` may 404 today — acceptable stable hook (the account module is future). Confirm
  it does not throw; if the router 500s on unknown routes, point it to `#` instead.
- **Intentional deviation (L-GATE_S F-190-UIALIGN-02):** `.sh__icon` is rendered as `<a href="/search">` (a real
  navigable link to the search route), where the LOD300 mockup used a `<button>`. The `<a>` is correct for a nav
  target; `.sh__icon` CSS styles both identically. Noted, not a defect.

### 2d. `#sfa-logo` symbol — define once, reference via `<use>`

Inline the design symbol once at body-open (next to the existing `@readfile(icons.svg)` at `_layout.php:79`).
Verbatim (`…/LOD300 Crop Book v1.html` lines 12–19):

```html
<svg width="0" height="0" style="position:absolute" aria-hidden="true"><symbol id="sfa-logo" viewBox="0 0 48 48">
  <rect x="1.5" y="1.5" width="45" height="45" rx="12" fill="#3a4d22"/>
  <g fill="#9bb172"><rect x="12" y="34" width="6" height="4" rx="1.2"/><rect x="21" y="34" width="6" height="4" rx="1.2"/><rect x="30" y="34" width="6" height="4" rx="1.2"/></g>
  <path d="M24 33 V18.5" stroke="#f6f1e3" stroke-width="2.6" stroke-linecap="round"/>
  <path d="M24 24.5 C 19 24.5 15 21.5 14 16.5 C 20 16.5 24 19.5 24 24.5 Z" fill="#f6f1e3"/>
  <path d="M24 21.5 C 29 21.5 33 18.5 34 13.5 C 28 13.5 24 16.5 24 21.5 Z" fill="#cfe0b0"/>
  <circle cx="24" cy="15.5" r="2.4" fill="#d39a32"/>
</symbol></svg>
```

Per COMPONENTS-delta §24 Brand note: the hand-painted seedling mark is **not** used for the app — ship this
system mark, defined once, referenced via `<use href="#sfa-logo"/>`.

### 2e. Retirements

| target | action |
|---|---|
| `templates/shell/mobile.php` | retire — remove include `_layout.php:82` |
| `templates/shell/desktop.php` | retire — remove include `_layout.php:83` |
| `templates/partials/nav.php` (`.sfa-nav` 3rd bar) | retire — remove include `_layout.php:81` |
| `templates/shell/_mark_svg.php` | retire — replaced by `#sfa-logo` `<use>` |
| `public_assets/css/gj.css` lines 27–96 (`.gj-shell … .gj-foot__sep` chrome) | delete that block; **keep** the rest of gj.css (components from `.gj-eyebrow` onward still used) |
| `public_assets/css/desktop.css` (100% `.dt-*` shell) | retire whole file; remove `<link>` `_layout.php:65`; drop `'desktop'` from asset-version array `_layout.php:27` |
| `public_assets/css/hub.css` `.sfa-nav*` block (~line 382+) | delete that block; keep rest of hub.css |
| `public_assets/css/desktop-extras.css:526–529` (gj↔dt toggle) | delete; audit file — drop other dead `.dt-*` extensions; if wholly dead, retire file + `<link>` `_layout.php:66` + `'desktop-extras'` from array |
| desktop sidebar community feed (`desktop.php:77–93`, `CommunityFeed::recent()`) | **dropped from chrome** (not part of `.sh`); the community *page* keeps its own body feed — confirm community.php still renders its feed independently |

**Guard:** removing files referenced by the asset-version `foreach` is safe (`@filemtime` skips missing) but the
`<link>` tags MUST be removed or they 404. Keep `'tokens','gj','hub','community','crop-book-deep','crop-book-v1'`
in the array; remove `'desktop'` (and `'desktop-extras'` if retired).

**→ AC-2, AC-6.**

---

## Deliverable 3 — Crop-book + calculator visual fidelity

crop-book + calc already use the v2 component CSS (crop-book-v1.css, crop-book-deep.css). Once on the white
ground (D1) + `.sh` shell (D2) they should match the LOD300 frames. The build must **visually confirm** (not
assume) each frame matches: book-entry, crop simple/full/drill, calc-dash — palette, type, spacing, components.

Type: confirm `Carmela.ttf` (in design `assets/`) is served from `public_assets/` and `@font-face`-declared for
`--gj-font-brand` (the design tokens.css declares it with `src: url("assets/Carmela.ttf")` — the delivery tier
needs the font file copied into `public_assets/` and the `@font-face` `src` path corrected to the served
location). Frank Ruhl Libre + Assistant load from Google Fonts (already in `_layout.php:57`).

**→ AC-3.**

---

## Deliverable 4 — Fix `/calc`

### 4a. JS load (root cause F-CALC-002)

`_layout.php:69` gates `crop-book-v1.js` on `$active === 'crop-book'`; `/calc/` sets `$active='calc'` → JS never
loads → `SFA_CALC` undefined → panels inert. Change to:

```php
<?php if (isset($active) && in_array($active, ['crop-book', 'calc'], true)): ?>
<script defer src="/public_assets/js/crop-book-v1.js?v=<?= $h($asset_ver) ?>"></script>
<?php endif; ?>
```

### 4b. Surface 14 calculators (F-CALC-003)

SSoT: `_COMMUNICATION/TEAM_100/SFA-S003-P004-WP-CB-1/CALCULATOR_CATALOG_v1.0.0.md` §2. Render all **14** catalog
cards on the calc dash (`templates/pages/calc_dash.php`). **6 are interactive** (CALC fns exist in
crop-book-v1.js): #1 seed, #7 beds, #8 yield, #9 revenue, #10 pop, #12 fert. Live currently renders 5 — **add
the #7 beds panel** (the `beds` CALC fn already exists in crop-book-v1.js; it just has no panel). The remaining
**8** (#2 transplants, #3 nursery, #4 sow-date, #5 harvest-date, #6 succession, #11 frost, #13 profit, #14
seed-cost) render in the **disabled / not-yet-interactive state per catalog §7** (show what's needed + a
"request info" / "בקרוב" affordance) — clearly labeled, never faked.

**team_00 rule applied:** the design JS used `frost`(#11) where the live code has `beds`(#7); since calculators
are *content/fields → from code*, the 6 interactive follow the **code** (beds is in; frost stays in the
surfaced-but-not-interactive set until its JS lands in a later WP).

### 4c. Export (F-EXPORT-001)

Route `/calc/export.{fmt:csv|pdf}` → `HubController::calcExport` exists on branch (`routes.php:24`). Wire the
dash export buttons to the crop-book-v1.js serialize/export path (CSV downloads; PDF opens print view). If the
LIVE site still 404s after the deploy, that is **deploy-lag**, not a code defect → route a deploy mandate to
team_99 (FTPS→uPress per `documentation/05-admin-and-operations/UI_DEPLOY_RUNBOOK.md`). Do not change the route.

**→ AC-4.**

---

## Deliverable 5 — Regression guard

- `composer test` green (run in `sfa_delivery/`).
- `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` → 0 FAIL.
- No LOCKED Python / migration touched (this WP is delivery-tier PHP/CSS/JS only).
- All mandated routes still 200: `/`, `/crop-book/`, a crop page, `/market/`, `/calc/`, `/calc/export.csv`.

**→ AC-5.**

---

## Files touched (authoritative list)

**Edit:**
- `sfa_delivery/templates/_layout.php` — body rewrite (single `.sh`), `#sfa-logo` inline, JS-load fix, asset-array trim
- `sfa_delivery/public_assets/css/tokens.css` — token reconciliation (D1)
- `sfa_delivery/public_assets/css/crop-book-v1.css` — add `.sh` shell + nav + responsive toggle (D2a/b)
- `sfa_delivery/public_assets/css/gj.css` — delete `.gj-shell` chrome block (27–96)
- `sfa_delivery/public_assets/css/hub.css` — delete `.sfa-nav*` block
- `sfa_delivery/public_assets/css/desktop-extras.css` — delete dead `.dt-*`/toggle (or retire file)
- `sfa_delivery/templates/pages/calc_dash.php` — surface 14 cards + add #7 beds panel

**Retire (delete + de-reference):**
- `sfa_delivery/templates/shell/mobile.php`, `…/desktop.php`, `…/_mark_svg.php`
- `sfa_delivery/templates/partials/nav.php`
- `sfa_delivery/public_assets/css/desktop.css`

**Add (asset):** `sfa_delivery/public_assets/.../Carmela.ttf` (copied from design `assets/`) + corrected
`@font-face` `src`.

---

## Acceptance criteria (binding — visual fidelity is mandatory)

- **AC-1** zero cream: served CSS has no `--paper:` / `#f5f3ec` / "Cool Stone"; computed `body` background =
  `#f8fbf8` (verify via computed style, not screenshot).
- **AC-2** app-shell present: `.sh__bar` + `.sh__nav` (desktop) + `.sh__nav--mobile` (≤899px) + `#sfa-logo`;
  active nav color per surface (leaf/sun/tomato); legacy `.gj-shell`/`.dt-shell`/`.sfa-nav` gone on in-scope pages.
- **AC-3** pixel fidelity: book-entry, crop simple/full/drill, calc-dash — a design-frame-vs-live pair per screen.
- **AC-4** `/calc` interactive: `SFA_CALC` defined; 6 calcs recompute live; 14 surfaced; export CSV downloads +
  PDF opens print view (no 404).
- **AC-5** no regression: `composer test` green; `validate_aos` 0 FAIL; no LOCKED Python/migration; routes 200.
- **AC-6** RTL legible; no raw keys / "Array" / stray "—"; watercolor art + heroes render on `.sh`.

---

## QA addendum (2026-06-02, post-build internal visual QA) — spec corrections

team_50 internal visual QA (computed-style, design-vs-live harness) found 4 defects; all fixed at commit
`f85691e`. Two are **spec gaps in this LOD400** worth recording so the gate sees a complete picture:

- **D1 correction (F-QA-01, BLOCKER):** D1's token grep targeted `var(--paper)` *consumers* but missed that
  `gj.css:4–10` carried a leftover v1 cream `:root` *redefining* `--gj-paper #f6f1e3` (+ `-2/-3/--gj-ink/-soft/
  --gj-line`). Because gj.css loads after tokens.css, it overrode the v2 white ground → `body` rendered cream.
  **Corrected scope:** D1 must also remove cream `--gj-*` *redefinitions* anywhere in served CSS, not only
  legacy `--paper` consumers. Fixed (gj.css cream `:root` removed).
- **Token-port gap (F-QA-02):** served tokens.css was missing `--status-{fresh,aging,stale,error}` (present in
  design tokens.css §status) — `.sh__foot .dot` and freshness cues had no color. Added.
- **F-QA-03 (MINOR):** `.sh__foot .dot` needed `flex:none` (flex-shrink collapsed it to width:0).
- **F-QA-04 (design gap, MAJOR):** the SSoT styles only `.sh__nav a`, never `.sh__nav--mobile a` — the mobile
  bottom bar (a primary nav surface) rendered as default blue/underlined links with no active color. Added
  faithful mobile-nav color + per-surface active (leaf/sun/tomato). **This is a gap in the team_35 design board
  itself — flagged for team_35 to confirm/own in the Class B delivery.**

Evidence: `_COMMUNICATION/TEAM_50/SFA-S003-P004-WP-CB-UI-ALIGN/INTERNAL_VISUAL_QA_2026-06-02_v1.0.0.md`.

## Build constraints (team_10 / Sonnet)

- Delivery-tier only. Do NOT touch `_aos/`, Python, migrations, or any LOCKED file.
- **Do NOT change git state** (no commit/branch/checkout/reset) — leave the working tree for team_100 to commit.
  (Per the `subagent_git_isolation` lesson; team_100 verifies ancestry after.)
- Stay on branch `claude/wp-cb-ui-align-2026-06-02`.
- After edits, self-verify with the preview tools per the Verification section of the plan; capture
  design-vs-live evidence for crop-book + calc.
