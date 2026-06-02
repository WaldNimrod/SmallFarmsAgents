#!/usr/bin/env bash
# sync_ftps_cred.sh — propagate a new uPress FTPS password to waldhomeserver's .env.
#
# Run from the Mac (repo root) after rotating the FTPS password in the uPress
# control panel and updating the Mac .env. Never echoes the secret to stdout.
#
# Configurable via env vars (override defaults below):
#   SERVER_USER      SSH user on waldhomeserver  (default: nimrod)
#   SERVER_HOST      SSH host/alias              (default: waldhomeserver)
#   SERVER_ENV_PATH  path to .env on the server  (default: ~/SmallFarmsAgents/.env)
#   SKIP_VERIFY      set to 1 to skip FTPS login test after update
#
# See: documentation/05-admin-and-operations/FTPS_CRED_ROTATION_SYNC_RUNBOOK.md
set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration (override via env if needed)
# ---------------------------------------------------------------------------
SERVER_USER="${SERVER_USER:-nimrod}"
SERVER_HOST="${SERVER_HOST:-waldhomeserver}"
SERVER_ENV_PATH="${SERVER_ENV_PATH:-~/SmallFarmsAgents/.env}"
SKIP_VERIFY="${SKIP_VERIFY:-0}"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
info()  { echo "[sync_ftps_cred] $*"; }
error() { echo "[sync_ftps_cred] ERROR: $*" >&2; }
die()   { error "$*"; exit 1; }

cleanup_local_tmp() {
  if [ -n "${LOCAL_TMP:-}" ] && [ -f "$LOCAL_TMP" ]; then
    rm -f "$LOCAL_TMP"
    info "local temp file cleaned up"
  fi
}
trap cleanup_local_tmp EXIT

# ---------------------------------------------------------------------------
# Step 1: Prompt for new password (hidden input)
# ---------------------------------------------------------------------------
info "Enter the new uPress FTPS password (input hidden):"
read -rs NEW_PASS
echo  # newline after hidden input
[ -z "$NEW_PASS" ] && die "password cannot be empty"

# ---------------------------------------------------------------------------
# Step 2: Write to local temp file (mode 600, no trailing newline)
# ---------------------------------------------------------------------------
LOCAL_TMP="$(mktemp /tmp/sfa_ftp_pass.XXXXXX)"
chmod 600 "$LOCAL_TMP"
printf '%s' "$NEW_PASS" > "$LOCAL_TMP"
info "temp file created (mode 600): $LOCAL_TMP"

# ---------------------------------------------------------------------------
# Step 3: SCP to server
# ---------------------------------------------------------------------------
REMOTE_TMP="/tmp/sfa_ftp_pass_incoming_$$.tmp"
info "SCP to ${SERVER_USER}@${SERVER_HOST}:${REMOTE_TMP} ..."
scp -q -o StrictHostKeyChecking=accept-new \
    "$LOCAL_TMP" "${SERVER_USER}@${SERVER_HOST}:${REMOTE_TMP}"

# ---------------------------------------------------------------------------
# Step 4: Delete local temp file immediately after SCP
# ---------------------------------------------------------------------------
rm -f "$LOCAL_TMP"
LOCAL_TMP=""  # prevent double-delete by EXIT trap
info "local temp file deleted"

# ---------------------------------------------------------------------------
# Step 5: Server-side — backup, update in-place, cleanup remote temp
# ---------------------------------------------------------------------------
info "Updating server .env ..."
# Pass variables as env; never embed the secret in the remote command string.
# The secret travels only via the already-transferred temp file.
ssh "${SERVER_USER}@${SERVER_HOST}" \
  REMOTE_TMP="$REMOTE_TMP" SERVER_ENV_PATH="$SERVER_ENV_PATH" \
  bash <<'ENDSSH'
set -euo pipefail

ENV_FILE="${SERVER_ENV_PATH/#\~/$HOME}"
[ -f "$ENV_FILE" ] || { echo "ERROR: server .env not found at $ENV_FILE" >&2; exit 1; }

TS="$(date +%Y%m%d_%H%M%S)"
BACKUP="${ENV_FILE}.bak.${TS}_sfa_pass_rotation"

# Backup (mode 600)
cp "$ENV_FILE" "$BACKUP"
chmod 600 "$BACKUP"
echo "[server] backup: $BACKUP"

# Read new password (no trailing newline — printf wrote it that way)
NEW_PASS_VALUE="$(cat "$REMOTE_TMP")"

# Update or append SFA_FTP_PASS
if grep -q '^SFA_FTP_PASS=' "$ENV_FILE"; then
  sed -i.sedbak "s|^SFA_FTP_PASS=.*|SFA_FTP_PASS=${NEW_PASS_VALUE}|" "$ENV_FILE"
  rm -f "${ENV_FILE}.sedbak"
else
  echo "SFA_FTP_PASS=${NEW_PASS_VALUE}" >> "$ENV_FILE"
  echo "[server] WARNING: SFA_FTP_PASS was missing from .env — appended."
fi

# Delete remote temp immediately
rm -f "$REMOTE_TMP"
echo "[server] remote temp deleted, .env updated"
ENDSSH

info "server .env updated"

# ---------------------------------------------------------------------------
# Step 6: Verify FTPS login (unless SKIP_VERIFY=1)
# ---------------------------------------------------------------------------
if [ "$SKIP_VERIFY" = "1" ]; then
  info "SKIP_VERIFY=1 — skipping login test. Run manually:"
  info "  ssh ${SERVER_USER}@${SERVER_HOST} 'source ~/SmallFarmsAgents/.env && lftp ...'"
  exit 0
fi

info "Running FTPS login test on server ..."
VERIFY_RESULT=0
ssh "${SERVER_USER}@${SERVER_HOST}" \
  SERVER_ENV_PATH="$SERVER_ENV_PATH" \
  bash <<'ENDSSH' || VERIFY_RESULT=$?
set -euo pipefail
ENV_FILE="${SERVER_ENV_PATH/#\~/$HOME}"
set -a; source "$ENV_FILE"; set +a
lftp -c "
set ftp:ssl-allow yes
set ftp:ssl-force yes
set ftp:ssl-protect-data yes
set ssl:verify-certificate no
set ftp:passive-mode yes
set net:max-retries 1
set net:timeout 20
open -u \"${SFA_FTP_USER},${SFA_FTP_PASS}\" -p ${SFA_FTP_PORT:-21} ${SFA_FTP_HOST}
ls ${SFA_FTP_ROOT:-/}
bye"
echo "[verify] FTPS login OK"
ENDSSH

if [ "$VERIFY_RESULT" -ne 0 ]; then
  error "FTPS login test FAILED (exit $VERIFY_RESULT). Check the new password and retry."
  error "If the login test shows '530 Login incorrect', the password on uPress may differ"
  error "from what you entered. Restore from the server backup if needed."
  exit 1
fi

info "Done. FTPS credential synced and verified."
info "Run the full deploy from waldhomeserver when ready:"
info "  ssh ${SERVER_USER}@${SERVER_HOST} 'cd ~/SmallFarmsAgents && bash scripts/ftp_deploy_sfa_ui.sh'"
