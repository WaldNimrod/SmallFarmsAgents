---
id: MANDATE_SFA-S003-P002-WP-B_TEAM110_EXECUTION_v1.0.0
from: team_00
to: team_110
date: "2026-05-24"
type: EXECUTION_MANDATE
wp: "SFA-S003-P002-WP-B (program: B1 + B2 + B3)"
project: smallfarmsagents
branch: main
execution_authority: full
status: ACTIVE
spec_ref: "_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B/PROGRAM_BRIEF_v1.0.0.md"
mandate_basis: "team_00 in-session grant 2026-05-24 (canonical registration grant)"
prior_gate: "L-GATE_PRE_HANDOFF PASS (team_190 verdict at commit d70bf11)"
---

# Execution Mandate — SFA-S003-P002-WP-B (Program: B1 + B2 + B3)

> **execution_authority: full** — team_110 is the primary executor for the
> full lifecycle of this 3-WP program (WP-B1, WP-B2, WP-B3) per ADR045.
> team_100 receives a single COMPLETION_REPORT per WP upon its LOD500_LOCKED.
> No mid-execution approvals from team_100 are required.
>
> Reference: `_aos/governance/directives/ADR045_TEAM_110_AUTONOMOUS_EXECUTION_v1.0.0.md`

---

## §1 Scope

Three-work-package program to populate the multi-source crop knowledge base:
- **WP-B1** — JMF MasterClass Excel base layer (PR tier, 0.70)
- **WP-B2** — JMF PDF extraction via concrete `NIImporter` (NI tier, hard override)
- **WP-B3** — Tend Israel adaptation overlay (OP tier, 0.55)

All three build on the WP-A enrichment engine (LOD500_LOCKED at commit 594cbc8).

Full program scope, asset paths, schemas, AC targets:
`_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B/PROGRAM_BRIEF_v1.0.0.md`

---

## §2 Spec References (read before beginning)

- `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B/PROGRAM_BRIEF_v1.0.0.md` (primary input)
- `_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B/PRE_HANDOFF_VERDICT_v1.0.0.md` (4 advisories)
- `_aos/work_packages/S003/SFA-S003-P002-WP-A/LOD400_spec.md` (structural reference)
- `_aos/governance/directives/ADR045_TEAM_110_AUTONOMOUS_EXECUTION_v1.0.0.md`
- `_aos/governance/team_110.md`

---

## §3 Acceptance Criteria (program-level — full ACs in LOD400 you author)

For the program to reach LOD500_LOCKED for each WP:
- AC-PROG-1: LOD200 spec authored (all 12 required sections per ACTIVATION_PROMPT §5)
- AC-PROG-2: LOD400 spec authored (all 15 required sections, mirror WP-A LOD400 v1.1.0)
- AC-PROG-3: L-GATE_S (spec lock) verdict PASS or PASS_WITH_FINDINGS by team_190
- AC-PROG-4: Build complete per LOD400 spec (builder mandate issued to sfa_build)
- AC-PROG-5: L-GATE_V (validate) verdict PASS or PASS_WITH_FINDINGS by team_190
- AC-PROG-6: ADR042 3-step closure executed (archive + roadmap update + sync)
- AC-PROG-7: COMPLETION_REPORT filed to team_00 + team_100
- AC-PROG-8: 4 advisory items from PRE_HANDOFF_VERDICT addressed in LOD400 specs

Per-WP detailed ACs are produced by team_110 in each LOD400 spec.

---

## §4 Execution sequence — program orchestration

team_110 executes for **EACH WP** (B1 first; then B2 + B3 in parallel if resources allow):

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Phase 1: LOD200 authoring                                              │
│    Write _aos/work_packages/S003/{WP_ID}/LOD200_spec.md                 │
│    Replace placeholder; full 12-section spec                            │
│                                                                          │
│  Phase 2: LOD400 authoring                                              │
│    Write _aos/work_packages/S003/{WP_ID}/LOD400_spec.md                 │
│    Full 15-section spec mirroring WP-A LOD400 v1.1.0                    │
│    Address all 4 PRE_HANDOFF advisories                                 │
│                                                                          │
│  Phase 3: L-GATE_S mandate to team_190                                  │
│    File _COMMUNICATION/team_190/{WP_ID}/MANDATE_L-GATE_S_v1.0.0.md     │
│    Wait for verdict file in _COMMUNICATION/TEAM_190/{WP_ID}/            │
│    LOD400-VERDICT_v1.x.x.md                                             │
│    If FAIL: remediate + resubmit (loop until PASS)                      │
│                                                                          │
│  Phase 4: Roadmap state transition                                      │
│    Per ADR045 R2 #3: team_110 MAY update _aos/roadmap.yaml WP entry     │
│    Update: lod_status: LOD400_LOCKED, current_lean_gate: L-GATE_B       │
│                                                                          │
│  Phase 5: L-GATE_B mandate to builder (sfa_build / team_10)             │
│    File _COMMUNICATION/team_10/{WP_ID}/MANDATE_L-GATE_B_v1.0.0.md      │
│    Builder runs in separate session (likely Claude Code).               │
│    Wait for BUILD_REPORT in _COMMUNICATION/TEAM_10/{WP_ID}/             │
│                                                                          │
│  Phase 6: L-GATE_V mandate to team_190                                  │
│    File _COMMUNICATION/team_190/{WP_ID}/MANDATE_L-GATE_V_v1.0.0.md     │
│    Wait for verdict. If FAIL: remediate via builder, resubmit.          │
│                                                                          │
│  Phase 7: ADR042 3-step closure                                         │
│    Step 1: Write _archive/{WP_ID}/ARCHIVE_MANIFEST.md                   │
│    Step 2: Update _aos/roadmap.yaml WP entry → status: DONE,            │
│            lod_status: LOD500_LOCKED, current_lean_gate: L-GATE_V       │
│    Step 3: validate_aos.sh expected 29 PASS / 17 SKIP / 0 FAIL          │
│                                                                          │
│  Phase 8: COMPLETION_REPORT                                             │
│    Write _COMMUNICATION/team_110/{WP_ID}/                               │
│    COMPLETION_REPORT_{WP_ID}_v1.0.0.md                                  │
│    Recipients: team_00 + team_100                                       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## §5 Iron Rule preservation (CRITICAL)

- **IR#1** — team_110 MUST NOT validate its own specs or implementation.
  Always delegate to team_190 (non-Claude per IR#1 — currently GPT-5.5).
  The builder engine (team_10 / sfa_build) MUST also differ from team_190's engine.
- **IR#4** — In execution mode, team_110 MAY edit roadmap WP-entry **lifecycle
  fields only** (status, lod_status, current_lean_gate, closed_at). Other fields
  remain team_100-only.
- **IR#6** — All inter-team mandates and verdicts via `_COMMUNICATION/<team>/`.
- **IR#7** — When AOS DB is online, structured mutations go via API.
- **IR#11** — Never touch `_aos/governance/`, `_aos/lean-kit/`, or hub-only files.
- **IR#12** — Never invoke `/AOS_gov-update` or `/AOS_gov-sync`.

---

## §6 Authorization basis

This mandate is issued under **team_00 Principal grant 2026-05-24** (in-session
authorization for the WP-B program). Verified by team_190 in PRE_HANDOFF_VERDICT
(commit d70bf11): IR#4 exception properly documented per CLAUDE.md Directory
Authority.

team_110 fallback: if session ends before LOD500_LOCKED for any WP, team_100
resumes ownership of that WP per ADR045 R3 #4.

---

## §7 Completion criteria — program level

Program SFA-S003-P002-WP-B is complete when ALL THREE WPs have:
- [ ] LOD200 + LOD400 specs authored
- [ ] L-GATE_S PASS by team_190
- [ ] L-GATE_B PASS by builder
- [ ] L-GATE_V PASS by team_190
- [ ] ARCHIVE_MANIFEST.md exists
- [ ] roadmap.yaml entry → status: DONE, lod_status: LOD500_LOCKED
- [ ] validate_aos.sh: 29 PASS / 17 SKIP / 0 FAIL
- [ ] COMPLETION_REPORT filed (per WP, to team_00 + team_100)
- [ ] All commits on `main` (no LOD500_LOCKED file mutations; roadmap edits
      attributed correctly)

---

*EXECUTION_MANDATE | TEAM_110 | ADR045 | issued 2026-05-24 by team_10 on behalf of team_00 grant*
