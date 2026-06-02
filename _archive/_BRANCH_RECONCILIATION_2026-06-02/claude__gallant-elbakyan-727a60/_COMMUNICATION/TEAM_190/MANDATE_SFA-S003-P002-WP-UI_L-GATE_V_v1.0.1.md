---
id: MANDATE_SFA-S003-P002-WP-UI_L-GATE_V_v1.0.1
from: Team 100 (Chief System Architect — smallfarmsagents spoke)
to: Team 190 (External Constitutional Validator)
date: 2026-05-27
type: GATE_MANDATE_SUPERSEDED
gate: L-GATE_V
wp: SFA-S003-P002-WP-UI
project: smallfarmsagents
status: ACTIVE
verdict: PENDING
engine_constraint: "Cross-engine per IR#1. Builders are Claude (team_10 + team_100). You (team_190) MUST be non-Claude — GPT-5.5 / Cursor Composer / Codex / GPT-5."
resubmission_round: 1
supersedes: MANDATE_SFA-S003-P002-WP-UI_L-GATE_V_v1.0.0.md
supersede_reason: "Team 00 process correction: dispatching L-GATE_V with 2 known-bug carry-overs (F-BUILD-04, F-BUILD-05) is incorrect — validation gate is for catching new findings, not blessing documented ones. team_100 fix-forwarded both before dispatch. This v1.0.1 mandate reflects the truly clean BUILD_COMPLETE state."
prior_gate_verdict: _COMMUNICATION/TEAM_190/VERDICT_SFA-S003-P002-WP-UI_L-GATE_S_v1.0.1.md
---

# L-GATE_V Mandate (Round 1) — SFA-S003-P002-WP-UI

**Standalone web UX shell — adopt team_35 LOD300 onto Slim/PHP/uPress**
**Track:** A | **Profile:** L0 | **Risk:** MEDIUM

---

## 0. SUPERSEDE NOTICE — read first

This v1.0.1 SUPERSEDES MANDATE_SFA-S003-P002-WP-UI_L-GATE_V_v1.0.0 (committed in `21ad884` on `gallant-elbakyan-727a60`). The v1.0.0 mandate referenced 2 documented findings (F-BUILD-04 + F-BUILD-05) as items for you to triage. team_00 correctly objected: validation gates are for catching what we **didn't** know, not for ratifying known bugs.

team_100 fix-forwarded both findings before validation:
- **F-BUILD-04** RESOLVED via deterministic `variety-{id}` slug pattern (commit `740ea2c` on `claude/sfa-ui-build`)
- **F-BUILD-05** RESOLVED via full rewrite of `book_variety.php` with labeled Hebrew field rendering (same commit)

**Updated BUILD_REPORT:** `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-UI/BUILD_REPORT_v1.0.2.md` (BUILD_COMPLETE CLEAN, 38 PASS / 0 PARTIAL / 0 FAIL, zero carry-overs).

Your validation should focus on items you can find that team_100 missed — not the 2 already-resolved findings.

---

## 2. Prior Gate History

| Gate | Result | Date | Validator | Notes |
|------|--------|------|-----------|-------|
| L-GATE_E | PASS | 2026-05-24 | team_00 | Option B in-session approval. |
| L-GATE_S R1 | FAIL | 2026-05-27 | team_190 | 5 findings; LOD400 amended v1.0.1. |
| L-GATE_S R2 | PASS_WITH_FINDINGS | 2026-05-27 | team_190 | All R1 resolved; 2 minor cleaned to v1.0.2. DISPATCH_BUILD. |
| L-GATE_B R1 | PARTIAL | 2026-05-27 | sfa_build (team_10) | Functional but uncommitted + no deploy + a11y 90-92 + 4 NOT_RUN. |
| L-GATE_B R2 | PASS_WITH_FINDINGS | 2026-05-27 | team_100 | a11y 100/100/100; deployed live; 37 PASS + 1 PARTIAL; 2 findings F-BUILD-04/05 documented. |
| **L-GATE_B R3 (fix-forward)** | **PASS CLEAN** | **2026-05-27** | **team_100** | **F-BUILD-04 + F-BUILD-05 resolved; 38 PASS / 0 PARTIAL / 0 FAIL. BUILD_REPORT_v1.0.2.md. Commit `740ea2c`.** |

This is **Round 1** for L-GATE_V — first constitutional validation post-clean-BUILD.

---

## 3. Scope

**L-GATE_V — Constitutional validation.** Final cross-engine review of the implementation against LOD400 v1.0.2 + parent DECISION + canonical docs. After PASS here, WP-UI transitions to COMPLETE/LOD500_LOCKED.

**Specifically you must verify:**
1. The deployed system at `https://sfa.nimrod.bio/` implements LOD400 v1.0.2 §3 (file mapping) + §4 (routes) + §5 (38 ACs) correctly
2. All 38 ACs in LOD400 §5 actually PASS at the live system
3. No architectural drift: still Slim/PHP/uPress (no Flask), `/crop-book/*` URLs (no `/book/*`), no community write surfaces
4. No regression on existing live system (sfa.nimrod.bio APIs, waldhomeserver cron, legacy site 404)
5. Cross-engine policy honored: team_10 + team_100 (both Claude) built; you (non-Claude) validate
6. Iron Rules satisfied: IR#1 cross-engine, IR#4 single roadmap writer, IR#6 artifact comms

**Validate the fix-forward specifically:**
- `/crop-book/anise-hyssop/variety/variety-1` returns 200 with **labeled Hebrew fields** (not raw JSON)
- CB5 detail (`/crop-book/anise-hyssop`) generates `href="/crop-book/anise-hyssop/variety/variety-{id}"` links with unique IDs
- (Cannot verify multi-variety uniqueness on prod data since most crops have 0-1 varieties; verify logic via code review of `CropBookViewController::varietySlug()`)

---

## 4. Validation Criteria

Same 9 VCs as v1.0.0, but VC-V-5 and VC-V-6 are revised:

| # | Criterion | What to Check |
|---|-----------|---------------|
| VC-V-1 | **Live file mapping** (BLOCKING) | All 7 design CSS served (curl each). modules.php = 8 modules. |
| VC-V-2 | **14 HTML routes return 200 with correct Hebrew content** (BLOCKING) | Especially `/crop-book/anise-hyssop/variety/variety-1` should show labeled Hebrew fields (NOT raw JSON). |
| VC-V-3 | **8 API endpoints work** (BLOCKING) | curl each. |
| VC-V-4 | **Lighthouse mobile** | team_100 measured 94/100/96/100 on `/`; sample independently. |
| VC-V-5 | **F-BUILD-04 fix verification** | (Revised) Confirm `CropBookViewController::varietySlug()` exists and returns `'variety-' . id`. Confirm CB5 links use this pattern. Confirm variety route lookup uses this pattern. Spot-check live: `curl -sS https://sfa.nimrod.bio/crop-book/anise-hyssop` returns links matching `variety-[0-9]+`. |
| VC-V-6 | **F-BUILD-05 fix verification** | (Revised) Confirm `book_variety.php` no longer contains `<pre>`-wrapped `json_encode`. Confirm it renders `<dl class="variety-fields">` with Hebrew field labels (שם באנגלית, ימים לבגרות, מרווח בשורה, etc.). Spot-check live: `curl -sS https://sfa.nimrod.bio/crop-book/anise-hyssop/variety/variety-1 \| grep -c '<dt>'` ≥ 1. |
| VC-V-7 | **Architectural invariants** (BLOCKING) | No Flask code anywhere; no `community_contributions` table; `/crop-book/*` canonical (not `/book/*`). |
| VC-V-8 | **No live regression** (BLOCKING) | AC-36 health OK; AC-37 waldhomeserver cron within 24h; AC-38 legacy `www.nimrod.bio/smallfarmsagent/` → 404. |
| VC-V-9 | **Cross-engine + IR#4** | git log on `claude/sfa-ui-build` — builder commits Claude; no roadmap edits in build commits. |

**VC-V-1/2/3/7/8 BLOCKING.** A FAIL on any blocks the gate.

---

## 5. Files to Review

### Primary review targets
- **BUILD_REPORT v1.0.2 (clean):** `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-UI/BUILD_REPORT_v1.0.2.md` (current — supersedes v1.0.0 + v1.0.1)
- **LOD400 v1.0.2:** `_aos/work_packages/S003/SFA-S003-P002-WP-UI/LOD400_spec.md`
- **visual_diff/diff_notes.md** (updated with v1.0.2 fix narrative)
- **Lighthouse v2 evidence:** `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-UI/lighthouse_v2/*.json`

### Implementation source
- All under `sfa_delivery/` on branch `claude/sfa-ui-build` (commit `740ea2c` head)
- Specifically inspect `CropBookViewController::varietySlug()` (new method) and `book_variety.php` (full rewrite) for the fix-forward verification

### Architectural authority (unchanged)
- `_COMMUNICATION/team_00/DECISION_SFA-S003-P003_DEDICATED_SFA_SUBDOMAIN_2026-05-23_v1.0.0.md`
- `documentation/02-architecture/sfa-delivery-tier.md`
- `documentation/03-data-and-schema/sfa-mysql-mirror.md`

### Live system (canonical)
- https://sfa.nimrod.bio/ — full site, all routes deployed

---

## 6. Resolved Findings from prior

| ID | Severity | Resolution |
|----|----------|------------|
| F-BUILD-04 | MAJOR | RESOLVED by team_100 fix-forward at commit `740ea2c`. New `varietySlug()` method uses `variety-{id}` pattern. Live verified: CB5 generates unique slugs. |
| F-BUILD-05 | MINOR | RESOLVED by team_100 fix-forward at commit `740ea2c`. `book_variety.php` rewritten with labeled Hebrew fields. Live verified: 12 `<dt>` labels, 0 `<pre>` raw-JSON. |

(These were documented but unresolved in v1.0.0 of this mandate. v1.0.1 reflects resolved state.)

---

## 7. Output Format

Write verdict to:
`_COMMUNICATION/TEAM_190/VERDICT_SFA-S003-P002-WP-UI_L-GATE_V_v1.0.0.md`

(First verdict file for L-GATE_V — no v1.0.0 verdict exists yet since v1.0.0 mandate was superseded before you started.)

Use the **unified verdict template** (7 sections):

1. **Verdict Summary** — `PASS` | `PASS_WITH_FINDINGS` | `FAIL` + 2-sentence rationale.
2. **Parameters** — engine + version, time spent, files actually read, live URLs checked.
3. **Criteria Table** — VC-V-1..VC-V-9 each with result + 1-line rationale.
4. **Findings** — only NEW findings you discover (use `LV-V-N` numbering).
5. **validate_aos.sh** — run it; expect 29/17/0.
6. **Disposition** — `CLOSE_WP` (PASS) | `WP_UI_PATCH01_THEN_CLOSE` (PASS_WITH_FINDINGS) | `RETURN_TO_BUILD` (FAIL).
7. **Next Step** — single imperative sentence for team_100.

### Constraints

- **Cross-engine (IR#1):** builders are Claude. You MUST be non-Claude.
- **Evidence-based:** every finding cites `file:line` or live URL + actual HTTP/JSON output.
- **Live system access:** curl + (your engine's) headless browser + Lighthouse independently.
- **No code execution beyond reading + curl + Lighthouse.** No phpunit, no git mutations.
- **No roadmap mutation:** IR#4.
- **Enforcement mode:** STANDARD. PASS allowed only with truly zero findings of MAJOR-or-above.

---

*Mandate v1.0.1 (superseding v1.0.0) generated 2026-05-27 by team_100 per `/AOS_gate-mandate` canon + team_00 process correction. Awaiting clean L-GATE_V verdict.*
