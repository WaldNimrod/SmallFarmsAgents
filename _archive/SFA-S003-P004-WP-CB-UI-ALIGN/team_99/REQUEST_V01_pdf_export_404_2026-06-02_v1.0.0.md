# REQUEST (V01) — /calc/export.pdf 404 on live — team_100 → team_99 — v1.0.0

**Date:** 2026-06-02 · **From:** team_100 · **To:** team_99 (ops/hosting) · **WP:** SFA-S003-P004-WP-CB-UI-ALIGN
**Context:** L-GATE_V Round 1 BLOCKER F-190-UIALIGN-V01. `/calc/export.pdf` returns 404 on live (browser + curl);
`/calc/export.csv` returns 200. Same Slim route `/calc/export.{fmt:csv|pdf}`, same controller `calcExport`
(renders `pages/calc_export_print` for pdf), and `templates/pages/calc_export_print.php` EXISTS on the deployed
tree (b72bcca). So the code supports PDF — the 404 is hosting/edge, not code.

## team_100 diagnosis (needs your confirmation)
- `curl -sI https://sfa.nimrod.bio/calc/export.pdf` → `404`, **`cf-cache-status: HIT`, `age 139`,
  `cache-control: max-age=14400`**. The zone appears to **ignore query strings** (a novel `?cb=1` also HIT the
  same cached 404), so I cannot probe origin from the edge. This looks like a **stale Cloudflare cache of the
  pre-fix 404** (F-EXPORT-001 era, when the route truly 404'd) — but it could also be uPress/Apache not routing
  the `.pdf` extension to `index.php`/Slim at origin.

## Please do (ops — you have server + CDN access)
1. **Probe origin directly** (bypass Cloudflare) on uPress: from the server, `curl -sI http://127.0.0.1/calc/export.pdf`
   (or the origin host with the right Host header). Report the **origin** status:
   - **Origin 200** → it's purely the CDN cache → **purge Cloudflare** for `/calc/export.pdf` (or the zone) and re-verify.
   - **Origin 404** → uPress is not routing `.pdf` to Slim (e.g. a server-level handler / mod_negotiation for
     `.pdf`). Report what intercepts it; team_100 will then change the export URL scheme in code (e.g.
     `/calc/export?fmt=pdf`) to sidestep the extension. (Don't change code yourself.)
2. After purge (if origin 200): confirm `curl -sI https://sfa.nimrod.bio/calc/export.pdf` → 200 + the print HTML.

## Recommended hardening (optional, team_100 can do in code)
Have `calcExport` send `Cache-Control: no-store` so HTML/error responses are never edge-cached again.

**Return** the origin probe result + purge outcome to team_100 — it gates L-GATE_V R2.
