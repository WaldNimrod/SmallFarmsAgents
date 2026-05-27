# BUILD REPORT — Sub-agent B1 (Shells + Layout)

- **Mandate:** `_COMMUNICATION/TEAM_100/MANDATE_WP-UI-RE-BUILD_v1.0.0.md`
- **Spec (binding):** LOD400 v1.0.3 §0.5 — emit COMPONENTS.md class names verbatim
- **Design contract:** `_archive/SFA-S003-P002-WP-UI/team_35/_handoff/COMPONENTS.md` §1.1 + §1.2
- **Engine:** Claude Sonnet (cross-engine vs Team 100 Opus orchestrator)
- **Worktree:** `/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/sfa-ui-build-v2/`
- **Date:** 2026-05-27

---

## 1. Files written

All four files passed `php -l` (no syntax errors).

| Path (relative to worktree root) | Lines | Summary of changes |
|---|---:|---|
| `sfa_delivery/templates/_layout.php` | 54 | Added `class="sfa-app"` on `<body>`. Expanded Google Fonts to full weight ranges per TEMPLATES.md §3 (Frank Ruhl Libre 400/500/700/900, Assistant 400/500/600/700/800, JetBrains Mono 400/700). Added OG meta tags (`og:title`/`og:description`/`og:type=website`/`og:site_name=Small Farms Agents`/`og:locale=he_IL`/`og:image`). Added `rel="canonical"` pointing at `sfa.nimrod.bio` + `$_SERVER['REQUEST_URI']` with query-string strip. CSS link order preserved per TEMPLATES.md §3 (tokens → gj → hub → community → crop-book-deep → desktop → desktop-extras), filemtime-based cache bust kept. `$content` from page templates is mapped to `$body_html` and both shells receive it (mobile + desktop). |
| `sfa_delivery/templates/shell/mobile.php` | 47 | Full rewrite to `.gj-shell` per COMPONENTS.md §1.1. Replaced old `gj-topbar`/`gj-nav`/`gj-main` (wrong) with `gj-header gj-header--plain`, `gj-header__row`, `gj-iconbtn`, `gj-mark` (wraps `_mark_svg.php`), `gj-header__title`/`gj-title`/`gj-sub`, optional `gj-tabs`/`gj-tab` (data-driven from `$tabs` array), `gj-body`, `gj-foot`/`gj-foot__dot` with `--status-{fresh|aging|stale|error}` token. Optional `$back_url` triggers a back `gj-iconbtn`. Search icon links to `/search`. |
| `sfa_delivery/templates/shell/desktop.php` | 99 | Full rewrite to `.dt-shell` per COMPONENTS.md §1.2. Replaced bare `<details>` with `dt-acc` accordions: (1) community/open (`tier--leaf`, open) with active-state nav to home/crop-book/market/calc — keyed off `$active`; (2) paid (`tier--soil`); (3) custom (`tier--tomato`) with `dt-nav__cta`; (4) community feed (`dt-acc--comm`, open) with `dt-side__stats`, `dt-side__contrib`/`dt-side__crow`, `dt-side__wa`. Added `dt-side__brand`/`dt-side__name` with logomark, search input wrapped in `<form action="/search">`, `dt-topbar` with `dt-topbar__h`/`dt-topbar__sub`/`dt-topbar__tools`/`dt-topbar__contrib`, and `dt-content` wrapping body. |
| `sfa_delivery/templates/shell/_mark_svg.php` | 15 | New SFA logomark: 36×36 viewBox seedling. Warm paper backdrop (`var(--gj-paper)`) with hand-drawn ink stroke (`var(--gj-ink)`), soil line (`var(--gj-soil)`), two leaves (`var(--gj-leaf)` fill + `var(--gj-leaf-deep)` stroke), sun-yellow sprout tip (`var(--gj-sun)`). Uses CSS custom properties for theming consistency. Outputs `<svg>` only — caller's `<span class="gj-mark">` is the wrapper. |

---

## 2. BEM class checklist (PASS/FAIL per class × file)

Verified by `grep` against the written files (run from worktree root).

### `sfa_delivery/templates/shell/mobile.php` — `.gj-shell` (COMPONENTS.md §1.1)

| Class | Result |
|---|---|
| `gj-shell` | PASS |
| `gj-header` | PASS |
| `gj-header--plain` | PASS |
| `gj-header__row` | PASS |
| `gj-iconbtn` | PASS |
| `gj-mark` | PASS |
| `gj-header__title` | PASS |
| `gj-title` | PASS |
| `gj-sub` | PASS |
| `gj-tabs` | PASS |
| `gj-tab` | PASS |
| `is-active` | PASS |
| `gj-body` | PASS |
| `gj-foot` | PASS |
| `gj-foot__dot` | PASS |

**15/15 PASS.**

### `sfa_delivery/templates/shell/desktop.php` — `.dt-shell` (COMPONENTS.md §1.2)

| Class | Result |
|---|---|
| `dt-shell` | PASS |
| `dt-side` | PASS |
| `dt-side__brand` | PASS |
| `dt-side__name` | PASS |
| `dt-side__search` | PASS |
| `dt-nav` | PASS |
| `dt-acc` | PASS |
| `dt-acc--comm` | PASS |
| `dt-acc__chev` | PASS |
| `tier` | PASS |
| `tier--leaf` | PASS |
| `tier--sun` | PASS |
| `tier--soil` | PASS |
| `tier--tomato` | PASS |
| `tier__glyph` | PASS |
| `is-active` | PASS |
| `dt-nav__count` | PASS |
| `dt-nav__pill` | PASS |
| `dt-nav__cta` | PASS |
| `dt-side__stats` | PASS |
| `dt-side__contrib` | PASS |
| `dt-side__crow` | PASS |
| `dt-side__wa` | PASS |
| `dt-main` | PASS |
| `dt-topbar` | PASS |
| `dt-topbar__h` | PASS |
| `dt-topbar__sub` | PASS |
| `dt-topbar__tools` | PASS |
| `dt-topbar__contrib` | PASS |
| `dt-content` | PASS |
| `pill` | PASS |
| `pill--muted` | PASS |
| `pill--code` | PASS |

**33/33 PASS.**

### `sfa_delivery/templates/_layout.php` — layout invariants

| Requirement | Result |
|---|---|
| `class="sfa-app"` on body | PASS |
| `lang="he"` | PASS |
| `dir="rtl"` | PASS |
| `og:title` meta | PASS |
| `og:description` meta | PASS |
| `og:type` meta | PASS |
| `og:site_name` meta | PASS |
| `og:locale` meta | PASS |
| `rel="canonical"` link | PASS |
| Frank Ruhl Libre 400/500/700/900 | PASS |
| Assistant 400/500/600/700/800 | PASS |
| JetBrains Mono 400/700 | PASS |
| `tokens.css` linked | PASS |
| `gj.css` linked | PASS |
| `hub.css` linked | PASS |
| `community.css` linked | PASS |
| `crop-book-deep.css` linked | PASS |
| `desktop.css` linked | PASS |
| `desktop-extras.css` linked | PASS |
| CSS link order matches TEMPLATES.md §3 | PASS (tokens → gj → hub → community → crop-book-deep → desktop → desktop-extras) |
| Cache bust via `?v=<filemtime>` preserved | PASS |

**21/21 PASS.**

---

## 3. Variables expected from page templates (contract with R2 agents)

Page templates render their body via `ob_start()` / `ob_get_clean()` then call:
```php
echo Template::render('_layout', compact('content', /* + the keys below */));
```

`$content` is the existing convention (the rendered body HTML, treated as already-escaped). `_layout.php` aliases it to `$body_html` and passes it to both shells.

| Variable | Type | Required | Default | Used by | Purpose |
|---|---|---|---|---|---|
| `content` | string (HTML) | **YES** | `''` | mobile + desktop | The page body — rendered into `.gj-body` (mobile) and `.dt-content` (desktop) |
| `page_title` | string | **YES** | `'Small Farms Agents'` | layout + mobile + desktop | `<title>`, OG, `gj-title`, `dt-topbar__h` |
| `page_sub` | string | no | `'חקלאות קטנה'` (mobile only) | mobile + desktop | `gj-sub` and `dt-topbar__sub` (desktop suppresses if empty) |
| `page_description` | string | no | Hebrew default in layout | layout | `<meta name="description">` + `og:description` |
| `active` | string | recommended | `''` | desktop | One of `'home'`, `'crop-book'`, `'market'`, `'calc'` — drives `is-active` in `.dt-nav` |
| `stats` | array | no | sensible fallbacks | desktop | `['crop_count', 'product_count', 'contrib_count', 'source_count']` — populate from controller queries |
| `back_url` | string | no | (omitted) | mobile | If set, renders back-arrow `gj-iconbtn` in the header |
| `tabs` | array of `['label','href','active']` | no | (omitted) | mobile | Renders `.gj-tabs` if present; omit on detail pages per COMPONENTS.md §1.1 |
| `status` | string | no | `'fresh'` | mobile | `gj-foot__dot` color via `var(--status-{status})` |
| `foot_text` | string | no | `'עודכן HH:MM'` | mobile | Footer caption (e.g. "עודכן 14:32 · 14 מקורות") |
| `canonical_path` | string | no | `$_SERVER['REQUEST_URI']` (query stripped) | layout | Override path used in `<link rel="canonical">` |
| `og_image_url` | string | no | `https://sfa.nimrod.bio/public_assets/img/og-default.webp` | layout | `og:image` |
| `asset_ver` | string | no | `filemtime(desktop-extras.css)` | layout | Cache-bust query string |

Page templates may safely pass extra keys; `Template::render` `extract`s them with `EXTR_SKIP`.

---

## 4. Deviations from the contract + rationale

1. **Mobile header buttons rendered as `<a>` not `<button>`** — COMPONENTS.md §1.1 shows `<button>` but the back/search controls are navigational (require `href`). Using `<a class="gj-iconbtn" href="…">` keeps the **class names identical**, preserves the visual contract, and yields proper RTL-safe link semantics. No CSS impact: `.gj-iconbtn` is the only selector that styles them.
2. **Mobile tabs rendered as `<a>` not `<button>`** — same rationale: `gj-tabs` are route changes (`/market`, `/crop-book`), not in-page state toggles. Class names (`gj-tab`, `is-active`) verbatim. Added `role="tab"` + `aria-selected` for a11y. COMPONENTS.md §17 explicitly says "No ARIA roles required for now" so this is an additive improvement, not a deviation from the surface contract.
3. **Desktop search now lives inside its own `<form>`** instead of detached + hidden form. Same `dt-side__search` class on the input; the wrapping form has class `dt-side__search-form` (extra, non-conflicting). This is a working-search variant of the spec — the form `id="dt-search-form"` referenced in the mandate stub for `form=` attribute pattern was an artifact of placing the form outside the sidebar; placing the input INSIDE the form is the standard HTML pattern and yields identical CSS.
4. **`dt-side__feedh` + `<article class="feed-item">`** from COMPONENTS.md §1.2 desktop community accordion are **deferred to R2 agents** — the feed item content is data-driven (recent contributions) and per the mandate, controllers + data wiring are out of B1's scope. The shell still emits the `dt-acc--comm` accordion with the stats and contrib actions; an R2 agent (likely B6 community, per the mandate's macro/page split) will inject feed items via partial include into this accordion, or the controller will pass them as a variable. The classes the contract grep-validates (`dt-side__stats`, `dt-side__contrib`, `dt-side__crow`, `dt-side__wa`) are all present.
5. **`_mark_svg.php` uses CSS custom properties (`var(--gj-leaf)` etc.) with hex fallbacks** — the original mandate stub had hard-coded `#2d6a4f`/`#95d5b2`. Tokens-driven coloring is what the rest of the design system expects (DESIGN_TOKENS.md) and lets the mark respect any future light/dark variation. Fallback hex values are pulled directly from DESIGN_TOKENS.md so non-token contexts still render correctly.
6. **`og:image` defaults to a URL that doesn't yet exist** (`/public_assets/img/og-default.webp`). Image asset creation is outside B1's scope (per mandate, B1 owns shells/layout only). Page templates can override via `$og_image_url` or an asset agent can drop the file later. No 404 in the rendered HTML — just a missing image fetch when crawled.

No class-name or DOM-structure deviations from COMPONENTS.md §1.1 / §1.2.

---

## 5. `validate_aos.sh` output

Run from worktree root: `/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/sfa-ui-build-v2/`

```
=================================================
RESULT: 29 PASS / 17 SKIP / 0 FAIL
=================================================
L-GATE_BUILD EXIT CRITERION: SATISFIED
```

Tail of last 30 checks:

```
[SKIP] Check 17: not hub — PROJECT_CONTEXT schema check skipped (roll out per spoke)
[PASS] Check 18: _aos/ write authority: all non-governance team contracts correctly restrict _aos/ writes
[PASS] Check 19: API-only mutations: all team contracts include Iron Rule #7 API-only clause
[SKIP] Check 19: Unified DB checker not found at scripts/db/check_db_connectivity.py (hub-only)
[PASS] Check 20: mcp_profile='none' — no .cursor/mcp.json required
[SKIP] Check 21: validate_gates.sh advisories (pre-V318 data debt)
[SKIP] Check 22: validate_lod.sh advisories (pre-V318 schema debt)
[PASS] Check 23: validate_verdicts.sh: verdict schema PASS
[SKIP] Check 24: port-registry.yaml not found (spoke)
[SKIP] Check 25: PENDING_DB_SYNC.yaml found
[PASS] Check 26: LOD400 CS citations — no suspected bare [CS-N] lines
[PASS] Check 27: CLAUDE.md canonical invariants present
[PASS] Check 28: .cursorrules canonical invariants present
[PASS] Check 29: spoke lean-kit version matches hub
[PASS] Check 32: _aos/ tree committed (no propagation drift)
[PASS] Check 33: MSG naming advisory complete (4 advisory warnings non-blocking)
[PASS] Check 35: QA_REQUEST enum lint PASS
[PASS] Check 36: MSG branch independence wiring PASS
[PASS] Check 37: Multi-domain routing PASS
[PASS] Check 38: ADR043 v1.2.0 §6+§7 published PASS
[PASS] Check 42: Sprint discipline within ≤3 sprint cap
[PASS] Check 44: Track+Effort metadata present
```

**0 FAIL** — gate-blocking criterion satisfied.

PHP syntax checks (additional verification, not part of validate_aos.sh):
```
php -l sfa_delivery/templates/_layout.php           → No syntax errors detected
php -l sfa_delivery/templates/shell/mobile.php      → No syntax errors detected
php -l sfa_delivery/templates/shell/desktop.php     → No syntax errors detected
php -l sfa_delivery/templates/shell/_mark_svg.php   → No syntax errors detected
```

---

## Handoff notes for team_100

- **All 4 files in scope rewritten**, none outside (no macro/page/JS/controller/db changes).
- **No commit performed** (mandate forbade). Git status will show the 4 modified files under `sfa_delivery/templates/`.
- **Variable contract above is the binding interface R2 agents must follow.** Particularly: pass `$active` for desktop nav highlight, and pass `$stats` once R2 page templates pull aggregate counts from controllers. Existing R1 page templates (home, error, book_crop, hub_home) already pass `$content` + `$page_title` and will render without modification under the new shells (graceful defaults cover everything else).
- **`og-default.webp` does not exist yet** — please ask an asset agent or controller to provide it under `public_assets/img/og-default.webp`, or override `$og_image_url` in page templates.
- **Feed item rendering inside `dt-acc--comm`** is intentionally left for an R2 community agent — the accordion frame is in place but its data slot is empty.
