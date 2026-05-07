#!/usr/bin/env python3
"""
CLI: discover likely active public pages under https://mypips.app/<slug>.

Delegates to organic_market_agent.discovery.mypips_scan (httpx, verified TLS).

Example:
    python scripts/mypips_discover.py \\
        --seeds data/mypips_seeds.txt --hebrew --english \\
        --workers 4 --delay 1.0 --years --max 3000

Calibration (known-good slugs only, no variant expansion):
    python scripts/mypips_discover.py --reference --workers 2 --delay 1.0

Experiment / validation (custom list only, no expansion):
    python scripts/mypips_discover.py --seeds path/to/slugs.txt --seeds-only --workers 3 --delay 1.0
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

# Repo root on path when running as `python scripts/mypips_discover.py`
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from organic_market_agent.discovery.mypips_scan import (  # noqa: E402
    build_candidates,
    load_lines,
    print_ethics_reminder,
    run_scan,
    save_results,
    slugify,
)


def _default_out_dir() -> Path:
    return _ROOT / "output" / "discovery"


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan mypips.app for active public slugs.")
    parser.add_argument("--seeds", type=str, help="Path to custom seed list (one per line)")
    parser.add_argument(
        "--reference",
        action="store_true",
        help="Calibration: scan only data/mypips_reference_slugs.txt (no Hebrew/English/variant expansion)",
    )
    parser.add_argument(
        "--seeds-only",
        action="store_true",
        help="Scan only slugified lines from --seeds (no Hebrew/English/numeric/year variant expansion)",
    )
    parser.add_argument("--hebrew", action="store_true", help="Include built-in Hebrew seeds")
    parser.add_argument("--english", action="store_true", help="Include built-in English seeds")
    parser.add_argument("--numeric-suffixes", type=int, default=2, help="Generate suffixes 1..N")
    parser.add_argument("--years", action="store_true", help="Append year variants")
    parser.add_argument("--workers", type=int, default=5, help="Concurrent workers")
    parser.add_argument("--delay", type=float, default=0.8, help="Delay after each request per worker")
    parser.add_argument("--timeout", type=float, default=12.0, help="Per-request timeout in seconds")
    parser.add_argument("--max", type=int, default=None, help="Max candidate count to test")
    default_dir = _default_out_dir()
    parser.add_argument(
        "--out",
        type=str,
        default=str(default_dir / "mypips_scan.csv"),
        help="CSV output path (default: output/discovery/mypips_scan.csv)",
    )
    parser.add_argument(
        "--out-active",
        type=str,
        default=str(default_dir / "mypips_active.txt"),
        help="TXT output path for active URLs only (default: output/discovery/mypips_active.txt)",
    )
    parser.add_argument(
        "--no-ethics-reminder",
        action="store_true",
        help="Suppress stderr reminder about robots.txt and ToS",
    )
    args = parser.parse_args()

    if args.seeds_only and not args.seeds:
        print("--seeds-only requires --seeds FILE", file=sys.stderr)
        return 2
    if args.seeds_only and args.reference:
        print("Use either --reference or --seeds-only, not both.", file=sys.stderr)
        return 2

    custom_seeds: list[str] = []
    if args.reference:
        ref_path = _ROOT / "data" / "mypips_reference_slugs.txt"
        custom_seeds = load_lines(ref_path)
    elif args.seeds:
        custom_seeds = load_lines(Path(args.seeds))

    if not args.hebrew and not args.english and not custom_seeds and not args.reference:
        print(
            "No seed source selected. Use --reference, --seeds-only with --seeds, "
            "or --hebrew and/or --english and/or --seeds FILE.",
            file=sys.stderr,
        )
        return 2

    if not args.no_ethics_reminder:
        print_ethics_reminder()

    if args.reference or args.seeds_only:
        candidates = sorted({s for s in (slugify(x) for x in custom_seeds) if s})
    else:
        candidates = build_candidates(
            custom_seeds=custom_seeds,
            use_hebrew=args.hebrew,
            use_english=args.english,
            numeric_suffixes=args.numeric_suffixes,
            years=args.years,
        )

    print(f"Candidate count: {len(candidates)}")
    results = asyncio.run(
        run_scan(
            candidates=candidates,
            workers=max(1, args.workers),
            delay=max(0.0, args.delay),
            timeout_s=max(1.0, args.timeout),
            max_count=args.max,
        )
    )
    save_results(results, Path(args.out), Path(args.out_active))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
