---
id: LOD400_VERDICT_SFA-S003-P004-WP-CB-UI-CLASSB_v1.0.0
from: team_190
to: team_100
cc:
  - team_00
  - team_10
  - team_50
date: 2026-06-02
gate: L-GATE_S
round: 1
wp: SFA-S003-P004-WP-CB-UI-CLASSB
spec_under_review: _aos/work_packages/S003/SFA-S003-P004-WP-CB-UI-CLASSB/LOD400_spec.md
spec_version: v1.0.0 LOCKED
mandate: _COMMUNICATION/TEAM_100/SFA-S003-P004-WP-CB-UI-CLASSB/VALIDATION_MANDATE_team190_LGATE-S_2026-06-02_v1.0.0.md
design_ssot: _COMMUNICATION/team_35/SFA-S003-P004-WP-CB-UI-CLASSB/HANDOFF/
branch: claude/wp-cb-ui-align-2026-06-02
head: ac4a71a
validator_engine: Cursor / Composer (non-Claude)
result: PASS_WITH_FINDINGS
blockers: 0
major: 0
minor: 7
---

# LOD400 Verdict v1.0.0 — SFA-S003-P004-WP-CB-UI-CLASSB

## §0 Executive verdict

| Field | Value |
|-------|--------|
| **Gate** | L-GATE_S (precision / spec) |
| **Spec** | LOD400 v1.0.0 LOCKED (`_aos/work_packages/S003/SFA-S003-P004-WP-CB-UI-CLASSB/LOD400_spec.md`) |
| **Result** | **PASS_WITH_FINDINGS** |
| **Blockers** | 0 |
| **Disposition** | team_100 may dispatch **team_10** build. team_50 prepares design-vs-live screenshot matrix per AC-2. |

**Bottom line:** A fresh builder can implement all seven Class B surfaces plus shell refinements from LOD400 §2 + Board-B + `classb.css`/`classb.js` + `B_COMPONENTS-TEMPLATES-classb-delta.md` without inventing layout or data policy. team_00 §9 + §9a are encoded and locked. Seven MINOR clarifications below remove residual guess-work; none block handoff.

---

## 1. Mandate compliance

| Requirement | Result | Evidence |
|-------------|--------|----------|
| IR#1 / IR#5 non-Claude validator | PASS | Validator: Cursor / Composer (not Claude). Spec author team_100 (Claude) — cross-engine satisfied. |
| Read mandate + LOD400 + design SSoT | PASS | Files read in full; code probed under `sfa_delivery/`. |
| §9a not relitigated | PASS | Thresholds ≤3 / 4–7 / >7 and unit table treated as team_00-APPROVED. |
| Verdict path | PASS | This file. |
| `validate_aos.sh` | PASS | 29 PASS / 19 SKIP / 0 FAIL (2026-06-02 session). |

---

## 2. L-GATE_S checks

### C1 — Precision (zero-guessing buildability)

**PASS_WITH_FINDINGS**

| Surface | Named in LOD400 §2? | Board frame + CSS? | Ambiguity |
|---------|---------------------|-------------------|-----------|
| 2.1 Shell refine | Yes (`_layout.php`, `shell-desktop/mobile`) | Board-B §3.1 + `classb.css` `.sh__search`/`.sh__foot` | MINOR: inline `.sh__search` lives in Class B CSS, not LOD400 verbatim CSS block — port `classb.css` resolves. |
| 2.2 Hub | Yes | `hub-home`, `hub-home-mobile` | None blocking. |
| 2.3 Market list | Yes | `market-list` | Disclaimer BEM rename (F-01). |
| 2.4 Market detail | Yes | `market-detail` | Range label 30 vs 28 days (F-02). |
| 2.5 Search | Yes | `search-results`, `search-nomatch` | Search row aggregates (F-04). |
| 2.6 Community | Yes | `community` feed-less | B-delta stale “feed” line (F-06). |
| 2.7 About | Yes | `about-tiers` | None blocking. |
| 2.8 Account | Yes (new template + controller) | `account`, `account-profile` | Route/controller named; `/account` 404 until built (expected). |

§2 names exact routes, PHP templates, controllers, `data-screen-label` frames, and component families. Shared partials listed; `prov_table` / `tier_badge` reuse confirmed in repo. New macros (`module_tile`, `freshness_pill`) are named with §9a logic for freshness — sufficient for implementation.

**Dependency:** `depends_on: SFA-S003-P004-WP-CB-UI-ALIGN`. ALIGN L-GATE_S + L-GATE_V **PASS** (`_COMMUNICATION/TEAM_190/SFA-S003-P004/WP-CB-UI-ALIGN/`). Class B shell hooks (`.sh__search`, 4th mobile tab, `.sh__foot`) extend ALIGN’s `.sh` contract; no missing ALIGN hook blocks Class B.

---

### C2 — Data fidelity (existing code vs new code)

**PASS**

| Claim (LOD400 §3) | Verified | Location |
|-------------------|----------|----------|
| `fetchHistory(28)` | Yes | `MarketViewController::detail` L75; private `fetchHistory` L184–201 |
| `/api/v1/market/{slug}/history` | Yes | `routes.php` L59; `productHistoryApi` L94–109; `MarketHistoryTest.php` |
| Market aggregates (min/median/max/sources) | Yes | `fetchAggregatesAll()` L278–308; `mapProductRow` L218–251 |
| `HubController::search` (crops + products LIKE) | Yes | `HubController.php` L47–108 |
| `POST /api/v1/contribute` | Yes | `AssumptionsController::contribute` L115–154; `routes.php` L63 |
| `Modules::all()` hub/tiers | Yes | `HubController::home`/`tiers`; `ModulesController` |
| **Only new server code** | Yes | No `AccountController`; no `/account` route in `routes.php` — matches spec (visual shell only). |

No hidden Python/migration/schema requirement for the seven surfaces. REGISTER entry SRV-4 documents empty mirror prices as data/OPS, not UI scope (LOD400 §8).

**Note (MINOR F-03):** §3 “`.reqchip` adds a `kind` value” vs endpoint accepting only `kind=request-info` — see findings.

---

### C3 — Honest-data rule (§4 + §9)

**PASS_WITH_FINDINGS**

- §4 binding: structure from Board-B; values from code; empty/stale/disabled states named (`.pcard.is-empty`, `.emptybox`, `.srch-nomatch`, disabled `.rangesel` 90/year).
- §9 #3: 7 + 28 live; 90 + year **disabled** with “בקרוב” — never fabricated series.
- §9a: freshness pill + unit display table grounded on `freshness_days` + `unit` — matches ingest (`sfa_ingest_push.py` L563 area) and product SELECT in `MarketViewController`.

**Risk:** `HubController::search` sets `price_median/min/max = price` and `source_count = 0` for product hits (L88–94). Reskin must obey §4 (show single price or empty, not fake range/sources) — F-04.

---

### C4 — team_00 decisions §9 + §9a

**PASS**

| # | Decision | Encoded in LOD400? |
|---|----------|-------------------|
| Q1 | Community feed-less | §9.1, AC-6, §8 — manifesto + `.reqcard` only |
| Q2 | Account UI shell + “בקרוב” | §9.2, AC-6, §8 — no auth backend |
| Q3 | Graph 7+28 live; 90/year disabled | §9.3, AC-3 |
| Q4 | Search client-side only; server ideas → register | §9.4, REGISTER `SFA-S003-P004-WP-SRV-IDEAS` |
| Q5 | Units + freshness | §9.5 → §9a table (locked) |

---

### C5 — Server-side guardrail

**PASS**

- LOD400 §9 #4: STOP + log to `SFA-S003-P004-WP-SRV-IDEAS`, never implement in this WP.
- Register exists: `_aos/work_packages/S003/SFA-S003-P004-WP-SRV-IDEAS/REGISTER.md` with PROPOSED entries (search index, 90d graph, auth, ingest data).
- Rule for team_10/50 restated in register § “Rule for the build”.

---

### C6 — Constitutional (delivery-tier only)

**PASS**

- Scope: `sfa_delivery/` templates, controllers, `public_assets` only; §8 excludes backend/migrations/crop-book/calculator redesign.
- No LOCKED Python/migration edits required.
- Palette: `HANDOFF/design/tokens.css` sha256 `17e7719f5a94ba35fb5e2570ad9be955367bb81a3e9457df016aa315b52dded2` — matches intake manifest “byte-identical to v1”.
- `classb.css` 42 711 bytes; `classb.js` 1 385 bytes — matches handoff README scale.

---

### C7 — AC testability (incl. VISUAL fidelity)

**PASS**

| AC | Objectively verifiable? |
|----|-------------------------|
| AC-1 | Yes — asset paths, load order (`cropbook-v1.js` before `classb.js`) |
| AC-2 | Yes — **design-vs-live screenshot pair per surface, desktop + mobile** (closes prior QA gap) |
| AC-3 | Yes — disclaimer presence, aud toggle, 3-state freshness, graph/rangesel, empty cards |
| AC-4 | Yes — hub grid, tiers, `.is-soon`, manifest, audience cards |
| AC-5 | Yes — grouped results, `<mark>`, nomatch + CTA |
| AC-6 | Yes — feed-less community, 5 tiers, account shells + “בקרוב” |
| AC-7 | Yes — `composer test`, `validate_aos` 0 FAIL, routes 200, RTL, no raw keys |

---

## 3. Findings (MINOR — non-blocking)

### F-190-CLASSB-01 — Disclaimer BEM: `.mk-disclaimer` → `.mkt-disc`

**Where:** LOD400 §2.3–2.4 vs served `macros/market_disclaimer.php` (`.mk-disclaimer`) vs design `classb.css` (`.mkt-disc`).

**Fix for team_10:** Reskin macro markup/classes to `.mkt-disc*` per Board-B; **preserve team_00 LOCKED Hebrew bullet copy** from existing macro (4 bullets including 7-day OMA window). QA grep both class names during transition.

---

### F-190-CLASSB-02 — Range selector label: board “30 י” vs spec 28-day API

**Where:** Board-B `rangesel` button text “30 י”; LOD400 §9 #3 wires **28-day** history; API default `days=28`.

**Fix:** Implement active control as **28י** (or equivalent Hebrew) mapped to `fetchHistory(28)` / `?days=28`. Do not imply 30-day data exists.

---

### F-190-CLASSB-03 — `.reqchip` kinds vs `contribute` API

**Where:** LOD400 §3 community; Board-B five chips; `AssumptionsController::contribute` accepts only `kind=request-info` (L127–130).

**Fix:** UI may show multiple chips; **POST body stays `kind=request-info`** with chip intent encoded in `field_name` / message fields, OR builder files SRV register row before any kind expansion. Do not extend API inside this WP.

---

### F-190-CLASSB-04 — Search product row shim vs §4 honest-data

**Where:** `HubController::search` L88–94 duplicates current price into min/median/max with `source_count=0`.

**Fix:** Class B `.srow` must not render fake ranges/source counts; use price-only or empty state per §9a “no price row” row.

---

### F-190-CLASSB-05 — `.rangesel` disabled behavior not in `classb.js`

**Where:** `classb.js` `wireRangeSel` toggles all buttons; §9 #3 requires 90/year `.is-disabled` + “בקרוב”.

**Fix:** Mark non-live buttons disabled in PHP template; optionally guard clicks in JS. Disabled buttons must not fetch fabricated history (REGISTER SRV-2).

---

### F-190-CLASSB-06 — B-delta route table still mentions community feed

**Where:** `B_COMPONENTS-TEMPLATES-classb-delta.md` routes row “Contact + feed”.

**Fix:** **LOD400 §9.1 supersedes** — remove feed from `community.php` reskin; ignore stale B-delta prose when it conflicts with locked LOD400.

---

### F-190-CLASSB-07 — `_layout.php` asset chain for Class B

**Where:** AC-1; current `_layout.php` loads hub/community CSS, gates `crop-book-v1.js` to crop-book/calc only (L68–69).

**Fix:** Add `classb.css` + load `cropbook-v1.js` then `classb.js` on Class B routes (`/`, `/market/*`, `/search`, `/community`, `/about`, `/account`). Extend `$asset_ver` foreach to include `classb.css` mtime.

---

## 4. Design SSoT integrity (team_35 HANDOFF)

| Check | Result |
|-------|--------|
| Board-B present | PASS — `design/Board-B-Hub-Market-Search-Community-About-Account.html` |
| `classb.css` / `classb.js` | PASS — 42 711 B / 1 385 B |
| B-delta §30–42 + routes | PASS |
| Intake manifest | PASS — tokens byte-identical claim spot-checked (sha256 prefix `17e7719f…`) |
| Community feed-less in design | PASS — board uses `.comm-manifest` + `.reqcard`; no feed grid in Class B frames |

---

## 5. Check summary

| Check ID | Result |
|----------|--------|
| C1 Precision | PASS_WITH_FINDINGS |
| C2 Data fidelity | PASS |
| C3 Honest-data | PASS_WITH_FINDINGS |
| C4 team_00 §9 + §9a | PASS |
| C5 Server guardrail | PASS |
| C6 Constitutional | PASS |
| C7 AC testability | PASS |

---

## 6. Decision

**PASS_WITH_FINDINGS** — 0 blockers, 0 major, 7 minor.

team_100: dispatch team_10 on branch integrating WP-CB-UI-ALIGN shell + this LOD400. team_50: plan AC-2 visual matrix (7 surfaces × desktop/mobile) before L-GATE_V.

*Issued by team_190 · 2026-06-02 · Cursor / Composer (non-Claude) per IR#1/#5.*
