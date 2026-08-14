# Delivery report — SFA-S003-P005-WP001 (pilot arm A)

**Branch:** `pilot/arm-a` (from `main` @ `0d8e8cd`) · **Engine:** Claude Code / claude-opus-5
**Session start:** 2026-08-14T19:11:13Z · **Report written:** 2026-08-14T19:21:44Z

---

## 1. Task

Full DV-1 fix for the SmallFarmsAgents deploy path: make the server-side
post-receive hook prove that the code actually being served is the code that
was pushed, instead of printing `DEPLOY OK (no health check for SFA)`
unconditionally. K=6 deliverables (D1 health endpoint + test, D2 corrected
hook, D3 hub installer block, D4 `sfa-admin.service` assessment, D5 proof of
work, D6 this report). Author-only: the conductor installs server-side.

## 2. Sources checked

| Source | Use |
|---|---|
| `SERVER_FACTS_SFA_DEPLOY_v1.0.0.md` (hub, 2026-08-14) | the only file read outside the repo — current hook §1, reference hook §2, deploy-tree + `.env`/`.venv` hazard §4, unit §5, missing health surface §6, drift §7, push wiring §8 |
| `CLAUDE.md`, `_aos/roadmap.yaml` (WP entry) | session-startup obligations, WP scope + AC-B4 |
| `organic_market_agent/admin/__init__.py`, `admin/auth.py`, `utils/config.py`, `db/session.py` | app-factory shape, auth model, and the D4 evidence (`load_dotenv` + `os.environ["DATABASE_URL"]` at import) |
| `tests/conftest.py`, `tests/test_admin_routes.py` | test fixtures + house conventions |
| live `GET /api/system/health` (AOS API), `validate_aos.sh` | CTX-05 probe (`db.status: online`), startup validation |

No `.env*` file was read, printed, or logged at any point — the hook's guard
uses `test -s` only.

## 3. Produced / missing

**Produced (all committed on `pilot/arm-a`):**

| D | Artifact | Note |
|---|---|---|
| D1 | `organic_market_agent/admin/routes/health.py` | `GET /api/health` → `{status, service, build_sha}`; no auth, no DB |
| D1 | `organic_market_agent/admin/__init__.py` (edited) | registers the blueprint, snapshots the sha at app construction, skips the DB session for health requests |
| D1 | `tests/test_admin_health.py` | 8 tests, incl. the process-snapshot and no-DB guarantees |
| D2 | `scripts/deploy/post-receive.sfa` | sha256 `5dad59dfcdbd8dc5915ec137cf1a29167c55b1e8ad8b49438231ca67de3e306a` |
| D3 | `scripts/deploy/hub_installer_sfa_block.sh` | idempotent, backs up, syntax-checks, refuses destructive hooks |
| D4 | `documentation/05-admin-and-operations/SFA_DEPLOY_DV1.md` §3 | verdict: **do not soften** `EnvironmentFile=` |
| D5 | `scripts/deploy/dryrun_post_receive_sfa.sh` + `evidence/DV1_DRYRUN_post_receive_sfa_2026-08-14.txt` | 6 scenarios / 12 assertions, real output |
| D5 | `evidence/DV1_LOCKED_SUITE_2026-08-14.txt` | locked-suite output |
| D6 | this file | |

**Locked test command** — `1 failed, 1010 passed, 88 skipped, 25 deselected`.
The single failure is the declared pre-existing baseline
(`tests/crop_book/test_wp_upload_crop_book.py::test_dispatch_upload_crop_book_profile`).
**Zero new failures; +8 passed.**

**Missing / not done (deliberate):**

- **AC-B4 — DV-1 demonstrated failing on the real deploy path.** Requires
  server access, which this session does not have. Demonstrated instead against
  a scratch repo pair with mocked restart/health (scenario 2 → exit 23). The
  real-path demonstration is the conductor's step and remains open.
- **Hook installation.** Artifact only, per the WP.
- **D3's diff against the hub installer's *current* SFA block.** The brief said
  that content was in the facts pack; it is not (the pack quotes the two hooks
  and `aos_hub_deploy.sh` lines 1–60, and names `scripts/deploy_server_hooks.sh`
  only inside a comment). With no server access and a one-file read limit
  outside the repo, the block was written standalone and side-effect-free on
  source, with the gap stated in its header. The conductor must reconcile
  house style (log helper, variable prefixes) when pasting.
- **`.env.bak` permission fix** (two world-readable backups, facts pack §4) —
  server-side, out of scope, flagged in §5 below.

## 4. Confidence + assumptions

**High confidence:**
- The health endpoint's semantics. The process-snapshot design is the load-
  bearing decision and is pinned by a test; a per-request `git rev-parse` would
  have made the whole check vacuous (it would report the new sha from a stale
  process).
- Hook control flow. All six paths were executed against the real artifact,
  not a re-implementation — exit codes 0/10/21/22/23 observed directly.
- D4's verdict. It rests on read code (`config.py:11,17`), not on general
  systemd lore: with `.env` gone, soft vs hard both end in a restart loop, and
  soft loses the clearer error.

**Medium confidence:**
- Warmup/retry tuning (3 s + 10 × 2 s ≈ 23 s). Chosen to mirror the reference
  `aos_hub_deploy.sh` shape; SFA's real Flask boot time on waldhomeserver was
  never measured from here. Too short only costs a false exit 22, and both
  numbers are env-overridable.
- Exit-code numbering (10/20/21/22/23). Deliberately *not* the reference
  script's 21/22 (rollback-OK / rollback-failed), because this hook has no
  auto-rollback. If the hub wants one code space across projects, renumber.

**Assumptions (stated, not verified from here):**
1. `sudo systemctl restart sfa-admin` remains passwordless for `nimrodw` — the
   old hook relied on this too, so no new dependency.
2. The deploy tree's `origin` remote still points at the local bare repo
   (facts pack §4) — the hook's `pull origin main` is unchanged from the
   installed hook in this respect.
3. `AOS_BUILD_SHA` is left unset in production, so `build_sha` comes from
   `git rev-parse HEAD` in `WorkingDirectory`. Setting it would require writing
   to `.env` — the file the destruction guard protects — for no gain.
4. `python3` is on the server's PATH for the hook's JSON parse (it is: the unit's
   ExecStart is a python3 path). A `sed` fallback exists regardless.
5. The deploy tree diverging from `origin/main` is a fault, not a workflow —
   hence `--ff-only`. If someone commits *on the server*, the hook now fails
   loudly (exit 20) where the old one authored a merge commit silently.

## 5. Needed now (conductor / team_00)

1. **Install D2 via D3** on `/data/repos/smallfarmsagents.git/hooks/post-receive`,
   ordered so the deploy tree carries `admin/routes/health.py` — either install
   the hook and immediately push this branch's merge to `waldhome`, or push
   first and install after. Installing against the current server tree
   (`987306c`, no health endpoint) makes the next main push exit 22, correctly
   but confusingly.
2. **Server is behind `origin/main` by 1 commit** (facts pack §7, `6277c4d`).
   That commit has never gone through the hook. Expect the first verified deploy
   to carry it.
3. **Run AC-B4 on the real path** — the honest version is to push, then confirm
   exit 0 and the `DEPLOY VERIFIED:` line, and separately to prove the catch
   (e.g. mask the restart so the old process survives → expect exit 23).
4. **`validate_aos.sh` on this spoke reports 4 FAIL, all pre-existing and all
   outside a builder's write authority:**
   - Check 4 — the pilot WP's own `spec_ref` in `_aos/roadmap.yaml` is a hub
     path (`"hub agents-os: _COMMUNICATION/…"`), which cannot resolve
     repo-internally (Iron Rule #3). It fails *because of how this WP was
     entered*, so it is worth fixing at the source.
   - Checks 11 / 13 / 65 — incomplete governance snapshot (on-disk cache 287 vs
     stamp 301; `governance/team_00.md` and 9 other team files missing). Needs
     `aos_sync_all.sh` on the hub side.
   Neither is touched here: `_aos/` is read-only to this team.
5. **Permissions hygiene**, unrelated to this WP but found in the pack:
   `.env.bak.202604181511` and `.env.bak.20260507_wp007` are `0644` while `.env`
   is `0600`.

## 6. Artifact list

```
PILOT_ARM_MEASUREMENT.md                                                  (new)
DELIVERY_REPORT_SFA-S003-P005-WP001.md                                    (new)
organic_market_agent/admin/routes/health.py                               (new)
organic_market_agent/admin/__init__.py                                    (edited)
tests/test_admin_health.py                                               (new)
scripts/deploy/post-receive.sfa                                          (new, 0755)
scripts/deploy/hub_installer_sfa_block.sh                                (new, 0755)
scripts/deploy/dryrun_post_receive_sfa.sh                                (new, 0755)
documentation/05-admin-and-operations/SFA_DEPLOY_DV1.md                  (new)
documentation/05-admin-and-operations/evidence/DV1_DRYRUN_post_receive_sfa_2026-08-14.txt (new)
documentation/05-admin-and-operations/evidence/DV1_LOCKED_SUITE_2026-08-14.txt            (new)
```

## 7. Timestamps

| Event | UTC |
|---|---|
| session start (measurement file) | 2026-08-14T19:11:13Z |
| baseline suite confirmed (1F/1002P/88S) | 2026-08-14T19:13Z |
| D1 tests green | 2026-08-14T19:16Z |
| first full dry run green | 2026-08-14T19:17:07Z |
| evidence dry run captured | 2026-08-14T19:17:35Z |
| installer block tested | 2026-08-14T19:18:41Z |
| locked suite after change (1F/1010P/88S) | 2026-08-14T19:20Z |
| report written | 2026-08-14T19:21:44Z |

## 8. Cost

Single Claude Code session, engine `claude-opus-5`, ~11 minutes wall clock from
first action to report. Roughly 30 tool calls; no sub-agents, no workflows, no
web access, one human interaction (none needed — see `PILOT_ARM_MEASUREMENT.md`).
Token/currency accounting is not exposed to the session, so it is not reported
here rather than estimated.
