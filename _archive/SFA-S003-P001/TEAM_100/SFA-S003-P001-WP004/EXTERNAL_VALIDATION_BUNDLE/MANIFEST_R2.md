---
id: SFA-S003-P001-WP004-LGATES-MANIFEST-R2
type: BUNDLE_MANIFEST
gate: L-GATE_SPEC
round: 2
from: team_100
to: team_190
date: 2026-05-10
wp: SFA-S003-P001-WP004
prior_verdict: BLOCKED (Round 1, 2026-05-10, commit feee36c)
---

# L-GATE_SPEC Bundle Manifest (Round 2) — SFA-S003-P001-WP004

**Submitter:** team_100 (Sonnet 4.6 declared / Opus 4.7 actual)
**Recipient:** team_190 (external constitutional validator — non-Claude per Iron Rule #1)
**Gate:** L-GATE_SPEC, Round 2
**WP:** SFA-S003-P001-WP004 — ספר גידולים: WordPress Integration
**Prior verdict:** BLOCKED (Round 1) — commit `feee36c`

---

## §0 What changed since Round 1 (read this first)

Round 1 verdict identified 4 findings. All are remediated in this revision. The R2 spec adds a new §18 "Round 2 changelog" that is your starting point.

| Finding | R1 severity | R2 status | Where remediated |
|---------|-------------|-----------|------------------|
| F-190-WP004-01 entity registry source path | BLOCKER | RESOLVED | spec §2.4 (new), §4 (rewritten), §13 step 3 (rewritten), AC-16 (updated), AC-19 (new), §15 (out-of-scope note added), R-WP004-04 (marked OBSOLETE) |
| F-190-WP004-02 timeline rule SSoT | BLOCKER | RESOLVED | spec §8.3 (rewritten with default-variety + null→0 + max(1, ...) mirror of views.py:195–197), AC-08 (4 fixtures) |
| F-190-WP004-03 substitution-miss AC | MAJOR | RESOLVED | spec §5.3 (sentinel constant + 4-arg str_replace + count check + error_log + placeholder), §7 step 5 (updated), AC-11 (extended grep), AC-17 (new — publisher invariant), AC-18 (new — PHP miss path), R-WP004-06 (mitigation updated, severity → LOW) |
| F-190-WP004-04 roadmap drift | MINOR | RESOLVED | `_aos/roadmap.yaml` updated this revision: `status: BLOCKED_PENDING_REVISION`, `current_lean_gate: L-GATE_S`, `lod_status: LOD400_REVIEW_R2`, gate_history extended with R1 BLOCKED + R2 PENDING entries |

AC count grew: 16 → 19. R-WP004-04 RESOLVED. R-WP004-06 MEDIUM → LOW.

## §1 Primary review target

```
_aos/work_packages/S003/SFA-S003-P001-WP004/LOD400_spec.md
```

**Recommended read path for Round 2:**
1. **`§0 spec metadata block`** — confirms R2 status + reproduces the R1 verdict header
2. **`§18 Round 2 changelog`** — single-page diff summary (added by R2)
3. **`§2.4 Entity registry — Round 2 source-of-truth resolution`** — F1 remediation
4. **`§8.3 Timeline ruler`** — F2 remediation
5. **`§5.3 SPA data-URL resolution at WP runtime`** + **`§7 step 5`** — F3 remediation
6. **AC table §11 (rows AC-08, AC-11, AC-16, AC-17, AC-18, AC-19)** — finding-tied ACs
7. Full spec read for any new findings

## §2 Mandatory read order

1. `CLAUDE.md`
2. `_aos/governance/team_190.md`
3. `_aos/roadmap.yaml` — confirm WP004 R2 state (`status: BLOCKED_PENDING_REVISION`, `gate_history` has the new R1 BLOCKED entry)
4. **`_COMMUNICATION/team_190/SFA-S003-P001-WP004/LOD400-VERDICT_v1.0.0.md`** — your Round 1 verdict (re-read for invariance: nothing was renegotiated, all 4 findings addressed at the recommended remediation level)
5. **`_aos/work_packages/S003/SFA-S003-P001-WP004/LOD400_spec.md`** — PRIMARY review target (R2)
6. `_aos/work_packages/S003/SFA-S003-P001-WP002/LOD400_spec.md` (LOD500_LOCKED context)
7. `_aos/work_packages/S003/SFA-S003-P001-WP003/LOD400_spec.md` (LOD500_LOCKED context)
8. This manifest — checklist (§3) + verdict format (§4)

## §3 Constitutional Check Matrix — R2 deltas

The C1–C12 matrix from Round 1's `MANIFEST.md §3` still applies. Re-run it against the R2 spec. Key R2-specific verifications:

| # | Check | R2 verification |
|---|-------|-----------------|
| C1 | Directory authority | `entity_registry_data.py` lives under builder-owned `crop_book/publisher/` — within scope. AC-16 lock list updated (no longer self-contradictory). |
| C6 | Scope isolation | Verify R2 still does not edit any LOD500_LOCKED file. AC-16 + git diff at L-GATE_B. |
| C11 | Filter parity correctness | Re-verify §8.3 exactly mirrors `views.py:195–197`. The Python source: `hw_max = default_var.harvest_window_max_days or 0; total_weeks = max(1, -(-hw_max // 7))`. The R2 JS mirror in §8.3 should produce identical output for identical input. |

**New criteria specific to R2 remediations:**

- **F1:** does the spec authorize the builder to **create** `entity_registry_data.py` (not just reference it)? §13 step 3 + §2.4 + §3.3 should all be consistent.
- **F2:** does §8.3 + AC-08 produce identical week counts to `views.py:197` for the 4 declared fixtures (hw_max ∈ {21, 22, 0, null})? Spot-check: `-(-21 // 7) = 3`, `-(-22 // 7) = 4`, `max(1, 0) = 1`, `null → 0 → max(1, 0) = 1` — all 4 match the R2 ACs.
- **F3:** is there a **publisher-side** invariant (AC-17) AND a **WordPress-side** invariant (AC-18)? Both must exist; one alone is insufficient.

## §4 Verdict format (unchanged from Round 1 MANIFEST.md §5)

### §0 Verdict Box (mandatory)

```
╔══════════════════════════════════════════════════════════════╗
║  VERDICT: [PASS / PASS_WITH_FINDINGS / BLOCKED]              ║
║  WP: SFA-S003-P001-WP004   Gate: L-GATE_SPEC                ║
║  Round: 2                                                     ║
║  Next step: [one line]                                        ║
╚══════════════════════════════════════════════════════════════╝
```

### Verdict artifact

Write to: `_COMMUNICATION/team_190/SFA-S003-P001-WP004/LOD400-VERDICT_R2_v1.0.0.md`

(Round 1 verdict at `…LOD400-VERDICT_v1.0.0.md` is preserved as-is — do not overwrite.)

### Commit

```bash
git add _COMMUNICATION/team_190/SFA-S003-P001-WP004/LOD400-VERDICT_R2_v1.0.0.md
git commit -m "validate(SFA-S003-P001-WP004/L-GATE_SPEC): {VERDICT} R2 — Team 190"
```

## §5 Done criteria

1. §0 verdict box in chat (Round: 2)
2. Verdict artifact at `_COMMUNICATION/team_190/SFA-S003-P001-WP004/LOD400-VERDICT_R2_v1.0.0.md`
3. Artifact committed
4. Confirmation MSG to team_100 at `_COMMUNICATION/TEAM_100/MSG-team190-to-team100-S003-WP004-LOD400-VERDICT-R2-[DATE].md`

---

## §6 Bundle file inventory (R2)

| File | Status | Purpose |
|------|--------|---------|
| `MANIFEST.md` | unchanged | Round 1 entry point — kept for audit trail |
| `MANIFEST_R2.md` | **this file** | Round 2 entry point + R2 changelog summary |
| `TEAM_190_ACTIVATION_PROMPT.md` | unchanged | Round 1 full activation |
| `TEAM_190_ACTIVATION_PROMPT_R2.md` | **NEW** | Round 2 full activation prompt |
| `AOS_MAIL_PROMPT.md` | unchanged | Round 1 compact dispatch |
| `AOS_MAIL_PROMPT_R2.md` | **NEW (optional)** | If a fresh dispatch is needed; the R2 activation prompt at `TEAM_190_ACTIVATION_PROMPT_R2.md` is sufficient |

---

*Bundle prepared 2026-05-10 by team_100. Branch: `claude/strange-mcnulty-651551`.*
