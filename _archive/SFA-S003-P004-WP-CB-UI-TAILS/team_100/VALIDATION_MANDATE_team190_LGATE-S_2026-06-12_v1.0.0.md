# VALIDATION MANDATE + PROMPT — SFA-S003-P004-WP-CB-UI-TAILS (L-GATE_S) — team_100 → team_190 — v1.0.0

**Date:** 2026-06-12
**From:** team_100 (Chief System Architect, Claude Opus — build session)
**To:** team_190 (Independent Validator)
**Routed by:** team_00
**Repo:** `/Users/nimrod/Documents/SmallFarmsAgents`
**Gate:** **L-GATE_S** (spec review) of WP-CB-UI-TAILS — three delivery-tier UI tails. **Pre-build** — review the LOD400 SPEC for soundness, precision, root-cause correctness, and constitutional/scope compliance. **No build exists yet** (except the item-1 price-chip head-start, below) — this is a SPEC review; do not build or run live-DB mutations.

**Refs:**
- **Spec under review (as corrected — see SPEC §8):** `_COMMUNICATION/TEAM_100/SFA-S003-P004-WP-CB-UI-TAILS/SPEC_2026-06-12_v1.0.0.md` on branch `docs/cb-handoff-specs` (pushed to origin).
- **Source pins:** review against `origin/main` @ **`609a8d5`** — the current canonical source. ⚠ **Local `main` (`90ed1e0`) is STALE** (15 `sfa_delivery/` files behind, incl. the MOCKUP-FIDELITY + WI7 closures); do **not** review against it.
- **Item-1 price-chip baseline (already built):** `feat/wp-cb-book-market-pricechip` @ **`ab71d9f`** (CropBookViewController `entry()` slug-OR-`hebrew_name` resolution; +2 `CropBookV1RouteTest`; phpunit 234/234).

---

## 0. Cross-engine constraint (IR#1/#5 — MANDATORY)
The LOD400 author (team_100) and the future builder (team_10) are both **Claude**. Therefore this L-GATE_S **MUST run on a NON-CLAUDE engine** (Cursor Composer / GPT-5.x / Codex / Gemini). State the engine in the verdict header. A Claude-run verdict is constitutionally void.

## 1. Context
Three delivery-tier (`sfa_delivery/` only) loose ends from the recent crop-book UI work, grouped because they share a tier, test harness, and deploy. No data/schema/pipeline changes.
1. **Book↔market ₪ price-chip** — head-start already fixes the production "0 chips" bug (slug-OR-`hebrew_name`); extend with an **estimated-price-from-book** fallback.
2. **Deep-provenance source pills** — the EX/PR/WR provenance pill is dropped when the enrichment mirror carries no `winning_source_class`; restore it from the variety payload.
3. **Calculator precision-to-mockup** — align `/calc/` to the team_35 `calc.html` mockup (the deferred WI7 F-REA-005/006 pixel-polish).

## 2. Artifacts to review
- **LOD400 SPEC (subject):** the path above — read it in full **including §3 Acceptance criteria and §8 (build-session pre-validation corrections)**.
- **Source files the spec pins (verify each line ref resolves to the claimed code on `origin/main` @ `609a8d5`):**
  - `sfa_delivery/app/Controllers/CropBookViewController.php`
    - Item 1: `entry()` price map (the head-start lives here on the `feat/…pricechip` branch); the `market_link` attach at **L578–L585** (`$crop['market_link']['price_current'] = (float)($marketRow['last_price'] ?? 0.0)`) — the source for AC-1.2's estimate.
    - Item 2: enrichment vs payload `source_class` — **L611–L669** (the `winning_source_class` / `source_class` reads), the variety-payload mapper `buildSourceClasses()` at **L1032+**, the per-field `winning_source_class` emits at **L901 / L934 / L949**, and the stale comment block at **~L685–L686 / ~L741–L744** (AC-2.3).
  - `sfa_delivery/templates/pages/book_entry.php` — the `.cc__price` chip (AC-1.1/1.2 render site).
  - `sfa_delivery/templates/macros/crop_topics.php` + `prov_value.php` + `prov_table.php` — the deep `.prov`/`.srcline` source rows (AC-2.1/2.2 render contract).
  - `sfa_delivery/templates/pages/calc_dash.php` + `sfa_delivery/public_assets/css/redesign.css` (`.qb-goal`/`.qb-intro`/`.step__h`) — Item 3.
  - **Mockup (DS SSoT for AC-3):** `_COMMUNICATION/TEAM_100/UI_REDESIGN_2026-06/mockups/calc.html`.

## 3. Spec-review checklist — run each independently against the actual source

### 3.1 Root-cause correctness (did the LOD pin the RIGHT code + is the approach sound?)
- **R1 — Item 1 price source is real & honest.** Confirm the crop payload genuinely carries `market_link.price_current` (CropBookViewController L583–585) so AC-1.2's estimate has a real backing field, and that the priority rule (AC-1.4: **live > book-estimate > none**) is sound. Confirm AC-1.2's estimate reads a **cached** payload value (not a live re-query) and is honestly labeled distinct from live (`מחיר מוערך`, not `בשוק`).
- **R2 — Item 2 provenance fallback targets the right gap.** Confirm `source_class` can legitimately originate from the **variety payload** (`buildSourceClasses` / the payload mapper) and not only the enrichment mirror's `winning_source_class`, so AC-2.1's pill-restoration is the correct fix; confirm AC-2.2 (omit the row when there is genuinely no provenance — no fabricated/blank pill) preserves honesty; confirm AC-2.3's "stale comment" actually exists at the cited location.
- **R3 — Item 3 is presentation-only, reusing the engine.** Confirm AC-3.4's directive holds: the alignment reuses the **existing** `qb-*` components / `AssumptionField` / `/calc` endpoints (no parallel re-implementation), AC-3.2 keeps the 6 working client-calcs' behavior unchanged, and AC-3.3 keeps the 8 "בקרוב" server-stubs honestly marked (no fabricated math).

### 3.2 Precision / executability (junior-dev gate — could a fresh team_10 build this with zero guesses?)
- **P1 — Pins resolve.** Spot-check every §2/§4 file:line against source; flag any that does not resolve. (Note: SPEC §8 already corrected the calc-mockup path and the `crop_topics.php`→`templates/macros/` path — confirm those corrections are right.)
- **P2 — AC-1.2 is unambiguous.** The label (`מחיר מוערך`), the `price_kind: live|estimated` flag, and the muted/dashed `.cc__price--est` modifier give the builder an exact, testable target; the estimate renders **only** when `market_link.price_current > 0`.
- **P3 — Calc parity is measurable.** AC-3.1 is checkable via `qa_probe.mjs --shots` vs the now-correctly-pinned mockup at 375 + desktop (`overflow=false` + visual parity) — not a vague "make it nicer".
- **P4 — Test plan is concrete.** §5 adds the right tests (AC-1.5b estimate chip, AC-1.5c no-chip, AC-2.4 payload-only deep pill) and preserves the 234 green.

### 3.3 Constitutional / scope discipline
- **C1 — Tier scope is airtight.** Confirm every change is `sfa_delivery/` render-layer (PHP map/format + template + CSS); Non-goals (§2) correctly exclude schema, DB writes, pipeline, `_aos/`, `/market/{slug}` (→ MARKET-DETAIL), `/about` (→ ABOUT), and Phase-B calcs.
- **C2 — IR#4 (single-writer roadmap).** Confirm the builder is not expected to edit `_aos/roadmap.yaml`; roadmap mutations are team_100's at closure.
- **C3 — Validation flow is constitutional.** External L-GATE_S (this) + external L-GATE_V both non-Claude; builder = Claude team_10; deploy = FTPS from the Mac (team_00 opens the Mac IP).
- **C4 — Locked DS principles respected.** DS tokens (`redesign.css`), `.num` RTL isolation, readability floor (13px / body 17–18px), watercolors = identity; AC-1.2's estimate honesty is the crux of Item 1.

## 4. Verdict format → `_COMMUNICATION/team_190/SFA-S003-P004/WP-CB-UI-TAILS/WP-CB-UI-TAILS_LGATE-S_VERDICT_v1.0.0.md`
```yaml
wp: SFA-S003-P004-WP-CB-UI-TAILS
gate: L-GATE_S
validator_engine: <non-Claude — name it>
result: PASS | PASS_WITH_FINDINGS | BLOCKED
rootcause_checks: <n/3>      # R1..R3
precision_checks: <n/4>      # P1..P4
constitutional_checks: <n/4> # C1..C4
findings:
  - id: F-190-TAILS-S-NN
    severity: BLOCKER | MAJOR | MINOR | INFO
    summary: ...
    evidence: <file:line>
    disposition: <fix-inline | builder-acknowledge | R2>
authorize_build: true | false
summary: <one paragraph>
```
- **PASS / PASS_WITH_FINDINGS (build-authorized)** → team_100 folds any MAJOR/MINOR into the LOD, then team_10 (Claude) builds, then external L-GATE_V.
- **BLOCKED** → team_100 revises the LOD400 and routes R2.

Notify via a MSG in `_COMMUNICATION/TEAM_100/` (ADR043 naming).

---
*Self-contained L-GATE_S package for non-Claude execution. team_00: route to a non-Claude validator. SPEC review only — verify the pinned root causes against `origin/main` @ `609a8d5` source; do not build or mutate the live DB.*
