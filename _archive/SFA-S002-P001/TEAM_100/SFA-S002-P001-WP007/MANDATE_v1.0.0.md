# MANDATE — SFA-S002-P001-WP007 — TEAM_100 → sfa_build

**Date:** 2026-05-07
**From:** team_100 (Opus, orchestrator)
**To:** sfa_build (Sonnet, Team 10 builder)
**WP:** SFA-S002-P001-WP007 — HTTP Upload Migration via WP REST API
**Type:** GATE_MANDATE
**Gate:** L-GATE_BUILD (entering)
**Priority:** P0 — actual fix for the launch blocker (F-01)
**Supersedes:** WP006 (code was correct; F-01 root cause was network-level, not TLS)

---

## 1. Identity

You are **sfa_build (Team 10)** running on Claude Sonnet under cross-engine governance. team_100 (Opus) orchestrates; you build; external validates. Stay distinct (Iron Rule #1).

---

## 2. Why this WP exists (story)

WP003 Pass-1 found public artifacts 19 days stale (F-01). WP006 hypothesized TLS-session-reuse code regression — sfa_build (you, in a previous turn) verified the code was correct. team_99 production smoke + team_100 network probes via `/server` proved the actual root cause: **Bezeq home-network blocks outbound port 21 entirely** (both Mac and waldhomeserver), and **uPress IP whitelist did NOT unblock** because the block is on Bezeq egress, not uPress.

**Port 443 to the same uPress IP works.** shaked-wg-agent runs on the same waldhomeserver, uses WP REST API on port 443, uploads daily — verified HTTP 200 from server.

Your job: copy that pattern into SFA.

---

## 3. Binding spec

`_aos/work_packages/S002/SFA-S002-P001-WP007/LOD400_spec.md` — 7 ACs (AC-01..AC-07). Read fully.

---

## 4. Authoritative reference (read-only — do NOT modify)

```
/Users/nimrod/Documents/shaked-wg-agent/shaked_wg_agent/publisher/wp_upload.py
```

This is the proven pattern. Copy it faithfully into SFA, adapting for SFA's 4 artifacts (manifest.json, public_report.json, public_report.html, public_report_body.html) instead of shaked-wg's single HTML.

shaked-wg-agent's production `.env` (on server, NOT in git) has these keys — SFA's `.env` lacks them and team_99 will add them post-build:
- `UPRESS_WP_REST_BASE`
- `UPRESS_WP_APP_USER`
- `UPRESS_WP_APP_PASS`

---

## 5. Working environment

| Item | Value |
|------|-------|
| Branch | `offline/2026-05-07-smallfarmsagents-release-prep` (already checked out) |
| Repo root | `/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/beautiful-antonelli-be5888` |
| Python | 3.11 |
| Network | Outbound port 21 BLOCKED (Bezeq) — do NOT attempt FTPS smoke locally |
| WP REST endpoint | `https://www.nimrod.bio/wp-json/` (verified HTTP 200 from server, no creds locally) |

---

## 6. Architectural choice you must make (LOD400 AC-04)

WP REST `/wp/v2/media` stores files at date-based paths. SFA's existing shortcode reads from a fixed `wp-content/uploads/market/` path. Pick ONE integration path and document in `_COMMUNICATION/team_10/SFA-S002-P001-WP007/SHORTCODE_INTEGRATION_DECISION.md`:

- **A. Manifest URL pointer** — pipeline writes one small `sfagent-manifest-of-urls.json` to media library; shortcode fetches it then dereferences. **PREFERRED.**
- **B. WP option storage** — pipeline POSTs URLs to a WP option; shortcode reads it.
- **C. URL slug pinning** — verify uPress returns stable URL on delete-then-reupload with same canonical filename; hard-code shortcode URLs.

Make a decision based on what's simplest given uPress's actual `/wp/v2/media` behavior. Choose A unless there's a compelling reason against.

---

## 7. Hard constraints

1. **Do NOT modify `ftps_upload.py`** — keep it as defensive fallback (under `UPRESS_FALLBACK_FTPS=1` env var, default off).
2. **Do NOT modify shaked-wg-agent** — reference only.
3. **Do NOT commit credentials** — `.env.example` may have new keys (no values).
4. No DB schema, migrations, collector changes.
5. No `_aos/` writes; no `roadmap.yaml`.
6. **No git push** — commits only. team_100 reviews + pushes.
7. **Do NOT attempt FTPS smoke locally** — port 21 is blocked from this network. Smoke uses `requests.get` against the WP REST URL (just verify endpoint reachability if needed).

---

## 8. Process

1. Read MANDATE + LOD400 + this prompt fully.
2. Read shaked-wg's `wp_upload.py` end-to-end. Internalize the auth pattern, delete-before-overwrite, and Content-Disposition usage.
3. Read SFA's current upload chain: `organic_market_agent/publisher/engine.py`, `ftps_upload.py`, `viewer.py`, `__main__.py` — find where `--upload` is wired.
4. Create `organic_market_agent/publisher/wp_upload.py` with `upload_artifact(local_path, canonical_filename, content_type)` returning `(media_id, public_url)`.
5. Add 3 config fields to `organic_market_agent/utils/config.py` (`upress_wp_rest_base`, `upress_wp_app_user`, `upress_wp_app_pass`); add the 3 lines (no values) to `.env.example`.
6. Wire the publisher to call `wp_upload.upload_artifact` per artifact instead of (or before) FTPS.
7. Implement defensive fallback to FTPS gated on `UPRESS_FALLBACK_FTPS=1` (default off).
8. Make AC-04 architectural choice, document in `SHORTCODE_INTEGRATION_DECISION.md`, implement the chosen path (including `wp_shortcode_install.py` update if needed).
9. Add `tests/test_wp_upload.py` per LOD400 AC-05.
10. Run `pytest tests/test_wp_upload.py -v` — green.
11. Run full suite (DB tests will skip — fine).
12. Run `validate_aos.sh` — 0 FAIL.
13. Update `documentation/05-admin-and-operations/PUBLISH_CHECKLIST.md` §4 (WP REST primary, FTPS opt-in fallback).
14. Append a note in `docs/UPRESS_WORDPRESS_STANDARD_v2.md` (block-on-port-21 → WP REST canonical alternative).
15. Update `CHANGELOG.md` `[Unreleased]` `### Changed`.
16. Author `_COMMUNICATION/team_10/SFA-S002-P001-WP007/DEPLOY_HANDOFF.md` (per LOD400 AC-06) so team_99 can flip the env in one step.
17. Commit with message starting `build(S002-WP007): WP REST API upload — F-01 fix`.
18. Do NOT push.

---

## 9. Reporting back

Final message format per LOD400 §3 AC table. Plus:
- Architectural choice made for AC-04 + rationale.
- Whether `.json` MIME issue was encountered (and the workaround if any).
- Deploy hand-off note ready for team_99.
- Commit SHA(s).

---

## 10. Authority limits

- MAY commit to offline branch.
- MAY NOT push, merge, tag, or issue gate verdicts.
- MAY NOT modify shaked-wg-agent code.
- MAY NOT touch credentials (`.env`, only `.env.example`).
- MAY NOT modify FTPS code (preserve as fallback).

---

*Mandate issued. Cross-engine: Sonnet builder. Production deploy by team_99 after build completes (env update + smoke + WP003 Pass-2).*
