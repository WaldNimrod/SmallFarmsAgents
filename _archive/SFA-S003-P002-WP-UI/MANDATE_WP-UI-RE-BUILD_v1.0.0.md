---
id: MANDATE_WP-UI-RE-BUILD_v1.0.0
from: Team 00 (Principal) → Team 100 (Chief System Architect — incoming session)
to: Team 100 (Chief System Architect — Claude Sonnet builder/orchestrator)
date: 2026-05-27
type: RE_BUILD_MANDATE
gate: L-GATE_B (re-open) → L-GATE_V (final, cross-engine)
wp: SFA-S003-P002-WP-UI
project: smallfarmsagents
priority: HIGH
status: ACTIVE
verdict: PENDING
authority: team_00 (Principal — directly mandated post-visual-audit)
engine_constraint: "BUILD: Claude Sonnet (you, team_100). FINAL VALIDATION: team_190 non-Claude (GPT-5.5 / Cursor / Codex) per IR#1. Do NOT delegate BUILD to team_10 (Codex) — that's what produced the bare-bones implementation in v1.0.0 / v1.0.1 / v1.0.2 that triggered this re-build."
previous_attempt: "WP-UI v1.0.0 → v1.0.2 sequence (commit 740ea2c on claude/sfa-ui-build). L-GATE_V R2 PASS verdict was technically valid for the VCs checked but did not catch visual-fidelity gap. team_00 directly audited live site vs design and revoked."
supersedes: "All prior WP-UI BUILD reports (v1.0.0 / v1.0.1 / v1.0.2) — preserved in _COMMUNICATION/TEAM_10/SFA-S003-P002-WP-UI/ as audit trail; not the basis for re-build."
parallel_session_context: "A parallel session is expanding the canonical Postgres schema on waldhomeserver + adding new fields to crops/varieties/products. Your BUILD must accommodate evolving field-set; do NOT hardcode field lists; treat /api/v1/crops/{slug} and /api/v1/products/{slug} as the authoritative shape SSoT at any moment."
---

# RE-BUILD Mandate — SFA-S003-P002-WP-UI v2

**Standalone web UX shell on https://sfa.nimrod.bio/ — complete design fidelity + DB-aware + responsive + merged + deployed + cross-engine validated**

**Track:** A | **Profile:** L0 | **Risk:** MEDIUM-HIGH (visible to public; multi-stream coordination required)
**Estimated effort:** 8-12 hours
**Reporting cadence:** chapter mark per phase; quick status checks every ~2h

---

## 0. Why you're here (Team 00 audit summary)

Previous WP-UI build sequence produced a **functional but visually wrong** site:
- All 14 routes returned 200 with Hebrew content ✓
- Lighthouse mobile a11y 100/100/100 ✓
- team_190 R2 PASSED constitutional validation ✓
- **BUT** the actual rendered HTML on https://sfa.nimrod.bio/ does NOT match team_35's LOD300 design. The CSS files (75 KB total) are loaded but ~75% is dead code because the HTML lacks the BEM class hooks team_35's CSS targets.

**Root cause:** team_10 (Codex) wrote simplified HTML during BUILD; team_100 (Claude) remediation focused on a11y not visual fidelity; LOD400 ACs did not include "DOM matches COMPONENTS.md contract"; team_190 L-GATE_V VCs did not include visual diff vs artboards. The constitutional gates were correct for what they checked — but the spec didn't ask them to check what mattered most.

team_00 directive: **revoke L-GATE_V, return to BUILD with comprehensive new mandate.**

---

## 1. Four deliverables (binding, from team_00)

### Deliverable 1 — Full design fidelity per team_35 LOD300

- 14 HTML templates + 10 macros + 3 shells (mobile/desktop/_mark_svg) rewritten so the **DOM exactly matches** `COMPONENTS.md` BEM contract
- Every CSS class declared in the 7 design files (`tokens.css`, `gj.css`, `hub.css`, `community.css`, `crop-book-deep.css`, `desktop.css`, `desktop-extras.css`) must be **either used by templates or removed**. No dead CSS, no missing DOM hooks.
- All 28 artboards in `_archive/SFA-S003-P002-WP-UI/team_35/_handoff/design/index.html` must be reproducible at the correct viewport
- Vegetable SVG sprite from `illustrations.jsx::CROP_ICON` extracted and used (icons.svg)
- Hebrew RTL preserved end-to-end; Frank Ruhl Libre headings + Assistant body + JetBrains Mono code per `DESIGN_TOKENS.md`
- 3-tier color system honored: leaf (open) / sun (beta) / soil (paid) / tomato (custom) / paper (coming)

### Deliverable 2 — DB-aware: accommodate parallel-session schema expansion

- A parallel team session is **actively expanding** the canonical Postgres schema (waldhomeserver) and pushing new fields to MySQL via `sfa_ingest_push.py`
- Your BUILD must **NOT hardcode the field set** of crops/varieties/products
- Authoritative shape SSoT at any moment = the live response from `GET /api/v1/crops/{slug}` and `/api/v1/products/{slug}` and `/api/v1/crops` etc.
- Templates use defensive rendering: iterate over `payload_json` keys with a known-label dictionary; gracefully render unknown fields under a "more info" section; never blow up on null/missing
- Before each deploy, `curl -sS https://sfa.nimrod.bio/api/v1/crops/anise-hyssop | jq keys` to snapshot the field set; adapt the variety/crop detail templates to it
- If field set grows mid-BUILD, re-pull from API and adapt — do not block on the parallel session

### Deliverable 3 — Merge + full deploy

- Build branch: create `claude/sfa-ui-build-v2` off `origin/claude/sfa-ui-build` (commit `740ea2c`)
- All commits on `claude/sfa-ui-build-v2` push to origin per phase
- After BUILD complete and validated: **merge `claude/sfa-ui-build-v2` → `main`** via fast-forward or merge commit (you decide; either is fine)
- Push main to origin
- FTPS deploy from main's `sfa_delivery/` to `https://sfa.nimrod.bio/` (using main `.env` SFA_FTP_* creds)
- Verify post-deploy via curl + Claude_in_Chrome at all 14 routes

### Deliverable 4 — Final comprehensive test (cross-engine)

- Run all 38 ACs from LOD400 v1.0.2 §5 (existing — keep as floor)
- ADD 14 new ACs: **per-route visual fidelity** — DOM contains the BEM classes from COMPONENTS.md per template (specific class list per route in §3 below)
- ADD 4 new ACs: **responsive emulation** — true mobile viewport (Chrome devtools mobile profile via Playwright/Puppeteer or MCP that supports CSS viewport, NOT just OS window resize). Mobile shell visible <900px; desktop shell visible ≥900px; no double-render.
- Run MCP browser tests via Claude_in_Chrome OR Playwright (whichever supports actual viewport emulation)
- After your BUILD_REPORT: dispatch canonical L-GATE_V mandate to **team_190 non-Claude** with **new VCs explicitly checking visual fidelity per BEM contract + responsive**

---

## 2. Mandatory: responsive (team_00 emphasis)

**⚠️ "חובה לתת דגש על התאמה רספונסיבית" — this is non-negotiable.**

Specifically:
- Test at **3 viewport widths**: 390px (iPhone), 768px (iPad), 1280px (laptop)
- At 390px: only `.gj-shell` (mobile) renders; `.dt-shell` is `display:none`. Header is sticky single-row with hamburger or compact tabs. Content fits without horizontal scroll. Touch targets ≥44px.
- At 768px: still mobile shell (the swap is at 900px per team_35 §3.5)
- At 1280px: only `.dt-shell` (desktop) renders; sidebar accordion visible; main content grid layouts
- The CSS swap must be media-query-driven (already deployed in `desktop-extras.css` v1.0.1 — VERIFY still working in your rebuild)
- Capture screenshots at all 3 widths per route (42 screenshots for 14 routes) and include in BUILD_REPORT visual evidence

**Acceptance:** if you cannot reproduce a smooth narrow-viewport experience that matches the mobile artboards in team_35's `_handoff/design/index.html`, the BUILD is not COMPLETE.

---

## 3. Per-route DOM contract (extracted from COMPONENTS.md)

Each route's template MUST render at least these BEM classes (additional are fine):

| Route | Required BEM classes (minimum) | Artboard ref |
|-------|--------------------------------|--------------|
| `/` (hub home) | `gj-shell` `gj-header` `gj-header__row` `gj-mark` `gj-title` `gj-sub` `gj-body` `gj-foot` `gj-foot__dot` `module-card` `module-card__h` `module-card__sub` `module-card__stat` `module-card__icon` `tier` `tier--leaf`/`--sun`/`--soil`/`--tomato`/`--paper` `tier__glyph` | H1 (mobile), D1 (desktop) |
| `/about` | `gj-shell` `gj-header` `gj-body` `hub-tiers-intro` `hub-tier-list` `tier tier--lg` | H2/D2 |
| `/search?q=` | `gj-shell` `gj-topbar` (or `dt-search` on desktop) | D8 |
| `/calc` | `gj-shell` `tier tier--sun` `gj-crosslink` (WhatsApp CTA pattern) | H3/D7 |
| `/crop-book/` | `gj-shell` 4 entry-cards with `module-card` pattern | CB0 |
| `/crop-book/questions` | `gj-shell` `gj-row__big` (question cards) | CB1 |
| `/crop-book/family` | `gj-shell` family taxonomy list | CB2 |
| `/crop-book/table` | `gj-shell` (mobile) + `dt-shell` `dt-table` (desktop); `<th scope="col">` per column | CB3/D3 |
| `/crop-book/search?q=` | `gj-shell` `gj-search` | CB4 |
| `/crop-book/{slug}` | `gj-shell` `crop-detail__head` `crop-detail__h1` `crop-detail__sci` `crop-vars__list` `crop-vars__row` (per variety) | CB5/D4 |
| `/crop-book/{slug}/variety/{vslug}` | extends CB5 with `crop-vars__row--expanded` + field grid (`variety-fields` `<dl><dt><dd>`) | CB5 expanded |
| `/market/` | `gj-shell` `market-disclaimer` (with all 4 sub-bullets) + `gj-row` per product with `gj-row__big` (price) + `gj-row__sub` (date+source) | MK1/D5 |
| `/market/{slug}` | `gj-shell` `gj-pricebig` `gj-pricebig__big` `gj-pricebig__unit` + price history table | MK2/D6 |
| `/community` | `gj-shell` `contact-card` `contact-card__h` `contact-card__lede` `contact-card__cta` (WhatsApp link, NO form per L-GATE_S binding) | H4/D9 |

(Cross-reference each with `COMPONENTS.md` §1-§N for full DOM/attribute contract.)

---

## 4. Phased build plan (suggested — adjust as needed)

| Phase | Hours | Output |
|-------|-------|--------|
| P.0 | 0.5 | Worktree branch `claude/sfa-ui-build-v2` off `740ea2c`. Read COMPONENTS.md + TEMPLATES.md + DESIGN_TOKENS.md end-to-end. Browse `design/index.html` artboards in real browser. |
| P.1 | 1 | Rewrite `_layout.php` chain — verify CSS link order + asset_ver + Google Fonts. Extract icons.svg from `illustrations.jsx`. |
| P.2 | 2 | Rewrite `shell/mobile.php` + `shell/desktop.php` + `shell/_mark_svg.php` to EXACT BEM contract per §1.1 + §1.2 of COMPONENTS.md (header rows, mark SVG, tabs, foot dot, sidebar accordion, etc.). |
| P.3 | 2 | Rewrite all 10 macros per COMPONENTS.md §2-§N: `tier_badge.php` (tier + tier__glyph + tier--{color}), `module_card.php` (full BEM with __h __sub __stat __icon), `price_card.php`, `crop_card.php`, `variety_row.php`, `contrib_strip.php`, `crosslink.php`, `market_disclaimer.php` (with all 4 mandatory bullets), `feed_item.php`, `timeline_bar.php`. |
| P.4 | 2 | Hub: rewrite `hub_home.php`, `hub_tiers.php`, `hub_calc.php`. Tier sections with proper headers + module-card grid. |
| P.5 | 2 | Crop book: rewrite `book_entry.php`, `book_questions.php`, `book_family.php`, `book_table.php`, `book_search.php`, `book_crop.php` (CB5 with full crop-detail__ + crop-vars__ DOM), `book_variety.php`. |
| P.6 | 1.5 | Market: `market_list.php` (with mandatory disclaimer block + gj-row pattern), `market_product.php` (gj-pricebig + history). |
| P.7 | 0.5 | Community: `community.php` static contact-card. Search: `search_results.php`. |
| P.8 | 1 | DEPLOY: bundle + lftp mirror to sfa.nimrod.bio. Verify each route via curl. |
| P.9 | 1.5 | RESPONSIVE TEST: Playwright or Chrome devtools mobile profile at 390/768/1280; 42 screenshots; verify mobile shell vs desktop shell swap; no horizontal scroll mobile; touch targets verified. |
| P.10 | 1 | DB-EVOLVE CHECK: re-pull /api/v1/crops/{slug} schema; verify all returned fields render gracefully (known labels + unknown-field fallback). |
| P.11 | 1 | MERGE: rebase/merge `claude/sfa-ui-build-v2` → `main`. Push main. Re-deploy from main if any drift. |
| P.12 | 1 | BUILD_REPORT_v2.0.0.md with full 38 + new visual + new responsive ACs, all PASS. |
| P.13 | — (dispatch only) | Canonical L-GATE_V mandate to team_190 with explicit visual-fidelity + responsive VCs. |

**Total: ~17 hours.** This is more than v1 — but it's design-correct, DB-resilient, merged, deployed, responsive-tested, and cross-engine validated.

---

## 5. Acceptance Criteria (for L-GATE_V validator)

### 5.1 Inherit from v1.0.2 LOD400 §5 — all 38 PASS still (route 200s, Hebrew, APIs, regression, etc.)

### 5.2 NEW — Visual fidelity (14 new ACs)

For each of the 14 routes in §3 above: `curl https://sfa.nimrod.bio/{route}` returns HTML that contains **all required BEM classes** listed in §3 (use `grep -c` per class; expect ≥1 per class per route).

### 5.3 NEW — Responsive (4 new ACs)

| # | AC | Verify |
|---|----|----|
| AC-R-1 | At 390×844 viewport (true Chrome mobile emulation), only `.gj-shell` is computed-visible; `.dt-shell` has `display: none` | Playwright `page.locator('.gj-shell').isVisible()` true AND `.dt-shell` evaluated computed style display=none |
| AC-R-2 | At 1280×900, only `.dt-shell` is visible; `.gj-shell` is hidden | inverse of AC-R-1 |
| AC-R-3 | At 390px width, no horizontal scroll on any of 14 routes | Playwright `page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth)` returns false |
| AC-R-4 | Touch targets (`<a>`, `<button>`, `summary`, `input`) all have rendered bounding box ≥24×24 CSS px per WCAG | axe-core / Lighthouse a11y target-size audit returns 0 failures (already verified in v1.0.2 — must not regress) |

### 5.4 NEW — DB-resilience (1 new AC)

| # | AC | Verify |
|---|----|----|
| AC-DB-1 | Templates render correctly when `payload_json` contains 1+ fields NOT in the template's known-label dictionary | Manually inject a test crop with an unknown `payload_json` key via /api/v1/ingest; navigate to `/crop-book/{slug}`; verify page renders 200 + the unknown field appears in a "more info" fallback section (not a PHP warning, not silent drop) |

**Total: 38 (from v1.0.2) + 14 visual + 4 responsive + 1 DB-resilience = 57 ACs.**

---

## 6. Files to read (in this order)

### Primary contracts (binding)
1. `_archive/SFA-S003-P002-WP-UI/team_35/_handoff/COMPONENTS.md` — DOM contract per macro/shell. **Read fully.**
2. `_archive/SFA-S003-P002-WP-UI/team_35/_handoff/DESIGN_TOKENS.md` — CSS variables, color palette, typography
3. `_archive/SFA-S003-P002-WP-UI/team_35/_handoff/TEMPLATES.md` — per-page contract
4. `_archive/SFA-S003-P002-WP-UI/team_35/_handoff/MODULES_REGISTRY.yaml` — 8 modules + tiers (use this verbatim, no edits)
5. `_archive/SFA-S003-P002-WP-UI/team_35/_handoff/design/index.html` — visual canvas; **open in browser**; pan/zoom each artboard
6. `_archive/SFA-S003-P002-WP-UI/team_35/_handoff/design/*.jsx` — visual ground truth for components (do NOT port directly; use as visual reference for the BEM DOM)
7. `_archive/SFA-S003-P002-WP-UI/team_35/_handoff/HANDOFF_LOD300.md` — full design rationale

### Current state (your inputs)
8. `_aos/work_packages/S003/SFA-S003-P002-WP-UI/LOD400_spec.md` v1.0.2 (kept as floor — your re-build adds to it, doesn't replace; bump to v1.1.0 only if you change ACs)
9. `sfa_delivery/` on branch `claude/sfa-ui-build` (commit `740ea2c`) — what to rewrite
10. `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-UI/BUILD_REPORT_v1.0.2.md` — the previous attempt's report (lessons)

### Architecture context
11. `_COMMUNICATION/team_00/DECISION_SFA-S003-P003_DEDICATED_SFA_SUBDOMAIN_2026-05-23_v1.0.0.md`
12. `documentation/02-architecture/sfa-delivery-tier.md` + `documentation/03-data-and-schema/sfa-mysql-mirror.md`

### DB-evolution awareness (parallel session)
13. Latest `GET https://sfa.nimrod.bio/api/v1/crops/anise-hyssop` (or whatever the API returns) — re-pull at start of each template work
14. waldhomeserver Postgres: `ssh nimrodw@100.125.98.56 'ls /data/projects/smallfarmsagents/organic_market_agent/db/versions/ | tail -10'` — check latest alembic migration index

---

## 7. Output

### BUILD_REPORT
Write to: `_COMMUNICATION/TEAM_100/WP-UI-RE-BUILD_REPORT_v2.0.0.md`

7 sections:
1. **Outcome** — BUILD_COMPLETE | BUILD_PARTIAL + 2-sentence rationale
2. **Parameters** — branch, commits, engine, hours actual vs estimate
3. **AC Table** — all 57 (38 inherited + 14 visual + 4 responsive + 1 DB) with PASS evidence
4. **Findings** — anything not perfect (severity, must_resolve_before)
5. **validate_aos.sh** output
6. **Artifacts** — visual_diff/ (42 screenshots × 3 viewports), responsive test outputs, Lighthouse JSONs, merge commit ref, deploy log
7. **Next step** — single imperative for team_190 L-GATE_V

### L-GATE_V dispatch
After BUILD_REPORT: invoke `/AOS_gate-mandate` skill OR generate mandate manually at `_COMMUNICATION/TEAM_190/MANDATE_WP-UI_L-GATE_V_R3_v2.0.0.md`. Include the **new visual + responsive + DB VCs** explicitly so team_190 actually checks them this time.

---

## 8. Constraints + reminders

- **Cross-engine (IR#1):** YOU build (Claude). team_190 (non-Claude) validates. Do NOT delegate BUILD to team_10/Codex this round — Codex's v1.0.0 produced the bare-bones HTML that triggered this re-build.
- **IR#4 single roadmap writer:** you are team_100 — you write roadmap.yaml. No other agent should touch it.
- **Parallel-session coordination:** another team session is modifying Postgres + pushing new fields. Do NOT touch `organic_market_agent/db/versions/` or `sfa_ingest_push.py`. Your work is strictly `sfa_delivery/`. If you see schema-drift errors at deploy time, re-pull API + adapt templates.
- **No fake "complete" — visual fidelity is the bar.** team_00 will personally audit live site before accepting close.
- **Responsive is non-negotiable.** Test at true mobile viewport (Playwright or Chrome devtools), NOT OS-window resize.
- **Merge to main is required.** Site cannot live forever on a feature branch.
- **No skipping team_190 with "PASS_WITH_FINDINGS" carry-overs.** This time L-GATE_V must be a true PASS with the visual + responsive VCs explicitly verified.

---

## 9. Orchestration role

You are not just builder — you are **orchestrator** for this end-to-end re-build. That includes:

- Status update to user (team_00) every ~2 hours or per chapter mark
- Coordinate with the parallel DB-expansion session (don't step on each other)
- Detect when team_00 needs to make a decision (uPress IP allowlist change, schema field naming, etc.) and surface it cleanly
- Maintain task list via TaskCreate/TaskUpdate so user can see progress
- When BUILD_REPORT complete: dispatch L-GATE_V; when verdict back: handle remediation OR close

End state when you're done:
- WP-UI roadmap status: COMPLETE / LOD500_LOCKED (via genuine cross-engine L-GATE_V PASS)
- main branch reflects the work
- https://sfa.nimrod.bio/ visually matches team_35 design across 3 viewports
- New fields from parallel session render gracefully
- team_00 can open the live URL on phone + laptop and see the design they signed off on

---

*Mandate filed 2026-05-27 by team_00 (Principal) via team_100 orchestrator (this session — outgoing). Incoming team_100 session: this is your read-first artifact. Begin with §6 reading order.*
