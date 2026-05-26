---
id: VERDICT_SFA-S003-P002-WP-UI_L-GATE_S_v1.0.0
from: team_190 (External Constitutional Validator)
to: team_100 (Chief System Architect)
date: 2026-05-27
type: CONSTITUTIONAL_VERDICT
wp: SFA-S003-P002-WP-UI
gate: L-GATE_S
round: 1
engine: GPT-5.5 / Cursor
engine_constraint: "non-Claude; distinct from assigned builder sfa_build (Claude Sonnet)"
verdict: FAIL
disposition: AMEND_LOD400_AND_RESUBMIT
---

# VERDICT — SFA-S003-P002-WP-UI — TEAM_190 — v1.0.0

**Date:** 2026-05-27
**Author:** team_190
**WP:** SFA-S003-P002-WP-UI
**Type:** CONSTITUTIONAL_VERDICT

## 1. Verdict Summary

**FAIL** — LOD400 v1.0.0 is not ready for BUILD dispatch.

The spec correctly identifies that the team_35 design must be adapted away from Flask/waldhomeserver and onto the Slim/PHP/uPress delivery tier, but it then changes two binding delivery-tier contracts without a matching team_00 decision: it replaces the frozen `/crop-book/*` public URL contract with `/book/*`, and it adds public community write endpoints/tables even though the canonical S003 delivery tier is read-only except for HMAC ingest. These are builder-facing architectural contradictions, not implementation details.

## 2. Parameters

| Field | Value |
|-------|-------|
| Validator | team_190 |
| Engine | GPT-5.5 / Cursor |
| Gate | L-GATE_S |
| Round | 1 |
| Timebox | Single-pass constitutional spec review |
| Primary target | `_aos/work_packages/S003/SFA-S003-P002-WP-UI/LOD400_spec.md` |
| Mandate | `_COMMUNICATION/TEAM_190/MANDATE_SFA-S003-P002-WP-UI_L-GATE_S_v1.0.0.md` |

Files actually read:

- `_aos/governance/team_190.md`
- `_aos/context/PROJECT_CONTEXT.md`
- `_aos/context/ACTIVATION_VALIDATOR.md`
- `_aos/roadmap.yaml`
- `_COMMUNICATION/TEAM_190/MANDATE_SFA-S003-P002-WP-UI_L-GATE_S_v1.0.0.md`
- `_aos/work_packages/S003/SFA-S003-P002-WP-UI/LOD400_spec.md`
- `_COMMUNICATION/team_00/DECISION_SFA-S003-P003_DEDICATED_SFA_SUBDOMAIN_2026-05-23_v1.0.0.md`
- `documentation/02-architecture/sfa-delivery-tier.md`
- `documentation/03-data-and-schema/sfa-mysql-mirror.md`
- `_COMMUNICATION/team_35/SFA-S003-P002-WP-UI/_handoff/README.md`
- `_COMMUNICATION/team_35/SFA-S003-P002-WP-UI/_handoff/HANDOFF_LOD300.md`
- `_COMMUNICATION/team_35/SFA-S003-P002-WP-UI/_handoff/IMPLEMENTATION_PLAN.md`
- `_COMMUNICATION/team_35/SFA-S003-P002-WP-UI/_handoff/DESIGN_TOKENS.md`
- `_COMMUNICATION/team_35/SFA-S003-P002-WP-UI/_handoff/COMPONENTS.md`
- `_COMMUNICATION/team_35/SFA-S003-P002-WP-UI/_handoff/TEMPLATES.md`
- `_COMMUNICATION/team_35/SFA-S003-P002-WP-UI/_handoff/MODULES_REGISTRY.yaml`

Mechanical checks:

- `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` → **29 PASS / 17 SKIP / 0 FAIL**
- `scripts/lint_constitutional_package.py` → not run; script is absent from this repo/worktree and not found under `/Users/nimrod`.

## 3. Criteria Table

| VC | Result | Rationale |
|----|--------|-----------|
| VC-1 Architectural consistency | **FAIL** | LOD400 honors Slim/PHP/uPress in broad stack terms, but violates binding URL and write-surface contracts in the parent delivery-tier docs. |
| VC-2 AC completeness | **FAIL** | The 22 ACs do not independently cover all page templates or all new endpoints listed in §4. |
| VC-3 Risk register adequacy | **PASS_WITH_FINDINGS** | The register covers several material risks, but misses/under-specifies NAT rate-limit collisions and PHP/uPress compatibility checks. |
| VC-4 GCR analysis correctness | **FAIL** | "No GCR needed" is incorrect because LOD400 changes the canonical schema surface and public write model without updating the binding schema/architecture docs. |
| VC-5 Test plan adequacy | **PASS_WITH_FINDINGS** | Test categories are directionally right, but DB mode for phpunit and visual/Lighthouse ownership are not specified tightly enough for dispatch. |
| VC-6 Out-of-scope discipline | **PASS_WITH_FINDINGS** | Most deferrals are plausible, but the contribution workflow is not a harmless UI deferral because the backend write path itself conflicts with S003 constraints. |
| VC-7 Phase plan realism | **PASS_WITH_FINDINGS** | The phase sequence is coherent, but B.8's 1h for 28 screenshots, Lighthouse, and report is not credible. |

## 4. Findings

### LV-S-1 — BLOCKER — VC-1 / VC-4

**Summary:** LOD400 introduces public community writes in S003, contradicting the binding delivery-tier architecture and schema docs.

**Detail:** LOD400 adds `community_contributions`, `POST /api/v1/community/contribute`, and a public community feed/write surface:

- `_aos/work_packages/S003/SFA-S003-P002-WP-UI/LOD400_spec.md:124-127` defines `CommunityController`, `SearchController`, and `ModulesController`.
- `_aos/work_packages/S003/SFA-S003-P002-WP-UI/LOD400_spec.md:133-153` defines new migration `004_community.sql`.
- `_aos/work_packages/S003/SFA-S003-P002-WP-UI/LOD400_spec.md:189-190` defines `/api/v1/community/feed` and `/api/v1/community/contribute`.
- `_aos/work_packages/S003/SFA-S003-P002-WP-UI/LOD400_spec.md:222-224` makes public contribution submission an acceptance criterion.

That conflicts with the binding architecture:

- `documentation/02-architecture/sfa-delivery-tier.md:56-64` says the delivery tier has no canonical writes and is a read mirror.
- `documentation/02-architecture/sfa-delivery-tier.md:195-205` says S003 has no user write paths and no PII in MySQL.
- `documentation/02-architecture/sfa-delivery-tier.md:209-220` forbids public write endpoints without HMAC or JWT.
- `documentation/03-data-and-schema/sfa-mysql-mirror.md:21-32` freezes the table inventory at 4 data + 2 plumbing tables.
- `documentation/03-data-and-schema/sfa-mysql-mirror.md:359-365` explicitly defers comments/community tables to S004.

The parent decision allows S004 to add calculator/community later, but it does not authorize S003 to add authless public write endpoints on the delivery tier. A builder cannot safely implement this without either violating the canonical docs or silently changing the architecture.

**must_resolve_before:** BUILD_DISPATCH

**Required remediation:** Remove `community_contributions` and public contribution writes from WP-UI LOD400, or obtain/update a team_00 decision plus canonical architecture/schema docs that explicitly authorize S003 public writes, PII/contact handling, and the delivery-tier DB table expansion.

### LV-S-2 — BLOCKER — VC-1 / VC-4

**Summary:** LOD400 changes the frozen public URL contract from `/crop-book/*` to `/book/*` without a new decision artifact.

**Detail:** LOD400 states `/crop-book/` becomes `/book/` and old paths 301:

- `_aos/work_packages/S003/SFA-S003-P002-WP-UI/LOD400_spec.md:157-202` defines `/book/*` as the new binding route tree and redirects `/crop-book/*`.
- `_aos/work_packages/S003/SFA-S003-P002-WP-UI/LOD400_spec.md:204` states the URL change explicitly.

The binding architecture freezes the public URL contract at `/crop-book/` and `/crop-book/{slug}`:

- `_COMMUNICATION/team_00/DECISION_SFA-S003-P003_DEDICATED_SFA_SUBDOMAIN_2026-05-23_v1.0.0.md:42-46` names `/crop-book/` as the user route.
- `documentation/02-architecture/sfa-delivery-tier.md:174-191` freezes `/crop-book/` and says changes require a new DECISION artifact.

The team_35 design route map is contextual design input, not authority to override a frozen architecture contract. LOD400 can preserve the design intent while keeping canonical `/crop-book/*` routes, or it must route a decision update through team_00.

**must_resolve_before:** BUILD_DISPATCH

**Required remediation:** Keep `/crop-book/*` as canonical and optionally add `/book/*` aliases only if explicitly allowed, or file/record a team_00 decision amending the frozen public URL contract.

### LV-S-3 — MAJOR — VC-2 / VC-5

**Summary:** Acceptance criteria do not cover every page template and endpoint introduced by the spec.

**Detail:** LOD400 lists 14 page templates and multiple new endpoints:

- `_aos/work_packages/S003/SFA-S003-P002-WP-UI/LOD400_spec.md:93-107` lists the page templates.
- `_aos/work_packages/S003/SFA-S003-P002-WP-UI/LOD400_spec.md:179-193` lists the API routes.

The AC table covers several important routes, but there is no direct AC for `/about`, `/book/questions`, `/book/family`, `/book/table`, `/book/search`, `/book/{slug}/variety/{vslug}`, `/market/{slug}`, `/community`, `/search`, `/api/v1/community/feed`, or `/api/v1/market/{slug}/history`. AC-16 is broad RTL/manual coverage, not page-functional coverage.

**must_resolve_before:** BUILD_DISPATCH

**Required remediation:** Add explicit AC rows or a route-by-route matrix that maps each template and new endpoint to a verification command/screenshot/API assertion. At minimum, every route introduced in §3.3/§4 needs one concrete pass/fail check.

### LV-S-4 — MAJOR — VC-3 / VC-5

**Summary:** Risk/test planning is not tight enough around the delivery-tier environment.

**Detail:** The risk register covers CSS order, Cloudflare stale redirects, `.htaccess` partial-honor debt, spam, and LCP:

- `_aos/work_packages/S003/SFA-S003-P002-WP-UI/LOD400_spec.md:267-280`

However, it omits or under-specifies:

- Shared-IP/NAT false positives for the `max 3 per IP per hour` contribution rate limit in AC-12.
- PHP/uPress compatibility criteria, despite the build relying on PHP-FPM/Slim/PDO on a managed shared host.
- The phpunit DB mode and fixture strategy: `sqlite` vs test MySQL vs mocked PDO is not declared.
- Visual diff ownership and thresholds are split across BUILD and L-GATE_V without enough detail for reproducibility.

These do not independently force FAIL, but they must be corrected if LOD400 is amended for the blocking findings.

**must_resolve_before:** BUILD_DISPATCH

**Required remediation:** Add a small environment/test subsection specifying PHP version target, test DB backend/fixtures, visual diff owner, and tolerance. If community writes remain after a decision update, add NAT-aware rate-limit risk and expected behavior.

### LV-S-5 — MINOR — VC-7

**Summary:** The final validation phase budget is not credible.

**Detail:** B.8 budgets 1 hour for "screenshots × 14 routes × 2 viewports = 28", Lighthouse, commit, BUILD_REPORT, and handoff:

- `_aos/work_packages/S003/SFA-S003-P002-WP-UI/LOD400_spec.md:323-325`

That is under-budgeted for a visual-heavy Hebrew RTL UI and risks turning L-GATE_B into a rushed checklist rather than a reproducible build report.

**must_resolve_before:** BUILD_DISPATCH

**Required remediation:** Increase B.8 or split browser evidence collection into a separate phase with explicit artifact paths.

## 5. validate_aos.sh

`validate_aos.sh` was run from the mandate branch worktree:

```text
RESULT: 29 PASS / 17 SKIP / 0 FAIL
```

For L-GATE_S, this is a hygiene signal only. The constitutional result above is based on spec completeness and consistency with binding architecture.

## 6. Disposition

**AMEND_LOD400_AND_RESUBMIT.**

Do not dispatch BUILD for `SFA-S003-P002-WP-UI` on this LOD400 version. The required changes are architectural-contract fixes, not builder discretion.

## 7. Next Step

team_100 should amend LOD400 to reconcile public write scope and URL contract with the binding delivery-tier docs, then resubmit `SFA-S003-P002-WP-UI` for L-GATE_S Round 2.
