#!/usr/bin/env bash
# dryrun_post_receive_sfa.sh — exercise scripts/deploy/post-receive.sfa end to
# end against a scratch repo pair with a mocked health endpoint.
#
# WP: SFA-S003-P005-WP001 (D5 proof of work).
#
# This runs THE REAL HOOK FILE — the same bytes proposed for installation on
# waldhomeserver — with its env overrides pointed at a throwaway bare repo +
# work tree under $TMPDIR. Nothing here re-implements the hook's control flow,
# so a green run is evidence about the artifact, not about a stunt double.
# Nothing touches the server, the real deploy tree, or any real .env.
#
# Six scenarios, each asserting an exact exit code:
#   1 HAPPY        health serves the pushed sha            -> 0
#   2 STALE        health serves the PREVIOUS sha          -> 23  (the DV-1 catch)
#   3 DOWN         health endpoint unreachable             -> 22
#   4 RESTART_FAIL restart command fails                   -> 21
#   5 WRONG_REF    push to a non-deploy ref                -> 0, tree untouched
#   6 NO_ENV       .env missing                            -> 10, tree untouched
#
# Scenarios 1, 5 and 6 additionally assert that untracked files (.env, a .venv
# marker) survive the run — the capra-mio destruction guard.
#
# Usage: bash scripts/deploy/dryrun_post_receive_sfa.sh

set -uo pipefail

HOOK="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/post-receive.sfa"
ROOT="$(mktemp -d "${TMPDIR:-/tmp}/sfa-dryrun-XXXXXX")"
trap 'rm -rf "$ROOT"' EXIT

PASS=0
FAIL=0

banner() { printf '\n=== %s ===\n' "$*"; }

# Rebuild a pristine fixture: bare repo whose main is one commit AHEAD of the
# deploy tree, exactly like the server after a push.
build_fixture() {
  rm -rf "$ROOT/bare.git" "$ROOT/src" "$ROOT/project"
  git init -q --bare -b main "$ROOT/bare.git"
  git init -q -b main "$ROOT/src"
  git -C "$ROOT/src" config user.email dryrun@local
  git -C "$ROOT/src" config user.name dryrun
  echo v1 > "$ROOT/src/app.txt"
  git -C "$ROOT/src" add -A
  git -C "$ROOT/src" commit -qm "commit A"
  git -C "$ROOT/src" remote add origin "$ROOT/bare.git"
  git -C "$ROOT/src" push -q origin main
  git clone -q "$ROOT/bare.git" "$ROOT/project"
  git -C "$ROOT/project" config user.email dryrun@local
  git -C "$ROOT/project" config user.name dryrun

  # Untracked, unrecoverable state — the files the capra-mio incident destroyed.
  printf '# dry-run placeholder, no secrets\n' > "$ROOT/project/.env"
  mkdir -p "$ROOT/project/.venv"
  printf 'venv marker\n' > "$ROOT/project/.venv/marker"

  echo v2 > "$ROOT/src/app.txt"
  git -C "$ROOT/src" commit -qam "commit B"
  git -C "$ROOT/src" push -q origin main

  SHA_A="$(git -C "$ROOT/project" rev-parse HEAD)"
  SHA_B="$(git -C "$ROOT/bare.git" rev-parse main)"
  : > "$ROOT/deploy.log"
}

# run_hook <ref> <health-cmd> <restart-cmd>
run_hook() {
  local ref="$1" health_cmd="$2" restart_cmd="$3"
  SFA_DEPLOY_PROJECT_DIR="$ROOT/project" \
  SFA_DEPLOY_LOG="$ROOT/deploy.log" \
  SFA_DEPLOY_SERVICE="sfa-admin-dryrun" \
  SFA_DEPLOY_RESTART_CMD="$restart_cmd" \
  SFA_DEPLOY_HEALTH_CMD="$health_cmd" \
  SFA_DEPLOY_HEALTH_URL="http://127.0.0.1:5001/api/health (mocked)" \
  SFA_DEPLOY_WARMUP=0 \
  SFA_DEPLOY_HEALTH_RETRIES=2 \
  SFA_DEPLOY_HEALTH_INTERVAL=0 \
    bash "$HOOK" <<< "$SHA_A $SHA_B $ref"
}

check() {
  # check <label> <expected> <actual>
  if [ "$2" = "$3" ]; then
    echo "  [PASS] $1: $3"
    PASS=$((PASS + 1))
  else
    echo "  [FAIL] $1: expected $2, got $3"
    FAIL=$((FAIL + 1))
  fi
}

assert_untracked_survived() {
  local ok=yes
  [ -s "$ROOT/project/.env" ] || ok=no
  [ -s "$ROOT/project/.venv/marker" ] || ok=no
  check "untracked .env + .venv survived" yes "$ok"
}

echo "hook under test : $HOOK"
echo "hook sha256     : $( (shasum -a 256 "$HOOK" 2>/dev/null || sha256sum "$HOOK") | awk '{print $1}')"
echo "scratch root    : $ROOT"
echo "git             : $(git --version)"
echo "date (utc)      : $(date -u +%FT%TZ)"

# ---------------------------------------------------------------- 1. HAPPY
banner "SCENARIO 1 — HAPPY PATH (health serves the pushed sha)"
build_fixture
echo "pushed sha = $SHA_B / previous = $SHA_A"
run_hook refs/heads/main "printf {\"status\":\"ok\",\"service\":\"sfa-admin\",\"build_sha\":\"$SHA_B\"}" true
check "exit code" 0 "$?"
check "deploy tree advanced to pushed sha" "$SHA_B" "$(git -C "$ROOT/project" rev-parse HEAD)"
assert_untracked_survived

# ---------------------------------------------------------------- 2. STALE
banner "SCENARIO 2 — STALE PROCESS (restart silently did not take effect)"
build_fixture
run_hook refs/heads/main "printf {\"status\":\"ok\",\"service\":\"sfa-admin\",\"build_sha\":\"$SHA_A\"}" true
check "exit code" 23 "$?"

# ---------------------------------------------------------------- 3. DOWN
banner "SCENARIO 3 — HEALTH ENDPOINT DOWN"
build_fixture
run_hook refs/heads/main false true
check "exit code" 22 "$?"

# ---------------------------------------------------------- 4. RESTART_FAIL
banner "SCENARIO 4 — RESTART COMMAND FAILS"
build_fixture
run_hook refs/heads/main "printf {\"build_sha\":\"$SHA_B\"}" false
check "exit code" 21 "$?"

# ------------------------------------------------------------- 5. WRONG_REF
banner "SCENARIO 5 — PUSH TO A NON-DEPLOY REF (must be a no-op)"
build_fixture
run_hook refs/heads/some-feature "printf {\"build_sha\":\"$SHA_B\"}" true
check "exit code" 0 "$?"
check "deploy tree NOT moved" "$SHA_A" "$(git -C "$ROOT/project" rev-parse HEAD)"
assert_untracked_survived

# ---------------------------------------------------------------- 6. NO_ENV
banner "SCENARIO 6 — .env MISSING (must refuse before restarting)"
build_fixture
rm -f "$ROOT/project/.env"
run_hook refs/heads/main "printf {\"build_sha\":\"$SHA_B\"}" true
check "exit code" 10 "$?"
check "deploy tree NOT moved" "$SHA_A" "$(git -C "$ROOT/project" rev-parse HEAD)"
check ".venv untouched" yes "$([ -s "$ROOT/project/.venv/marker" ] && echo yes || echo no)"

banner "RESULT"
echo "checks passed : $PASS"
echo "checks failed : $FAIL"
[ "$FAIL" -eq 0 ] && echo "DRY RUN: ALL SCENARIOS BEHAVED AS SPECIFIED" || echo "DRY RUN: FAILURES PRESENT"
exit "$([ "$FAIL" -eq 0 ] && echo 0 || echo 1)"
