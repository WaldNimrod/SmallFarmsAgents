#!/usr/bin/env bash
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VALIDATE="$(cd "$SCRIPT_DIR/../../lean-kit/modules/validation-quality/scripts" && pwd)/validate_gates.sh"
FIXTURES="$SCRIPT_DIR/fixtures/roadmap"
PASS=0; FAIL=0

check() {
    local desc="$1" expected_exit="$2" expected_pattern="$3"
    local fixture_file="$4"
    local output exit_code
    output=$(bash "$VALIDATE" --roadmap "$FIXTURES/$fixture_file" 2>&1)
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
        echo "       output: $(echo "$output" | head -3)"
        ((FAIL++)) || true
    fi
}

echo "=== test_validate_gates.sh ==="
check "valid_roadmap exits 0"                    0 "PASS"    "valid_roadmap.yaml"
check "invalid_progression exits 1 + V-GATE-1"  1 "V-GATE-1" "invalid_roadmap_progression.yaml"
check "invalid_reportpath exits 1 + V-GATE-2"   1 "V-GATE-2" "invalid_roadmap_reportpath.yaml"

echo "─────────────────────────────"
echo "RESULT: $PASS PASS · $FAIL FAIL"
[ "$FAIL" -eq 0 ]
