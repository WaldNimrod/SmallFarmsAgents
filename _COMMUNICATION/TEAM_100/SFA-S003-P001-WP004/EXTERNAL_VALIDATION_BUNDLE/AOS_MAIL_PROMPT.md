# Agent Onboarding — team_190 / smallfarmsagents — SFA-S003-P001-WP004 LOD400 Spec Review

*Generated 2026-05-09 · team_100 (Sonnet 4.6 declared / Opus 4.7 actual) · Gate: L-GATE_SPEC · Round 1*

## Activation TL;DR
- **Identity:** team_190 · role: Senior Constitutional Validator
- **Engine:** external / non-Claude (Iron Rule #1 — cross-engine mandate)
- **Domain:** smallfarmsagents · profile: L0
- **Assignment:** L-GATE_SPEC external review — **SFA-S003-P001-WP004** (ספר גידולים — WordPress integration, single WP)
- **Gate:** L-GATE_SPEC (pre-implementation constitutional spec review)
- **Round:** 1
- **Writes to:** `_COMMUNICATION/team_190/`
- **First reads:** `CLAUDE.md` · `_aos/governance/team_190.md` · `_aos/roadmap.yaml`
- **Worktree:** `/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/strange-mcnulty-651551`
- **Branch:** `claude/strange-mcnulty-651551`

## Infrastructure Note — DB ONLINE this session

| Service | Status | Action |
|---------|--------|--------|
| DB `127.0.0.1:5432` | ONLINE (PostgreSQL 16.13, alembic head=040) | Read-only access acceptable; not required for spec review |
| AOS API `127.0.0.1:8090` | Hub-side; not required for L-GATE_SPEC | — |

**Spec review is document-driven** — no code execution required to issue an L-GATE_SPEC verdict.

---

## Assignment

You are performing **L-GATE_SPEC Round 1** external constitutional review for **SFA-S003-P001-WP004** — the WordPress integration phase of the ספר גידולים (Crop Book) module.

**Context:** S003 Phase 1 (WP002 + WP003) closed 2026-05-08, both LOD500_LOCKED. Your prior verdicts on those WPs:
- `_COMMUNICATION/team_190/SFA-S003-P001-WP002-LGATEV-VERDICT_v1.0.0.md`
- `_COMMUNICATION/team_190/SFA-S003-P001-WP003-PATCH01-VERDICT_v1.0.0.md`

**WP004 scope:** delivers the public-facing crop book to `https://www.nimrod.bio` via a new shortcode `[sfagent_crop_book]`. Mirrors the existing `[sfagent_market_report]` pipeline. Does not modify the LOD500_LOCKED Phase 1 work.

This is a **pre-implementation spec review** — no code has been written. Your verdict determines whether sfa_build (team_10) may proceed. A BLOCKED verdict stops all downstream work.

---

## Read order (mandatory — read ALL before issuing verdict)

### Step 1 — AOS context
1. `CLAUDE.md` — Iron Rules, directory authority, AOS spoke rules
2. `_aos/governance/team_190.md` — your role and authority scope
3. `_aos/roadmap.yaml` — confirm WP004 is registered (`status: ELIGIBLE`)

### Step 2 — Locked dependency context (LOD500_LOCKED — not under review)
4. `_aos/work_packages/S003/SFA-S003-P001-WP002/LOD400_spec.md` (DB + seed)
5. `_aos/work_packages/S003/SFA-S003-P001-WP003/LOD400_spec.md` (Flask views — semantic SSoT for filter parity)

### Step 3 — Bundle (constitutional checklist C1–C12 + risk register + verdict format)
6. `_COMMUNICATION/TEAM_100/SFA-S003-P001-WP004/EXTERNAL_VALIDATION_BUNDLE/MANIFEST.md`

### Step 4 — PRIMARY REVIEW TARGET
7. `_aos/work_packages/S003/SFA-S003-P001-WP004/LOD400_spec.md`

### Step 5 — Operational + reference reads (only if a finding hinges on them)
8. `documentation/05-admin-and-operations/UPRESS_WP_REST_API_PUBLISH_RUNBOOK.md`
9. `organic_market_agent/publisher/engine.py` (reference impl)
10. `organic_market_agent/publisher/wp_upload.py` (extension target)
11. `organic_market_agent/publisher/upload_dispatch.py` (extension target — `profile` kwarg)
12. `organic_market_agent/crop_book/views.py` (filter logic SSoT, lines 234–304)

---

## What to validate

Run the **12 constitutional checks** from `MANIFEST.md §3` (C1–C12) against the WP004 spec. Findings beyond C1–C12 are also in scope.

Additionally verify (from `MANIFEST.md §3` "Additional L-GATE_SPEC criteria"):
- The data-URL substitution mechanism (spec §5.3 + R-WP004-06) — robustness of literal-string sentinel
- The entity-registry regex extraction (spec §4 last paragraph + R-WP004-04) — failure-mode specification
- The 12-case filter parity matrix (spec §11.1) — does it actually exercise all four dimensions (q, category, season[], dtm_max) in combination?
- Bundle size measurement step (R-WP004-02) — is the L-GATE_B measurement requirement explicit?

---

## Verdict destination

Write your verdict file to:
```
_COMMUNICATION/team_190/SFA-S003-P001-WP004/LOD400-VERDICT_v1.0.0.md
```

Follow the verdict format from `MANIFEST.md §5`. Sign the verdict as team_190 with date.

Open chat response with the §0 verdict box (mandatory):
```
╔══════════════════════════════════════════════════════════════╗
║  VERDICT: [PASS / PASS_WITH_FINDINGS / BLOCKED]              ║
║  WP: SFA-S003-P001-WP004   Gate: L-GATE_SPEC                ║
║  Round: 1                                                     ║
║  Next step: [one line]                                        ║
╚══════════════════════════════════════════════════════════════╝
```

Commit message:
```bash
git commit -m "validate(SFA-S003-P001-WP004/L-GATE_SPEC): {VERDICT} — Team 190"
```

---

## ADVERSARIAL requirement

Per your governance contract: you must NOT be aware of team_100's conclusions before forming your own verdict. Read the spec independently. The MANIFEST.md constitutional checklist is a structural aid — it does not constrain your finding scope. If you identify concerns NOT in the checklist, include them as additional findings under `§2 Additional findings`.

---

## Done criteria

1. §0 verdict box shown in chat
2. Verdict artifact at `_COMMUNICATION/team_190/SFA-S003-P001-WP004/LOD400-VERDICT_v1.0.0.md`
3. Artifact committed (commit message above)
4. Confirmation message posted to `_COMMUNICATION/TEAM_100/` as `MSG-team190-to-team100-S003-WP004-LOD400-VERDICT-[DATE].md`

---

*Activation prompt v1.0.0 — prepared 2026-05-09 by team_100.*
*Worktree: `strange-mcnulty-651551` · Branch: `claude/strange-mcnulty-651551` · Bundle commit: `38208ee`*
