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
- **The deploy machine's CURRENT external IP must be allowlisted on uPress** (see below).

## ⚠ uPress FTPS IP allowlist — the #1 deploy gotcha (CORRECTED 2026-06-06)

> **Earlier docs wrongly said "Bezeq blocks port 21 egress, deploy from the server."
> That is NOT the cause.** uPress FTPS (port 21) accepts only **allowlisted source
> IPs**, and home/office external IPs are **dynamic** (not static). The deploy works
> from **any** machine — Mac or waldhomeserver — once that machine's *current* external
> IP is opened on uPress.

- **The allowlist is dynamic and openable in seconds — just ask Nimrod (team_00).** He opens the current external IP in the uPress panel; it is not a permanent, server-only arrangement.
- **Symptom of a closed IP:** TCP to `ftp.s1240.upress.link:21` **times out** (not "connection refused"). Check + report your IP:
  ```bash
  curl -sS https://api.ipify.org            # your current external IP
  nc -z -G8 ftp.s1240.upress.link 21        # "succeeded" = open; timeout = ask Nimrod to open the IP above
  ```
- **The Mac can deploy directly** (it has `composer` + `lftp` + `php 8.x` + the `.env` creds). waldhomeserver is **not** a mandatory relay — it was simply whichever IP happened to be open. **Verified 2026-06-06:** WP-CB-MOBILE deployed straight from the Mac after the Mac IP `79.177.137.143` was opened → `mobile-fixes.css` HTTP 200, asset `?v=` bumped.
- HTTPS *data* ingest (`/api/v1/ingest`) goes via Cloudflare and needs **no** allowlist — only FTPS *code* deploy does.

## Deploy (FTPS — current canonical method)

```bash
# from repo root, on a machine whose external IP is allowlisted on uPress (ask Nimrod)
bash scripts/ftp_deploy_sfa_ui.sh
```

Overrides:
- `ENV_FILE=path/to/.env` — alternate env file
- `SFA_DELIVERY_SRC=./sfa_delivery` — alternate source tree

The script: loads env → `composer install --no-dev --optimize-autoloader` in the
source tree → verifies `vendor/` exists → `lftp mirror -R --delete` to
`SFA_FTP_ROOT`. Excludes `.env*`, `.git*`, `logs/`, `tests/`, `.DS_Store`,
`*.pyc`, `__pycache__/`.

## Post-deploy smoke (the exact checks used 2026-06-06)

1. `curl -sI https://sfa.nimrod.bio/ | head -1` → `200`.
2. **Confirm the asset version bumped** + any NEW CSS/JS is served (not 404):
   ```bash
   curl -s https://sfa.nimrod.bio/ | grep -oE '\?v=[0-9]+' | head -1            # new ?v=
   curl -s -o /dev/null -w '%{http_code}\n' https://sfa.nimrod.bio/public_assets/css/<new-file>.css
   ```
3. Spot-check the surfaces you changed (e.g. `/market/`, a crop page `/crop-book/<slug>/`),
   grepping for the new markup classes and confirming **no raw enum/region tokens leak**.
4. Desktop sidebar (`קהילה` accordion) shows community feed items.

## Rollback

Re-deploy the previous known-good commit's `sfa_delivery/` tree (the mirror is
idempotent; `--delete` makes the remote match the local source exactly).

## Alternative (FUTURE — not yet adopted): uPress Git deploy

uPress supports a **Git-based deploy** (push to a uPress-side repo / pull on the host),
which would remove the FTPS IP-allowlist dance entirely. **Not yet evaluated or wired for
this project** — do not assume the exact steps. Before adopting:
1. Read uPress's own help center (Hebrew) on Git deployment, or ask uPress support for the
   per-site Git remote + branch + any build-hook details.
2. Confirm how `vendor/` is produced on their side (our Option B builds it pre-upload; a
   Git deploy would need a server-side `composer install --no-dev` hook or a committed vendor).
3. Pilot to a staging path before switching the canonical deploy.
Until then, **FTPS via `scripts/ftp_deploy_sfa_ui.sh` (above) is the canonical method.**
