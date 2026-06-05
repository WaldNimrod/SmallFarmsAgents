---
id: MSG-team100-to-team99-20260604-002
schema_version: aos_v1_team_messaging
from_team: team_100
to_team: team_99
type: task
subject: "EXECUTE DEPLOY — WP-CB-UI-FIDELITY @ 8ce4fe1 (FIDELITY + visual remediation + 70 crop icons + patch01 WI-8/9)"
date: 2026-06-04
status: SENT
priority: high
related_wp: SFA-S003-P004-WP-CB-UI-FIDELITY
mandate_branch: claude/ui-polish-hub-cropbook-2026-06-03
mandate_ref: "_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-UI-FIDELITY/DEPLOY_MANDATE_team99_2026-06-04_v1.0.0.md"
deploy_sha: 8ce4fe1
expects_response: true
---

## Subject
EXECUTE DEPLOY — WP-CB-UI-FIDELITY @ `8ce4fe1` to sfa.nimrod.bio

## Body
team_00 approved. Please execute the delivery-tier deploy of branch `claude/ui-polish-hub-cropbook-2026-06-03` at **HEAD `8ce4fe1`** (pushed to origin) to uPress (`sfa.nimrod.bio`), per the mandate:
`_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-UI-FIDELITY/DEPLOY_MANDATE_team99_2026-06-04_v1.0.0.md`

**What's in this deploy (one shot):**
1. FIDELITY blocker fixes — number formatting (no raw floats), Hebrew units, Hebrew market category chips, single crop hero (dedup), working **עונה**/dtm filters + restored leading-questions.
2. Visual remediation — card grid restored to 168px (team_35 template); crop detail page centered (`.cb-crop-detail max-width:1120px`, fixes the full-width stretch); toggle aligned.
3. **70/70 crop watercolor icons** — **67 new/changed `public_assets/img/crops/wc-*.png` (~49 MB) MUST upload.** A CSS-only mirror would leave crops on the generic glyph — confirm the image tree mirrors.
4. patch01 **WI-8/WI-9** (`/crop-book/table` @375 RTL overflow) rides along — clears the residual deferred at patch01 R2.

**Key deploy notes:**
- **Bump `?v=`** (cache-bust) — fixes are in `crop-book-v1.css`, `crop-book-deep.css`, `classb.js`, templates.
- **Ensure `public_assets/img/crops/` is in the FTPS mirror set** (the visible payload is the images).
- composer **192/192**, validate **0 FAIL**, delivery-tier only, IR#4 clean.

**After deploy** — run the mandate §"Post-deploy smoke" (1–7), especially: crop cards show real art (not 🌱), formatted numbers + Hebrew units on `/crop-book/lettuce/`, Hebrew market chips, `?season=summer` non-empty, served `wc-strawberry.png`/`wc-potato.png`/`wc-wheat.png` = 200. Then write `_COMMUNICATION/team_99/SFA-S003-P004-WP-CB-UI-FIDELITY/DEPLOY_REPORT_v1.0.0.md` (deployed SHA `8ce4fe1` + new `?v=` + count of wc-*.png served) and notify team_100.

team_100 then routes **team_190 (non-Claude) FIDELITY L-GATE_V** on the live site (the launch gate).

— team_100 (Chief System Architect, Claude Opus) 2026-06-04
