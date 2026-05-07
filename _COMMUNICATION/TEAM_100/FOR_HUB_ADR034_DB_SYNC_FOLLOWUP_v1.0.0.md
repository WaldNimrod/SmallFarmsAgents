---
id: FOR_HUB_ADR034_DB_SYNC_FOLLOWUP
schema_version: aos_v1_for_hub_routing
for_hub: true
from_team: team_100 (spoke session — smallfarmsagents)
to_team: team_100 (hub — agents-os)
type: db_sync_followup
subject: "ADR034 R8 closure — sync SFA-S002-P001 Phase 1 offline mutations to DB when online"
date: 2026-05-07T10:12:00Z
related_program: SFA-S002-P001
project_id: smallfarmsagents
note: "This artifact follows the for_hub: true routing pattern (team_100.md §Boundaries). team_00 reads this in a hub session and routes to the AOS hub team_100. spoke session does NOT write to agents-os repo."
---

## ADR034 R8 closure follow-up — SFA-S002-P001 Phase 1

### Context

The SFA spoke ran an offline session on 2026-05-07 (`offline/2026-05-07-smallfarmsagents-release-prep`) to deliver SFA-S002-P001 Phase 1 (Public Index Launch Readiness, F-01 + F-190-01 closed). Hub DB has been offline since 2026-05-06T18:59:16Z (port 5434 connection refused). Per ADR034 R8 + team_99 contract, the session was conducted on a named offline branch with `_aos/PENDING_DB_SYNC.yaml` recording all mutations.

### What needs to happen when DB returns online

1. **Hub-side probe + reactivation:**
   ```bash
   # When AOS v3 PostgreSQL is reachable again:
   bash /Users/nimrod/Documents/agents-os/scripts/probe_database.sh
   # Refresh status:
   cat /Users/nimrod/Documents/agents-os/_aos/db_connectivity_status.json
   ```

2. **Run sync from spoke (or hub-driven dry-run first):**
   ```bash
   cd /Users/nimrod/Documents/SmallFarmsAgents
   bash /Users/nimrod/Documents/agents-os/scripts/sync_offline_to_db.sh --dry-run
   # Review output, then:
   bash /Users/nimrod/Documents/agents-os/scripts/sync_offline_to_db.sh --force
   ```

3. **Note — ADR034 R9 spoke-native exception:**
   All WPs in the SFA Phase 1 are spoke-native (`SFA-SNNN-PNNN-WPNNN` format). Per R9, file-based SSoT is authoritative for these. Hub may elect:
   - **(a)** Skip DB sync entirely — file-based remains authoritative.
   - **(b)** Mirror as informational rows for cross-domain visibility.

   Either is acceptable. team_100 (spoke) recommends (b) for audit consistency, but defers to hub team_100 / team_00.

4. **After sync completes:**
   - Apply label `[offline-sync-complete]` to the offline branch / PR.
   - Remove `_aos/PENDING_DB_SYNC.yaml` (or mark resolved in-place).
   - Re-run `validate_aos.sh` on spoke — Check 25 should change from `PENDING_DB_SYNC.yaml found` back to `No pending offline DB sync`.

### Inventory of pending mutations (full detail in PENDING_DB_SYNC.yaml)

| Entity | ID | Operation |
|--------|----|-----------|
| milestone | S002 | open (active) |
| work_package | SFA-S002-P001-WP001 | create (DEFERRED_PHASE2) |
| work_package | SFA-S002-P001-WP002 | create (DEFERRED_PHASE2) |
| work_package | SFA-S002-P001-WP003 | create + complete (LOD500_LOCKED) |
| work_package | SFA-S002-P001-WP004 | create + complete (LOD500_LOCKED) |
| work_package | SFA-S002-P001-WP005 | create + complete (LOD500_LOCKED) |
| work_package | SFA-S002-P001-WP006 | create + complete + supersede (LOD500_LOCKED) |
| work_package | SFA-S002-P001-WP007 | create + complete (LOD500_LOCKED) |
| work_package | SFA-S002-P001-WP008 | create_and_complete (LOD500_LOCKED) |
| phase_closure | SFA-S002-P001-Phase1 | close (effective PASS) |

### Authority routing

This artifact is `for_hub: true`. team_00 routes to a hub team_100 session in `agents-os` repo when DB returns online. Spoke team_100 does NOT cross-write to hub.

---

*Filed 2026-05-07 by spoke team_100 (Claude Opus 4.7) for hub-side action when DB connectivity is restored.*
