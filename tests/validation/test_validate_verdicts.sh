#!/usr/bin/env bash
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VALIDATE="$(cd "$SCRIPT_DIR/../../lean-kit/modules/validation-quality/scripts" && pwd)/validate_verdicts.sh"
FIXTURES="$SCRIPT_DIR/fixtures/verdicts"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PASS=0; FAIL=0

check() {
    local desc="$1" expected_exit="$2" expected_pattern="$3"; shift 3
    local output exit_code
    output=$(bash "$VALIDATE" "$@" 2>&1)
    exit_code=$?
    local ok=1
    [ "$exit_code" != "$expected_exit" ] && ok=0
    if [ -n "$expected_pattern" ]; then
        echo "$output" | grep -q "$expected_pattern" || ok=0
    fi
    if [ "$ok" = "1" ]; then
        echo "[PASS] $desc"; ((PASS++)) || true
    else
        echo "[FAIL] $desc (exit=$exit_code, expected=$expected_exit)"
        ((FAIL++)) || true
    fi
}

# Copy all verdict fixtures into _COMMUNICATION/ for scanning
COMM="$REPO_ROOT/_COMMUNICATION"
BACKUP_T50="" BACKUP_T190=""
# Backup existing verdict files if any
if ls "$COMM/team_50/"*VTEST* 2>/dev/null; then BACKUP_T50=$(mktemp -d); cp "$COMM/team_50/"*VTEST* "$BACKUP_T50/"; fi
if ls "$COMM/team_190/"*VTEST* 2>/dev/null; then BACKUP_T190=$(mktemp -d); cp "$COMM/team_190/"*VTEST* "$BACKUP_T190/"; fi

mkdir -p "$COMM/team_50" "$COMM/team_190"
cp "$FIXTURES/valid_verdict_t50/"* "$COMM/team_50/"
cp "$FIXTURES/invalid_verdict_t50/"* "$COMM/team_50/"
cp "$FIXTURES/valid_verdict_t190/"* "$COMM/team_190/"
cp "$FIXTURES/invalid_verdict_t190/"* "$COMM/team_190/"

echo "=== test_validate_verdicts.sh ==="
check "valid t50 fixture exits 0"    0 "PASS" --team team_50 --wp AOS-VTEST-SYNTHETIC
check "invalid t50 fixture exits 1"  1 "FAIL" --team team_50 --wp AOS-VTEST-MISSING
check "valid t190 fixture exits 0"   0 "PASS" --team team_190 --wp AOS-VTEST-SYNTHETIC
check "invalid t190 fixture exits 1" 1 "FAIL" --team team_190 --wp AOS-VTEST-MISSING-CRITERIA

# Cleanup test fixtures from _COMMUNICATION/
rm -f "$COMM/team_50/VERDICT_VTEST_LGATE_BUILD_v1.0.0.md" "$COMM/team_50/VERDICT_VTEST_MISSING_FIELDS.md"
rm -f "$COMM/team_190/VERDICT_VTEST_LGATE_VALIDATE_v1.0.0.md" "$COMM/team_190/VERDICT_VTEST_MISSING_CRITERIA.md"
# Restore backups if any
[ -n "$BACKUP_T50" ] && cp "$BACKUP_T50/"* "$COMM/team_50/" && rm -rf "$BACKUP_T50"
[ -n "$BACKUP_T190" ] && cp "$BACKUP_T190/"* "$COMM/team_190/" && rm -rf "$BACKUP_T190"

echo "─────────────────────────────"
echo "RESULT: $PASS PASS · $FAIL FAIL"
[ "$FAIL" -eq 0 ]
