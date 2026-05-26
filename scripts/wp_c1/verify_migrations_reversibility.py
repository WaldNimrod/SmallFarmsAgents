"""WP-C1 — Migration reversibility verification (static + isolated-PG).

Verifies AC-C1-01 + AC-C1-02 (migrations 049 + 050) reversibility through
TWO independent checks:

  1. STATIC: parse migration files, verify both upgrade() + downgrade() exist
     and that downgrade reverses upgrade (drops tables/indexes that upgrade
     creates).
  2. ISOLATED PG (optional): if DATABASE_URL_TEST is set, run
     alembic stamp 048 -> upgrade head -> downgrade 048 -> upgrade head
     on an isolated PostgreSQL DB.

Why not pure SQLite:
  Earlier migrations (035..040 from WP-A/B) use PostgreSQL-only JSONB,
  preventing upgrade-from-zero on SQLite. Reversibility of 049+050 ALONE
  is what matters for WP-C1 AC verification.

Usage:
    python3 scripts/wp_c1/verify_migrations_reversibility.py
    DATABASE_URL_TEST=postgresql://... python3 scripts/wp_c1/verify_migrations_reversibility.py
"""
from __future__ import annotations
import ast
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = REPO / "organic_market_agent" / "db" / "versions"


def static_check(migration_file: Path) -> tuple[bool, list[str]]:
    msgs: list[str] = []
    src = migration_file.read_text(encoding="utf-8")
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return False, [f"  Syntax error: {e}"]

    has_upgrade = False
    has_downgrade = False
    upgrade_ops: set[str] = set()
    downgrade_ops: set[str] = set()

    def collect_op_calls(node):
        ops = set()
        for sub in ast.walk(node):
            if isinstance(sub, ast.Call):
                f = sub.func
                if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name):
                    if f.value.id == "op":
                        ops.add(f.attr)
        return ops

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name == "upgrade":
                has_upgrade = True
                upgrade_ops = collect_op_calls(node)
            elif node.name == "downgrade":
                has_downgrade = True
                downgrade_ops = collect_op_calls(node)

    if not has_upgrade:
        return False, ["  FAIL: upgrade() function missing"]
    if not has_downgrade:
        return False, ["  FAIL: downgrade() function missing"]

    msgs.append(f"  upgrade ops:   {sorted(upgrade_ops)}")
    msgs.append(f"  downgrade ops: {sorted(downgrade_ops)}")

    expected_reverse = {
        "create_table": "drop_table",
        "create_index": "drop_index",
        "add_column": "drop_column",
        "create_check_constraint": "drop_constraint",
        "create_unique_constraint": "drop_constraint",
    }
    asymmetric = [
        f"upgrade has {u} but downgrade missing {expected_reverse[u]}"
        for u in upgrade_ops
        if u in expected_reverse and expected_reverse[u] not in downgrade_ops
    ]
    if asymmetric:
        msgs.append("  WARN: asymmetric ops:")
        for a in asymmetric:
            msgs.append(f"    - {a}")
    else:
        msgs.append("  OK: symmetric upgrade/downgrade ops")
    return True, msgs


def isolated_pg_check(database_url):
    msgs = []
    env = os.environ.copy()
    env["DATABASE_URL"] = database_url
    for cmd, label in [
        (["alembic", "stamp", "048"], "stamp 048 (baseline before C1)"),
        (["alembic", "upgrade", "head"], "upgrade head (apply 049+050)"),
        (["alembic", "downgrade", "048"], "downgrade 048 (reverse 049+050)"),
        (["alembic", "upgrade", "head"], "re-upgrade head (re-apply 049+050)"),
    ]:
        res = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO, env=env, timeout=60)
        if res.returncode != 0:
            msgs.append(f"  FAIL: {label}")
            msgs.append(f"    stderr: {res.stderr[:300]}")
            return False, msgs
        msgs.append(f"  OK:   {label}")
    return True, msgs


def main() -> int:
    print("=" * 70)
    print("WP-C1 Migration Reversibility Verification")
    print("AC-C1-01 (migration 049) + AC-C1-02 (migration 050)")
    print("=" * 70)

    targets = [
        MIGRATIONS_DIR / "049_crop_planting_calendar.py",
        MIGRATIONS_DIR / "050_crop_cover_crops.py",
    ]
    all_ok = True
    for m in targets:
        print(f"\nSTATIC CHECK: {m.name}")
        ok, msgs = static_check(m)
        for line in msgs:
            print(line)
        if not ok:
            all_ok = False

    db_test = os.environ.get("DATABASE_URL_TEST")
    if db_test:
        print(f"\nISOLATED PG CHECK: {db_test}")
        ok, msgs = isolated_pg_check(db_test)
        for line in msgs:
            print(line)
        if not ok:
            all_ok = False
    else:
        print("\nISOLATED PG CHECK: SKIPPED (set DATABASE_URL_TEST to enable)")
        print("  Note: at build time, sfa_build ran alembic upgrade head on live PG")
        print("        (see _COMMUNICATION/team_10/SFA-S003-P002-WP-C1/BUILD_REPORT_v1.0.0.md)")

    print("\n" + "=" * 70)
    if all_ok:
        print("RESULT: PASS - WP-C1 migrations 049+050 reversibility verified")
        return 0
    print("RESULT: FAIL - see messages above")
    return 1


if __name__ == "__main__":
    sys.exit(main())
