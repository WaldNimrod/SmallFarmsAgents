# Session Handoff — team_100 (Chief System Architect) · spoke: SmallFarmsAgents (L0)

> **Provenance:** authored directly by team_100 on 2026-06-04 because the hub prompt-generate API
> (`http://100.125.98.56:8090`) was **unreachable** (port refused; localhost = 410 legacy stub). Faithful to
> the canonical 7-section format; re-generate via `/AOS_handoff full 100` once the hub API is back if a
> SSoT-rendered version is wanted. Governance boilerplate per `CLAUDE.md` + `_aos/governance/team_100.md`.

## 1. Identity & governance (full)
- **You are team_100** — Chief System Architect, Claude Code (Opus), spoke `SmallFarmsAgents`, profile L0.
- **Hub:** `/Users/nimrod/Documents/agents-os` (read-only methodology SSoT). **`_aos/` here is a read-only snapshot.**
- **Iron Rules (must honor):** IR#1/#5 cross-engine (builder ≠ architect ≠ validator; **team_100 NEVER self-issues
  L-GATE_S/L-GATE_V** — route to team_190 non-Claude); IR#4 single-writer on `_aos/roadmap.yaml` (only team_100);
  IR#7 API-only structured mutations when DB online (in practice this spoke edits `roadmap.yaml` file-based on a
  named branch under the single-writer rule); delivery-tier scope discipline; no `_aos/` edits by build sub-agents.
- **Directory authority:** team_100 writes `_COMMUNICATION/team_100/`, `_aos/roadmap.yaml`, `_aos/work_packages/`.

## 2. TL;DR — repo + program state (2026-06-04)
- **Active branch:** `claude/ui-polish-hub-cropbook-2026-06-03` (tip ~`430f57f`, pushed). `main` carries the
  closed S003-P004 work. Several auto-syncer governance commits interleave on the branch — commit defensively
  (explicit paths, verify `git merge-base --is-ancestor`). A **pre-push hook runs validate_aos** — keep 0 FAIL.
- **S003-P004 status:** WP-CB-DATA + WP-CB-UI-CLASSB = **DONE / LOD500_LOCKED** (team_190 PASS, live). UI-patch01
  (WI-1..WI-9: hub full-width/Field-Log, crop density, copy/term חקלאי-מקומי, drop-Tend, hub CTA, logo fix,
  mobile-overflow) — built + mostly deployed; **WI-9 (`/crop-book/table` mobile-overflow) final deploy + L-GATE_V
  still pending** (folds into the new WP).
- **THE NEW WORK → `SFA-S003-P004-WP-CB-UI-FIDELITY`** (status SPEC, LOD400 **DRAFT**). team_00 found the live site
  "far from the mockups." A **team_100 CDP audit** (real browser rendering — the gap our composer/validate/L-GATE_V
  marker checks missed) **confirmed launch-blocking defects** on the core pages.

## 3. The audit findings (grounded — see evidence)
**Evidence:** `_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-UI-FIDELITY/audit_evidence/` (live + Board-A/B screenshots
+ `cdp_facts.json`). **BLOCKERS:** D-1 raw 6-decimal floats on crop pages (59.043478, 30.000000); D-2 English unit
codes (cm/days/weeks/count); D-3 market category chips = raw English DB keys (root_vegetables/leafy_greens/…);
D-4 crop-book filters return 0 (`season` token vs Hebrew data mismatch); D-5 broken/duplicated oversized crop hero
(`.crophero` + `.cb-crop-hero`). **MAJOR:** classb.js not loaded on crop-book/calc; English `<small>` eyebrows;
full mockup-fidelity sweep. **WORKS (don't regress):** hub, market list, global search, market detail graph, palette.

## 4. SESSION TASK (team_00 directive)
**Execute `SFA-S003-P004-WP-CB-UI-FIDELITY` to launch-readiness.** Per team_00, this session MUST:
1. **Read + REVIEW + IMPROVE** the DRAFT LOD: `_aos/work_packages/S003/SFA-S003-P004-WP-CB-UI-FIDELITY/LOD400_spec.md`
   (add any defect it missed; pin exact code locations; decide the team_35 design questions).
2. **Route external L-GATE_S to team_190 (non-Claude, IR#1/#5) BEFORE any build.** Address findings; re-route if BLOCKED.
3. **Build** (team_10 Sonnet) per WI-1..WI-7; **team_100 independent L-GATE_B with CDP VISUAL verification**
   (screenshots vs Board-A/B + the AC CDP scans) — **NOT** the Haiku QA tier (it proved unreliable this session).
4. **Deploy** (team_99 FTPS) — verify served `?v=` advanced + markers present.
5. **External L-GATE_V + repeat visual round** — team_190 per-surface design-vs-live vs Board-A/B + AC matrix on the
   LIVE site → on PASS LOD500_LOCKED (the launch gate).
6. **team_35 design completions** (WI-7) resolved before declaring GO — file a DESIGN_REQUEST for any missing v2
   design / label / enum-Hebraization / icon-set decision; never guess a missing design.

## 5. FIRST ACTION
Read the LOD + `audit_evidence/` (view the live screenshots vs `MOCK_Board-A`/`MOCK_Board-B`) →
improve the LOD → author the L-GATE_S validation mandate + Cursor prompt → route to team_190 (non-Claude).
Do NOT start the build before external L-GATE_S PASS.

## 6. ACTIVATION PROMPT (copy this to start the next session)
```
HANDOFF_DEPTH: full
ACTIVATION_SCOPE: team_100 only

You are team_100 — Chief System Architect (Claude Code / Opus) — on the SmallFarmsAgents AOS spoke (L0).
Repo: /Users/nimrod/Documents/SmallFarmsAgents. Hub (read-only): /Users/nimrod/Documents/agents-os.
Honor the Iron Rules: IR#1/#5 cross-engine (builder Sonnet ≠ architect Opus ≠ validator team_190 non-Claude;
team_100 NEVER self-issues L-GATE_S/L-GATE_V), IR#4 (team_100 single-writer on _aos/roadmap.yaml), delivery-tier
scope. Commit defensively (explicit paths; verify ancestry — an auto-syncer interleaves _aos/ commits; a pre-push
hook runs validate_aos — keep 0 FAIL). Production deploys + SSH to waldhomeserver are auth-gated for this Mac
session → route deploys to team_99 (server session). Do visual/RTL verification with the CDP harness
(_aos/lean-kit/modules/validation-quality/scripts/qa/qa_probe.mjs) yourself — the Haiku QA tier was unreliable.

SESSION TASK: execute WP SFA-S003-P004-WP-CB-UI-FIDELITY (pre-launch crop-book + market UI fidelity & Hebrew
localization) to launch-readiness. Spec (LOD400 DRAFT — REVIEW + IMPROVE it first):
  _aos/work_packages/S003/SFA-S003-P004-WP-CB-UI-FIDELITY/LOD400_spec.md
Audit evidence (view the live-vs-mockup screenshots):
  _COMMUNICATION/team_100/SFA-S003-P004-WP-CB-UI-FIDELITY/audit_evidence/
Confirmed BLOCKERS: D-1 raw 6-decimal floats on crop pages; D-2 English unit codes (cm/days/weeks); D-3 market
category chips = raw English keys; D-4 crop-book filters return 0; D-5 broken/duplicated oversized crop hero.
Also fold in patch01 WI-9 (/crop-book/table mobile overflow) — still pending final deploy + L-GATE_V.

MANDATORY FLOW (team_00 directive): (1) review + improve the DRAFT LOD (pin code locations, list any missed
defects, decide team_35 design questions); (2) route external L-GATE_S to team_190 (non-Claude) BEFORE any build;
(3) build via team_10 (Sonnet) → team_100 independent L-GATE_B with CDP VISUAL verification vs Board-A/B (not a
Haiku QA pass); (4) team_99 deploy; (5) team_190 L-GATE_V design-vs-mockup on the LIVE site + repeat visual round
→ LOD500_LOCKED; (6) team_35 design completions (WI-7) resolved before GO.

FIRST ACTION: read the LOD + audit_evidence, improve the LOD, then author + route the team_190 L-GATE_S mandate
(non-Claude) with a Cursor prompt. Do NOT build before external L-GATE_S PASS.

MANDATORY READS: _aos/work_packages/S003/SFA-S003-P004-WP-CB-UI-FIDELITY/LOD400_spec.md ·
_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-UI-FIDELITY/audit_evidence/ · _aos/governance/team_100.md · CLAUDE.md ·
_aos/roadmap.yaml (WP-CB-UI-FIDELITY + WP-CB-UI-patch01 entries) ·
the team_50 pre-launch QA mandate (_COMMUNICATION/team_50/SFA-PRELAUNCH-QA/QA_MANDATE_PRELAUNCH_VISUAL_E2E_2026-06-03_v1.0.0.md) ·
memories: reference_prod_deploy_authorization, reference_sfa_deploy_topology, feedback_crossengine_validation.
```

## 7. Blockers / open items
- **Deploy is the recurring bottleneck:** the Mac orchestrator's SSH/FTPS to prod is classifier-gated → every fix
  needs team_99 (waldhomeserver session) to run the deploy. Expect to push branches + route DEPLOY mandates + wait.
- **Haiku QA unreliable:** team_50 (Haiku) gave a false NO-GO + mis-read CSS + missed the rendered defects this
  session. Use **team_100 CDP (qa_probe / a DOM-walk offender finder) + team_190 (non-Claude)** for visual/RTL.
- **patch01 WI-9** (`/crop-book/table` mobile overflow — root cause: two table views with no responsive toggle, fixed
  by `@media ≤720px hide .dt-table-wrap`) awaits its final team_99 deploy + team_190 L-GATE_V; fold into FIDELITY.
- **Hub prompt-generate API was DOWN** (100.125.98.56:8090 refused) at handoff time — this artifact is hand-authored.
- **LOD is DRAFT** — improve it + pass external L-GATE_S before build (team_00 directive).
