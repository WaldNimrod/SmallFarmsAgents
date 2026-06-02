# DEPLOY MANDATE (R3) — SFA-S003-P004-WP-CB-UI-ALIGN — team_100 → team_99 — v1.0.0

**Date:** 2026-06-02 · **From:** team_100 · **To:** team_99 (OPS / waldhomeserver) · **Routed by:** team_00
**Deploy ref:** `origin/main` @ **b5ad8e5** (R3 cherry-pick merged to main; FF 3ff92ea→b5ad8e5)
**Target:** sfa.nimrod.bio (uPress) · **Method:** `scripts/ftp_deploy_sfa_ui.sh` from waldhomeserver (per prior rounds)

## What changed since the last deploy (R3 — tiny, 2 files)
L-GATE_V R2 BLOCKER F-190-UIALIGN-R2-V02 fix is now on main:
- `templates/macros/rotation_hint.php` — removed the farmer-facing `<span class="meta">family: {latin}</span>`
  debug line (users saw "family: variety" on crop pages).
- `templates/pages/calc_dash.php` — removed the raw `(succession_interval_weeks)` from the disabled
  calc-card message (Hebrew label only).
main already carries V01 (/calc/print) + V02 + V03 from prior rounds. No other delivery-tier change.

## Deploy (waldhomeserver — Mac IP not uPress-allowlisted)
```
git fetch origin && git checkout main && git pull --ff-only origin main   # expect b5ad8e5
git rev-parse --short HEAD
bash scripts/ftp_deploy_sfa_ui.sh
```

## Smoke (PRECISE — the exact checks L-GATE_V R3 will re-run)
```
# V02 residual must be GONE (note: scan for 'family:' WITH and WITHOUT a space):
curl -sL https://sfa.nimrod.bio/crop-book/lettuce    | grep -c 'family:'   # expect 0
curl -sL https://sfa.nimrod.bio/crop-book/watermelon | grep -c 'family:'   # expect 0
# calc disabled card — no raw key in visible text:
curl -sL https://sfa.nimrod.bio/calc/ | grep -c '(succession_interval_weeks)'   # expect 0 (HTML comment is fine if present)
# no regression on prior fixes:
curl -sI https://sfa.nimrod.bio/calc/print      | head -1   # 200
curl -sI https://sfa.nimrod.bio/calc/export.csv | head -1   # 200
for u in / /crop-book/ /calc/ /market/ ; do curl -s -o /dev/null -w "%{http_code} $u\n" https://sfa.nimrod.bio$u ; done  # all 200
```

## Return
Reply to team_100 (`_COMMUNICATION/team_100/`) with deployed SHA + the smoke output → unblocks team_190
**L-GATE_V R3** (final constitutional round). Rollback: re-deploy the prior known-good commit.
