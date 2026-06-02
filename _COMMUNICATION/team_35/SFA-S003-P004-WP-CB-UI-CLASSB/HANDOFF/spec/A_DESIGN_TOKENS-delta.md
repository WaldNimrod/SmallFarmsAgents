# DESIGN_TOKENS.md — delta for Crop Book v1

> **WP:** SFA-S003-P004-WP-CB-1 · extends canonical `DESIGN_TOKENS.md`.

> **v2 palette (revision):** the neutral base moved off cream/brown to **white with a whisper of green**. Only the *neutral* tokens changed — the leaf/tomato/sun/soil/code accent worlds are unchanged.
>
> | token | was (cream) | now (green-white) |
> |---|---|---|
> | `--gj-paper` | `#f6f1e3` | `#f8fbf8` |
> | `--gj-paper-2` | `#ece5d2` | `#eef4ee` |
> | `--gj-paper-3` | `#ddd2b2` | `#dde8dd` |
> | `--gj-ink` | `#2a2418` (warm) | `#1f2a22` (green-charcoal) |
> | `--gj-ink-soft` | `#776a4d` | `#5d6b5e` |
> | `--gj-line` | `#d8ccae` | `#dce6dc` |
>
> Shadows re-tinted green-neutral. Dark chrome (`.board__top`, tooltips, `.ref-srcbar`, `.calc-context`, table footers) shifted to a green-charcoal ground with `#eef4ee` text; sticky-header accent line moved tomato → leaf. Watercolor masters still `mix-blend-mode: multiply` — they sit cleaner on near-white.
>
> **Field ordering (within a topic):** related fields must be adjacent — `rows_per_bed` + `in_row_spacing_cm` pair; timing fields (`harvest_window` + `succession_interval`) pair; climate (`frost_tolerance` + `needs_summer_shade`) pair; water (`irrigation_type` + `root_depth_class`) pair. The 2-col field grid renders each pair as one row.

---

## 1. New custom properties — confidence / provenance / assumptions

```css
:root {
  /* ─── Confidence / provenance state (Gap-Fill Plan §2) ─── */
  --cb-validated:    var(--gj-leaf-deep);   /* #4d6a2c — plain, trustworthy value */
  --cb-unvalidated:  var(--gj-sun-deep);    /* #a4711a — asterisk + tooltip       */
  --cb-missing:      var(--gj-tomato-deep); /* #8e3018 — "—" + request-info        */

  /* ─── AssumptionField (NEW component) ─── */
  --cb-assume:       var(--gj-code);         /* #2d8a8c — teal "digital/planning" accent */
  --cb-assume-wash:  #e3eeee;                /* panel background                          */

  /* ─── one new world ramp value (was implicit) ─── */
  --gj-sun-deep:     #a4711a;                /* deep sun for unvalidated text on paper    */

  /* ─── brand wordmark face ─── */
  --gj-font-brand:   "Carmela", "Frank Ruhl Libre", serif;  /* SFA wordmark + hero display */
}
```

**Rationale**
- Confidence states reuse the **world ramp** so the palette stays closed: leaf = trust, sun = caution, tomato = attention/gap. No new hues invented.
- The AssumptionField gets the **code/digital teal** (`--gj-code`) — it is the only place teal appears in the book, which makes "this is a tunable planning assumption, not crop data" instantly legible against the green book values and amber calculator chrome.
- `--gj-sun-deep` is added because the existing `--gj-sun` (#d39a32) fails AA as text on `--gj-paper`; the asterisk + unvalidated labels use the deep variant.

---

## 2. Carmela — wordmark / display face

Carmela (brand master, `source_masters/font_carmela/`) is registered for the **SFA wordmark and crop-hero display only**. Body + UI stay on Assistant; headings stay on Frank Ruhl Libre (the locked kit). Carmela is brand seasoning, not a body face.

```css
@font-face {
  font-family: "Carmela";
  src: url("assets/Carmela.ttf") format("truetype");
  font-weight: 400 700; font-display: swap;
}
.sh__name, .board__brand b { font-family: var(--gj-font-brand); }
```

> **Open issue Q3** — confirm Carmela may be self-hosted/subset for the public app, or whether the wordmark should be shipped as an SVG (no font dependency).

---

## 3. Calculator chrome — semantic color map

| Surface | Token | Meaning |
|---------|-------|---------|
| Book value chip (`.bv`) | `--gj-leaf` wash | reconciled `value_best`, cross-linked to the book |
| AssumptionField (`.af`) | `--cb-assume` / `--cb-assume-wash` | adjustable planning assumption |
| User input (`.ipt`) | `--gj-line` / `--gj-paper` | neutral — the user's own number |
| Calculator header / result | `--gj-sun` wash · `--gj-soil-deep` numerals | the beta "calculator" world |
| Disabled calc (`.cv.is-disabled`) | `--gj-paper-2` + `--gj-tomato` dashed | a required field is missing |

This three-language operand coding (green book / teal assumption / neutral input) is the core legibility decision of the calculator panel — keep it consistent everywhere a calculator appears (Cards, Table inline, crop page).

---

## 4. No changes to

Spacing scale, radii, shadows, breakpoints (900 / 1280), z-index map, animation budget — all inherited unchanged. The calculator interactions use only the existing "hover lift / chevron rotate" motion budget plus one new affordance: the AssumptionField `.af__edit` 180ms ✎-rotate on open.
