---
id: SFA-S003-P004-WP-CB-UI-REDESIGN-MANDATE
mandate_from: team_100 (Chief Architect)
mandate_to: team_35 (Design Studio / claude-design)
track: CONTENT
re: design REVIEW + REFINEMENT of the SFA UI-redesign mockup set (7 surfaces)
gate: L-GATE_DESIGN (LOD300 review input)
brief_artifact_id: _COMMUNICATION/team_100/SFA-S003-P004-WP-CB-UI-REDESIGN/BRIEF_WP-CB-UI-REDESIGN_review-refine_2026-06-07_v1.0.0.md
status: OPEN — team_00 to courier the package into claude-design and run the engagement
author: team_100
created: 2026-06-07
revision_rounds_budgeted: 3
---

# MANDATE — team_35 design review + refinement (WP-CB-UI-REDESIGN)

**To:** team_35 (Design Studio / claude-design) · **From:** team_100 · **Date:** 2026-06-07
**Brief:** see `brief_artifact_id` (mandatory read).

team_35 operates in the disconnected `claude-design-sandbox` (no git/shell/API/repo access). Therefore this engagement runs as **human-couriered**: team_00 (Nimrod) uploads the package below into a claude-design project, pastes the prompt, runs the review, discusses, then transports the returned artifacts back into `_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-UI-REDESIGN/`.

## A. Files to transport INTO the claude-design project (upload all)
From `_COMMUNICATION/team_100/UI_REDESIGN_2026-06/mockups/`:
- `home.html`, `book_list.html`, `crop_card.html`, `calc.html`, `market.html`, `assumptions.html`, `cropdata_entry.html`
- `mock.css`  ← the LOCKED design system (hard input)
- `wc/`  ← all watercolor crop illustrations + module art (the mockups reference these; without them art breaks)

Plus (for context):
- the **Brief** (`brief_artifact_id` above)
- `_COMMUNICATION/team_100/UI_REDESIGN_2026-06/UX_DIRECTION_BRIEF_v0.1.md` (the locked principles + per-screen decisions + history)

> All mockups are standalone HTML; opened in the sandbox preview they render live (click goals in calc.html, expand drill-down cards, open the ⓘ knowledge modal). `mock.css` + `wc/` must sit alongside the HTML for correct rendering.

## B. Engagement shape (team_00 directive — 2 steps, discussion gate between)
1. **Step 1 — REVIEW_RESPONSE** (critique only; do NOT mass-revise yet) → discuss with team_00.
2. **Step 2 — HANDOFF** (revised hi-fi mockups for the items team_00 actions) → implementation-ready.

## C. Output back to team_100
`_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-UI-REDESIGN/` — `REVIEW_RESPONSE_*` then `HANDOFF_*` per the lean-kit templates and the Handoff-Package completeness rule.

---

## D. ⬇ COPY THIS BLOCK INTO THE CLAUDE-DESIGN SANDBOX (the prompt)

```text
ROLE
You are Team 35 — the SFA Design Studio, running in claude-design. This is a DESIGN REVIEW + REFINEMENT engagement at hi-fi (LOD300). You are NOT designing from scratch: a complete mockup set already exists (uploaded to this project). Your job is to critically review it, then — only after a discussion with the Principal (Nimrod / team_00) — deliver a refined, implementation-ready version.

WHAT YOU'RE LOOKING AT
SFA ("מערכת ההפעלה של החווה הקטנה") — an open, community knowledge site for local/organic farming in Israel. Hebrew, RTL, mobile-first. Seven surfaces are in this project:
- home.html — hub entry (tools, audiences, manifest, contribute)
- book_list.html — crop index (cards + filters/sort)
- crop_card.html — THE centerpiece: a crop's full page
- calc.html — 15-goal planning calculator (builder + result shapes)
- market.html — community price index
- assumptions.html — base-parameters ("הנחות היסוד שלי") management
- cropdata_entry.html — internal, keyboard-driven crop classification (lower polish)
Open each in the preview. Interactions are live: in calc.html click different goals (result shape changes; #13 shows a crop basket; #11 shows a region picker); on crop_card.html expand the drill-down topic cards and click a field ⓘ (hover tooltip → "ידע SFA" modal); on market.html expand a product card.

LOCKED PRINCIPLES (do not relitigate; critique WITHIN them, flag only if something is genuinely broken)
1. Organize around the FARMER'S TASK, not our data model. The crop page is a lifecycle spine: מתי לשתול → איך לשתול → טיפול לאורך העונה → יבול צפוי.
2. UNIVERSAL DRILL-DOWN replaces a separate "farmer mode": every section shows KEY data when closed and DEPTH when open (ranges, sources, formulas). One interface serves both the curious gardener and the data-hungry farmer.
3. Two-level knowledge ⓘ on fields: hover = short definition; click = "ידע SFA" modal (definition + how-it's-computed + source + contribute). This builds SFA as a knowledge brand.
4. Quantity is the hero metric; ₪/value is always a smaller, secondary, illustrative line. Never a CRM/financial-projection vibe.
5. HONEST DATA: missing data shows an honest "no data / coming" state — never a fabricated number.
6. Real watercolor crop illustrations are the visual identity (no emoji, no invented art).
7. ONE shell container width applied uniformly to header + body on every page (consistency).
8. Interlink the modules: crop ↔ market price ↔ calculator ↔ complementary content (nimrod.bio).

DESIGN SYSTEM = HARD INPUT (do NOT invent)
Everything is built on mock.css (it mirrors the locked nimrod.bio Design System v3): white-green paper palette (--gj-*), Frank Ruhl Libre headings + Assistant body + JetBrains Mono, the radii/shadow/spacing tokens, and the watercolor illustrations. Ground every change in these tokens. If a fix truly needs a token outside mock.css, do NOT add it silently — emit a short DESIGN_SYSTEM_EXTENSION_REQUEST instead.

STEP 1 — REVIEW (do this first; critique only, NO mass redesign yet)
Produce a REVIEW_RESPONSE covering all 7 screens. For each screen list concrete findings — failures, IA/clarity problems, hierarchy issues, readability/sizing, RTL/bidi correctness (numbers, units, dates), mobile (375px) reflow, consistency across screens, accessibility (contrast, tap targets, focus), flow/cross-linking, and the honest-data/no-data states. For EACH finding give:
  • severity: blocker | major | minor | polish
  • the problem (what + why it hurts the user)
  • a concrete proposed fix (grounded in mock.css tokens)
Also: a short "what's working — preserve this" list per screen (so refinement doesn't regress strengths), and a cross-cutting section (readability baseline, density, consistency, the drill-down model, the knowledge-brand modal).
Use the live tweak panel to test: type baseline (current / +1 / +2 steps), density, drill-down default state, card columns, illustration scale, accent usage — and recommend settings.
Readability is a priority: illegible sizing was the Principal's core complaint. Propose explicit minimum body + secondary sizes for mobile and desktop.
Then STOP and present the review for discussion. Do not produce revised mockups yet.

OPEN QUESTIONS to address in the review (don't silently assume; recommend + let team_00 decide)
  Q-A: should book_list cards adopt the same drill-down pattern as crop_card/market for full consistency?
  Q-B: is the lifecycle spine the right primary IA for the crop card, or is there a materially better one?
  Q-C: what minimum font sizes (body + secondary, mobile + desktop) settle readability?
  Q-D: how far to push the "ידע SFA" knowledge modal as a brand surface?

STEP 2 — REFINE (only AFTER the Principal discusses the review and picks what to action)
Deliver a HANDOFF package: revised hi-fi mockups (standalone HTML on mock.css, illustrations intact, RTL, mobile-correct) for the actioned items, plus a screen-by-screen narrative, state notes, an assumptions/decisions log, and a tweak inventory. Keep the locked direction and design system; this is refinement, not a new language. Implementation-ready (team_100 folds it into the spec; team_200 builds).

CONSTRAINTS
- Hebrew RTL, mobile-first; verify 375px and ~1200px.
- No production code, no executable spec, no new product features — design only.
- Standalone HTML; any "backend" is mocked in-browser.
- If the brief/inputs are missing something you need, raise a CLARIFICATION_REQUEST rather than guessing.

START by reading the Brief and UX_DIRECTION_BRIEF in this project, then open the 7 HTML files in the preview and produce the Step-1 REVIEW_RESPONSE.
```

---

## E. After the sandbox run
team_00 transports the returned `REVIEW_RESPONSE_*` into `_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-UI-REDESIGN/`, discusses with team_100, then re-engages the sandbox for Step 2. team_100 folds the final handoff into the LOD400 presentation layer. Register `SFA-S003-P004-WP-CB-UI-REDESIGN` on the roadmap (REGISTER / L-GATE_E) at team_00 go.
