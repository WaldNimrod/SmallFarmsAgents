---
id: ARCHIVE_MANIFEST_SFA-S003-P004-WP-CB-UI-CLASSB
wp: SFA-S003-P004-WP-CB-UI-CLASSB
status: DONE
lod_status: LOD500_LOCKED
closed_at: "2026-06-03"
archived_at: "2026-06-03"
archived_by: team_191
mandate_ref: "_COMMUNICATION/team_191/MANDATE_SFA-S003-P004-CLOSURE-ARCHIVE_2026-06-03_v1.0.0.md"
roadmap_entry: "_aos/roadmap.yaml → id: SFA-S003-P004-WP-CB-UI-CLASSB"
archive_root: "_archive/SFA-S003-P004-WP-CB-UI-CLASSB/"
---

# Archive Manifest — SFA-S003-P004-WP-CB-UI-CLASSB

**WP:** ספר גידולים: Class B — עיצוב v2 למשטחי hub/market/search/community/about/account (ממתין לצוות 35)
**Final status:** DONE / LOD500_LOCKED
**Live URL:** https://sfa.nimrod.bio (all 7 Class B surfaces)
**Branch:** `claude/sfa-p004-cbdata-classb-2026-06-02`

---

## Gate Ladder

| Gate | Result | Date | Validator | Notes |
|------|--------|------|-----------|-------|
| L-GATE_E (blocked) | BLOCKED | 2026-06-02 | team_00 | Waiting on team_35 v2 design delivery |
| L-GATE_E | PASS | 2026-06-02 | team_100 | team_35 delivered Board-B (6 surfaces, classb.css/js); LOD400 v0.9.0 authored |
| L-GATE_S | PASS_WITH_FINDINGS | 2026-06-02 | team_190 (Cursor/GPT) | 0 blockers/0 major/7 minor; build-precision confirmed; verdict commit 45badf6 |
| L-GATE_B (initial) | PASS | 2026-06-02 | team_10 | Commit 4695fc7; 7 surfaces + shell; 22 new ClassBRouteTests; 128/129 suite |
| QA (initial) | PASS_WITH_FINDINGS | 2026-06-02 | team_50 | 2 MAJOR/6 MINOR/2 COSMETIC; team_00 directive: fix ALL |
| L-GATE_B (fix-all) | PASS | 2026-06-02 | team_100 (verify), team_10 (build) | All 10 findings addressed; composer 135/135; validate_aos 29/19/0 |
| QA (re-QA) | PASS | 2026-06-02 | team_50 | v1.1.0 re-QA PASS — all 10 findings resolved; 7 routes 200 |
| DEPLOY (routed) | ROUTED | 2026-06-02 | team_99 | Mandate pre-staged; SSH auth-gated to team_00/team_99 |
| L-GATE_V R2 | FAIL | 2026-06-03 | team_190 (Cursor/GPT) | Deploy-precondition FAIL — live site still pre-fix-all; NOT a build defect |
| DEPLOY | SUCCESS | 2026-06-03 | team_99 | deployed_sha c51c2e5; 9 transferred / 7 replaced; 7/7 smoke checks PASS |
| L-GATE_V R3 | PASS_WITH_FINDINGS | 2026-06-03 | team_190 (Cursor/GPT) | 7/7 surfaces + 4/4 constitutional; 2 INFO non-blocking; LOD500_LOCKED |

---

## Verdict References

| Gate | Verdict File | Result |
|------|-------------|--------|
| L-GATE_S | `_COMMUNICATION/TEAM_190/SFA-S003-P004/WP-CB-UI-CLASSB/` (LOD400-VERDICT via commit 45badf6) | PASS_WITH_FINDINGS |
| L-GATE_V R1 | *(pre-deploy run — no formal verdict file; R2 supersedes)* | — |
| L-GATE_V R2 | `_COMMUNICATION/TEAM_190/SFA-S003-P004/WP-CB-UI-CLASSB/WP-CB-UI-CLASSB_LGATE-V_VERDICT_R2_v1.0.0.md` | FAIL (deploy-precondition) |
| L-GATE_V R3 | `_COMMUNICATION/TEAM_190/SFA-S003-P004/WP-CB-UI-CLASSB/WP-CB-UI-CLASSB_LGATE-V_VERDICT_R3_v1.0.0.md` | **PASS_WITH_FINDINGS** (closing verdict) |
| LOD400 spec verdict (team_190) | `_COMMUNICATION/TEAM_190/SFA-S003-P004/WP-CB-UI-CLASSB/LOD400-VERDICT_v1.0.0.md` | PASS_WITH_FINDINGS |

Note: All four verdict files remain in-place at `_COMMUNICATION/TEAM_190/SFA-S003-P004/WP-CB-UI-CLASSB/` (cross-referenced, not moved — team_190 owns that dir structure).

---

## Deploy Report Reference

`_archive/SFA-S003-P004-WP-CB-UI-CLASSB/team_99/SFA-S003-P004-WP-CB-UI-CLASSB/DEPLOY_REPORT_v1.0.0.md`
- Status: SUCCESS
- deployed_sha: `c51c2e5` (short) / `c51c2e57bb70698bbf2ff5f179188bb94951f6c0` (full, from L-GATE_V R3 verdict)
- branch_head at L-GATE_V R3: `5ead7e1c2138f96284f246e57d0bda61e1f91be1`
- pre_reset_sha (server main before checkout): `815acdc`

---

## Key Commit SHAs

| Commit | Description | Source |
|--------|-------------|--------|
| `c51c2e5` | Deployed SHA (live on sfa.nimrod.bio via FTPS) | deploy_report + L-GATE_V R3 verdict |
| `5ead7e1c2138f96284f246e57d0bda61e1f91be1` | Branch head at L-GATE_V R3 validation | L-GATE_V R3 verdict frontmatter |
| `4695fc7` | team_10 initial L-GATE_B build commit | roadmap.yaml gate_history |
| `45badf6` | team_190 L-GATE_S verdict commit | roadmap.yaml gate_history |
| `355be17` | Branch tip pushed before DEPLOY routed | roadmap.yaml DEPLOY gate notes |
| `815acdc` | Server main HEAD before checkout (pre-deploy) | DEPLOY_REPORT_v1.0.0.md |

---

## Design Handoff Reference

`_archive/SFA-S003-P004-WP-CB-UI-CLASSB/team_35/SFA-S003-P004-WP-CB-UI-CLASSB/`
- `DESIGN_MANDATE_team35_v2-surfaces_2026-06-02_v1.0.0.md` — team_35 design ruling on M-1 hub hero RTL
- `HANDOFF/` — Full design package: Board-B HTML, classb.css, classb.js, cropbook-v1.css/js, tokens.css, 12x hero webp + crop PNGs, spec deltas (A_COMPONENTS, A_DESIGN_TOKENS, A_TEMPLATES, A_OPEN_ISSUES, B_COMPONENTS-TEMPLATES)

---

## Files Moved (source → archive destination)

### TEAM_10
- `_COMMUNICATION/TEAM_10/SFA-S003-P004-WP-CB-UI-CLASSB/` → `_archive/SFA-S003-P004-WP-CB-UI-CLASSB/TEAM_10/SFA-S003-P004-WP-CB-UI-CLASSB/`
  - `BUILD_REPORT_v1.0.0.md`
  - `BUILD_REPORT_FIXALL_v1.0.0.md`

### TEAM_50
- `_COMMUNICATION/TEAM_50/SFA-S003-P004-WP-CB-UI-CLASSB/` → `_archive/SFA-S003-P004-WP-CB-UI-CLASSB/TEAM_50/SFA-S003-P004-WP-CB-UI-CLASSB/`
  - `QA_MANDATE_visual_2026-06-02_v1.0.0.md`
  - `VISUAL_QA_REPORT_2026-06-02_v1.0.0.md`
  - `VISUAL_QA_REPORT_REQA_v1.1.0.md`
  - `visual_evidence_2026-06-02/EVIDENCE_MANIFEST.md`

### team_99
- `_COMMUNICATION/team_99/SFA-S003-P004-WP-CB-UI-CLASSB/` → `_archive/SFA-S003-P004-WP-CB-UI-CLASSB/team_99/SFA-S003-P004-WP-CB-UI-CLASSB/`
  - `DEPLOY_REPORT_v1.0.0.md`

### TEAM_100
- `_COMMUNICATION/TEAM_100/SFA-S003-P004-WP-CB-UI-CLASSB/` → `_archive/SFA-S003-P004-WP-CB-UI-CLASSB/TEAM_100/SFA-S003-P004-WP-CB-UI-CLASSB/`
  - `DEPLOY_MANDATE_team99_2026-06-02_v1.0.0.md`
  - `DISPATCH_sfa_build_2026-06-02_v1.0.0.md`
  - `DISPATCH_sfa_build_FIXALL_2026-06-02_v1.0.0.md`
  - `FINDINGS_RESPONSE_LGATE-V_2026-06-03_v1.0.0.md`
  - `VALIDATION_MANDATE_team190_LGATE-S_2026-06-02_v1.0.0.md`
  - `VALIDATION_MANDATE_team190_LGATE-V_2026-06-02_v1.0.0.md`

### team_35
- `_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-UI-CLASSB/` → `_archive/SFA-S003-P004-WP-CB-UI-CLASSB/team_35/SFA-S003-P004-WP-CB-UI-CLASSB/`
  - `DESIGN_MANDATE_team35_v2-surfaces_2026-06-02_v1.0.0.md`
  - `HANDOFF/` (full design package — all subfiles and assets)

---

## Left In Place (intentionally not moved)

| Path | Reason |
|------|--------|
| `_COMMUNICATION/TEAM_190/SFA-S003-P004/WP-CB-UI-CLASSB/` (4 verdict files) | team_190 verdict dir — cross-referenced, mandate says leave originals; do not delete verdicts |
| `_COMMUNICATION/TEAM_190/MSG-team100-to-team190-SFA-S003-P004-WP-CB-UI-CLASSB-LGATE-V-2026-06-02.md` | Loose MSG in a shared team_190 dir, not a per-WP subfolder |
| `_COMMUNICATION/TEAM_100/MSG-team190-to-team100-WP-CB-UI-CLASSB-LGATE-V-VERDICT-2026-06-03.md` | Loose MSG in shared TEAM_100 dir (not a per-WP subfolder) |
| `_COMMUNICATION/TEAM_100/MSG-team190-to-team100-WP-CB-UI-CLASSB-LGATE-V-R2-VERDICT-2026-06-03.md` | Loose MSG in shared TEAM_100 dir |
| `_COMMUNICATION/TEAM_100/MSG-team190-to-team100-WP-CB-UI-CLASSB-LGATE-V-R3-VERDICT-2026-06-03.md` | Loose MSG in shared TEAM_100 dir |
| `_COMMUNICATION/TEAM_100/HANDOFF_SELF_100_WP-CB-DATA+CLASSB_PARALLEL_2026-06-02_v1.md` | Spans BOTH WPs (CB-DATA + CLASSB); belongs to neither exclusively; left in shared TEAM_100 dir |
| `_COMMUNICATION/team_35/MSG-team100-to-team35-SFA-S003-P004-WP-CB-UI-CLASSB-M1-hub-hero-2026-06-02.md` | Loose MSG file at team_35 root (not inside the WP subfolder); left in place |
| `_COMMUNICATION/team_191/` | team_191's own mandate directory — never touched |
| `_COMMUNICATION/team_00/` | Principal inbox — never touched |

---

## Branch Reconciliation (from docs — not git-verified)

Per mandate note and roadmap entries: `main` and `origin/claude/sfa-p004-cbdata-classb-2026-06-02` converged through the S003-P004 program via the messaging helper and team_99 deploy commits. The roadmap records `closed_at: 2026-06-03` with the branch pushed and team_99 deploying from `c51c2e5` on that branch. Branch cleanup (merge → main or deletion) is a separate action outside this archive mandate.

---

## Open INFO Follow-ups (non-blocking — log only)

1. **tokens.css legacy comment:** `--paper #f5f3ec` remains as a comment-only line in `public_assets/css/tokens.css` (live computed body background is correct `rgb(248,251,248)` via `--gj-paper #f8fbf8`). Cosmetic scrub candidate; noted at WP-CB-UI-ALIGN closure (F-190-CLASSB-V-R3-01).
2. **SRV-5 (live hub stats):** Design intent for `66 גידולים · 242 זנים` live counts remains PROPOSED/unapproved in `WP-SRV-IDEAS` register. Server-side; out of Class B scope. No action in this archive.

---

*Manifest authored by team_191 (Git/Files) per ADR042 archive mandate, 2026-06-03.*
