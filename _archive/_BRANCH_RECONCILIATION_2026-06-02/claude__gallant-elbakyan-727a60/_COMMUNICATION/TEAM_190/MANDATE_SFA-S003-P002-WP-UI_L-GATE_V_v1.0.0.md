---
id: MANDATE_SFA-S003-P002-WP-UI_L-GATE_V_v1.0.0
from: Team 100 (Chief System Architect — smallfarmsagents spoke)
to: Team 190 (External Constitutional Validator)
date: 2026-05-27
type: GATE_MANDATE
gate: L-GATE_V
wp: SFA-S003-P002-WP-UI
project: smallfarmsagents
status: ACTIVE
verdict: PENDING
engine_constraint: "Cross-engine per IR#1. builder=sfa_build (Claude Sonnet team_10) + team_100 remediation (Claude Sonnet). You (team_190) MUST be non-Claude — GPT-5.5 / Cursor Composer / Codex / GPT-5. Same engine as L-GATE_S R1+R2 preferred for continuity."
resubmission_round: 1
prior_gate_verdict: _COMMUNICATION/TEAM_190/VERDICT_SFA-S003-P002-WP-UI_L-GATE_S_v1.0.1.md
---

# L-GATE_V Mandate — SFA-S003-P002-WP-UI

**Standalone web UX shell — adopt team_35 LOD300 onto Slim/PHP/uPress**
**Track:** A | **Profile:** L0 | **Risk:** MEDIUM

---

## 2. Prior Gate History

| Gate | Result | Date | Validator | Notes |
|------|--------|------|-----------|-------|
| L-GATE_E | PASS | 2026-05-24 | team_00 | Option B in-session approval. |
| L-GATE_S R1 | FAIL | 2026-05-27 | team_190 (GPT-5.5/Cursor) | 5 findings (2 BLOCKER + 2 MAJOR + 1 MINOR). |
| L-GATE_S R2 | PASS_WITH_FINDINGS | 2026-05-27 | team_190 | All R1 resolved; 2 new MINOR (LV-S-6/7) addressed inline in v1.0.2. DISPATCH_BUILD. |
| L-GATE_B R1 | PARTIAL | 2026-05-27 | sfa_build (team_10, Codex 5.3) | Implemented but uncommitted + no deploy + a11y 90-92 + 4 ACs NOT_RUN. team_100 took over for Path B remediation. Report v1.0.0. |
| **L-GATE_B R2** | **PASS_WITH_FINDINGS** | **2026-05-27** | **team_100 (self-execute remediation)** | **Lighthouse a11y 100/100/100; deploy live; 37 PASS + 1 PARTIAL (AC-17). 2 new findings F-BUILD-04/05 documented. Report v1.0.1.** |

This is **Round 1** for L-GATE_V — first constitutional validation post-BUILD.

---

## 3. Scope

**L-GATE_V — Constitutional validation.** Final cross-engine review of the implementation against the LOD400 v1.0.2 spec, the parent DECISION_SFA-S003-P003, and the binding canonical docs. After PASS here, WP-UI transitions to COMPLETE/LOD500_LOCKED.

**Specifically you must verify:**
1. The deployed system at `https://sfa.nimrod.bio/` implements LOD400 v1.0.2 §3 (file mapping) + §4 (routes) + §5 (38 ACs) correctly
2. All 38 ACs in LOD400 §5 actually PASS at the live system (you may sample-curl + spot-check; team_100's BUILD_REPORT v1.0.1 documents each)
3. The 2 BUILD findings (F-BUILD-04 slug collision + F-BUILD-05 variety detail rendering) are appropriately categorized — BLOCKING for v1.0 / PASS_WITH_FINDINGS with WP-UI-patch01 deferral / or PASS as-is
4. No architectural drift: still Slim/PHP/uPress (no Flask resurrection), `/crop-book/*` URLs (no `/book/*` change), no community write surfaces (no `community_contributions` table or `POST /community/contribute`)
5. No regression on existing live system (sfa.nimrod.bio /api/v1/health, /api/v1/crops, /api/v1/products, /api/v1/ingest HMAC, waldhomeserver cron, legacy site 404)
6. Cross-engine policy honored: team_10 + team_100 (both Claude) built; you (non-Claude) validate
7. Iron Rules satisfied: IR#1 cross-engine, IR#4 single roadmap writer, IR#6 artifact comms, IR#7 API-only mutations (no roadmap writes from your session)

**The implementation is LIVE at https://sfa.nimrod.bio/.** You can curl + visit + Lighthouse independently. Do not rely solely on team_100's BUILD_REPORT.

---

## 4. Validation Criteria

| # | Criterion | What to Check |
|---|-----------|---------------|
| VC-V-1 | **Live system implements LOD400 §3 file mapping** (BLOCKING) | All 7 design CSS files served (curl each `https://sfa.nimrod.bio/public_assets/css/{tokens,gj,hub,community,crop-book-deep,desktop,desktop-extras}.css` → 200). modules.php generated from MODULES_REGISTRY.yaml (curl `/api/v1/modules` → 8 modules). |
| VC-V-2 | **All 14 HTML routes per LOD400 §4 return 200 with correct Hebrew content** (BLOCKING) | curl + spot-visual each route. Especially: `/` shows 8 modules, `/crop-book/table` lists 52 crops + `<th scope=col>`, `/market/` leads with disclaimer + 65 products, `/community` is STATIC (no form). |
| VC-V-3 | **All 8 API endpoints per LOD400 §4 work** (BLOCKING) | curl `/api/v1/{health,modules,search,crops,crops/{slug},products,products/{slug},market/{slug}/history,ingest}` — last with valid HMAC = 200, bad HMAC = 401. |
| VC-V-4 | **Lighthouse mobile profile meets AC-31** | `npx lighthouse https://sfa.nimrod.bio/ --form-factor=mobile --throttling-method=simulate`. Expect Performance ≥75, Accessibility ≥95, Best-Practices ≥95, SEO ≥90. team_100 measured 94/100/96/100 on `/`; sample your own. |
| VC-V-5 | **F-BUILD-04 disposition** | Decide: BLOCKER (BUILD must fix slugify before L-GATE_V PASS) / MAJOR-with-defer (PASS_WITH_FINDINGS, fix in WP-UI-patch01) / acceptable (most varieties share Hebrew names — collision is moot). State your reasoning. |
| VC-V-6 | **F-BUILD-05 disposition** | Same triage for variety detail template rendering raw JSON instead of labeled fields. |
| VC-V-7 | **Architectural invariants honored** (BLOCKING) | (a) No Flask/gunicorn/waldhomeserver-as-user-facing code anywhere. (b) No `community_contributions` table on MySQL (you can `curl /api/v1/health` then read the migration count via SHOW TABLES if you have phpMyAdmin access; or check `sfa_delivery/migrations/` count = 3 files: 001/002/003 only). (c) `/crop-book/*` is canonical (no `/book/*` routes deployed). |
| VC-V-8 | **No live regression** (BLOCKING) | AC-36 health OK; AC-37 cron from waldhomeserver pushed within last 24h; AC-38 legacy site `www.nimrod.bio/smallfarmsagent/` → 404. |
| VC-V-9 | **Cross-engine + IR#4 honored** | Read git log on `claude/sfa-ui-build` — confirm builder commits were Claude; confirm no roadmap edits in the build commits. Roadmap mutations only on `claude/gallant-elbakyan-727a60` from team_100. |

**Total: 9 VCs. VC-V-1/2/3/7/8 are BLOCKING. A FAIL on any blocks the gate.**

---

## 5. Files to Review

### Primary review targets (binding)
- **LOD400 v1.0.2:** `_aos/work_packages/S003/SFA-S003-P002-WP-UI/LOD400_spec.md` (your prior R2 PASS target)
- **BUILD_REPORT v1.0.1 (team_100 remediation):** `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-UI/BUILD_REPORT_v1.0.1.md`
- **Visual diff notes:** `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-UI/visual_diff/diff_notes.md`
- **Lighthouse v2 evidence:** `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-UI/lighthouse_v2/{home,crop-book_table,market}_mobile_v3.json`
- **team_10 v1.0.0 BUILD_PARTIAL report (audit context):** `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-UI/BUILD_REPORT_v1.0.0.md`

### Implementation source (binding)
- All under `sfa_delivery/` on branch `claude/sfa-ui-build` (commit `1fdd396` head)
- Especially: `sfa_delivery/app/Controllers/`, `sfa_delivery/app/Lib/`, `sfa_delivery/templates/`, `sfa_delivery/public_assets/css/`, `sfa_delivery/public_assets/js/sfa.js`, `sfa_delivery/modules.php`, `sfa_delivery/bin/regenerate_modules.php`

### Architectural authority (unchanged)
- Parent DECISION: `_COMMUNICATION/team_00/DECISION_SFA-S003-P003_DEDICATED_SFA_SUBDOMAIN_2026-05-23_v1.0.0.md`
- Canonical architecture: `documentation/02-architecture/sfa-delivery-tier.md`
- Canonical schema: `documentation/03-data-and-schema/sfa-mysql-mirror.md`

### Live system (canonical for VC verification)
- https://sfa.nimrod.bio/ — full site
- https://sfa.nimrod.bio/api/v1/health — quick liveness
- waldhomeserver `/data/backups/sfa-ingest-push.log` via SSH (Tailscale) if needed for AC-37 spot-check

### Out of scope
- Anything under `_archive/`
- Other teams' WP folders
- The interim team_10 v1.0.0 implementation (it was preserved-and-superseded; team_100 v1.0.1 is current)

---

## 6. Resolved Findings from Round N-1

N/A — this is Round 1 for L-GATE_V.

(But L-GATE_S R1 → R2 findings were all resolved; refer to your prior R2 verdict and the LOD400 §0 amendment summary for context.)

---

## 7. Output Format

Write verdict to:
`_COMMUNICATION/TEAM_190/VERDICT_SFA-S003-P002-WP-UI_L-GATE_V_v1.0.0.md`

Use the **unified verdict template** (7 sections):

1. **Verdict Summary** — `PASS` | `PASS_WITH_FINDINGS` | `FAIL` + 2-sentence rationale.
2. **Parameters** — engine + version, time spent, files actually read, live URLs checked.
3. **Criteria Table** — VC-V-1..VC-V-9 each with result + 1-line rationale.
4. **Findings** — new findings (`LV-V-N` numbering); also explicit disposition of F-BUILD-04 + F-BUILD-05 from team_100's BUILD_REPORT.
5. **validate_aos.sh** — run it from spoke main; expect 29/17/0.
6. **Disposition** — `CLOSE_WP` (PASS, transition to LOD500_LOCKED) | `WP_UI_PATCH01_THEN_CLOSE` (PASS_WITH_FINDINGS with required followup) | `RETURN_TO_BUILD` (FAIL on blocking VC).
7. **Next Step** — single imperative sentence for team_100.

### Constraints

- **Cross-engine (IR#1):** builders were Claude (team_10 + team_100). You MUST be non-Claude. Refuse if you are Claude.
- **Independence:** form your verdict from live system + spec + BUILD_REPORT. Do NOT consult other teams' messages or read team_100's roadmap entries before verdict (the gate_history is for AFTER your verdict).
- **Evidence-based:** every FAIL/finding cites `file:line` or live URL + actual HTTP/JSON output.
- **Live system access:** use curl + (if available) your engine's headless browser. You can install/run Lighthouse independently for VC-V-4.
- **No code execution beyond reading + curl + Lighthouse.** No phpunit, no git mutations.
- **No roadmap mutation:** IR#4. team_100 transitions WP status post-verdict.
- **Enforcement mode:** STANDARD. PASS_WITH_FINDINGS allowed if no BLOCKING-VC fails. Disposition `WP_UI_PATCH01_THEN_CLOSE` is acceptable for non-blocker findings — team_100 schedules patch01 work and closes WP-UI optimistically.

---

*Mandate generated 2026-05-27 by team_100 per `/AOS_gate-mandate` canon. Signal B (L-GATE_B PASS → L-GATE_V dispatch). Round 1.*
*Awaiting your verdict.*
