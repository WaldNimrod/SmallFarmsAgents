# Branch Reconciliation Manifest — 2026-06-02

**Author:** team_191 (Git/Files)
**Date:** 2026-06-02
**Strategy:** ARCHIVE-CONSOLIDATION — unique files extracted into `_archive/_BRANCH_RECONCILIATION_2026-06-02/<branch>/`, then branches deleted. No changes to any live path outside `_archive/`.

## Recovery Instruction

To recover a specific file from any archived branch:
```
git checkout <tip-SHA> -- <original/path/to/file>
```
Or directly from the archive directory at the path shown below.

---

## Reconciliation Table

| Branch | Type | Tip SHA | Files Archived | Status | Description |
|--------|------|---------|---------------|--------|-------------|
| `archive/raw-material-tend-masterclass-2026-04` | remote | `64d5137` | 287 | **archived** | Team 80 Tend farm MasterClass exports (2018–2022): Hebrew-named PDFs, CSV/ZIP crop data archives, tools lists, bubbler diagrams. Raw material reference set. |
| `claude/eager-meninsky-1e6876` | remote+local | `8214fec` | 1 | **archived** | S003-WP004 planning handoff to team_100 (2026-05-10). Single handoff mandate doc not merged. |
| `claude/fervent-vaughan-12711e` | local | `166bb3b` | 13 | **archived** | S002 final routings + Phase 2 handoff for team_100 (2026-05-07). Phase-2 planning/handoff docs. Shares tip with sad-bhabha and suspicious-nightingale. |
| `claude/fix-crop-families-2026-06-02` | local | `574c868` | 5 | **archived** | F-DATA-001 crop-family fallback fix (Aizoaceae systemic bug) authored 2026-06-02. Bug-fix branch not yet merged. |
| `claude/flamboyant-gould-e7b891` | local | `956deb7` | 32 | **archived** | S003-P001 Phase 1 LOD500_LOCKED + Phase 2 LOD400_LOCKED merge branch (2026-05-10). Intermediate merge state with phase lock docs. |
| `claude/gallant-elbakyan-727a60` | remote+local | `1444a90` | 11 | **archived** | Canonical /AOS_handoff full (2026-05-27). Handoff comms and planning artifacts. |
| `claude/sad-bhabha-0b4f7f` | local | `166bb3b` | 13 | **archived** | Same tip as fervent-vaughan. S002 final routings + Phase 2 handoff artifacts. Duplicate branch ref pointing to same work. |
| `claude/sfa-ui-patch01` | remote+local | `b41d508` | 1 | **archived** | team_190 L-GATE_V R2 media re-check mandate (2026-05-29). Single validation mandate doc. |
| `claude/suspicious-nightingale-73dda2` | local | `166bb3b` | 13 | **archived** | Same tip as fervent-vaughan and sad-bhabha. S002 Phase 2 handoff branch. Duplicate ref. |
| `cursor/m10-doc-mandates-spike` | remote | `bb981ed` | 579 | **archived** | M10 doc mandates spike (v1.1): LOD400 comms, DB migrations 072/073, basket tier resolver, QA remediation, dev stack docs (2026-04-10). Large research/spike branch. |
| `cursor/mypips-communication-and-handoffs` | remote | `64d5137` | 209 | **archived** | Same tip as archive/raw-material branch. Contains same Team 80 Tend farm MasterClass exports. Duplicate remote ref. |
| `fix/r3-v02-cherry` | local | `b5ad8e5` | 19 | **archived** | WP-CB-UI-ALIGN L-GATE_V R3 cherry-pick fix: remove farmer-facing family latin line + raw key on calc card (2026-06-02). |
| `msg/team99-r3-deploy` | local | `f66360d` | 20 | **archived** | team_99 DEPLOY R3 mandate + MSG-HUB-20260602-006 (deploy main @ b5ad8e5) comms (2026-06-02). |
| `team60/ftps-cred-sync-runbook` | local | `0b6dfc8` | 22 | **archived** | FTPS cred rotation & sync runbook + helper script for team_60 ops (2026-06-02). |
| `worktree-agent-a48041ae95a53a4a4` | local | `100c58d` | 4 | **archived** | team_100 brand-asset commit merge from origin/main (2026-05-28). 4 files not yet on main. |
| `worktree-agent-a9dca339512719135` | local | `5e3ce98` | 6 | **archived** | WP-UI-patch02: 70 slug-exact watercolor crop-icon generation prompts (2026-05-29). |
| `worktree-agent-aeaaa5f2bc4e2e755` | local | `919ecb8` | 0 | **fully-redundant** | WP-CB-UI-ALIGN ADR042 L-GATE_V R3 PASS / DONE / LOD500_LOCKED (2026-06-02). Ancestor of main — all content already on main. |
| `wp/c6-sparse-crops` | local | `d20769a` | 0 | **fully-redundant** | WP-C6 sparse-crops WR expansion 19 crops (2026-05-29). All unique files already on main. |
| `wp/sever-www-legacy` | local | `bbd8ebe` | 0 | **fully-redundant** | ops(publisher): sever www.nimrod.bio legacy paths (2026-05-28). All unique files already on main. |
| `wp/ui-patch02-icons` | local | `4dd96a7` | 0 | **fully-redundant** | WP-UI-patch02 icon system (2026-05-29). Ancestor of main — all content already on main. |

---

## Worktrees Removed

| Path | HEAD SHA | Branch | Disposition |
|------|----------|--------|-------------|
| `/private/tmp/sfa-wp-cb-1-val` | `9f9d9d1d` | detached | removed (ancestor of main) |
| `/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/agent-a48041ae95a53a4a4` | `bbd8ebe2` | `wp/sever-www-legacy` | removed (branch archived) |
| `/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/agent-a9dca339512719135` | `5e3ce989` | `worktree-agent-a9dca339512719135` | removed (branch archived) |
| `/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/agent-aeaaa5f2bc4e2e755` | `0b6dfc84` | `team60/ftps-cred-sync-runbook` | removed (branch archived) |
| `/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/flamboyant-gould-e7b891` | `956deb78` | `claude/flamboyant-gould-e7b891` | removed (branch archived) |
| `/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/gallant-elbakyan-727a60` | `1444a908` | `claude/gallant-elbakyan-727a60` | removed (branch archived) |
| `/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/sad-bhabha-0b4f7f` | `166bb3b1` | `claude/sad-bhabha-0b4f7f` | removed (branch archived) |
| `/tmp/sfa-reconcile` | detached | _(reconcile worktree)_ | removed after archive commit pushed |

---

## Notes

- **Hebrew filenames:** `archive/raw-material-tend-masterclass-2026-04` contains Hebrew-named PDFs under `_COMMUNICATION/TEAM_80/MasterClass/Crops Data/`. Extracted using `git cat-file blob` (SHA-based) to bypass shell quoting issues with octal-escaped names.
- **Duplicate tips:** `claude/fervent-vaughan-12711e`, `claude/sad-bhabha-0b4f7f`, `claude/suspicious-nightingale-73dda2` all point to `166bb3b`. Same 13 files archived in each directory.
- **Duplicate remote:** `cursor/mypips-communication-and-handoffs` == `archive/raw-material-tend-masterclass-2026-04` tip `64d5137`. Both archived independently.
- **`/tmp/sfa-reconcile`:** this reconcile worktree itself, removed at end of Step 4.
