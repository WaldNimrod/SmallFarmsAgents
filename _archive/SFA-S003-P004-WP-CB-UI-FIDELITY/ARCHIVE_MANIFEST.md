---
id: ARCHIVE_MANIFEST_SFA-S003-P004-WP-CB-UI-FIDELITY
wp: SFA-S003-P004-WP-CB-UI-FIDELITY
status: DONE
lod_status: LOD500_LOCKED
closed_at: "2026-06-04"
archived_at: "2026-06-04"
archived_by: team_100
archive_method: "L2 spoke self-archive (ADR034 R9 — git commit is the audit record)"
closing_verdict: "_COMMUNICATION/team_190/SFA-S003-P004/WP-CB-UI-FIDELITY/WP-CB-UI-FIDELITY_LGATE-V_VERDICT_v1.0.0.md"
roadmap_entry: "_aos/roadmap.yaml → id: SFA-S003-P004-WP-CB-UI-FIDELITY"
archive_root: "_archive/SFA-S003-P004-WP-CB-UI-FIDELITY/"
live_sha: acca9b2
served_asset_version: 1780576560
---

# Archive Manifest — SFA-S003-P004-WP-CB-UI-FIDELITY

**WP:** Crop-book + market UI fidelity & Hebrew localization remediation (pre-launch) + visual round (cards/centered crop page/toggle) + **70 crop watercolor icons**.
**Final status:** DONE / LOD500_LOCKED · **Live:** https://sfa.nimrod.bio @ `acca9b2` (`?v=1780576560`).
**Branch:** `claude/ui-polish-hub-cropbook-2026-06-03`.

## Gate Ladder
| Gate | Result | Date | Validator | Notes |
|------|--------|------|-----------|-------|
| L-GATE_E | PASS | 2026-06-04 | team_00 | CDP audit confirmed launch-blocking defects on crop/market pages |
| L-GATE_S | PASS_WITH_FINDINGS | 2026-06-04 | team_190 (Cursor/GPT-5.x, non-Claude) | LOD v1.1.0; rootcause 5/5, precision 5/5, constitutional 5/5; 1 MINOR folded |
| L-GATE_B | PASS | 2026-06-04 | team_100 (Opus) | team_10 build WI-1..9 + Decisions A/B + visual round + 70 icons; render-harness 19/19; composer 192/192 |
| DEPLOY r1 | SUCCESS_WITH_1_FINDING | 2026-06-04 | team_99 | `4c9bab2` blockers live; prov__srcval finding → FIXED (acca9b2) |
| DEPLOY r2 | SUCCESS | 2026-06-04 | team_99 | `acca9b2` — 67 watercolors + code (80 files); all smoke PASS; `?v=`→1780576560 |
| L-GATE_V | **PASS_WITH_FINDINGS** | 2026-06-04 | team_190 (Cursor Agent GPT-5.x, non-Claude) | **launch gate** — AC-1..AC-7 pass on live; 3 INFO; **closing verdict** |

## What shipped
- **Blockers:** D-1 number formatting (incl. discrete-unit int rounding + provenance values), D-2 Hebrew unit map, D-3 market category Hebrew labels, D-4 season-from-months filter (`sowing_months ∪ transplant_months`) + restored leading-questions, D-5 hero dedup + green-blob removal + `#identity` retarget.
- **Visual round:** card grid restored to team_35 168px; crop detail centered (`.cb-crop-detail max-width:1120px`); view-toggle aligned.
- **Icons:** 70/70 crops with watercolor art — 14 recovered via slug-map fix + **43 new Devora masters** (Nano Banana / gemini-2.5-flash-image, session recipe), cream→alpha knockout baked into `wc_derivatives.sh`.
- Key commits: build `0cbd5b8`/`4c9bab2`; visual `ea9b975`; icons `67195a4`/`8ce4fe1`; prov fix `acca9b2`. composer 192/192, validate 0 FAIL.

## Verdict refs (team_190 dir — left in place)
- L-GATE_S: `_COMMUNICATION/team_190/SFA-S003-P004/WP-CB-UI-FIDELITY/WP-CB-UI-FIDELITY_LGATE-S_VERDICT_v1.0.0.md`
- L-GATE_V (closing): `…/WP-CB-UI-FIDELITY_LGATE-V_VERDICT_v1.0.0.md`

## Files moved (source → archive)
| Source | Destination |
|---|---|
| `_COMMUNICATION/TEAM_10/SFA-S003-P004-WP-CB-UI-FIDELITY/` (build reports v1.0–v1.3) | `…/TEAM_10/SFA-S003-P004-WP-CB-UI-FIDELITY/` |
| `_COMMUNICATION/TEAM_100/SFA-S003-P004-WP-CB-UI-FIDELITY/` (LOD-handoff mandates, L-GATE_B verdict, deploy mandate, design/decision/audit/visual-audit + audit_evidence + live_evidence_acca9b2 + Gemini-recipe request) | `…/TEAM_100/SFA-S003-P004-WP-CB-UI-FIDELITY/` |
| `_COMMUNICATION/team_99/SFA-S003-P004-WP-CB-UI-FIDELITY/` (DEPLOY_REPORT v1.0.0 + v2.0.0) | `…/team_99/SFA-S003-P004-WP-CB-UI-FIDELITY/` |

> **Amendment 2026-06-05:** the team_99 DEPLOY_REPORT v1/v2 (originally noted "left in place")
> were moved here to satisfy Iron Rule #15 / validate_aos Check 15 — a `_COMMUNICATION/team_*/`
> dir named for a COMPLETE+LOD500 WP is a stale artifact. `roadmap.yaml` `report_ref`s for both
> reports were updated to the archived paths in the same change.

## Left in place
- `_COMMUNICATION/team_190/SFA-S003-P004/WP-CB-UI-FIDELITY/` (verdicts) — nested under `SFA-S003-P004`; cross-referenced.
- Loose `MSG-team190-to-team100-…` / `MSG-team100-to-team99-…` in shared team dirs.

## Open INFO follow-ups (non-blocking — from L-GATE_V verdict)
1. **WI-7 (team_35 design completions):** English mono eyebrows (Board-B decorative), category wording (Q2), dunam-vs-hectare unit (Q3), fuller leading-question set + "מתאים לקיץ" semantics (Q4), eyebrow Hebraization (Q5). DESIGN_REQUEST filed; tracked separately.
2. **Calc page JSON embed** carries English field keys (machine payload, NOT user-visible) — cosmetic scrub candidate.
3. **Dead legacy route** `/crop-book/table?category=summer` still resolvable though the UI now uses `?season=summer` — remove/redirect in a future cleanup.

*Self-archived by team_100 per ADR042 closure protocol on L-GATE_V PASS, 2026-06-04. git commit is the audit record (ADR034 R9, L2 spoke).*
