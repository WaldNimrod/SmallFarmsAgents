# VALIDATION MANDATE — WP-CB-UI-patch01 (L-GATE_V) — team_100 → team_190 — v1.0.0

**Date:** 2026-06-03 · **From:** team_100 (Opus) · **To:** team_190 (NON-CLAUDE, IR#1/#5) · **Routed by:** team_00
**Repo:** `/Users/nimrod/Documents/SmallFarmsAgents` · branch `claude/ui-polish-hub-cropbook-2026-06-03` (tip 3c74c87)
**Gate:** L-GATE_V — live visual confirmation after team_99 deploys. **Precondition:** team_99 DEPLOY_REPORT SUCCESS.

## 0. Cross-engine (IR#1/#5)
Builder = Claude Sonnet (team_10); L-GATE_B verifier = Claude Opus (team_100). This L-GATE_V MUST run on a non-Claude engine; confirm in the header.

## 1. Context
Two delivery-tier UI fixes from team_00 live feedback (LOD `_aos/work_packages/S003/SFA-S003-P004-WP-CB-UI-patch01/LOD400_spec.md`):
WI-1 compact `/crop-book/` entry (dense crop grid); WI-2 hub open-tools row full-width + a 4th "יומן השדה / Field Log" בפיתוח teaser. team_100 L-GATE_B PASS (composer 149/149, validate 0 FAIL).

## 2. Checks (live + code)
- **C1 (hub `/`):** the open-tools row spans the **full content width** (no trailing empty gap) — `.hub-grid` uses `auto-fit`; there are **4 tiles** (3 live + the Field-Log teaser).
- **C2 (Field-Log tile):** renders **"יומן השדה"** + **"בפיתוח"**, class `is-dev`, **non-clickable** (no href / aria-disabled), palette-consistent (muted/dashed). It must read as in-development — NOT as an available tool.
- **C3 (crop-book `/crop-book/`):** the crop grid is **markedly denser** — clearly more cards per row + per viewport than before (target ≥5–6 columns at desktop); cards compact; **no horizontal overflow**; RTL intact; filters/search/audience toggle still work; page still 200.
- **C4 (mobile):** `/` and `/crop-book/` remain legible at narrow width (few columns, no break).
- **C5 (constitutional):** delivery-tier only (no `_aos/`/Python/migration); palette unchanged (#f8fbf8, no cream); classb.css last; composer green (159); validate_aos 0 FAIL; IR#4 (no builder roadmap edit).
- **C6 (hub copy, WI-3):** the GARDENER audience card reads **"גנן"** (NOT "גינאי ביתי"); the hub-intro tagline *"ספר גידולים קהילתי, מחירון שוק בזמן-אמת, ומחשבון שדה — בנויים על ניסיון שדה ומחקר AI."* renders on **ONE line** at desktop, wraps cleanly on mobile, **no horizontal overflow**.
- **C7 (terminology, WI-3):** customer-facing copy uses **"חקלאות מקומית" / "חקלאי מקומי"** — no remaining "חקלאות קטנה"/"חקלאי קטן" on `/`, `/community`, `/market/` (disclaimer), or the page subtitle. (Unrelated "קטן/קטנה" — small garden, small contribution — may remain.)
- **C8 (Tend removed, WI-3):** `/about` (tiers) and crop/variety pages carry **no customer-facing Tend integration/connection** mention (neutralized to generic field-data wording).
- **C9 (hub CTA, WI-4):** the hub `/` shows a `.hub-cta` section with two offers — secondary "שתפו אותנו במידע והשלמות לספר" → /community, and a **primary** "ספרו לנו מה תרצו שנפתח לחווה שלכם" → WhatsApp/contact. Both links work; primary is visually prominent; RTL + responsive (stacks on mobile).

## 3. Verdict → `_COMMUNICATION/team_190/SFA-S003-P004/WP-CB-UI-patch01/WP-CB-UI-patch01_LGATE-V_VERDICT_v1.0.0.md`
```yaml
wp: SFA-S003-P004-WP-CB-UI-patch01
gate: L-GATE_V
validator_engine: <non-Claude>
result: PASS | PASS_WITH_FINDINGS | FAIL
checks: <n/5>
findings: [...]
summary: ...
```
On PASS → team_100 advances to LOD500_LOCKED + records gate. On FAIL → back to team_10.

## 4. Cursor prompt (paste into the non-Claude validator)
> You are team_190 on a NON-CLAUDE engine (confirm in header; IR#1/#5). Repo `/Users/nimrod/Documents/SmallFarmsAgents`,
> branch `claude/ui-polish-hub-cropbook-2026-06-03`, deployed live to sfa.nimrod.bio. Gate: L-GATE_V for WP-CB-UI-patch01.
> Run §2 checks against the LIVE site + the code: hub `/` open-tools row full-width with a 4th non-clickable
> "יומן השדה / בפיתוח" `is-dev` tile; `/crop-book/` crop grid markedly denser (≥5–6 cols, no overflow, RTL ok,
> filters work); mobile legible; delivery-tier-only + composer 149 + validate 0 FAIL. Emit the verdict YAML (§3).
