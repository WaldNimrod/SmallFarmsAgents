---
id: MANDATE_SFA-S003-P002-WP-UI-patch01_L-GATE_V_R2_v1.0.0
from: Team 100 (Chief System Architect — smallfarmsagents spoke)
to: Team 190 (Senior Constitutional Validator — NON-CLAUDE engine)
date: 2026-05-29
type: GATE_MANDATE
gate: L-GATE_V
wp: SFA-S003-P002-WP-UI-patch01
project: smallfarmsagents
status: ACTIVE
verdict: PENDING
resubmission_round: 2
engine_constraint: "IR#1 CROSS-ENGINE MANDATORY. Builder/orchestrator = Claude. You MUST be non-Claude (GPT-5.5/Cursor/Codex/Gemini). If you are any Claude model, STOP and decline."
prior_round: "R1 PASS (verdict de275ac) — validated the patch01 CODE (CommunityFeed, deploy script, module_card hero support, tests)."
---

# L-GATE_V Round 2 — SFA-S003-P002-WP-UI-patch01 (media addition re-check)

R1 already PASSED the code. **R2 scope = the visual-asset addition** committed in
`e8cd4ce` on branch `claude/sfa-ui-patch01`. The watercolor assets were composed
DETERMINISTICALLY from the authentic Devora brand masters (not AI-generated) — see
`_COMMUNICATION/TEAM_100/NIMROD_BIO_VISUAL_SYSTEM_CHATGPT/tools/compose_brand_assets.py`.

## 1. Inputs
- Branch `claude/sfa-ui-patch01` @ `e8cd4ce` (checkout this branch).
- R1 verdict: `_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-UI-patch01/LGATEV-VERDICT_v1.0.0.md`
- Spec: `_aos/work_packages/S003/SFA-S003-P002-WP-UI-patch01/LOD400_spec.md` (§4 ACs; A/D were deferred-media sub-items — now fulfilled).

## 2. Verify (R2 — additive scope only)
| # | Check | Pass condition |
|---|-------|----------------|
| R2-1 | `php -l sfa_delivery/modules.php` + `_layout.php` | no syntax errors |
| R2-2 | 8 hero assets present `public_assets/img/heroes/{crop-book,market,calc,planner,clients,inventory,tend-bridge,field-log}.webp` | all exist, each ≤90 KB |
| R2-3 | `og-default.webp` (≤120 KB), `hub-hero.webp`/`contact.webp` (≤140 KB), `favicon-32.png`, `apple-touch-icon.png` present | exist |
| R2-4 | `modules.php` `hero_url` for all 8 modules points to the matching existing file | 8 mappings, files exist |
| R2-5 | `module_card.php` renders `<img class="mod-card__hero">` for a module with `hero_url` (AC-13); icon reverts to corner (CSS `:has()`) | render check |
| R2-6 | **No text/wordmark baked into any hero image** (inventory uses `basket.png`, NOT the wordmark logo) | visual check of the 8 heroes |
| R2-7 | `_layout.php` og:image → `og-default.webp` (now present) + favicon links valid | grep + file exist |
| R2-8 | `composer test` (sfa_delivery) | 0 new failures vs R1 baseline (48 pass) |
| R2-9 | `validate_aos.sh .` | 0 FAIL |
| R2-10 | Scope: `git show --stat e8cd4ce` = only the media assets + `modules.php` + `_layout.php`; no other LOD500_LOCKED file touched; no `vendor/`; no roadmap edit | clean |

## 3. Output
- VERDICT: `_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-UI-patch01/LGATEV-VERDICT_R2_v1.0.0.md`
  (PASS | PASS_WITH_FINDINGS | FAIL + your non-Claude engine/version + R2-1..R2-10 results + findings).
- Notify team_100 via `_COMMUNICATION/TEAM_100/MSG-team190-to-team100-WP-UI-patch01-LGATEV-R2-...md`.

## 4. Notes
- Style/aesthetic judgement is team_00's (already approved the series); your job is
  constitutional + functional integrity of the addition, not art critique.
- On PASS → team_100 merges `claude/sfa-ui-patch01` → main, deploys to sfa.nimrod.bio,
  and sets LOD500_LOCKED. **Deploy is the immediate next step after your PASS.**
