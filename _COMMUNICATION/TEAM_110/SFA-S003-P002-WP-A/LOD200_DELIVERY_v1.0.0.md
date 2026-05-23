---
id: TEAM_110-SFA-S003-P002-WP-A-LOD200-DELIVERY
type: DELIVERY_SUMMARY
from: team_110 (Domain Architect)
to: team_00 (advisory review), team_100 (routing to L-GATE_S)
date: 2026-05-23
spec_path: _aos/work_packages/S003/SFA-S003-P002-WP-A/LOD200_spec.md
status: DELIVERED — awaiting team_00 advisory review
---

# LOD200 Delivery — SFA-S003-P002-WP-A: Data Enrichment Architecture

## What was delivered

`_aos/work_packages/S003/SFA-S003-P002-WP-A/LOD200_spec.md` — Phase 1 architecture
design document for the Data Enrichment work package.

## Summary of architectural decisions made

| Decision | Choice |
|----------|--------|
| Source taxonomy | 5 classes: EX (Expert) > PR (Prescriptive) > OP (Operational) > MK (Market) > WB (Web) |
| Schema delta | Option C hybrid: migration 041 (new crop_field_enrichment table, no GCR) + migration 042 (extend source_values with trust_tier/confidence_weight, GCR_1 required) |
| Reconciler | Pluggable source registry + field policy table + two blend strategies (weighted_mean / hard_winner) |
| Range fields | min/max/best_estimate in crop_field_enrichment table (not extending crop_varieties directly) |
| Validation harness | Shadow-run calibration script against team_00 EX overrides (scripts/validate_enrichment.py) |
| UI — WP-A scope | New enrichment JSON artifact (no locked files) + Flask API route (new file) |
| UI — WP-B scope | Full Flask template confidence indicators (GCR_2 for views.py) + inline data.json (GCR_3 for publisher/) |
| OMA market price | Deferred to WP-B |
| Web sources | Deferred to WP-B (team_00 to specify scope) |

## Open questions requiring team_00 decisions (§12 of spec)

Q1 — Weighted-mean blend vs simpler hard_winner? (default: weighted_mean)
Q2 — Surface range (min/max) in UI? (default: yes)
Q3 — OMA integration in WP-A or WP-B? (default: WP-B)
Q4 — Which web sources? (default: defer, team_00 specifies)
Q5 — Confidence score in public SPA? (default: yes)
Q6 — Pre-authorize GCR_1 (models.py) here? (default: prefer yes — unblocks build)
Q7 — WP-A + WP-B split vs single WP? (default: two WPs)

## Effort summary

- WP-A (data layer): LARGE (~16–20h builder)
- WP-B (UI + source expansion): LARGE (~14–18h builder)

## Key constraints flagged

1. **GCR_1 (models.py)**: Adding columns to `CropVarietySourceValue` requires a formal
   GCR + team_100 mandate before the LOD400 build can start on migration 042.
   Pre-authorization via team_00 advisory is preferred to unblock the builder.

2. **GCR_2 (views.py) + GCR_3 (publisher/)**: Deferred to WP-B. WP-A delivers
   enrichment without touching locked files.

## Done criteria for this session (per onboarding mandate)

- [x] LOD200 authored at _aos/work_packages/S003/SFA-S003-P002-WP-A/LOD200_spec.md
- [ ] team_00 advisory review + iteration to acceptance
- [ ] LOD200_LOCKED ACK → hand back to team_100

## team_100 action after LOD200_LOCKED

1. Add SFA-S003-P002-WP-A entry to `_aos/roadmap.yaml` (team_100 is single writer)
2. Package LOD200 into L-GATE_S bundle for team_190
3. Issue GCR_1 if Q6 pre-authorization granted by team_00
4. Author LOD400 spec (or re-activate team_110 for LOD400)

---

*Delivered 2026-05-23 by team_110. Spec at: _aos/work_packages/S003/SFA-S003-P002-WP-A/LOD200_spec.md*
