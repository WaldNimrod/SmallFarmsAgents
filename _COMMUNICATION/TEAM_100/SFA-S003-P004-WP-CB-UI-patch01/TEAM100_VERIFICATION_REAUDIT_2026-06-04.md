# team_100 verification — patch01 deploy + re-audit reconciliation (2026-06-04)

**Context:** team_99 DEPLOY_REPORT claimed SUCCESS @ 6703313; team_50 Haiku re-audit returned NO-GO claiming
the WI-5/6/7 CSS was NOT deployed + 3 mobile-overflow failures. team_100 (Opus) independently arbitrated.

## Findings (team_100, hard evidence)
1. **Deploy IS live + correct.** The 3 live CSS files are **byte-identical to the branch**
   (crop-book-v1.css 58870, classb.css 49231, crop-book-deep.css 20618), `cf-cache-status: MISS`, and ALL
   WI-5/6/7 markers present (live counts = local counts): cb-paths grid (1), sh__mark svg (1), phist-wrap (2),
   dt-table-wrap (2), cb-crop-detail (2). `?v=` advanced 1780515224→1780520599. **team_99 was correct.**
2. **team_50 re-audit was a FALSE NO-GO on the CSS:** it checked the WRONG file (`hub.css` for `.cb-paths`,
   which only has the legacy `gap` rule — WI-5 lives in crop-book-v1.css) and mis-detected markers. Its
   "not deployed" conclusion is rejected.
3. **Mobile overflow (team_100 qa_probe CDP @375):** `/crop-book/lettuce/` = no overflow ✓;
   `/market/prd059` = no overflow ✓ (team_50's claims on these two were FALSE — WI-7 resolved them).
   `/crop-book/table` = scrollWidth 517 > 375 = **REAL overflow** (team_50 correct here). Root cause: RTL
   scroll-origin leak — the table's overflow-x:auto scroll extent propagates to <html>.scrollWidth with no
   clipping ancestor. **Fixed in WI-8** (`.cb-table-page { overflow-x: clip }`).

## Disposition
- patch01 deploy of 6703313: VERIFIED LIVE by team_100.
- 1 real residual (/crop-book/table RTL overflow) → WI-8 fix → requires a final redeploy + live re-probe.
- team_50 re-audit superseded by this team_100 verification; team_50 to re-run with corrected method
  (probe crop-book-v1.css not hub.css; cache-bust to the live ?v=) after the WI-8 redeploy.
