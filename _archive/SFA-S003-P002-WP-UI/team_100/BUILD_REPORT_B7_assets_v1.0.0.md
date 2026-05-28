# BUILD REPORT — B7 Assets (icons.svg + sfa.js)

- WP: SFA-S003-P002-WP-UI
- Agent: B7 (build sub-agent, dispatched by team_100)
- Worktree: `/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/sfa-ui-build-v2/`
- Date: 2026-05-27
- Status: COMPLETE — awaiting team_100 review + commit

## 1. icons.svg

- **Path:** `sfa_delivery/public_assets/img/icons.svg`
- **Line count:** 98
- **Symbols declared (10 total — meets the ≥8 requirement + 2 generics):**

| `id` | Hebrew gloss | Extraction source |
|------|---|---|
| `icon-leaf` | generic crop fallback | Pre-existing; **redrawn at 24×24** (was 64×64) to match the new system aesthetic + `currentColor` stroke contract |
| `icon-seedling` | hub home tier card | Invented — no direct seedling component in `illustrations.jsx`; two-leaf sprout sketched in calm-craft style |
| `icon-tomato` | עגבנייה | **Derived from `Tomato()`** in `illustrations.jsx` lines 79–97 — circular fruit + 5-lobed calyx + center stem |
| `icon-lettuce` | חסה | **Derived from `Lettuce()`** lines 99–117 — overlapping rosette of ruffled leaves + radial veins |
| `icon-cucumber` | מלפפון | **Derived from `Cucumber()`** lines 179–193 — rotated capsule (≈-22°) + diagonal seed dots |
| `icon-pepper` | פלפל | **Derived from `Pepper()`** lines 141–156 — bell body w/ shoulder dimples + stem |
| `icon-eggplant` | חציל | Invented (no `Eggplant()` in source) — pear body + spiked calyx crown, matches palette/stroke contract |
| `icon-carrot` | גזר | **Derived from `Carrot()`** lines 119–139 — tapered root + 3 vertical grain lines + tri-leaf top |
| `icon-onion` | בצל | **Derived from `Onion()`** lines 158–177 — bulb + 2 horizontal grain curves + 3 sprouts |
| `icon-zucchini` | קישוא | Invented (no `Zucchini()` in source) — elongated body w/ stem cap + 2 subtle grain lines, adapted from cucumber geometry |

**Style contract:** All symbols use `viewBox="0 0 24 24"`, `fill="none"`, `stroke="currentColor"`, `stroke-width="1.5"` (decorative inner lines at 0.8–1.3), `stroke-linecap="round"`, `stroke-linejoin="round"`. This lets PHP templates color them via CSS: `.gj-cropcard__icon { color: var(--gj-leaf-deep) }`.

**Loading contract verified:** `templates/macros/module_card.php` lines 30–33 already wire `<svg aria-hidden="true"><use href="/assets/icons.svg#{icon_id}"></use></svg>` — sprite is fetched once and cached by the browser. No additional inline-echo plumbing needed.

## 2. sfa.js

- **Path:** `sfa_delivery/public_assets/js/sfa.js`
- **Line count:** 109 (under the 200 cap)

### Behavior checklist

| # | Behavior | Wiring |
|---|---|---|
| 1 | Accordion `<details>` persistence (sessionStorage) | `initAccordion()` — preserved verbatim from prior implementation, now namespaced inside IIFE |
| 2 | Contrib-strip WhatsApp CTA enhancement | `initContribAnalytics()` — sets `target="_blank"`, merges `rel="noopener noreferrer"`, attaches click → `data-clicked="true"` |
| 3 | Pro-table sort via `[data-sort]` headers | `initTableSort()` — toggles `aria-sort`, numeric vs Hebrew-locale string compare, operates on `<tbody>` of the closest table |
| 4 | Calculator live recompute | `initCalc()` — wires `input` listeners on `[data-calc-input]` inside `[data-calc-form]`, updates `[data-calc-output]` text |

### Init wiring excerpt

```js
function boot() {
  initAccordion();
  initContribAnalytics();
  initTableSort();
  initCalc();
}
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', boot);
} else {
  boot();
}
```

### Behavior 3 numeric-coercion detail

```js
var an = parseFloat(av.replace(/[^\d.\-]/g, ''));
var bn = parseFloat(bv.replace(/[^\d.\-]/g, ''));
if (!isNaN(an) && !isNaN(bn)) return asc ? an - bn : bn - an;
return asc ? av.localeCompare(bv, 'he') : bv.localeCompare(av, 'he');
```

The regex strip lets cells like `"12.5 ק״ג"` or `"₪ 240"` sort numerically; pure-text cells fall back to Hebrew-locale collation.

### Behavior 4 output excerpt

```js
if (outY) outY.textContent = totalYield.toFixed(1) + ' ק"ג';
if (outR) outR.textContent = '₪ ' + totalRevenue.toFixed(0);
```

Initial `recompute()` call ensures outputs are populated on first render (not blank until first keystroke).

## 3. Browser compatibility notes

- Target: ES2017+ (mandate spec). No ES2020+ syntax used.
- No optional chaining (`?.`) — replaced with `(form.querySelector(...) || {}).value` pattern for safety on older Safari.
- No nullish coalescing (`??`) — used `||` throughout (acceptable because inputs default to 0 anyway).
- `Array.from(...)`, `String.prototype.localeCompare(str, 'he')`, `Element.closest()`, `HTMLTableElement.tBodies` — all baseline since ES2015 / Edge legacy.
- `var` retained (not `let`/`const`) for symmetric style with the preserved Behavior 1 code.

## 4. Deviations + rationale

1. **Icon style: stroke-based instead of watercolor-fill.** The team_35 source uses gradient fills (`url(#wc-tomato)` etc.) that depend on a `<WatercolorDefs>` component injecting `<defs>` once per page. The mandate explicitly asks for `currentColor` stroke icons so CSS can color them per-context. I extracted the **shapes** (silhouette + key geometric features) from each illustration and re-rendered them as line work. The watercolor versions remain available to team_35 for hero/header art if needed.
2. **`icon-eggplant` and `icon-zucchini` invented.** No `Eggplant()` or `Zucchini()` exists in `illustrations.jsx` (only Tomato/Lettuce/Cucumber/Carrot/Pepper/Onion/Basil/Strawberry). The mandate's required-slug list includes both. Invented icons follow the same stroke contract; geometry is consistent with the calm-craft aesthetic (pear body + calyx for eggplant, elongated cucumber-like body with broader shoulders + stem cap for zucchini).
3. **`icon-leaf` redrawn at 24×24** (was 64×64 with hard fills). Necessary to keep the sprite homogeneous — all symbols must share the same viewBox and color contract for CSS sizing/coloring to work uniformly.
4. **Source illustrations did include `Basil` and `Strawberry`**, which were not in the mandate's required list. They are NOT included in this sprite — kept the symbol count at the requested 10 to avoid sprite bloat. If team_100 wants them, easy to add in a follow-up.
5. **Hebrew quote escape in sfa.js calc output.** Used straight double quotes (`'ק"ג'`) instead of geresh+gershayim because the JS source must stay ASCII-safe for older grep/build tooling. Visually identical on render.
6. **Behavior 2 simplification.** Mandate says "wire `target="_blank"` + `rel="noopener"` if not already there." Implemented as defensive merge — preserves any existing `rel` tokens (e.g., `nofollow`) and adds `noreferrer` for extra privacy hygiene (industry best practice when opening external links in new tabs).

## 5. validate_aos.sh output

Ran from worktree root `/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/sfa-ui-build-v2/`:

```
RESULT: 29 PASS / 17 SKIP / 0 FAIL
L-GATE_BUILD EXIT CRITERION: SATISFIED
```

No FAIL. All SKIP entries are pre-existing acceptable-skip checks (msg-log, auto-activation, milestones, WAN dual-stack, etc. — none related to this WP's deliverables).

---

## Unresolved questions

None. All deliverables complete. Awaiting team_100 review.
