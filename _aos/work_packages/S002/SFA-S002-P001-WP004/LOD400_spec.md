# LOD400 — SFA-S002-P001-WP004 — Mobile UI Parity

**Date:** 2026-05-07
**Author:** team_100
**WP:** SFA-S002-P001-WP004
**Type:** LOD400_SPEC
**Status:** READY for L-GATE_S
**Builder:** sfa_build (Sonnet, Team 10)
**QA:** Team 50 (Haiku)
**Validator:** external

---

## 1. Goal

Ensure the public price-index page (`[sfagent_market_report]` shortcode rendering [`public_report_body.html`](../../../../organic_market_agent/publisher/templates/public_report_body.html) + [`sfagent-base.css`](../../../../organic_market_agent/publisher/static/sfagent-base.css)) is **accurate, legible and usable on mobile devices** as a launch precondition. RTL Hebrew rendering preserved across all viewports.

---

## 2. Scope (files in play)

| Path | Role |
|------|------|
| `organic_market_agent/publisher/templates/public_report.html` | Full-page wrapper |
| `organic_market_agent/publisher/templates/public_report_body.html` | Body fragment loaded by `[sfagent_market_report]` |
| `organic_market_agent/publisher/static/sfagent-base.css` | Theme CSS |
| `scripts/wp_shortcode_install.py` | WP shortcode registration (reference only — no change) |

Out of scope: WP server-side PHP, WP theme files, FTPS pipeline.

---

## 3. Acceptance Criteria

### AC-01 — Viewport correctness (3 breakpoints minimum)
- 375 px (iPhone SE / older Android): no horizontal scroll, no overflow, table readable (font ≥ 14 px effective).
- 414 px (iPhone Pro / typical Android): same, plus product images (if any) intact.
- 768 px (tablet portrait): preserves desktop columns or graceful collapse with priority columns visible.

### AC-02 — RTL Hebrew preserved
- `dir="rtl"` and `lang="he"` set on `<html>` or wrapper.
- Numbers/currency rendered LTR within RTL flow per [`docs/RTL_DEVELOPMENT_GUIDE.md`](../../../../docs/RTL_DEVELOPMENT_GUIDE.md).
- No clipped Hebrew glyphs at any of AC-01 viewports.

### AC-03 — Filter/source-type bar (post-WP002 stash apply)
- Source-type filter buttons (`הכל / 🌱 מגדלים / 🏪 חנויות / 🏬 רשתות`) wrap-friendly, target-size ≥ 44 px (iOS HIG / WCAG 2.5.5).
- Active state visible (color + weight) without hover.

### AC-04 — Data table readable
- Product rows: name + price visible without truncation at 375 px (allow ellipsis on secondary columns).
- Sticky header (if present) does not block first row.
- Tap on row reveals details (if collapsible) without page reload.

### AC-05 — Lighthouse mobile audit
- Lighthouse mobile **Performance ≥ 85**, **Accessibility ≥ 90**, **Best Practices ≥ 90**, **SEO ≥ 90**. Run against `https://www.nimrod.bio/SmallFarmsAgent` or local equivalent.
- Largest Contentful Paint ≤ 2.5 s on Slow 4G simulation.

### AC-06 — Cross-device smoke
- Real-device or BrowserStack-equivalent smoke on:
  - iOS Safari (latest)
  - Android Chrome (latest)
  - Mobile Firefox (best effort)
- Screenshots captured at each viewport, attached to the QA artifact.

### AC-07 — Stale banner + data-quality block visible on mobile
- `data_quality` transparency block ([`PUBLISH_CHECKLIST.md`](../../../../documentation/05-admin-and-operations/PUBLISH_CHECKLIST.md) §1) renders on mobile without overlap.
- Stale banner (if `staleness_level != fresh`) visible above fold at 375 px.

---

## 4. File-level deliverables

| Path | Action |
|------|--------|
| `organic_market_agent/publisher/static/sfagent-base.css` | UPDATE — responsive media queries; touch-target sizes; safe-area insets |
| `organic_market_agent/publisher/templates/public_report_body.html` | UPDATE — viewport meta, dir/lang attrs, accessible markup for filter bar |
| `organic_market_agent/publisher/templates/public_report.html` | UPDATE — same viewport meta if not already present |
| `tests/test_publisher_local.py` (or new `test_responsive_html.py`) | UPDATE / ADD — assertions on rendered HTML structure (viewport meta, dir attr, filter button accessible names) |
| `_COMMUNICATION/TEAM_50/reports/2026-05-XX_MOBILE_PARITY_QA_TEAM50.md` | CREATE — QA evidence: Lighthouse JSON + screenshots |

No DB schema changes. No migration. No collector changes.

---

## 5. Implementation notes

- Use CSS-only responsive design (no JS layout shifts). Breakpoints in `sfagent-base.css`.
- Touch targets: `min-height: 44px; min-width: 44px;` on interactive elements.
- Avoid `max-width: 100vw` traps with RTL — prefer `max-width: 100%` on containers.
- Hebrew column labels: avoid CSS `text-overflow: ellipsis` on RTL columns where ambiguity hurts comprehension; prefer wrap.
- Consider `font-size-adjust` or `clamp()` for fluid typography between 14–18 px.

---

## 6. Constraints

- **Shortcode interface stable:** no breaking changes to `[sfagent_market_report]` API. Builder must not modify [`scripts/wp_shortcode_install.py`](../../../../scripts/wp_shortcode_install.py).
- **uPress hosting:** cannot install custom WP plugins; everything must work via FTPS-uploaded HTML/CSS.
- **No external CDN dependencies.** Self-host any added font (or use `system-ui` stack).
- **Backwards compatibility:** existing desktop rendering must not regress.

---

## 7. Test plan

### Unit
- HTML structure assertions: viewport meta present, `dir="rtl"`, button `aria-label` set, filter buttons in `<nav>` or `role=tablist`.
- CSS lint (`stylelint`) passes.

### Integration
- Render fixture data through publisher; serve locally; run Lighthouse CLI: `lighthouse http://localhost:8080/public_report.html --emulated-form-factor=mobile --output=json`.
- Snapshot HTML at 375/414/768 with headless Playwright; image-diff vs golden.

### Manual smoke
- Open production URL on real iOS/Android; verify ACs.

---

## 8. Risks and mitigations

| Risk | Mitigation |
|------|-----------|
| WordPress theme injects competing CSS | Scope all rules with `.sfagent-` class prefix; use specificity over `!important` |
| Hebrew RTL + LTR numbers cause directional bugs | Use `<bdi>` for currency; test on real Hebrew strings, not lorem ipsum |
| WP002 filter UI not yet landed when WP004 starts | Build mobile CSS for both with-filter and without-filter HTML; mark stash-dependent assertions as "post-WP002" |

---

## 9. Inputs from upstream WPs

- **WP002 (MyPIPS):** Adds source-type filter UI to `public_report_body.html` via stash apply. WP004 must accommodate this UI in responsive design even before WP002 lands (build for both states).
- **WP001 (M10):** No direct inputs; M10 doesn't change publisher templates beyond minor.

---

## 10. References

- Program package: [`PROGRAM_PACKAGE_LOD200_v1.0.0.md`](../../../../_COMMUNICATION/TEAM_100/SFA-S002-P001/PROGRAM_PACKAGE_LOD200_v1.0.0.md)
- WP002 audit (filter UI source): [`AUDIT_WP002_MYPIPS.md`](../../../../_COMMUNICATION/TEAM_100/SFA-S002-P001/AUDIT_WP002_MYPIPS.md)
- RTL guide: [`docs/RTL_DEVELOPMENT_GUIDE.md`](../../../../docs/RTL_DEVELOPMENT_GUIDE.md)
- uPress hosting spec: [`docs/UPRESS_WORDPRESS_STANDARD_v2.md`](../../../../docs/UPRESS_WORDPRESS_STANDARD_v2.md)

---

*LOD400 ready for L-GATE_S verdict.*
