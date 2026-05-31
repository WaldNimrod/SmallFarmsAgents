# HANDOFF_PACKAGE — SFA-S003-P004-WP-CB-1 — team_35 → team_100 — v1.0.0

**Date:** 2026-05-31
**From:** team_35 (Design Studio)
**To:** team_100 (Chief Architect — implementation)
**WP:** SFA-S003-P004-WP-CB-1 — ספר גידולים v1 (Calculator-Driven Planning Tool)
**Type:** DESIGN_HANDOFF (LOD300)
**Status:** RECEIVED + INDEXED (intake by team_100, 2026-05-31)

---

## 1. Provenance

Original delivery: `SFA Small Farms Agents (3).zip` → `design_handoff_crop_book_v1/`
(dropped by Nimrod / team_00, 2026-05-31 22:15). Extracted verbatim into this folder by
team_100 during WP-CB-1 UI-slice intake. **No design file was altered** — this is the
canonical, byte-for-byte handoff archive. Web-optimized derivatives (e.g. resized/webp
crop images) are produced separately under `sfa_delivery/public_assets/` during the build
and are NOT a substitute for these masters.

This package supersedes, for the crop-book surface, the earlier digest
`_COMMUNICATION/TEAM_100/RESEARCH_team35_design_digest_2026-05-27_v1.0.0.md` (which predates
the calculator/AssumptionField/provenance design layer).

## 2. Status of the WP at intake

- Backend slice **built + cross-engine verified** (commit `fd7dfba`): `calculators.py` (14),
  `assumptions.py`, `calculator_meta.py`, 2 `field_policy` wirings, ingest contract.
- Data layer **LOCKED**: Canon `WP-CB-0` (LOD200_LOCKED) + `WP-CB-MIG` (LOD500_LOCKED, `053313a`).
- This package satisfies the second unblocker for WP-CB-1 (the first being WP-CB-MIG's field-layer
  correction). LOD400 §10 (UI mockups) is filled by embedding this package; LOD400 locks to v1.0.0.

## 3. Contents

```
HANDOFF_PACKAGE/
├── HANDOFF_PACKAGE_v1.0.0.md     ← this manifest (team_100)
├── CHECKSUMS.sha256             ← sha256 of every design file (team_100)
├── README.md                    ← team_35 handoff brief + build order
├── design/
│   ├── LOD300 Crop Book v1.html  (109 KB)  pannable spec board — visual source of truth
│   ├── tokens.css                (5.8 KB)  --gj-* tokens (v2 white-green) — port verbatim
│   ├── cropbook-v1.css           (69 KB)   component styles (.cb-/.cv-/.af-) — visual contract
│   ├── cropbook-v1.js            (19 KB)   vanilla ES5 — CALC formulas + interactions — behavior contract
│   └── assets/
│       ├── Carmela.ttf           (1.4 KB)  brand wordmark/display font (subset; licensed per Q3)
│       ├── wc-lettuce.png        (3.3 MB)  watercolor master — חסה
│       ├── wc-radish.png         (2.5 MB)  watercolor master — צנונית
│       ├── wc-parsley.png        (3.7 MB)  watercolor master — פטרוזיליה
│       └── wc-dill.png           (2.1 MB)  watercolor master — שמיר
└── spec/
    ├── COMPONENTS-delta.md       (16 KB)   11 new component contracts + extensions
    ├── DESIGN_TOKENS-delta.md    (4.7 KB)  palette v2 + confidence/assumption tokens
    ├── TEMPLATES-delta.md        (6.4 KB)  route map + macro contracts + page composition
    └── OPEN_ISSUES.md            (5.1 KB)  8 resolved decisions + 7 proposed schema fields
```

Integrity: see `CHECKSUMS.sha256` (14 files). Carmela.ttf is a valid but heavily-subset
TrueType (wordmark glyphs only) — expected, not a corruption.

## 4. Design contract — DO NOT SHIP AS-IS

The `design/` files are a **reference prototype in HTML/CSS/JS**, not production code. The build
recreates them in the **Slim4/PHP on uPress** delivery tier (`sfa_delivery/`): server-rendered
templates + light vanilla JS. `tokens.css` ports verbatim; `cropbook-v1.css` is the visual
contract (adapt selectors to our template structure, preserve the result); `cropbook-v1.js` is
the behavior contract (its `CALC[kind]` formulas must stay in parity with the locked Python
`calculators.py`).

## 5. Resolved decisions (team_00, 2026-05-31) — binding

Q1 per-session override only · Q2 Cards default · Q3 Carmela licensed, self-host · **Q4 τ — see note** ·
Q5 lightweight request-info capture (no triage UI) · Q6 small calcs = modal, full = `/calc/` dashboard ·
Q7 main UI per-bed-meter, calc/full-detail shows documented units · Q8 single field "ימים במשתלה".

**τ note (team_00, this intake):** design Q4 proposes τ≥0.50; the locked backend ships **τ=0.40**
for v1 (decision: ship on locked threshold). τ=0.50 is recorded as a fast-follow corrective. The UI
renders `prov_value` cues against the backend's `field_state` — no UI-side threshold logic.

## 6. Proposed schema additions → routed to a gated WP

`OPEN_ISSUES.md §"still open"` proposes a 13-topic taxonomy + 7 field groups (seeder_model,
irrigation_type, root_depth_class, common_pests, sale_unit, labor_rate_*, plantings_per_season).
team_00 directed **Full** adoption. Because the data layer is LOCKED, this is handled as a separate
gated Canon-amendment + migration WP (`WP-CB-MIG2`), not an inline edit. The UI is built to render
these fields via the shared `prov_value`/topic macros; until the migration lands they display as
"מוצע/proposed" and light up automatically afterward.

## 7. Disposition

- Indexed into the docs SSoT: `documentation/09-design-system/` (design templates for the crop-book surface).
- Embedded into `LOD400_spec.md §10`; LOD400 locked to v1.0.0 → eligible for L-GATE_S.
- team_35 role for this WP closes on §10 embed + team_00 approval; build dispatched to the build slice.

*Intake by team_100 (Chief Architect) · 2026-05-31 · cross-engine build/validation per IR#1/#5 to follow.*
