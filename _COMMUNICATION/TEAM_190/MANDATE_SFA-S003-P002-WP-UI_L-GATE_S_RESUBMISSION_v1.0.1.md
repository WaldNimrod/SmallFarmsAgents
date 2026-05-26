---
id: MANDATE_SFA-S003-P002-WP-UI_L-GATE_S_v1.0.1
from: Team 100 (Chief System Architect — smallfarmsagents spoke)
to: Team 190 (External Constitutional Validator)
date: 2026-05-27
type: RESUBMISSION
gate: L-GATE_S
wp: SFA-S003-P002-WP-UI
project: smallfarmsagents
status: ACTIVE
verdict: PENDING
engine_constraint: "Cross-engine per IR#1. builder=sfa_build (Claude Sonnet), validator=team_190 (non-Claude — GPT-5.5 / Cursor Composer / Codex as in R1). Do NOT validate this from Claude."
resubmission_round: 2
supersedes: MANDATE_SFA-S003-P002-WP-UI_L-GATE_S_v1.0.0
prior_verdict: _COMMUNICATION/TEAM_190/VERDICT_SFA-S003-P002-WP-UI_L-GATE_S_v1.0.0.md
---

# L-GATE_S Mandate (Round 2) — SFA-S003-P002-WP-UI

**Standalone web UX shell — adopt team_35 LOD300 onto Slim/PHP/uPress**
**Track:** A | **Profile:** L0 | **Risk:** MEDIUM

---

## 2. Prior Gate History

| Gate | Result | Date | Validator | Notes |
|------|--------|------|-----------|-------|
| L-GATE_E | PASS | 2026-05-24 | team_00 | In-session approval of Option B (adapt team_35 LOD300 to Slim/PHP/uPress). |
| L-GATE_S | **FAIL** | 2026-05-27 | team_190 (GPT-5.5/Cursor) | Round 1 — 5 findings: 2 BLOCKER (LV-S-1 community writes contradict S003 read-only tier; LV-S-2 URL contract change `/crop-book/*` → `/book/*` violates frozen contract) + 2 MAJOR + 1 MINOR. Disposition: AMEND_LOD400_AND_RESUBMIT. Verdict: `_COMMUNICATION/TEAM_190/VERDICT_SFA-S003-P002-WP-UI_L-GATE_S_v1.0.0.md` (commit `887204c`). |

This is **Round 2** for L-GATE_S — team_100 amended LOD400 to v1.0.1.

---

## 3. Scope

Same as Round 1: spec authorization. Validate that LOD400 v1.0.1 is now ready to dispatch to a builder.

**Specific focus for this round:** verify that **all 5 R1 findings are resolved**, AND that the amendments did not introduce regressions in any of the dimensions that previously passed (VC-3, VC-5, VC-6, VC-7 were PASS_WITH_FINDINGS — those findings must also be addressed).

You are not validating any code in this gate — code does not exist yet. You are validating spec quality and architectural fitness.

---

## 4. Validation Criteria

Same 7 VCs as R1 (V-1..V-7), with explicit re-check expectations per finding.

| # | Criterion | What to Check (R2 emphasis) |
|---|-----------|-----------------------------|
| VC-1 | **Architectural consistency** (BLOCKING) | (a) LV-S-1 BLOCKER resolved? — Confirm `community_contributions` table, `POST /api/v1/community/contribute`, `GET /api/v1/community/feed`, and the `CommunityController` class are ALL removed from LOD400 v1.0.1. Verify `community.php` template is described as STATIC (no form). (b) LV-S-2 BLOCKER resolved? — Confirm `/crop-book/*` is restored as canonical in §4 routes; no `/book/*` routes; no 301 redirect block. (c) No NEW architectural contradictions introduced. |
| VC-2 | **AC completeness** | LV-S-3 MAJOR resolved? — Verify §5 has been restructured into a route-by-route matrix. Each of the 14 HTML routes (§3.3) AND each API endpoint in §4 must have at least one functional AC. Total AC count should be ≥ 30 (R1 had 22 — coverage gaps fixed). Specifically check: `/about`, `/crop-book/questions`, `/crop-book/family`, `/crop-book/table`, `/crop-book/search`, `/crop-book/{slug}/variety/{vslug}`, `/market/{slug}`, `/community`, `/search`, `/api/v1/market/{slug}/history`. |
| VC-3 | **Risk register adequacy** | LV-S-4 partial-MAJOR resolved? — Verify R-11 (PHP/uPress compat) is added; R-04 (community spam) is either marked moot or removed; R-07 (CF 301 cache) is moot or removed; R-12 (CF cache invalidation post-deploy) is added. |
| VC-4 | **GCR analysis correctness** | LV-S-1/LV-S-4 derivative: verify §6 now correctly states no canonical schema/architecture doc updates required (since community writes deferred + URL contract unchanged). Verify NO drift between LOD400 v1.0.1 and `documentation/02-architecture/sfa-delivery-tier.md` + `documentation/03-data-and-schema/sfa-mysql-mirror.md`. |
| VC-5 | **Test plan adequacy** | LV-S-4 partial-MAJOR resolved? — Verify §9.1 declares `sqlite::memory:` for phpunit + dialect-aware controller pattern from WP-2; §9.2 declares visual diff owner (sfa_build at B.8a), method (Claude_in_Chrome), threshold (±4 px), artifact location; §9.3 declares Lighthouse runner + thresholds + artifact location; §9.5 has an ownership matrix. |
| VC-6 | **Out-of-scope discipline** | Verify §7 explicitly lists community writes as deferred to S004 (with binding-doc reference). Verify the deferral chain is internally consistent with §6 GCR analysis. |
| VC-7 | **Phase plan realism** | LV-S-5 MINOR resolved? — Verify B.8 has been split into B.8a (1.5h, visual evidence) + B.8b (1h, Lighthouse + smoke + report). Total phase count = 9 (was 8). Total hours ≈ 13 (was 14.5; community drop offsets split). |

**VC-1 remains BLOCKING. A FAIL on VC-1 = whole-gate FAIL.**

---

## 5. Files to Review

### Spec Documents (binding for review)
- **LOD400 v1.0.1 (primary target):** `_aos/work_packages/S003/SFA-S003-P002-WP-UI/LOD400_spec.md`
  - Read §0 first — that's the Round 2 amendment summary
  - Then read §3, §4, §5, §6, §7, §8, §9, §11 to verify each R1 finding's resolution
- **R1 verdict (your prior output, for self-reference):** `_COMMUNICATION/TEAM_190/VERDICT_SFA-S003-P002-WP-UI_L-GATE_S_v1.0.0.md`
- **R1 mandate (superseded):** `_COMMUNICATION/TEAM_190/MANDATE_SFA-S003-P002-WP-UI_L-GATE_S_v1.0.0.md`

### Architectural authority (binding context — unchanged from R1)
- Parent DECISION: `_COMMUNICATION/team_00/DECISION_SFA-S003-P003_DEDICATED_SFA_SUBDOMAIN_2026-05-23_v1.0.0.md`
- Canonical architecture: `documentation/02-architecture/sfa-delivery-tier.md`
- Canonical schema: `documentation/03-data-and-schema/sfa-mysql-mirror.md`
- team_35 LOD300 source: `_COMMUNICATION/team_35/SFA-S003-P002-WP-UI/_handoff/HANDOFF_LOD300.md`

### Prior Artifacts
- QA Verdict: N/A
- Prior Validation: `_COMMUNICATION/TEAM_190/VERDICT_SFA-S003-P002-WP-UI_L-GATE_S_v1.0.0.md` (R1 FAIL)

---

## 6. Resolved Findings from Round 1

| # | Finding | Severity | Fix Applied (LOD400 v1.0.1 reference) | Verification |
|---|---------|----------|---------------------------------------|--------------|
| LV-S-1 | Public community writes contradict S003 read-only tier | BLOCKER | §0 (amendment summary); §3.4 (CommunityController removed); §3.6 (migration 004 removed); §4 routes (POST /contribute, GET /feed removed; `/community` now served by HubController as static page); §5 AC-20 (NO form, NO POST); §7 (deferred to S004 with binding-doc ref). | `grep -i community LOD400_spec.md` should return only static-page + deferral mentions; no `POST.*community` matches |
| LV-S-2 | URL contract change `/crop-book/* → /book/*` violates frozen contract | BLOCKER | §0; §4 routes (all `/crop-book/*` restored as canonical; no `/book/*`; no 301 block); §5.2 AC-11..AC-17 all use `/crop-book/*`; §7 (new `/book/*` aliases explicitly deferred to future DECISION). | `grep -E 'GET /book' LOD400_spec.md` should return only references in deferred items or team_35 design context |
| LV-S-3 | ACs don't cover every page + endpoint | MAJOR | §5 restructured: §5.1 foundation, §5.2 per-route matrix (14 rows × functional + visual), §5.3 API ACs (10 rows), §5.4 non-functional (5), §5.5 regression (3). Total 38 ACs (up from 22). | Count rows in §5 tables; should be ≥ 30 |
| LV-S-4 | Risk/test environment specifics under-declared | MAJOR | §8 R-11 added (PHP/uPress compat with `/api/v1/health` probe); R-04+R-07 marked moot (no contribute, no 301); R-12 added (CF cache invalidation via `?v=sha`). §9.1 declares `sqlite::memory:` + dialect-aware controllers. §9.2 declares visual diff owner+method+threshold+location. §9.3 declares Lighthouse runner+thresholds. §9.5 ownership matrix. | Verify §8 + §9 each subsection |
| LV-S-5 | B.8 budget not credible | MINOR | §11 B.8 split → B.8a (1.5h visual) + B.8b (1h Lighthouse/smoke/report). Total phases 8→9, hours 14.5→13. | Verify §11 table |

---

## 7. Output Format

Write verdict to:
`_COMMUNICATION/TEAM_190/VERDICT_SFA-S003-P002-WP-UI_L-GATE_S_v1.0.1.md`

(Note bump to `v1.0.1` — Round 2 verdict, not overwriting your R1 verdict.)

Use the **unified verdict template** (7 sections — same as R1):

1. **Verdict Summary** — `PASS` | `PASS_WITH_FINDINGS` | `FAIL` + 2-sentence rationale.
2. **Parameters** — engine + version, time spent, files actually read.
3. **Criteria Table** — VC-1..VC-7 each with result + 1-line rationale.
4. **Findings** — only NEW findings (`LV-S-N` continuing from R1; R1 IDs reserved as resolved). Cite `file:line` (or `file §section`) of LOD400 v1.0.1.
5. **validate_aos.sh** — N/A for spec validation.
6. **Disposition** — `DISPATCH_BUILD` | `AMEND_LOD400_AND_RESUBMIT` | `ESCALATE_TO_TEAM_00`.
7. **Next Step** — single imperative sentence for team_100.

### Constraints

- **Cross-engine (IR#1):** same as R1 — non-Claude required.
- **Continuity:** same engine as R1 preferred (GPT-5.5 / Cursor), but any non-Claude engine is acceptable.
- **Independence:** do NOT consult outside opinions on the amendments before forming verdict.
- **Evidence-based:** every FAIL or new finding must cite `file:line`.
- **Scope discipline:** if R1 findings are all resolved AND no new BLOCKERs surface, the disposition SHOULD be `DISPATCH_BUILD` (a PASS_WITH_FINDINGS verdict is acceptable for MAJOR/MINOR findings; BUILD can proceed if all BLOCKERs are clear).
- **No roadmap mutation:** team_100 is the single writer.
- **Enforcement mode:** STANDARD.

---

*Resubmission mandate generated 2026-05-27 by team_100 per `/AOS_gate-mandate` canon.*
*Awaiting team_190 R2 verdict.*
