---
id: L-GATE_D_VERDICT_SFA-S003-P004-WP-CB-CALC_v1.0.0
from: team_190
to: team_100
cc:
  - team_00
  - team_10
  - team_35
  - team_50
date: 2026-06-07
gate: L-GATE_D
round: 1
wp:
  - SFA-S003-P004-WP-CB-CALC
  - SFA-S003-P004-WP-CB-CROPDATA-DATES
validation_request: SFA-S003-P004-WP-CB-CALC-VALREQ (team_100, 2026-06-07)
specs_under_review:
  - _aos/work_packages/S003/SFA-S003-P004-WP-CB-CALC/LOD400_spec.md
  - _aos/work_packages/S003/SFA-S003-P004-WP-CB-CROPDATA-DATES/LOD400_spec.md
  - _COMMUNICATION/team_100/SFA-S003-P004-WP-CB-CALC/LOD_DESIGN_2026-06-07_v1.0.0.md
branch: claude/cb-followups-2026-06-07
head: 4540625
staged_commits:
  - f491172  # Phase A transplants
  - 62b1e9a  # server plumbing
  - 6314a44  # SFA_DATEC date engine
validator_engine: Cursor / Composer (non-Claude)
builder_engine: Claude Code (Opus)
result: PASS_WITH_FINDINGS
blockers: 0
major: 0
minor: 3
residuals: 2
---

# L-GATE_D Verdict v1.0.0 — WP-CB-CALC + WP-CB-CROPDATA-DATES

## §0 Executive verdict

| Field | Value |
|-------|--------|
| **Gate** | L-GATE_D (design validation — pre-implementation) |
| **Specs** | LOD400 WP-CB-CALC + LOD400 WP-CB-CROPDATA-DATES + LOD_DESIGN 2026-06-07 |
| **Result** | **PASS_WITH_FINDINGS** |
| **Blockers** | 0 |
| **Disposition** | team_100 may resume implementation on **team_00 explicit go**. Staged increments on `claude/cb-followups-2026-06-07` are **validated as foundations**; merge remains gated on team_00 + coordination with the parallel UI_REDESIGN session. Full team_50 visual QA deferred until typed-result render + date-goal UI wiring land (per validation request §4). |

**Bottom line:** The design bundle is **decision-complete** and buildable without inventing product policy. team_00 decisions (§0 of LOD_DESIGN) are encoded in both LOD400 specs. The three staged commits correctly implement the **engine/server slice** (transplants live, date numerics + `SFA_CROP_BOOK_TXT`, `SFA_DATEC` parity module); presentation-layer work (typed `showResult`, 15th goal, relabels, B-now goal wiring) remains correctly **out of scope** for this gate and is the next build increment. Two **documented residuals** (#13 basket mockup, frost-region dates) do not block L-GATE_D.

---

## 1. Mandate compliance (validation request)

| Requirement | Result | Evidence |
|-------------|--------|----------|
| IR#1 / IR#5 — non-Claude binding verdict | **PASS** | Validator: Cursor / Composer. Spec author + builder: team_100 / Claude Opus. Cross-engine satisfied. |
| Read LOD400 ×2 + LOD_DESIGN + staged branch | **PASS** | Files read; branch `claude/cb-followups-2026-06-07` probed at `4540625`. |
| Constitutional checks (§3 of request) | **PASS** | See §3 below. |
| team_50 partial — mockup ↔ LOD400 mapping | **PASS_WITH_FINDINGS** | See §4 below; residual R-01 (#13 basket). |
| `validate_aos.sh` | **PASS** | 30 PASS / 21 SKIP / 0 FAIL (2026-06-07 session). |
| PHP suite (`sfa_delivery`, sqlite in-memory) | **PASS** | 221/221 via `phpunit -c phpunit.xml` (2026-06-07 session). |

---

## 2. L-GATE_D design checks

### D1 — Decision completeness (team_00 §0)

**PASS**

All seven team_00 decisions (2026-06-07) are reflected consistently across LOD_DESIGN §0, WP-CB-CALC LOD400 §1–§4, and WP-CB-CROPDATA-DATES LOD400 §1–§3:

- `water` (#0) split to `WP-CB-WATER` — stub retained, no fabricated numbers.
- #13 reframed quantity-first (`compare` / השוואת גידולים); no profit/margin wording in spec.
- #11 frost → region picker + static asset (B-later).
- #5 `harvest_window` → 15th goal (B-now).
- Date-data gap collapsed; succession **derived** `round(harvest_window_max_days/7)`; categoricals gated to `WP-CB-CROPDATA-DATES` for B-later only.
- Session → per-device `sessionStorage`.
- Guided classification tool + `both` planting_method value.

Phasing A → B-now → CROPDATA-DATES → B-later is unambiguous. No open product decisions block build.

### D2 — Buildability (zero-guessing for team_10)

**PASS_WITH_FINDINGS**

| Slice | Spec location | Implementation anchor in repo | Gap |
|-------|---------------|------------------------------|-----|
| Phase A ports | LOD400 §2 | `CALC.transplants` live (`crop-book-v1.js:55`); seed_cost/compare spec'd | seed_cost + compare not yet coded — expected |
| Server plumbing | LOD400 §5 / CROPDATA §4 | `HubController.php:147-199`, route tests `CropBookV1RouteTest.php:473-508` | **Landed** on branch |
| Date engine B0 | LOD400 §3.1 | `window.SFA_DATEC` (`crop-book-v1.js:152-209`) | Module landed; `runEngine()` not yet consuming — expected |
| Typed results | LOD400 §6 | Mockup DOM/classes in `calc.html` gallery | Render refactor not started — expected pre-go |
| B-now goals | LOD400 §3.2 | Mockup `G[]` registry (`calc.html:209-224`) | `calc_dash.php` still 14 goals, no `harvest` entry — expected |
| B-later goals | LOD400 §4 | CROPDATA-DATES LOD400 §3 | Correctly gated |
| CROPDATA tool | CROPDATA LOD400 §3 | `cropdata_entry.html` mockup exists | Tool not built — expected |

A builder can implement the remaining increments from LOD400 + mockups without relitigating team_00 policy.

### D3 — Staged increments (commits f491172, 62b1e9a, 6314a44)

**PASS**

| Increment | Claim | Verified |
|-----------|-------|----------|
| #2 transplants (6→7 live) | `f491172` | `calc_dash.php:66` `kind:'transplants','soon'=>false`; route test asserts 7 live kinds including `transplants` |
| Server plumbing | `62b1e9a` | Date numerics in whitelist; `crop_attribute` query; `window.SFA_CROP_BOOK_TXT` emitted; RICH route seed + graceful-degradation test |
| `SFA_DATEC` (#4/#5/#6) | `6314a44` | `DATEC.sowDate`, `harvestWindow`, `succession` mirror Python branches; `testDateEngineParityAnchors` anchors sow 16/06/2026, harvest 15/09→27/10, succession 5×2wk |

Parity literals match `calculators.py` `sowing_date_from_harvest` / `harvest_window_from_sowing` / `succession_schedule` semantics (direct-seed path; transplant branch includes `both` in `isTransplant`).

**Note:** Staged code does **not** yet wire date goals into the live builder UI — consistent with the validation request scope ("validate before further build").

### D4 — Product integrity ("no fabricated numbers")

**PASS**

- Honest no-data is first-class in LOD400 §6–§7 and mockup `.r-nodata`.
- `water` stays stubbed to separate WP.
- #13 primary metric is yield/m; ₪/m is secondary/illustrative.
- Server degrades gracefully when `crop_attribute` absent (route test 200, no TXT channel).

### D5 — IR#3 spec_ref integrity

**PASS**

All cited refs resolve to existing repo files (probed 2026-06-07): `calculators.py`, `assumptions.py`, `MANDATE_CALC_MOCKUPS_2026-06-07.md`, `MOCKUP_RETURN_team35_2026-06-07_v1.0.0.md`, `calc.html`, `cropdata_entry.html`, `mock.css`.

Roadmap `spec_ref` / `design_ref` for `SFA-S003-P004-WP-CB-CALC` point at the LOD400 + LOD_DESIGN paths above.

---

## 3. Constitutional checks (team_190)

| Check | Result | Evidence |
|-------|--------|----------|
| Directory authority | **PASS** | `git diff main...HEAD` — edits under `_COMMUNICATION/team_100|team_35/`, `_aos/roadmap.yaml`, `_aos/work_packages/S003/`, `sfa_delivery/`. **No** `_aos/governance/` edits. |
| IR#4 single-writer roadmap | **PASS** | Roadmap write authority documented as team_100; WP registrations for CB-CALC / CROPDATA-DATES / CB-WATER present at `_aos/roadmap.yaml` ~4567+. |
| IR#3 repo-internal spec_ref | **PASS** | See D5. |
| IR#7 API-only when DB online | **PASS** | No structured DB mutations in this session; CROPDATA-DATES LOD400 §3 mandates hub API writes for the guided tool. |
| IR#1 cross-engine | **PASS** | Builder ≠ validator (see §1). |

---

## 4. team_50 partial — mockup ↔ LOD400 mapping

**PASS_WITH_FINDINGS** (full visual QA correctly deferred)

| LOD400 §6 `type` | Mockup container | Mockup `G[]` / gallery | Match |
|------------------|------------------|------------------------|-------|
| `scalar` | `.r-scalar > .big/.lbl` | Goals 1,2,7,8,10,12 + gallery | ✅ |
| `scalar` + ₪ secondary | `.r-scalar > .second` | #9 revenue, #14 seed_cost | ✅ |
| `date` | `.r-date > .d/.anchor` | #4 sow_date | ✅ |
| `date_range` | `.r-range > .ends/.bar/.fill` | #5 harvest, #11 frost | ✅ |
| `date_list` | `.r-list > .item` | #6 succession | ✅ |
| `ranked_list` | `.r-rank > table` | #13 compare | ✅ (shape); **R-01** on step-2 UX |
| `scalar+date` | `.r-scalar` + `.second` date | #3 nursery | ✅ |
| `nodata` | `.r-nodata` | water + no-date crop demo | ✅ |

Builder contract elements present in `calc.html`: 15-goal grid with `.st.live/.soon/.dev`, 4-step ASK, live anchor (`anchorhint`, `datefld` opacity), goal-specific `.extra` panels, session rows, export row, assumptions link.

### R-01 (residual — not a blocker)

**#13 compare step-2 UX:** Mockup `comparenote` still reads "מדרג את **כל הגידולים**" and `G[8].compare` dims single-crop select. LOD400 §2 + team_00 decision supersede this with a **selected-crop basket** (2–6 multi-select). team_35 iteration is in flight (`FROST_REGIONS_AND_SPEC_LOCK_2026-06-07.md` §1, LOD400 §2). **Does not block L-GATE_D** — engine can proceed on other increments; #13 UI ships after basket mockup returns.

### R-02 (residual — B-later only)

**Frost region dates:** Canonical keys frozen in `team_35/FROST_REGIONS_AND_SPEC_LOCK_2026-06-07.md`; date values marked **DRAFT pending team_00**. B-later (#11) only — not blocking Phase A / B-now.

---

## 5. Findings register

| ID | Severity | Finding | Action |
|----|----------|---------|--------|
| F-01 | MINOR | LOD400 AC#6 cites **217/217** PHP tests; suite is now **221/221** after WP-CB-CALC route/macro additions. | Update AC count at next spec touch (cosmetic). |
| F-02 | MINOR | CROPDATA-DATES LOD400 §1/§3 refers to `attribute_name`; delivery-tier schema + `HubController` correctly use **`attribute_key`** (`migrations/005_crop_attribute.sql`, `CropBookViewController.php:682`). | Align spec terminology to `attribute_key` on next edit. |
| F-03 | MINOR | LOD_DESIGN title still says "6/14 → **14** live" while §0 decision #4 + LOD400 define **15** goals (incl. `harvest_window`). | Fix title on next LOD touch. |
| R-01 | RESIDUAL | #13 basket mockup iteration pending (see §4). | team_35 → team_100; block #13 UI only. |
| R-02 | RESIDUAL | Frost-region date literals DRAFT (team_00 approval). | team_00 before `frost_regions.json` ships (B-later). |

**Blockers: 0 · Major: 0**

---

## 6. Recommended next build sequence (post team_00 go)

1. **Typed-result refactor** (`showResult` / `pushSession` per LOD400 §6) — unblocks visual QA.
2. **Phase A remainder** — `seed_cost` (#14), `compare` (#13 engine; basket UI after R-01).
3. **B-now wiring** — expose `TRAY_CELLS`/`HARDINESS_OFFSET` to JS; wire `runEngine()` to `SFA_DATEC`; add `harvest_window` 15th goal + `calc_dash` relabels (14→15 מטרות, רווח→השוואת גידולים).
4. **Parallel:** `WP-CB-CROPDATA-DATES` guided tool (API-only writes per IR#7).
5. **B-later** after categoricals filled — nursery, frost, transplant-accurate sow_date.

---

## 7. Routing

- **team_100:** L-GATE_D **PASS_WITH_FINDINGS** — resume implementation on team_00 go.
- **team_50:** Hold full visual QA until typed render lands; partial mockup mapping **accepted** (§4).
- **team_35:** Close R-01 (#13 basket); frost keys already frozen (R-02 dates → team_00).
- **team_00:** Explicit go still required per LOD_DESIGN §8; approve frost-region DRAFT dates when B-later approaches.

---

*Validator: team_190 · Engine: Cursor / Composer · 2026-06-07*
