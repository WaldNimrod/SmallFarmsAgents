---
id: SFA-S003-P004-WP-CB-DEEP-PROVENANCE-REGISTER
wp: SFA-S003-P004-WP-CB-DEEP-PROVENANCE — deep-view source provenance (comment fix + fallback robustness)
gate: L-GATE_E (registered)
status: DEFERRED (team_00 2026-06-07) — revisit later
author: team_100
created: 2026-06-07
builder: team_10
validator: team_50
trigger: "Carried forward from WP-CB-MOBILE; reassessed SMALL — pills already render in production (lettuce 32)."
design: _COMMUNICATION/team_100/SFA-S003-P004-WP-CB-DEEP-PROVENANCE/DISPOSITION_2026-06-07_v1.0.0.md
---

# REGISTER — WP-CB-DEEP-PROVENANCE (DEFERRED)

Deep-view EX/PR/WR source pills **already work in production** (verified live 2026-06-07: 32 srcpill on
lettuce). Reassessed small.

**Scope when reactivated (team_00 decision):** (a) fix the **stale/false comment** at
`CropBookViewController.php:693-696` (contradicted by L666-683, which query the very tables it claims absent);
(b) **fallback robustness** — add `source_class{}` to the per-variety payload + read it in the 3 fallback
branches (`:879,887,912`) so sparsely-enriched crops also show pills. Data-coverage split to a separate
crop-enrichment WP. No-leak intent for `OP/MK/WB/UC` retained.

**Status:** DEFERRED — not urgent (provenance functions today). Disposition authored; no LOD until reactivated.
