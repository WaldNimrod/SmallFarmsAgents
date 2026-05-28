---
id: ROUTE_TO_TEAM_100_aos_reauthor_SFA-S003-P002-WP-C5_v1.0.0
from: team_10
to: team_100
cc: team_00, team_190
date: 2026-05-28
type: routing_request
wp: SFA-S003-P002-WP-C5 (+ WP-C6, WP-C2 roadmap blocks)
trigger: L-GATE_V R1 BLOCKER F-190-C5-LV-01
authority: team_00 decision 2026-05-28 (route _aos/ re-authorship to team_100)
status: AWAITING_TEAM_100_REAUTHOR
---

# Routing Request — team_100 re-author `_aos/` edits (WP-C5 R1 BLOCKER)

## Why this request exists

team_190's L-GATE_V R1 verdict on WP-C5 Phase A returned **BLOCKED** on a
single governance finding (all 12 functional ACs PASSED):

> **F-190-C5-LV-01 — BLOCKER** — Build commit `1a29c03` (and follow-ups)
> modified `_aos/roadmap.yaml` and `_aos/work_packages/...` while team_10 is
> the builder. Per Directory Authority, `_aos/` write authority is
> team_100 / sfa_arch — not team_10.

team_00 (Principal) had granted team_10 an in-session IR#4 exception to edit
the roadmap, but it was never recorded as a verifiable artifact, and team_00
has now decided (2026-05-28) to **regularize via team_100 re-authorship**
rather than a retroactive ratification.

**team_10 will make no further `_aos/` edits.** This artifact hands team_100
everything needed to re-author the `_aos/` content under proper authority.

## `_aos/` files needing re-authorship

All content is already in the repo (functionally validated by team_190).
team_100 should review + take authorship (re-commit as team_100), optionally
folding in the F-03 fix below.

| File | Change | Introduced in commit |
|------|--------|----------------------|
| `_aos/roadmap.yaml` | WP-C5 block: gate_history L-GATE_S + L-GATE_B PASS, status IN_REVIEW, current_lean_gate L-GATE_V, assigned_validator team_190, build_commit, validation_mandate_ref | `6cae289` |
| `_aos/roadmap.yaml` | WP-C6 block: NEW entry, status PROPOSED, LOD200_LOCKED, depends_on WP-C5 | `1a29c03` |
| `_aos/roadmap.yaml` | WP-C2 block: gate_history L-GATE_B PASS, status IN_REVIEW, current_lean_gate L-GATE_V, assigned_validator team_190 | `d46160c` |
| `_aos/work_packages/S003/SFA-S003-P002-WP-C5/LOD200_spec.md` | v1.1.0 amendment — Phase A (code+data cleanup) added | `1a29c03` |
| `_aos/work_packages/S003/SFA-S003-P002-WP-C6/LOD200_spec.md` | NEW — sparse crops future expansion spec | `1a29c03` |

Exact diffs:
```
git show 1a29c03 -- _aos/
git show 6cae289 -- _aos/
git show d46160c -- _aos/
```

## F-03 (MINOR) fix to fold in during re-author

`_aos/work_packages/S003/SFA-S003-P002-WP-C5/LOD200_spec.md` references a
stale path `python scripts/run_enrichment.py` (file does not exist). Replace
with the real entrypoint:
`organic_market_agent.crop_book.importer.enrichment_runner.run_enrichment(session, dry_run=False)`.
(team_10 already applied the equivalent fix in the DECISION_RECORD artifact.)

## What team_10 has already remediated (no team_100 action needed)

- **F-190-C5-LV-02 (MAJOR, Hebrew in source):** fixed in commit `47c3746`
  (054, 055, source_weights_db.py → English; verbatim Hebrew retained only in
  DECISION_RECORD). Application source only — within team_10 authority.
- **F-190-C5-LV-03 (MINOR) in DECISION_RECORD:** fixed in `47c3746`.

## Requested team_100 deliverables

1. Re-author the 5 `_aos/` changes above under team_100 authority (re-commit,
   folding in the F-03 spec fix), OR ratify-in-place with an explicit
   team_100 authorship commit.
2. File a short confirmation artifact (e.g.
   `_COMMUNICATION/team_100/SFA-S003-P002-WP-C5/AOS_REAUTHOR_CONFIRM_v1.0.0.md`)
   with the re-authored commit hash, so team_190 R2 can verify.
3. Notify team_10 + team_190 so team_10 can request the narrow L-GATE_V R2.

## After re-authorship

team_190 runs a **narrow L-GATE_V R2** focused on F-01 only (functional ACs
already PASSED in R1 and need not be reopened unless the re-author changes
implementation). On R2 PASS → team_10 executes ADR042 3-step closure →
LOD500_LOCKED → WP-C5 Phase B (team_00 manual) opens.

Note: the same `_aos/` authorship issue applies to the **WP-C2** roadmap
block (`d46160c`); please re-author it in the same pass so WP-C2's pending
L-GATE_V is not later blocked on the identical finding.

---

*Routing request by team_10 (Claude Sonnet 4.7) 2026-05-28 per team_00
decision. team_10 holds at WP-C5 R1 remediation-complete (functional + F-02 +
F-03); F-01 awaits team_100.*
