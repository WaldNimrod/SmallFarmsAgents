# Team 100 — M7 Work Plan Review Feedback for Team 10

**Date:** 2026-03-31
**From:** Team 100 (Architecture)
**To:** Team 10 (Feature Development)
**Subject:** M7 Work Plan — APPROVED WITH REVISIONS (v1 → v2)

---

## Summary

Team 10's M7 draft (v1) was well-structured and covered the right scope. Team 100 has upgraded it to **v2** with binding architectural decisions, concrete implementation specifications, and fixes for identified gaps. **All 4 decisions from §7 have been made — no further consultation needed.**

The revised plan is at:
`_COMMUNICATION/TEAM_100/reports/2026-03-31_M7_WORK_PLAN_FOR_APPROVAL_TEAM100.md`

---

## Key Changes: v1 → v2

### 1. Architectural Decisions Made (§7)

| Decision | v1 (open question) | v2 (binding) |
|----------|--------------------|----|
| Publish contract | "Team 100 should pick A or B" | **Option A — APPROVED** (versioned + fixed filenames + manifest pointers) |
| WP integration | "Approve body fragment + shortcode?" | **APPROVED** with concrete shortcode spec |
| Manifest fields | "Approve extending?" | **APPROVED** — full manifest v2 schema defined in §6.3 |
| Scheduler chain | "Single cron vs separate upload cron?" | **Single chain — APPROVED**, with `skip_upload=True` default |
| Upload default | Not specified | **Default OFF** — `scheduler_config.upload_enabled` controls cron behavior |

### 2. New Concrete Specifications Added (§6)

| Section | What was added |
|---------|---------------|
| §6.1 Test Requirements | Proper pytest conventions, file naming, marker registration, English-only, known bugs in mandate draft code |
| §6.2 FTPS Module Spec | Full interface (`FtpsUploadResult` dataclass, `upload_artifacts()` function), retry strategy, timeout, alert tags |
| §6.3 Manifest v2 Schema | Complete JSON schema with all fields defined; upload protocol with strict 8-step ordering |
| §6.4 Pipeline Integration | `skip_upload` parameter spec, `run_upload` CLI command, `scheduler_config.upload_enabled` column |
| §6.5 WP Body Fragment | Template rules, CSS prefixing, PHP shortcode code, install instructions |
| §6.6 Configuration | Exact `.env.example` keys, config module extension spec |
| §6.7 Rollback/Degradation | Full failure scenario table with expected behavior |

### 3. Missing Items Added

| Item | Why it matters |
|------|---------------|
| **M7-9: Test artifact cleanup** | Mandate tests upload files to production server — must be cleaned up |
| **§11: New files list** | Complete inventory of files to create and modify — agents know exactly what to touch |
| **Known bugs in mandate test code** | URL construction bug in U08, redundant imports, print()-based testing — flagged for rewrite |
| **Migration 030** | `upload_enabled` column on `scheduler_config` — assigned to Team 20 |
| **Alert tags** | 4 new FTPS alert tags defined |
| **Upload protocol** | Strict 8-step ordering: artifacts first → fixed names → manifest last → manifest_last_good on full success |
| **Rollback table** | What happens when upload fails partially, fully, or TLS is unsupported |

### 4. WBS Changes

| v1 | v2 |
|----|----|
| 10 items (M7-0 → M7-9) | 13 items (M7-0 → M7-12) |
| M7-2: "publish contract decision" (waiting for 100) | M7-2: "manifest v2 schema" (decision made, implement now) |
| No cleanup step | M7-9: test artifact cleanup |
| No docs step | M7-10: documentation update |
| — | M7-11: completion report |
| — | M7-12: QA validation |

### 5. Items NOT Changed (v1 was correct)

- Overall scope boundaries (in-scope / out-of-scope)
- Preconditions (G6, Nimrod approval)
- Timeline structure (4 weeks)
- §10 information checklist from Nimrod
- Risk identification (expanded with likelihood/impact)

---

## Action Items for Team 10

1. **Read the v2 plan in full** before starting any M7 work
2. **Read the spec documents** listed in §2 Preconditions
3. **Rewrite all test code** from the mandate as proper pytest (§6.1) — the mandate code is illustrative only
4. **Fix the known bugs** in test code (U08 URL construction, redundant imports)
5. **Follow the upload protocol** exactly as specified in §6.3 — artifact order matters
6. **Log all changes** in `CHANGELOG.md` under `[Unreleased]` per project iron rule
7. **Wait for Nimrod** to complete §10 checklist before starting M7-1

---

## Action Items for Team 20

1. **Prepare migration 030:** add `upload_enabled BOOLEAN DEFAULT FALSE` to `scheduler_config` table
2. **Review `.env.example`** additions when Team 10 implements them

---

## Action Items for Team 50

1. **Issue `QA_MANDATE_G7.md`** after Nimrod gives M7 go-ahead, aligned to v2 plan
2. **Include changelog verification** in G7 gate criteria per project iron rule
3. **U01–U12 must pass** as proper pytest tests, not as standalone scripts

---

*End of feedback.*
