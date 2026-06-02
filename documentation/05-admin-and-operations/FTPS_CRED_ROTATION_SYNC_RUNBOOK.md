# FTPS Credential Rotation & Sync Runbook

**Scope:** Keeping `SFA_FTP_PASS` (uPress FTPS password) in sync between the
Mac development workstation and waldhomeserver after a uPress password rotation.

**Related:** [UI Deploy Runbook](./UI_DEPLOY_RUNBOOK.md)

---

## 1. Why this matters

The SFA deploy topology has two hosts that each hold a `.env` file with the
uPress FTPS credentials:

| Host | Role |
|------|------|
| **Mac (dev workstation)** | Where the developer sets/tests configuration |
| **waldhomeserver (deploy relay)** | Where `bash scripts/ftp_deploy_sfa_ui.sh` actually runs |

Only waldhomeserver's egress IP is allowlisted by uPress for port-21 FTPS
access. The Mac's Bezeq home IP is **not** allowlisted, so all deploys must
originate from the server. This means **the server `.env` is the one that
actually matters for deploys**.

When uPress rotates the FTPS password, the Mac `.env` is typically updated
first (the developer sees the new password in the uPress control panel). If the
server `.env` is not updated in step, the next deploy attempt will fail with:

```
530 Login incorrect
```

This exact failure occurred during WP-CB-UI-ALIGN: the server `SFA_FTP_PASS`
was 11 characters (stale) while the Mac held the current 13-character password.

---

## 2. Where the credential lives

### Mac

```
/Users/nimrod/Documents/SmallFarmsAgents/.env
```

Key variable:

```
SFA_FTP_PASS=<current-password>
```

### waldhomeserver

```
~/SmallFarmsAgents/.env
```

(Same repo clone on the server — path may vary if the repo was cloned elsewhere;
confirm with `find ~ -name ".env" -path "*/SmallFarmsAgents/*"` on the server.)

### Important: `.env` is gitignored

`.env` is listed in `.gitignore` and must never be committed. Secrets propagate
only via the secure sync procedure below — never via git.

---

## 3. Rotation-sync procedure

Perform these steps from the **Mac** immediately after updating your Mac `.env`
with the new password.

### Variables (set once, used throughout)

```bash
SERVER_USER="nimrod"                         # waldhomeserver SSH user
SERVER_HOST="waldhomeserver"                 # or IP / hostname alias
SERVER_ENV_PATH="~/SmallFarmsAgents/.env"    # path to .env on the server
NEW_PASS="<paste-new-password-here>"         # only use this in the terminal, never in a file
```

### Step 1 — Write new password to a local temp file (mode 600)

```bash
TMPFILE="$(mktemp /tmp/sfa_ftp_pass.XXXXXX)"
chmod 600 "$TMPFILE"
printf '%s' "$NEW_PASS" > "$TMPFILE"
```

> `printf '%s'` avoids a trailing newline that `echo` would add, preventing
> off-by-one length confusion when the server reads the value.

### Step 2 — SCP the temp file to the server

```bash
REMOTE_TMP="/tmp/sfa_ftp_pass_incoming.tmp"
scp -o StrictHostKeyChecking=accept-new "$TMPFILE" "${SERVER_USER}@${SERVER_HOST}:${REMOTE_TMP}"
```

### Step 3 — Auto-delete the local temp file

```bash
rm -f "$TMPFILE"
echo "[local] temp file deleted"
```

### Step 4 — On the server: backup, update, clean up

SSH into waldhomeserver and run the following block (or paste it as a single
here-doc in one SSH call — see Step 4a below):

```bash
ssh "${SERVER_USER}@${SERVER_HOST}" bash <<'ENDSSH'
set -euo pipefail

ENV_FILE="${HOME}/SmallFarmsAgents/.env"
REMOTE_TMP="/tmp/sfa_ftp_pass_incoming.tmp"
TS="$(date +%Y%m%d_%H%M%S)"
BACKUP="${ENV_FILE}.bak.${TS}_sfa_pass_rotation"

# Backup current .env (mode 600)
cp "$ENV_FILE" "$BACKUP"
chmod 600 "$BACKUP"
echo "[server] backup saved: $BACKUP"

# Read new password from temp file (strip any trailing newline)
NEW_PASS_VALUE="$(cat "$REMOTE_TMP")"

# Update SFA_FTP_PASS in-place (sed; works on both GNU and BSD)
if grep -q '^SFA_FTP_PASS=' "$ENV_FILE"; then
  # Replace existing line
  sed -i.tmp "s|^SFA_FTP_PASS=.*|SFA_FTP_PASS=${NEW_PASS_VALUE}|" "$ENV_FILE"
  rm -f "${ENV_FILE}.tmp"   # sed -i.tmp leaves a .tmp backup on BSD/macOS sed
else
  # Append if the variable is missing entirely (should not normally happen)
  echo "SFA_FTP_PASS=${NEW_PASS_VALUE}" >> "$ENV_FILE"
fi

# Delete the remote temp file immediately
rm -f "$REMOTE_TMP"
echo "[server] temp file deleted, .env updated"
ENDSSH
```

### Step 4a — One-liner alternative (no interactive SSH session)

The Step 4 block above can be pasted verbatim as a here-doc into your terminal;
no interactive SSH login is required.

### Step 5 — Verify the length on the server matches the Mac

```bash
# On Mac — count characters of new password
printf '%s' "$NEW_PASS" | wc -c

# On server — verify the stored value has the same length
ssh "${SERVER_USER}@${SERVER_HOST}" \
  'grep "^SFA_FTP_PASS=" ~/SmallFarmsAgents/.env | cut -d= -f2- | wc -c'
```

The two counts must match (server output will be one higher if there is a
trailing newline from `wc -c` on some systems — both showing e.g. 13 and 14
are fine if the difference is exactly 1 due to the implicit newline that
`wc -c` counts on some platforms; the sed replacement above strips trailing
newlines).

---

## 4. Verification — test the FTPS login

After updating the server `.env`, confirm FTPS authentication succeeds before
re-running a full deploy:

```bash
ssh "${SERVER_USER}@${SERVER_HOST}" bash <<'ENDSSH'
set -a; source ~/SmallFarmsAgents/.env; set +a
lftp -c "
set ftp:ssl-allow yes
set ftp:ssl-force yes
set ftp:ssl-protect-data yes
set ssl:verify-certificate no
set ftp:passive-mode yes
set net:max-retries 1
set net:timeout 15
open -u \"${SFA_FTP_USER},${SFA_FTP_PASS}\" -p ${SFA_FTP_PORT:-21} ${SFA_FTP_HOST}
ls ${SFA_FTP_ROOT:-/}
bye" && echo "[verify] FTPS login OK"
ENDSSH
```

Expected output ends with `[verify] FTPS login OK`. If you still see
`530 Login incorrect`, double-check that:

- The correct new password was written (no extra spaces, quotes, or newlines).
- The uPress control panel shows the same password you used.
- The server `.env` line was actually updated (re-check with
  `grep SFA_FTP_PASS ~/SmallFarmsAgents/.env` on the server — do not share the
  output anywhere; just compare the character count or verify login).

### Full deploy verification

Once the login test passes, run the full deploy from the server:

```bash
ssh "${SERVER_USER}@${SERVER_HOST}" \
  'cd ~/SmallFarmsAgents && bash scripts/ftp_deploy_sfa_ui.sh'
```

Post-deploy smoke checks are in [UI_DEPLOY_RUNBOOK.md](./UI_DEPLOY_RUNBOOK.md#post-deploy-smoke).

---

## 5. Helper script

A standalone helper script is provided at
`scripts/sync_ftps_cred.sh` (in this repo). It automates the entire procedure
above — temp-file creation, SCP, server-side backup + in-place update, and
cleanup — without ever echoing the secret to stdout.

Usage (run from the **Mac**, repo root):

```bash
bash scripts/sync_ftps_cred.sh
```

The script will prompt for the new FTPS password interactively (input is hidden
via `read -rs`). Alternatively, supply the SERVER variables via environment:

```bash
SERVER_USER=nimrod SERVER_HOST=waldhomeserver bash scripts/sync_ftps_cred.sh
```

After propagation, the script runs the FTPS login test automatically and
reports success or failure.

See the script header for all configurable variables.

---

## 6. Backup retention

Backups created by this procedure are named:

```
.env.bak.<YYYYMMDD_HHMMSS>_sfa_pass_rotation
```

They are kept on the server at `~/SmallFarmsAgents/`. They are gitignored (the
`.gitignore` already covers `.env*`). Retain at least the most recent backup
in case the rotation needs to be rolled back. Delete older backups manually
once the new credential is confirmed working.

---

## 7. Cross-references and hosting canon

- **Deploy runbook:** [UI_DEPLOY_RUNBOOK.md](./UI_DEPLOY_RUNBOOK.md)
- **Hosting canon (anti-drift):**
  - `sfa.nimrod.bio` is hosted on **uPress** (shared LAMP; Cloudflare edge).
    Only uPress-allowlisted IPs can reach FTPS port 21.
  - **waldhomeserver** is the allowlisted FTPS upload relay. All FTPS sessions
    must originate there.
  - The Mac's Bezeq home IP is **not** allowlisted. Running
    `ftp_deploy_sfa_ui.sh` locally on the Mac will fail with a connection error
    (not a 530 — the connection never reaches uPress).
  - Full topology: `documentation/02-architecture/sfa-delivery-tier.md`
- **Script:** `scripts/sync_ftps_cred.sh` (see Section 5)
- **Incident context:** WP-CB-UI-ALIGN — stale server password (11 chars vs
  current 13 chars) caught by team_99; synced out-of-band via temp-file/scp
  pattern that this runbook now codifies.
