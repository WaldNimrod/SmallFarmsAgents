# PRE-LAUNCH VISUAL + E2E QA MANDATE — team_100 → team_50 — v1.0.0

**Date:** 2026-06-03 · **From:** team_100 (Chief System Architect) · **To:** team_50 (QA & Functional Acceptance)
**Routed by:** team_00 · **Subject:** full-system launch-readiness audit of **https://sfa.nimrod.bio**
**Required output:** a single launch-readiness verdict — **GO / GO-WITH-FIXES / NO-GO** — plus a prioritized punch-list.

---

## 0. Why this exists
team_00 is about to take SFA to market. Before that, team_50 must **independently certify the whole live system
is sound, complete, and pixel-faithful to the approved team_35 design** — every surface, every button, every
feature. Two recent defects (giant `/crop-book/` entry cards; a broken site-wide app-shell logo) were **invisible
to code/test gates** (composer + validate_aos pass on both) because they are **rendering** bugs. This audit must
catch that entire class. **Curl is not sufficient** (it sees HTML, never the rendered box model). Use a real
browser (CDP) for every visual claim.

## 1. Preconditions
- **Target build:** the LATEST deployed tip. Confirm team_99 has deployed **patch01 tip `7fbcf89`** (WI-1..WI-6)
  and that the live `crop-book-v1.css?v=…` / `classb.css?v=…` reflect it (WI-5 `cb-paths { display: grid`, WI-6
  `.sh__mark svg { width: 100%`). If not yet live, QA the branch render locally AND flag that live ≠ branch.
- **Engine:** team_50 (Claude, read-only). **Do NOT** edit source, run git, or fix anything — **report only**.
- **Branch (for code cross-checks):** `claude/ui-polish-hub-cropbook-2026-06-03` (or `main` post-merge).

## 2. Tooling (mandatory)
- **Primary — real rendering (CDP):** `_aos/lean-kit/modules/validation-quality/scripts/qa/qa_probe.mjs`
  (Node 18+, dependency-free; see `_aos/lean-kit/modules/validation-quality/docs/BROWSER_QA_HARNESS_CANON_v1.0.0.md`).
  Use it to: load each route, capture **screenshots**, read **computed styles + element bounding boxes** (to catch
  oversized/overflowing elements), check **horizontal overflow** (`scrollWidth > clientWidth`), read **console
  errors**, and follow links/click buttons.
- **Viewports (test EACH surface at all three):** desktop **1440×900** and **1280×800**, tablet **768**, mobile **375×812**.
- **Design reference (approved team_35 mockups):**
  - Board-A (Crop Book + Calculator): `_archive/SFA-S003-P004-WP-CB-UI-CLASSB/team_35/SFA-S003-P004-WP-CB-UI-CLASSB/HANDOFF/design/Board-A-Book-and-Calculator.html`
  - Board-B (Hub/Market/Search/Community/About/Account): `_archive/SFA-S003-P004-WP-CB-UI-CLASSB/team_35/SFA-S003-P004-WP-CB-UI-CLASSB/HANDOFF/design/Board-B-Hub-Market-Search-Community-About-Account.html`
  - Design tokens/system: white-green (`--gj-*`, paper `#f8fbf8`, no cream); fonts Assistant + Frank Ruhl Libre + Carmela; RTL; watercolor crop art; `.sh` app-shell.
  - Serve each Board locally (e.g. `php -S` / static) and produce **design-vs-live screenshot pairs** per surface.
- curl/Lighthouse are **secondary** (Lighthouse perf/a11y is informative; remember dev SEO/cache scores are artifacts — re-measure on the production domain).

## 3. Surface inventory — audit EVERY route
For each: HTTP 200 (or correct 404/redirect), renders without break, matches the mockup, no horizontal overflow,
RTL correct, palette/fonts correct, no console errors, no broken asset (img/art/icon 404).

| # | Route | Page | Design ref |
|---|-------|------|-----------|
| 1 | `/` | Hub / home | Board-B hub-home |
| 2 | `/crop-book/` | Crop book entry (hero, entry-path cards, crops grid) | Board-A |
| 3 | `/crop-book/{slug}` | Crop detail — **all 3 depths**: simple / full / drill | Board-A |
| 4 | `/crop-book/{slug}/variety/{vslug}` | Variety detail | Board-A |
| 5 | `/crop-book/family` | Botanical families | Board-A |
| 6 | `/crop-book/table` | Table view | Board-A |
| 7 | `/crop-book/search` + `/search?q=` | Search (match + no-match) | Board-A/B |
| 8 | `/crop-book/questions` | Leading questions | Board-A |
| 9 | `/crop-book/cover-crops` | Cover crops | Board-A |
| 10 | `/calc/` | Calculator dashboard (14 calcs) | Board-A |
| 11 | `/calc/print` + `/calc/export.csv` | Plan export (print + CSV) | Board-A |
| 12 | `/market/` | Market index list | Board-B market-list |
| 13 | `/market/{slug}` | Market detail (graph + ranges) | Board-B market-detail |
| 14 | `/community` | Community (manifesto + request form) | Board-B community |
| 15 | `/about` | About / 5-tier ladder | Board-B about-tiers |
| 16 | `/account` | Account shell ("בקרוב") | Board-B account |
| 17 | App-shell (every route) | header logo + nav (desktop+mobile) + search + footer | Board-A/B `.sh` |

## 4. E2E interaction matrix — click/exercise EVERY control
Confirm each does the right thing (navigates / opens / computes / toggles / submits) AND nothing is dead/broken.
- **App-shell:** logo → `/` (and logo renders correctly — NOT broken/oversized); each desktop nav link (ספר/מחשבון/מחירון) + mobile bottom-nav (4 tabs incl. חשבון) → correct route + active state; inline search → submit → `/search`; footer links (על הכלים→/about, קהילה→/community) — and footer קהילה is non-self-linking on /community.
- **Hub `/`:** intro tagline is ONE line (desktop); 4 module tiles → routes (3 live clickable + the **Field-Log "יומן השדה / בפיתוח" tile is NON-clickable**); audience cards; `.hub-cta` — secondary "שתפו...לספר"→/community + **primary "ספרו לנו..."→WhatsApp** both work; soon-grid tiles non-interactive.
- **Crop book entry:** the 4 entry-path cards → their routes (questions/family/table/search) and are **compact, not giant**; filters (family, season, dtm, sow-method, frost) apply; search box; audience toggle (Cards⇄Table); each crop card → crop page.
- **Crop page (`/crop-book/{slug}`):** depth tabs **simple / full / drill** switch content; provenance cues render (VALIDATED/UNVALIDATED + winning-source) and read from the enrichment tables (not raw keys); variety links; any tooltips; no farmer-facing raw enum/field keys (e.g. `direct_seed`, `half_hardy`, `family:variety`, `yield_per_bed_m`).
- **Calculator `/calc/`:** crop `<select>` → **book-chips populate** (SFA_CROP_BOOK); adjust an **AssumptionField** → recompute; each of the **14 calculators** runs and shows output (or a correct disabled/MISSING state); export → **CSV** downloads + **print** view renders.
- **Market `/market/`:** Cards⇄Table density toggle; freshness pills (fresh/aging/stale); category filter; product → `/market/{slug}`; on detail: graph range buttons (**7י/28י active, 90י/שנה disabled**), contribute prompt; honest empty/stale states (`.pcard.is-empty`, `.emptybox`).
- **Search:** query → grouped results; no-match → the `◐ בקשו` `.reqinfo` CTA → /community.
- **Community:** request chips (kind selection); the contribute form submits to `/api/v1/contribute` (verify the POST path works / returns sanely — do NOT spam; one test submission).
- **Forms generally:** validation, required fields, success/error feedback, no console error on submit.

## 5. Design-vs-mockup fidelity (per surface)
For each surface, place the **live screenshot beside the Board-A/B frame** and judge: layout structure, spacing,
type scale/fonts, color tokens (computed `#f8fbf8` ground, no cream `#f5f3ec`), component shapes (cards, pills,
buttons, tiers), watercolor art presence, RTL alignment. Flag any divergence with severity. Intentional, approved
deviations (note prior L-GATE_V notes) are not defects — but call them out.

## 6. Cross-cutting checks (launch-blockers if failing)
- **C-A — Oversized/unsized-element hunt (the recent bug class):** scan EVERY page for elements whose rendered
  box is disproportionately large or overflows its container — especially **inline `<svg><use>`** (logos, icons,
  card art) that lack width/height, and cards with `aspect-ratio` on full-width containers. Report any element with
  bbox far exceeding intent.
- **C-B — Horizontal overflow / RTL:** no page scrolls horizontally at any viewport; RTL direction + alignment
  correct throughout; Hebrew not truncated/clipped.
- **C-C — Asset integrity:** no 404 on CSS/JS/img/watercolor-art/icon-sprite; fonts actually load (Assistant/Frank
  Ruhl Libre/Carmela); favicon/og present.
- **C-D — Honest data + no leakage:** no `Array`/`NULL`/`undefined`/`[object`/raw DB keys/untranslated enum tokens
  rendered to users; empty/partial/stale states read gracefully.
- **C-E — JS console:** zero uncaught console errors per route.
- **C-F — Link integrity:** crawl internal links; none 404 / dead.
- **C-G — Consistency:** the app-shell (logo/nav/footer) is byte-consistent across all pages.
- **C-H — Accessibility basics:** images have alt (or aria-hidden), interactive elements are reachable/labelled,
  disabled teasers carry `aria-disabled`, focus states visible.
- **C-I — Responsiveness:** the 4 viewports each render a coherent layout (nav collapses correctly, grids reflow).
- **C-J — Performance sanity:** page weight reasonable, no obviously unoptimized payload; (Lighthouse on production
  domain optional/informative).

## 7. Add-your-own
team_50: **append any additional check you judge necessary** to certify launch-readiness (e.g. SEO meta/og per
page, sitemap/robots, 404 page UX, error-page UX, security headers, mixed-content, mobile tap-target sizes,
print-stylesheet sanity, i18n edge cases, long-content overflow, slow-network behavior). List what you added + why.

## 8. Output — write to `_COMMUNICATION/team_50/SFA-PRELAUNCH-QA/PRELAUNCH_QA_REPORT_2026-06-03_v1.0.0.md`
1. **Verdict:** GO / GO-WITH-FIXES / NO-GO (one line + rationale).
2. **Per-surface table:** route · desktop fidelity · mobile · E2E pass · key findings.
3. **Findings list** with severity — **BLOCKER** (breaks/ugly/wrong, must fix pre-launch) · **MAJOR** · **MINOR** ·
   **COSMETIC** — each with: route, what, evidence (screenshot path / CDP bbox / computed value), and a suggested fix.
4. **E2E matrix results** (every control: PASS / FAIL / N/A + note).
5. **Design-vs-mockup** notes per surface (+ screenshot-pair references).
6. **Cross-cutting (C-A..C-J)** results + your §7 additions.
7. **Prioritized punch-list** (ordered, so team_100 can dispatch fixes to team_10).
8. **Evidence folder:** `_COMMUNICATION/team_50/SFA-PRELAUNCH-QA/evidence_2026-06-03/` (screenshots + a manifest).

## 9. Constraints
- **Read-only.** No source edits, no git, no `_aos/` edits, no fixes — findings only.
- Use the **CDP browser harness** for all visual/box-model/overflow claims (curl-only visual claims are rejected).
- Cross-engine note: team_50 is Claude (internal QA). The final external constitutional gate remains **team_190
  (non-Claude)** after fixes — this audit feeds the fix punch-list, it does not replace L-GATE_V.
- Be exhaustive and skeptical: assume nothing renders correctly until the browser proves it does.
