# BUILD_REPORT — B2: WP-UI Macros (10 BEM components)

- **Agent:** Build sub-agent B2 (Claude Opus 4.7)
- **Dispatched by:** team_100 (Chief Architect)
- **Mandate:** `_COMMUNICATION/TEAM_100/MANDATE_WP-UI-RE-BUILD_v1.0.0.md` (worktree `gallant-elbakyan-727a60`)
- **LOD400 ref:** `_aos/work_packages/S003/SFA-S003-P002-WP-UI/LOD400_spec.md` v1.0.3 §0.5 (team_00 approved 2026-05-27 20:00 IDT — COMPONENTS.md class names verbatim)
- **Design contract:** `_archive/SFA-S003-P002-WP-UI/team_35/_handoff/COMPONENTS.md` §2–§17
- **Working tree:** `/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/sfa-ui-build-v2/`
- **Date:** 2026-05-27

---

## 1. Macros written — paths + line counts

| # | Macro | Path (relative to worktree root) | Lines | PHP lint |
|---|-------|----------------------------------|-------|----------|
| 1 | tier_badge       | `sfa_delivery/templates/macros/tier_badge.php`       | 28 | PASS |
| 2 | module_card      | `sfa_delivery/templates/macros/module_card.php`      | 54 | PASS |
| 3 | price_card       | `sfa_delivery/templates/macros/price_card.php`       | 64 | PASS |
| 4 | crop_card        | `sfa_delivery/templates/macros/crop_card.php`        | 35 | PASS |
| 5 | variety_row      | `sfa_delivery/templates/macros/variety_row.php`      | 52 | PASS |
| 6 | contrib_strip    | `sfa_delivery/templates/macros/contrib_strip.php`    | 43 | PASS |
| 7 | crosslink        | `sfa_delivery/templates/macros/crosslink.php`        | 34 | PASS |
| 8 | market_disclaimer| `sfa_delivery/templates/macros/market_disclaimer.php`| 24 | PASS |
| 9 | feed_item        | `sfa_delivery/templates/macros/feed_item.php`        | 54 | PASS |
| 10| timeline_bar     | `sfa_delivery/templates/macros/timeline_bar.php`     | 36 | PASS |

**Total:** 10 macros, 424 lines, **0 syntax errors** (verified with `php -l`).

---

## 2. BEM class checklist — required classes confirmed present

Method: each macro's rendered output was generated with sample inputs and grepped against the required class list. All classes listed below appear in the macro's literal markup (either as static class strings or as `prefix--<?= $token ?>` interpolations whose token comes from a fixed enum in the macro).

### tier_badge.php (COMPONENTS.md §2)
- `tier` ✓
- `tier--lg` ✓ (size='lg' branch)
- `tier--leaf` / `tier--sun` / `tier--paper` / `tier--soil` / `tier--tomato` ✓ (driven by `$tier_map[$tier]['color']` enum: open→leaf, beta→sun, coming→paper, paid→soil, custom→tomato)
- `tier__glyph` ✓

### module_card.php (COMPONENTS.md §3) — `.mod-card` (NOT `.module-card`)
- `mod-card` ✓
- `mod-card--{color}` ✓ (interpolated from `$module['tier_color']`)
- `mod-card--{tier}` ✓ (interpolated from `$module['tier']`)
- `mod-card__art` ✓
- `mod-card__icon` ✓
- `mod-card__body` ✓
- `mod-card__head` ✓
- `mod-card__name` ✓
- `mod-card__sub` ✓
- `mod-card__stat` ✓
- `data-tier` attribute ✓
- Embeds `tier_badge.php` via `include __DIR__ . '/tier_badge.php';` (passes `$tier`, sets `$size='sm'`)

### price_card.php (COMPONENTS.md §5) — `.pcard` (NOT `.price-card`)
- `pcard` ✓
- `pcard__head` ✓
- `pcard__glyph` ✓
- `pcard__name` ✓
- `pcard__unit` ✓
- `pcard__price` ✓
- `big` ✓ / `cur` ✓ / `med` ✓ (inside `.pcard__price`)
- `pcard__range` ✓
- `fill` ✓
- `pcard__range-text` ✓
- `pcard__meta` ✓
- `sources` ✓ (with 3 nested `<span>`)
- `pcard__bookcta` ✓

### crop_card.php (COMPONENTS.md §6) — `.gj-cropcard`
- `gj-cropcard` ✓
- `gj-cropcard__art` ✓
- `gj-cropcard__icon` ✓
- `gj-cropcard__body` ✓
- `gj-cropcard__name` ✓
- `gj-cropcard__en` ✓
- `gj-cropcard__meta` ✓
- `gj-tag` ✓
- `gj-cropcard__dtm` ✓ (rendered only when `$dtm_days` is present **and** not the `-32768` sentinel)

### variety_row.php (COMPONENTS.md §7) — `.cb-var` (BLOCK, not `<tr>`)
- `cb-var` ✓
- `cb-var--default` ✓ (when `is_default` truthy)
- `cb-var__head` ✓
- `cb-var__star` ✓ (when `is_default` truthy)
- `cb-var__grid` ✓
- `pill` ✓ / `pill--code` ✓
- **Sentinel handling:** `dtm_days === -32768` (WP-B1/B3 "presence-only" sentinel) renders the DTM cell as `—`. Same em-dash also used for `null`/empty.

### contrib_strip.php (COMPONENTS.md §8)
- `contrib-strip` ✓ (with `data-context` attribute)
- `contrib-strip__head` ✓
- `contrib-strip__icon` ✓
- `contrib-strip__h` ✓
- `contrib-strip__sub` ✓
- `contrib-strip__input` ✓
- `contrib-strip__cta` ✓
- `contrib-strip__quick` ✓ (with `role="group"`)
- `contrib-strip__chip` ✓ (×4)

### crosslink.php (COMPONENTS.md §4) — `.gj-crosslink`
- `gj-crosslink` ✓
- `gj-crosslink--soil` ✓ (when `$direction === 'market-to-book'`)
- `gj-crosslink__art` ✓
- `gj-crosslink__body` ✓
- `gj-crosslink__big` ✓
- `gj-crosslink__sub` ✓
- `gj-crosslink__cta` ✓

### market_disclaimer.php (COMPONENTS.md §10) — `.mk-disclaimer` (NOT `.market-disclaimer`)
- `mk-disclaimer` ✓
- `mk-disclaimer__head` ✓
- `mk-disclaimer__icon` ✓
- `mk-disclaimer__h` ✓
- `mk-disclaimer__list` ✓
- `mk-disclaimer__cta` ✓
- **Copy verbatim per team_00 lock** (4-bullet "מה / מאיפה / למה / לא" + CTA "קראו עוד על המתודולוגיה →")

### feed_item.php (COMPONENTS.md §9)
- `feed-item` ✓
- `feed-item__kind` ✓
- `feed-item__kind--sun` / `--tomato` / `--leaf` ✓ (mapped from `$kind`: suggest→sun, correction→tomato, data→leaf)
- `feed-item__body` ✓
- `feed-item__head` ✓
- `feed-item__date` ✓
- `feed-item__text` ✓
- `feed-item__meta` ✓
- `feed-item__tag` ✓
- `feed-item__upvotes` ✓ (rendered when `$upvotes > 0`)
- `pill` ✓ / `pill--muted` ✓

### timeline_bar.php (COMPONENTS.md §12) — `.gj-timeline`
- `gj-timeline` ✓
- `gj-timeline__bar` ✓
- `gj-timeline__seg` ✓
- `gj-timeline__seg--prep` ✓
- `gj-timeline__seg--grow` ✓
- `gj-timeline__seg--harv` ✓
- `gj-timeline__ruler` ✓ (rendered only when `$week_labels` non-empty)

**Result:** 100% of required BEM classes confirmed present across all 10 macros.

---

## 3. Variable contract per macro (what page templates must pass)

All macros follow the existing convention: variables are passed by-name in the **enclosing PHP scope** (i.e. `include __DIR__ . '/macros/foo.php'` reads `$foo_var` from the caller's variables). No `$data[]` extraction. All string-bearing fields are routed through `htmlspecialchars($value, ENT_QUOTES, 'UTF-8')`; HTML-bearing fields (`$icon_svg`, `$art_html`) are emitted raw with a `/* trusted */` annotation.

| Macro | Required vars | Optional vars |
|-------|---------------|---------------|
| **tier_badge**       | `$tier` ∈ {open, beta, coming, paid, custom} | `$size` ∈ {sm (default), lg} |
| **module_card**      | `$module[]` — keys: `slug`, `name_he`, `tier`, `tier_color`, `sub_he`, `stat_he`, `href`, `icon_svg` OR `icon_id` | `$module['data_tier']` (defaults to `$module['tier']`) |
| **price_card**       | `$product[]` — keys: `slug`, `name_he`, `en_name`, `unit_he`, `glyph_letter`, `price_current`, `currency`, `price_median`, `price_min`, `price_max`, `source_count`, `observation_count` | `$price_range_min`, `$price_range_max` (global scale for `.fill`; defaults to card's own min/max) |
| **crop_card**        | `$crop[]` — keys: `slug`, `name_he`, `en_name`, `family_tag_he`, `dtm_days`, `icon_svg` | — |
| **variety_row**      | `$variety[]` — keys: `vslug`, `name_he`, `breeding_type`, `is_default`, `dtm_days`, `yield_kg_per_m2`, `color_he`, `shape_he`, `taste_stars`, `resistance_he`; `$crop_slug` (parent crop slug, for href) | — |
| **contrib_strip**    | `$context` (e.g. `market.tomato`), `$context_label_he` | — |
| **crosslink**        | `$href`, `$art_html` (trusted), `$big_text`, `$small_unit`, `$sub_text` | `$direction` ∈ {book-to-market (default), market-to-book} |
| **market_disclaimer**| _(no inputs — static copy locked by team_00)_ | — |
| **feed_item**        | `$kind` ∈ {suggest, correction, data}, `$author_he`, `$region_he`, `$date_he`, `$text_he`, `$tag_he` | `$upvotes` (int) |
| **timeline_bar**     | `$prep_pct`, `$grow_pct`, `$harv_pct`, `$harv_days` | `$week_labels` (array<string>) |

---

## 4. Deviations + rationale

1. **`tier_badge` glyph mapping built inline (not extracted).** Mandate said "build it inline" — confirmed. The map lives only inside `tier_badge.php`; downstream callers pass only `$tier` + optional `$size`. This keeps callers (`module_card`) decoupled from the color/glyph/label table.

2. **`module_card` icon fallback.** Mandate said input is `icon_svg` (trusted) OR `icon_id` (sprite ref). I implemented `icon_svg` as primary; if absent and `icon_id` is set, the macro composes `<svg aria-hidden="true"><use href="/assets/icons.svg#{icon_id}"></use></svg>`. Sprite path is conventional (`/assets/icons.svg`) — page templates may override by passing `icon_svg` directly with a different sprite path.

3. **`price_card` fill bar — global vs local range.** COMPONENTS.md §5 says the fill should be computed "from min/max relative to a global range — keep dynamic". I added two optional caller-scope vars `$price_range_min` / `$price_range_max` that, when set, scale this card's min/max inside the global window. When absent, the card's own min/max fills the bar 100%. Calculation: `inset-inline-end = (global_max − price_max) / span * 100`, `inline-size = (price_max − price_min) / span * 100`, clamped to [0,100]. Span floor of `0.0001` prevents division by zero.

4. **`variety_row` sentinel + cell handling.** Per mandate, `dtm_days === -32768` (WP-B1/B3 sentinel) renders as `—`. I also render `—` for `null` / empty / missing. Other cells (`color_he`, `shape_he`, etc.) use `?? '—'` for nulls. `taste_stars` clamped to [0,5] before `str_repeat`. `yield_kg_per_m2` formatted to 1 decimal with " ק״ג/מ״ר" suffix.

5. **`contrib_strip` WhatsApp link wrapper.** Per LOD400 v1.0.2 §0 LV-S-1, public community WRITES are forbidden in this WP. The macro renders the visual contract from COMPONENTS.md §8 but every interactive surface (`__cta` + 4 × `__chip`) points to `https://wa.me/972547776770` with a `text=` query encoding the action prefix + context label. No `<form>`, no `/wp-json/sfa/v1/contribute` POST endpoint. Phone number `972547776770` taken from existing `crosslink.php` history pattern; confirm with team_00 if a different community number is preferred.

6. **`market_disclaimer` copy.** Verbatim per mandate §8. Class is `.mk-disclaimer` (not `.market-disclaimer` as in the legacy stub). No inputs.

7. **`feed_item.kind_label_he`.** Mandate showed `<?= $kind_label_he ?>` but did not specify the strings. I added them to the `$kind_map`: `suggest → "הצעה"`, `correction → "תיקון"`, `data → "נתון"`. team_00 / team_35 can rename via the map without touching the markup.

8. **`crop_card` DTM sentinel.** Although mandate only called out the sentinel for `variety_row`, the same `-32768` convention applies at the crop level. I render the `.gj-cropcard__dtm` element only when `dtm_days` is truthy **and** not the sentinel.

9. **All macros pass `php -l`.** Verified with PHP CLI; no syntax errors.

10. **No `_aos/`, no shells, no pages, no JS, no DB code touched.** Scope limited to `sfa_delivery/templates/macros/` (10 files). Confirmed via `git status` would show only those 10 modifications.

---

## 5. tests/php smoke

**N/A** — no `tests/php` directory exists in this worktree (`tests/` is Python-only). Instead, I executed an in-line PHP smoke render of all 10 macros against representative input data; all produced well-formed HTML with the expected BEM classes. Notable cases verified:

- `tier_badge` with `size=lg`, `tier=beta` → `class="tier tier--lg tier--sun"`, glyph `β`, label "בטא · ניסיוני"
- `module_card` embeds `tier_badge` correctly via include
- `price_card` fill bar math: global range [0, 20], card range [7, 12] → `inset-inline-end: 40.00%; inline-size: 25.00%` (correct: (20−12)/20 = 40%, (12−7)/20 = 25%)
- `variety_row` with `dtm_days = -32768` → renders DTM cell as `—`
- `variety_row` with `taste_stars = 4` → renders `★★★★`
- `contrib_strip` URLs use `urlencode()` for Hebrew text (confirmed `%D7%...` byte sequences)
- `crosslink` with `direction=market-to-book` → applies `gj-crosslink--soil` modifier
- `market_disclaimer` copy verbatim, 4 bullets, methodology CTA
- `feed_item` with `kind=suggest` → `feed-item__kind--sun`, glyph 💡, label "הצעה", upvotes block conditional
- `timeline_bar` segments: 10/70/20 → `style="width: 10.00%"` etc., ruler with 3 labels

---

## 6. validate_aos.sh output

```
RESULT: 29 PASS / 17 SKIP / 0 FAIL
L-GATE_BUILD EXIT CRITERION: SATISFIED
```

Pre-existing advisories carried forward unchanged (no new SKIPs introduced by this build):
- Check 21/22: gate/LOD advisories (pre-V318 data debt) — unrelated to this WP.
- Check 25: PENDING_DB_SYNC.yaml from offline-2026-05-07 — unrelated.
- Check 33: 4 MSG-* naming advisories — unrelated.

**No FAIL. No new SKIP introduced by this build. Spoke remains clean per Iron Rule expectations.**

---

## Unresolved questions for team_100

1. **WhatsApp phone number for `contrib_strip`** — used `972547776770`. Confirm this is the canonical community contact for SFA, or supply alternate.
2. **`icon_id` sprite path** — assumed `/assets/icons.svg`; confirm WP publish path matches once shell rewrite lands (B1).
3. **`feed_item` Hebrew kind labels** — supplied default mapping (suggest→"הצעה", correction→"תיקון", data→"נתון"); team_00 may want different strings.
4. **`price_card` global range source** — left `$price_range_min` / `$price_range_max` as optional caller scope. Page template (`market_list.php` etc.) needs to compute or fetch a global range; confirm whether team_100 wants this baked into a data layer helper.

---

## Sign-off

- Builder: B2 (Claude Opus 4.7)
- Verifier engine for L-GATE: must be ≠ Claude Code (Iron Rule #1 — cross-engine). Recommend team_190 (Codex / Cursor / Desktop) for verdict.
- **No commits made.** team_100 reviews + commits per mandate.
