#!/usr/bin/env bash
# sfa_post_receive.sh — SFA-S003-P005-WP001 (D2)
#
# THIS FILE IS THE HOOK CONTENT. Install verbatim as:
#   /data/repos/smallfarmsagents.git/hooks/post-receive   (mode 0755, owner nimrodw)
# It is kept in-repo so it is reviewable, diffable and dry-runnable (D5) — the
# installed copy must stay byte-identical to this file (the hub installer block,
# D3, is what guarantees that).
#
# New-file justification (R5): `grep -rl "post-receive"` over this repo (excluding
# .git/.venv/_aos) returned zero — there was no existing deploy-hook file to edit.
#
# WHAT IT FIXES
#   The previous hook ended with `echo "DEPLOY OK (no health check for SFA)"`,
#   printed unconditionally after a `git pull` and a restart whose failure was
#   swallowed by `|| echo WARN`. Nothing verified what was actually serving, so a
#   failed restart, a stale process, or an unreachable app all reported DEPLOY OK.
#   This version asserts the SHA the running admin process reports at
#   /api/health equals the SHA that was pushed, and fails LOUD + non-zero
#   otherwise (R4: "a hook exit code, a log line, or a bare HTTP 200 is never
#   sufficient").
#
# WHAT IT DELIBERATELY DOES NOT DO (R3 — capra-mio destruction class)
#   No `git reset --hard`, no `git clean -fdx`, no `rm -rf` of the project dir,
#   no delete-and-reclone. The deploy tree carries UNTRACKED `.env` and `.venv/`
#   (facts pack §4); destroying them is a known multi-hour outage. The pull-in-
#   place mechanism of the previous hook is preserved — only hardened with
#   `--ff-only`, so a divergent tree fails loudly instead of being "fixed"
#   destructively or silently merged.
#
# EXIT CODES (never a false 0)
#   0   deploy verified: served build_sha == pushed SHA
#   20  pre-flight failed BEFORE any mutation (missing deploy tree / env file)
#   21  pull failed, or deploy-tree HEAD != pushed SHA — service NOT restarted
#   22  service restart failed
#   23  health endpoint unreachable or unparseable after all retries
#   24  DV-1 MISMATCH: served build_sha != pushed SHA (the whole point of this hook)
#   Any non-zero leaves the tree as-is; recovery is manual and non-destructive
#   (see the FAIL banner). Auto-rollback is intentionally out of scope for this
#   WP — a safe rollback needs a persisted previous-SHA state dir and an ff-only
#   re-activation path, and inventing one here would add an unverified mutation
#   to the failure path.
#
# ENV OVERRIDES — every default is the REAL production target (facts pack §1/§4/§5/§6).
#   Overrides exist so the dry-run harness exercises THIS code against a scratch
#   sandbox instead of a second, parallel implementation of the same logic (DV-2).
#     SFA_DEPLOY_WT            deploy work tree     (default /data/projects/smallfarmsagents)
#     SFA_DEPLOY_LOG           deploy log           (default $WT/deploy.log)
#     SFA_DEPLOY_REMOTE        remote in $WT        (default origin — the bare repo path)
#     SFA_DEPLOY_BRANCH        branch to deploy     (default main)
#     SFA_DEPLOY_SERVICE       systemd unit         (default sfa-admin)
#     SFA_DEPLOY_RESTART_CMD   full restart command (default: sudo systemctl restart $SERVICE)
#     SFA_DEPLOY_HEALTH_URL    DV-1 probe URL       (default http://127.0.0.1:5001/api/health)
#     SFA_DEPLOY_HEALTH_CMD    full probe command   (default: curl -fsS --max-time 5 $HEALTH_URL)
#     SFA_DEPLOY_ENV_FILE      existence-checked only, NEVER read (default $WT/.env; set
#                              empty to skip the check)
#     SFA_DEPLOY_WARMUP        seconds before first probe   (default 8)
#     SFA_DEPLOY_RETRIES       probe attempts               (default 5)
#     SFA_DEPLOY_RETRY_SLEEP   seconds between attempts     (default 3)
#
# Prerequisites on the server: bash, git, python3, curl, systemctl + sudo.
# Ports opened by this script: none.

set -uo pipefail
unset GIT_DIR
unset GIT_WORK_TREE

WT="${SFA_DEPLOY_WT:-/data/projects/smallfarmsagents}"
LOG="${SFA_DEPLOY_LOG:-$WT/deploy.log}"
REMOTE="${SFA_DEPLOY_REMOTE:-origin}"
BRANCH="${SFA_DEPLOY_BRANCH:-main}"
SERVICE="${SFA_DEPLOY_SERVICE:-sfa-admin}"
RESTART_CMD="${SFA_DEPLOY_RESTART_CMD:-sudo systemctl restart $SERVICE}"
HEALTH_URL="${SFA_DEPLOY_HEALTH_URL:-http://127.0.0.1:5001/api/health}"
HEALTH_CMD="${SFA_DEPLOY_HEALTH_CMD:-curl -fsS --max-time 5 $HEALTH_URL}"
ENV_FILE="${SFA_DEPLOY_ENV_FILE-$WT/.env}"
WARMUP="${SFA_DEPLOY_WARMUP:-8}"
RETRIES="${SFA_DEPLOY_RETRIES:-5}"
RETRY_SLEEP="${SFA_DEPLOY_RETRY_SLEEP:-3}"

ZERO_SHA="0000000000000000000000000000000000000000"

log() {
  printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" | tee -a "$LOG"
}

fail() {
  local code="$1"; shift
  {
    echo "########################################################################"
    echo "### DEPLOY FAILED — SFA — exit $code"
    echo "### $*"
    echo "### The deploy tree was NOT reset, cleaned or re-cloned; untracked"
    echo "### .env / .venv are intact. Recover by hand on the server, then re-push."
    echo "########################################################################"
  } | tee -a "$LOG"
  exit "$code"
}

# Compare a served SHA to the pushed SHA. Equal, or one an unambiguous prefix of
# the other (>= 7 hex chars) — so an AOS_BUILD_SHA stamped short still verifies.
sha_matches() {
  local served="$1" pushed="$2"
  served="$(printf '%s' "$served" | tr 'A-Z' 'a-z')"
  pushed="$(printf '%s' "$pushed" | tr 'A-Z' 'a-z')"
  [ -n "$served" ] || return 1
  [ "$served" = "$pushed" ] && return 0
  if [ "${#served}" -ge 7 ] && [ "${#served}" -lt "${#pushed}" ]; then
    [ "${pushed:0:${#served}}" = "$served" ] && return 0
  fi
  return 1
}

# Extract .build_sha from the health JSON. Prints nothing on unparseable input.
parse_build_sha() {
  python3 -c '
import json,sys
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(1)
sha = d.get("build_sha")
if not isinstance(sha, str) or not sha.strip():
    sys.exit(1)
print(sha.strip())
' 2>/dev/null
}

deploy() {
  local pushed="$1"

  log "post-receive: $BRANCH -> $pushed (DV-1 verified deploy)"

  # ---- pre-flight: nothing is mutated above this line -------------------------
  [ -d "$WT/.git" ] || fail 20 "deploy tree $WT is not a git work tree"
  if [ -n "$ENV_FILE" ] && [ ! -s "$ENV_FILE" ]; then
    # Existence/size only — the file's CONTENT is never read, printed or logged (R2).
    # sfa-admin.service uses a hard `EnvironmentFile=` (no '-'), so starting
    # without this file is a restart loop, not a degraded start. Catch it here,
    # before the restart, while the old process is still serving.
    fail 20 "required env file $ENV_FILE is missing or empty — refusing to restart $SERVICE into a crash loop"
  fi

  # ---- pull in place (non-destructive; --ff-only, never reset/clean/re-clone) --
  if ! git -C "$WT" fetch "$REMOTE" "$BRANCH" 2>&1 | tee -a "$LOG"; then
    fail 21 "git fetch $REMOTE $BRANCH failed"
  fi
  if ! git -C "$WT" pull --ff-only "$REMOTE" "$BRANCH" 2>&1 | tee -a "$LOG"; then
    fail 21 "git pull --ff-only $REMOTE $BRANCH failed (divergent tree? resolve by hand — do NOT reset --hard)"
  fi

  local head
  head="$(git -C "$WT" rev-parse HEAD 2>/dev/null)"
  if [ "$head" != "$pushed" ]; then
    fail 21 "deploy tree HEAD ($head) != pushed SHA ($pushed) after pull — service NOT restarted"
  fi
  log "pull OK: $WT HEAD = $head"

  # ---- restart ---------------------------------------------------------------
  log "restarting $SERVICE: $RESTART_CMD"
  if ! eval "$RESTART_CMD" 2>&1 | tee -a "$LOG"; then
    fail 22 "restart failed ($RESTART_CMD) — the previously running process may still be serving OLD code"
  fi

  # ---- DV-1: what is ACTUALLY serving? ---------------------------------------
  log "health warmup ${WARMUP}s, then probing $HEALTH_URL (up to $RETRIES attempts, ${RETRY_SLEEP}s apart)"
  sleep "$WARMUP"

  local attempt=1 body="" served=""
  while [ "$attempt" -le "$RETRIES" ]; do
    body="$(eval "$HEALTH_CMD" 2>/dev/null)"
    if [ -n "$body" ]; then
      served="$(printf '%s' "$body" | parse_build_sha)"
      [ -n "$served" ] && break
    fi
    log "health attempt $attempt/$RETRIES: no usable build_sha yet"
    served=""
    attempt=$((attempt + 1))
    [ "$attempt" -le "$RETRIES" ] && sleep "$RETRY_SLEEP"
  done

  if [ -z "$served" ]; then
    fail 23 "health endpoint $HEALTH_URL unreachable or returned no build_sha after $RETRIES attempts — $SERVICE is NOT verified up"
  fi

  if ! sha_matches "$served" "$pushed"; then
    fail 24 "DV-1 MISMATCH: served build_sha=$served but pushed SHA=$pushed — $SERVICE is serving OTHER code than you pushed (restart did not take effect, or the process is stale)"
  fi

  log "DEPLOY VERIFIED: $SERVICE serves build_sha=$served == pushed $pushed (probe: $HEALTH_URL)"
  exit 0
}

# Ref-scoped, like the agents-os reference hook: a push to any other ref is a
# no-op instead of an unconditional `git pull origin main`.
while read -r _old new ref; do
  if [ "$ref" = "refs/heads/$BRANCH" ]; then
    if [ "$new" = "$ZERO_SHA" ]; then
      log "post-receive: refs/heads/$BRANCH DELETED — no deploy performed"
      exit 0
    fi
    deploy "$new"
  else
    log "post-receive: ignoring $ref (only refs/heads/$BRANCH deploys)"
  fi
done

exit 0
