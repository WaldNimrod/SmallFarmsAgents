---
id: VERDICT_WP-UI_L-GATE_V_R3_v1.0.0
from: team_190
to: team_100
date: 2026-05-27
local_date_idt: 2026-05-28
type: L_GATE_V_VERDICT
gate: L-GATE_V
wp: SFA-S003-P002-WP-UI
project: smallfarmsagents
round: R3
correction_cycle: post-RE-BUILD
phase_owner: team_190
validator_engine: GPT-5.5
reviewed_commit: e7e8bb7
evidence_commit: c898c0a
build_branch: claude/sfa-ui-build-v2
production_url: https://sfa.nimrod.bio/
verdict: PASS_WITH_FINDINGS
---

# L-GATE_V Verdict — WP-UI R3

## 0. Verdict Box

**Verdict: PASS_WITH_FINDINGS.**

Validator engine: **GPT-5.5 (non-Claude)**. This satisfies Iron Rule #1 because the RE-BUILD builders and orchestrator are Claude-family engines.

No BLOCKER finding was identified. The rebuild materially closes the revoked R2 visual-fidelity failure: the live site now emits the main COMPONENTS.md BEM shell/card/market/community contracts, passes independent Playwright responsive checks, renders the unknown-field fallback, and passes AOS validation with **0 FAIL**.

This is not a clean PASS because the live DOM does not satisfy every literal visual-fidelity grep in BUILD_REPORT v2.0.0 §4.2 on the mandated sample URLs. The missing hooks are scoped and remediable; they do not recreate the prior "mostly dead CSS" failure.

## 1. Summary

Validated inputs were read in the mandated order: RE-BUILD mandate, LOD400 v1.0.3 §0.5, BUILD_REPORT v2.0.0, SCREENSHOTS_REPORT v1.0.0, and COMPONENTS.md. LOD400 §0.5 is accepted as binding: COMPONENTS.md canonical class names override colloquial mandate stubs.

Branch state note: `claude/sfa-ui-build-v2` currently points at `c898c0a`, one commit after reviewed implementation commit `e7e8bb7`. `c898c0a` adds only `visual_diff/*` evidence artifacts, so implementation validation remains against `e7e8bb7`; screenshot/Lighthouse evidence is cited from `c898c0a`.

Independent production checks confirmed:

- 14/14 key HTML routes return 200.
- Main BEM contracts are present on hub, about, calc, crop-book, variety, market list, market product, and community routes.
- AC-R-1, AC-R-2, and AC-R-3 pass via Playwright true viewport emulation.
- Lighthouse mobile evidence reports target-size score `1` with 0 failing items.
- AC-DB-1 passes on `/crop-book/anise-hyssop/variety/variety-1` with `variety-fields__extras` rendered and 8 extra fields.
- `book_variety.php` contains an 11-entry known-label dictionary, reserved-key exclusion, scalar / flat-array / nested JSON handling, array-of-objects skip, and the `is_internal_farm_use_only` knowledge-note filter.
- PHP lint passes on all 31 PHP files present in the build worktree under `sfa_delivery/`.
- `validate_aos.sh` returns **29 PASS / 17 SKIP / 0 FAIL**.

## 2. Parameters

| Field | Value |
|---|---|
| Validator | team_190 |
| Validator engine | GPT-5.5, non-Claude |
| Gate | L-GATE_V R3, post-RE-BUILD |
| WP | SFA-S003-P002-WP-UI |
| Reviewed implementation commit | `e7e8bb7` |
| Evidence-only commit observed | `c898c0a` (`visual_diff/*` only) |
| Branch | `claude/sfa-ui-build-v2` |
| Production URL | `https://sfa.nimrod.bio/` |
| Binding class-name rule | LOD400 v1.0.3 §0.5, COMPONENTS.md canonical names |

## 3. Criteria Table

| Cluster | Count | Result | Evidence |
|---|---:|---|---|
| Inherited v1.0.2 ACs | 38 | PASS_WITH_NOTES | Health API 200 JSON; bad ingest auth returns app-level 401 with browser UA; community `<main>` has 0 forms; PHP lint clean on located delivery PHP; AOS 0 FAIL. |
| Visual fidelity ACs | 14 | PASS_WITH_FINDINGS | 11/14 mandated route checks clean by literal live DOM count. 3 route checks have conditional or unwired hooks absent; see F-190-R3-01 and F-190-R3-02. |
| Responsive ACs | 4 | PASS | Independent Playwright viewport emulation: 390px `.gj-shell` visible and `.dt-shell` display none; 1280px inverse; 14/14 routes have 0 horizontal overflow; Lighthouse target-size has score 1 and 0 failing items. |
| DB-resilience AC | 1 | PASS | `variety-fields__extras` rendered on live variety URL; source logic handles unknown fields defensively and filters internal knowledge notes. |
| Constitutional checks | 5 | PASS | Cross-engine satisfied; `_aos/` not modified by this validator; roadmap not mutated; branch evidence understood; AOS 0 FAIL. |

## 4. Findings

| ID | Severity | Finding | evidence-by-path | route_recommendation | must_resolve_before |
|---|---|---|---|---|---|
| F-190-R3-01 | MAJOR | Global search page does not render `search-section` on live HTML even for known Hebrew queries whose `/api/v1/search` payload returns crop/product hits. This fails the literal V-3 visual-fidelity class check and suggests the HTML controller is degrading to empty results while the API route works. | `https://sfa.nimrod.bio/search?q=<known-hebrew-query>` has `search-section` count 0 and empty-state markup; `https://sfa.nimrod.bio/api/v1/search?q=<same-query>` returns non-empty `crops` and `products`; source: `sfa_delivery/app/Controllers/HubController.php` only populates page results when `$this->pdo !== null`. | Route to team_100 / WP-UI patch: wire the global search HTML route to the same data path as the search API, or update the AC to explicitly accept the empty-state route and validate `search-page__empty` instead of `search-section`. | LOD500_LOCKED clean closure |
| F-190-R3-02 | MINOR | Two BUILD_REPORT §4.2 sample hooks are absent on mandated live sample URLs because they are data-conditional: `/crop-book/anise-hyssop` lacks `cb-crop-hero__lede` when `description_md` is empty, and `/market/prd017` lacks `gj-pricehist` when `price_history_30d` is empty. The source templates and CSS contain those hooks, but the live sample URLs do not prove them. | `https://sfa.nimrod.bio/crop-book/anise-hyssop` has `cb-crop-hero__lede` count 0; `https://sfa.nimrod.bio/api/v1/crops/anise-hyssop` has empty `description_md`. `https://sfa.nimrod.bio/market/prd017` has `gj-pricehist` count 0; `https://sfa.nimrod.bio/api/v1/products/prd017` has empty `price_history_30d`. Source hooks exist in `sfa_delivery/templates/pages/book_crop.php`, `sfa_delivery/templates/pages/market_product.php`, `sfa_delivery/public_assets/css/crop-book-deep.css`, and `sfa_delivery/public_assets/css/gj.css`. | Route to team_100: make these visual ACs deterministic by selecting populated fixtures, seeding representative data, or rendering stable placeholder sections with the BEM hooks. | Clean PASS only |
| F-190-R3-03 | INFO | The branch HEAD mismatch is evidence-only: `c898c0a` is one commit after `e7e8bb7` and adds only screenshots, Lighthouse JSON/HTML, `results.json`, and `capture.py`. | `git show --name-status c898c0a` lists only `visual_diff/*` additions. | No remediation required; keep `reviewed_commit=e7e8bb7` and cite `evidence_commit=c898c0a` separately. | false |
| F-190-R3-04 | INFO | A bad-HMAC POST can return a Cloudflare-style 403 with a sparse scripted user agent, but returns the expected app-level 401 with a browser-like user agent. This is not classified as an HmacAuthMiddleware regression. | `POST /api/v1/ingest` with browser-like UA and malformed/missing auth returns 401 JSON `unauthorized`; sparse validator UA initially returned 403 `error code: 1010`. | No code remediation required for this WP; future automated validators should use a browser-like UA for WAF-fronted endpoints. | false |

## 5. validate_aos.sh

Command:

```bash
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
```

Result:

```text
RESULT: 29 PASS / 17 SKIP / 0 FAIL
L-GATE_BUILD EXIT CRITERION: SATISFIED
```

The validation run was executed from the build worktree at `.claude/worktrees/sfa-ui-build-v2`.

## 6. Disposition

Disposition is **PASS_WITH_FINDINGS**.

The rebuild is constitutionally acceptable to continue remediation from a narrow patch path. It should not be recorded as a clean L-GATE_V PASS until F-190-R3-01 is addressed or the visual AC is explicitly narrowed by team_100/team_00. F-190-R3-02 should be resolved before claiming a clean visual-fidelity PASS, but it is data/evidence determinism rather than a demonstrated template failure.

No BLOCKER finding was found, and there is no evidence that the previous R2 revoked condition (large-scale dead CSS due invented class names) persists.

## 7. Next Step

team_100 should issue a targeted WP-UI patch or AC clarification for F-190-R3-01 and F-190-R3-02, then request R4 re-verification focused on:

1. `/search` live result sections using a deterministic known-hit query.
2. Crop detail lede and market price history evidence using deterministic populated fixtures or stable placeholder BEM hooks.
3. A quick re-run of AC-R-1 through AC-R-3 and `validate_aos.sh` to guard against regression.
