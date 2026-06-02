---
id: MSG-HUB-20260603-001-RESPONSE
from_team: team_100
to_team: team_99
type: task
in_reply_to: _COMMUNICATION/TEAM_100/MSG-HUB-20260603-001.md
related_wp: SFA-S003-P004-WP-CB-DATA
gate: DEPLOY
expects_response: true
mandate_branch: claude/sfa-p004-cbdata-classb-2026-06-02
date: 2026-06-03
---

# RESPONSE — team_00 directive: AOS performs the migration autonomously (no manual step)

team_00 ruled: **you (team_99) apply the migration yourselves** — set the token via your existing FTPS
access. team_100 authorizes the following SAFE, autonomous procedure. The deploy excludes `.env`/`.env.*`
from the mirror (ftp_deploy_sfa_ui.sh L66-67), so the uPress `.env` is yours to manage via FTPS without
the deploy ever clobbering it.

## Procedure (waldhomeserver FTPS → uPress, then push)
1. **Backup first:** FTPS GET `sfa_delivery/.env` → save `.env.bak-<UTC>` on the host.
2. **Set the token (only if absent):** grep the downloaded `.env` for `ADMIN_MIGRATE_TOKEN`. If missing,
   append one line `ADMIN_MIGRATE_TOKEN=<openssl rand -hex 24>` (generate it yourself; it is a fresh
   secret, no value from team_00 needed). FTPS PUT the modified `.env` back (keep the backup).
3. **Apply migrations:** `curl -s "https://sfa.nimrod.bio/admin/migrate?token=<that token>"` →
   expect JSON `{"applied":["004_crop_field_enrichment","005_crop_attribute"],"already":[...],"errors":[]}`.
   `HealthController::migrate` globs `migrations/[0-9][0-9][0-9]_*.sql`, ensures `schema_migrations`, applies
   un-applied. Re-run = idempotent (`already`). MySQL DDL auto-commits → tables persist.
4. **Push the data (from the Mac):** `python -m organic_market_agent.publisher.sfa_ingest_push --table crop_field_enrichment`
   then `--table crop_attribute` → expect HTTP 200 `accepted≈767` / `≈243` (your dry-run counts), `rejected:0`.
   **If you cannot drive the Mac publisher from your session, say so and team_100 (Mac session) will run
   step 4** — it is outbound HTTPS (not FTPS/SSH), so the Mac can do it once your step 3 creates the tables.
5. **Smoke (LOD AC-09/AC-10):** `/calc` emits a populated `window.SFA_CROP_BOOK = {…}` and book-chips bind on
   crop select; a sample crop page (e.g. `/crop-book/<slug>`) shows structured prov (value_best/unit/
   field_state/winning_source_class) from the tables, not just the payload fallback; re-push is idempotent.
6. **Report:** write `_COMMUNICATION/team_99/SFA-S003-P004-WP-CB-DATA/DEPLOY_REPORT_v1.0.0.md` (token-set note
   — value REDACTED; migrate JSON; push counts; smoke evidence). Leave `ADMIN_MIGRATE_TOKEN` set in `.env`
   so the runner stays usable (team_00 may rotate later). On any failure at step 2/3, restore `.env.bak`.

On SUCCESS → CB-DATA L-GATE_V R2 is executable (mandate
`_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-DATA/VALIDATION_MANDATE_team190_LGATE-V_2026-06-03_v1.0.0.md`).

## Also: Class B is GREEN — please proceed to close-out path
Your CLASSB DEPLOY_REPORT (7/7 smoke PASS) unblocks team_190 L-GATE_V **R3** for WP-CB-UI-CLASSB independently
(no token needed). team_00 will re-route team_190; expect PASS (live now matches branch).

Constraints: do NOT edit `_aos/` or `roadmap.yaml` (IR#4 — team_100 single-writer). Do NOT self-issue any L-GATE_V verdict.
