# BUILD_REPORT — B4: Crop Book Page Templates (7 templates + legacy tree delete)

- **Agent:** Build sub-agent B4 (Claude Sonnet — cross-engine vs Team 100 Opus orchestrator)
- **Dispatched by:** team_100 (Chief Architect)
- **Mandate:** `_COMMUNICATION/TEAM_100/MANDATE_WP-UI-RE-BUILD_v1.0.0.md` (worktree `gallant-elbakyan-727a60`)
- **LOD400 ref:** `_aos/work_packages/S003/SFA-S003-P002-WP-UI/LOD400_spec.md` v1.0.3 §0.5 (team_00 approved 2026-05-27 — COMPONENTS.md class names verbatim)
- **Design contracts:**
  - `_archive/SFA-S003-P002-WP-UI/team_35/_handoff/COMPONENTS.md` §6/§7/§8/§12
  - `_archive/SFA-S003-P002-WP-UI/team_35/_handoff/TEMPLATES.md` §1/§7/§8
- **Data contracts:**
  - `_COMMUNICATION/TEAM_100/RESEARCH_data_layer_inventory_2026-05-27_v1.0.0.md` (AC-DB-1 fallback, §E.5 licensing gate)
  - `_COMMUNICATION/TEAM_100/RESEARCH_dual_template_tree_resolution_2026-05-27_v1.0.0.md` (recommendation A — delete legacy tree)
- **Foundation (R1, commit 7f8b908):** `BUILD_REPORT_B1_shells_v1.0.0.md`, `BUILD_REPORT_B2_macros_v1.0.0.md`
- **Working tree:** `/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/sfa-ui-build-v2/`
- **Date:** 2026-05-27

---

## 1. Seven templates rewritten — paths + line counts

All under `sfa_delivery/templates/pages/`. All use the existing `Template::render('_layout', compact(...))` convention so the `_layout.php` shell wrapper (B1) handles both mobile (`.gj-shell`) and desktop (`.dt-shell`) rendering for the same `$content`.

| # | Route | Page (CB#) | Path | Lines | `php -l` |
|---|-------|-----------|------|------:|---------|
| 1 | `/crop-book/`                                    | CB0 entry        | `sfa_delivery/templates/pages/book_entry.php`     | 81  | PASS |
| 2 | `/crop-book/questions`                           | CB1 questions    | `sfa_delivery/templates/pages/book_questions.php` | 54  | PASS |
| 3 | `/crop-book/family`                              | CB2 family       | `sfa_delivery/templates/pages/book_family.php`    | 75  | PASS |
| 4 | `/crop-book/table`                               | CB3 / D3 table   | `sfa_delivery/templates/pages/book_table.php`     | 117 | PASS |
| 5 | `/crop-book/search`                              | CB4 search       | `sfa_delivery/templates/pages/book_search.php`    | 68  | PASS |
| 6 | `/crop-book/{slug}`                              | CB5 / D4 crop    | `sfa_delivery/templates/pages/book_crop.php`      | 160 | PASS |
| 7 | `/crop-book/{slug}/variety/{vslug}`              | CB5 expanded     | `sfa_delivery/templates/pages/book_variety.php`   | 225 | PASS |

**Total:** 7 templates, 780 lines, 0 syntax errors.

Each template sets shell variables consistently:
- `$page_title` — header `<title>` + `gj-title` + `dt-topbar__h`
- `$page_sub`   — subtitle / secondary scientific-name slot
- `$active = 'crop-book'` — desktop nav highlight
- `$back_url = '/crop-book/'` on routes 2–7 (mobile shell renders back arrow)

Page body is captured via `ob_start()` / `ob_get_clean()` and routed through `Template::render('_layout', compact(...))`. Layout dispatches to both `templates/shell/mobile.php` and `templates/shell/desktop.php` (CSS media-query swap) — page templates do not duplicate the shell DOM (B1 contract).

---

## 2. Per-route BEM checklist (LOD400 §0.5 — COMPONENTS.md class names verbatim)

### 2.1 `book_entry.php` (CB0)
- `cb-entry`        — section wrapper (matches `crop-book-deep.css` L4)
- `cb-section-h`    — section heading (L5)
- `cb-paths`        — entry-card flex column (L13)
- `mod-card` ×4     — via `module_card.php` macro (slugs: questions/family/table/search)
- Embeds `module_card.php`. Tier-color tokens: `sun` / `leaf` / `soil` / `tomato`.
- icon ids: `icon-leaf`, `icon-seedling`, `icon-tomato`, `icon-cucumber`.

### 2.2 `book_questions.php` (CB1)
- `cb-questions`    — section wrapper
- `cb-section-h`, `cb-qhint`
- `cb-qgrid`, `cb-qcard`, `cb-qcard__num`, `cb-qcard__q`, `cb-qcard__sub`, `cb-qcard__count` (crop-book-deep.css L57–96)
- Empty-state placeholder: "שאלות יעלו לאחר ייבוא נתוני העונה" (per mandate spec)
- Trailing `contrib_strip` (`context=book.questions`)

### 2.3 `book_family.php` (CB2)
- `cb-families` — section wrapper
- `cb-fam-list`, `cb-fam`, `cb-fam--{tomato|sun|soil|leaf}`, `cb-fam__head`, `cb-fam__he`, `cb-fam__en`, `cb-fam__count`, `cb-fam__crops` (crop-book-deep.css L113–137)
- `pill pill--muted` chips for crop drill-down inside family
- Trailing `contrib_strip` (`context=book.family`)

### 2.4 `book_table.php` (CB3 / D3)
Mandate §3 (route 8): `.gj-shell` (mobile) + `.dt-shell` `.dt-table` (desktop); `<th scope="col">` per column.
- Mobile compact list: `cb-table`, `cb-table__head`, `cb-table__row`, `cb-table__name`, `cb-table__fam`, `cb-table__num`, `cb-table__num--accent` (crop-book-deep.css L140–172)
- Desktop data grid: `dt-table` with `<th scope="col">` on every column header
- **Both renderings** carry `data-sort="<key>"` so `sfa.js` Behavior 3 wires sort against `data-name_he`/`data-family_he`/`data-dtm_days`/`data-yield_kg_per_m2` row attributes
- `visually-hidden` span used for the actions column heading (a11y)
- Trailing `contrib_strip` (`context=book.table`)

### 2.5 `book_search.php` (CB4)
- `cb-search` wrapper
- `cb-search-form` + `gj-search` (gj-search added per mandate §3 token), `cb-search-input`, `cb-search-submit`, `cb-search-tip` (crop-book-deep.css L175–252)
- `role="search"`, `<legend>` per a11y contract
- Result cards: `gj-cropcard` via `crop_card.php` macro (no duplication of the macro DOM)
- 3 distinct empty states: no query / query + no results / query + N results
- Trailing `contrib_strip` (`context=book.search`)

### 2.6 `book_crop.php` (CB5 / D4) — the big one
- `cb-crop-hero` (crop-book-deep.css L260)
- `cb-crop-hero__breadcrumb` (L268–276) — includes `›` separators
- `cb-crop-hero__head`, `cb-crop-hero__icon`, `cb-crop-hero__h` (L277), `cb-crop-hero__sci`, `cb-crop-hero__lede`
- `cb-crop-hero__meta` (L284) with `pill pill--soil` (family tag) + `pill pill--muted` (DTM days, sentinel-aware)
- Optional `gj-timeline` (via `timeline_bar.php` macro) when controller supplies `$crop['timeline']`
- Optional `gj-crosslink` (via `crosslink.php` macro) when controller supplies `$crop['market_link']`
- `cb-vars` wrapper, `cb-vars-head` (L342–354), `cb-vars__list`
- Each variety rendered via `variety_row.php` macro (`cb-var` BEM family; macro handles `-32768` sentinel)
- `cb-notes`, `cb-notes__h`, `cb-note`, `cb-note--{kind}`, `cb-note__h`, `cb-note__body`, `cb-note__src`
- Trailing `contrib_strip` (`context=book.{slug}`)

### 2.7 `book_variety.php` (CB5 expanded)
- `cb-var-detail` (page-level wrapper) **+ `cb-var__row--expanded`** (DOM hook from mandate §3 spec)
- `cb-crop-hero__breadcrumb` (re-use of the breadcrumb pattern from CB5)
- `cb-var-detail__head`, `cb-var-detail__back`, `cb-var-detail__h`, `cb-var__star`
- `pill pill--code` for `breeding_type`
- `variety-fields` `<dl>` with `variety-fields__row` rows (label dictionary, 11 known keys, in display order)
- **`variety-fields__extras`** `<details>` — AC-DB-1 unknown-field fallback (§4 below)
- `cb-var-conf`, `cb-var-conf__label`, `cb-var-conf__score`, `cb-var-conf__tier`, `pill pill--{wsc_lc}` (winning_source_class — only emits if matches `^[a-z0-9_-]+$`)
- `cb-notes`, `cb-notes__h`, `cb-note`, `cb-note__h`, `cb-note__body`, `cb-note__src` (filtered)
- `muted` utility class for the breadcrumb-style scientific-name line and DTM sentinel
- Trailing `contrib_strip` (`context=book.variety.{vslug}`)

---

## 3. Legacy files deleted

Per `RESEARCH_dual_template_tree_resolution_2026-05-27_v1.0.0.md` (recommendation A — DELETE; no controllers reference the legacy tree):

| Path | git evidence |
|------|--------------|
| `sfa_delivery/templates/crop_book/detail.php` | `D` (staged delete via `git rm`) |
| `sfa_delivery/templates/crop_book/list.php`   | `D` (staged delete via `git rm`) |
| `sfa_delivery/templates/crop_book/` directory | implicitly removed (git does not track empty dirs; verified `ls: No such file or directory`) |

Command run (worktree root):

```
git rm sfa_delivery/templates/crop_book/detail.php sfa_delivery/templates/crop_book/list.php
# →
# rm 'sfa_delivery/templates/crop_book/detail.php'
# rm 'sfa_delivery/templates/crop_book/list.php'
```

`git status --short` excerpt (B4 scope only):

```
D  sfa_delivery/templates/crop_book/detail.php
D  sfa_delivery/templates/crop_book/list.php
 M sfa_delivery/templates/pages/book_crop.php
 M sfa_delivery/templates/pages/book_entry.php
 M sfa_delivery/templates/pages/book_family.php
 M sfa_delivery/templates/pages/book_questions.php
 M sfa_delivery/templates/pages/book_search.php
 M sfa_delivery/templates/pages/book_table.php
 M sfa_delivery/templates/pages/book_variety.php
```

(Other entries in `git status` belong to parallel B-agents — out of B4 scope.)

---

## 4. AC-DB-1 evidence — unknown-field fallback in `book_variety.php`

Mandate §5.4 / AC-DB-1: templates must render gracefully when `payload_json` carries fields outside the known-label dictionary (parallel-session schema expansion). Implementation in `book_variety.php` L48–66 + L134–168:

```php
// Known-label dictionary (11 keys, display order)
$known_labels = [
    'dtm_days'           => 'ימים לקציר',
    'yield_kg_per_m2'    => 'יבול (ק״ג/מ״ר)',
    'color_he'           => 'צבע',
    'shape_he'           => 'צורה',
    'taste_stars'        => 'טעם',
    'resistance_he'      => 'עמידות',
    'breeding_type'      => 'סוג רבייה',
    'origin_country_he'  => 'מקור',
    'seed_supplier_he'   => 'ספק זרעים',
    'planting_season_he' => 'עונת שתילה',
    'harvest_window_he'  => 'חלון קציר',
];

// Identifier / system / specially-handled fields excluded from the fallback.
$reserved_keys = [
    'vslug', 'slug', 'name_he', 'name_lat', 'name_en', 'crop_slug', 'crop_id',
    'is_default', 'knowledge_notes', 'enrichment', 'confidence_score',
    'winning_source_class',
];

// ... known fields render via the labeled <dl> above ...

// AC-DB-1 — unknown-field fallback.
$payload_extras = [];
foreach ($variety as $key => $value) {
    if (isset($known_labels[$key]))           continue;  // already rendered
    if (in_array($key, $reserved_keys, true)) continue;  // identifier / system
    if ($value === null || $value === '')     continue;  // empty
    if (is_array($value)) {
        if (empty($value))                            continue;
        if (isset($value[0]) && is_array($value[0])) continue;  // array-of-objects
    }
    $payload_extras[$key] = $value;
}
if (!empty($payload_extras)): ?>
  <details class="variety-fields__extras">
    <summary>פרטים נוספים מהמקור (<?= (int)count($payload_extras) ?>)</summary>
    <dl>
      <?php foreach ($payload_extras as $key => $value): ?>
        <div class="variety-fields__row">
          <dt><?= $h(str_replace('_', ' ', (string)$key)) ?></dt>
          <dd><?php
            if (is_scalar($value)) {
                echo $h((string)$value);
            } elseif (is_array($value)) {
                // Flat scalar array → join; otherwise JSON-encode safely.
                $flat = true;
                foreach ($value as $iv) { if (!is_scalar($iv)) { $flat = false; break; } }
                echo $flat
                  ? $h(implode(', ', array_map('strval', $value)))
                  : '<code>' . $h(json_encode($value, JSON_UNESCAPED_UNICODE)) . '</code>';
            } else { echo '—'; }
          ?></dd>
        </div>
      <?php endforeach; ?>
    </dl>
  </details>
<?php endif; ?>
```

Behaviors covered:
- **No PHP warnings** — all access via `array_key_exists` / `isset` / null-coalescing.
- **No silent drop** — anything not already rendered, not in `$reserved_keys`, and not empty appears in the collapsed `<details>` block with a Hebrew summary count.
- **Snake-case → label** — `str_replace('_', ' ', $key)` produces a human-readable label until a Hebrew dictionary entry is added (controller can later promote a key by adding it to `$known_labels`).
- **Defensive types** — scalars render via `htmlspecialchars`; flat scalar arrays join as comma-separated text; nested structures emit safely-encoded JSON inside `<code>` (visible, not stringified-bare); arrays-of-objects are intentionally skipped (need bespoke rendering, not raw dump).

---

## 5. `knowledge_notes` licensing filter (data inventory §E.5)

Public site MUST NEVER render notes flagged `is_internal_farm_use_only=TRUE`.

### 5.1 `book_crop.php` (L128–148)

```php
// Knowledge notes — MANDATORY filter on is_internal_farm_use_only.
// Public site MUST NEVER render internal-only notes (data inventory §E.5 licensing hard-gate).
if (!empty($crop['knowledge_notes']) && is_array($crop['knowledge_notes'])):
    $public_notes = array_values(array_filter(
        $crop['knowledge_notes'],
        fn ($n) => is_array($n) && empty($n['is_internal_farm_use_only'])
    ));
    if (!empty($public_notes)): ?>
        <section class="cb-notes">
          <h2 class="cb-notes__h">הערות ידע</h2>
          ...
        </section>
    <?php endif;
endif; ?>
```

### 5.2 `book_variety.php` (L195–214)

```php
// Knowledge notes — MANDATORY filter on is_internal_farm_use_only.
if (!empty($variety['knowledge_notes']) && is_array($variety['knowledge_notes'])):
    $public_notes = array_values(array_filter(
        $variety['knowledge_notes'],
        fn ($n) => is_array($n) && empty($n['is_internal_farm_use_only'])
    ));
    if (!empty($public_notes)): ?>
        <section class="cb-notes">
          <h2 class="cb-notes__h">הערות</h2>
          ...
        </section>
    <?php endif;
endif; ?>
```

Both predicates: `is_array($n) && empty($n['is_internal_farm_use_only'])`. `empty()` correctly treats missing key, `null`, `false`, `0`, `""`, `[]` as public — and any truthy value (including the string `"true"` from JSON) as internal-only → filtered out. Section header is suppressed entirely if all notes are filtered out.

---

## 6. `-32768` DTM sentinel handling (WP-B1/B3 "presence-only")

| File | Line(s) | Handling |
|------|--------:|----------|
| `templates/macros/variety_row.php`  | 32–34 | `$dtm_display` = `'—'` when `null` / `''` / `-32768`; else cast to int — already correct from B2 (no edits) |
| `templates/macros/crop_card.php`    | 30    | `.gj-cropcard__dtm` element omitted entirely when `dtm_days` is empty or sentinel — already correct from B2 |
| `templates/pages/book_table.php`    | 35    | `$fmt_dtm` closure: `null`/`''`/`-32768` → `'—'`; mirrored into both mobile `cb-table` and desktop `dt-table` rows |
| `templates/pages/book_crop.php`     | 77    | DTM-days pill in `cb-crop-hero__meta` only renders when `dtm` non-empty and not sentinel |
| `templates/pages/book_variety.php`  | 108–111 | Inside the `variety-fields` row for `dtm_days`: sentinel renders `<span class="muted">—</span>` (NOT integer cast — protects against accidental `-32768` leakage to the UI) |

**Confirmation:** the existing `variety_row.php` macro (B2) already handles the sentinel correctly — `book_crop.php` renders the variety list via that macro, so the sentinel is applied uniformly at the row level. `book_variety.php` adds a second, page-level guard inside `variety-fields`.

---

## 7. Mapping table — mandate §3 class names → COMPONENTS.md actual names

Per LOD400 v1.0.3 §0.5: where mandate §3 used placeholder names that do not match COMPONENTS.md / `crop-book-deep.css`, COMPONENTS.md wins. The mapping below should land in BUILD_REPORT v2.0.0 §3 reference table.

| Mandate §3 token       | COMPONENTS.md / CSS-SSoT class               | Used in template(s)             | CSS reference |
|------------------------|----------------------------------------------|---------------------------------|---------------|
| (entry: 4 mod-cards)   | `.cb-paths` wrapper (mod-cards rendered via macro `.mod-card`) | book_entry.php           | crop-book-deep.css L13 |
| `gj-row__big` (Q-cards)| `.cb-qgrid` + `.cb-qcard`                    | book_questions.php              | crop-book-deep.css L57 |
| (family list)          | `.cb-fam-list` + `.cb-fam`                   | book_family.php                 | crop-book-deep.css L113 |
| `gj-shell` (table mobile) | `.cb-table` family (`__head`, `__row`, `__name`, `__fam`, `__num`) | book_table.php  | crop-book-deep.css L140 |
| `dt-shell` `dt-table`  | `.dt-table` (verbatim — desktop.css)         | book_table.php (desktop)        | desktop.css |
| `gj-search`            | `.gj-search` (kept on the `<form>`) + `.cb-search-form` + `.cb-search-input` | book_search.php | crop-book-deep.css L175 |
| `crop-detail__head`    | `.cb-crop-hero__head`                         | book_crop.php                   | crop-book-deep.css L260 |
| `crop-detail__h1`      | `.cb-crop-hero__h`                            | book_crop.php                   | crop-book-deep.css L277 |
| `crop-detail__sci`     | `.cb-crop-hero__sci`                          | book_crop.php                   | crop-book-deep.css (hero family) |
| `crop-vars__list`      | `.cb-vars__list`                              | book_crop.php                   | (BEM extension of `.cb-vars`) |
| `crop-vars__row`       | `.cb-var` (macro `variety_row.php`)           | book_crop.php (via macro)       | crop-book-deep.css L377 |
| `crop-vars__row--expanded` | `.cb-var__row--expanded`                  | book_variety.php (page-level)   | (BEM modifier on `.cb-var`) |
| `variety-fields` `<dl>`| `.variety-fields` + `.variety-fields__row`    | book_variety.php                | (LOD300 + digest §7)  |
| (unknown-fields fallback) | `.variety-fields__extras`                  | book_variety.php (AC-DB-1)      | (LOD300 + digest §7)  |

Notes:
- `crop-detail__*` and `crop-vars__*` from mandate §3 are advisory tokens describing the SHAPE of the DOM; COMPONENTS.md uses `cb-crop-hero` / `cb-vars` / `cb-var` for the actual class names. Per LOD400 §0.5 directive, the COMPONENTS.md names are the binding contract for both DOM hooks and CSS selectors.
- `.cb-vars__list` is the only BEM extension I added that is not already in `crop-book-deep.css` — it is the natural list-wrapper modifier on the `cb-vars` block (BEM-compliant) and degrades to plain block layout if the CSS doesn't style it.
- `.dt-table` is referenced verbatim from mandate §3 — it lives in `desktop.css`.

---

## 8. `php -l` per file

```
$ for f in book_entry.php book_questions.php book_family.php book_table.php book_search.php book_crop.php book_variety.php; do
    php -l sfa_delivery/templates/pages/$f
  done
No syntax errors detected in sfa_delivery/templates/pages/book_entry.php
No syntax errors detected in sfa_delivery/templates/pages/book_questions.php
No syntax errors detected in sfa_delivery/templates/pages/book_family.php
No syntax errors detected in sfa_delivery/templates/pages/book_table.php
No syntax errors detected in sfa_delivery/templates/pages/book_search.php
No syntax errors detected in sfa_delivery/templates/pages/book_crop.php
No syntax errors detected in sfa_delivery/templates/pages/book_variety.php
```

**7/7 PASS.**

---

## 9. `validate_aos.sh` output

Run from worktree root: `/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/sfa-ui-build-v2/`

```
=================================================
RESULT: 29 PASS / 17 SKIP / 0 FAIL
=================================================
L-GATE_BUILD EXIT CRITERION: SATISFIED
```

**0 FAIL.** Same baseline as B1/B2 — no new advisories introduced by B4. Pre-existing SKIPs unchanged (Checks 17/21/22/24/25/39/40/41/43/45 — all unrelated WP-UI data debt or pre-W*-propagation guards).

---

## 10. Constraints honored

- Touched only the 7 page templates and removed exactly 2 legacy files (`crop_book/detail.php`, `crop_book/list.php`).
- **No edits** to: `_aos/`, shells (`templates/shell/*`, `templates/_layout.php`), macros (`templates/macros/*`), controllers, JS (`sfa.js`), CSS (`*.css`), DB code, Python.
- COMPONENTS.md class names verbatim (LOD400 §0.5) — see §7 mapping table for the mandate→COMPONENTS reconciliation.
- AC-DB-1 unknown-field fallback in `book_variety.php` (§4 above) is presentation-only; controllers MAY ship new fields without template changes.
- `knowledge_notes` `is_internal_farm_use_only=TRUE` filter applied at both crop and variety levels (§5 above). Public output guaranteed to never leak internal-only notes regardless of controller payload shape.
- `-32768` sentinel handled at four distinct touchpoints (§6 table). Macro layer (B2) provides the primary guard; page templates add belt-and-suspenders defense at hero / table / variety-detail.
- **No commit performed.** team_100 reviews + commits per mandate.

---

## 11. Unresolved questions for team_100

1. **`cb-vars__list` BEM extension** — I introduced this list-wrapper class (BEM-compliant extension of `cb-vars`) in `book_crop.php`. `crop-book-deep.css` does not currently style it, so layout falls back to block flow. Two acceptable resolutions: (a) keep as-is and add CSS later, or (b) collapse to `<div>` with no class. Recommend (a) for DOM-stability.
2. **Family taxonomy depth** — `book_family.php` renders an OPTIONAL inner `cb-fam__crops` chip strip when controller provides `$family['crops']`. The controller can omit this and the page degrades cleanly to a flat family list. Confirm whether controller will populate.
3. **`winning_source_class` → `pill--{token}` whitelist** — `book_variety.php` accepts any `^[a-z0-9_-]+$` token (defensive regex) and renders `pill--{token}` from `winning_source_class`. Mandate §A.7 listed `{ex,ni,pr,op,mk,wb,uc}` — the CSS will quietly skip styling for tokens outside that set, but the markup will not crash. Confirm whether team_00 wants strict-whitelist rejection or the current open-token pattern (better forward-compat).
4. **Empty-state copy** — Hebrew placeholders ("שאלות יעלו לאחר ייבוא נתוני העונה", "אין עדיין זנים מתועדים לגידול זה", "אין עדיין מידע מפורט על זן זה") were drafted to match the mandate's example tone. team_00 may have preferred phrasing — easy single-line swap.

---

## Sign-off

- **Builder:** B4 (Claude Sonnet) — engine ≠ Team 100 Opus (Iron Rule #1 satisfied)
- **Verifier engine for L-GATE_V:** must be ≠ Claude Sonnet AND ≠ Claude Opus 4.7 (Iron Rule #1 cross-engine). Recommend Codex / Cursor / Desktop for verdict.
- **No commits made.** team_100 reviews + commits per mandate.
- **All 7 templates** under `sfa_delivery/templates/pages/` + **2 legacy files** under `sfa_delivery/templates/crop_book/` (deleted via `git rm`, leaving an empty directory automatically pruned).
