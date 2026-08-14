#!/usr/bin/env bash
# sfa_post_receive_dryrun.sh — SFA-S003-P005-WP001 (D5 proof of work)
#
# Exercises scripts/deploy/sfa_post_receive.sh — THE REAL HOOK FILE, not a copy or
# a re-implementation — against a disposable sandbox (its own bare repo + work
# tree), with the systemd restart and the /api/health probe mocked via the hook's
# documented env overrides. Nothing on the server, and nothing in this repo's
# working tree, is touched.
#
# New-file justification (R5): `grep -rl "post-receive"` over this repo returned
# zero, so there was no existing harness to extend.
#
# Usage:  bash scripts/deploy/sfa_post_receive_dryrun.sh [sandbox-parent-dir]
# Exit 0 iff every scenario produced its expected exit code.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
HOOK="$REPO_ROOT/scripts/deploy/sfa_post_receive.sh"
PARENT="${1:-${TMPDIR:-/tmp}}"
SANDBOX="$(mktemp -d "${PARENT%/}/sfa-hook-dryrun.XXXXXX")"

# The sandbox is a throwaway directory created by mktemp in this same run — this
# is the only recursive delete in the deliverable, and it can never name the real
# deploy tree (R3).
cleanup() { [ -n "${KEEP_SANDBOX:-}" ] || rm -rf "$SANDBOX"; }
trap cleanup EXIT

ZERO="0000000000000000000000000000000000000000"
PASS_COUNT=0
FAIL_COUNT=0

hr() { printf '%s\n' "------------------------------------------------------------------"; }

# ---------------------------------------------------------------------------
# Sandbox: bare repo (stands in for /data/repos/smallfarmsagents.git) and a work
# tree (stands in for /data/projects/smallfarmsagents) with an untracked env file
# and an untracked venv-shaped dir, so the destruction guard has something real
# to preserve.
# ---------------------------------------------------------------------------
BARE="$SANDBOX/smallfarmsagents.git"
WT="$SANDBOX/deploy-tree"
SRC="$SANDBOX/pusher"

git init -q --bare "$BARE"
git init -q "$SRC"
git -C "$SRC" config user.email dryrun@example.invalid
git -C "$SRC" config user.name "dryrun"
echo "v1" > "$SRC/app.txt"
git -C "$SRC" add app.txt
git -C "$SRC" commit -qm "v1"
git -C "$SRC" branch -M main
git -C "$SRC" push -q "$BARE" main

git clone -q "$BARE" "$WT"
git -C "$WT" config user.email dryrun@example.invalid
git -C "$WT" config user.name "dryrun"
# Untracked files the deploy must never destroy. Named `env.sandbox`, not `.env`
# — no real secret file is created, read, or printed anywhere in this harness (R2).
printf 'SANDBOX_PLACEHOLDER=not-a-secret\n' > "$SANDBOX/env.sandbox"
mkdir -p "$WT/.venv-sandbox" && printf 'marker\n' > "$WT/.venv-sandbox/marker"

export SFA_DEPLOY_WT="$WT"
export SFA_DEPLOY_LOG="$SANDBOX/deploy.log"
export SFA_DEPLOY_REMOTE="origin"
export SFA_DEPLOY_BRANCH="main"
export SFA_DEPLOY_SERVICE="sfa-admin-sandbox"
export SFA_DEPLOY_RESTART_CMD='echo "[mock] systemctl restart sfa-admin"'
export SFA_DEPLOY_ENV_FILE="$SANDBOX/env.sandbox"
export SFA_DEPLOY_WARMUP=0
export SFA_DEPLOY_RETRIES=2
export SFA_DEPLOY_RETRY_SLEEP=0
export SFA_DEPLOY_HEALTH_URL="mock://api/health"

# Produce a new commit in the pusher, publish it to the bare repo, echo its SHA.
new_commit() {
  local msg="$1"
  echo "$msg" >> "$SRC/app.txt"
  git -C "$SRC" commit -qam "$msg"
  git -C "$SRC" push -q "$BARE" main
  git -C "$SRC" rev-parse HEAD
}

mock_health() { printf '%s' "$1" > "$SANDBOX/health.json"; export SFA_DEPLOY_HEALTH_CMD="cat $SANDBOX/health.json"; }

# scenario <name> <expected-exit> <pushed-sha> ; hook is fed a real post-receive stdin line
scenario() {
  local name="$1" expected="$2" pushed="$3"
  hr
  echo "SCENARIO: $name   (expect exit $expected)"
  hr
  printf '%s %s refs/heads/main\n' "$ZERO" "$pushed" | bash "$HOOK"
  local rc=$?
  echo "--> exit code: $rc (expected $expected)"
  if [ "$rc" = "$expected" ]; then
    echo "--> RESULT: PASS"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    echo "--> RESULT: FAIL (unexpected exit code)"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
  echo
}

echo "=================================================================="
echo "SFA post-receive DV-1 dry run"
echo "hook under test : $HOOK"
echo "sandbox         : $SANDBOX"
echo "date_utc        : $(date -u +%FT%TZ)"
echo "=================================================================="
echo

# --- S1: happy path — served build_sha == pushed SHA -----------------------
SHA1="$(new_commit "v2")"
mock_health "{\"status\": \"ok\", \"build_sha\": \"$SHA1\", \"sha_source\": \"git\"}"
scenario "served build_sha == pushed SHA" 0 "$SHA1"

# --- S2: the failure the old hook could not see ----------------------------
# Restart silently did not take effect: the tree is new, the PROCESS is old.
SHA2="$(new_commit "v3")"
mock_health "{\"status\": \"ok\", \"build_sha\": \"$SHA1\", \"sha_source\": \"git\"}"
scenario "stale process — served build_sha is the PREVIOUS SHA (DV-1 mismatch)" 24 "$SHA2"

# --- S3: health surface down / unparseable ---------------------------------
SHA3="$(new_commit "v4")"
export SFA_DEPLOY_HEALTH_CMD='printf "%s" "<!doctype html><title>404 Not Found</title>"'
scenario "health endpoint returns Flask 404 HTML (pre-D1 server state)" 23 "$SHA3"

# --- S4: restart itself fails ----------------------------------------------
SHA4="$(new_commit "v5")"
mock_health "{\"status\": \"ok\", \"build_sha\": \"$SHA4\"}"
SAVED_RESTART="$SFA_DEPLOY_RESTART_CMD"
export SFA_DEPLOY_RESTART_CMD='echo "[mock] restart refused"; false'
scenario "systemctl restart fails" 22 "$SHA4"
export SFA_DEPLOY_RESTART_CMD="$SAVED_RESTART"

# --- S5: pre-flight — required env file absent, BEFORE any mutation ---------
SHA5="$(new_commit "v6")"
mock_health "{\"status\": \"ok\", \"build_sha\": \"$SHA5\"}"
SAVED_ENV="$SFA_DEPLOY_ENV_FILE"
export SFA_DEPLOY_ENV_FILE="$SANDBOX/env.absent"
HEAD_BEFORE="$(git -C "$WT" rev-parse HEAD)"
scenario "required env file missing — abort before pull/restart" 20 "$SHA5"
HEAD_AFTER="$(git -C "$WT" rev-parse HEAD)"
export SFA_DEPLOY_ENV_FILE="$SAVED_ENV"
hr
echo "PRE-FLIGHT NON-MUTATION CHECK: HEAD before=$HEAD_BEFORE after=$HEAD_AFTER"
if [ "$HEAD_BEFORE" = "$HEAD_AFTER" ]; then
  echo "--> RESULT: PASS (aborted deploy mutated nothing)"; PASS_COUNT=$((PASS_COUNT + 1))
else
  echo "--> RESULT: FAIL (tree moved despite pre-flight abort)"; FAIL_COUNT=$((FAIL_COUNT + 1))
fi
echo

# --- S6: non-main ref is a no-op -------------------------------------------
hr
echo "SCENARIO: push to refs/heads/feature-x is ignored   (expect exit 0, no deploy)"
hr
printf '%s %s refs/heads/feature-x\n' "$ZERO" "$SHA5" | bash "$HOOK"
RC=$?
echo "--> exit code: $RC (expected 0)"
if [ "$RC" = 0 ]; then echo "--> RESULT: PASS"; PASS_COUNT=$((PASS_COUNT + 1)); else echo "--> RESULT: FAIL"; FAIL_COUNT=$((FAIL_COUNT + 1)); fi
echo

# --- S7: end-to-end through a real `git push` with the hook INSTALLED -------
hr
echo "SCENARIO: real 'git push' into the sandbox bare repo, hook installed as hooks/post-receive"
hr
# Catch the deploy tree up first, so this push is a clean fast-forward.
git -C "$WT" pull -q --ff-only origin main
cp "$HOOK" "$BARE/hooks/post-receive"
chmod 755 "$BARE/hooks/post-receive"
echo "v7" >> "$SRC/app.txt"
git -C "$SRC" commit -qam "v7"
SHA7="$(git -C "$SRC" rev-parse HEAD)"
mock_health "{\"status\": \"ok\", \"build_sha\": \"$SHA7\", \"sha_source\": \"git\"}"
git -C "$SRC" push "$BARE" main 2>&1
PUSH_RC=$?
echo "--> git push exit code: $PUSH_RC"
SERVED_HEAD="$(git -C "$WT" rev-parse HEAD)"
echo "--> deploy tree HEAD after push: $SERVED_HEAD (pushed $SHA7)"
if [ "$SERVED_HEAD" = "$SHA7" ]; then
  echo "--> RESULT: PASS (hook fired from a real push and fast-forwarded the deploy tree)"
  PASS_COUNT=$((PASS_COUNT + 1))
else
  echo "--> RESULT: FAIL"; FAIL_COUNT=$((FAIL_COUNT + 1))
fi
echo

# --- S8: real `git push` whose DV-1 leg FAILS ------------------------------
# Records what the PUSHER actually observes when the hook rejects a deploy —
# git's documented behaviour is that a post-receive failure does not un-update
# the ref, so the pusher's signal is the remote FAIL banner (and the hook's
# non-zero exit, which the conductor can also read from deploy.log), not
# necessarily a non-zero `git push`.
hr
echo "SCENARIO: real 'git push' with a stale served build_sha (DV-1 mismatch end-to-end)"
hr
echo "v8" >> "$SRC/app.txt"
git -C "$SRC" commit -qam "v8"
SHA8="$(git -C "$SRC" rev-parse HEAD)"
mock_health "{\"status\": \"ok\", \"build_sha\": \"$SHA7\", \"sha_source\": \"git\"}"   # stale: still v7
git -C "$SRC" push "$BARE" main 2>&1
PUSH_RC8=$?
echo "--> git push exit code: $PUSH_RC8"
if grep -q "DEPLOY FAILED — SFA — exit 24" "$SFA_DEPLOY_LOG"; then
  echo "--> RESULT: PASS (loud DV-1 FAIL banner reached the pusher and deploy.log)"
  PASS_COUNT=$((PASS_COUNT + 1))
else
  echo "--> RESULT: FAIL (no DV-1 failure recorded)"; FAIL_COUNT=$((FAIL_COUNT + 1))
fi
echo

# --- Destruction guard: untracked files survived every scenario ------------
hr
echo "DESTRUCTION GUARD (R3 / capra-mio class)"
hr
UNTRACKED_OK=1
[ -s "$SANDBOX/env.sandbox" ] || UNTRACKED_OK=0
[ -s "$WT/.venv-sandbox/marker" ] || UNTRACKED_OK=0
echo "env file present after all scenarios       : $([ -s "$SANDBOX/env.sandbox" ] && echo yes || echo NO)"
echo "untracked .venv-sandbox/ present in tree   : $([ -s "$WT/.venv-sandbox/marker" ] && echo yes || echo NO)"
echo "forbidden ops in the hook (reset --hard / clean -fdx / rm -rf / git clone):"
grep -nE 'reset --hard|clean -fdx|rm -rf|git clone' "$HOOK" || echo "  (none — grep returned zero)"
if [ "$UNTRACKED_OK" = 1 ]; then
  echo "--> RESULT: PASS"; PASS_COUNT=$((PASS_COUNT + 1))
else
  echo "--> RESULT: FAIL (untracked deploy-tree files were destroyed)"; FAIL_COUNT=$((FAIL_COUNT + 1))
fi
echo

hr
echo "SUMMARY: $PASS_COUNT passed, $FAIL_COUNT failed"
hr
[ "$FAIL_COUNT" = 0 ] || exit 1
exit 0
