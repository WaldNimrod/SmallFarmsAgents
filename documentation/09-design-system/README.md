# 09 — Design System

> Canonical design templates for the SFA public delivery tier (`sfa.nimrod.bio`).
> The design SSoT is the **team_35 LOD300 handoff**; this folder points to it (does not duplicate it).

## Current design contract — Crop Book v1 (calculator-driven)

**Source of truth:** `_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-1/HANDOFF_PACKAGE/`
(byte-for-byte handoff archive from team_35; see its `HANDOFF_PACKAGE_v1.0.0.md` manifest).

| Artifact | Path | Role |
|----------|------|------|
| Visual source of truth | `…/HANDOFF_PACKAGE/design/LOD300 Crop Book v1.html` | Pannable spec board — every screen + state + annotation. Open in a browser; compare pixel-for-pixel during build. |
| Design tokens | `…/HANDOFF_PACKAGE/design/tokens.css` | `--gj-*` palette (v2 white-green), type, spacing, radii, shadows. Ported verbatim into `sfa_delivery/public_assets/css/tokens.css`. |
| Component styles | `…/HANDOFF_PACKAGE/design/cropbook-v1.css` | Visual contract for `.cb-/.cv-/.af-` components. |
| Behavior | `…/HANDOFF_PACKAGE/design/cropbook-v1.js` | Vanilla ES5 `CALC[kind]` formulas + interactions; JS mirror must stay in parity with `organic_market_agent/crop_book/calculators.py`. |
| Tokens delta | `…/HANDOFF_PACKAGE/spec/DESIGN_TOKENS-delta.md` | Palette v2 + confidence/assumption tokens over the prior kit. |
| Components delta | `…/HANDOFF_PACKAGE/spec/COMPONENTS-delta.md` | 11 new component contracts (AssumptionField, CalcPanel, prov cues, depth tabs, …) + extensions. |
| Templates delta | `…/HANDOFF_PACKAGE/spec/TEMPLATES-delta.md` | Route map + macro contracts + page composition. |
| Open issues | `…/HANDOFF_PACKAGE/spec/OPEN_ISSUES.md` | 8 resolved decisions (binding) + 7 proposed schema fields (→ WP-CB-MIG2). |

## How this maps to the build

- **Spec embedding:** the LOD300 is embedded into `_aos/work_packages/S003/SFA-S003-P004-WP-CB-1/LOD400_spec.md §10`.
- **Field binding:** every design field key is bound to the migrated data model in
  `_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-1/FIELD_INTERFACE_MAP_v1.0.0.md` — no raw DB key is rendered to users.
- **Delivery target:** `sfa_delivery/` (Slim4/PHP on uPress). Tokens → `public_assets/css/`, components → `templates/macros/`,
  behavior → `public_assets/js/`, crop masters → `public_assets/img/crops/` (web-optimized; the masters above stay canonical).

## Brand anchors (locked)

AOS Design System v3.4 (`--gj-*` worlds: leaf/sun/tomato/soil/code) · RTL Hebrew · Assistant (body) /
Frank Ruhl Libre (headings) / JetBrains Mono (technical LTR) / Carmela (wordmark+hero, licensed self-host) ·
Devora watercolor crop masters (`mix-blend-mode: multiply` on near-white).

---

*Indexed by team_100, 2026-05-31. Keep this folder a pointer to the handoff SSoT — do not fork the design files here.*
