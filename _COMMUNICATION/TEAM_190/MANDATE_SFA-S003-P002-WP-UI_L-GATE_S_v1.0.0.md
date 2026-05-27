---
id: MANDATE_SFA-S003-P002-WP-UI_L-GATE_S_v1.0.0
from: Team 100 (Chief System Architect — smallfarmsagents spoke)
to: Team 190 (External Constitutional Validator)
date: 2026-05-24
type: GATE_MANDATE
gate: L-GATE_S
wp: SFA-S003-P002-WP-UI
project: smallfarmsagents
status: ACTIVE
verdict: PENDING
engine_constraint: "Cross-engine per IR#1. builder=sfa_build (Claude Sonnet), validator=team_190 (non-Claude — GPT-5 / GPT-5.5 / Cursor Composer / Codex). Do NOT validate this from Claude."
resubmission_round: 1
---

# L-GATE_S Mandate — SFA-S003-P002-WP-UI

**Standalone web UX shell — adopt team_35 LOD300 onto Slim/PHP/uPress**
**Track:** A | **Profile:** L0 | **Risk:** MEDIUM

---

## 2. Prior Gate History

| Gate | Result | Date | Validator | Notes |
|------|--------|------|-----------|-------|
| L-GATE_E | PASS | 2026-05-24 | team_00 | team_00 in-session approval of Option B (adapt team_35 LOD300 v1.2.0 design to deployed Slim/PHP/uPress stack). team_35 had assumed Flask+gunicorn+waldhomeserver — incompatible with parent DECISION_SFA-S003-P003 §2 (waldhomeserver = backend only). LOD400 preserves all team_35 design intent and supersedes only the IMPLEMENTATION_PLAN (Flask → PHP/Slim). 22 ACs. 10 risks. No GCRs. 14.5h budget. |

This is **Round 1** for L-GATE_S — no prior validation attempt.

---

## 3. Scope

**L-GATE_S — Spec authorization.** Validate that the LOD400 spec is complete, coherent, and ready to dispatch to a builder.

Specifically: does the LOD400 correctly translate the team_35 LOD300 design intent into a deployable Slim/PHP/uPress implementation plan that honors the parent architectural decisions (DECISION_SFA-S003-P003), the canonical architecture/schema docs (`documentation/02-architecture/sfa-delivery-tier.md`, `documentation/03-data-and-schema/sfa-mysql-mirror.md`), and the Iron Rules (especially IR#1 cross-engine, IR#4 single roadmap writer)?

A PASS here authorizes team_100 to dispatch BUILD to sfa_build. A FAIL means team_100 must amend the LOD400.

**You are not validating any code in this gate** — code does not exist yet. You are validating spec quality and architectural fitness.

---

## 4. Validation Criteria

| # | Criterion | What to Check |
|---|-----------|---------------|
| VC-1 | **Architectural consistency** (BLOCKING) | LOD400 §2 + §3.1-§3.6 + §4: does the spec honor `DECISION_SFA-S003-P003 §2` ("waldhomeserver = backend only; uPress = ONLY public-facing tier")? Are Slim/PHP/MySQL used throughout with no Flask/Jinja2/SQLAlchemy/gunicorn paths smuggled in? Does §2 explicitly enumerate what survives from team_35 LOD300 vs what is replaced? |
| VC-2 | **AC completeness** | LOD400 §5 lists 22 ACs. Does each of the 14 page templates (§3.3) have at least one AC? Do all 5 new API endpoints (§4) have ACs? Is regression of existing live functionality (`/api/v1/health`, `/api/v1/crops`, `/api/v1/products`, `/api/v1/ingest`, waldhomeserver cron) covered? Is the `/crop-book/* → /book/*` 301 redirect covered? Are non-functional requirements (LCP, console errors, WCAG AA, RTL correctness) covered? |
| VC-3 | **Risk register adequacy** | LOD400 §8: 10 risks listed. Are material risks NOT listed (specifically: rate-limit collisions on `community_contributions` if NAT'd users share IPs; CSS cascade ordering bugs; PHP version compatibility on uPress; Cloudflare cache invalidation; uPress nginx `.htaccess` partial-honor F-1 carry-over)? Are mitigations testable / actionable (not vague)? Is each high-impact risk (R-04 spam, R-05 modules YAML↔PHP drift, R-07 CF stale-redirect) mitigated to acceptable residual? |
| VC-4 | **GCR analysis correctness** | LOD400 §6: team_100 claims zero locked-file changes. Verify: is `organic_market_agent/crop_book/models.py` on waldhomeserver truly untouched? Is the canonical schema doc (`documentation/03-data-and-schema/sfa-mysql-mirror.md`, which lists 4 data + 2 plumbing tables) consistent with the new `community_contributions` table — should the canonical doc be updated as part of this WP, or as carry-over? Are the deprecated `wp_upload.py` / `ftps_upload.py` / `upload_dispatch.py` modules untouched (already DEPRECATED-annotated from WP-S003-P003-WP-5)? |
| VC-5 | **Test plan adequacy** | LOD400 §9: are unit + integration + visual tests appropriately partitioned? Will phpunit run against MySQL on uPress, or stays sqlite-backed in-memory (the spec doesn't specify — flag if a decision is needed)? Is Lighthouse automation realistic on a Hebrew RTL Heebo/Frank Ruhl Libre + 7 CSS file site? Visual diff: who runs it (Claude_in_Chrome at BUILD time? team_190 at L-GATE_V?), what's the diff threshold? |
| VC-6 | **Out-of-scope discipline** | LOD400 §7: are the 9 deferred items genuinely deferrable (no MVP-killers hidden)? Specifically: email notification on contribution — is "DB-only, review via phpMyAdmin" acceptable for v1, or does team_00 expect notification? Calculator stub showing "בקרוב" — is that a UX promise that must materialize within S004? |
| VC-7 | **Phase plan realism** | LOD400 §11: 14.5h total for 8 phases — is each phase budget realistic given the deliverable count? B.4 budgeted 3h for 5 templates + controller methods — adequate? B.8 budgeted 1h for 28 screenshots + Lighthouse + report — adequate? Any phase that should be split? Any sequencing risk (B.3 hub depends on B.2 shells; B.4-7 share macro dependencies — well-ordered)? |

**Total: 7 criteria.** VC-1 is BLOCKING — a FAIL here is auto-FAIL on the whole gate.

---

## 5. Files to Review

### Spec Documents (binding)
- **LOD400 (primary review target):** `_aos/work_packages/S003/SFA-S003-P002-WP-UI/LOD400_spec.md`
- LOD300 source (team_35): `_COMMUNICATION/team_35/SFA-S003-P002-WP-UI/_handoff/HANDOFF_LOD300.md`
- LOD300 implementation plan (explicitly superseded by LOD400 §11): `_COMMUNICATION/team_35/SFA-S003-P002-WP-UI/_handoff/IMPLEMENTATION_PLAN.md`
- LOD300 components / templates / tokens (context — preserved verbatim by LOD400):
  - `_COMMUNICATION/team_35/SFA-S003-P002-WP-UI/_handoff/DESIGN_TOKENS.md`
  - `_COMMUNICATION/team_35/SFA-S003-P002-WP-UI/_handoff/COMPONENTS.md`
  - `_COMMUNICATION/team_35/SFA-S003-P002-WP-UI/_handoff/TEMPLATES.md`
  - `_COMMUNICATION/team_35/SFA-S003-P002-WP-UI/_handoff/MODULES_REGISTRY.yaml`

### Architectural authority (binding context)
- Parent DECISION: `_COMMUNICATION/team_00/DECISION_SFA-S003-P003_DEDICATED_SFA_SUBDOMAIN_2026-05-23_v1.0.0.md`
- Canonical architecture: `documentation/02-architecture/sfa-delivery-tier.md`
- Canonical schema: `documentation/03-data-and-schema/sfa-mysql-mirror.md`
- Existing live system (current sfa_delivery/): `sfa_delivery/` (Slim PHP 4 app; 27 source files; live at https://sfa.nimrod.bio)
- Existing publisher: `organic_market_agent/publisher/sfa_ingest_push.py` (waldhomeserver cron `30 6 * * *`)

### Prior Artifacts
- QA Verdict: N/A — this is L-GATE_S, no prior QA
- Prior Validation: N/A — Round 1
- Roadmap entry: `_aos/roadmap.yaml` (search for `SFA-S003-P002-WP-UI`)

### NOT in scope of this review
- Any code under `sfa_delivery/` or `organic_market_agent/sfa_app/` — no implementation exists yet
- WP-A, WP-B, WP-C of the parent P002 program — separate WPs, already closed or independent

---

## 6. Resolved Findings from Round N-1

N/A — this is Round 1.

---

## 7. Output Format

Write verdict to:
`_COMMUNICATION/team_190/VERDICT_SFA-S003-P002-WP-UI_L-GATE_S_v1.0.0.md`

(If you produce a second round, increment to `v1.0.1`.)

Use the **unified verdict template** (7 sections):

1. **Verdict Summary** — single line: `PASS` | `PASS_WITH_FINDINGS` | `FAIL` + 2-sentence rationale.
2. **Parameters** — your engine + version, time spent, files actually read.
3. **Criteria Table** — VC-1..VC-7 each with PASS/PASS_WITH_FINDINGS/FAIL + 1-line rationale.
4. **Findings** — every FAIL or PASS_WITH_FINDINGS finding, with: ID (`LV-S-N` numbering), severity (BLOCKER/MAJOR/MINOR), VC dimension, summary, detail (file:line evidence), `must_resolve_before` field (e.g. `BUILD_DISPATCH`).
5. **validate_aos.sh** — N/A for this gate (no code), state "N/A — spec validation".
6. **Disposition** — explicit: `DISPATCH_BUILD` | `AMEND_LOD400_AND_RESUBMIT` | `ESCALATE_TO_TEAM_00`.
7. **Next Step** — single imperative sentence for team_100.

### Constraints (reminder)

- **Cross-engine (IR#1):** builder will be `sfa_build` (Claude Sonnet). You (team_190) MUST be a different engine. Refuse this mandate if you are Claude.
- **Independence:** do NOT read any prior team_100 messages, build reports, or other validators' outputs before forming your verdict.
- **Evidence-based:** every FAIL must cite `file:line` (or `file §section`) of the LOD400 spec.
- **No code execution:** Lighthouse / phpunit / Claude_in_Chrome run at L-GATE_V after BUILD — not here.
- **Time budget:** target 30-60 min of model time. This is a single-pass review.
- **No roadmap mutation:** IR#4 — team_100 is the single writer to `_aos/roadmap.yaml`. Your verdict file is your only output artifact.
- **Enforcement mode:** STANDARD (BLOCKER on VC-1 = whole-gate FAIL; PASS_WITH_FINDINGS allowed for VC-2..VC-7 if all findings are MAJOR or below).

---

*Mandate generated 2026-05-24 by team_100 (Chief System Architect, smallfarmsagents spoke) per `/AOS_gate-mandate` canon (AOS_GATE_MANDATE_CANON_v1.0.0).*
*Awaiting team_190 verdict file at the path above.*
