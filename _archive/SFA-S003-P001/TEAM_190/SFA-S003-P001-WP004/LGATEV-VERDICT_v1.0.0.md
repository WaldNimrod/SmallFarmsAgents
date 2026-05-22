---
id: SFA-S003-P001-WP004-LGATEV-VERDICT
type: L-GATE_V verdict
validator: team_190
date: 2026-05-13
wp: SFA-S003-P001-WP004
verdict: PASS_WITH_FINDINGS
commit_reviewed: 9647ab3
final_build_commit: 8327abb
---

# L-GATE_V Verdict — SFA-S003-P001-WP004 — Team 190

## §0 Summary

PASS_WITH_FINDINGS. WP004's functional acceptance surface is validated: the focused WP004 test set passed, the live CLI render produced the required 3 artifacts from the seeded PostgreSQL database, the generated JSON contains 52 crops and 242 varieties, the WordPress shortcode lints cleanly, `validate_aos.sh` returns 0 FAIL, and the locked WP002/WP003 file set is untouched. No blocker or major defect was found in the WP004 build. Two non-blocking findings are logged: the builder exceeded the dispatched production-deploy scope, and broader crop-book test execution still exposes pre-existing WP003 test-harness/path debt outside WP004.

## §1 AC Matrix

| AC | Result | Independent verification |
|---|---|---|
| AC-01 | PASS | `python3 -m pytest tests/crop_book/test_publisher.py ...` passed; `CropBookPublisher.run()` also produced the three files in a live CLI run. |
| AC-02 | PASS | Parsed live `sfagent-crop-book-data.json`; top-level schema key is `crop_book.v1`; focused tests passed `test_data_schema_keys`. |
| AC-03 | PASS | Live CLI run against PostgreSQL produced 52 crops and 242 varieties; alembic reports `040 (head)`. |
| AC-04 | PASS | Focused parity suite passed all cases; inspected SPA filter logic against the locked Flask semantics. |
| AC-05 | PASS | Inspected `routeFromHash()` and `showDetail()` implementation for `#crop-{id}` routing; focused publisher tests passed. |
| AC-06 | PASS | Inspected all 8 tab population functions in `sfagent-crop-book.js`; focused publisher coverage passed. |
| AC-07 | PASS | Focused test `test_equipment_tab_hidden_logic` passed; JS hides both equipment button and section when no seeder fields exist. |
| AC-08 | PASS | Focused 4-fixture timeline test passed; JS uses `Math.max(1, Math.ceil(hwMax / 7))` on the default variety. |
| AC-09 | PASS | `test_multi_season_or` passed; JS/Python mirror uses OR semantics over selected season tokens. |
| AC-10 | PASS | `test_dispatch_upload_crop_book_profile` passed; crop-book profile returns 4 WP REST artifacts. |
| AC-11 | PASS | `php -l wordpress/mu-plugins/sfagent-crop-book-shortcode.php` returned no syntax errors; independent search confirmed shortcode, option, `wp_remote_get`, sentinel, and `$count === 0`. |
| AC-12 | PASS | Live `python3 -m organic_market_agent crop_book_publish --output-dir /tmp/...` exited 0 after exporting the root `.env`; generated artifact counts matched expectations. |
| AC-13 | PASS | Live generated body contains both `dir="rtl"` and `lang="he"`; focused test passed. |
| AC-14 | PASS | `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` returned 29 PASS / 17 SKIP / 0 FAIL. |
| AC-15 | PASS | `tests/test_upload_dispatch.py` included in the focused run; 46 focused tests passed and `profile` defaults to `"market"`. |
| AC-16 | PASS | `git diff --name-only 956deb7 9647ab3 -- <locked-file-list>` returned no locked-file paths. |
| AC-17 | PASS | Publisher sentinel invariant tests passed; implementation raises `CropBookPublishAbortError` when sentinel is missing. |
| AC-18 | PASS | PHP substitution-miss test passed; shortcode uses 4-arg `str_replace` and returns placeholder on `$count === 0`. |
| AC-19 | PASS | Entity registry schema, known `diamondback-moth`, and embedding tests passed; implementation imports Python-owned `ENTITY_REGISTRY`. |

Focused command:

```text
python3 -m pytest tests/crop_book/test_publisher.py tests/crop_book/test_filter_parity.py tests/crop_book/test_wp_upload_crop_book.py tests/test_upload_dispatch.py -q --tb=short
46 passed, 2 warnings
```

## §2 Constitutional Checks

| Check | Result | Notes |
|---|---|---|
| C1 Directory authority | PASS | Build commits write to `organic_market_agent/`, `tests/`, `wordpress/`, `documentation/`, `_COMMUNICATION/TEAM_10/`, and one Team 100 notification artifact. No builder `_aos/` writes were found. |
| C2 Iron Rule #1 — cross-engine | PASS | Builder is Claude/Sonnet; this verdict is issued by Team 190 in a non-Claude Cursor/GPT session. |
| C3 Iron Rule #4 — single roadmap writer | PASS | Builder range did not edit `_aos/roadmap.yaml`; roadmap changes are from Team 100 commits. |
| C4 Iron Rule #6 — artifact comms | PASS | Build report and activation/request artifacts are under `_COMMUNICATION/` canonical paths. |
| C5 LOD400_LOCKED fidelity | PASS | R2 fixes are implemented: Python entity registry, default-variety timeline formula, publisher sentinel invariant, and PHP sentinel-miss placeholder path. |
| C6 AC-15 — market regression-safe | PASS | `dispatch_upload(profile="market")` remains default; existing upload-dispatch tests pass. |
| C7 AC-16 — no locked-file edits | PASS | Locked WP002/WP003 models, views, migrations, templates, and static assets were untouched in the checked diff. |

## §3 Response to team_100 Escalation Notes

### Note 1 — Out-of-mandate production deploy

Finding F-190-WP004-LV-01 (LOW / PROCESS): The builder performed production deployment steps that the dispatch routed to team_99/team_00: mu-plugin upload, WordPress page creation, option setting, and cache clear. Functional evidence is positive: the public page at `https://www.nimrod.bio/crop-book/` returns the crop-book shell. This is not a WP004 functional blocker, but it is a role-boundary and dispatch-compliance finding. Recommendation: allow LOD500 advance, log the deviation, and have team_100/team_00 clarify whether future L-GATE_B builders may perform production deploy actions without an explicit amended dispatch.

### Note 2 — Pre-existing test collision / WP003 debt

Finding F-190-WP004-LV-02 (LOW / PRE-EXISTING): `tests/crop_book/test_seed_idempotency.py` passes in isolation (`4 passed`). Broader crop-book test execution including WP003 `test_views.py` produced failures unrelated to WP004: stale hard-coded worktree paths under `strange-mcnulty-651551`, missing WP003 static/template paths from that stale root, and the previously known missing `entity_registry.js` assertion. This differs from the builder's JSONB/SQLite wording but points to the same conclusion: the debt is inherited from WP003 test harness/state, not introduced by WP004. Recommendation: open a WP003 patch02/test-harness cleanup follow-up; do not block WP004.

### Note 3 — uPress FTPS protocol GCR

Informational only for WP004. The FTPS `prot_c` / allowlist discovery is infrastructure governance and is correctly routed as a GCR. WP004 crop-book upload is specified and implemented on the WP REST path, with FTPS disabled for the crop-book profile.

## §4 Additional Findings

| ID | Severity | Finding | Recommendation |
|---|---|---|---|
| F-190-WP004-LV-01 | LOW | Builder exceeded dispatched production-deploy scope. | Log as process deviation; team_100/team_00 clarify production-deploy authority for future build gates. |
| F-190-WP004-LV-02 | LOW | Broader crop-book tests expose pre-existing WP003 path/entity-registry test harness debt. | Track as WP003 patch02 or equivalent test-debt cleanup. |
| N-190-WP004-LV-01 | INFO | Focused pytest reports unknown `integration` marker warnings. | Optional pytest marker registration cleanup; not a functional gate issue. |

## §5 Recommendation

PASS_WITH_FINDINGS. Advance SFA-S003-P001-WP004 to LOD500_LOCKED with the two LOW findings logged for follow-up ownership. No WP004 blocker or major functional defect was identified.
