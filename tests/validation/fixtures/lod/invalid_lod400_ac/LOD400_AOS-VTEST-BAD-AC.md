---
lod_target: LOD400
lod_status: LOD400_APPROVED
track: A
profile: lean
authoring_team: team_test
consuming_team: team_10
date: 2026-01-01
version: v1.0.0
work_package_id: AOS-VTEST-BAD-AC
milestone_ref: VTEST
---

# LOD400 — Bad AC Format Fixture

## §0 Scope
Test-only fixture with bad AC numbering.

## §1 Technical Architecture
Content here.

## §2 Script Specifications
Content here.

## §3 Fixture Specifications
Content here.

## §4 Test Script Specifications
Content here.

## §5 Interface Contracts
Content here.

## §6 Governance Document Update Manifest
Content here.

## §7 Deployment Instructions
Run make install.

## §8 Rollback Procedure
Run make uninstall.

## §9 Acceptance Criteria

| AC | Criterion |
|----|-----------|
| AC-1 | Script exists at declared path |
| AC-2 | Script exits 0 on valid fixture |
| AC-10 | Script exits 1 on invalid fixture |
