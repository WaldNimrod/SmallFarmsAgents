# Deploy Report — SFA-S003-P004-WP-CB-CALC (team_99)

Closes L-GATE finding **A-01** (deploy evidence of record). Two deploys to the delivery tier
(uPress, `sfa.nimrod.bio`) via `bash scripts/ftp_deploy_sfa_ui.sh` — composer `--no-dev` + `lftp mirror`.

## Deploy #1 — main `2f31d89`
- Method: `bash scripts/ftp_deploy_sfa_ui.sh` (team_99) — `composer install --no-dev` + `lftp mirror` to uPress.
- Live smoke: **PASS**
  - `/calc/` → 200
  - calculator markers present
  - `frost_regions.json` → 200
  - `SFA_DATEC` live
  - "רווח גולמי" (gross profit) **absent** (correct — profit reframed out of hero)
  - assets served at `?v=1780865050`

## Deploy #2 — main `0a993e9` (F-05 hotfix redeploy)
- Method: redeploy via same `scripts/ftp_deploy_sfa_ui.sh`.
- Verified:
  - `data-goal-input="profit"` present (count 1)
  - `"compare"` goal input **absent** (count 0)
  - `/calc/` → 200

**Final live build:** main `0a993e9` at https://sfa.nimrod.bio/calc/ (`?v=1780865050`).
