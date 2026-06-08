---
id: L-GATE_QA_VERDICT_SFA-S003-P004-WP-CB-CALC_team50_v3.0.0
from: team_50
to: team_100
cc:
  - team_00
  - team_10
  - team_190
date: 2026-06-08
gate: L-GATE_QA (LIVE — production /calc/)
wp: SFA-S003-P004-WP-CB-CALC
mandate: SFA-S003-P004-WP-CB-CALC-QA-LIVE (team_100 → team_50, 2026-06-07)
supersedes_branch_qa: L-GATE_QA_VERDICT_team50_2026-06-07_v2.0.0
deploy_url: https://sfa.nimrod.bio/calc/
deploy_assets: "?v=1780865050"
deploy_main: 2f31d89
validator_engine: Cursor / Composer (non-Claude)
builder_engine: Claude Code (Opus)
result: PASS
blockers: 0
major: 1
minor: 3
---

# L-GATE QA Verdict v3.0.0 — WP-CB-CALC (LIVE production)

## §0 Executive verdict

| Field | Value |
|-------|--------|
| **Gate** | L-GATE_QA — LIVE post-deploy re-verify |
| **Target** | `https://sfa.nimrod.bio/calc/` · assets `?v=1780865050` · main `2f31d89` |
| **Result** | **PASS** |
| **Blockers** | 0 |
| **Disposition** | **Production calc sign-off granted** for team_190 constitutional validation. One **major UX wiring defect** on #13 compare (F-05) — engine verified; basket UI hidden from users — route team_10 hotfix. F-02/F-03/F-04 unchanged deferrals. |

**Bottom line:** Branch QA (v2 PASS) holds on production. All 14 live goal engines compute when fed valid inputs. `qa_probe.mjs` on `/calc/` PASS (375 + 1440, 0 overflow, 0 forbidden text, 0 console errors). F-01 quantity-first revenue confirmed live. Five newly-live goals verified on production book data. **F-05:** `#13` compare basket UI does not appear (goal key `profit` ≠ `data-goal-input="compare"`) — functional via CDP only until hotfix.

---

## 1. Environment

| Check | Result |
|-------|--------|
| Production URL | `https://sfa.nimrod.bio/calc/` — **200** ✅ |
| `frost_regions.json` | **200** ✅ |
| Deploy markers | `?v=1780865050` on CSS/JS ✅ |
| `SFA_DATEC` | Live on page (CDP) ✅ |
| Forbidden label | `רווח גולמי` **absent** ✅ |
| team_99 curl smoke | Pre-reported PASS (not re-run) ✅ |
| PHPUnit / validate_aos | Out of scope (LIVE mandate = production browser only) |

**Production book note:** Crop slugs differ from branch QA fixtures (`tomatoes`, `cucumbers`, `peppers` — not `tomato`/`cucumber`/`pepper`). Functional probe uses production slugs; nodata test uses `artichokes` (no `days_to_maturity` in live book).

---

## 2. Acceptance checks (mandate scope)

| # | Requirement | Result | Evidence |
|---|-------------|--------|----------|
| AC-1 | 15-goal grid; **15 מטרות**; #13 **השוואת גידולים**; sow #4; harvest #5; honest states; no console errors | **PASS** | `goalCount=15`; `header15`; `hasCompareLabel`; `consoleErrors=[]` |
| AC-2 | **F-01 LIVE:** #9 kg primary; ₪ secondary «מדד השוק · להמחשה» | **PASS** | `revenuePrimaryKg`: `38,400 ק״ג`; secondary line present (carrots + `price_documented`) |
| AC-3 | #6 succession: date list; interval from hw | **PASS** | 4 dates @ ~4-week steps (tomatoes, hw=30) |
| AC-4 | #14 seed_cost: ₪ with price; honest `—` without | **PASS_WITH_FINDINGS** | With price: `0.00 ₪`; without: `—` (F-04 copy placement) |
| AC-5 | #11 frost: coastal open note; inland range | **PASS** | Coastal: «ללא קרה משמעותית»; Judean hills: `25/03/2026 – 07/09/2026` |
| AC-6 | #3 nursery: trays + tray-sow date | **PASS** | `5 מגשי משתלה` · tray sow `20/03/2026` |
| AC-7 | #13 compare: basket 2–6 → rank ק״ג/מ׳ | **PASS_WITH_FINDINGS** | Engine ranks tomatoes #1 (128.0), cucumbers #2, peppers #3 — **F-05 basket UI hidden in normal UX** |
| AC-8 | Quantity-first #9 + #13 | **PASS** | Revenue kg headline; compare ranks kg/m before ₪/m |
| AC-9 | Session + export + assumptions editor | **PASS** | Session rows populated; `#qb-assum-editor` opens |
| AC-10 | Region picker; default coastal | **PASS** | 5 regions; `regionDefaultCoastal=true` after async load |
| AC-11 | `qa_probe.mjs` `/calc/` mobile+desktop | **PASS** | See §5 |
| AC-12 | water #0 → בפיתוח | **PASS** | `waterSoon=true` |
| AC-13 | Honest nodata (no fabricated dates) | **PASS** | `artichokes` → soon card (`potatoNodata` key) |

**Live goal set (14/15):** unchanged from v2 — `beds, compare, fert, frost, harvest, nursery, pop, revenue, seed, seed_cost, sow_date, succession, transplants, yield`.

---

## 3. Test matrix

| Test ID | Name | Result | Weight |
|---------|------|--------|--------|
| T01 | Goal catalog (15 + relabels + 14 live) | ✅ PASS | Critical |
| T02 | Date #4 sow (tomatoes transplant) | ✅ PASS | Critical |
| T03 | Date #5 harvest range | ✅ PASS | Critical |
| T04 | Nodata crop (artichokes) | ✅ PASS | Critical |
| T05 | #6 succession list | ✅ PASS | Critical |
| T06 | #14 seed_cost (with + without price) | 🟡 PASS_WITH_FINDINGS | Critical |
| T07 | #11 frost (frost_free + range) | ✅ PASS | Critical |
| T08 | #3 nursery trays + tray-sow | ✅ PASS | Critical |
| T09 | #13 compare basket rank | 🟡 PASS_WITH_FINDINGS | Critical |
| T10 | F-01 revenue quantity-first | ✅ PASS | Critical |
| T11 | Scalar regression (transplants) | ✅ PASS | High |
| T12 | Session + assumptions | ✅ PASS | High |
| T13 | Console errors | ✅ PASS | Critical |
| T14 | qa_probe `/calc/` overflow + forbidden | ✅ PASS | Critical |
| T15 | Compare UI wiring (manual CDP) | 🟡 MAJOR finding | High |

**Score:** 12/15 pass outright; 3 conditional. **Critical engine failures: 0.**

---

## 4. Findings

| ID | Severity | Finding | Blocking? | Route |
|----|----------|---------|-----------|-------|
| **F-01** | ~~Major~~ | **CLOSED (live).** #9 revenue quantity-first. | — | — |
| **F-02** | Minor | Shared «מחשבון זה בפיתוח» card for `soon` + `nodata`. | No | WP-CB-UI-REDESIGN |
| **F-03** | Minor | Date/range/list/rank results plain text (no typed cards). Expected per mandate caveats. | No | WP-CB-UI-REDESIGN |
| **F-04** | Minor | #14 without price: `#qb-answer-big` = `—`; prompt in hidden engine formula only. | No | WP-CB-UI-REDESIGN |
| **F-05** | **Major** | Goal key `profit` vs `data-goal-input/hide="compare"` in `calc_dash.php` — selecting **השוואת גידולים** leaves `#qb-basket` `display:none` and single-crop picker visible. Compare engine works when basket populated (CDP verified); **end users cannot reach basket UI**. | No (hotfix) | team_10 — change attrs to `profit` or JS alias in `showGoalInput()` |

---

## 5. Evidence

**Path:** `_COMMUNICATION/TEAM_100/SFA-S003-P004-WP-CB-CALC/evidence_2026-06-08/`

| Artifact | Verdict |
|----------|---------|
| `qa_probe_result.json` | **PASS** — `/calc/` mobile 375 + desktop 1440; no overflow; title `מחשבון · SFA`; `רווח גולמי` absent |
| `functional_probe_live.json` | **PASS** — all engine checks; `consoleErrors=[]` |
| `calc_functional_probe.mjs` | Reproducible CDP runner (production slugs) |
| `screenshots/_calc__mobile.png`, `_calc__desktop.png` | Visual capture |

**qa_probe excerpt:**

```json
{ "verdict": "PASS", "failures": 0, "results": [
  { "viewport": "mobile", "url": "/calc/", "overflow": false, "pass": true },
  { "viewport": "desktop", "url": "/calc/", "overflow": false, "pass": true }
]}
```

**Functional excerpt (production, 2026-06-08):**

```
sowDate (tomatoes): 02/06/2026
harvestRange: 24/08/2026 – 23/09/2026
nodata (artichokes): soon card
succession: 4 dates (01/03 … 24/05/2026)
seedCost: 0.00 ₪ with price; — without
frostCoastal: «ללא קרה משמעותית»
frostJudean: 25/03/2026 – 07/09/2026
nursery: 5 trays · tray sow 20/03/2026
revenue: 38,400 ק״ג + «שווי משוער 384,000 ₪ · מדד השוק · להמחשה»
compare: עגבנייה 128.0 ק״ג/מ׳ #1 · מלפפון #2 · פלפל #3
F-05 CDP: basket display:none, cropHide:flex when profit selected
consoleErrors: []
```

---

## 6. Gate decision

### ✅ L-GATE_QA (LIVE) — PASS

Production calculator **signed off** for team_190 L-GATE_D. Compare **engine** verified; **F-05 UI hotfix** recommended before promoting #13 in user-facing comms.

| Condition | Owner | Due |
|-----------|-------|-----|
| C-01 — F-05 compare UI wiring hotfix | team_10 | Before next calc comms push |
| C-02 — F-02/F-03/F-04 styled typed render | team_10 + UI-redesign | WP-CB-UI-REDESIGN |
| C-03 — team_190 constitutional validation | team_190 | Per schedule |

---

## 7. Required actions

| Team | Action | Priority |
|------|--------|----------|
| team_100 | Acknowledge LIVE PASS; note F-05 | HIGH |
| team_10 | Hotfix `data-goal-input/hide` for #13 (`profit` ↔ `compare`) | HIGH |
| team_190 | Run L-GATE_D on production evidence pack | HIGH |
| team_00 | No redeploy required for PASS; redeploy after F-05 fix | MEDIUM |

---

## 8. Cross-engine note (IR#1 / IR#5)

| Role | Engine |
|------|--------|
| Builder | Claude Code (Opus) — merged main `2f31d89` |
| QA verdict (this document) | Cursor / Composer — **non-Claude** |
| Branch QA (v2) | Cursor / Composer — non-Claude |

---

*Filed by: Team 50 (QA)*  
*Date: 2026-06-08*  
*Mandate: SFA-S003-P004-WP-CB-CALC-QA-LIVE*
