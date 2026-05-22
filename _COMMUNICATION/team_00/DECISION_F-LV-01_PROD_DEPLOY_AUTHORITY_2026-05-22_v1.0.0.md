---
id: DECISION_F-LV-01_PROD_DEPLOY_AUTHORITY_v1.0.0
type: DECISION_RECORD
gate: closure_follow_up
from: team_00 (Principal)
recorded_by: team_100 (smallfarmsagents)
date: 2026-05-22
related_wp: SFA-S003-P001-WP004
related_finding: F-190-WP004-LV-01
verdict_ref: _COMMUNICATION/team_190/SFA-S003-P001-WP004/LGATEV-VERDICT_v1.0.0.md
decision_brief_format: /AOS_decide
status: APPROVED
authority: team_00 (Principal — single human authority, IR §0)
next_step: "team_100 to file GCR-class amendment to hub MANDATE_TEMPLATE.md adding `prod_deploy_authority` field per Hybrid Option C. Local DISPATCH composition in this spoke applies Hybrid policy immediately."
handoff_to: team_100
handoff_context_pointer: _COMMUNICATION/team_00/DECISION_F-LV-01_PROD_DEPLOY_AUTHORITY_2026-05-22_v1.0.0.md
---

# Decision Record — F-LV-01 Production-Deploy Authority

## §1 Decision

**Option C (Hybrid) APPROVED** per team_00 directive 2026-05-22.

`prod_deploy_authority` becomes a mandatory DISPATCH field with three valid values:
- `builder` — L-GATE_B builder may execute production deploy steps in-session (default for L0 / SMALL WPs)
- `team_99` — production deploy routed to team_99 server ops (default for LARGE / production-critical WPs)
- `amend_required` — DISPATCH amendment + team_00 approval required before any prod deploy (security-sensitive WPs)

team_100 sets the value at L-GATE_S based on WP effort tier + risk profile. team_00 may override at L-GATE_E.

## §2 Principal emphasis (team_00 directive 2026-05-22)

> "אנחנו פועלים בשלבים אבל בתוצאה הסופית צריכה להיות פריסה מלאה — זה לא שיש לנו לקוחות כרגע — זה שרת סטייגינג שלנו לפיתוח ובדיקות אין טעם להשאיר פערים — אנחנו צריכים מערכת תקינה ומלאה וקוד אחיד בלי ענפים וגרסאות בסוף התהליך."

**Translation + binding interpretation for team_100 orchestration:**

The staging server (nimrod.bio) is for internal development and testing — no live customer load. Multi-step deployment is acceptable as a work pattern, but the **end-state of every program** must satisfy three invariants:

1. **Unified deployment**: production reflects the full intended functional surface — no partial deploys remaining as "WIP".
2. **Single canonical branch**: all feature branches are merged to `main` (or otherwise retired) — no orphan branches surviving past program closure.
3. **No version drift**: the same code base is the source of truth for staging and production — no separate "deploy versions" diverging from the working tree.

team_100 orchestration MUST validate these three invariants at **program closure** (after L-GATE_V PASS of the final WP, before issuing the team_191 archive mandate). Failing closure: open a follow-up cleanup WP before issuing closure artifacts.

## §3 Application to S003 WP004 (retroactive)

WP004 is already LOD500_LOCKED (2026-05-13). Retroactive review per the three invariants:

| Invariant | Status | Notes |
|-----------|--------|-------|
| Unified deployment | ✓ PASS | Site live at https://www.nimrod.bio/crop-book/ with full SPA + data + manifest. No partial deploy artifacts remaining. |
| Single canonical branch | ⏳ PENDING | Working branch `claude/gallant-elbakyan-727a60` carries WP004 + this decision + patch02 (forthcoming). Closure merge to `main` to occur after patch02 LOD500_LOCKED + all GCR resolutions land. |
| No version drift | ✓ PASS | Production reflects `claude/gallant-elbakyan-727a60` HEAD (the only code base for crop_book). |

**Closure obligation accepted** — team_100 will not close the S003 program (issue final archive notification) until the canonical-branch merge happens.

## §4 Application to WP004 builder out-of-mandate deploy

team_10's prod deploy during WP004 build (mu-plugin upload + WP page + option set + cache clear) is **retroactively classified** as `prod_deploy_authority: builder` — a permitted action under the new Hybrid policy. No process violation. The L-GATE_V finding F-LV-01 stands as historical record of the decision-trigger; no remediation required.

## §5 Forward orchestration actions for team_100

1. **Local lean-kit cannot be edited** in spokes (CLAUDE.md AOS Spoke Notice — `_aos/` is read-only snapshot from hub). All template changes belong to hub team_100.
2. **GCR amendment required**: file/amend a GCR to hub team_100 adding `prod_deploy_authority` field to `lean-kit/modules/validation-quality/templates/MANDATE_TEMPLATE.md`. Recommend bundling with the in-flight `GCR_AOS_MESSAGING_INFRA_HARDENING` as a §-amendment, OR a separate `GCR_DISPATCH_PROD_DEPLOY_AUTHORITY` if the messaging GCR has already passed L-GATE_S.
3. **Local DISPATCH composition** by team_100 starts applying Hybrid immediately: all DISPATCH artifacts from this date forward include the `prod_deploy_authority` line.
4. **Program closure checklist** added to team_100 self-handoff template: validate the three end-state invariants before issuing archive mandate.

## §6 Cross-references

- Finding: `_COMMUNICATION/team_190/SFA-S003-P001-WP004/LGATEV-VERDICT_v1.0.0.md` §3 Note 1 + §4 F-190-WP004-LV-01
- Decision brief: in-chat to team_00, 2026-05-22 (per `/AOS_decide` format)
- Related GCR (potential bundle target): `_COMMUNICATION/TEAM_100/GCR_AOS_MESSAGING_INFRA_HARDENING_2026-05-10_v1.0.0.md`
- Hub canonical template: `lean-kit/modules/validation-quality/templates/MANDATE_TEMPLATE.md` (READ-ONLY snapshot in spoke at `_aos/lean-kit/...`)

---

*Decision recorded 2026-05-22 by team_100 (smallfarmsagents) on behalf of team_00 (Principal).*
*Branch: `claude/gallant-elbakyan-727a60` · Commit: pending.*
