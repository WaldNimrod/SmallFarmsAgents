# DECISION — SFA Hosting/Deploy Canon — Drift Root-Cause & Canonical Fix — team_100 — v1.0.0

**Date:** 2026-05-29
**Author:** team_100 (Chief Architect)
**WP:** (cross-cutting — architecture/canon; no WP)
**Type:** DECISION / architecture clarification
**Trigger:** team_00 in-session directive 2026-05-29 — "the site MUST be on the uPress subdomain, NOT the home server; this drift recurs — locate the source and update the architecture & deployment fully and canonically."

---

## 1. Problem

A recurring drift: agents (and prose in operational artifacts) conclude that the
public site `sfa.nimrod.bio` is *served from* the home server (`waldhomeserver`).
It is not. The live site is served from **uPress** (shared LAMP, Slim/PHP + MySQL).

## 2. Root-cause analysis (where the drift comes from)

The **binding canon was already correct** — the drift is seeded by *other* docs an
agent reads first or alongside it:

| # | Source | Problem | Severity |
|---|--------|---------|----------|
| 1 | `_aos/context/PROJECT_CONTEXT.md` §"WordPress / uPress — public market index (as of 2026-05-07)" | **Mandatory session-startup read** (CLAUDE.md startup step 2) still described the **superseded** `www.nimrod.bio` WordPress / WP-REST / mu-plugin tier as current and named its runbook "AUTHORITATIVE". Every new session absorbed the old model first. | **ROOT** |
| 2 | `CLAUDE.md` Domain rules — Stack line + Upload-path (WP008) bullet | Called the delivery layer "WordPress presentation layer (uPress hosting)"; framed WP-REST upload as the current path. | HIGH |
| 3 | `UPRESS_WP_REST_API_PUBLISH_RUNBOOK.md`, `WORDPRESS_PUBLIC_PUBLISH_RUNBOOK.md`, `PUBLISH_CHECKLIST.md`, `docs/UPRESS_WORDPRESS_STANDARD_v2.md` | www-era runbooks with **no superseded banner** → still mined as current; one even has a heading "Production home server (waldhomeserver)". | HIGH |
| 4 | Terminology: "deploy host" / "OPS deploy host" (deploy reports, roadmap notes) | The word **"host"** conflates *the machine you deploy **from*** (waldhomeserver relay) with *the machine that **serves*** (uPress). | MEDIUM |

The actual architecture: delivery on `www.nimrod.bio` (WordPress) → migrated to the
dedicated subdomain `sfa.nimrod.bio` (uPress LAMP) at **P003, 2026-05-23**; the legacy
www tier was **severed 2026-05-28** (env + code + cron). So "once it really was
different" = the pre-P003 www WordPress tier, whose docs were never demoted.

## 3. Canonical resolution (the binding answer)

Three roles, never conflated (now stated identically in every entry point):

| Role | Machine | Serves end-user HTTP? |
|------|---------|------------------------|
| **Web host** (live site + MySQL read-mirror) | **uPress** `sfa.nimrod.bio` (Cloudflare edge) | **YES — only here** |
| **Backend / pipeline host** (canonical Postgres SSoT, scrapers, agents, cron) | **waldhomeserver** | **NO — never** |
| **Deploy / push origin** (FTPS upload relay; egress uPress-allowlisted, Mac/Bezeq is not) | **waldhomeserver** | n/a — relay only |

**The live site MUST be served from the uPress subdomain `sfa.nimrod.bio`, never from
waldhomeserver.** Code deploy → `UI_DEPLOY_RUNBOOK.md` (`scripts/ftp_deploy_sfa_ui.sh`,
`lftp mirror` to uPress). Data push → `sfa_ingest_push.py` (`POST /api/v1/ingest`, HMAC).
SSoT: `documentation/02-architecture/sfa-delivery-tier.md` (+ `02-architecture/README.md` hard invariant).

## 4. Edits applied this session

1. `documentation/02-architecture/sfa-delivery-tier.md` — added **§0 Terminology — "host" disambiguation (anti-drift, binding)** with the 3-role table + superseded note.
2. `_aos/context/PROJECT_CONTEXT.md` — replaced the stale "WordPress / uPress — public market index" section with **"Public delivery tier — sfa.nimrod.bio (canonical)"**: anti-drift host table, SSoT + current deploy/data pointers, durability caveat, explicit SUPERSEDED list (www tier).
3. `CLAUDE.md` Domain rules — fixed Stack line (Slim 4/PHP 8 delivery tier); added **"⚠ Delivery & hosting canon"** bullet (3-role disambiguation); replaced "Upload path (WP008)" with "Deploy paths (current)" + SUPERSEDED note. (Preserved-across-sync project section.)
4. SUPERSEDED banners added to 4 www-era runbooks: `UPRESS_WP_REST_API_PUBLISH_RUNBOOK.md`, `WORDPRESS_PUBLIC_PUBLISH_RUNBOOK.md`, `PUBLISH_CHECKLIST.md`, `docs/UPRESS_WORDPRESS_STANDARD_v2.md`.
5. This DECISION artifact (audit record).

## 5. Not changed (deliberately)

- `_aos/roadmap.yaml` gate_history prose and `_archive/**` reports — immutable historical record; the canon fix lives in the live docs above, not by rewriting history.
- The www-era publisher code (`wp_upload.py`/`ftps_upload.py`/`upload_dispatch.py`/`static_upload.py`) — retained as audit/defensive; flagged SUPERSEDED in CLAUDE.md, not deleted (separate cleanup WP if desired).

## 6. Verification

- `validate_aos.sh` → 0 FAIL (see commit).
- The disambiguation now appears at all three places an agent reads first: session-startup `PROJECT_CONTEXT.md`, always-loaded `CLAUDE.md`, and the architecture SSoT.

---

*team_100 (Claude Opus 4.8) — 2026-05-29. Authorized in-session by team_00 (Principal).*
