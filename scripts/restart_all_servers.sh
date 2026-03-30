#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# MyFarmAgents — Restart All Servers
# מפעיל מחדש את שני השרתים: Admin Dashboard + Public Viewer
# Usage:
#   ./scripts/restart_all_servers.sh          # restart both
#   ./scripts/restart_all_servers.sh status   # status only
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

CMD="${1:-restart}"

echo "════════════════════════════════════════"
echo " MyFarmAgents — $CMD"
echo "════════════════════════════════════════"
echo ""

echo "▶  Admin Dashboard"
bash "$SCRIPT_DIR/admin_server.sh" "$CMD"
echo ""

echo "▶  Public Viewer"
bash "$SCRIPT_DIR/viewer_server.sh" "$CMD"
echo ""

echo "════════════════════════════════════════"
echo " סיום"
echo "════════════════════════════════════════"
