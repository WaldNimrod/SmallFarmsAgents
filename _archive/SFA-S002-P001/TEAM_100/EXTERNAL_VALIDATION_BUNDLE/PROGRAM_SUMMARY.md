# PROGRAM SUMMARY — SFA-S002-P001 Phase 1

**One-line:** Restored SFA's public price-index from a 19-day public regression to live daily-fresh data via WP REST API migration, plus mobile UI parity preparation.

## Why this program

The OrganicMarketAgent public price-index page on `https://www.nimrod.bio/SmallFarmsAgent` had stopped receiving fresh data on 2026-04-17 (visible to all viewers as 19-day-old prices). Daily ingestion from 5 community sources continued working, but the upload step to uPress's WordPress hosting silently failed every day for 19+ days.

## What changed

| Area | Before | After |
|------|--------|-------|
| Upload protocol | FTPS port 21 (failing — Bezeq home-network egress block) | WP REST API port 443 (working) |
| Public freshness | 19 days stale | <24h fresh |
| Mobile rendering | Desktop-only assumptions | Responsive 375/414/768 + RTL Hebrew + accessible filter UI |
| Server verification | None systematic | team_99 OPS-track verification report (Pass-1 baseline + Pass-2 post-fix) |
| Documentation | FTPS-centric, partial | Authoritative WP REST runbook + PROJECT_CONTEXT pointer |
| Defensive fallback | — | FTPS retained under `UPRESS_FALLBACK_FTPS=1` for non-Bezeq deploy environments |

## What did NOT change (deliberate scope)

- **WP001 (M10 Thaw + Completion)** — DEFERRED to Phase 2. Migrations 072/073, basket_tier_resolver, dev stack docs from `cursor/m10-doc-mandates-spike@bb981ed` are NOT integrated yet.
- **WP002 (MyPIPS Source Integration)** — DEFERRED to Phase 2. The 4 priority sources (mashtelatharoe, anatiyot, fruit4soul, finerotem) are NOT yet onboarded.
- Post-M9 LOD200 features (WP-A1 moderated submissions, WP-A2 farmer calculator) — DEFERRED beyond S003.
- Tend exports + MasterClass PDFs (raw material) — UNTOUCHED on `cursor/mypips-communication-and-handoffs`.

## Diagnostic chain (for the validator's audit trail)

1. WP003 Pass-1 found public stale (F-01 HIGH).
2. WP006 hypothesized TLS-session-reuse code regression — sfa_build (Sonnet) verified code was correct; 14 tests pass. WP006 PASS_CODE_CORRECT.
3. team_99 production smoke + team_100 network probes via `/server` proved Bezeq blocks port 21 outbound (Mac AND server, even after uPress IP whitelist). Block is on Bezeq egress, not uPress.
4. WP007 opened — replace FTPS with WP REST API on port 443. Pattern adapted from sibling `shaked-wg-agent`.
5. WP007 build PASS (sfa_build Sonnet, commit 73eaf3e), 20/20 tests.
6. team_99 deploy attempt 1 BLOCKED — uPress rejects non-image MIME types. Required mu-plugin install (no remote install path because port 21 + 22 + alt FTP all blocked).
7. team_00 manually installed `wp-content/mu-plugins/sfagent-allow-json.php` via uPress panel file manager.
8. team_100 smoke verified JSON+HTML POST → HTTP 201 from server.
9. team_99 ran full publisher pipeline. 5/5 artifacts uploaded. WP003 Pass-2 PASS.
10. F-01 CLOSED. Site renders fresh data publicly.

## Cross-engine map

| Role | Engine | Confirmed |
|------|--------|-----------|
| Orchestrator (team_100) | Claude Opus 4.7 | This session |
| Builder (sfa_build) | Claude Sonnet 4.6 | Spawned via Agent tool, 3 dispatches (WP004/WP006/WP007) |
| Server ops (team_99) | Claude Code on waldhomeserver | 3 server-side reports filed |
| External validator | non-Opus | This bundle is the dispatch request |

## Bundle entry point for the validator

Read `MANIFEST.md` first. Then `AOS_MAIL_PROMPT.md` for activation. Then per-WP folders for evidence.
