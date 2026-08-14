# SFA deploy path — DV-1 verification

**WP:** SFA-S003-P005-WP001 (AOS stage-B pilot, arm A) · **Date:** 2026-08-14
**Facts basis:** `SERVER_FACTS_SFA_DEPLOY_v1.0.0.md` (hub, 2026-08-14) — the only
server-side source consulted. This session had **no server access**; every
server-side change below is an artifact for the conductor to install.

---

## 1. The defect

The installed hook (`/data/repos/smallfarmsagents.git/hooks/post-receive`) ends with:

```bash
echo "DEPLOY OK (no health check for SFA)"
```

That line is unconditional. It prints after a failed pull, after a failed
restart (which the old hook downgraded to `WARN: sfa-admin not active` and then
walked past), and after a restart that took effect on nothing. The deploy path
reported success without ever asking what was serving. There was also nothing
to ask: `GET /api/health` returned Flask's default 404 (facts pack §6), and the
build sha appeared nowhere in the app.

Secondary defect from the same pack: the hook is not ref-scoped — it ran
`git pull origin main` for a push to *any* ref (§1).

## 2. What was built

| # | Deliverable | File |
|---|---|---|
| D1 | Health endpoint + tests | [`organic_market_agent/admin/routes/health.py`](../../organic_market_agent/admin/routes/health.py), [`tests/test_admin_health.py`](../../tests/test_admin_health.py) |
| D2 | Corrected hook | [`scripts/deploy/post-receive.sfa`](../../scripts/deploy/post-receive.sfa) |
| D3 | Hub installer block | [`scripts/deploy/hub_installer_sfa_block.sh`](../../scripts/deploy/hub_installer_sfa_block.sh) |
| D5 | Dry-run harness + output | [`scripts/deploy/dryrun_post_receive_sfa.sh`](../../scripts/deploy/dryrun_post_receive_sfa.sh), [`evidence/DV1_DRYRUN_post_receive_sfa_2026-08-14.txt`](evidence/DV1_DRYRUN_post_receive_sfa_2026-08-14.txt) |

### 2.1 `GET /api/health`

```json
{"status": "ok", "service": "sfa-admin", "build_sha": "<40-hex>"}
```

`build_sha` = `$AOS_BUILD_SHA` when set and non-empty, else
`git rev-parse HEAD` in the checkout, else the literal `unknown`. Always 200,
always JSON, no auth, and it deliberately does **not** open a DB session — a
Postgres outage must not be indistinguishable from a bad deploy.

**The one design decision that makes the check worth anything:** the sha is
resolved *once*, when `create_app()` builds the Flask app, and stored in
`app.config`. A per-request `git rev-parse` would read the freshly-pulled
working tree and happily report the new sha from a process still running the
old code — i.e. it would green-light exactly the failure the hook exists to
catch. Because it is a process snapshot, "pulled but never restarted" surfaces
as a mismatch. `tests/test_admin_health.py::test_health_sha_is_a_process_snapshot_not_a_live_tree_read`
pins this.

Consequence worth knowing: on waldhomeserver nothing needs to set
`AOS_BUILD_SHA`. `WorkingDirectory` is the deploy tree, so the git fallback
resolves to the tree's `HEAD` at process start, which after a successful pull
is the pushed sha. Setting the env var would mean writing to `.env` — the file
the destruction guard exists to protect — for no gain.

### 2.2 The hook

Same mechanism, kept deliberately: **pull-in-place** into
`/data/projects/smallfarmsagents` + `systemctl restart sfa-admin`. Added:

1. **ref scoping** — only `refs/heads/main` deploys; a deleted ref is refused.
2. **pre-flight** — project dir is a work tree; `.env` exists and is non-empty
   (`test -s`; the file is never read, echoed, or logged — R-6).
3. **`--ff-only`** on the pull. Still pull-in-place; cannot rewrite or discard
   anything; fails loudly on divergence instead of authoring a merge commit on
   the server. Then asserts post-pull `HEAD == pushed sha`.
4. **restart failure is a failure**, not a warning printed on the way past.
5. **DV-1 verify** — poll `/api/health` (3 s warmup, 10 tries, 2 s apart) and
   compare the *served* `build_sha` to the pushed sha.
6. **exit codes**, never a false zero:

   | code | meaning |
   |---|---|
   | 0 | verified: pushed sha == sha served by the restarted process |
   | 10 | pre-flight failed (no work tree / `.env` missing) — nothing touched |
   | 20 | pull failed or post-pull HEAD != pushed sha — service not restarted |
   | 21 | restart failed |
   | 22 | health unreachable/unparseable after all retries |
   | 23 | health served the wrong sha — **the DV-1 catch** |

**Forbidden, and absent:** `git reset --hard`, `git clean -fdx`, `rm -rf` of the
project dir, delete-and-reclone. The deploy tree holds untracked, unrecoverable
`.env` (0600) and `.venv/` (the interpreter `ExecStart` points at); destroying
them is the capra-mio failure class (34.6 h outage). There is therefore **no
auto-rollback** — rolling back would mean moving the work tree backwards, and
the safe forms of that are a human's call. Every failure path instead prints
the previous sha so a human can forward-fix or fast-forward back deliberately.
The installer (D3) additionally greps a candidate hook for those operations and
refuses to install one that contains them.

## 3. D4 — should `EnvironmentFile=` be softened for SFA?

**Unit as installed (facts pack §5):**
`EnvironmentFile=/data/projects/smallfarmsagents/.env` — no `-` prefix, so
systemd fails the unit if the file is missing or unreadable.

### Verdict: **NO. Keep it hard. Do not add the `-`.**

The reasoning, against this codebase rather than against the general pattern:

**1. Softening would not prevent the crash loop it appears to prevent.**
`organic_market_agent/utils/config.py:11` calls `load_dotenv(_PROJECT_ROOT / ".env")`
itself, and line 17 is `DATABASE_URL: str = os.environ["DATABASE_URL"]` — a bare
subscript evaluated at class-body time, i.e. at import. With `.env` gone,
`EnvironmentFile=-` lets systemd start the process, then the import raises
`KeyError: 'DATABASE_URL'`, the process exits non-zero, and `Restart=always`
restarts it: the same crash loop, just diagnosed from a Python traceback
instead of systemd's unambiguous "Failed to load environment files". Softening
buys nothing here and costs the clearer error message.

**2. If the app ever *did* tolerate a missing `.env`, soft would be worse than
the crash loop, not better.** A process that boots without secrets is a process
that serves — with `ADMIN_SECRET_KEY` falling back to the literal
`dev-secret-change-me` (`admin/__init__.py:46`, session-forging material) and
whatever DB the remaining defaults point at. And it would look *healthy* to the
work in this WP: `/api/health` deliberately avoids the DB, so it would answer
`status: ok` with the correct `build_sha` while the app was functionally dead.
A silent green deploy is precisely the class of failure this WP was opened to
end. The hard form converts that into a loud, correctly-attributed failure.

**3. The capra-mio lesson is about the deleted file, not the unit.** The hard
`EnvironmentFile` was the *amplifier* in that incident; the *cause* was a deploy
mechanism that destroyed an untracked `.env`. Softening treats the amplifier and
leaves the cause. D2 treats the cause: no destructive git operation exists in
the hook, and the `test -s "$ENV_FILE"` pre-flight refuses to restart at all
when `.env` is missing — so the currently-running healthy process keeps serving
and the operator gets exit 10 with a named file, instead of a restarted service
thrashing. That guard makes the hard/soft distinction close to unreachable on
the deploy path, which is the right place to have solved it.

**4. The one real argument for softening does not apply.** systemd's
`EnvironmentFile` parser is stricter than python-dotenv's, so in principle a
`.env` line systemd dislikes could break a unit the app itself would have run
fine. But systemd *warns and skips* malformed lines — only a missing or
unreadable file fails the unit — and the app does not depend on systemd's parse
at all, since `config.py` loads the same file through dotenv. The failure mode
is not reachable through this route.

### What to do instead (recommended, not done here — no server access)

1. **Keep** `EnvironmentFile=/data/projects/smallfarmsagents/.env` as is.
2. **Adopt the hook's `.env` pre-flight** (already in D2) — the actual guard.
3. **Tighten two backup files' permissions.** `.env.bak.202604181511` and
   `.env.bak.20260507_wp007` are `0644`, world-readable, while `.env` and the
   other four backups are `0600` (facts pack §4). `chmod 600` them, or move all
   six out of the deploy tree. Assessed from mode bits only; contents never read.
   Out of this WP's scope — flagged for the conductor.
4. Optional, if a `.env`-missing boot must be survivable later: give `config.py`
   an explicit fail-fast with a readable message rather than `KeyError`, and
   only then reconsider. The unit is the wrong lever.

## 4. Verification performed

- Locked suite: `1 failed, 1010 passed, 88 skipped` — the 1 failure is the known
  pre-existing baseline (`tests/crop_book/test_wp_upload_crop_book.py::test_dispatch_upload_crop_book_profile`),
  +8 passed, zero new failures.
- Hook dry run: 6 scenarios / 12 assertions, all as specified — see the evidence
  file. It executes the real hook artifact with mocked restart + health commands
  against a scratch bare-repo/work-tree pair, so nothing about the deploy path is
  simulated by a re-implementation.
- **Not verified (cannot be, from here):** behaviour against the real
  waldhomeserver deploy tree, the real `sfa-admin` unit, or a real `sudo
  systemctl restart`. AC-B4 ("DV-1 demonstrated failing on the real deploy path
  before PASS") is the conductor's step, and remains open.
