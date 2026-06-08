---
id: SFA-S003-P004-WP-CB-UI-REDESIGN-WORKPLAN
type: WORKPLAN
from: team_100 (Chief Architect)
re: implement the full redesigned version (7 surfaces) + calc re-skin → production on sfa.nimrod.bio
created: 2026-06-08
status: OPEN — feeds aos_handoff full 100
inputs:
  - team_35 handoff (refined LOD300): _COMMUNICATION/team_35/SFA-S003-P004-WP-CB-UI-REDESIGN/handoff_ui_redesign/
  - deployed calc: WP-CB-CALC (14/15 live, main @8f2ae91, in final L-GATE_V)
  - locked principles: _COMMUNICATION/team_100/UI_REDESIGN_2026-06/UX_DIRECTION_BRIEF_v0.1.md
---

# WORKPLAN — SFA full redesigned version → production

## 0. Inputs studied (this session)
1. **team_35 Step-2 handoff** (`handoff_ui_redesign/`): refined hi-fi for all 7 surfaces + `00_DESIGN_BOARD.html` + `HANDOFF_NARRATIVE.html` + `README.md`. NEW: **`mock-v2.css`** (refinement overlay, `mock.css` untouched) + **`sfa-icons.js`** (26-glyph inline-SVG sprite, replaces ALL emoji). Two DS extensions: **DSX-1** (icon set), **DSX-2** (type scale / readability floor 13px min). Decisions locked: Q-A book cards = nav (no in-card drill-down), Q-B lifecycle spine kept, Q-C type +1 step tokens, Q-D "ידע SFA" modal as brand anchor. ₪ prices = demo; story/treatments content arrives from a content WP (honest empty-states meanwhile).
2. **Deployed calculator** (WP-CB-CALC): **14/15 goals live in production** (`/calc/`), only `water` deferred. Engine = `crop-book-v1.js` (`SFA_CALC` + `SFA_DATEC` date engine), `calc_dash.php` builder, `HubController` server plumbing (date numerics + categorical channel), `calculators.py` (Python parity), `frost_regions.json`. Currently in **final cross-engine validation** (team_50 LIVE QA + team_190 L-GATE_V). **This engine is owned by WP-CB-CALC and is NOT to be re-implemented here.**

## 1. Objective & scope boundary
Ship ONE coherent redesigned version of the public app to `sfa.nimrod.bio`, implementing the team_35 refined mockups across the Slim/PHP delivery tier.

| Surface | Production today | This WP |
|---|---|---|
| home, book_list, crop_card, market, assumptions | old WP-CB-MOBILE/Class-A/B templates | **FULL BUILD** from refined mockups |
| calc | **deployed (WP-CB-CALC engine)** | **RE-SKIN ONLY** — apply new DS (icons/type/RTL fixes/layout) to the existing builder; **do not touch engine logic, goals, result shapes, parity** |
| cropdata_entry | none | build (internal, light polish) |
| Design system | `tokens.css` + page CSS | **fold DSX-1 (icons) + DSX-2 (type scale) + mock-v2 refinements** |

**Out of scope:** calc engine changes; `water` (#0 → WP-CB-WATER); story/treatment content authoring (content WP); dark mode; new product features; inventing tokens (DS locked).

## 2. Work breakdown

**WI-0 · DS foundation (blocks all surfaces)**
- Fold **DSX-2 type scale** into `tokens.css` (`--fs-body/data/secondary/micro`, 17/18 · 18/19 · 14 · 13; floor 13px) + the LTR number-isolation utility (`.num` nowrap).
- Land **DSX-1 icons**: ship `sfa-icons.js` (or the build's icon pipeline keeping the same 26 IDs/semantics) injected once via `_layout.php`; replace emoji site-wide. Watercolors stay for crops/modules.
- Add the **`mock-v2.css` refinement layer** to the real asset chain (after page CSS so it wins), or promote rules into `tokens.css` per team_35's gradual-adoption note. Bump asset version.
- Approve the two **DESIGN_SYSTEM_EXTENSION_REQUESTs** (team_100/team_00).

**WI-1 · Shell/layout unification (`_layout.php`)**
- ONE `--shell-max` container on header **and** body across every page (the core consistency fix); logo lockup consistent off-home.
- Mobile header ≤680px: collapse search+account, nav → scrollable row (per-surface in-page search exists).

**WI-2 · home** (`hub_home.php`) — hub: hero collage (real wc), 3 tool tiles (module art), audience cards (line icons), manifest (sprout glyph, contrast-fixed), contribute CTA, "בפיתוח" tiles.

**WI-3 · book_list** (crop index templates) — decision cards (now/next pill via line icons, days, yield, **₪ price chip** closing book↔market loop, difficulty), DTM value LTR-isolated nowrap, always-visible filters + sort, view toggle. Card = link to crop page (Q-A: no in-card drill-down).

**WI-4 · crop_card** (`book_crop.php`) — THE centerpiece. Lifecycle spine (מתי→איך→טיפול→יבול), **universal drill-down** (closed=key / open=depth) replacing Simple/Full/Deep, **two-level knowledge ⓘ → "ידע SFA" modal** (44px touch, mobile tap=L2), nursery⇄field split, spacing→plants visual, in-season care (irrigation/feeding/pruning/pests/companions + **compost/organic** line), cross-links (market chip, calc ghost button, nimrod.bio content), contribute CTA. **Honest empty-states** for story/treatments until content WP. `dl` 2-col, values nowrap.

**WI-5 · market** (`market_list.php`) — drill-down price cards (closed=price+freshness+spark / open=range/median/sources/**28-day trend**), LTR-isolated prices, "אין מגמה" wording for stale, fresh/aging/stale states, cross-links to book + calc.

**WI-6 · assumptions** (assumptions editor template) — grouped collapsibles, search, **clickable "used-in" chips** (→ calc/crop), community default + reset, sticky save bar, type-scale applied.

**WI-7 · calc RE-SKIN** (`calc_dash.php` view only) — apply icons + type scale + mock-v2 (step-badge grid, RTL number isolation, gallery folded to `<details>`) to the **existing** builder/result. **No change** to `crop-book-v1.js`, goal set, result shapes, region picker, basket, parity. **Rebase on WP-CB-CALC post L-GATE_V** to avoid regressing the validated engine.

**WI-8 · cropdata_entry** (internal owner-only tool) — keyboard 1–5 + progress + queue; light polish only.

**WI-9 · QA** — dependency-free browser-QA (`qa_probe.mjs`) for RTL/overflow/mobile(375)/desktop(1200) on all surfaces; PHP route tests per touched path seeding **RICH** crop/market fixtures (avoid the shared-include `$notes` 500 — `feedback_shared_include_scope_var_clobber`); cross-engine validation (IR#1/#5: builder≠validator) by team_50; final constitutional **L-GATE_V** by team_190.

**WI-10 · Deploy** — `scripts/ftp_deploy_sfa_ui.sh` (composer --no-dev → lftp mirror over FTPS to uPress); ⚠ open the deploy machine's **current external IP on uPress** (ask team_00 — dynamic allowlist); asset cache-bust; **live smoke** on `sfa.nimrod.bio` for every surface; rollback-first discipline on any 500.

## 3. Sequencing
```
WI-0 (DS) → WI-1 (shell) ─┬→ WI-2 home
                          ├→ WI-3 book_list
                          ├→ WI-4 crop_card   (largest)
                          ├→ WI-5 market
                          ├→ WI-6 assumptions
                          └→ WI-8 cropdata_entry
WI-7 calc re-skin ── gated on WP-CB-CALC L-GATE_V PASS (rebase first)
        ↓ (all build complete)
WI-9 QA (browser + route + cross-engine) → WI-10 deploy + live smoke → L-GATE_V → LOD500_LOCK → archive
```
Public surfaces (WI-2..6,8) parallelize after WI-0/WI-1. Deploy as ONE coherent version (avoid half-redesigned site); calc re-skin merges once its engine validation locks.

## 4. Team assignments (AOS)
- **team_100** — LOD400 presentation spec from the refined mockups; coordination; approve DSX-1/DSX-2; this workplan.
- **team_10 / team_200** — build (templates + DS folding + re-skin), cross-engine vs validator.
- **team_50** — QA / L-GATE_BUILD (non-Claude engine).
- **team_190** — final constitutional L-GATE_V (non-Claude; IR#1/#5).
- **team_99** — uPress deploy + live smoke (from allowlisted IP).
- **team_191** — archive on LOD500_LOCK.

## 5. Risks & mitigations
| Risk | Mitigation |
|---|---|
| Regressing the validated/deployed calc engine | WI-7 is re-skin only; rebase on WP-CB-CALC after its L-GATE_V; no edits to `crop-book-v1.js`/goals/parity. |
| Shared-include scope var clobber (the `$notes` 500) | Namespace template locals; seed RICH route fixtures; smoke LIVE post-deploy; roll back first then diagnose. |
| curl-only layout checks miss RTL/overflow | Use `qa_probe.mjs` (CDP) for every layout/RTL/mobile check — never curl alone. |
| uPress FTPS IP allowlist (dynamic) | Ask team_00 to open the deploy machine's current external IP; symptom = TCP :21 timeout. |
| mock-v2 overlay specificity vs real CSS | Load order: page CSS → refinement layer last; verify computed styles via `qa_probe`/inspect. |
| Content (story/treatments) not ready | Honest empty-states ship now; content WP authors `description_md`/`care.*_md` later — no schema/UI block. |
| Half-redesigned site mid-rollout | Ship as one version; calc re-skin gated; feature-flag/branch until all surfaces pass QA. |

## 6. Definition of done
All 7 surfaces live on `sfa.nimrod.bio` in the refined DS (icons, type floor, RTL-correct, mobile-correct, unified shell); calc re-skinned with engine intact; browser-QA + route tests green; cross-engine L-GATE_V PASS; LOD500_LOCKED; archived. Open follow-ups (story/treatments content WP, `water`/WP-CB-WATER) registered, not blocking.
