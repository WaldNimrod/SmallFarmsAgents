# MANDATE — SFA-S002-P001-WP003 — TEAM_100 → team_99

**Date:** 2026-05-07
**From:** team_100 (sfa_arch, Claude Opus 4.7 — orchestrator)
**To:** team_99 (Home Server Team, terminal-managed Claude Code on waldhomeserver)
**WP:** SFA-S002-P001-WP003 — Server Scraping Verification
**Type:** GATE_MANDATE
**Gate:** L-GATE_BUILD (entering — team_99 self-attests OPS-track per ADR044 §1 / team_99 contract §43-49)

---

## 1. Identity (you, on the server)

You are **team_99 (Home Server Team)** running on `waldhomeserver` via SSH/terminal. You operate in `OUT_OF_GATE_ISOLATED` mode. For OPS-track WPs (this is one) you self-attest L-GATE_BUILD upon completion — team_190 cross-engine validation is NOT required for this WP since no application-code merge to `main` is involved.

Per your contract §63: **No application code changes** under this WP. This is a read-only verification operation.

---

## 2. Binding spec

Read fully and treat as binding work order:
`_aos/work_packages/S002/SFA-S002-P001-WP003/LOD400_spec.md`

7 Acceptance Criteria (AC-01..AC-07) define DONE.

---

## 3. Branch + working directory

The WP004 mandate work and the LOD400 spec live on the **offline branch**:

```
branch:    offline/2026-05-07-smallfarmsagents-release-prep
remote:    origin (already pushed)
spoke:     /data/projects/smallfarmsagents/   (on waldhomeserver)
```

**First action on the server:**
```bash
cd /data/projects/smallfarmsagents
git fetch origin
git checkout offline/2026-05-07-smallfarmsagents-release-prep
git pull
```

Read the LOD400 spec and this mandate from this branch.

---

## 4. Verification scope (per LOD400 §3)

Execute verification across these AC dimensions and capture evidence per AC:

- **AC-01** Scheduler enabled + recent (last successful ingest + publish < 24h)
- **AC-02** Per-collector freshness (every active collector ran successfully in last 24h; 7d run count ≥ baseline−20%)
- **AC-03** Log integrity (no undocumented ERROR/CRITICAL in last 7d; no open `pipeline_alerts` older than 7d)
- **AC-04** Public artifact freshness (FTPS round-trip): `manifest.json` HTTP 200 + `artifact_version` matches host + `staleness_level ∈ {fresh, acceptable}`
- **AC-05** Public page renders: `https://www.nimrod.bio/SmallFarmsAgent` HTTP 200; shortcode renders without errors
- **AC-06** Index integrity gate (≥ 2 distinct community sources in rolling window)
- **AC-07** Verification report filed at `_COMMUNICATION/team_99/SFA-S002-P001-WP003/VERIFICATION_REPORT_v1.0.0.md` (note: WP003 LOD400 says `_COMMUNICATION/TEAM_60/...` — adjust to `team_99/` since you are the executor; cross-reference both teams in the report header)

The report schema is in LOD400 §5. Use it verbatim (sections 1–6).

---

## 5. Hard constraints

1. **No application code changes.** No git commits to `organic_market_agent/**`, no migrations, no schema changes, no scheduler-config edits.
2. **No service restarts** unless verification reveals a failure that team_00 explicitly authorizes a restart for.
3. **No edits to `_aos/`** (Iron Rule #11 / your contract IR#13). Roadmap/gate updates go to team_100 via REPORT artifact.
4. **Secrets discipline** (your IR#3): no SSH keys, env values, or credentials in artifacts or commits.
5. **No exposure of internal IPs/ports** (your IR#12) in the report. Use logical names (`waldhomeserver`, `aos-api`).
6. **Push authority** (per your contract Push Authority section): you MAY push the verification report to origin/main directly. You MUST NOT push outside the allowed paths.

---

## 6. Process

1. `/server --status` — capture pre-verification snapshot.
2. Open `documentation/05-admin-and-operations/PUBLISH_CHECKLIST.md` and run sections 1–4 (skip §5 lead review).
3. Inspect cron / systemd timer for the daily pipeline. Capture last 7 invocation timestamps.
4. Inspect `pipeline_alerts` and pipeline log files. Search for ERROR/CRITICAL.
5. Curl `https://www.nimrod.bio/wp-content/uploads/market/manifest.json` — record HTTP code + `artifact_version` + `staleness_level` + `product_count`.
6. Compare public `manifest.json` against host-side `output/public/manifest.json` (≤ 60 min lag tolerated for ezCache).
7. Curl `https://www.nimrod.bio/SmallFarmsAgent` — record HTTP code; if available, render a screenshot (or note "rendering verified via curl + visual inspection").
8. Per-collector check: query `raw_extracted_items` counts per source over trailing 7 days and per source last successful run.
9. Compose the verification report per LOD400 §5 schema. Verdict = **PASS** / **PASS_WITH_FINDINGS** / **FAIL**.
10. Save report to `_COMMUNICATION/team_99/SFA-S002-P001-WP003/VERIFICATION_REPORT_v1.0.0.md` and a copy to `_COMMUNICATION/TEAM_60/reports/2026-05-XX_SCRAPING_VERIFICATION_TEAM60.md` (cross-team delivery per your push authority — reports CAN be pushed to other teams' inboxes).
11. Push to `origin/main`.

---

## 7. Two-pass note

This is **Pass-1 (baseline)** of WP003. After WP001 (M10 thaw) and WP002 (MyPIPS sources) land on production, WP003 will run **Pass-2** (full collector roster). Mark this verification clearly as `pass: 1` in the report frontmatter.

---

## 8. Reporting back

Final report content per LOD400 §5 schema. Verdict line is the headline. If FAIL — describe each failed AC with severity, evidence, and recommendation; do NOT take corrective code action.

Report path will be picked up by team_100 for inclusion in the WP005 external validation bundle.

---

## 9. Authority limits (recap)

- You MAY push verification report to origin/main (allowed path: `_COMMUNICATION/team_99/**` + `_COMMUNICATION/*/REPORT_team_99_*.md`).
- You MAY run read-only commands on the server.
- You MAY NOT change application code, restart services, modify governance, or issue gate verdicts beyond OPS-track L-GATE_BUILD self-attestation.
- You MAY NOT modify `_aos/roadmap.yaml` or `_aos/governance/`.

---

## 10. References

- LOD400 spec: `_aos/work_packages/S002/SFA-S002-P001-WP003/LOD400_spec.md`
- Program package: `_COMMUNICATION/TEAM_100/SFA-S002-P001/PROGRAM_PACKAGE_LOD200_v1.0.0.md`
- Publish checklist: `documentation/05-admin-and-operations/PUBLISH_CHECKLIST.md`
- WordPress publish runbook: `documentation/05-admin-and-operations/WORDPRESS_PUBLIC_PUBLISH_RUNBOOK.md`
- Server agent comms: `documentation/05-admin-and-operations/WALD_HOME_SERVER_AGENT_COMMUNICATION.md`
- Your governance contract: `_aos/governance/team_99.md`
- ADR-049 (server-side push authority): hub `governance/directives/ADR-049_*`
- ADR034 R8/R9 (offline DB): your contract §74-93

---

*Mandate issued. team_99 self-attests L-GATE_BUILD upon successful verification. Pass-1 baseline only — Pass-2 follows after WP001 + WP002.*
