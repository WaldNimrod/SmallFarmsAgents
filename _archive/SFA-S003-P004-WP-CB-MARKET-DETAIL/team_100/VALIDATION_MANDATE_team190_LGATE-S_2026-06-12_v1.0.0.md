# VALIDATION MANDATE + PROMPT — SFA-S003-P004-WP-CB-MARKET-DETAIL (L-GATE_S) — team_100 → team_190 — v1.0.0

**Date:** 2026-06-12
**From:** team_100 (Chief System Architect, Claude Opus — build session)
**To:** team_190 (Independent Validator)
**Routed by:** team_00
**Repo:** `/Users/nimrod/Documents/SmallFarmsAgents`
**Gate:** **L-GATE_S** (spec review) of WP-CB-MARKET-DETAIL — re-skin `/market/{slug}` to the redesign DS. **Pre-build** — review the LOD400 SPEC for soundness, precision, root-cause correctness, and constitutional/scope compliance. **No build exists yet** — SPEC review only; do not build or mutate the live DB.

**Refs:**
- **Spec under review (as corrected — see SPEC §8):** `_COMMUNICATION/TEAM_100/SFA-S003-P004-WP-CB-MARKET-DETAIL/SPEC_2026-06-12_v1.0.0.md` on branch `docs/cb-handoff-specs` (pushed to origin).
- **Source pins:** review against `origin/main` @ **`609a8d5`** — current canonical source. ⚠ **Local `main` (`90ed1e0`) is STALE** (15 `sfa_delivery/` files behind); do **not** review against it.

---

## 0. Cross-engine constraint (IR#1/#5 — MANDATORY)
The LOD400 author (team_100) and the future builder (team_10) are both **Claude**. This L-GATE_S **MUST run on a NON-CLAUDE engine** (Cursor Composer / GPT-5.x / Codex / Gemini). State the engine in the verdict header. A Claude-run verdict is constitutionally void.

## 1. Context
`/market/{slug}` (`market_product.php`) is the last surface still on the **old Class-B v2 design** (`.pbig`/`.pgraph`/`.pstats` + heavy inline styles + raw OS emoji), while the market **list** + crop pages moved to the redesign DS in WP-CB-UI-MOCKUP-FIDELITY. This WP brings the detail page into the same design language, folds the DSX1-excluded emoji, wires the watercolor hero, and dispositions the two disabled range buttons. **Render-layer only** — no data/price-history/schema change.

## 2. Artifacts to review
- **LOD400 SPEC (subject):** the path above — read in full **including §3 Acceptance criteria and §8 (build-session pre-validation corrections, which RETRACT the v1.0.0 controller-change instruction)**.
- **Source files the spec pins (verify each resolves on `origin/main` @ `609a8d5`):**
  - `sfa_delivery/templates/pages/market_product.php` (380 lines) — the re-skin target. Raw emoji at **L126 `📦`** (hero `veg` letter), **L197 `📭`**, **L205 `📊`**, **L264 `📭`**, **L343 `📖`** (AC-2). Class-B v2 blocks `.pbig`/`.pgraph`/`.pstats`/`.pdetail` (file header L6–8; usage throughout). Freshness pill logic L59–67; sparkline L72–77/L326–331 (AC-4).
  - `sfa_delivery/app/Controllers/MarketViewController.php` — **`mapProductRow()` sets `wc_art` at L260 and `book_slug` at L261**, and is called by **both** `index()` (L63) **and** `detail()` (L86). ⚠ **This is the §8 correction:** `detail()` ALREADY exposes `$product['wc_art']` — AC-3 is **template-only**, no controller edit. Confirm this independently.
  - `sfa_delivery/public_assets/css/redesign.css` — the list `.pcard`/`.pc__*`/`.fresh`/`.spark`/`.bigspark` components to reuse (AC-1/AC-4).
  - `sfa_delivery/public_assets/css/classb.css` + `mobile-fixes.css` — the `.pbig`/`.pgraph`/`.pstats`/`.pdetail` blocks proposed for retirement (gated on a usage check — AC-1 + §4 + §7).
  - **DS mockup (AC-1 parity SSoT):** `_COMMUNICATION/TEAM_100/UI_REDESIGN_2026-06/mockups/market.html`.

## 3. Spec-review checklist — run each independently against the actual source

### 3.1 Root-cause correctness (did the LOD pin the RIGHT code + is the approach sound?)
- **R1 — The re-skin target & DS reuse are correct.** Confirm `market_product.php` is genuinely the last Class-B v2 surface (inline `.pbig`/`.pgraph`/`.pstats`), and that the redesign components AC-1/AC-4 reuse (`.pcard`/`.pc__*`/`.fresh`/`.spark`/`.bigspark`) exist in `redesign.css` and match the list/drill-down language — reuse, not re-duplication (the `.fresh::before` classb-vs-redesign conflict MOCKUP-FIDELITY resolved is the risk to watch, §7).
- **R2 — Watercolor hero is template-only (the §8 correction).** **Verify** that `wc_art` is set by the shared `mapProductRow()` (L260) and that `detail()` (L86) calls it, so `$product['wc_art']` is already available to `market_product.php` — i.e. AC-3 needs **no** controller change, only wiring the existing value into the hero (replacing the L126 letter glyph), with a line-glyph fallback when empty. Flag if you find `detail()` does NOT in fact receive `wc_art`.
- **R3 — Emoji inventory is complete & correct.** Confirm the five emoji (L126/197/205/264/343) are the full set in `market_product.php` and that `.gi` + the `ui-icons.svg` sprite is the correct DSX-1 replacement (AC-2).
- **R4 — Data contract is preserved.** Confirm `MarketViewController::detail()` → `$product`/`$history` is unchanged (AC-4: 28-day graph + history table + freshness pill preserved, render-only restyle); no price-history/schema/data mutation (Non-goals §2).

### 3.2 Precision / executability (junior-dev gate)
- **P1 — Pins resolve.** Spot-check every §2/§4 ref against source; flag any that does not resolve. (SPEC §8 already corrected the watercolor-hero controller claim and verified the emoji lines + added the `market.html` mockup pin — confirm.)
- **P2 — The retirement step is gated, not blind.** Confirm §4/§7's instruction to retire `.pbig`/`.pgraph`/`.pstats`/`.pdetail` from `classb.css`/`mobile-fixes.css` is correctly **gated behind a repo-wide usage check** (include-gate, as in MOCKUP-FIDELITY) with a no-regression re-verify of all Class-B routes — the highest-risk step.
- **P3 — AC-5 range-button disposition is decided, not deferred.** Confirm §1.3 gives a concrete disposition for the disabled `90י`/`שנה` buttons (default: keep honestly-disabled `בקרוב`, or remove) so the builder has no open affordance question. **(team_35/00 call — flag if you read it as still-ambiguous.)**
- **P4 — Empty-state + cross-links are specified.** Confirm AC-6 (empty/no-price state renders cleanly) and AC-7 (→ crop-book, → calc cross-links + the mandatory market disclaimer preserved) are explicit.

### 3.3 Constitutional / scope discipline
- **C1 — Tier scope is airtight.** Every change is `sfa_delivery/` render-layer (template + CSS + the one already-present controller value); no data/price-history/schema (Non-goals §2); no market-list change (already at parity).
- **C2 — IR#4.** Builder does not edit `_aos/roadmap.yaml`.
- **C3 — Validation flow is constitutional.** External L-GATE_S (this) + external L-GATE_V both non-Claude; builder = Claude team_10; deploy = FTPS from the Mac.
- **C4 — Locked DS principles + QA discipline.** DS tokens, `.num` RTL isolation, capped `.shell` (1100px); AC-6 requires `qa_probe.mjs --shots` `overflow=false` + visual parity at 375 + desktop — **never validate this layout with curl alone** (CLAUDE.md).

## 4. Verdict format → `_COMMUNICATION/team_190/SFA-S003-P004/WP-CB-MARKET-DETAIL/WP-CB-MARKET-DETAIL_LGATE-S_VERDICT_v1.0.0.md`
```yaml
wp: SFA-S003-P004-WP-CB-MARKET-DETAIL
gate: L-GATE_S
validator_engine: <non-Claude — name it>
result: PASS | PASS_WITH_FINDINGS | BLOCKED
rootcause_checks: <n/4>      # R1..R4
precision_checks: <n/4>      # P1..P4
constitutional_checks: <n/4> # C1..C4
findings:
  - id: F-190-MKTD-S-NN
    severity: BLOCKER | MAJOR | MINOR | INFO
    summary: ...
    evidence: <file:line>
    disposition: <fix-inline | builder-acknowledge | R2>
authorize_build: true | false
range_button_disposition_ack: <keep-disabled | remove | needs-team35>
summary: <one paragraph>
```
- **PASS / PASS_WITH_FINDINGS (build-authorized)** → team_100 folds any MAJOR/MINOR into the LOD, then team_10 (Claude) builds, then external L-GATE_V.
- **BLOCKED** → team_100 revises the LOD400 and routes R2.

Notify via a MSG in `_COMMUNICATION/TEAM_100/` (ADR043 naming).

---
*Self-contained L-GATE_S package for non-Claude execution. team_00: route to a non-Claude validator. SPEC review only — verify the pinned root causes (esp. the §8 watercolor-hero correction) against `origin/main` @ `609a8d5` source; do not build or mutate the live DB.*
