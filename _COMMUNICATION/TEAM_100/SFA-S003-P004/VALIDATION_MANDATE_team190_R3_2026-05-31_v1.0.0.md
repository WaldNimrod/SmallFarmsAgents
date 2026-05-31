# VALIDATION MANDATE (ROUND 3) — SFA-S003-P004-WP-CB-0 — team_100 → team_190 — v1.0.0

**Date:** 2026-05-31
**From:** team_100 (Claude Opus) · **To:** team_190 · **Routed by:** team_00
**Repo:** `/Users/nimrod/Documents/SmallFarmsAgents` · `main` · HEAD `<this commit>`
**Round:** **3** — confirm the 2 errata from R2. **R2 verdict:** `_COMMUNICATION/team_190/SFA-S003-P004/TARGET_A_CANON_L-GATE_S_R2_VERDICT_v1.0.0.md`

---

## 0. Cross-engine (IR#1/#5)
Non-Claude only (Cursor Composer / GPT-5.x / Codex). Confirm engine in header.

## 1. Why R3 (ultra-narrow)
R2 = PASS_WITH_FINDINGS: F-190-CB0-02 RESOLVED; **F-190-CB0-01 + F-190-CB0-03 INSUFFICIENT** — two live variants weren't enumerated. team_100 applied the errata in **Canon v1.2.0** and ran the exhaustive gate (claims these are the ONLY two). R3 confirms the errata; **nothing else is re-opened.**

## 2. Re-check (exactly two gates)

### Errata A — F-190-CB0-01 — `half-hardy` collapse (§6.3)
Canon v1.2.0 §6.3 now collapses `semi_hardy→half_hardy` **and** `half-hardy→half_hardy`.
```bash
docker exec oma-postgres psql -U oma -d organic_market_agent -tAc \
  "select distinct value_text from crop_variety_source_values where field_name='frost_tolerance_class'"
```
PASS iff **every** returned value (`half-hardy`, `hardy`, `semi_hardy`, `tender`, `very_tender`) maps to a canonical token `{hardy, half_hardy, tender, very_tender}` via the §6.3 collapse.

### Errata B — F-190-CB0-03 — bare `kg` on yield (§6.1)
Canon v1.2.0 §6.1 now maps `kg → kg_per_bed_m` for `avg_yield_per_bed_m`.
```bash
docker exec oma-postgres psql -U oma -d organic_market_agent -tAc \
  "select distinct coalesce(unit,'(NULL)') from crop_variety_source_values where field_name='avg_yield_per_bed_m'"
```
PASS iff every returned unit (`kg`, and any other) has a canonical target in §6.1.

### Optional belt-and-suspenders (team_100 already ran this; reproduce if desired)
Full enum + unit gate — confirm **no other** stranded value exists:
```bash
docker exec oma-postgres psql -U oma -d organic_market_agent -tAc \
  "select coalesce(unit,'(NULL)'),count(*) from crop_variety_source_values group by 1 order by 1"
for f in planting_method frost_tolerance_class storage_ethylene_sensitivity; do echo "== $f =="; \
  docker exec oma-postgres psql -U oma -d organic_market_agent -tAc \
  "select distinct value_text from crop_variety_source_values where field_name='$f'"; done
```

## 3. Verdict → `_COMMUNICATION/team_190/SFA-S003-P004/TARGET_A_CANON_L-GATE_S_R3_VERDICT_v1.0.0.md`
```yaml
target: A (Canon L-GATE_S) — Round 3
validator_engine: <non-Claude>
result: PASS | PASS_WITH_FINDINGS
errata_recheck:
  - id: F-190-CB0-01
    status: RESOLVED | INSUFFICIENT
  - id: F-190-CB0-03
    status: RESOLVED | INSUFFICIENT
other_stranded_variants_found: <none | list>
summary: <one paragraph>
```
- **PASS** (both RESOLVED, no other stranded variants) → **Canon LOCKS** (LOD200_LOCKED); team_100 opens the Migration WP.
- Any INSUFFICIENT / new variant → list it precisely; team_100 fixes + R4.

Notify via `_COMMUNICATION/team_100/` (MSG, ADR043).

---
*Self-contained R3 package. team_00: route to a non-Claude validator.*
