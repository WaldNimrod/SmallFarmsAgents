---
id: MANDATE_SFA-S003-P002-WP-B3_L-GATE_B_v1.0.0
from: team_110 (AOS Domain Architect — ADR045 execution_authority: full)
to: team_10 (sfa_build — Builder — separate session per IR#1)
date: 2026-05-25
type: GATE_MANDATE
gate: L-GATE_B
wp: SFA-S003-P002-WP-B3
project: smallfarmsagents
status: ACTIVE
verdict: PENDING
engine_constraint: "Iron Rule #1 — builder engine MUST differ from team_190 (GPT-5.5). Recommended: Claude Code (Sonnet) in a SEPARATE session from team_110 (Claude Opus 4.7)."
authorization_basis: "ADR045 R2 #2 — same EXECUTION_MANDATE as B1 / patch01 / B2."
spec_ref: _aos/work_packages/S003/SFA-S003-P002-WP-B3/LOD400_spec.md
spec_version: v1.0.1
spec_lock_commit: "TBD"   # the LOD400_LOCKED commit (this commit + the v1.0.1 cleanup); team_10 will reference at build time
parent_wp_b1_lod500_commit: "6a85561"
parent_wp_b1_patch01_lod500_commit: "3e1f946"
lgate_s_verdict_ref: _COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B3/LOD400-VERDICT_v1.0.0.md
team_00_decision_ref: _COMMUNICATION/team_00/DECISION_SFA-S003-P002-WP-B3-WHITELIST_2026-05-25_v1.0.0.md
sequencing_constraint: "B3 migration 046 has down_revision='045' — B2 migration 045 MUST be committed before B3 builder runs `alembic upgrade 046`. Builder STOPs at Step 4 if 045 missing (per spec §11 + R-07). Recommended: team_110 holds the spawn of B3 builder until B2 LOD500_LOCKS."
---

# L-GATE_B Mandate — SFA-S003-P002-WP-B3

**ספר גידולים: Tend Israel Adaptation Overlay**
**Track:** A | **Profile:** L0 | **Effort:** MEDIUM | **Risk:** MEDIUM (GCR-authorized LOD500_LOCKED extension)

---

## 1. Gate History

| Gate | Result | Validator |
|------|--------|-----------|
| L-GATE_E | PASS | team_00 |
| L-GATE_S R1 | **PASS_WITH_FINDINGS** | team_190 (GPT-5.5) — 0 BLOCKER / 0 MAJOR / 2 MINOR (F1 closed in v1.0.1 cleanup; F2 carry — lean-kit profile drift) |
| L-GATE_B | (this mandate ↓) | team_10 |

Spec is now LOD400_LOCKED at v1.0.1.

---

## 2. Scope

Implement LOD400 v1.0.1 per the 10-step build sequence at §11. MEDIUM effort:
- Migration 046 (new `crop_harvest_stats` table + ALTER `crop_task_templates` CHECK constraint)
- ORM module `crop_harvest_stats.py`
- GCR-B3-1: append 6 entries to `TASK_TYPE_VALUES` in `crop_task_templates.py` (team_00 pre-authorized via DECISION file)
- New importer `tend_overlay.py` (3 parsers + orchestrator + upsert helpers)
- `constants.py` additions: `TEND_TASK_WHITELIST` (11 entries) + `TEND_TASK_BLACKLIST` (10 entries) + `TEND_TASK_TYPE_MAP` (9 entries + Method-disambiguated)
- `seed.py` CLI: 4 new flags
- ≥ 20 new tests

**Critical sequencing:** Migration 046 `down_revision = "045"` (B2's migration). **Before running `alembic upgrade 046`, verify B2 migration 045 is committed** (`ls organic_market_agent/db/versions/045_*.py`). If missing, **STOP and file inquiry** to team_110 — do NOT improvise. team_110 will hold spawning the B3 builder sub-agent until B2 LOD500_LOCKS, but if mandate is read live anyway, this is the safety net.

---

## 3. Acceptance Criteria

Spec §9 (LOD400 v1.0.1) defines 20 ACs. Critical:

- **AC-01a/b** — Migration 046 upgrade + downgrade on both Postgres and SQLite (SQLite uses `batch_alter_table(recreate="always")` for the ALTER CHECK)
- **AC-03** — `TASK_TYPE_VALUES` extended to 20 entries (GCR-B3-1 scope)
- **AC-09** — HARVESTS aggregation NEVER per-record (≤ crops × 4 seasons × 1 year)
- **AC-11** — CHECK regression: B1 baseline values still accepted post-migration
- **AC-13** — Trellis + Fertilize (Option-B additions) actually flow through
- **AC-17** — Zero regression on prior tests (56 patch01 + 56 B1 still PASS)
- **AC-19** — No LOD500_LOCKED touches beyond GCR-B3-1 scope

---

## 4. LOD500_LOCKED files (DO NOT modify beyond GCR-B3-1)

See spec §14 for the full list. The ONLY permitted exception is `crop_task_templates.py` — append exactly 6 entries to `TASK_TYPE_VALUES` tuple (no other change).

Permitted additive modifications (the 4 existing files):
- `organic_market_agent/crop_book/constants.py` (append TEND_TASK_* dicts)
- `organic_market_agent/crop_book/crop_task_templates.py` (GCR-B3-1 — single tuple extension)
- `organic_market_agent/crop_book/importer/seed.py` (4 CLI flags + 1 call-site block)
- `CHANGELOG.md`

---

## 5. Required Files to Read FIRST

1. This mandate
2. Spec v1.0.1: `_aos/work_packages/S003/SFA-S003-P002-WP-B3/LOD400_spec.md`
3. L-GATE_S verdict (2 MINOR carries — F2 will appear in your AC-18 validate_aos.sh output as 28 PASS / 20 SKIP; this is expected — NOT a regression): `_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B3/LOD400-VERDICT_v1.0.0.md`
4. team_00 DECISION (whitelist + GCR-B3-1 authorization): `_COMMUNICATION/team_00/DECISION_SFA-S003-P002-WP-B3-WHITELIST_2026-05-25_v1.0.0.md`
5. Parent WP-B1 LOD400 (LOD500_LOCKED — read-only reference for crop_task_templates schema): `_aos/work_packages/S003/SFA-S003-P002-WP-B1/LOD400_spec.md`

---

## 6. Iron Rule constraints

- **IR#1** — Sonnet ≠ GPT-5.5 (team_190) ≠ Opus 4.7 (team_110)
- **IR#4** — Do NOT touch `_aos/roadmap.yaml`
- **IR#5** — L-GATE_V is team_190's
- **IR#6** — BUILD_REPORT in `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B3/`
- **IR#11** — Never touch `_aos/governance/`, `_aos/lean-kit/`

---

## 7. Commit policy

Separate commits per build step (Steps 2-10 per spec §11). Prefix: `build(WP-B3/...):`. After each commit, run `validate_aos.sh` and confirm `0 FAIL` (PASS/SKIP totals may be 28/20 or 29/18 depending on lean-kit profile — F2 carry).

End every commit message with:
```
Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

---

## 8. Output — BUILD_REPORT

Write to: `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B3/BUILD_REPORT_v1.0.0.md` per the canonical 8-section pattern (verdict, per-AC table, pytest tail, validate_aos.sh tail, LOD500_LOCKED audit, files touched, runtime stats from import on live Tend_2022/ CSVs, open items).

Final agent response to team_110: ≤200 words, including commit hash range, test counts, BUILD_REPORT path, any inquiries filed.

---

## 9. Authorization basis

ADR045 R2 #2. Mandate root `_COMMUNICATION/TEAM_110/SFA-S003-P002-WP-B/EXECUTION_MANDATE_v1.0.0.md`. GCR-B3-1 pre-authorized via team_00 DECISION. team_100 NOT in routing chain.

---

*Mandate issued 2026-05-25 by team_110 (Claude Opus 4.7).*
*Spawn note: team_110 holds spawning the B3 builder sub-agent until B2 R2 PASS (sequencing safety per §2). Mandate filed now for audit-trail completeness; actual sub-agent invocation deferred.*
