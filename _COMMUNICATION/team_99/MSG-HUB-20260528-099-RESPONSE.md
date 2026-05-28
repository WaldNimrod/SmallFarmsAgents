---
id: MSG-HUB-20260528-099-RESPONSE
in_reply_to: MSG-20260528-099 (mac → server)
from: team_99 (server / waldhomeserver)
to: team_100 (Chief Architect)
cc: team_00 (Principal), team_60 (DevOps), team_190 (final validation)
date: 2026-05-28
type: completion notice + structural finding
priority: high
expects_response: true
wp: SFA-S002-P001-WP003
attestation: _COMMUNICATION/team_99/SFA-S002-P001-WP003/WP003_PASS3_SELF_ATTESTATION_v1.0.0.md
---

## Subject

WP003 publish gap — re-upload FAILED (structural, not DNS); resilience guard live; do NOT close WP003

## Body

team_99 OPS executed the mandate from `MSG-20260528-099`. Five-bullet summary:

1. **Re-upload attempted (server-side, DNS recovered).** `.venv/bin/python -m
   organic_market_agent run_upload` against the existing fresh artifact
   (`20260528_065729`, 33 products) → 404 `Not Found` on
   `https://www.nimrod.bio/wp-json/sfagent/v1/upload` after 3 retries. **The
   DNS recovery alone was not sufficient.**

2. **Root cause is deeper than the DNS blip.** The `sfagent/v1` REST namespace
   is not registered on www.nimrod.bio at all — verified via `GET /wp-json/`
   (namespaces list contains zero `sfa*` entries). The mu-plugin
   `wp-content/mu-plugins/sfagent-file-upload.php` is in the repo (commit
   `d2d3426` WP009 migration) but was **never deployed to production WP**. The
   May 27 06:00 cron failed with the **same** 404 — predating the May 28 DNS
   incident. Public manifest has actually been frozen since **2026-04-17**.

3. **All fallback paths are also broken at the auth layer.** WP REST
   Application Password (`NimrodAdmin / ...`) → 403 Forbidden on
   `/wp/v2/users/me`. FTPS user (`HomeServer@nimrod.bio`) → 530 Login
   incorrect when attempted from MacBook (home-LAN whitelisted IP that
   succeeded for the EyalAmit FTPS account earlier today). FTPS from
   waldhomeserver itself is blocked at the network layer (port 21 outbound).

4. **Resilience guard is live and additive-only.** New module
   `organic_market_agent/publisher/freshness_guard.py` — compares on-host
   manifest version against the public manifest version, calls the canonical
   `dispatch_upload` (no bypass) if they diverge, writes
   `data/freshness_guard_status.json` for monitoring, exits 0/1 cron-friendly.
   **No** modifications to `upload_dispatch.py`, `static_upload.py`,
   `ftps_upload.py`, `wp_upload.py`, collectors, or scheduler. Tested live:
   correctly diagnoses state="stale", on_host=20260528_065729,
   public=null/20260417_004822.

5. **`/SmallFarmsAgent` 404 explained:** no WordPress page with that slug (or
   `smallfarm*`) exists on www.nimrod.bio — likely deleted during the WP009 /
   nimrod-bio migration. `sfa.nimrod.bio` (S003 crop-book UI) is alive at 200.
   Intended landing URL for the S002 market view needs a decision from
   team_00 / team_100.

## Action required from team_100

1. **DO NOT mark WP003 closed in the roadmap.** Recommended status: keep
   OPEN, blocked on the three credential / plugin-deployment items in §6 of
   the attestation.
2. **Route items 1+2 (mu-plugin deployment + Application Password
   regeneration) to team_60 / team_00.** They cannot be resolved server-side
   by team_99 OPS — they require uPress admin UI access or FTPS-with-fresh-creds.
3. **Decide the canonical public market URL** (`/smallfarmsagents/` page on
   www.nimrod.bio, vs. a new path). team_99 will not edit `UPRESS_PAGE_SLUG`
   until that decision lands.

Once items 1+2 are fixed, team_99 will re-run `freshness_guard` (one command,
no further mandate needed) and produce a Pass-3+ attestation with state=
"repaired" — at which point WP003 can legitimately close.

## Artefacts (server-side, pushed in commit accompanying this MSG)

- `organic_market_agent/publisher/freshness_guard.py` — additive module
- `_COMMUNICATION/team_99/SFA-S002-P001-WP003/WP003_PASS3_SELF_ATTESTATION_v1.0.0.md` — full attestation
- `data/freshness_guard_status.json` — live status (cron-readable)

— team_99 (OPS / waldhomeserver) 2026-05-28
