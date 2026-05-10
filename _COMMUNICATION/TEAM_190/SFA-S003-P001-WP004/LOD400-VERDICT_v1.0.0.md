---
id: SFA-S003-P001-WP004-LOD400-VERDICT
type: L-GATE_SPEC verdict
validator: team_190
date: 2026-05-10
wp: SFA-S003-P001-WP004
verdict: BLOCKED
---

# L-GATE_SPEC Verdict — SFA-S003-P001-WP004 — Team 190

**Date:** 2026-05-10
**Author:** team_190
**Gate:** L-GATE_SPEC
**WP:** SFA-S003-P001-WP004
**Round:** 1
**Commit reviewed:** b9baf75

## §0 Summary

BLOCKED. WP004 is directionally sound and the public WordPress architecture is appropriate, but the current LOD400 is not yet safe to hand to the builder. Two contradictions would produce ambiguous or impossible implementation work: the entity-registry source path points to a file that is not present in the reviewed tree and is not created by WP004, and the SPA timeline rule contradicts the locked Flask SSoT while claiming parity with it. A third non-blocking but required clarification is needed around the shortcode data-URL substitution failure path and test coverage.

## §1 Constitutional Checks C1-C12

| Check | Result | Finding if any |
|---|---|---|
| C1 Directory authority | PASS_WITH_FINDING | WP004 mostly respects builder boundaries, but the spec references `organic_market_agent/crop_book/static/entity_registry.js` as an input while AC-16 treats `crop_book/static/{crop_book.css,crop_book.js,entity_registry.js}` as LOD500_LOCKED. The reviewed commit has no tracked `entity_registry.js` at any path, so the source/deliverable boundary is not buildable as written. See F-190-WP004-01. |
| C2 Iron Rule #1 cross-engine | PASS | Builder is `sfa_build` / Claude; validator is team_190 / non-Claude. |
| C3 Iron Rule #4 single roadmap writer | PASS_WITH_FINDING | No builder AC directs roadmap edits, but `_aos/roadmap.yaml` still has WP004 `current_lean_gate: L-GATE_E` and `lod_status: LOD400_DRAFT` while the bundle invokes L-GATE_SPEC. Team 100 should repair gate-state drift after this verdict. |
| C4 Iron Rule #7 ADR034 | PASS | WP004 product DB access is read-only SELECT. WordPress option writes are outside AOS hub structured-state mutation. |
| C5 Iron Rule #8 port canon | PASS | No new long-running listener; CLI publish and WordPress PHP shortcode reuse existing processes and HTTPS port 443. |
| C6 Scope isolation | BLOCKED | Scope isolation cannot be verified until the entity-registry path is canonicalized and the spec states whether WP004 reads an existing locked asset, creates a new copied asset, or embeds registry data directly. |
| C7 ACs are testable | PASS_WITH_FINDING | Most ACs are named and testable. Missing explicit AC coverage for entity-registry source existence/path and for shortcode substitution-miss behavior. |
| C8 S002 + Phase-1 regression risk | PASS | AC-15 protects market upload behavior; AC-16 bars Phase 1 locked-file edits. |
| C9 validate_aos.sh mandate | PASS | AC-14 requires 0 FAIL. Independent run at review time returned 29 PASS / 17 SKIP / 0 FAIL. |
| C10 No half-finished implementations | PASS | Out-of-scope list and LOD500 DoD are concrete. |
| C11 Filter parity correctness | BLOCKED | Search/category/season/DTM parity is mostly specified, but timeline parity is internally contradictory: §8.3 says to use max harvest window across all varieties while also saying to match `views.py:197`; the locked Flask view computes from the selected default variety. See F-190-WP004-02. |
| C12 Manual mu-plugin install acknowledged | PASS | §7 and §10 make the one-time uPress File Manager install explicit and cite the existing `sfagent-allow-json.php` precedent. |

## §2 Additional Findings

### F-190-WP004-01 — BLOCKER — Entity registry source path is absent and not in WP004 deliverables

**Evidence:** WP004 LOD400 §4 states that the publisher reads `organic_market_agent/crop_book/static/entity_registry.js`. The manifest repeats that reference. At reviewed commit `b9baf75`, `git ls-tree -r --name-only HEAD -- 'organic_market_agent/*static*' 'organic_market_agent/crop_book' 'tests/crop_book'` shows no tracked `entity_registry.js` anywhere. The WP004 file-level deliverables create `organic_market_agent/crop_book/publisher/static/sfagent-crop-book.js`, but do not create or copy `entity_registry.js`. AC-16 also treats `crop_book/static/{crop_book.css,crop_book.js,entity_registry.js}` as locked, which prevents the builder from creating/fixing that path without violating the spec.

**Impact:** The builder cannot implement the mandated publisher as written because its required registry input does not exist and the spec does not authorize creating it. The entity-registry parser and tests cannot be made reliable without a canonical source path.

**Required remediation:** Choose one canonical source and make the file contract explicit. Acceptable fixes include: point WP004 to the actual tracked WP003 asset path if that asset is restored; add a WP004 deliverable that copies the registry into a publisher-owned path; or replace file extraction with a Python-owned JSON fixture. Then add an AC that asserts the canonical source exists and that a known entity is parsed.

### F-190-WP004-02 — BLOCKER — Timeline rule contradicts the locked Flask SSoT

**Evidence:** WP004 §8.3 says: `weeks = Math.ceil(hwMax / 7)` where `hwMax = max(v.harvest_window_max_days for v in crop.varieties ...)`, then says "Match `views.py:197` exactly." The locked WP003 view computes `total_weeks` from the default variety's `harvest_window_max_days`, not from the maximum across all varieties. WP004 AC-08 also says the asserted fixture is for the default variety.

**Impact:** The builder is given two incompatible instructions for the public timeline. Using max-across-varieties will diverge from the declared SSoT; using default-variety parity will diverge from §8.3. This is exactly the kind of ambiguity L-GATE_SPEC must catch before implementation.

**Required remediation:** Pick the intended public rule and make every reference consistent. If parity with WP003 is required, define timeline weeks from the selected default variety and update §8.3. If public WordPress intentionally uses crop-wide max, remove the "match views.py" claim and update AC-08 plus the parity expectations.

## §3 WP004-Specific Findings

### F-190-WP004-03 — MAJOR — Data-URL substitution miss is mitigated in risk text but not specified as an AC

**Evidence:** §5.3 uses PHP `str_replace` against the exact literal `window.CROP_BOOK_DATA_URL = "./sfagent-crop-book-data.json"`. R-WP004-06 correctly identifies this as fragile and says PHP should log and return a placeholder if substitution fails, but §7 shortcode logic only says "Apply the data-URL substitution" and AC-11 only checks static PHP syntax/grep for shortcode registration, option registration, and `wp_remote_get`.

**Impact:** A builder can satisfy AC-11 while shipping a shortcode that silently returns body HTML with the relative local-preview data URL still present. On WordPress, that can produce a broken SPA fetch path without a clear server-side failure.

**Required remediation:** Add explicit shortcode behavior and test coverage: if the sentinel is absent or replacement count is zero, `error_log` a clear message and return the placeholder. Add a static or unit-style test that confirms the sentinel check exists, and add a publisher-side test that the rendered body contains the sentinel before upload.

### F-190-WP004-04 — MINOR — Roadmap gate-state drift should be corrected by Team 100

**Evidence:** `_aos/roadmap.yaml` has WP004 registered with `status: ELIGIBLE`, `current_lean_gate: L-GATE_E`, and `lod_status: LOD400_DRAFT`, while the bundle and LOD400 invoke L-GATE_SPEC Round 1. The notes say "Awaiting team_190 L-GATE_S Round 1."

**Impact:** This does not block the content review, but it creates confusing gate telemetry for downstream agents.

**Required remediation:** Team 100 should update the roadmap through the authorized path after processing this verdict so the current gate and LOD status reflect the real review state.

## §4 Recommendation

BLOCKED. Builder must NOT proceed until Team 100 revises WP004 LOD400 to resolve F-190-WP004-01 and F-190-WP004-02. F-190-WP004-03 should be fixed in the same revision because it is a small spec/test addition in a high-risk WordPress runtime path. After revision, re-submit L-GATE_SPEC Round 2 to team_190.

