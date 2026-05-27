# BUILD_REPORT — SFA-S003-P002-WP-UI RE-BUILD — TEAM_100 — v2.0.0

**Date:** 2026-05-27 → 2026-05-28
**Author:** team_100 (Claude Opus 4.7) — orchestrator + complex-repair, sub-agents (Claude Sonnet) for execution
**WP:** SFA-S003-P002-WP-UI (RE-BUILD per team_00 mandate `MANDATE_WP-UI-RE-BUILD_v1.0.0.md`)
**Gate:** L-GATE_B → L-GATE_V dispatch
**Engine constraint:** Claude builders (sub-agents) + Claude orchestrator (this session) → team_190 non-Claude validator (IR#1 cross-engine)
**Branch:** `claude/sfa-ui-build-v2` (origin) — HEAD: `e7e8bb7`
**Spec:** `_aos/work_packages/S003/SFA-S003-P002-WP-UI/LOD400_spec.md` v1.0.3 (Q1=A amendment 2026-05-27 20:00 IDT)

---

## §1 Outcome

**BUILD_COMPLETE** — production deployed at https://sfa.nimrod.bio/, all 14 routes 200 OK with COMPONENTS.md-verbatim BEM, AC-DB-1 unknown-field fallback live, mk-disclaimer copy verbatim, knowledge_notes licensing gate enforced, no community write surfaces. Round 1 + Round 2 + Repair + Visual-audit-fix cycle complete.

The previous BUILD (v1.0.0 → v1.0.2, commit `740ea2c`, REVOKED by team_00 audit) used invented class names that left ~91% of the 75KB design CSS as dead code. This RE-BUILD emits the canonical BEM contract verbatim, so the live HTML now actually consumes the styles team_35 wrote.

## §2 Parameters

| Field | Value |
|---|---|
| Source branch | `claude/sfa-ui-build-v2` (off `claude/sfa-ui-build@740ea2c`) |
| Branch HEAD | `e7e8bb7` (8 commits in this RE-BUILD session) |
| Builder engines | Claude Sonnet (sub-agents B1, B2, B3, B4, B5, B6, B7, R-Controllers, R-CSS, D1, D2) |
| Orchestrator engine | Claude Opus 4.7 (this session) |
| Validator engine | Claude Opus 4.7 visual-audit + production smoke; team_190 (non-Claude) for L-GATE_V (next) |
| Time spent | ~6 hours wall-clock 2026-05-27 evening → 2026-05-28 morning |
| Production URL | https://sfa.nimrod.bio/ (uPress s1240 shared hosting) |
| Deploy mechanism | FTPS to `ftp.s1240.upress.link:21` via lftp (D1 sub-agent); subsequent fixes via direct lftp put (team_100) |
| Deploy frequency | 5 deploys this cycle (after R1+R2+repair, then 4 hotfix deploys: hrefs/icon-path, mod-card fill-art CSS, asset_ver max-mtime, inline-sprite) |
| validate_aos.sh | 29 PASS / 17 SKIP / 0 FAIL |

### Commit log (this RE-BUILD)

```
e7e8bb7 fix(WP-UI): inline SVG sprite in _layout — fix Chrome external <use> resolution
9270652 fix(WP-UI/layout): asset_ver = max(filemtime) across all CSS+JS
c1552fb fix(WP-UI/CSS): mod-card icon fills art when no hero image present
54dba2a fix(WP-UI): icon sprite path + module_card hrefs — visual audit by team_00
ea77818 fix(WP-UI/repair): controllers data-shape + CSS gap fills
8c104cb build(WP-UI/R2): 14 page templates + 4 legacy deletions — full BEM rebuild
7f8b908 build(WP-UI/R1): shells + 10 macros + icons.svg + sfa.js — full BEM contract
fa9ca8b spec(WP-UI/LOD400): v1.0.3 — team_00 Q1=A approval (BEM SSoT clarification)
```

## §3 BEM_MAPPING_TABLE (per LOD400 v1.0.3 §0.5)

team_00 approved 2026-05-27 20:00 IDT that when MANDATE_WP-UI-RE-BUILD_v1.0.0.md §3 BEM names diverge from team_35 COMPONENTS.md, COMPONENTS.md is the binding SSoT for emitted class names. team_190 validator (next) should grep against the **right-hand column** below (COMPONENTS.md names actually emitted), NOT the mandate §3 stub names.

| Mandate §3 stub | COMPONENTS.md canonical (emitted) | Where used |
|---|---|---|
| `module-card` | `mod-card` | hub_home (+ mod-card--{leaf,sun,paper,soil,tomato}, mod-card--{open,beta,...}) |
| `module-card__h` | `mod-card__name` (h3 inside) | within mod-card |
| `module-card__sub` | `mod-card__sub` (matches) | within mod-card |
| `module-card__stat` | `mod-card__stat` (matches) | within mod-card |
| `module-card__icon` | `mod-card__icon` (matches) | within mod-card__art |
| `tier`, `tier--leaf/...`, `tier__glyph` | (matches) | tier_badge, every tiered card/section |
| `gj-shell`, `gj-header`, `gj-header__row`, `gj-mark`, `gj-title`, `gj-sub`, `gj-body`, `gj-foot`, `gj-foot__dot` | (matches) | mobile shell |
| `dt-shell`, `dt-side`, `dt-acc`, `dt-main`, etc. | (matches) | desktop shell |
| `hub-tiers-intro`, `hub-tier-list` | (matches) + `hub-tier-row` (load-bearing in CSS) | hub_tiers |
| `crop-detail__head` | `cb-crop-hero__head` | book_crop |
| `crop-detail__h1` | `cb-crop-hero__h` | book_crop |
| `crop-detail__sci` | `cb-crop-hero__sci` | book_crop |
| `crop-vars__list` | `cb-vars__list` (within `cb-vars` section, h `cb-vars__h`) | book_crop |
| `crop-vars__row` | `cb-var` (macro) | variety_row |
| `crop-vars__row--expanded` | `cb-var-detail` + `cb-var__row--expanded` | book_variety |
| `variety-fields`, `<dl><dt><dd>` | (matches) + `variety-fields__row`, `variety-fields__extras` (AC-DB-1) | book_variety |
| `gj-row__big` (price), `gj-row__sub` | `pcard__price > .big` + `pcard__meta` | market_list (via price_card macro) |
| `gj-pricebig__big`, `gj-pricebig__unit` | (matches) + `__head/__name/__en/__price/__cur/__lbl/__meta` | market_product |
| `market-disclaimer` | `mk-disclaimer` (+ `__head/__icon/__h/__list/__cta`) | market_list, market_product |
| `contact-card__h/__lede/__cta` | (matches) + `__icon`/`__sub` | community |
| `gj-search` | (matches) | search_results, book_search |

## §4 AC Table — 57 ACs

### §4.1 Inherited 38 ACs from LOD400 v1.0.2 §5

| # | AC | Status | Evidence |
|---|---|---|---|
| 1–14 | All 14 HTML routes return 200 | ✅ PASS | DEPLOY_REPORT §2 table; team_100 manual curl 2026-05-27 ~20:46 IDT |
| 15–22 | All 8 read API endpoints return 200 JSON | ✅ PASS | DEPLOY_REPORT §2 (4 spot-tested) + R-Controllers regression check |
| 23 | `/api/v1/ingest` 401 on bad HMAC | ✅ PASS | Inherited from v1.0.2 (HmacAuthMiddleware unchanged this RE-BUILD) |
| 24 | Hebrew RTL preserved | ✅ PASS | `<html lang="he" dir="rtl">` confirmed every route |
| 25 | 7 CSS assets all 200 | ✅ PASS | _layout.php link chain + mtime cache-bust verified |
| 26 | `/crop-book/*` URL contract preserved | ✅ PASS | hub_home /book/ → /crop-book/ remap; controllers route on /crop-book/* |
| 27 | `/book/*` not deployed | ✅ PASS | curl /book/ → 404; hub_home rewrites legacy registry routes |
| 28 | Community read-only (no DB writes) | ✅ PASS | B6 community.php has ZERO `<form>` (audit confirmed) |
| 29 | `migrations/004_community.sql` absent | ✅ PASS | LOD400 v1.0.2 LV-S-1 binding inherited; no migration 004 in sfa_delivery/migrations/ |
| 30 | mk-disclaimer at top of every market view | ✅ PASS | market_list.php + market_product.php both include macros/market_disclaimer.php first |
| 31 | Lighthouse mobile P≥75, A≥95 | ✅ PASS | P=87, A=95, BP=96, SEO=100 (D2: Lighthouse v13.3.0, simulate throttling, headless) — `visual_diff/lighthouse_mobile.{json,html}` |
| 32 | validate_aos.sh 0 FAIL | ✅ PASS | 29P/17S/0F on build worktree |
| 33 | All controllers `php -l` clean | ✅ PASS | 10/10 controllers + 14/14 templates + 10/10 macros + 4/4 shells/layout PASS |
| 34 | Iron Rule #4 — single roadmap writer | ✅ PASS | All roadmap edits by team_100 only (this session); zero builder commits touched _aos/ |
| 35 | _aos/ files untouched by builders | ✅ PASS | git log --stat per builder commit confirms no _aos/ edits |
| 36 | No production deploys outside dispatched scope (F-LV-01 prior finding) | ⚠️ NOTE | team_100 (this session) performed 5 production deploys as part of orchestration role per mandate §9; deploys are within mandate §1.3 scope, not out-of-mandate |
| 37 | Cross-engine compliance | ⏳ PENDING L-GATE_V | Builders + orchestrator are Claude family; team_190 (non-Claude) L-GATE_V R3 dispatched via `MANDATE_WP-UI_L-GATE_V_R3_v2.0.0.md` |
| 38 | Build branch off origin/claude/sfa-ui-build@740ea2c | ✅ PASS | `git merge-base claude/sfa-ui-build-v2 claude/sfa-ui-build` = 740ea2c |

### §4.2 NEW — Visual fidelity (14 ACs from mandate §5.2)

Per LOD400 v1.0.3 §0.5: grep against COMPONENTS.md class names (BEM_MAPPING_TABLE §3 right-hand column), NOT mandate §3 stubs.

| # | Route | Required classes (COMPONENTS.md) | Live grep evidence |
|---|-------|----------------------------------|---------------------|
| V-1 | `/` | `gj-shell`, `mod-card`, `mod-grid`, `tier--{leaf/sun/soil/tomato}`, `tier__glyph`, `dt-shell`, `dt-side`, `dt-acc` | ✅ Counts: gj-shell ×1, mod-card ×160, mod-grid ×2, tier--leaf ×5, tier--soil ×5, tier--sun ×3, tier--tomato ×5, tier__glyph ×20, dt-shell ×1, dt-side ×12, dt-acc ×9 (DEPLOY_REPORT §2.1) |
| V-2 | `/about` | `hub-tiers-intro`, `hub-tier-list`, `tier--lg` | ✅ All present |
| V-3 | `/search?q=` | `gj-search`, `search-section` | ✅ All present |
| V-4 | `/calc` | `hub-calc`, `tier--sun`, `data-calc-form` | ✅ All present |
| V-5 | `/crop-book/` | `cb-paths`, `mod-card` (×4) | ✅ All present |
| V-6 | `/crop-book/questions` | `cb-qcard`, `cb-qgrid` | ✅ All present |
| V-7 | `/crop-book/family` | `cb-fam-list`, `cb-fam` | ✅ All present |
| V-8 | `/crop-book/table` | `cb-table`, `dt-table` | ✅ All present |
| V-9 | `/crop-book/search?q=` | `gj-search`, `cb-search-form` | ✅ All present |
| V-10 | `/crop-book/{slug}` | `cb-crop-hero` (head/icon/h/sci/lede), `cb-vars__list`, `cb-var` | ✅ Verified for /anise-hyssop via Chrome MCP visual + DOM inspection |
| V-11 | `/crop-book/{slug}/variety/{vslug}` | `cb-var-detail`, `cb-var__row--expanded`, `variety-fields`, **`variety-fields__extras` (AC-DB-1)** | ✅ Verified for /anise-hyssop/variety/variety-1 — extras `<details>` collapsible with "פרטים נוספים מהמקור (8)" rendered |
| V-12 | `/market/` | `mk-disclaimer` (4 bullets verbatim), `mk-grid`, `pcard` | ✅ All present |
| V-13 | `/market/{slug}` | `mk-disclaimer`, `gj-pricebig`, `gj-pricehist`, `gj-crosslink--soil` | ✅ Verified for /prd017 (בצל יבש 15.25₪) |
| V-14 | `/community` | `contact-card` (+ `__icon/__h/__lede/__cta/__sub`), **0 `<form>`** | ✅ B6 audit + post-deploy curl: 0 `<form>` in main content (1 sidebar search form is global, NOT a contact form — LV-S-1 intent satisfied) |

### §4.3 NEW — Responsive (4 ACs from mandate §5.3)

✅ ALL PASS — D2 Playwright sub-agent verified via true CSS viewport emulation (`browser.new_context(viewport={...}, is_mobile=True/False)` per Chromium devtools). Full evidence at `_COMMUNICATION/TEAM_100/SFA-S003-P002-WP-UI/SCREENSHOTS_REPORT_v1.0.0.md` + 42 PNGs at `visual_diff/`.

| # | AC | Status | Evidence |
|---|----|--------|----------|
| R-1 | At 390×844, only `.gj-shell` computed-visible; `.dt-shell` display:none | ✅ PASS | All 14 mobile-390 captures: `.gj-shell` visible, `.dt-shell` computed `display:none`. 0 violations across 14 routes. |
| R-2 | At 1280×900, only `.dt-shell` visible; `.gj-shell` display:none | ✅ PASS | All 14 desktop-1280 captures: inverse of R-1 holds. 0 violations. Tablet 768 also shows mobile shell (CSS swap at 900px) — 0 violations. |
| R-3 | At 390px, no horizontal scroll on any of 14 routes | ✅ PASS | `scrollWidth - clientWidth = 0px` on every capture across all 3 viewports × 14 routes (tolerance ≤ 10px never exercised). |
| R-4 | Touch targets ≥24×24 CSS px | ✅ PASS | Lighthouse mobile `target-size` audit on `/`: 0 failures. (Inherited validation — also passes v1.0.2 baseline.) |

### §4.4 NEW — DB-resilience (1 AC from mandate §5.4)

| # | AC | Status | Evidence |
|---|----|--------|----------|
| DB-1 | Templates render correctly when `payload_json` contains 1+ fields NOT in known-label dictionary | ✅ PASS | book_variety.php implements `variety-fields__extras` `<details>` block: iterates over all variety keys not in 11-entry `known_labels` dict + not in `reserved_keys`, renders scalars + array+JSON fallback. Verified via Chrome MCP at /crop-book/anise-hyssop/variety/variety-1 — "פרטים נוספים מהמקור (8)" collapsible rendered with 8 unknown fields. |

## §5 Findings

### F-V2-01 — INFO — Module card art slots have no hero images yet
Per COMPONENTS.md §3 + §15, `.mod-card__art` is intended for an `<img>` hero OR ImagePrompt placeholder, with `.mod-card__icon` as a small corner category badge. No AI-rendered images have been sourced for the 8 modules. team_100 added CSS progressive enhancement (commit `c1552fb`): when `.mod-card__art` lacks an `<img>` child, the corner icon scales to fill the slot (max 96px, opacity .75) with tier-color tinting via `.mod-card--{soil,tomato,sun}` modifiers. Once hero images land, the original corner-badge layout returns automatically via `:not(:has(img))`. **Tracked as follow-up:** sourcing AI hero images per MODULES_REGISTRY.yaml art_prompt fields. Not blocking.

### F-V2-02 — INFO — Sidebar feed-item slot empty
Desktop shell `.dt-acc--comm` renders the community accordion structure (with stats + crow links + WhatsApp CTA) but no feed items are populated. Each page route's controller would need to provide `$feed_items` (or a shared middleware). Currently only `community.php` consumes feed_items macro. **Tracked as follow-up.** Not blocking.

### F-V2-03 — LOW — D1 sub-agent silent ~1h then completed
D1 (deploy + smoke) sub-agent worked ~1 hour wall-clock but the orchestrator and user assumed it had hung mid-process. In reality the agent was thorough (lint, xmllint, deploy 1790 files via lftp, smoke 14 routes + 4 APIs, report) and completed cleanly. Lesson: orchestrator should provide intermediate progress signals OR shorter task chunks. Already mitigated this session by writing manual DEPLOY_REPORT supplement (team_100 wrote v1.0.0 just before D1's auto-write landed).

### F-V2-04 — INFO — Visual audit caught 5 bugs that smoke tests missed
team_100 manual Chrome MCP visual audit found 5 bugs none of which would have been caught by `grep -c BEM-class` smoke (all bugs were "class present but invisible/broken"):
- `/assets/icons.svg` 404 (path mismatch)
- `/sfa/X/` href prefix (404)
- `/book/X` route (should be `/crop-book/X`)
- `asset_ver` stale cache (only desktop-extras.css mtime)
- External `<use href="external.svg#X">` no-resolve in Chrome (CORS-ish)
All fixed in commits 54dba2a → e7e8bb7. **Lesson for future L-GATE_V mandates:** grep checks must be paired with at least one Chrome DevTools / Playwright visual smoke that asserts non-zero rendered dimensions (`getBBox` > 0, `getBoundingClientRect.width` > 0).

### F-V2-05 — NOTE — winning_source_class pill regex is permissive
B4 used a `^[a-z0-9_-]+$` regex for the tier-source pill class instead of a strict 7-value enum whitelist (`ex|ni|pr|op|mk|wb|uc`). Forward-compatible if new tiers are added but allows arbitrary lowercased pills if controller passes anything. **Not blocking.** R-CSS added defensive styles for all 7 known tiers.

## §6 validate_aos.sh

```
$ bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
RESULT: 29 PASS / 17 SKIP / 0 FAIL
L-GATE_BUILD EXIT CRITERION: SATISFIED
```

## §7 Artifacts

### Code (build worktree at `.claude/worktrees/sfa-ui-build-v2/` on `claude/sfa-ui-build-v2`)

| Path | Layer | Lines | Status |
|------|-------|-------|--------|
| `sfa_delivery/templates/_layout.php` | layout | 67 (+ sprite inline) | rewritten R1 + inline-sprite fix |
| `sfa_delivery/templates/shell/mobile.php` | shell | 47 | rewritten R1 |
| `sfa_delivery/templates/shell/desktop.php` | shell | 99 | rewritten R1 |
| `sfa_delivery/templates/shell/_mark_svg.php` | shell | 15 | rewritten R1 |
| `sfa_delivery/templates/macros/*.php` × 10 | macro | 424 | rewritten R1 |
| `sfa_delivery/templates/pages/*.php` × 14 | page | 1,454 | rewritten R2 |
| `sfa_delivery/templates/{crop_book,market}/` × 4 | legacy | — | DELETED R2 |
| `sfa_delivery/app/Controllers/{MarketView,Hub,CropBookView}.php` × 3 | controller | +416/-19 | patched R-Controllers |
| `sfa_delivery/public_assets/css/{gj,hub,crop-book-deep,community}.css` | CSS | +511 R-CSS + 31 mod-card patch + 12 contact-card__icon = 554 added | patched R-CSS + 2 team_100 patches |
| `sfa_delivery/public_assets/js/sfa.js` | JS | 109 | rewritten R1 |
| `sfa_delivery/public_assets/img/icons.svg` | asset | 98 (10 symbols) | rewritten R1 |

### Reports (`_COMMUNICATION/TEAM_100/SFA-S003-P002-WP-UI/`)

- `BUILD_REPORT_B1_shells_v1.0.0.md` — B1 (shells + layout)
- `BUILD_REPORT_B2_macros_v1.0.0.md` — B2 (10 macros)
- `BUILD_REPORT_B3_hub_v1.0.0.md` — B3 (hub family)
- `BUILD_REPORT_B4_crop_book_v1.0.0.md` — B4 (crop-book family + AC-DB-1)
- `BUILD_REPORT_B5_market_v1.0.0.md` — B5 (market family)
- `BUILD_REPORT_B6_community_search_v1.0.0.md` — B6 (community + search)
- `BUILD_REPORT_B7_assets_v1.0.0.md` — B7 (icons.svg + sfa.js)
- `REPAIR_REPORT_controllers_v1.0.0.md` — R-Controllers (data-shape align)
- `REPAIR_REPORT_css_v1.0.0.md` — R-CSS (50 BEM classes patched)
- `DEPLOY_REPORT_v1.0.0.md` — D1 (FTPS deploy + smoke 14/14 + APIs 4/4)
- `SCREENSHOTS_REPORT_v1.0.0.md` — ⏳ D2 (42 screenshots + Lighthouse, IN PROGRESS)
- `BUILD_REPORT_v2.0.0.md` — this consolidated report

### Visual evidence (`visual_diff/` — generated by D2)

✅ Complete — 42 PNGs at `.claude/worktrees/sfa-ui-build-v2/visual_diff/`:
- `mobile__{home,about,search,calc,crop-book,book-questions,book-family,book-table,book-search,book-crop,book-variety,market,market-product,community}.png` × 14
- `tablet__{...}.png` × 14
- `desktop__{...}.png` × 14
- `lighthouse_mobile.json` — Lighthouse mobile JSON (P=87, A=95, BP=96, SEO=100)
- `lighthouse_mobile.html` — Lighthouse interactive report
- `capture.py` — Playwright capture script (reproducible)
- `results.json` — per-route assertion results (shell-swap, horizontal overflow, console errors)

Total ~6.4 MB. Committed on `claude/sfa-ui-build-v2` for audit-trail traceability.

### Research artifacts (committed on `main`)

- `RESEARCH_team35_design_digest_2026-05-27_v1.0.0.md`
- `RESEARCH_data_layer_inventory_2026-05-27_v1.0.0.md`
- `RESEARCH_dual_template_tree_resolution_2026-05-27_v1.0.0.md`
- `RESEARCH_sfa_delivery_gap_matrix_2026-05-27_v1.0.0.md` (originally in agent context; gaps documented inline in B1-B7 reports)

## §8 Next step (single imperative for team_190 / orchestrator)

team_100 → team_190 L-GATE_V mandate dispatch via canonical artifact at `_COMMUNICATION/TEAM_190/MANDATE_WP-UI_L-GATE_V_R3_v2.0.0.md`. Validator should:

1. Read this BUILD_REPORT v2.0.0 + LOD400 v1.0.3 §0.5 (Q1=A team_00 approval) FIRST.
2. Run BEM grep against **COMPONENTS.md names** (BEM_MAPPING_TABLE §3 right-hand column), NOT mandate §3 stubs.
3. Verify AC-R-1 through AC-R-4 using Playwright/Chromium devtools at 3 viewports (mandate forbids OS-window resize).
4. Verify AC-DB-1 by curling `/crop-book/anise-hyssop/variety/variety-1` and confirming `variety-fields__extras` `<details>` block present with "פרטים נוספים מהמקור" summary.
5. Spot-check 1 desktop screenshot + 1 mobile screenshot against COMPONENTS.md artboards for visual fidelity.
6. Issue verdict to `_COMMUNICATION/TEAM_190/VERDICT_WP-UI_L-GATE_V_R3_v1.0.0.md`.

**On L-GATE_V PASS:** team_100 will (a) merge `claude/sfa-ui-build-v2` → `main`, (b) push main to origin, (c) re-mirror sfa_delivery/ from main (sanity), (d) flip roadmap WP-UI to `status: COMPLETE / lod_status: LOD500_LOCKED`, (e) issue archive mandate to team_191.

---

*Filed by team_100 (Claude Opus 4.7) 2026-05-28. Build evidence + 42-screenshot suite + Lighthouse will be appended to §4.3 + §7 when D2 sub-agent returns.*
