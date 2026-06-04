# VALIDATION MANDATE + PROMPT — SFA-S003-P004-WP-CB-UI-FIDELITY (L-GATE_S) — team_100 → team_190 — v1.0.0

**Date:** 2026-06-04
**From:** team_100 (Chief System Architect, Claude Opus)
**To:** team_190 (Independent Validator)
**Routed by:** team_00
**Repo:** `/Users/nimrod/Documents/SmallFarmsAgents` · branch `claude/ui-polish-hub-cropbook-2026-06-03`
**Gate:** **L-GATE_S** (spec review) of WP-CB-UI-FIDELITY — pre-launch crop-book + market UI fidelity & Hebrew localization. **Pre-build** — review the LOD400 (v1.1.0, team_100-reviewed) for soundness, precision, root-cause correctness, and constitutional/scope compliance. **No build exists yet** — this is a SPEC review; do not attempt a live build or live-DB checks.

---

## 0. Cross-engine constraint (IR#1/#5 — MANDATORY)
The LOD400 author (team_100) and the future builder (team_10) are both **Claude**. Therefore this L-GATE_S **MUST run on a NON-CLAUDE engine** (Cursor Composer / GPT-5.x / Codex). State the engine in the verdict header. A Claude-run verdict is constitutionally void.

## 1. Context
team_00 reported sfa.nimrod.bio is far from the approved team_35 mockups: **raw DB floats, English unit codes, English category menus, dead filters, a broken/duplicated crop hero.** team_100 ran a CDP browser audit (real rendering — the prior code gates check structure/markers only, which is why these shipped past composer/validate and even L-GATE_V; the team_50 Haiku QA tier was also unreliable). The audit + a full source trace **confirmed** five launch-blocking defects and located each to exact `file:line`. This WP remediates them to Board-A/B fidelity, **render-layer only** (no DB/data mutation). The executing session must externally validate this spec **before** any build.

## 2. Artifacts to review
- **LOD400 (this gate's subject):** `_aos/work_packages/S003/SFA-S003-P004-WP-CB-UI-FIDELITY/LOD400_spec.md` (v1.1.0, team_100-reviewed)
- **Audit evidence (live renders + mockups + facts):** `_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-UI-FIDELITY/audit_evidence/` — `live_crop-page_lettuce.png`, `live_market-list.png`, `live_hub.png`, `live_crop-book-entry.png`, `MOCK_Board-A_book-calc.png`, `MOCK_Board-B_surfaces.png`, `cdp_facts.json`
- **Design SSoT:** Board-A / Board-B (paths in LOD400 frontmatter `design_ssot`)
- **Source files the LOD pins (verify the line refs resolve to the claimed code):**
  - `sfa_delivery/templates/pages/book_crop.php` (`$pv()` L47-70; topic-card units L208/215/227; heroes L154-172 + L467-527; `#identity` L468)
  - `sfa_delivery/templates/macros/prov_value.php` (L66/80/84)
  - `sfa_delivery/app/Lib/FieldRegistry.php` (`ENUM_LABELS['category']` L260-275; `enumLabel()`; no `unitLabel()` yet)
  - `sfa_delivery/app/Controllers/CropBookViewController.php` (`entry()` season L54; `questions()` L124-128; `tableView()` L152-187)
  - `sfa_delivery/app/Controllers/MarketViewController.php` (`fetchCategories()` L354-371)
  - `sfa_delivery/templates/pages/book_entry.php` (season input L158; filter form L130-189)
  - `sfa_delivery/public_assets/css/crop-book-deep.css` (`.cb-crop-hero__icon` L522-528) · `crop-book-v1.css` (`.crophero` L157-165)
  - `sfa_delivery/templates/_layout.php` (per-route JS asset gate)

## 3. Spec-review checklist — run each independently against the actual source

### 3.1 Root-cause correctness (the heart of this review — confirm the LOD pinned the RIGHT code)
- **R1 — D-1/D-2 render path.** Confirm the crop page renders values through the inline `$pv()` closure in `book_crop.php` (NOT the `prov_value.php` macro), and that L63 emits the value with no numeric formatting and L67/L69 print the raw `unit`. Confirm WI-1/WI-2 target this path. Verify the `is_numeric()` guard requirement is correct so enum values still route through `enumLabel()`.
- **R2 — D-1b double-unit.** Confirm `book_crop.php:208/215/227` hardcode a Hebrew unit while `$pv()` also emits the field unit (→ "72.000000 days ימ׳"). Confirm the single-unit rule (renderer owns the unit; remove the three `<small>` suffixes) actually de-duplicates without dropping the unit on the headline row (L185-200, whose `$hv_fields['unit']` is unused).
- **R3 — D-3 category root cause.** Confirm `MarketViewController::fetchCategories()` sets `name_he => $cat` (raw slug) and that `market_list.php:53` renders it faithfully (so the fix belongs in the controller + `ENUM_LABELS`, NOT the template). Confirm the three missing keys (`legumes_fresh`, `eggs`, `baskets`) are genuinely absent from `ENUM_LABELS['category']` and the other seven are present.
- **R4 — D-4 two root causes.** (a) Confirm the season filter (`entry()` L54 `season LIKE ?`) depends on a token format the LOD does NOT assume but requires the build to verify against stored `crops.season`. (b) Confirm D-4b: `questions()` builds `table?category=summer|winter|fast|beginner|small-space` while `tableView()` filters `WHERE category = ?` against the botanical `category` column → guaranteed 0. Confirm the re-routing instruction is sound and that "beginner/small-space without backing data" is correctly escalated (Q4/WI-7) rather than silently shipped.
- **R5 — D-5 / D-5b hero.** Confirm BOTH `.crophero` (L154-172) and `.cb-crop-hero` (L467-527) render a breadcrumb + `<h1>` name (→ duplicate identity), that `.cb-crop-hero__icon` is an 80×80 green box (`crop-book-deep.css:522`) wrapping a zero-bbox sprite `<use>` (matches `cdp_facts.svg_zero:2`), and that the dedup ruling preserves the description lede + family/dtm pills and retargets `#identity` so the section nav (L126/535) does not break.

### 3.2 Precision / executability (junior-dev gate — could a fresh team_10 Sonnet build this with zero guesses?)
- **P1 — Every defect names a real file + mechanism + the exact change.** Spot-check the §2 pinned-location table against source; flag any line ref that does not resolve to the claimed code.
- **P2 — The number-format rule is unambiguous** (integers when whole; ≤1–2 sig decimals; strip trailing zeros; numeric-only). Confirm AC-1's regex (`\d+\.\d{3,}` + trailing-zero) actually catches the audit examples (59.043478, 30.000000, 8.000000).
- **P3 — The unit map is complete enough.** Confirm WI-2 cites `organic_market_agent/crop_book/canon/field_registry.py` as the authoritative per-field unit source and that unknown tokens degrade safely (return as-is).
- **P4 — Calc-dashboard parity is an explicit requirement, not an aside** (D-1/D-2 apply to `/calc/`; calc_dash/calc_panel/calc_seq listed).
- **P5 — Interaction E2E (M-1) is testable**: the toggle/audience/depth-tab/adv-filter/market-graph-range/calc/search checks are concrete CDP click tests, and the `window.fetchHistory` gap is correctly framed as a JS-binding issue (endpoint `productHistoryApi:94` exists).

### 3.3 Constitutional / scope discipline
- **C1 — Render-layer scope is airtight.** Confirm every WI is a PHP map/format + template + CSS + one JS asset-gate; NO DB/data mutation. Confirm the D-4 data caveat (§7) correctly says: if stored `crops.season` tokens are themselves wrong, STOP and scope a separate data WP — do not fold silently.
- **C2 — IR#4.** Confirm AC-7 forbids builder `_aos/roadmap.yaml` edits.
- **C3 — Validation flow is constitutional.** Confirm §6 routes external L-GATE_S (this) and external L-GATE_V to team_190 (non-Claude), with team_100 doing only the independent L-GATE_B (CDP), and deploy routed to team_99 (this Mac session is deploy-auth-gated).
- **C4 — No regression contract.** Confirm the "WORKS" list (§1) and patch01 WI-9 (`/crop-book/table` 375 overflow, committed e798bc8, undeployed) are both in the AC regression budget (AC-6/AC-7) so WI-9 reaches LOD500 with this WP.
- **C5 — Design authority respected.** Confirm the team_35-authority items (Q2 wording, Q3 dunam-vs-hectare unit, Q4 beginner/small-space, Q5 eyebrows) are routed via WI-7 and BLOCK only their own items, while the architect-decided Q1 (hero dedup) needs no team_35 input. Flag any place the spec guesses a missing design.

## 4. Verdict format → `_COMMUNICATION/team_190/SFA-S003-P004/WP-CB-UI-FIDELITY/WP-CB-UI-FIDELITY_LGATE-S_VERDICT_v1.0.0.md`
```yaml
wp: SFA-S003-P004-WP-CB-UI-FIDELITY
gate: L-GATE_S
validator_engine: <non-Claude — name it>
result: PASS | PASS_WITH_FINDINGS | BLOCKED
rootcause_checks: <n/5>      # R1..R5
precision_checks: <n/5>      # P1..P5
constitutional_checks: <n/5> # C1..C5
findings:
  - id: F-190-FID-S-NN
    severity: BLOCKER | MAJOR | MINOR | INFO
    summary: ...
    evidence: <file:line or screenshot>
    disposition: <fix-inline | builder-acknowledge | R2>
authorize_build: true | false
summary: <one paragraph>
```
- **PASS / PASS_WITH_FINDINGS (build-authorized)** → team_100 folds any MAJOR/MINOR into the LOD inline, then dispatches team_10 (Sonnet) for the L-GATE_B build.
- **BLOCKED** → team_100 revises LOD400 and routes R2.

Notify via a MSG in `_COMMUNICATION/team_100/` (ADR043 naming).

---
*Self-contained L-GATE_S package for non-Claude execution. team_00: route to a non-Claude validator. This is a SPEC review — no build exists yet; verify the pinned root causes against source, but do not build or run live-DB checks.*
