---
id: HUB_INSTALLER_SFA_BLOCK_SFA-S003-P005-WP001_v1.0.0
type: ARTIFACT
deliverable: D3
wp: SFA-S003-P005-WP001
branch: pilot/arm-b
date: 2026-08-14
audience: hub conductor (installs; the builder has no server access)
---

# D3 — SFA block for the hub installer script

## 0. Source-material gap (stated, not papered over)

The task line says *"current content in the facts pack"*. The facts pack
(`SERVER_FACTS_SFA_DEPLOY_v1.0.0.md`) contains **no hub installer script**. What it
contains is:

- §1 the current SFA `post-receive` **hook** verbatim (what an installer would write);
- §2 the agents-os reference hook plus lines 1–60 of `aos_hub_deploy.sh`, whose header
  names the installer as `scripts/deploy_server_hooks.sh` (S4) — **its body is not quoted
  anywhere in the pack**.

I was constrained to read exactly one file outside this repo, so I did not open
`deploy_server_hooks.sh`. **This block is therefore written against the observable
contract, not against the installer's literal current text**: it is a self-contained,
idempotent, drop-in bash function that assumes only `bash`, `git`, `install`, `sha256sum`
and (optionally) `curl`. **Assumption to confirm at install time:** the installer defines
its per-project blocks as shell functions or `case` arms invoked once per project. If it
instead uses a table-driven template, take the body of `sfa_install_post_receive` below as
the payload and keep the surrounding form.

## 1. Design choice — install by copy, never by heredoc

The hook body lives in the SFA repo at `scripts/deploy/sfa_post_receive.sh` and is
reviewed, diffed and dry-run there (D2/D5). The installer therefore **copies that file**
instead of re-embedding a second copy of the same script inside the installer. A heredoc
copy would create exactly the two-path drift that DV-2 forbids: the installed hook and the
reviewed hook could silently diverge and nothing would notice.

Consequence — **ordering matters**: the deploy tree must already contain
`scripts/deploy/sfa_post_receive.sh` before this block can install it. See §3.

## 2. The block

```bash
# ---------------------------------------------------------------------------
# SFA — smallfarmsagents post-receive (DV-1 verified deploy)
# Replaces the pre-2026-08-14 hook, whose last line was the unconditional
#   echo "DEPLOY OK (no health check for SFA)"
# Source of truth for the hook body: the SFA repo file below — installed by COPY
# so the installed hook and the reviewed hook can never drift (DV-2).
# Destruction guard (R3): this block only writes hooks/post-receive and a backup
# of it. It never touches /data/projects/smallfarmsagents (untracked .env/.venv
# live there — the capra-mio failure class).
# ---------------------------------------------------------------------------
sfa_install_post_receive() {
  local bare="${SFA_BARE:-/data/repos/smallfarmsagents.git}"
  local wt="${SFA_WT:-/data/projects/smallfarmsagents}"
  local src="$wt/scripts/deploy/sfa_post_receive.sh"
  local dst="$bare/hooks/post-receive"
  local ts; ts="$(date -u +%Y%m%dT%H%M%SZ)"

  [ -d "$bare/hooks" ] || { echo "SFA: FAIL — $bare/hooks missing (not a bare repo?)"; return 1; }
  if [ ! -s "$src" ]; then
    echo "SFA: FAIL — $src not present in the deploy tree."
    echo "SFA:        Land SFA-S003-P005-WP001 on main and let the CURRENT hook pull it"
    echo "SFA:        in first, then re-run this installer (see D3 §3 bootstrap order)."
    return 1
  fi

  # Idempotent: identical content -> no write, no backup churn.
  if [ -f "$dst" ] && cmp -s "$src" "$dst"; then
    echo "SFA: post-receive already up to date ($(sha256sum "$dst" | cut -c1-12))"
    return 0
  fi

  if [ -f "$dst" ]; then
    cp -p "$dst" "$dst.bak.$ts" || { echo "SFA: FAIL — could not back up $dst"; return 1; }
    echo "SFA: previous hook backed up -> $dst.bak.$ts"
  fi

  install -m 0755 "$src" "$dst" || { echo "SFA: FAIL — install to $dst failed"; return 1; }
  cmp -s "$src" "$dst" || { echo "SFA: FAIL — installed hook differs from $src"; return 1; }
  echo "SFA: installed $dst (sha256 $(sha256sum "$dst" | cut -c1-12), mode 0755)"

  # Advisory only — never fatal. The hook's own DV-1 leg is the real gate; this
  # just tells the operator up front whether the health surface is live yet.
  if command -v curl >/dev/null 2>&1; then
    local url="${SFA_HEALTH_URL:-http://127.0.0.1:5001/api/health}"
    if curl -fsS --max-time 5 "$url" >/dev/null 2>&1; then
      echo "SFA: health surface reachable at $url"
    else
      echo "SFA: WARN — $url not answering yet. Restart sfa-admin once so the"
      echo "SFA:        health blueprint loads, or the FIRST verified push exits 23."
    fi
  fi
  return 0
}

sfa_install_post_receive || echo "SFA: block FAILED (see messages above)"
# ---------------------------------------------------------------------------
```

## 3. Pre-install precheck + bootstrap order (the one ordering trap)

**Run this precheck first, every time — not just on first install.** Installing the new
hook while the deployed code predates `/api/health` makes the very next push fail on the
health probe (exit 23), even though nothing about that push was wrong. Copy-paste on the
deploy host:

```bash
# SFA pre-install precheck — run BEFORE installing the new hook (§2).
if curl -fsS --max-time 5 http://127.0.0.1:5001/api/health >/dev/null 2>&1; then
  echo "PRECHECK OK — /api/health is live. Safe to run the §2 install block now."
else
  echo "PRECHECK FAIL — /api/health is not answering yet."
  echo "Fix:      sudo systemctl restart sfa-admin"
  echo "Confirm:  curl -fsS http://127.0.0.1:5001/api/health"
  echo "Re-run this precheck until it prints PRECHECK OK, THEN install."
fi
```

Bootstrap order, precheck folded in:

1. Merge this WP to `main` and push to `waldhome`. The **old** hook runs and pulls the
   new files (`scripts/deploy/sfa_post_receive.sh`, the health blueprint) into
   `/data/projects/smallfarmsagents`. It will print `DEPLOY OK (no health check…)` — that
   is expected; nothing is verified yet.
2. Run the precheck above. First install on a tree this old will normally FAIL here — that
   is the expected footgun, not a bug: `sudo systemctl restart sfa-admin` once, then re-run
   the precheck until it prints PRECHECK OK.
3. Run the block in §2. It copies the reviewed hook over the old one (backup kept).
4. The **next** push is the first DV-1-verified deploy.

## 4. AC-B4 — how to demonstrate DV-1 FAILING on the real deploy path

The point is to prove the hook can go red on production wiring, not only in the sandbox.
Non-destructive recipe, no code change:

```bash
# On the server: make the restart a no-op so the tree advances but the PROCESS stays old.
sudo systemctl stop sfa-admin        # nothing is serving the new SHA
# From the Mac:
git push waldhome main
# Expected: the remote output ends with the exit-24 FAIL banner
#   "DV-1 MISMATCH: served build_sha=… but pushed SHA=…"  (or exit 23 if fully down)
sudo systemctl start sfa-admin       # restore, then push again -> DEPLOY VERIFIED
```

**Observed in the D5 dry run and worth knowing before you read the result:** `git push`
itself still exits **0** when a `post-receive` hook fails — git does not un-update the ref
for a post-receive failure. The operator's signals are (a) the `remote:` FAIL banner in
the push output, (b) the same banner in `/data/projects/smallfarmsagents/deploy.log`, and
(c) the hook's own non-zero exit.

**Update — gate round 2 (C2):** a machine-readable green/red at the pusher is no longer a
follow-up; the hook now emits a single `SFA-DEPLOY-STATUS` line on every attempt. See §5.

## 5. Reading the deploy status marker (SFA-DEPLOY-STATUS)

The hook emits exactly one greppable line per deploy attempt, to the pusher's `remote:`
output and to `/data/projects/smallfarmsagents/deploy.log`:

```
SFA-DEPLOY-STATUS: ok sha=<pushed> served=<served> exit=0
SFA-DEPLOY-STATUS: fail reason=<token> sha=<pushed> served=<served-or-unknown> exit=<code>
```

`reason=` tokens (one per failure kind): `deploy-tree-missing`, `env-file-missing`,
`lock-timeout`, `fetch-failed`, `pull-failed`, `head-mismatch`, `restart-failed`,
`health-unreachable`, `dv1-mismatch`. (`lock-timeout` means another deploy was still
holding the pull/restart lock when this push arrived — see the hook header's CONCURRENCY
section; re-push once the other deploy finishes.)

Read it straight from the push:

```bash
git push waldhome main 2>&1 | grep 'SFA-DEPLOY-STATUS'
```

or from the server, after the fact:

```bash
ssh <deploy-host> "grep SFA-DEPLOY-STATUS /data/projects/smallfarmsagents/deploy.log | tail -1"
```

No `SFA-DEPLOY-STATUS` line at all means no deploy was attempted for this push — see §6.

## 6. Ref policy

A push to any ref other than `refs/heads/main` (the deploy branch — `SFA_DEPLOY_BRANCH`,
`main` by default), or a delete of that branch, is an intentional no-op: the hook exits 0
without attempting a deploy and without an `SFA-DEPLOY-STATUS` line. Treat that bare 0 as
"nothing happened," never as a deploy confirmation.

## 7. Tuning the readiness window (config change, not code change)

If `sfa-admin` is ever slow to become healthy after a restart, the wait is already
operator-tunable — no edit to `sfa_post_receive.sh` needed:

- `SFA_DEPLOY_WARMUP` — seconds before the first health probe (default `8`)
- `SFA_DEPLOY_RETRIES` — probe attempts (default `5`)
- `SFA_DEPLOY_RETRY_SLEEP` — seconds between probe attempts (default `3`)

These are read from the hook process's own environment at the moment `git push` invokes
it — set them in the environment that invokes git for the deploy user (e.g. the SSH
session environment for `nimrodw`), never by editing the installed hook body itself, which
would break the byte-identical install guarantee in §1. This section only documents that
the knobs already exist; this correction round does not change any default.
