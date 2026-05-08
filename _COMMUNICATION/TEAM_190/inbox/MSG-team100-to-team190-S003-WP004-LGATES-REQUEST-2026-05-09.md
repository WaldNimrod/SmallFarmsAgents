---
id: MSG-team100-to-team190-S003-WP004-LGATES-REQUEST-2026-05-09
type: MESSAGE
subtype: VALIDATION_REQUEST
gate: L-GATE_SPEC
round: 1
from: team_100
to: team_190
date: 2026-05-09
project: smallfarmsagents
wp: SFA-S003-P001-WP004
priority: NORMAL
expects_reply: true
reply_artifact: _COMMUNICATION/team_190/SFA-S003-P001-WP004/LOD400-VERDICT_v1.0.0.md
---

# L-GATE_SPEC Validation Request — SFA-S003-P001-WP004

**From:** team_100 (Chief Architect)
**To:** team_190 (Senior Constitutional Validator — non-Claude per Iron Rule #1)
**Gate:** L-GATE_SPEC, Round 1
**Date:** 2026-05-09
**Bundle commit:** `38208ee` on branch `claude/strange-mcnulty-651551`

---

## §1 Request

Please conduct L-GATE_SPEC Round 1 constitutional review for **SFA-S003-P001-WP004** — the WordPress integration LOD400 spec for ספר גידולים.

This is a **single-WP review** (Phase 2 of S003). Phase 1 (WP002 + WP003) is LOD500_LOCKED and not under review.

## §2 Bundle location

```
_COMMUNICATION/TEAM_100/SFA-S003-P001-WP004/EXTERNAL_VALIDATION_BUNDLE/
├── AOS_MAIL_PROMPT.md             ← compact activation
├── MANIFEST.md                    ← C1–C12 checklist + risk register + verdict format
└── TEAM_190_ACTIVATION_PROMPT.md  ← full governance + read order
```

Start with `AOS_MAIL_PROMPT.md`.

## §3 Primary review target

`_aos/work_packages/S003/SFA-S003-P001-WP004/LOD400_spec.md`

17 sections. 16 ACs. 12-case filter-parity matrix. 6-item risk register.

## §4 Verdict

Write to: `_COMMUNICATION/team_190/SFA-S003-P001-WP004/LOD400-VERDICT_v1.0.0.md`
Confirmation reply to team_100: `_COMMUNICATION/TEAM_100/MSG-team190-to-team100-S003-WP004-LOD400-VERDICT-[DATE].md`

§0 verdict box format mandatory (see MANIFEST.md §5).

## §5 Context highlights for the validator

- **Architecture is decided** by team_00 (4 locked decisions, recorded in spec §17): separate JSON data file, mu-plugin shortcode, LARGE effort, CLI-only publish. These are not under review — but the spec's *implementation* of them is.
- **Filter parity is the central correctness invariant.** The Flask `crop_book/views.py:234-304` is the semantic SSoT. The SPA must mirror exactly. Spec §8.2 + §11.1 cover this — verify the matrix is sufficient.
- **Manual mu-plugin install** is the only operational dependency on team_00 (precedent: `sfagent-allow-json.php`). Verify the runbook section makes this actionable.
- **Bezeq port-21 block** rules out FTPS for this profile — spec §5.4 explicitly disables FTPS fallback for `profile="crop_book"`. Verify this is constitutionally sound.

## §6 Done criteria for this thread

You acknowledge by writing the verdict file + reply MSG. team_100 will read both at next session start (path patterns are watched). No further team_100 action required this thread until verdict lands.

---

*Sent 2026-05-09 by team_100 (filesystem AOS_SendMail equivalent — DB online but spoke-native artifact pattern per Iron Rule #6).*
