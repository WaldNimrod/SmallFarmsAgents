# UI Deploy Runbook — sfa.nimrod.bio (sfa_delivery)

Deploy of the Slim/PHP UI shell (`sfa_delivery/`) to the dedicated subdomain
`sfa.nimrod.bio` over FTPS. Codifies the previously-inline lftp deploy used
during WP-UI (SFA-S003-P002-WP-UI).

## vendor/ strategy — Option B (team_00 ruling 2026-05-28)

`vendor/` is **gitignored**. The deploy script runs `composer install --no-dev`
before the lftp mirror, so the uploaded tree always carries a complete,
production-only dependency set. Do **not** `re-mirror from main` — `vendor/`
is absent on main and that broke production for ~60s during WP-UI closure.

## Prerequisites

- `lftp`, `composer`, PHP 8.x on the deploy machine.
- `.env` populated with the `sfa.nimrod.bio` FTPS credentials
  (`.env.example` lines 75-87):
  - `SFA_FTP_HOST`, `SFA_FTP_PORT` (21), `SFA_FTP_USER`, `SFA_FTP_PASS`, `SFA_FTP_ROOT` (`/`)
- Network that allows outbound port 21 (note: Bezeq home network blocks port 21
  egress — deploy from server/allowed network; see DOCKER_SHARED_WORKSTATION /
  WP007 history).

## Deploy

```bash
# from repo root
bash scripts/ftp_deploy_sfa_ui.sh
```

Overrides:
- `ENV_FILE=path/to/.env` — alternate env file
- `SFA_DELIVERY_SRC=./sfa_delivery` — alternate source tree

The script: loads env → `composer install --no-dev --optimize-autoloader` in the
source tree → verifies `vendor/` exists → `lftp mirror -R --delete` to
`SFA_FTP_ROOT`. Excludes `.env*`, `.git*`, `logs/`, `tests/`, `.DS_Store`,
`*.pyc`, `__pycache__/`.

## Post-deploy smoke

1. `curl -sI https://sfa.nimrod.bio/ | head -1` → `200`
2. Load `https://sfa.nimrod.bio/` — home renders, module grid present.
3. Desktop sidebar (`קהילה` accordion) shows community feed items.
4. Spot-check a crop page (`/book/<crop>`) and `/market/`.

## Rollback

Re-deploy the previous known-good commit's `sfa_delivery/` tree (the mirror is
idempotent; `--delete` makes the remote match the local source exactly).
