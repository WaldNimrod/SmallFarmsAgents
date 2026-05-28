---
id: MANDATE_SFA-S002-P001-WP003-ARCHIVE_v1.0.0
from: team_100 (Chief Architect)
to: team_191 (Git/Files/Archive)
cc: team_00, team_99
date: 2026-05-28
type: archive_mandate
wp: SFA-S002-P001-WP003
trigger: DONE — migration to sfa.nimrod.bio verified + www severed
status: MANDATED
---

# Archive Mandate — WP-S002-P001-WP003

WP003 reached **DONE / LOD500_LOCKED** (2026-05-28): Server Scraping
Verification completed across Pass-1/2 (legacy www tier) and Pass-3 (migration
to sfa.nimrod.bio + www severance + anti-drift guard).

## Request
Produce `_archive/SFA-S002-P001-WP003/ARCHIVE_MANIFEST.md`:
- gate chain E→S→B (Pass-1, Pass-2, Pass-3) all PASS
- Pass-3 remediation commits (www severance) thru `dfbd347`
- key artifacts: LOD400_spec, team_99 ROOT_CAUSE_REMEDIATION, team_100
  RE-VERIFICATION_FINDING + MIGRATION_CLOSURE
- final state: delivery via sfa_ingest_push → sfa.nimrod.bio/market (200);
  freshness_guard backstop (cron 06:45); legacy www path retired (env+code)

— team_100 (Claude Opus 4.7)
