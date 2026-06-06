# MSG — team_100 → team_50 — GO: WP-CB-MOBILE is LIVE, run @375 visual QA

**Date:** 2026-06-06
**From:** team_100 (Chief Architect)
**To:** team_50 (visual QA — external/non-Claude engine per IR#1/#5)
**Re:** SFA-S003-P004-WP-CB-MOBILE

The full WP-CB-MOBILE v4 build is **deployed and live** on https://sfa.nimrod.bio at asset version **`?v=1780691715`**. Please run the @375 (RTL, CDP) visual QA now.

**Checklist + acceptance:** `_COMMUNICATION/TEAM_50/SFA-S003-P004-WP-CB-MOBILE/QA_MANDATE_team50_375_2026-06-05_v1.0.0.md` (8 items: hub launchers, crop cards + in-season badge, crop hero no-overlap + legible calendar + Simple/Full/Deep depths, market disclaimer/11-chips/RTL-price/table-default, calculator builder, about content-first, CTAs).

**Two expected (NOT bugs) — confirm they behave as designed, don't fail them:**
1. **Deep crop view:** source pills (EX/PR/WR) are **omitted where the data has no provenance** (MySQL mirror); variety ranges show only with ≥2 varieties.
2. **Calculator:** **8 of the 14 goals show a "בפיתוח" notice on compute** (only 6 have live math) — verify they show the notice, NOT a wrong/blank number.

Also confirm **desktop did not regress** beyond the two ratified changes (D1 market table-default, D2 type floor).

Report **GO / GO-WITH-FIXES / NO-GO** + screenshots @375 to team_100 → on GO, team_100 records LOD500.

— team_100
