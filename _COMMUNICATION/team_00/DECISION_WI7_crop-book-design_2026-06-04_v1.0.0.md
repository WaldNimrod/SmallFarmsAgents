# DECISION — WP-CB-UI-WI7 crop-book design questions — team_00 — 2026-06-04

Recorded via /AOS_decide. Decider: team_00 (Nimrod). Supersedes the team_35 design mandate.

| Q | Topic | Decision |
|---|---|---|
| **Q2** | Market category chip wording | **APPROVED as-is** — keep all 10 live Hebrew labels (ירוקי עלים / ירקות פרי / פירות / ירקות שורש / סלים / כרוביים / בצליים / דלועיים / קטניות טריות / ביצים). No change. |
| **Q3** | Yield / nutrient-removal unit | **B — ק״ג/דונם.** Stored value is per-hectare (confirmed 67–100 kg/ha); team_10 must **divide by 10** (1 ha = 10 dunam) for all `kg_per_ha` fields AND relabel ק״ג/דונם. (Never relabel without the ÷10 — 10× error.) |
| **Q4** | Season model + "מתאים לקיץ" semantics | **Data CLOSED:** 4-level graded model (מועדף/מתאים/אפשרי/לא-מתאים = 3/2/1/0 season-months in sow∪transplant), semantics = sown/transplanted in season; 45-crop matrix approved. **Build = FUTURE WP `WP-CB-SEASON-VIZ`** (graded model + visual season interface using crop icons). NOT in WI-7 build. |
| **Q5** | English mono eyebrows | **B — Hebraize the menu-like tiles** (CROP-BOOK→ספר, MARKET→מחירון, CALC→מחשבון, FIELD-LOG→יומן); keep audience eyebrows (FARMER/GARDENER) as styled bilingual. |

**Also (team_00):** comprehensive full-system visual QA vs ALL mockups (Board-A + Board-B) requested before launch confidence → routed to team_50 (`WP-PRELAUNCH-QA` re-audit on live acca9b2).

**WI-7 build scope (team_10) after this:** Q3 (dunam ÷10) + Q5 (menu eyebrows) + 2 INFO cleanups. Q2 = no change. Q4 = deferred to WP-CB-SEASON-VIZ. Fold with the team_50 re-audit punch-list into one build/deploy.
