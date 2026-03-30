#!/usr/bin/env python3
"""Run G3 Phase A diagnosis SQL (see Team 10 G3 remediation plan). Usage: python3.11 scripts/run_g3_phase_a_diagnosis.py"""
from __future__ import annotations

import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# Ensure DATABASE_URL is set before importing app config
if not os.environ.get("DATABASE_URL"):
    print(
        "Set DATABASE_URL (e.g. source .env). Example:\n"
        "  set -a && source .env && set +a && python3.11 scripts/run_g3_phase_a_diagnosis.py",
        file=sys.stderr,
    )
    sys.exit(2)

from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from organic_market_agent.db.session import engine

Q1 = """
SELECT LEFT(COALESCE(unresolvable_reason, '(null)'), 120) AS reason_prefix,
       COUNT(*) AS cnt
FROM raw_extracted_items
WHERE extraction_status = 'unresolvable'
GROUP BY 1
ORDER BY cnt DESC
LIMIT 30
"""

Q2 = """
SELECT raw_product_name, COUNT(*) AS cnt
FROM raw_extracted_items
WHERE extraction_status = 'unresolvable'
GROUP BY 1
ORDER BY cnt DESC
LIMIT 50
"""

Q3 = """
SELECT s.code, COUNT(*) AS unresolvable_cnt
FROM raw_extracted_items rei
JOIN source_fetch_runs sfr ON sfr.id = rei.source_fetch_run_id
JOIN sources s ON s.id = sfr.source_id
WHERE rei.extraction_status = 'unresolvable'
GROUP BY s.code
ORDER BY unresolvable_cnt DESC
"""


def _print_result(title: str, sql: str) -> list[tuple]:
    print(f"\n=== {title} ===\n")
    rows: list[tuple] = []
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        cols = result.keys()
        print(" | ".join(cols))
        print("-" * 80)
        for row in result:
            rows.append(tuple(row))
            print(" | ".join(str(x) for x in row))
    return rows


def _estimate_mix(q1_rows: list[tuple]) -> tuple[int, int, int, int]:
    """Rough counts from reason_prefix (column 0) for narrative paragraph."""
    alias = price = post = other = 0
    for prefix, cnt in q1_rows:
        p = (prefix or "").lower()
        c = int(cnt) if cnt is not None else 0
        if "no alias" in p or "alias match" in p:
            alias += c
        elif "parse price" in p or "price" in p and "empty" in p:
            price += c
        elif "missing product_id" in p or "display_unit" in p:
            post += c
        else:
            other += c
    return alias, price, post, other


def main() -> None:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except OperationalError as exc:
        print(f"Database connection failed: {exc}", file=sys.stderr)
        sys.exit(1)
    print("G3 Phase A — unresolvable diagnosis (Team 10)")
    r1 = _print_result("Q1 — unresolvable_reason breakdown", Q1)
    _print_result("Q2 — top raw_product_name (unresolvable)", Q2)
    _print_result("Q3 — unresolvable by source code", Q3)

    a, pr, po, oth = _estimate_mix([(row[0], row[1]) for row in r1])
    total = a + pr + po + oth
    print("\n=== Draft classification paragraph (verify against Q1) ===\n")
    if total == 0:
        print("No unresolvable rows in Q1 sample scope (or empty DB).")
    else:
        print(
            f"Approximate mix from Q1 prefixes: alias-related ~{a} ({100 * a / total:.1f}%), "
            f"price_parse-related ~{pr} ({100 * pr / total:.1f}%), "
            f"post-stage (missing product/unit) ~{po} ({100 * po / total:.1f}%), "
            f"other ~{oth} ({100 * oth / total:.1f}%). "
            "Refine manually from the Q1 table before filing QA."
        )
    print("\nAttach this full output to _COMMUNICATION/TEAM_10/reports/ G3 remediation pack.")


if __name__ == "__main__":
    main()
