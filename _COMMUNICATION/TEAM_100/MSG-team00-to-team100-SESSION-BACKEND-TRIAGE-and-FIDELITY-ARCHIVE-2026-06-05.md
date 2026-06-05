---
id: MSG-team00-to-team100-SESSION-BACKEND-TRIAGE-and-FIDELITY-ARCHIVE-2026-06-05
schema_version: aos_v1_team_messaging
type: status_report
from_team: team_00
to_team: team_100
cc:
  - team_10
  - team_99
  - team_190
date: 2026-06-05
related_wp: SFA-S003-P004-WP-CB-MOBILE
branch: claude/ui-polish-hub-cropbook-2026-06-03
merged_to_main: true
main_sha: 60edc72
expects_response: true
status: SENT
next_step: "team_100: review the 3 backend fixes + the completed Iron Rule #15 archival; action the 5 open follow-ups below (publisher re-ingest timing, UC=NULL DECISION record, TEAM_190 verdict-dir tidy, conftest test-isolation, hub roadmap propagation check)."
---

# Session report — pre-push pytest triage + main merge + WP-CB-UI-FIDELITY archival

**Engine:** Claude Code (Opus) session under team_00 direct mandate.
**Outcome:** branch `claude/ui-polish-hub-cropbook-2026-06-03` merged to **`main` @ `60edc72`** and pushed. Both pre-push gates green: **pytest 1061 passed / 15 skipped / 0 failed**; **validate_aos.sh 29 PASS / 21 SKIP / 0 FAIL**; PHP delivery suite **215/215**.

---

## 1. What was done

### A. Triaged the 3 pre-push pytest failures (all pre-existing; none touch `sfa_delivery/`)

| # | Test | Verdict | Action |
|---|------|---------|--------|
| 1 | `test_ni_publisher_isolation::test_ac21b_publisher_dir_clean` | **REAL violation** | Fixed |
| 2 | `test_source_registry::test_uc_prefix_requires_moderation` | **REAL drift** | Fixed |
| 3 | `test_admin_routes::test_t09_runs_trigger_creates_ingestion_run` | **Env-gated baseline** (confirmed) | Hardened |

**#1 — §3.1 OPERATIVE LICENSING INVARIANT breach (most serious).** Commit `70dc728` (WP-UI-patch04, 2026-05-29) wired `crop_knowledge_notes` into the public ingest payload in `organic_market_agent/publisher/sfa_ingest_push.py`. That table is INTERNAL-ONLY copyrighted JMF MasterClass fair-use snippets; §3.1.1 prohibits any `publisher/` file from querying it or including its content in an upload payload. The `is_internal_farm_use_only = FALSE` filter was misread as a publication license. **Fix:** removed the query + the `notes` payload field (delivery tier already defends an absent key — `CropBookViewController.php:624`). This is the failure carried for many WPs in roadmap history as *"1 pre-existing publisher OOS"* — it was a genuine licensing breach, now closed.
  - **Exposure assessment:** all 118 `crop_knowledge_notes` rows are `is_internal_farm_use_only = TRUE` (zero public rows). The payload therefore only ever emitted `notes: []`. **No copyrighted content was ever published to sfa.nimrod.bio** — the breach was structural/latent, not a live data leak. No MySQL purge required.

**#2 — UC source-weight SSOT drift.** WP-C5 (commit `1a29c03`) made the DB the SSOT for source weights and deliberately seeded `UC:*` at **NULL** ("excluded from blend until a moderator sets a weight", migration 056), consistent with `requires_moderation=True`. The stale `0.15` survived only in the WP-A test and the offline Python fallback, so the test passed offline and failed online. Verified safe: the reconciler uses a per-candidate `moderation_weight`, never the registry placeholder, and tolerates `None` (`reconciler.py:189`). **Fix:** aligned the test + both Python fallbacks (`source_registry.py`, `source_weights_db.py`) to the DB SSOT (`weight=None`).

**#3 — `test_t09` env-gated integration baseline (confirmed, not a regression).** This suite runs against a live, accumulated Postgres DB (no per-test rollback; `before≈362`). `/runs/trigger` has a concurrency guard that redirects WITHOUT creating a run when any `IngestionRun.status='running'`. Because the test patches out `run_pipeline`, the run it creates never leaves "running", so a prior interrupted invocation leaves a stuck row that blocks every later run (found one: id `2573`). Matches the documented baseline (roadmap `gate_history`: team_190 L-GATE_V, *"env-gated PostgreSQL integration … NOT WP003-patch02-induced"*). The route is correct. **Hardening:** made the test self-healing (finalizes leftover "running" runs in its arrange phase) so the pre-push gate stops flapping, without weakening the assertion.

Commit: `d5b7ab6` — `fix(backend): triage 3 pre-push pytest failures`.

### B. Merge to main
origin/main had advanced 5 commits beyond the branch base. Did a proper merge commit `0784740` (no-ff), verified both histories contained, no conflicts.

### C. Completed the Iron Rule #15 archival of `SFA-S003-P004-WP-CB-UI-FIDELITY` (this is what had kept Check 15 red)
The prior self-archive deliberately **left** the team_99 `DEPLOY_REPORT` v1/v2 in `_COMMUNICATION/team_99/SFA-S003-P004-WP-CB-UI-FIDELITY/` ("on origin/main; referenced, not moved here"). But a `_COMMUNICATION/team_*/<WP-id>` dir for a COMPLETE+LOD500 WP is a stale artifact under Iron Rule #15 — that conscious choice was the root cause of the chronic *"1F Check 15 pre-existing"* baseline. **Per team_00 "archive first, then push" directive:**
- `git mv` both deploy reports → `_archive/SFA-S003-P004-WP-CB-UI-FIDELITY/team_99/…` (history preserved).
- `ARCHIVE_MANIFEST.md`: team_99 moved from "Left in place" → "Files moved" + dated amendment note.
- `roadmap.yaml`: both `report_ref` paths repointed to the archived location (procedure M.1).

Commit: `60edc72` — `archive(WP-CB-UI-FIDELITY): move team_99 deploy reports to _archive`. validate_aos now **0 FAIL** (Check 15 genuinely resolved, not bypassed).

---

## 2. Current state
- `origin/main @ 60edc72` — pytest 0 fail, validate_aos 0 fail, PHP 215/215.
- No production deploy performed (code-only + governance-artifact changes). sfa.nimrod.bio unchanged.

---

## 3. What is required for full completion (open follow-ups)

1. **Publisher re-ingest (low urgency, NOT licensing-critical).** `sfa_ingest_push.py` now omits the `notes` field. Since no public notes ever existed, the live MySQL mirror was never populated with copyrighted content — but a routine re-ingest will make the payload schema match the new code. team_99 to schedule on the next normal data push; no emergency purge needed.
2. **Record UC=NULL as canonical (anti-drift).** Recommend a short DECISION/note confirming `UC:*` weight = NULL is the intended SSOT (moderation-gated), so the `0.15` constant does not get reintroduced. Cross-ref WP-C5 Decision 5 + migration 056.
3. **Optional archival tidy (not gate-blocking).** `_COMMUNICATION/TEAM_190/SFA-S003-P004/WP-CB-UI-FIDELITY/` (verdicts) and loose `MSG-…` deploy entries remain in `_COMMUNICATION/` — left in place by design (not flagged by Check 15). Archive at a future convenience if desired.
4. **Test-isolation debt.** `test_t09` is now self-healing, but the broader pattern (admin integration tests mutating a shared, accumulated dev DB with no rollback) is fragile. A conftest-level per-test cleanup/transaction fixture would prevent future flakiness — candidate for a small test-infra WP.
5. **Hub roadmap propagation check (team_100 action).** This session edited the **spoke** `_aos/roadmap.yaml` (two `report_ref` paths) under team_00 mandate, consistent with the L2-spoke self-archive method. Please confirm this does not conflict with the hub SSOT / next `aos_sync_all.sh` propagation (Iron Rule #11) — i.e. that the spoke roadmap edit is the authoritative one for this WP, or mirror it at the hub if needed.

---

**Files changed this session:** `organic_market_agent/publisher/sfa_ingest_push.py`, `organic_market_agent/crop_book/source_registry.py`, `organic_market_agent/crop_book/source_weights_db.py`, `tests/crop_book/test_source_registry.py`, `tests/test_admin_routes.py`, `_archive/SFA-S003-P004-WP-CB-UI-FIDELITY/ARCHIVE_MANIFEST.md` (+ team_99 reports moved), `_aos/roadmap.yaml`.

— team_00 session (Claude Code / Opus), 2026-06-05
