# ROLLBACK PLAN — SFA-S002-P001 Phase 1

If the external validator returns FAIL or a critical regression is discovered post-merge, this is the canonical revert procedure.

## Trigger conditions (any one warrants rollback)

- Public site `https://www.nimrod.bio/SmallFarmsAgent` returns non-200 for >1 hour.
- `pipeline_alerts` shows persistent ERROR-level failures for >2 consecutive cron runs.
- External validator returns FAIL with blocking severity.
- Data loss / corruption observed on uPress media library.

## Decision authority

team_00 (Nimrod) is the sole authority to invoke rollback. team_99 / team_100 may PROPOSE rollback in writing; only team_00 EXECUTES the decision.

## Pre-rollback (mandatory before any destructive action)

1. Capture current state evidence:
   ```bash
   ssh nimrodw@waldhomeserver "cd /data/projects/smallfarmsagents && git log --oneline -10 && git status"
   curl -s "https://www.nimrod.bio/wp-content/uploads/2026/05/sfagent-manifest.json" | head -c 500
   ```
2. Save to `_COMMUNICATION/team_99/SFA-S002-P001/PRE_ROLLBACK_STATE_<DATE>.md`.
3. Notify team_99 via Telegram dispatch bot if severity is HIGH.

## Rollback procedure

### Code rollback (waldhomeserver)

The current production tip is on `main` after the offline branch was merged. To revert:

```bash
cd /data/projects/smallfarmsagents
git fetch origin
# Identify pre-merge commit on main (last commit before the offline branch was merged)
PRE_MERGE_SHA=<lookup>
git reset --hard "$PRE_MERGE_SHA"
```

Reverts in scope (commits to undo, in order from most recent):
- `4734fa6` — gate(S002): close WP003+WP007
- `4fedbf3` — docs(S002-WP007): runbook
- `73eaf3e` — build(S002-WP007): WP REST upload
- `2603727` + `30399a3` — WP004 mobile UI
- (and the supporting mandate / spec / gate commits in the same range)

**Better alternative:** identify the LAST main commit BEFORE this session's work began (`1772e39` or earlier) and reset to it. Use `git log` to confirm.

### WP option rollback (uPress)

```bash
# unset the manifest pointer URL — shortcode falls back to its previous behavior
# (or to legacy hard-coded path if shortcode was previously unmodified)
python scripts/wp_shortcode_install.py --set-mou-url ""
```

### mu-plugin removal (optional — only if deemed problematic)

Via uPress panel file manager: delete `wp-content/mu-plugins/sfagent-allow-json.php`. Note: removing this WHILE WP007 code is in production will cause every upload to fail with HTTP 500 — only remove together with code rollback.

### .env restoration

Backups created automatically during this session:
```
/data/projects/smallfarmsagents/.env.bak.20260507_wp007_creds
/data/projects/shaked-wg-agent/.env.bak.20260507_wp007_creds
```

To restore:
```bash
ssh nimrodw@waldhomeserver "
  for f in /data/projects/smallfarmsagents/.env /data/projects/shaked-wg-agent/.env; do
    if [ -f \"\${f}.bak.20260507_wp007_creds\" ]; then
      cp \"\${f}.bak.20260507_wp007_creds\" \"\${f}\"
      chmod 600 \"\${f}\"
    fi
  done
"
```

### Public artifact restoration

The pre-2026-05-06 state had `artifact_version=20260417_004822`. To restore to that previous broken-but-stable state, the easiest path is to re-run `run_publisher --upload` after code rollback — the upload will fail (FTPS blocked), but the manifest URL pointer will stay valid (it points to media library, not date-specific paths).

If the WP option is unset (per "WP option rollback" above), the shortcode will fall back to its pre-WP007 behavior. Whether that's "broken site" or "old shortcode reading FTPS-uploaded files" depends on what was on `main` at rollback target.

## Post-rollback verification

1. `https://www.nimrod.bio/SmallFarmsAgent` returns HTTP 200.
2. Site renders SOMETHING (even if stale data) — not a PHP fatal.
3. `pipeline_alerts` reflects the rolled-back code state.

## Notification chain

After rollback execution:
1. team_99 files `ROLLBACK_LOG_<DATE>.md` in `_COMMUNICATION/team_99/SFA-S002-P001/`.
2. team_100 updates `_aos/roadmap.yaml` to reflect WP statuses (mark relevant WPs ROLLED_BACK).
3. Open follow-up WP for re-attempt (likely WP007.B — second WP REST iteration with the validator's findings addressed).
