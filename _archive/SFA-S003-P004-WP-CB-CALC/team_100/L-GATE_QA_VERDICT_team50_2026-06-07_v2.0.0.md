---
id: L-GATE_QA_VERDICT_SFA-S003-P004-WP-CB-CALC_team50_v2.0.0
from: team_50
to: team_100
cc:
  - team_00
  - team_10
  - team_190
date: 2026-06-07
gate: L-GATE_QA (FULL — 14/15 live goals)
wp: SFA-S003-P004-WP-CB-CALC
mandate: SFA-S003-P004-WP-CB-CALC-QA-FULL (team_100 → team_50, 2026-06-07)
supersedes: L-GATE_QA_VERDICT_team50_2026-06-07_v1.0.0 (B-now)
branch: claude/cb-calc-ui-2026-06-07
head: 5794a67
validator_engine: Cursor / Composer (non-Claude)
builder_engine: Claude Code (Opus)
result: PASS
blockers: 0
major: 0
minor: 3
---

# L-GATE QA Verdict v2.0.0 — WP-CB-CALC (FULL 14/15 live)

## §0 Executive verdict

| Field | Value |
|-------|--------|
| **Gate** | L-GATE_QA — FULL post-implementation visual + functional |
| **Branch** | `claude/cb-calc-ui-2026-06-07` @ `5794a67` |
| **Result** | **PASS** |
| **Blockers** | 0 |
| **Disposition** | **Merge to `main` + deploy authorized** for team_100 + team_00. F-02/F-03/F-04 ride the UI-redesign CSS pass — not merge blockers. |

**Bottom line:** All 14 live calculator goals compute correctly on an enriched local DB. B-now regressions hold. **F-01 (revenue quantity-first) is FIXED.** Five newly-live goals (#3 nursery, #6 succession, #11 frost, #13 compare, #14 seed_cost) pass functional checks. Zero JS console errors. `qa_probe.mjs` PASS. PHPUnit **224/224**. `validate_aos.sh` **0 FAIL**.

---

## 1. Environment

| Check | Result |
|-------|--------|
| Branch | `claude/cb-calc-ui-2026-06-07` — ✅ checked out locally |
| PHP | 8.5.6 — ✅ |
| PHPUnit (`sfa_delivery`) | **224/224 PASS** — ✅ |
| `validate_aos.sh` | **30 PASS / 21 SKIP / 0 FAIL** — ✅ |
| Local QA host | `127.0.0.1:8796` — SQLite mirror (lettuce + tomato enriched; potato bare; cucumber/pepper for basket) |
| Production deploy | ❌ not tested (branch not deployed; mandate scope = local enriched DB) |

---

## 2. Acceptance checks (mandate §2)

| # | Requirement | Result | Evidence |
|---|-------------|--------|----------|
| AC-1 | B-now re-verify: 15-goal grid; **15 מטרות**; #13 **השוואת גידולים**; sow #4; harvest #5; honest states; no console errors | **PASS** | `goalCount=15`; `header15`; `noProfitLabel`; `sowDateOk`; `harvestOk`; `potatoSoon`; `consoleErrors=[]` |
| AC-2 | **F-01 FIXED:** #9 yield (ק״ג) primary; ₪ secondary illustrative line | **PASS** | `revenueHtml`: `90 <small>ק״ג</small>` + `שווי משוער 1,080 ₪ · מדד השוק · להמחשה` |
| AC-3 | #6 succession: sow date + count → N sowing dates; interval = round(hw/7) | **PASS** | 4 dates @ 3-week steps (hw=21→3w): 01/03, 22/03, 12/04, 03/05/2026 |
| AC-4 | #14 seed_cost: ₪/g OR pack → cost; no price → honest prompt | **PASS_WITH_FINDINGS** | With price: `0.03 ₪`; without: `#qb-answer-big` = `—` (formula `הזינו מחיר…` in engine only — F-04) |
| AC-5 | #11 frost: region picker; frost_free → open note; else range | **PASS** | Coastal: `ללא קרה משמעותית`; Judean hills: `11/03/2026 – 01/10/2026` |
| AC-6 | #3 nursery: field-set date + seedlings → trays + tray-sow | **PASS** | `5 מגשי משתלה` · tray sow `18/03/2026` (480 seedlings, 28d nursery) |
| AC-7 | #13 compare: basket 2–6 crops; rank by ק״ג/מ׳; ₪/מ׳ secondary; single-crop hidden | **PASS** | Tomato #1 (9.0 ק״ג/מ׳); cucumber #2; pepper #3; `[data-goal-hide="compare"]` hides `#qb-crop` |
| AC-8 | Quantity-first integrity #9 + #13 | **PASS** | Revenue kg headline; compare ranks kg/m before ₪/m |
| AC-9 | Session + export + assumptions editor | **PASS** | 12 session rows accumulated; export href populated with `rows[…]`; `#qb-assum-editor` opens |
| AC-10 | Region picker from `frost_regions.json`; default coastal | **PASS** | 5 regions + placeholder; `regionVal=coastal` after async load |
| AC-11 | No JS console errors; `qa_probe.mjs` PASS | **PASS** | CDP hook: 0 errors; qa_probe overflow PASS mobile+desktop |
| AC-12 | PHPUnit 224/224; validate_aos 0 FAIL | **PASS** | See §1 |
| AC-13 | water #0 shows בפיתוח — not a defect | **PASS** | `waterSoon=true` |

**Live goal set (14/15):** `beds, compare, fert, frost, harvest, nursery, pop, revenue, seed, seed_cost, sow_date, succession, transplants, yield` — matches mandate.

**Intentional deferred (1):** `water` (#0) — `soon`; not a defect.

---

## 3. Test matrix

| Test ID | Name | Result | Weight |
|---------|------|--------|--------|
| T01 | Goal catalog (15 + relabels + 14 live) | ✅ PASS | Critical |
| T02 | Date #4 sow (transplant tomato) | ✅ PASS | Critical |
| T03 | Date #5 harvest range (parity) | ✅ PASS | Critical |
| T04 | Nodata crop (potato) | ✅ PASS | Critical |
| T05 | #6 succession list | ✅ PASS | Critical |
| T06 | #14 seed_cost (with + without price) | 🟡 PASS_WITH_FINDINGS | Critical |
| T07 | #11 frost (frost_free + range) | ✅ PASS | Critical |
| T08 | #3 nursery trays + tray-sow | ✅ PASS | Critical |
| T09 | #13 compare basket rank | ✅ PASS | Critical |
| T10 | F-01 revenue quantity-first | ✅ PASS | Critical |
| T11 | Scalar regression (transplants → 480) | ✅ PASS | High |
| T12 | Session + export | ✅ PASS | High |
| T13 | Assumptions editor | ✅ PASS | Medium |
| T14 | Console errors | ✅ PASS | Critical |
| T15 | qa_probe overflow + forbidden text | ✅ PASS | High |
| T16 | PHPUnit + validate_aos | ✅ PASS | Critical |

**Score:** 15/16 pass outright; 1 conditional (F-04 copy placement). **Critical failures: 0.**

---

## 4. Findings

| ID | Severity | Finding | Blocking? | Route |
|----|----------|---------|-----------|-------|
| **F-01** | ~~Major~~ | **CLOSED.** #9 revenue now quantity-first (kg headline, ₪ secondary). | — | — |
| **F-02** | Minor | Nodata uses shared «מחשבון זה בפיתוח» card for `soon` + `nodata`. Functionally honest. | No | WP-CB-UI-REDESIGN |
| **F-03** | Minor | Date/range/list/rank results are plain formatted text (no `.r-date`/`.r-range`/`.r-list`/`.r-rank` cards). Expected per mandate scope caveats. | No | WP-CB-UI-REDESIGN |
| **F-04** | Minor | #14 seed_cost without price: `#qb-answer-big` shows `—`; prompt copy `הזינו מחיר זרעים…` lives in hidden `#qb-engine [data-formula]` only. Honest (no fabricated ₪) but less explicit than mandate copy target. | No | WP-CB-UI-REDESIGN typed render |

---

## 5. Evidence

**Path:** `_COMMUNICATION/TEAM_100/SFA-S003-P004-WP-CB-CALC/evidence_2026-06-07/`

- `qa_probe_result.json` — **PASS** (mobile + desktop; title `מחשבון · SFA`; `רווח גולמי` absent)
- `functional_probe.json` — CDP functional run (all goal checks)
- `screenshots/_calc__mobile.png`, `screenshots/_calc__desktop.png`

**CDP functional excerpt (2026-06-07, local `8796`):**

```
sowDateTomato: 12/05/2026 (target 2026-09-15, 91d + 35d nursery)
harvestRangeTomato: 15/09/2026 – 27/10/2026
potatoNodata: soon card (no fabricated date)
succession: 4 dates · 3-week interval (hw=21)
seedCost: 0.03 ₪ with price; — without (F-04)
frostCoastal: «ללא קרה משמעותית»
frostJudean: 11/03/2026 – 01/10/2026
nursery: 5 trays · tray sow 18/03/2026
revenue: 90 ק״ג + «שווי משוער 1,080 ₪ · מדד השוק · להמחשה»
compare: tomato 9.0 ק״ג/מ׳ #1 · cucumber #2 · pepper #3
transplants: 480 שתילים
export: rows[…] populated (12 calculations)
regionDefault: coastal (5 regions loaded)
consoleErrors: []
```

PHPUnit excerpt: `Tests: 224, Assertions: 692 — OK`

---

## 6. Gate decision

### ✅ L-GATE_QA — PASS

Gate is **closed**. team_100 + team_00 may **merge `claude/cb-calc-ui-2026-06-07` to `main` and deploy**.

| Condition | Owner | Due |
|-----------|-------|-----|
| C-01 — Merge + deploy branch to production | team_00 + team_100 | Immediate |
| C-02 — F-02/F-03/F-04 styled typed render + copy polish | team_10 + UI-redesign | WP-CB-UI-REDESIGN slice |

**Not required for merge:** F-02, F-03, F-04 (documented deferrals / cosmetic copy placement).

---

## 7. Required actions

| Team | Action | Priority |
|------|--------|----------|
| team_100 | Acknowledge PASS; authorize merge | HIGH |
| team_00 | Merge to `main` + deploy (`scripts/ftp_deploy_sfa_ui.sh`) | HIGH |
| team_10 | No pre-merge code fixes required | — |
| team_190 | L-GATE_D / constitutional validation on merged main (if scheduled) | MEDIUM |

---

## 8. Cross-engine note (IR#1 / IR#5)

| Role | Engine |
|------|--------|
| Builder | Claude Code (Opus) — branch `claude/cb-calc-ui-2026-06-07` |
| QA verdict (this document) | Cursor / Composer — **non-Claude** |

---

*Filed by: Team 50 (QA)*  
*Date: 2026-06-07*  
*Mandate: `_COMMUNICATION/TEAM_50/MANDATE_QA_WP-CB-CALC_full_2026-06-07.md`*
