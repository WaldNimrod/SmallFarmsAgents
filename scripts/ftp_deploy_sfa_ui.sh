#!/usr/bin/env bash
# ftp_deploy_sfa_ui.sh — deploy the sfa_delivery UI to sfa.nimrod.bio over FTPS.
#
# Strategy: Option B (team_00 ruling 2026-05-28) — vendor/ stays gitignored;
# this script runs `composer install --no-dev` before the lftp mirror so the
# upload always carries a complete vendor/ tree. Never deploy a worktree whose
# vendor/ was produced by a stale `composer install` — re-run is cheap.
#
# Env (from ./.env, see .env.example lines 75-87):
#   SFA_FTP_HOST  SFA_FTP_PORT  SFA_FTP_USER  SFA_FTP_PASS  SFA_FTP_ROOT
# Optional:
#   ENV_FILE          path to env file (default ./.env)
#   SFA_DELIVERY_SRC  source tree to mirror (default ./sfa_delivery)
set -euo pipefail

ENV_FILE="${ENV_FILE:-./.env}"
if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: env file '$ENV_FILE' not found (set ENV_FILE=...)." >&2
  exit 1
fi
set -a; source "$ENV_FILE"; set +a

SRC="${SFA_DELIVERY_SRC:-./sfa_delivery}"
REMOTE_ROOT="${SFA_FTP_ROOT:-/}"

: "${SFA_FTP_HOST:?SFA_FTP_HOST must be set in $ENV_FILE}"
: "${SFA_FTP_USER:?SFA_FTP_USER must be set in $ENV_FILE}"
: "${SFA_FTP_PASS:?SFA_FTP_PASS must be set in $ENV_FILE}"
FTP_PORT="${SFA_FTP_PORT:-21}"

if [ ! -d "$SRC" ]; then
  echo "ERROR: source '$SRC' not found." >&2
  exit 1
fi

# Option B: ensure a fresh production vendor/ tree before upload.
if command -v composer >/dev/null 2>&1; then
  echo "[deploy] composer install --no-dev (optimized autoloader)..."
  composer install --no-dev --optimize-autoloader --working-dir="$SRC"
else
  echo "[deploy] composer not on PATH — skipping install; verifying existing vendor/." >&2
fi

if [ ! -d "$SRC/vendor" ]; then
  echo "ERROR: $SRC/vendor missing. Install composer and re-run, or run 'composer install --no-dev' in $SRC first." >&2
  exit 1
fi

echo "[deploy] mirroring $SRC -> ${SFA_FTP_HOST}:${REMOTE_ROOT}"
cd "$SRC"
lftp -c "
set ftp:ssl-allow yes
set ssl:verify-certificate no
set ftp:ssl-protect-data yes
set ftp:passive-mode yes
set ftp:ssl-force yes
set net:max-retries 3
set net:timeout 30
open -u \"${SFA_FTP_USER},${SFA_FTP_PASS}\" -p ${FTP_PORT} ${SFA_FTP_HOST}
mirror -R --delete --verbose=1 --parallel=3 \
  --exclude-glob '.env' \
  --exclude-glob '.env.*' \
  --exclude-glob '.git*' \
  --exclude '^logs/' \
  --exclude '^tests/' \
  --exclude-glob '.DS_Store' \
  --exclude-glob '*.pyc' \
  --exclude '^__pycache__/' \
  ./ ${REMOTE_ROOT}
bye"

echo "[deploy] complete — smoke https://sfa.nimrod.bio/ next"
