---
id: SFA-S003-P001-WP004-LGATES-MANIFEST
type: BUNDLE_MANIFEST
gate: L-GATE_SPEC
round: 1
from: team_100
to: team_190
date: 2026-05-09
wp: SFA-S003-P001-WP004
---

# L-GATE_SPEC Bundle Manifest — SFA-S003-P001-WP004

**Submitter:** team_100 (Sonnet 4.6)
**Recipient:** team_190 (external constitutional validator — non-Claude per Iron Rule #1)
**Gate:** L-GATE_SPEC, Round 1
**WP:** SFA-S003-P001-WP004 — ספר גידולים: WordPress Integration

---

## §1 What you are validating

A single LOD400 implementation spec for the public-facing crop book delivery pipeline:

| File | Role |
|------|------|
| `_aos/work_packages/S003/SFA-S003-P001-WP004/LOD400_spec.md` | **PRIMARY** — full LOD400 spec, 17 sections, 16 ACs, 6-item risk register |

WP004 builds on WP002 (DB tables + seed, LOD500_LOCKED) and WP003 (Flask views, LOD500_LOCKED, used as the **semantic SSoT for filter parity**). It does not modify either.

---

## §2 Mandatory read order

1. `CLAUDE.md` (project root) — Iron Rules, directory authority, AOS spoke rules
2. `_aos/governance/team_190.md` — your full governance contract
3. `_aos/roadmap.yaml` — confirm WP004 is registered (status `ELIGIBLE`)
4. `_aos/work_packages/S003/SFA-S003-P001-WP004/LOD400_spec.md` — **PRIMARY review target**
5. `_aos/work_packages/S003/SFA-S003-P001-WP002/LOD400_spec.md` — context (LOD500_LOCKED dependency)
6. `_aos/work_packages/S003/SFA-S003-P001-WP003/LOD400_spec.md` — context (semantic SSoT for filter parity)
7. `documentation/05-admin-and-operations/UPRESS_WP_REST_API_PUBLISH_RUNBOOK.md` — operational context (mu-plugin precedent, port 21 block, App Password format)
8. This manifest's §3 (constitutional checklist) and §4 (risk register)

**Reference reading (only if a finding hinges on it):**
- `organic_market_agent/publisher/engine.py` — reference impl for `PublishEngine`
- `organic_market_agent/publisher/wp_upload.py` — canonical WP REST upload path
- `organic_market_agent/publisher/upload_dispatch.py` — single dispatch function
- `organic_market_agent/crop_book/views.py` — filter logic SSoT (lines 234–304)
- `organic_market_agent/crop_book/static/entity_registry.js` — entity registry source

---

## §3 Constitutional Check Matrix (L-GATE_SPEC criteria)

team_100 self-attestation (independent verification by team_190 required — adversarial stance per governance):

| # | Check | Evidence in spec | team_100 self-attestation |
|---|-------|------------------|---------------------------|
| C1 | **Directory authority** | §12 "Directory authority" + §16 AC-16 (no edits to LOD500_LOCKED files) | sfa_build writes only to `organic_market_agent/`, `tests/`, `wordpress/`, `documentation/`. No `_aos/` writes. |
| C2 | **Iron Rule #1 — cross-engine** | §0 metadata "Engine constraint" + §12 row 1 | sfa_build = Sonnet (Claude). team_190 must be non-Claude. |
| C3 | **Iron Rule #4 — single roadmap writer** | §12 row "#4" | No AC directs sfa_build to touch `_aos/roadmap.yaml`. team_100 (this commit) is sole writer for the WP004 entry. |
| C4 | **Iron Rule #7 — ADR034** | §12 row "#7" + §3.3 (read-only queries) | DB online → CropBookPublisher does SELECT only. Roadmap is spoke-native (file-based per ADR034 R9). |
| C5 | **Iron Rule #8 — port canon** | §12 row "#8" | No new long-running listeners. Publisher is one-shot CLI. mu-plugin runs in WordPress process — not a separate listener. |
| C6 | **Scope isolation** | §2.3 reuse table + AC-16 | WP004 is purely additive: new module under `crop_book/publisher/`, new mu-plugin file, two extension points to `wp_upload.py` + `upload_dispatch.py`. No edits to LOD500_LOCKED files. |
| C7 | **ACs are testable** | §11 (16 ACs) + §11.1 (12-case parity matrix) | Every AC has a named test or shell command for verification. Filter parity uses an explicit matrix. |
| C8 | **S002 + Phase-1 regression risk** | AC-15 (market `dispatch_upload` byte-identical), AC-16 (no LOD500_LOCKED edits) | Existing market-report tests must continue to pass; existing crop_book admin tests untouched. |
| C9 | **validate_aos.sh mandate** | AC-14 | Builder must achieve 0 FAIL post-build. |
| C10 | **No half-finished implementations** | §15 out-of-scope is explicit; §16 DoD is concrete | All deferred items are explicitly listed; the v1 surface is complete (CLI publish + mu-plugin + smoke). |
| C11 | **Filter parity is the central correctness invariant** | §8.2 + §11.1 | The semantic SSoT is `crop_book/views.py:234-304`. JS must mirror exactly. 12 matrix cases at L-GATE_S; team_190 may add more at L-GATE_V. |
| C12 | **Operational dependency on manual mu-plugin install is acknowledged** | §7 "Deployment" + §10 step 2 + R-WP004-03 | Precedent: `sfagent-allow-json.php` was installed via uPress File Manager by team_00. Same path here. team_99 owns first publish; team_00 owns mu-plugin upload. |

Findings beyond C1–C12 are also in scope.

---

## §4 Risk register (from spec §14)

| ID | Risk | Severity | Mitigation in spec |
|----|------|----------|-------------------|
| R-WP004-01 | SPA filter parity drift under edge cases not covered by the 12-case matrix | HIGH | AC-04 matrix + team_190 may add cases at L-GATE_V |
| R-WP004-02 | Bundle size — ~5 MB raw JSON borderline | MEDIUM | uPress server gzip is automatic; measured at L-GATE_B; chunking deferred to follow-up WP |
| R-WP004-03 | mu-plugin install requires manual uPress panel step | LOW | Documented in runbook; precedent set by `sfagent-allow-json.php`; team_00 owns this step |
| R-WP004-04 | `entity_registry.js` regex extraction breaks if file format changes | LOW | Loud failure (raises); regression test asserts known entity present |
| R-WP004-05 | WP `wp_remote_get` timeout on slow uPress edges → shortcode renders placeholder | LOW | Transient; 5-min cache absorbs variance; user reload fixes |
| R-WP004-06 | Body-HTML `str_replace` substitution is fragile if body fragment changes | MEDIUM | Builder-side assertion that the literal sentinel string is present; PHP-side logs failure to substitute |

---

## §5 Verdict format

### §0 Verdict Box (MANDATORY — must appear first in chat response)

```
╔══════════════════════════════════════════════════════════════╗
║  VERDICT: [PASS / PASS_WITH_FINDINGS / BLOCKED]              ║
║  WP: SFA-S003-P001-WP004   Gate: L-GATE_SPEC                ║
║  Round: 1                                                     ║
║  Next step: [one line]                                        ║
╚══════════════════════════════════════════════════════════════╝
```

### Verdict artifact

Write to: `_COMMUNICATION/team_190/SFA-S003-P001-WP004/LOD400-VERDICT_v1.0.0.md`

Frontmatter:
```yaml
---
id: SFA-S003-P001-WP004-LOD400-VERDICT
type: L-GATE_SPEC verdict
validator: team_190
date: [YYYY-MM-DD]
wp: SFA-S003-P001-WP004
verdict: PASS | PASS_WITH_FINDINGS | BLOCKED
---
```

Body sections:
- §0 Summary (one paragraph)
- §1 Constitutional Checks C1–C12 (table)
- §2 Additional findings (beyond C1–C12)
- §3 WP004-specific findings
- §4 Recommendation (one of PASS / PASS_WITH_FINDINGS / BLOCKED with actionable reason)

### Commit

```bash
git add _COMMUNICATION/team_190/SFA-S003-P001-WP004/LOD400-VERDICT_v1.0.0.md
git commit -m "validate(SFA-S003-P001-WP004/L-GATE_SPEC): {VERDICT} — Team 190"
```

---

## §6 Done criteria

Session is complete when:
1. §0 verdict box shown in chat
2. Verdict artifact written to `_COMMUNICATION/team_190/SFA-S003-P001-WP004/LOD400-VERDICT_v1.0.0.md`
3. Artifact committed (commit message per §5)
4. Confirmation message posted to `_COMMUNICATION/TEAM_100/` as `MSG-team190-to-team100-S003-WP004-LOD400-VERDICT-[DATE].md`

---

## §7 Bundle file inventory

| File | Bytes | Purpose |
|------|-------|---------|
| `MANIFEST.md` | (this file) | Bundle entry point + checklist + verdict format |
| `TEAM_190_ACTIVATION_PROMPT.md` | sibling | Canonical AOS_MAIL activation prompt for team_190 |

Verdict landing zone (created, awaiting team_190): `_COMMUNICATION/team_190/SFA-S003-P001-WP004/`

---

*Bundle prepared 2026-05-09 by team_100 (Sonnet 4.6).*
*Branch: `claude/strange-mcnulty-651551`. Worktree: `strange-mcnulty-651551`.*
