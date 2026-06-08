---
id: SFA-S003-P004-WP-CB-CALC-VALREQ
from: team_100 (Chief Architect — builder engine: Claude Opus)
to: team_190 (constitutional/cross-engine validation) + team_50 (visual QA)
re: pre-implementation validation — WP-CB-CALC + WP-CB-CROPDATA-DATES specs + staged increments
gate: L-GATE_D (design validation) before further build (team_00 directive: validate before implementation)
created: 2026-06-07
status: AWAITING cross-engine validation — builder is Claude, so the binding verdict MUST be non-Claude (IR#1/#5)
---

# Validation request — WP-CB-CALC (pre-implementation)

> **Why this is here:** team_00 directed "validate before implementation". Builder engine = **Claude (Opus)**; per IR#1 (builder ≠ validator) and IR#5 (final validation owned by team_190, cross-engine), team_100 **cannot self-issue** the binding verdict. This bundle is prepped for a **non-Claude** engine to validate; Nimrod routes it.

## 1. What to validate
**A. The specs (design, L-GATE_D):**
- `_aos/work_packages/S003/SFA-S003-P004-WP-CB-CALC/LOD400_spec.md` (decision-complete; presentation locked to team_35 mockups; 1 residual = #13 basket iteration).
- `_aos/work_packages/S003/SFA-S003-P004-WP-CB-CROPDATA-DATES/LOD400_spec.md`.
- Design + decisions: `_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-CALC/LOD_DESIGN_2026-06-07_v1.0.0.md`.

**B. Staged increments (branch `claude/cb-followups-2026-06-07`, built ahead — to be validated, not yet merged):**
1. `#2 transplants` ported (JS CALC + goal live; 6→7) — commit f491172.
2. Server plumbing — date numerics whitelist + categorical channel `SFA_CROP_BOOK_TXT` — commit 62b1e9a.
3. Date engine `SFA_DATEC` (#4/#5/#6) — commit 6314a44.

## 2. Evidence (builder-side, deterministic)
- PHP suite **221/221** green (`sfa_delivery` phpunit; SQLite in-memory).
- `validate_aos.sh` **0 FAIL** (30 PASS / 21 SKIP).
- **Date-engine parity cross-checked against the REAL `calculators.py`**: sow 16/06/2026; harvest 15/09→27/10; succession 5×2wk — identical to JS `SFA_DATEC`.
- Route tests seed **RICH** payloads (WP-CB-MOBILE 500 lesson) incl. a graceful-degradation case.

## 3. Constitutional checks requested (team_190)
- **Directory authority:** team_100 wrote only `_COMMUNICATION/team_100|team_35|team_190/`, `_aos/roadmap.yaml`, `_aos/work_packages/`, and application source under `sfa_delivery/`. (Builder role; no `_aos/governance` edits.)
- **IR#4 single-writer roadmap** — roadmap edits are team_100-only, committed defensively.
- **IR#3 spec_ref** — all repo-internal; point at existing files (verified).
- **IR#7 API-only when DB online** — no structured DB mutations performed (DB online); CROPDATA-DATES guided tool is specced to write via the hub API, not direct SQL.
- **Product integrity** — "no fabricated numbers": honest no-data state for missing-data goals; #13 is quantity-first (no "profit"); ₪ is secondary.
- **IR#1 cross-engine** — confirm builder (Claude) ≠ validator (this verdict).

## 4. team_50 (visual QA)
Defer full visual QA until the date-engine UI wiring + typed-result render land (mockups integrated). For now: confirm the mockups (`UI_REDESIGN_2026-06/mockups/calc.html`) match the LOD400 mapping.

## 5. Requested verdict
A cross-engine (non-Claude) L-GATE_D verdict: PASS → team_100 resumes implementation (typed render + B-now goals + #13 basket once team_35 iterates); or CHANGES → team_100 addresses before build. Route via `_COMMUNICATION/team_100/`.
