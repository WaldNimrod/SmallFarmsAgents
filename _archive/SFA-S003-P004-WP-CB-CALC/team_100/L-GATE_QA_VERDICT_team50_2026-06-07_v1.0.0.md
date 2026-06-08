---
id: L-GATE_QA_VERDICT_SFA-S003-P004-WP-CB-CALC_team50_v1.0.0
from: team_50
to: team_100
cc:
  - team_00
  - team_10
  - team_190
date: 2026-06-07
gate: L-GATE_QA (post-implementation visual + functional)
wp: SFA-S003-P004-WP-CB-CALC
mandate: SFA-S003-P004-WP-CB-CALC-QA-BNOW (team_100 → team_50, 2026-06-07)
branch: claude/cb-calc-ui-2026-06-07
head: e330e16
validator_engine: Cursor / Composer (non-Claude)
builder_engine: Claude Code (Opus)
result: PASS_WITH_FINDINGS
blockers: 0
major: 1
minor: 2
---

# L-GATE QA Verdict v1.0.0 — WP-CB-CALC (Phase A + B-now)

## §0 Executive verdict

| Field | Value |
|-------|--------|
| **Gate** | L-GATE_QA — post-implementation visual + functional (deferred from L-GATE_D) |
| **Branch** | `claude/cb-calc-ui-2026-06-07` @ `e330e16` |
| **Result** | **PASS_WITH_FINDINGS** |
| **Blockers** | 0 |
| **Disposition** | B-now date-goal **in-browser integration is sound** (correct dates, honest states, no JS crashes). team_100 may proceed to remaining input-bearing goals **and** merge planning with team_00, **after** addressing F-01 (revenue quantity-first display) — either in the UI-redesign typed-render slice or a small pre-merge patch. |

**Bottom line:** The 9/15 live goal set behaves correctly in the calculator builder. Date goals (#4 sow, #5 harvest window) compute with parity-verified math and render as plain LTR text (styled cards correctly deferred). One **functional** gap remains on #9 revenue hierarchy (₪ is primary, not secondary). No-data crops get an honest non-numeric state (shared “בפיתוח” card — dedicated `.r-nodata` copy deferred to UI-redesign).

---

## 1. Environment

| Check | Result |
|-------|--------|
| Branch | `claude/cb-calc-ui-2026-06-07` — ✅ checked out locally |
| PHP | 8.5.6 — ✅ |
| PHPUnit (`sfa_delivery`) | **223/223 PASS** — ✅ |
| Local QA host | `127.0.0.1:8796` — SQLite crop_book mirror (lettuce + tomato enriched; potato bare) + `.env.qa` |
| Production deploy | ❌ not tested (branch not deployed; mandate scope = local enriched DB) |
| `validate_aos.sh` | Not re-run this session (L-GATE_D: 0 FAIL) |

---

## 2. Acceptance checks (mandate §2)

| # | Requirement | Result | Evidence |
|---|-------------|--------|----------|
| AC-1 | Page loads; 15-goal grid; header **15 מטרות**; #13 **השוואת גידולים** (not רווח גולמי) | **PASS** | `data-calc-goals` count=15; header + dropdown label; `רווח גולמי` absent (`qa_probe --absent`) |
| AC-2 | Date goals compute for enriched crop (lettuce/tomato); dd/mm/yyyy LTR; anchor defaults | **PASS** | Tomato transplant: sow `12/05/2026` (target 15/09/2026 − 91d − 35d nursery); harvest `15/09/2026 – 27/10/2026` (parity anchor); `<span dir="ltr">` wrapper |
| AC-3 | Honest states: no-date crop → no guess; unbuilt goal → בפיתוח | **PASS_WITH_FINDINGS** | Potato + sow_date → `#qb-soon` shown, no fabricated date (F-02: copy is shared “בפיתוח”, not dedicated nodata string) |
| AC-4 | Quantity-first: #9 revenue shows ₪ as **secondary** line | **FAIL → F-01** | `#qb-answer-big` = `1,080 ₪` primary; yield `90 ק״ג` only in hidden `#qb-engine [data-extra]` |
| AC-5 | Session + export + assumptions editor | **PASS** | Session accumulated 4+ rows; export hrefs populated with `rows[…]` on click; `#qb-assum-editor` opens |
| AC-6 | No JS console errors on load / goal switch | **PASS** | CDP `console.error` hook: 0 errors across 9 goal switches |

**Live goal set (9/15):** `beds, fert, harvest, pop, revenue, seed, sow_date, transplants, yield` — matches mandate.

**Intentional בקרוב (6):** frost, water, profit/compare, seed_cost, succession, nursery — all show `#qb-soon`; not defects.

---

## 3. Test matrix

| Test ID | Name | Result | Weight |
|---------|------|--------|--------|
| T01 | Goal catalog (15 + relabels) | ✅ PASS | Critical |
| T02 | Date #4 sow (transplant tomato) | ✅ PASS | Critical |
| T03 | Date #5 harvest range (parity) | ✅ PASS | Critical |
| T04 | Nodata crop (potato) | 🟡 PASS_WITH_FINDINGS | Critical |
| T05 | Soon goal (succession) | ✅ PASS | High |
| T06 | Scalar regression (transplants lettuce → 480) | ✅ PASS | High |
| T07 | Revenue quantity-first | ❌ FAIL | Critical |
| T08 | Session + export | ✅ PASS | High |
| T09 | Assumptions editor | ✅ PASS | Medium |
| T10 | Console errors | ✅ PASS | Critical |
| T11 | qa_probe overflow + forbidden text | ✅ PASS | High |
| T12 | PHPUnit suite | ✅ PASS | Critical |

**Score:** 10/12 pass outright; 1 conditional; 1 fail (F-01). **Critical failures for merge:** 0 blockers (F-01 is major, fix before or with UI-redesign deploy).

---

## 4. Findings

| ID | Severity | Finding | Blocking? | Route |
|----|----------|---------|-----------|-------|
| **F-01** | Major | **#9 revenue quantity-first violated.** `showResult()` surfaces `CALC.revenue` main (₪) in `#qb-answer-big`; `out.extra` yield (ק״ג) stays in hidden engine only. LOD400 §6 + mandate AC-4 require yield primary / ₪ secondary (even as plain text before `mock.css`). | No (pre-deploy fix) | team_10 — extend typed scalar branch in `showResult()` for `g.kind==='revenue'` (surface `extra` as secondary line) |
| **F-02** | Minor | **Nodata uses shared “מחשבון זה בפיתוח” card** (`calc_dash.php:229-232`) for both `soon` and `nodata`. Functionally honest (no 0/guess) but copy differs from mockup `.r-nodata` (“אין עדיין נתון לגידול הזה”). | No | Deferred to WP-CB-UI-REDESIGN typed shapes |
| **F-03** | Minor | **Date/range results are plain text** (no `.r-date`/`.r-range` cards). Expected per mandate scope caveats. | No | WP-CB-UI-REDESIGN |

---

## 5. Evidence

**Path:** `_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-CALC/evidence_2026-06-07/`

- `qa_probe_result.json` — overflow PASS mobile+desktop; `רווח גולמי` absent
- `_calc__mobile.png`, `_calc__desktop.png` — layout screenshots
- CDP functional run (2026-06-07, local `8796`):

```
sowDateTomato: 12/05/2026 (transplant tomato, target 2026-09-15)
harvestRangeTomato: 15/09/2026 – 27/10/2026
potatoNodata: true — «תאריך זריעה» לגידול זה (no fabricated date)
revenueHtml: "1,080 <small>₪</small>" — F-01
revenueExtra (hidden): "יבול 90 ק״ג"
transplants: "480 שתילים"
export: rows[…] populated after click (PDF + CSV)
```

PHPUnit excerpt: `Tests: 223, Assertions: 688 — OK`

---

## 6. Gate decision

### 🟡 L-GATE_QA — PASS_WITH_FINDINGS

Gate is **open** for continued build (remaining input-bearing goals) and merge **coordination** with team_00, subject to:

| Condition | Owner | Due |
|-----------|-------|-----|
| C-01 — Fix F-01 revenue display hierarchy (yield primary, ₪ secondary in `#qb-answer-big`) | team_10 | Before production deploy of this slice (may ship with UI-redesign typed render) |
| C-02 — F-02/F-03 nodata + card styling | team_10 + UI-redesign | WP-CB-UI-REDESIGN slice |

**Not required for merge to `main`:** F-02, F-03 (documented deferrals).

---

## 7. Required actions

| Team | Action | Priority |
|------|--------|----------|
| team_100 | Acknowledge verdict; route F-01 to team_10 (small `showResult` patch or fold into typed-render mandate) | HIGH |
| team_10 | Patch revenue secondary line **or** confirm fix in UI-redesign PR before deploy | HIGH |
| team_00 | Merge + deploy when team_100 signals F-01 disposition | MEDIUM |
| team_50 | Re-QA F-01 only after patch (no full re-run required) | LOW |

---

## 8. Cross-engine note (IR#1 / IR#5)

| Role | Engine |
|------|--------|
| Builder | Claude Code (Opus) — branch `claude/cb-calc-ui-2026-06-07` |
| QA verdict (this document) | Cursor / Composer — **non-Claude** |

---

*Filed by: Team 50 (QA)*  
*Date: 2026-06-07*  
*Mandate: `_COMMUNICATION/TEAM_50/MANDATE_QA_WP-CB-CALC_B-now_2026-06-07.md`*
