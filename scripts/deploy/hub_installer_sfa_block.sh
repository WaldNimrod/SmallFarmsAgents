#!/usr/bin/env bash
# hub_installer_sfa_block.sh — the SFA block for the hub's server-hook installer.
#
# WP: SFA-S003-P005-WP001 (D3). Arm A deliverable.
# Installation is performed by the hub conductor, NOT by this repo and NOT by
# the authoring session. This file is the artifact to lift into
# agents-os `scripts/deploy_server_hooks.sh` (or to run standalone on
# waldhomeserver with `bash hub_installer_sfa_block.sh`).
#
# ⚠ SOURCING GAP — READ BEFORE MERGING INTO THE HUB INSTALLER
# ------------------------------------------------------------
# The task brief said the installer's current SFA block content was in the
# facts pack. It is not: SERVER_FACTS_SFA_DEPLOY_v1.0.0.md quotes the two
# post-receive hooks (§1, §2) and lines 1–60 of aos_hub_deploy.sh, and mentions
# `scripts/deploy_server_hooks.sh` only inside that header comment (S4). The
# installer's own text was never captured, and this session had no server
# access and no read access outside the one permitted file, so the existing
# block could not be diffed. This block is therefore written STANDALONE and
# side-effect-free at source time: it defines `sfa_install_post_receive_hook`
# and only runs it when executed directly. Dropping it into the hub installer
# is a paste + one call, and the conductor should reconcile naming/logging
# conventions with the surrounding blocks (variable prefixes, log helper) —
# the semantics below are the deliverable, the house style is not verified.
#
# WHAT IT DOES
#   1. resolves the hook source (default: the tracked copy in the deploy tree)
#   2. syntax-checks it (`bash -n`) before it can ever fire
#   3. backs up the currently installed hook, timestamped, never overwriting
#   4. installs it 0755 and verifies byte identity by checksum
#   5. is idempotent — a second run with identical content is a no-op
#
# WHAT IT DOES NOT DO (capra-mio destruction guard, DEC-2026-08-13-4)
#   Never touches /data/projects/smallfarmsagents: no reset --hard, no
#   clean -fdx, no rm -rf, no re-clone, no .env or .venv handling of any kind.
#   It writes exactly one file, inside the BARE repo's hooks/ directory.
#
# ORDERING NOTE (important): the new hook verifies that the restarted service
# serves the pushed sha via GET /api/health. That endpoint only exists from
# commit-with-D1 onward. Install the hook and then push the commit that carries
# organic_market_agent/admin/routes/health.py — or push it first and install
# after. Installing it while the deploy tree predates the endpoint means the
# next main push exits 22 (health unusable), correctly, but confusingly.

set -uo pipefail

SFA_BARE_REPO="${SFA_BARE_REPO:-/data/repos/smallfarmsagents.git}"
SFA_PROJECT_DIR="${SFA_PROJECT_DIR:-/data/projects/smallfarmsagents}"
SFA_HOOK_SRC="${SFA_HOOK_SRC:-$SFA_PROJECT_DIR/scripts/deploy/post-receive.sfa}"

sfa_log() { echo "[sfa-hook] $*"; }

sfa_sha256() {
  if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | awk '{print $1}';
  else shasum -a 256 "$1" | awk '{print $1}'; fi
}

sfa_install_post_receive_hook() {
  local bare="$SFA_BARE_REPO"
  local src="$SFA_HOOK_SRC"
  local dst="$bare/hooks/post-receive"
  local stamp backup

  if [ ! -d "$bare" ]; then
    sfa_log "FAIL: bare repo not found: $bare"
    return 1
  fi
  if [ ! -f "$src" ]; then
    sfa_log "FAIL: hook source not found: $src"
    sfa_log "      (set SFA_HOOK_SRC to the arm checkout's scripts/deploy/post-receive.sfa"
    sfa_log "       if the deploy tree does not carry it yet)"
    return 1
  fi
  if ! bash -n "$src"; then
    sfa_log "FAIL: $src does not parse — refusing to install a broken hook"
    return 1
  fi

  # Refuse to install a hook containing the forbidden destructive operations,
  # whatever its provenance. Cheap, and it makes the guard mechanical.
  # Comments are stripped first — the approved hook *documents* the ban in its
  # own header, and that prose must not trip the check.
  if sed 's/#.*//' "$src" \
     | grep -Eq 'reset[[:space:]]+--hard|clean[[:space:]]+-[a-z]*f[a-z]*d|rm[[:space:]]+-rf[[:space:]]+"?\$?\{?(SFA_)?PROJECT_DIR|git[[:space:]]+clone'; then
    sfa_log "FAIL: $src contains a forbidden destructive operation (reset --hard / clean -fd / rm -rf project / clone)"
    return 1
  fi

  if [ -f "$dst" ] && [ "$(sfa_sha256 "$src")" = "$(sfa_sha256 "$dst")" ]; then
    sfa_log "already installed and identical — no-op ($dst)"
    return 0
  fi

  if [ -f "$dst" ]; then
    stamp="$(date -u +%Y%m%dT%H%M%SZ)"
    backup="$dst.bak.$stamp"
    if ! cp -p "$dst" "$backup"; then
      sfa_log "FAIL: could not back up existing hook to $backup"
      return 1
    fi
    sfa_log "backed up previous hook -> $backup"
  else
    sfa_log "no existing post-receive hook (fresh install)"
  fi

  if ! install -m 0755 "$src" "$dst"; then
    sfa_log "FAIL: could not write $dst"
    return 1
  fi

  if [ "$(sfa_sha256 "$src")" != "$(sfa_sha256 "$dst")" ]; then
    sfa_log "FAIL: post-install checksum mismatch on $dst"
    return 1
  fi

  sfa_log "installed $dst (mode $(ls -l "$dst" | awk '{print $1}'), sha256 $(sfa_sha256 "$dst"))"
  sfa_log "verify next deploy with: tail -f $SFA_PROJECT_DIR/deploy.log"
  sfa_log "expected success line: 'DEPLOY VERIFIED: sfa-admin is serving build_sha=<sha> == pushed <sha>'"
  return 0
}

# Only self-execute when run directly; sourcing into the hub installer defines
# the function and does nothing else.
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  sfa_install_post_receive_hook
  exit $?
fi
