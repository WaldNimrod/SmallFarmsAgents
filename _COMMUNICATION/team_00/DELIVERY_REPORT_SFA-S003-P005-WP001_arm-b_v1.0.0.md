---
id: DELIVERY_REPORT_SFA-S003-P005-WP001_arm-b_v1.0.0
type: DELIVERY_REPORT
deliverable: D6
wp: SFA-S003-P005-WP001
arm: pilot/arm-b (branched from pilot/lean-env @ 7842617)
builder_engine: claude-code / claude-opus-5
date: 2026-08-14
---

# Delivery report — SFA-S003-P005-WP001 (arm-b)

## 1. Task

Full DV-1 fix for the SmallFarmsAgents deploy path: make a deploy green only when the code
**actually serving** is asserted equal to the code pushed. Six deliverables (D1 health
endpoint + test, D2 corrected `post-receive`, D3 hub-installer SFA block, D4 reasoned
assessment of `sfa-admin.service`'s hard `EnvironmentFile=`, D5 proof of work, D6 this
report). No server access — every server-side step is delivered as an artifact for the
conductor to install.

## 2. Sources checked

| Source | Why |
|---|---|
| `SERVER_FACTS_SFA_DEPLOY_v1.0.0.md` (the one permitted external file) | current hook text, deploy-tree/`.env`/`.venv` layout, `sfa-admin.service`, the `/api/health` 404, drift |
| `CLAUDE.md` §1–§6 | the binding rule set (R1–R8) and the locked test invocation |
| `_aos/roadmap.yaml` row for this WP (derived via §2a, not read whole) | scope, gate, validator wiring |
| `organic_market_agent/admin/__init__.py`, `routes/{diagnostics,maintenance}.py` | blueprint convention, `before_request` DB coupling, the `ADMIN_SECRET_KEY` fallback cited in D4 |
| `tests/conftest.py`, `tests/test_admin_routes.py` | existing fixtures — reused rather than duplicated |
| Repo greps for `health`, `AOS_BUILD_SHA`/`build_sha`, `post-receive`, `scripts/hooks/` | R5: prove nothing already existed before adding a file |

Nothing from §6's optional index was opened (reading is measured). No `.env*` file was
read, printed or logged at any point (R2); the hook's own check is `test -s`, existence and
size only.

## 3. Produced / missing

**Produced — all six.**

- **D1** `organic_market_agent/admin/routes/health.py` — public `GET /api/health` →
  `{"status":"ok","build_sha":…,"sha_source":"env|git|unavailable"}`. Env `AOS_BUILD_SHA`
  wins; fallback `git rev-parse HEAD` in the repo root; `"unknown"/"unavailable"` if git is
  absent. **The SHA is resolved once at import time (process start), not per request** —
  a per-request read would report the *working tree*, so a deploy whose pull landed but
  whose restart silently failed would still answer with the new SHA and verify green. The
  endpoint touches no database, so "which code is running" stays answerable when a
  dependency is down. Registered in `admin/__init__.py`. 5 tests appended to the existing
  `tests/test_admin_routes.py` (t19–t23), including one that asserts the served SHA does
  *not* follow a live env change.
- **D2** `scripts/deploy/sfa_post_receive.sh` — the hook content, kept in-repo so it is
  reviewable and dry-runnable, installed by copy (D3). Ref-scoped like the agents-os
  reference hook; pull-in-place **preserved** and hardened to `--ff-only`; asserts deploy
  tree `HEAD == pushed SHA` before restarting; restarts; then polls the health endpoint
  (warmup + retries) and compares served `build_sha` to the pushed SHA. Mismatch ⇒ loud
  banner + `exit 24`. Exit codes: 0 ok / 20 pre-flight (no mutation) / 21 pull or HEAD
  mismatch (service not restarted) / 22 restart failed / 23 health unreachable /
  24 DV-1 mismatch. **Forbidden ops absent**: no `reset --hard`, no `clean -fdx`, no
  `rm -rf`, no re-clone (R3).
- **D3** `_COMMUNICATION/team_00/HUB_INSTALLER_SFA_BLOCK_…_v1.0.0.md` — idempotent
  installer block (backup, `install -m 0755`, post-install `cmp` verify, advisory health
  probe), plus the bootstrap ordering trap and an AC-B4 recipe for demonstrating DV-1
  failing on the real path.
- **D4** `_COMMUNICATION/team_00/ASSESSMENT_SFA_ADMIN_SERVICE_ENVFILE_…_v1.0.0.md` —
  **verdict: keep the hard `EnvironmentFile=`, do not soften.** Softening removes the alarm
  and not the fault; this app's config-less start is silent-and-wrong (`ADMIN_SECRET_KEY`
  falls back to `"dev-secret-change-me"`); and a soft directive plus a DB-free health
  endpoint would manufacture a *verified* deploy of a service that cannot reach its
  database. The real cost of the hard form — a 5s crash loop under `Restart=always` — is
  paid by the hook's pre-restart `test -s` abort (delivered) and a recommended
  `StartLimitIntervalSec`/`StartLimitBurst` pair (conductor's call, not delivered).
- **D5** below (§ Proof of work).
- **D6** this file.

**Missing / deliberately out of scope** (named, not hidden):

1. **Auto-rollback.** The hook fails loud and leaves the tree as-is. A safe rollback needs
   a persisted previous-SHA state dir and an ff-only re-activation path; inventing one here
   would add an unverified mutation to the failure path. `aos_hub_deploy.sh` exit codes
   21/22 model what this would look like later.
2. **Installation and the AC-B4 real-path red demonstration.** No server access by design —
   D3 §3/§4 give the conductor the exact commands.
3. **`AOS_BUILD_SHA` stamping.** Not wired; the git fallback is sufficient and correct
   because it is captured at process start. D4's closing section describes the clean shape
   if it is wanted later.
4. **`_aos/roadmap.yaml` not touched.** CLAUDE.md §1 calls `_aos/` a read-only snapshot
   ("do not edit it") while §5 says a spoke row is edited directly and committed. I did not
   resolve that contradiction unilaterally in a governance file, especially with R7 giving
   the gate verdict to the conductor — flagged in §5 below.

## 4. Proof of work (D5)

**Locked test command**

```bash
cd /Users/nimrod/Documents/AOS_V5/SmallFarmsAgents && .venv/bin/python3 -m pytest -m "not upress and not integration" -q
```

| Run | Result |
|---|---|
| Baseline, before any change (this branch, 21:09Z) | `1 failed, 1002 passed, 88 skipped, 25 deselected` |
| After all changes (21:15Z) | `1 failed, 1007 passed, 88 skipped, 25 deselected` |

Same single pre-existing failure
(`tests/crop_book/test_wp_upload_crop_book.py::test_dispatch_upload_crop_book_profile`,
not mine), +5 passing = the five new health tests. **Zero new failures ⇒ green** by the
definition given.

**Hook dry run** — `bash scripts/deploy/sfa_post_receive_dryrun.sh`, full output attached
at `_COMMUNICATION/team_00/DRYRUN_OUTPUT_SFA-S003-P005-WP001_2026-08-14.txt`. It drives
**the real hook file** (not a copy or re-implementation) against a disposable sandbox — its
own bare repo + deploy tree — with the systemd restart and the health probe mocked through
the hook's documented env overrides. **10 checks, 10 passed:**

| # | Scenario | Expected | Got |
|---|---|---|---|
| S1 | served `build_sha` == pushed SHA | exit 0 `DEPLOY VERIFIED` | ✅ |
| S2 | stale process — served SHA is the *previous* one | exit 24 DV-1 MISMATCH | ✅ |
| S3 | health returns Flask 404 HTML (today's server state) | exit 23 | ✅ |
| S4 | `systemctl restart` fails | exit 22 | ✅ |
| S5 | required env file absent | exit 20, **before** any mutation | ✅ |
| S5b | deploy-tree HEAD unchanged after that abort | unchanged | ✅ |
| S6 | push to `refs/heads/feature-x` | ignored, exit 0 | ✅ |
| S7 | **real `git push`** into a bare repo with the hook installed | fires, ff, verifies | ✅ |
| S8 | **real `git push`** with a stale served SHA | loud exit-24 banner in output + `deploy.log` | ✅ |
| S9 | destruction guard: untracked env file and `.venv`-shaped dir survive all scenarios | intact | ✅ |

S2 is the case the old hook printed `DEPLOY OK` for.

**Rule self-checks over the staged diff**

```bash
git diff --cached -U0 | grep -nE 'cat .*\.env|source .*\.env'                 # R2 -> (none)
git diff --cached -U0 | grep -nE 'reset --hard|clean -fdx|rm -rf|git clone'   # R3
```

R3 returns hits only in (a) prose/comments that name the forbidden ops in order to forbid
them, (b) the dry-run harness's `rm -rf "$SANDBOX"` where `$SANDBOX` is a `mktemp -d`
directory created in the same run, and (c) that harness's `git clone` of its own sandbox
bare repo. Both (b) and (c) are the "disposable temp sandbox" carve-out R3 names; the
installed hook itself contains none of the four (the dry run greps it and prints the
result).

## 5. Confidence and assumptions

**High confidence**

- The health endpoint's contract and its process-start capture — covered by tests, and the
  capture semantics are asserted directly (t22).
- The hook's control flow, exit codes and destruction-safety — exercised end-to-end,
  including through a real `git push`, in 10 scenarios.
- D4's verdict — it rests on unit semantics plus a code fact in this repo
  (`ADMIN_SECRET_KEY` default), both checkable.

**Assumptions, each falsifiable by the conductor**

1. **The installer's shape (D3).** The facts pack contains no hub installer script — only
   the hook it writes — and I was limited to that one external file, so the block is
   written to the observable contract as a self-contained bash function. If
   `deploy_server_hooks.sh` is table-driven, the function body is the payload to lift.
2. **`origin` in the deploy tree is the bare repo** (facts pack §4 confirms
   `origin → /data/repos/smallfarmsagents.git`), so `git pull --ff-only origin main`
   reaches the pushed SHA. If that remote is ever repointed, the hook fails at exit 21
   rather than deploying something else — the safe direction.
3. **`--ff-only` will not regress today's behaviour.** The deploy tree has zero modified
   tracked files and is 1 commit behind (facts pack §4/§7), so the fast-forward is clean.
   A future divergence now fails loudly instead of silently merging — deliberate.
4. **`python3` exists on the server** for the hook's JSON parse (listed as a prerequisite of
   the neighbouring `aos_hub_deploy.sh`, so it is present on this host).
5. **Health probe target** `http://127.0.0.1:5001/api/health` matches the unit's
   `--host 127.0.0.1 --port 5001` and the path the facts pack already probed.

**Known behaviour worth stating rather than discovering later:** `git push` exits **0** even
when `post-receive` fails — git does not un-update the ref for a post-receive failure
(observed in S8, not assumed). The red signals are the `remote:` banner, `deploy.log`, and
the hook's exit code. A machine-readable green/red at the pusher would need the conductor
to invoke the deploy path over ssh and read its exit status, as the hub runbook does for
`aos_hub_deploy.sh`. Out of this WP's K=6; flagged.

## 6. Needed now (from the human / conductor)

1. **Install D3, in the order given in D3 §3** — the bootstrap trap is real: the hook can
   only be installed after the deploy tree already contains
   `scripts/deploy/sfa_post_receive.sh`, and `sfa-admin` must be restarted once so
   `/api/health` exists, or the first verified push exits 23.
2. **Run the AC-B4 red demonstration** (D3 §4) — DV-1 failing on the real deploy path,
   which only the conductor can do.
3. **Decide the `_aos/roadmap.yaml` question** (§3 item 4): CLAUDE.md §1 forbids editing
   `_aos/`, §5 instructs editing your own spoke row there. Those cannot both hold. I left
   the file untouched and am reporting the contradiction rather than resolving it silently,
   as §1 directs.
4. **Optional, one line, server-side:** `StartLimitIntervalSec=60` / `StartLimitBurst=3` in
   `sfa-admin.service` (D4 §4b) to bound the crash loop that the hard `EnvironmentFile=`
   implies.

Nothing was blocked on a human during the build: **zero questions asked**.

## 7. Artifacts

| Path | D | Kind |
|---|---|---|
| `organic_market_agent/admin/routes/health.py` | D1 | new |
| `organic_market_agent/admin/__init__.py` | D1 | edited (import + `register_blueprint`) |
| `tests/test_admin_routes.py` | D1 | edited (t19–t23 appended) |
| `scripts/deploy/sfa_post_receive.sh` | D2 | new — install verbatim as `/data/repos/smallfarmsagents.git/hooks/post-receive` |
| `scripts/deploy/sfa_post_receive_dryrun.sh` | D5 | new |
| `_COMMUNICATION/team_00/HUB_INSTALLER_SFA_BLOCK_SFA-S003-P005-WP001_v1.0.0.md` | D3 | new |
| `_COMMUNICATION/team_00/ASSESSMENT_SFA_ADMIN_SERVICE_ENVFILE_SFA-S003-P005-WP001_v1.0.0.md` | D4 | new |
| `_COMMUNICATION/team_00/DRYRUN_OUTPUT_SFA-S003-P005-WP001_2026-08-14.txt` | D5 | new — real captured output |
| `_COMMUNICATION/team_00/DELIVERY_REPORT_SFA-S003-P005-WP001_arm-b_v1.0.0.md` | D6 | new — this file |
| `PILOT_ARM_MEASUREMENT.md` | — | new — pilot instrumentation |

Every new file is justified under R5 by a search that returned zero: no health route or
build-SHA surface existed (`grep -rln 'health' --include='*.py'`, `grep -rn 'build_sha'` →
0 hits), and no deploy-hook file existed (`grep -rl 'post-receive'` → 0 hits;
`scripts/hooks/` holds only pre-commit/pre-push/pre-receive governance guards). Both test
additions and the blueprint registration went into files that already existed.

## 8. Timestamps

| Event | UTC |
|---|---|
| Session start (`PILOT_ARM_MEASUREMENT.md`) | 2026-08-14T21:08:27Z |
| Baseline locked-test run | 2026-08-14T21:09Z |
| D1 complete (health endpoint + 5 tests green) | 2026-08-14T21:11Z |
| D2 + D5 harness complete (first full dry run, 9/9) | 2026-08-14T21:13Z |
| D3 + D4 written; dry run extended to 10/10 and captured | 2026-08-14T21:14Z |
| Final locked-test run (1 failed / 1007 passed) | 2026-08-14T21:15Z |
| This report | 2026-08-14T21:16Z |

## 9. Cost

- **Wall clock, first action to report: ~8 minutes** (21:08:27Z → 21:16Z).
- **Human interruptions: 0.** No question was asked; no approval was needed.
- **External reading: 1 file** — the facts pack, as instructed. Zero files from CLAUDE.md
  §6's optional index were opened (that index exists because reading is a measured cost).
- **Server round-trips: 0** (no access by design; all server-side work is artifacts).
- **Executions: 2 full locked-suite runs (~11s and ~12s), 1 scoped test run, 2 full dry
  runs.** ~25 tool calls total.
- Token/currency accounting is not observable to me from inside the session; the conductor
  holds those figures for the arm comparison.
