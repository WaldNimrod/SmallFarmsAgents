# ARCHIVE MANDATE (ADR042) — SFA-S003-P004 closure — team_100 → team_191 — v1.0.0

**Date:** 2026-06-03
**From:** team_100 (Chief System Architect)
**To:** team_191 (Git/Files)
**Re:** Archive the two now-CLOSED S003-P004 work packages (both LOD500_LOCKED 2026-06-03).
**Branch:** `claude/sfa-p004-cbdata-classb-2026-06-02`.

## Scope — two WPs, both DONE / LOD500_LOCKED
1. **SFA-S003-P004-WP-CB-UI-CLASSB** — Class B content surfaces (hub/market/search/community/about/account).
   L-GATE_V R3 PASS_WITH_FINDINGS (team_190 non-Claude, 7/7 surface + 4/4 constitutional; 2 INFO non-blocking).
   LIVE on sfa.nimrod.bio.
2. **SFA-S003-P004-WP-CB-DATA** — enrichment mirror (`crop_field_enrichment` + `crop_attribute` on uPress MySQL).
   L-GATE_V R2 PASS_WITH_FINDINGS (team_190 non-Claude, live 3/3 + code 3/3; 1 INFO non-blocking). 1010 rows LIVE.

## Per ADR042
- Move the `_COMMUNICATION/` trails for both WPs (TEAM_10/TEAM_50/team_99/team_190/team_100 sub-folders + the
  team_35 Class B HANDOFF) → `_archive/SFA-S003-P004-WP-CB-UI-CLASSB/` and `_archive/SFA-S003-P004-WP-CB-DATA/`
  with an `ARCHIVE_MANIFEST.md` each (commit list, gate trail, verdict refs, deploy reports).
- Update each WP's `archive_ref` in `_aos/roadmap.yaml` from the "pending team_191" placeholder to the real
  manifest path. **NOTE:** `roadmap.yaml` is team_100 single-writer (IR#4) — propose the `archive_ref` value
  back to team_100 (or edit only under the team_191 propagation mandate per the Directory Authority table).
- Do NOT alter LOD500_LOCKED source artifacts (LOD specs, code, migrations, verdicts).
- Branch reconciliation: `main` and `origin/branch` have converged through this program via the messaging
  helper + the team_99 deploy commits; confirm ancestry and note any cleanup in your audit.

## Open INFO follow-ups (non-blocking — log, do not fix here)
- Class B: legacy `--paper #f5f3ec` remains as a COMMENT in `tokens.css` (computed body `#f8fbf8` ✓) — a
  cosmetic scrub candidate already noted at WP-CB-UI-ALIGN closure.
- WP-SRV-IDEAS SRV-5 (live hub stats) remains PROPOSED/unapproved — server-side, out of Class B scope.

On completion → reply to team_100; this closes the **S003-P004 program**.
