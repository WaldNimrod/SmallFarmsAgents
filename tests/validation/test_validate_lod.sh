#!/usr/bin/env bash
# test_validate_lod.sh — Test suite for validate_lod.sh
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VALIDATE="$(cd "$SCRIPT_DIR/../../lean-kit/modules/validation-quality/scripts" && pwd)/validate_lod.sh"
FIXTURES="$SCRIPT_DIR/fixtures/lod"
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
        echo "       output: $(echo "$output" | head -5)"
        ((FAIL++)) || true
    fi
}

echo "=== test_validate_lod.sh ==="
check "valid_lod400 exits 0"                0 ""         "$FIXTURES/valid_lod400"
check "invalid_lod400_tbd exits 1"          1 "V-LOD-4"  "$FIXTURES/invalid_lod400_tbd"
check "invalid_lod400_ac exits 1"           1 "V-LOD-3"  "$FIXTURES/invalid_lod400_ac"
check "invalid_lod400_frontmatter exits 1"  1 "V-LOD-1"  "$FIXTURES/invalid_lod400_frontmatter"
check "invalid_lod400_headers exits 1"      1 "V-LOD-2"  "$FIXTURES/invalid_lod400_headers"
check "invalid_lod500_specref exits 1"      1 "V-LOD-7"  "$FIXTURES/invalid_lod500_specref"
check "lod200 fixture skips V-LOD-3/4"     0 "SKIP"      "$FIXTURES/valid_lod400" --lod 200

echo "─────────────────────────────"
echo "RESULT: $PASS PASS · $FAIL FAIL"
[ "$FAIL" -eq 0 ]
