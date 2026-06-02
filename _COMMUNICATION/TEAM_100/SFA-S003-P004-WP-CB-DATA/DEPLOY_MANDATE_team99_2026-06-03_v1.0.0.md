# DEPLOY + DATA-PUSH MANDATE — SFA-S003-P004-WP-CB-DATA — team_100 → team_99 — v1.0.0

**Date:** 2026-06-03
**From:** team_100 (Chief System Architect)
**To:** team_99 (OPS / waldhomeserver) + Mac-side push
**Re:** Apply the enrichment-mirror migrations on uPress MySQL + push the data, so live /calc book-chips + crop-page structured reads bind.
**Branch:** `claude/sfa-p004-cbdata-classb-2026-06-02` (pushed; tip `9adf667`+).
**Preconditions met:** team_190 L-GATE_S PASS_WITH_FINDINGS (build authorized); team_100 L-GATE_B verify PASS (pytest 750/2-pre-existing, composer 141, validate_aos 0 FAIL); team_50 QA PASS.

## Coupling with the Class B deploy
This branch ALSO carries the Class B fix-all (DEPLOY_MANDATE_team99_2026-06-02). The single FTPS mirror of
`sfa_delivery/` deploys BOTH the Class B template/CSS fixes AND the new `sfa_delivery/migrations/004_*.sql` +
`005_*.sql`. **Do the Class B deploy and these CB-DATA steps in one pass** (mirror once, then the extra steps below).

## Steps (on waldhomeserver, then Mac)
```bash
# 1. (waldhomeserver) deploy the branch — same as the Class B mandate:
cd <repo-on-waldhomeserver>
git fetch origin && git checkout claude/sfa-p004-cbdata-classb-2026-06-02 \
  && git reset --hard origin/claude/sfa-p004-cbdata-classb-2026-06-02
bash scripts/ftp_deploy_sfa_ui.sh          # uploads templates/css + migrations/004,005 sql

# 2. (uPress) apply the two new MySQL migrations:
#    via shell if available:  php migrations/migrate.php
#    else via the token-gated web runner HealthController::migrate (first-deploy path).
#    Expect: [apply] 004_crop_field_enrichment OK ; [apply] 005_crop_attribute OK ; (re-run = [skip]).

# 3. (Mac — canonical oma-postgres must be up; HMAC ingest key in ./.env) push the data:
cd <repo-on-Mac>
python -m organic_market_agent.publisher.sfa_ingest_push --table crop_field_enrichment
python -m organic_market_agent.publisher.sfa_ingest_push --table crop_attribute
#   (or --table all to refresh everything). Each → HMAC POST https://sfa.nimrod.bio/api/v1/ingest,
#   expect HTTP 200 accepted=<n>. Note the no-default-crop log line from the enrichment fetcher.
```
**Note (topology):** crop data is pushed FROM THE MAC (server oma-postgres lacks the crop-book schema). The
push is outbound HTTPS (not FTPS) and needs the canonical Postgres (oma-postgres docker) + the ingest HMAC key.

## Smoke checks (must PASS — these are LOD AC-09/AC-10, live)
1. `/calc` book-chips populate: `curl -s https://sfa.nimrod.bio/calc/ | grep -c 'SFA_CROP_BOOK'` ≥1 and the
   embedded object is non-empty (selecting a crop fills `[data-book]` chips).
2. A sample crop page (e.g. `/crop-book/<slug>`) shows structured numeric provenance + categorical attributes +
   the COMPLETE/PARTIAL state, sourced from the tables (not only the payload fallback). Spot-check a crop known
   to have enrichment rows.
3. Re-run a push → idempotent (accepted again, no duplicate-key error; row count per crop stable).

## Report
`_COMMUNICATION/team_99/SFA-S003-P004-WP-CB-DATA/DEPLOY_REPORT_v1.0.0.md` (deployed SHA, migrate.php output,
push HTTP results + counts, smoke evidence). On SUCCESS → team_190 L-GATE_V is executable (mandate pre-staged:
`_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-DATA/VALIDATION_MANDATE_team190_LGATE-V_2026-06-03_v1.0.0.md`).
