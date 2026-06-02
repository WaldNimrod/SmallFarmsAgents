---
id: ARCHIVE_MANIFEST_SFA-S003-P004-WP-CB-DATA
wp: SFA-S003-P004-WP-CB-DATA
status: DONE
lod_status: LOD500_LOCKED
closed_at: "2026-06-03"
archived_at: "2026-06-03"
archived_by: team_191
mandate_ref: "_COMMUNICATION/team_191/MANDATE_SFA-S003-P004-CLOSURE-ARCHIVE_2026-06-03_v1.0.0.md"
roadmap_entry: "_aos/roadmap.yaml → id: SFA-S003-P004-WP-CB-DATA"
archive_root: "_archive/SFA-S003-P004-WP-CB-DATA/"
---

# Archive Manifest — SFA-S003-P004-WP-CB-DATA

**WP:** ספר גידולים: Enrichment Mirror — populate `crop_field_enrichment` + `crop_attribute` on the uPress MySQL delivery tier
**Final status:** DONE / LOD500_LOCKED
**Live URL:** https://sfa.nimrod.bio (migrations 004/005 applied; 1010 rows live)
**Branch:** `claude/sfa-p004-cbdata-classb-2026-06-02`

---

## Gate Ladder

| Gate | Result | Date | Validator | Notes |
|------|--------|------|-----------|-------|
| L-GATE_E | PASS | 2026-06-02 | team_00 | Full scope authorized: mirror both tables to uPress MySQL delivery tier |
| L-GATE_S (routed) | ROUTED | 2026-06-02 | team_190 | LOD400 v0.1.0 DRAFT authored by team_100; routed to team_190 for validation |
| L-GATE_S | PASS_WITH_FINDINGS | 2026-06-03 | team_190 (Cursor/GPT) | Constitutional 5/5, precision 6/6, scope 3/3; 2 INFO addressed inline (LOD400 v0.2.0); authorize_build: true |
| L-GATE_B | PASS | 2026-06-03 | team_100 (verify), team_10 (build) | MySQL migrations 004/005; IngestController whitelist; sfa_ingest_push enrichment/attribute fetchers; 750 pytest pass / 2 pre-existing; 141 composer; validate_aos 29/19/0 |
| QA | PASS | 2026-06-03 | team_50 | All 12 ACs PASS; 28 pytest + 6 PHPUnit pass |
| DEPLOY (routed) | ROUTED | 2026-06-03 | team_99 | Mandate pre-staged; SSH auth-gated to team_00/team_99 |
| L-GATE_V R1 | FAIL | 2026-06-03 | team_190 (Cursor/GPT) | Deploy-precondition FAIL — no DEPLOY_REPORT; tables not applied; NOT a build defect |
| DEPLOY (blocked) | BLOCKED | 2026-06-03 | team_99 | `ADMIN_MIGRATE_TOKEN` unset on uPress; 401 from `/admin/migrate` |
| DEPLOY | SUCCESS | 2026-06-03 | team_99 | Autonomous procedure: FTPS backup .env, self-generated token, `/admin/migrate` 004+005, Mac push 1010 rows / 0 errors; deployed_sha c51c2e5 |
| L-GATE_V R2 | PASS_WITH_FINDINGS | 2026-06-03 | team_190 (Cursor/GPT) | Live 3/3 + code 3/3; 1 INFO non-blocking (C3 no-default spot-check N/A); LOD500_LOCKED |

---

## Verdict References

| Gate | Verdict File | Result |
|------|-------------|--------|
| L-GATE_S | `_COMMUNICATION/TEAM_190/SFA-S003-P004/WP-CB-DATA/WP-CB-DATA_LGATE-S_VERDICT_v1.0.0.md` | PASS_WITH_FINDINGS |
| L-GATE_V R1 | `_COMMUNICATION/TEAM_190/SFA-S003-P004/WP-CB-DATA/WP-CB-DATA_LGATE-V_VERDICT_v1.0.0.md` | FAIL (deploy-precondition) |
| L-GATE_V R2 | `_COMMUNICATION/TEAM_190/SFA-S003-P004/WP-CB-DATA/WP-CB-DATA_LGATE-V_VERDICT_R2_v1.0.0.md` | **PASS_WITH_FINDINGS** (closing verdict) |

Note: All three verdict files remain in-place at `_COMMUNICATION/TEAM_190/SFA-S003-P004/WP-CB-DATA/` (cross-referenced, not moved — team_190 owns that dir structure).

---

## Deploy Report Reference

`_archive/SFA-S003-P004-WP-CB-DATA/team_99/SFA-S003-P004-WP-CB-DATA/DEPLOY_REPORT_v1.0.0.md`
- Status: SUCCESS
- deployed_sha: `c51c2e5` (short) / `c51c2e57bb70698bbf2ff5f179188bb94951f6c0` (full, from L-GATE_V R2 verdict)
- branch_head at L-GATE_V R2: `5ead7e1c2138f96284f246e57d0bda61e1f91be1`
- migrations_applied: `["004_crop_field_enrichment", "005_crop_attribute"]`
- rows_pushed_total: 1010 (crop_field_enrichment=767, crop_attribute=243)

---

## Key Commit SHAs

| Commit | Description | Source |
|--------|-------------|--------|
| `c51c2e5` | Deployed SHA (coupled FTPS mirror with WP-CB-UI-CLASSB; live on sfa.nimrod.bio) | DEPLOY_REPORT + L-GATE_V R2 verdict |
| `5ead7e1c2138f96284f246e57d0bda61e1f91be1` | Branch head at L-GATE_V R2 validation | L-GATE_V R2 verdict frontmatter |

Note: No dedicated builder commit SHA was recorded for WP-CB-DATA in the roadmap (build was done under the same branch as WP-CB-UI-CLASSB in a single coupled build session). The roadmap L-GATE_B notes do not cite a specific commit SHA for this WP's build; `c51c2e5` is the deployed tip that carried all changes.

---

## Data Summary

| Table | Rows Pushed | Source |
|-------|-------------|--------|
| `crop_field_enrichment` | 767 | oma-postgres → HMAC ingest push |
| `crop_attribute` | 243 | oma-postgres → HMAC ingest push |
| **Total** | **1010** | 0 rejected, 0 errors |

Migrations applied via `/admin/migrate?token=<REDACTED>` (HTTP 200, errors:[]).
Token (`ADMIN_MIGRATE_TOKEN`) left in uPress `.env` per team_00 RESPONSE §6. team_00 may rotate at will.

---

## Files Moved (source → archive destination)

### TEAM_10
- `_COMMUNICATION/TEAM_10/SFA-S003-P004-WP-CB-DATA/` → `_archive/SFA-S003-P004-WP-CB-DATA/TEAM_10/SFA-S003-P004-WP-CB-DATA/`
  - `BUILD_REPORT_v1.0.0.md`

### TEAM_50
- `_COMMUNICATION/TEAM_50/SFA-S003-P004-WP-CB-DATA/` → `_archive/SFA-S003-P004-WP-CB-DATA/TEAM_50/SFA-S003-P004-WP-CB-DATA/`
  - `QA_REPORT_v1.0.0.md`

### team_99
- `_COMMUNICATION/team_99/SFA-S003-P004-WP-CB-DATA/` → `_archive/SFA-S003-P004-WP-CB-DATA/team_99/SFA-S003-P004-WP-CB-DATA/`
  - `DEPLOY_REPORT_v1.0.0.md`

### TEAM_100
- `_COMMUNICATION/TEAM_100/SFA-S003-P004-WP-CB-DATA/` → `_archive/SFA-S003-P004-WP-CB-DATA/TEAM_100/SFA-S003-P004-WP-CB-DATA/`
  - `DEPLOY_MANDATE_team99_2026-06-03_v1.0.0.md`
  - `DISPATCH_sfa_build_2026-06-03_v1.0.0.md`
  - `VALIDATION_MANDATE_team190_LGATE-S_2026-06-02_v1.0.0.md`
  - `VALIDATION_MANDATE_team190_LGATE-V_2026-06-03_v1.0.0.md`

---

## Left In Place (intentionally not moved)

| Path | Reason |
|------|--------|
| `_COMMUNICATION/TEAM_190/SFA-S003-P004/WP-CB-DATA/` (3 verdict files) | team_190 verdict dir — cross-referenced, mandate says leave originals; do not delete verdicts |
| `_COMMUNICATION/TEAM_190/MSG-team100-to-team190-SFA-S003-P004-WP-CB-DATA-LGATE-S-2026-06-02.md` | Loose MSG in shared TEAM_190 dir, not a per-WP subfolder |
| `_COMMUNICATION/TEAM_100/MSG-team190-to-team100-WP-CB-DATA-LGATE-S-VERDICT-2026-06-03.md` | Loose MSG in shared TEAM_100 dir |
| `_COMMUNICATION/TEAM_100/MSG-team190-to-team100-WP-CB-DATA-LGATE-V-VERDICT-2026-06-03.md` | Loose MSG in shared TEAM_100 dir |
| `_COMMUNICATION/TEAM_100/MSG-team190-to-team100-WP-CB-DATA-LGATE-V-R2-VERDICT-2026-06-03.md` | Loose MSG in shared TEAM_100 dir |
| `_COMMUNICATION/TEAM_100/HANDOFF_SELF_100_WP-CB-DATA+CLASSB_PARALLEL_2026-06-02_v1.md` | Spans BOTH WPs (CB-DATA + CLASSB); belongs to neither exclusively; left in shared TEAM_100 dir |
| `_COMMUNICATION/team_99/MSG-HUB-20260603-001-RESPONSE.md` | team_99 shared dir MSG (autonomous procedure authorization response) — not a per-WP subfolder |
| `_COMMUNICATION/team_191/` | team_191's own mandate directory — never touched |
| `_COMMUNICATION/team_00/` | Principal inbox — never touched |

---

## Branch Reconciliation (from docs — not git-verified)

Per mandate note and roadmap entries: `main` and `origin/claude/sfa-p004-cbdata-classb-2026-06-02` converged through the S003-P004 program via the messaging helper and team_99 deploy commits. Both WP-CB-UI-CLASSB and WP-CB-DATA share the same branch and `c51c2e5` deployed SHA (single coupled FTPS mirror). The roadmap records `closed_at: 2026-06-03` for this WP. Branch cleanup (merge → main or deletion) is a separate action outside this archive mandate.

---

## Open INFO Follow-ups (non-blocking — log only)

1. **C3 no-default crop spot-check N/A:** Canonical Postgres has `no_default_count=0` (all 66 crops have an `is_default` variety), so the `is_default → first-by-name` fallback path was attested only by code + AC-04 tests, not live verified. Non-blocking; the rule is correctly coded and tested (F-190-CBDATA-V-R2-01).
2. **ADMIN_MIGRATE_TOKEN rotation:** Token is set in uPress `.env`; team_00 may rotate at will per DEPLOY_REPORT §6.
3. **Pre-existing pytest failures:** `test_ac21b_publisher_dir_clean` and `test_uc_prefix_requires_moderation` — both pre-existing from before WP-CB-DATA; unchanged from L-GATE_B baseline. Not introduced by this WP.

---

*Manifest authored by team_191 (Git/Files) per ADR042 archive mandate, 2026-06-03.*
