---
id: MANDATE_SFA-S003-P002-WP-UI-patch01_L-GATE_B_v1.0.0
from: Team 100 (Chief System Architect — smallfarmsagents spoke)
to: Team 10 (sfa_build — Claude Sonnet builder)
date: 2026-05-28
type: GATE_MANDATE
gate: L-GATE_B
wp: SFA-S003-P002-WP-UI-patch01
project: smallfarmsagents
status: ACTIVE
verdict: PENDING
engine_constraint: "IR#1 cross-engine. builder=team_10 (Claude Sonnet — you). QA=team_50 (Claude Haiku). L-GATE_V validator=team_190 (non-Claude — GPT-5.5/Cursor/Codex)."
resubmission_round: 1
---

# L-GATE_B Mandate — SFA-S003-P002-WP-UI-patch01

**WP-UI post-closure follow-up wave (items A/B/C/D)**
Track: A | Profile: L0 | Effort: SMALL | Risk: LOW

## 1. Mode — ADOPT-AND-OWN (not from-scratch)

team_100 authored and verified a complete draft of items B/C/D in-session. Your
job is to **adopt it as the canonical L-GATE_B build**: review every hunk, refine
for correctness/style parity, add test coverage, and produce the builder commit.
This is the team_00-directed orchestration model (Sonnet owns build; team_100
does not act as builder).

**Reference draft:** `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-UI-patch01/team100_draft.diff`
(7 files, 341 lines). The same changes are present in the working tree. If the
working tree is clean (fresh worktree), `git apply` the diff.

## 2. Prior Gate History

| Gate | Result | Date | Validator |
|------|--------|------|-----------|
| L-GATE_E | PASS | 2026-05-28 | team_00 (in-session + DECISION_WP-UI-followup) |
| L-GATE_S | PASS | 2026-05-28 | team_100 (fast-track, SMALL/LOW, code-proven) |

This is Round 1 for L-GATE_B.

## 3. Scope — 4 items

Read the binding spec first: `_aos/work_packages/S003/SFA-S003-P002-WP-UI-patch01/LOD400_spec.md` (§2 scope, §4 ACs, §5 phases).

- **A (og-default):** prompt-routing already done by team_100. No build code
  beyond confirming `_layout.php` fallback ref. Image + integration DEFERRED.
- **B (community feed):** `app/Lib/CommunityFeed.php` (`SFA\Lib`, read-only) +
  `data/community_feed.json` + wire into `templates/shell/desktop.php` `dt-acc--comm`.
  **Desktop only.** NO write surface (no POST, no DB write, no community table).
- **C (deploy script):** `scripts/ftp_deploy_sfa_ui.sh` (Option B: composer
  install --no-dev then lftp) + `documentation/05-admin-and-operations/UI_DEPLOY_RUNBOOK.md`.
- **D (module hero slot):** `templates/macros/module_card.php` hero `<img>` when
  `hero_url` set + `hub.css` `.mod-card__hero` cover rule. 8 hero prompts already
  routed. Image + `modules.php hero_url` wiring DEFERRED.

## 4. Validation Criteria — 19 ACs (LOD400 §4)

AC-01..AC-19. Summary: B = AC-01..06, C = AC-07..11, D = AC-12..15, A = AC-16,
D-prompts = AC-17, global = AC-18 (`validate_aos.sh` 0 FAIL) + AC-19 (`composer
test` 0 new failures). **Do not skip ACs.** AC-16/17 are already satisfied
(prompt artifacts exist) — verify, don't recreate.

## 5. You MUST add test coverage (this is the QA-prep delta over the draft)
- phpunit for `CommunityFeed::recent()` — limit clamp, ≤3 rows, all 7 keys,
  fallback on missing/invalid JSON, `normalize` invalid-kind→'data'.
- phpunit (or render-harness assertion) for `module_card` hero: img emitted when
  `hero_url` set, absent when unset.
- Place under `sfa_delivery/tests/` following existing test conventions.

## 6. Constraints (binding)
- **IR#4:** team_100 is sole roadmap writer. Do NOT touch `_aos/roadmap.yaml`.
- **No locked-file changes** beyond the 5 code files in scope.
- **No `vendor/` commit** (Option B — stays gitignored).
- **No community write surface** (LV-S-1 binding from parent WP-UI).
- **Do NOT touch unrelated parallel-session working-tree changes** (`data/jmf/`,
  `data/external_sources/`, `.env.example`, `CHANGELOG.md`) — other WPs own those.
  Stage ONLY the 7 patch files for your commit.
- **Deploy is NOT in L-GATE_B scope** — it is gated on team_00 media + a bundled
  L-GATE_V pass. Do not deploy.

## 7. Output
- **BUILD_REPORT:** `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-UI-patch01/BUILD_REPORT_v1.0.0.md`
  (Build summary | engine+branch | 19-AC table w/ evidence | findings | validate_aos output | artifacts | next step).
- **Branch:** `claude/sfa-ui-patch01` (builder commit separate from any team_100 commit — IR#4).
- **Next step:** flag QA readiness for team_50 in BUILD_REPORT §next.

*Enforcement: STANDARD. BUILD_PARTIAL/FAIL → stop, write report, hand back to team_100; no QA/L-GATE_V dispatch from a non-COMPLETE build.*
