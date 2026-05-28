# L-GATE_V VERDICT — SFA-S003-P002-WP-UI — TEAM_190 — v1.0.0

**Date:** 2026-05-27  
**Author:** team_190  
**WP:** SFA-S003-P002-WP-UI  
**Type:** L-GATE_V verdict  
**Gate:** L-GATE_V  
**Round:** 1  
**Engine:** GPT-5.5 / Cursor (non-Claude)  

## 0. Verdict Box

**VERDICT:** PASS_WITH_FINDINGS  
**WP / Gate / Round:** SFA-S003-P002-WP-UI / L-GATE_V / Round 1  
**Disposition:** WP_UI_PATCH01_THEN_CLOSE  
**Next step:** Team 100 should close WP-UI as LOD500_LOCKED and immediately open WP-UI-patch01 for the two variety-route findings below.

## 1. Verdict Summary

The live system at `https://sfa.nimrod.bio/` satisfies the blocking L-GATE_V criteria: required CSS assets are live, all 14 HTML routes return 200, the core read APIs return 200, the `/crop-book/*` URL contract is preserved, `/book/*` is not deployed, community remains static, Lighthouse mobile exceeds AC-31, and `validate_aos.sh` returns 0 FAIL.

The gate should not return to BUILD because no blocking VC failed. However, Team 100's F-BUILD-04 is confirmed as a real MAJOR defect: Hebrew variety names collapse to the same `variety` slug, orphaning non-first varieties behind a single URL. F-BUILD-05 is also confirmed as a MINOR UX defect: the variety detail template prints JSON in a `<pre>` block. Both belong in WP-UI-patch01.

## 2. Parameters

| Field | Value |
|---|---|
| Validator | team_190 |
| Engine | GPT-5.5 / Cursor, non-Claude |
| Builder/remediator engines | Claude-family commits on `origin/claude/sfa-ui-build`; commit log includes `Co-Authored-By: Claude Opus 4.7` |
| Validation window | 2026-05-27, approximately 45 minutes |
| Mandate source | `origin/claude/gallant-elbakyan-727a60:_COMMUNICATION/TEAM_190/MANDATE_SFA-S003-P002-WP-UI_L-GATE_V_v1.0.0.md` |
| Build branch reviewed | `origin/claude/sfa-ui-build`, head `1fdd396` |
| Spec reviewed | `origin/claude/gallant-elbakyan-727a60:_aos/work_packages/S003/SFA-S003-P002-WP-UI/LOD400_spec.md` |
| Reports reviewed | `BUILD_REPORT_v1.0.1.md`, `BUILD_REPORT_v1.0.0.md`, `visual_diff/diff_notes.md` |
| Implementation files reviewed | `sfa_delivery/app/Controllers/CropBookViewController.php`, `sfa_delivery/templates/pages/book_variety.php`, `sfa_delivery/app/Middleware/HmacAuthMiddleware.php`, `sfa_delivery/app/Lib/Hmac.php` |
| Live URLs checked | `https://sfa.nimrod.bio/`, all 14 LOD400 HTML routes, read APIs, ingest bad-HMAC path, legacy `https://www.nimrod.bio/smallfarmsagent/` |
| Lighthouse | Independent mobile run on `/`: Performance 93, Accessibility 100, Best Practices 96, SEO 100 |

## 3. Criteria Table

| VC | Result | Evidence |
|---|---|---|
| VC-V-1 — LOD400 §3 file mapping | PASS | All seven CSS assets returned 200: `tokens.css`, `gj.css`, `hub.css`, `community.css`, `crop-book-deep.css`, `desktop.css`, `desktop-extras.css`. `/api/v1/modules` returned 200 and parsed as 8 modules. |
| VC-V-2 — 14 HTML routes | PASS_WITH_FINDINGS | All 14 routes returned 200: `/`, `/about`, `/search?q=`, `/calc`, `/crop-book/`, `/crop-book/questions`, `/crop-book/family`, `/crop-book/table`, `/crop-book/search?q=`, `/crop-book/anise-hyssop`, `/crop-book/anise-hyssop/variety/variety`, `/market/`, `/market/prd017`, `/community`. Spot checks confirmed table headers (`<th scope="col"` count 8), market price/disclaimer text, and static community page with 0 forms. Variety route has quality defects captured under LV-V-1/LV-V-2. |
| VC-V-3 — 8 API endpoints | PASS_WITH_LIMITATION | Independent curls returned 200 for `/api/v1/health`, `/api/v1/modules`, `/api/v1/search?q=`, `/api/v1/crops`, `/api/v1/crops/anise-hyssop`, `/api/v1/products`, `/api/v1/products/prd017`, `/api/v1/market/prd017/history?days=28`. Bad HMAC on `/api/v1/ingest` returned 401 `hmac mismatch`. Valid-HMAC 200 was not re-run to avoid production mutation without the deploy secret; BUILD_REPORT v1.0.1 records valid HMAC 200. |
| VC-V-4 — Lighthouse mobile AC-31 | PASS | Independent `npx lighthouse https://sfa.nimrod.bio/ --form-factor=mobile --throttling-method=simulate` returned Performance 93, Accessibility 100, Best Practices 96, SEO 100. |
| VC-V-5 — F-BUILD-04 disposition | PASS_WITH_FINDINGS | Confirmed as MAJOR, non-blocking for this gate, mandatory WP-UI-patch01. Code evidence: `sfa_delivery/app/Controllers/CropBookViewController.php:152-157`; live evidence: `/crop-book/anise-hyssop` exposes only `/crop-book/anise-hyssop/variety/variety` as the unique variety link. |
| VC-V-6 — F-BUILD-05 disposition | PASS_WITH_FINDINGS | Confirmed as MINOR, mandatory WP-UI-patch01. Code evidence: `sfa_delivery/templates/pages/book_variety.php:9`; live evidence: `/crop-book/anise-hyssop/variety/variety` contains a `<pre>` JSON payload block. |
| VC-V-7 — Architectural invariants | PASS | Migration inventory on `origin/claude/sfa-ui-build` contains only `001_schema_migrations.sql`, `002_crops.sql`, `003_products.sql`, and `migrate.php`; `community_contribution` path matches = 0. `/book/` and `/book/table` both return 404. Implementation branch is `sfa_delivery/` Slim/PHP/uPress, not Flask/gunicorn. |
| VC-V-8 — No live regression | PASS_WITH_LIMITATION | `/api/v1/health` returns `{status:"ok", php_version:"8.5.5", db:"ok"}`. Legacy `https://www.nimrod.bio/smallfarmsagent/` returns 404. BUILD_REPORT v1.0.1 records waldhomeserver cron success on 2026-05-26 06:30 with 65 products and 0 rejected; SSH tail was not re-run in this validator session. |
| VC-V-9 — Cross-engine + IR#4 | PASS | Build branch log includes Claude attribution on `1fdd396` and `4d1888f`; this validator is GPT-5.5/non-Claude. Build commits `4d1888f` and `1fdd396` contain 0 `_aos/` paths and 0 `_aos/roadmap.yaml` paths. |

## 4. Findings

### LV-V-1 — MAJOR — Hebrew variety slug collision orphans varieties

**Disposition:** Required WP-UI-patch01 remediation; not blocking WP-UI L-GATE_V close.

**Evidence by path:**

- `sfa_delivery/app/Controllers/CropBookViewController.php:152-157`:
  `slugify()` uses `preg_replace('/[^a-z0-9\s-]/', '', $slug)` and falls back to literal `variety`. This strips Hebrew letters.
- `sfa_delivery/app/Controllers/CropBookViewController.php:102` and `:128` use that slug for link generation and route matching.

**Live evidence:**

```text
variety_links: ['/crop-book/anise-hyssop/variety/variety', '/crop-book/anise-hyssop/variety/variety']
unique_variety_links: ['/crop-book/anise-hyssop/variety/variety']
```

**Impact:** Any crop with multiple Hebrew-named varieties exposes duplicate links to the same `variety` URL; non-first varieties are not independently reachable. This is a real URL-layer defect, but it is scoped to the variety detail subroute and does not break the main crop book, market, hub, API, or deployment architecture.

**Required remediation:** Use a deterministic URL key that does not collapse Hebrew text, such as `variety-{id}`, percent-encoded raw name, or a Unicode-aware slug with `\p{L}` and `/u`.

### LV-V-2 — MINOR — Variety detail renders raw JSON payload

**Disposition:** Required WP-UI-patch01 remediation; not blocking WP-UI L-GATE_V close.

**Evidence by path:**

- `sfa_delivery/templates/pages/book_variety.php:9` renders:
  `json_encode($variety, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT)` inside `<pre>`.

**Live evidence:**

```text
variety_has_pre: True
variety_contains_json_markers: True
```

**Impact:** The route is available and readable, but it does not meet the intended branded/field-labeled presentation quality for CB5-style variety details.

**Required remediation:** Render named fields with Hebrew labels and hide internal payload structure.

### Disposition of Team 100 Build Findings

| Build finding | Team 190 disposition |
|---|---|
| F-BUILD-04 — `slugify()` strips Hebrew | CONFIRMED as LV-V-1 MAJOR; WP-UI-patch01 required. |
| F-BUILD-05 — raw JSON variety detail | CONFIRMED as LV-V-2 MINOR; WP-UI-patch01 required. |

No BLOCKER findings.

## 5. validate_aos.sh

Command:

```bash
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
```

Result:

```text
RESULT: 29 PASS / 19 SKIP / 0 FAIL
L-GATE_BUILD EXIT CRITERION: SATISFIED
```

The mandate expected 29/17/0 from earlier branch evidence; current spoke main returns 29/19/0 due two additional spoke skips. The binding criterion is 0 FAIL, which is satisfied.

## 6. Disposition

**Disposition:** WP_UI_PATCH01_THEN_CLOSE.

Team 190 authorizes WP-UI to close without returning to BUILD because all blocking validation criteria pass and the only confirmed issues are isolated to the variety detail subroute. The two findings must become WP-UI-patch01 acceptance criteria before the patch is considered complete.

## 7. Next Step

Team 100: mark SFA-S003-P002-WP-UI COMPLETE / LOD500_LOCKED, then open WP-UI-patch01 for Hebrew-safe variety URLs and labeled variety-detail rendering.

