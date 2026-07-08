---
id: HANDOFF_SFA-S003-P004-WP-CB-UI-MOCKUP-FIDELITY_v1.0.0
from: team_100 (session that investigated the live-UI vs team_35 mockup gap)
to: team_100 (implementing session)
date: 2026-06-11
type: session-handoff (aos_handoff full 100)
wp: SFA-S003-P004-WP-CB-UI-MOCKUP-FIDELITY
project: SFA-S003-P004
gate: L-GATE_E → L-GATE_SPEC → build
status: REGISTERED — awaits SPEC
engine: Claude Code (builder) — validator MUST differ (IR#1/#5)
---

# HANDOFF — SFA-S003-P004-WP-CB-UI-MOCKUP-FIDELITY — team_100 → team_100

**Bring the live delivery UI into fidelity with the team_35 Step-2 hi-fi mockups — a precision/fix
round, surface by surface.**
**Track:** A · **Effort:** MEDIUM-LARGE (UI/CSS/templates across 7 surfaces) · **Risk:** LOW-MEDIUM (delivery
tier only; no schema/data) · **Tier:** delivery (Slim4/PHP + CSS), deployed via **FTPS `lftp` from the Mac**.

## 0. ⭐ Why this WP exists (team_00 directive, 2026-06-11)

team_00 asked: *"why doesn't our interface look like the mockups we got from team_35?"* and directed a
precision/fix round to align the UI to those mockups. The mockup package (`SFA Small Farms Agents (8).zip`,
team_35 WP-CB-UI-REDESIGN **Step-2**) is copied verbatim into `mockups/` in this WP dir.

## 1. Investigation — why it doesn't match (root cause)

The design **system** and assets are ALREADY live — the gap is that the high-traffic **index/list surfaces
were never migrated to the Step-2 card design**, plus cross-surface drift.

**Already matching (do NOT redo):**
- DSX-1 icon system, DSX-2 type-scale tokens (`--fs-body/--fs-data/...`), `.num` RTL number-isolation — all
  present in `sfa_delivery/public_assets/css/redesign.css` (from prior WP-CB-UI-REDESIGN / DSX1-SWEEP / FIDELITY).
- Watercolor crop assets present: `sfa_delivery/public_assets/img/crops/wc-*.png`.
- The **deep crop page** (`book_crop.php`, ≈ `crop_card.html`) and the **home tool-cards** largely adopted the
  Step-2 look (hero, numbered lifecycle stages, care icons, module watercolors).

**The gap (DB- + screenshot-verified — see `gap_evidence/`):**

| Surface | Mockup (target) | Live (current) | Pri |
|---|---|---|---|
| **Crop-book LIST** `/crop-book` | spacious cards, **large watercolor per crop**, prominent **₪ price chip**, עכשיו/בקרוב line-glyph pills, comfortable density | dense small-card grid, **tiny/placeholder icons** (not the watercolors), cramped, ₪ not prominent | **P1** |
| **Market GRID** `/market` | spacious price cards: watercolor, big ₪, trend arrow, **freshness pill**, **28-day sparkline**, drill-down | dense table-like grid, small icons, **no sparklines**, cramped | **P1** |
| **Home** `/` | hero with a **watercolor crop strip** + manifesto (~60ch); tool cards w/ module watercolors | tool cards OK, but hero lacks the watercolor strip + has an **extra price-ticker** not in the mockup | **P2** |
| **Crop page** `/crop-book/{slug}` | related-crops shown as **watercolors**; 4-metric key-data row | related-crops use **generic leaf icons**; key-data differs (3 metrics; a stray `-80`) | **P2/P3** |
| **calc / assumptions / cropdata_entry** | per mockups (`calc.html` etc.) | `/crop-book/calc` returned 404 — **locate the live calc route** and diff vs `calc.html` | **P3** |

Mechanism: the deep page is governed by `redesign.css` (Step-2), but the list/market surfaces still render
with the older dense layout (`crop-book-v1.css` / `classb.css`). They were never refactored from v1 → the
Step-2 card design. The watercolors + tokens exist; the list/market templates just don't use them.

## 2. Scope — bring each surface to mockup fidelity

**P1 (the real miss):** refactor the **crop-book list** and **market grid** card layouts to the Step-2
mockups — spacious comfortable cards, prominent watercolor per crop (reuse `img/crops/wc-*.png`), ₪ price
chip, line-glyph status/freshness pills, market 28-day sparkline + drill-down. Reuse `redesign.css` tokens;
do NOT invent new visual language.
**P2:** home hero watercolor strip + reconcile the price-ticker against the mockup; crop-page related-crops →
watercolors + key-data row parity.
**P3:** calc/assumptions/cropdata_entry diff vs mockups; the README §"Key fixes" checklist (2-col `dl`
de-crush, calc step-badge grid, mobile header collapse, ⓘ→L2 modal 44px touch, `.num` everywhere).

Honor the locked principles: DS tokens locked (`mock.css` mirrors DS v3), watercolors = identity, RTL
number integrity (`.num` LTR+nowrap), readability floor 13px / body 17-18px (DSX-2).

## 3. Method

1. Open `mockups/00_DESIGN_BOARD.html` (all 7 screens, desktop + 375px) and `mockups/HANDOFF_NARRATIVE.html`
   (per-screen tweak inventory + decisions log). `mockups/README.md` = integration notes.
2. Per surface: render the live page + the mockup, diff (the `gap_evidence/` MOCK_*/LIVE_* pairs are a start),
   refactor the template + CSS (`sfa_delivery/templates/pages/*` + `public_assets/css/redesign.css`; retire the
   v1/classb card rules for those surfaces).
3. Browser-QA EVERY surface with `qa_probe.mjs --shots` at mobile(375) + desktop — overflow=false + visual
   parity (per CLAUDE.md: never validate layout with curl alone).
4. Local preview on the SQLite harness (port 8095, `reference_sfa_local_preview_harness`) before deploy.

## 4. Deploy + integrity (the "live system" requirement)

- **UI CODE deploy = FTPS `lftp` from the Mac** → uPress: `bash scripts/ftp_deploy_sfa_ui.sh`
  (`documentation/05-admin-and-operations/UI_DEPLOY_RUNBOOK.md`). **NOT** the HMAC ingest (that's data only).
  ⚠ uPress FTPS allowlists by current external IP — ask team_00 to open the Mac's IP (TCP :21 timeout = closed).
- Integrity: delivery `vendor/bin/phpunit` 0 fail (copied vendor) · `validate_aos.sh` 0 FAIL · production smoke
  (`qa_probe` overflow=false, visual parity on all 7 surfaces, mobile + desktop).

## 5. Cautions / startup

Read `CLAUDE.md` → `_aos/governance/team_100.md` → this handoff → `mockups/README.md` + `HANDOFF_NARRATIVE.html`.
**Use a `git worktree` per WP** (shared-checkout branch-collision hazard — see project memory). DB online → API
for hub mutations; spoke roadmap file-based (ADR034 R9). Cross-engine L-GATE_VALIDATE at the end (validator ≠
Claude Code). Verdict/closure return to **this team_100 origin**.

## 6. Verdict / done

All 7 mockup surfaces render at **visual parity** with `mockups/` at desktop + 375px (qa_probe overflow=false);
crop-book list + market grid use the spacious watercolor/₪/sparkline card design; cross-surface fidelity items
(P2/P3) closed or explicitly deferred via DECISION; delivery phpunit + `validate_aos` green; LIVE on
sfa.nimrod.bio + production smoke; cross-engine L-GATE_VALIDATE PASS → LOD500_LOCK.

## 7. Inputs / references

- Mockup package (verbatim): `mockups/` — `00_DESIGN_BOARD.html`, `HANDOFF_NARRATIVE.html`, `README.md`,
  7 `*.html`, `mock.css` (locked DS v3), `mock-v2.css` (Step-2 refinement layer), `sfa-icons.js`, `wc/`.
- Gap evidence: `gap_evidence/` (MOCK_* vs LIVE_* desktop screenshots, 2026-06-11).
- Live CSS/templates: `sfa_delivery/public_assets/css/redesign.css` (Step-2 tokens/icons/.num — reuse),
  `crop-book-v1.css` / `classb.css` (the dense layouts to retire on list/market), `templates/pages/*`.
- Deploy: `scripts/ftp_deploy_sfa_ui.sh`, `documentation/05-admin-and-operations/UI_DEPLOY_RUNBOOK.md`.
- Prior UI WPs (context, already locked): WP-CB-UI-REDESIGN, WP-CB-UI-FIDELITY, WP-CB-UI-CLASSB,
  WP-CB-UI-patch01, WP-CB-DSX1-SWEEP.
