# VALIDATION MANDATE + PROMPT — SFA-S003-P004-WP-CB-UI-CLASSB (L-GATE_V) — team_100 → team_190 — v1.0.0

**Date:** 2026-06-02
**From:** team_100 (Chief System Architect, Claude Opus)
**To:** team_190 (Independent Validator)
**Routed by:** team_00
**Repo:** `/Users/nimrod/Documents/SmallFarmsAgents` · branch `claude/sfa-p004-cbdata-classb-2026-06-02`
**Gate:** **L-GATE_V** — final constitutional + per-surface design-vs-live round for the Class B fix-all build.
**Precondition:** team_99 DEPLOY_REPORT = SUCCESS (live on sfa.nimrod.bio). Run AFTER deploy.

## 0. Cross-engine constraint (IR#1/#5 — MANDATORY)
Builder = team_10 (Claude Sonnet); L-GATE_B verifier + QA correctives = team_100 (Claude Opus) / team_50 (Claude Haiku). Therefore this L-GATE_V **MUST run on a NON-CLAUDE engine** (Cursor Composer / GPT-5.x / Codex). Confirm engine in the verdict header.

## 1. Context
Class B (hub/market list+detail/search/community/about/account) was previously built + merged + went live.
team_50 visual QA returned PASS_WITH_FINDINGS (2 MAJOR + 6 MINOR + 2 COSMETIC). Per team_00 ("fix ALL,
then resubmit"), team_10 fixed all 10 findings; team_100 independently verified L-GATE_B; team_50 re-QA
v1.1.0 = PASS. This gate confirms the fixes live + the Class B surfaces hold up to constitutional + design
fidelity review.

## 2. Artifacts
- **Build report:** `_COMMUNICATION/TEAM_10/SFA-S003-P004-WP-CB-UI-CLASSB/BUILD_REPORT_FIXALL_v1.0.0.md`
- **Re-QA:** `_COMMUNICATION/TEAM_50/SFA-S003-P004-WP-CB-UI-CLASSB/VISUAL_QA_REPORT_REQA_v1.1.0.md`
- **Original QA:** `…/VISUAL_QA_REPORT_2026-06-02_v1.0.0.md`
- **LOD400 (LOCKED v1.0.0):** `_aos/work_packages/S003/SFA-S003-P004-WP-CB-UI-CLASSB/LOD400_spec.md`
- **Design SSoT:** `_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-UI-CLASSB/HANDOFF/design/Board-B-…html`
- **SRV register (scope guard):** `_aos/work_packages/S003/SFA-S003-P004-WP-SRV-IDEAS/REGISTER.md` (SRV-5 = the MINOR-2 non-fix)

## 3. Checklist
### 3.1 Per-surface design-vs-live (desktop + mobile), each finding closed
- **C1 — Hub `/`:** the hero/intro no longer leaves a blank left band at wide viewport; intro + modtile grid share the bounded `.hub-home__inner` column (Board-B `hub-home`). No left-image regression.
- **C2 — Community `/community`:** the banner shows the `contact.webp` image (no bare beige `#f4ecdc` box); manifesto + feed-less reqcard intact.
- **C3 — Search `/search?q=<no-match>`:** `◐ בקשו` `.reqinfo` request CTA matches Board-B; → /community contribute.
- **C4 — Account `/account`:** the brand logo no longer overlaps the shell nav.
- **C5 — Market `/market/` + `/market/{slug}`:** table headers via `.ptable__th` (no inline `style`); mkt-disc always-on; 7י/28י active, 90י/שנה disabled; honest empty/stale states.
- **C6 — Footer:** `קהילה` is non-linking (`aria-current`) on `/community`, a link elsewhere; nav classes have no trailing space.
- **C7 — About `/about`:** 5-tier ladder intact.
### 3.2 Constitutional
- **C8 — Tokens/palette:** computed `body` ground `#f8fbf8`, no cream `#f5f3ec`; `tokens.css` + `cropbook-v1.*` unchanged (no palette drift); `classb.css` last in load order.
- **C9 — Scope:** the fix build touched delivery tier only (no `_aos/`, no Python, no migration, no LOCKED backend). IR#4 intact (no builder roadmap edits).
- **C10 — Scope-guard honesty:** MINOR-2 (live hub stats) correctly deferred to SRV-5 (server-side, out of Class B); COSMETIC-2 (canonical=production) correct on prod. Confirm no silent server-side change crept in.
- **C11 — Tests:** `composer test` green (135) on the deployed SHA; `validate_aos.sh` 0 FAIL.

## 4. Verdict → `_COMMUNICATION/team_190/SFA-S003-P004/WP-CB-UI-CLASSB/WP-CB-UI-CLASSB_LGATE-V_VERDICT_v1.0.0.md`
```yaml
wp: SFA-S003-P004-WP-CB-UI-CLASSB
gate: L-GATE_V
validator_engine: <non-Claude>
result: PASS | PASS_WITH_FINDINGS | FAIL
surface_checks: <n/7>
constitutional_checks: <n/4>
findings: [ {id: F-190-CLASSB-V-NN, severity: …, summary: …, evidence: …} ]
summary: <one paragraph>
```
- **PASS / PASS_WITH_FINDINGS** → team_100 advances WP-CB-UI-CLASSB to LOD500_LOCKED (records the QA + L-GATE_V gates in roadmap, incl. backfilling the team_50 QA gate) + ADR042 archive mandate → team_191.
- **FAIL** → findings back to team_10; re-deploy; R2.

## 5. Cursor prompt (paste into the non-Claude validator)
> You are **team_190**, validating on a **non-Claude** engine (confirm in the header — IR#1/#5). Repo
> `/Users/nimrod/Documents/SmallFarmsAgents`, branch `claude/sfa-p004-cbdata-classb-2026-06-02`, deployed
> live to sfa.nimrod.bio. Gate: **L-GATE_V** for the Class B QA fix-all build. Run the §3 checklist against
> BOTH the live site and the code (the 10 fixes are listed in the build report + dispatch
> `DISPATCH_sfa_build_FIXALL_2026-06-02_v1.0.0.md`). Compare each surface to the Board-B design frame. Verify
> the scope-guard (MINOR-2 → SRV-5, no server-side creep). Emit the verdict YAML (§4) to the path above.
