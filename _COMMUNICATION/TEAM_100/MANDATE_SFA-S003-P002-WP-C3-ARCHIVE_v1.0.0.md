---
id: MANDATE_SFA-S003-P002-WP-C3-ARCHIVE_v1.0.0
from: team_100 (Chief System Architect — Claude Opus 4.7)
to: team_191 (Git/Files / Archive Steward)
date: 2026-05-27
type: ARCHIVE_MANDATE
gate: post-L-GATE_V (LOD500_LOCKED)
wp: SFA-S003-P002-WP-C3
project: smallfarmsagents
priority: NORMAL
status: ACTIVE
authority: team_100 (post-L-GATE_V PASS by team_190 R2 — verdict commit reviewed `ffbc7fa`)
parent_authorization: team_00 Decision Brief response 2026-05-27 20:00 IDT (Q2=A — close WP-C3 now)
canon_ref: methodology/AOS_GATE_MANDATE_CANON_v1.0.0.md (Signal B.0 auto-archive); lean-kit/modules/gate-workflow/POST_GATE_ARCHIVE_PROCEDURE.md v1.1.0
---

# Archive Mandate — SFA-S003-P002-WP-C3

**ADR042 Step 1 of 3** — issued by team_100 immediately on L-GATE_V R2 PASS receipt. Step 2 (roadmap LOD500_LOCKED flip) executed in this same session on commit (forthcoming). Step 3 (multi-engine propagation) **N/A** — no `core/governance/` modifications in this WP.

## 1. WP context

| Field | Value |
|-------|-------|
| WP ID | SFA-S003-P002-WP-C3 |
| Label | ספר גידולים: Wave 3 — Secondary Sources + OCR + Backlog Sweep |
| Milestone | S003 |
| Program | SFA-S003-P002 (Data Enrichment) |
| Track | A |
| Effort | MEDIUM |
| Profile | L0 |
| Builder | sfa_build (team_10, Sonnet) |
| Validator | team_190 (external, non-Claude, GPT-5.5 / Cursor) |

## 2. Gate verdict references

| Gate | Round | Result | Commit | Verdict artifact |
|------|-------|--------|--------|-----------------|
| L-GATE_E | — | PASS | — | (in-session team_00 grant 2026-05-26) |
| L-GATE_S | — | PASS | — | (in-session team_10 self-attest 2026-05-26) |
| L-GATE_B | — | PASS | 99c1971 | `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-C3/HANDOFF_TO_190_SFA-S003-P002-WP-C3_2026-05-27_v1.md` |
| L-GATE_V | R1 | BLOCKED | 99c1971 | `_COMMUNICATION/TEAM_190/VERDICT_SFA-S003-P002-WP-C3_L-GATE_V_v1.0.0.md` |
| L-GATE_V | R2 | PASS | ffbc7fa | `_COMMUNICATION/TEAM_190/VERDICT_SFA-S003-P002-WP-C3_L-GATE_V_v1.0.1.md` |

## 3. Closure verdict summary (R2 — terminal)

- 10/10 ACs PASS (independent verification by team_190 GPT-5.5)
- F-C3-LV-01 BLOCKER RESOLVED (Curtis DTM `confidence_weight=0` field-specific moderation; `validate_enrichment.py` returns `CALIBRATED=5 MARGINAL=0 MISALIGNED=0`)
- F-C3-LV-02 + F-C3-LV-03 MAJOR evidence discrepancies sufficiently documented in `REMEDIATION_REPORT_v1.0.0.md` (OCR count 27/27, FRANCHI 27→21 reachable + 6 absent crops)
- validate_aos.sh: 29 PASS / 19 SKIP / 0 FAIL
- 12/12 focused `tests/crop_book/test_c3_*.py` green
- LOCKED_MATCH_COUNT:0 (no protected-file violations)
- Remediation commit scope clean: only `curtis_profiles_importer.py` + REMEDIATION_REPORT touched

## 4. Archive deliverable

team_191 to produce:

1. **Target directory:** `_archive/SFA-S003-P002-WP-C3/`
2. **Move into archive:**
   - `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-C3/` (full directory — BUILD_REPORT + REMEDIATION_REPORT + handoffs R1/R2)
   - `_COMMUNICATION/TEAM_190/VERDICT_SFA-S003-P002-WP-C3_L-GATE_V_v1.0.0.md`
   - `_COMMUNICATION/TEAM_190/VERDICT_SFA-S003-P002-WP-C3_L-GATE_V_v1.0.1.md`
   - `_COMMUNICATION/TEAM_190/MSG-HUB-20260527-001.md`
   - `_COMMUNICATION/TEAM_190/MSG-HUB-20260527-002.md`
   - `_COMMUNICATION/team_110/SFA-S003-P002-WP-C3/` (if exists — verify and include)
3. **Preserve in place (NOT archived):**
   - `_aos/work_packages/S003/SFA-S003-P002-WP-C3/LOD400_spec.md` (LOD500 reference for downstream WPs)
   - `organic_market_agent/crop_book/importer/urban_farmer/curtis_profiles_importer.py` (live production code)
   - Any tests under `tests/crop_book/test_c3_*.py` (live test suite)
4. **Archive manifest:** `_archive/SFA-S003-P002-WP-C3/ARCHIVE_MANIFEST.md` per `lean-kit/modules/gate-workflow/POST_GATE_ARCHIVE_PROCEDURE.md` v1.1.0 — list every moved file with source path + SHA; record verdict commits; record team_00 closure approval timestamp (2026-05-27 20:00 IDT).
5. **Validation requirement:** Post-archive run `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` — expect **29 PASS / 19 SKIP / 0 FAIL** (no regression). Check 15 (archive housekeeping) should PASS after this archival completes.

## 5. Completion signal

Write `_COMMUNICATION/team_191/SFA-S003-P002-WP-C3/COMPLETION_REPORT_v1.0.0.md` confirming:
- `ARCHIVE_MANIFEST.md` exists at `_archive/SFA-S003-P002-WP-C3/`
- validate_aos.sh post-archive output
- Commit SHA of the archive commit on `main`

Then notify team_100 (this session or successor) via standard inter-team message in `_COMMUNICATION/team_191/MSG-team191-to-team100-WP-C3-ARCHIVE-COMPLETE-2026-05-27.md`.

## 6. Iron-rule compliance

- **IR#4** (single roadmap writer): team_191 does NOT edit `_aos/roadmap.yaml` — that flip is owned by team_100 (this session, executed alongside this mandate).
- **IR#15** (post-gate archival): satisfied by this mandate per Signal B.0.
- **ADR034 R9**: spoke-native L2 WP — file-based SSoT; direct edit of `_aos/roadmap.yaml` is authorized; git commit serves as audit record.

---

*Mandate filed 2026-05-27 20:00 IDT by team_100 (Claude Opus 4.7, RE-BUILD orchestrator session) under team_00 Decision Brief Q2=A approval. No reply required from team_191 prior to executing — proceed when next available.*
