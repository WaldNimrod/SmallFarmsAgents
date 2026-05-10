"""
MyPIPS public slug discovery — scan https://mypips.app/<slug> for likely active store pages.

Adapted from Team 80 handoff with httpx, verified TLS, tighter heuristics, sorted outputs.

**Distinguishing real tenant stores from the generic SPA shell:** unknown slugs still return
HTTP 200 with a large HTML body. The ``<title>`` of that shell contains a fixed Hebrew phrase
(see ``MYPIPS_GENERIC_STORE_TITLE_MARKER``). Real stores use titles like
``עמוד הבית | <store name> | להזמנות | …`` (e.g. nimrod → "מהגינה של נימרוד"). Calibration
slugs: ``data/mypips_reference_slugs.txt``.
"""
from __future__ import annotations

import asyncio
import csv
import random
import re
import sys
import unicodedata
from pathlib import Path
from typing import Iterable, List, Set, Tuple
from urllib.parse import quote

import httpx

BASE_URL = "https://mypips.app"

# Honest UA; contact URL for site operators (project presentation domain).
DEFAULT_HEADERS = {
    "User-Agent": (
        "OrganicMarketAgent-mypips-discovery/1.0 "
        "(+https://nimrod.bio; research/community price index)"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "he,en;q=0.9,en-US;q=0.8",
}

# Present in <title> for unclaimed / generic slug responses (~5.8kB shell), not real tenants.
MYPIPS_GENERIC_STORE_TITLE_MARKER = (
    "מערכת ההזמנות של העסקים העצמאיים והקהילתיים בישראל"
)

# Phrase-only markers in body snippet (avoid bare "404" — too many false negatives).
NOT_FOUND_PHRASES = (
    "page not found",
    "could not be found",
    "cannot find this page",
    "this page doesn't exist",
    "העמוד לא נמצא",
    "לא נמצא העמוד",
    "אופס! העמוד",
    "oops! nothing was found",
    "לא נמצא",  # standalone phrase; checked only in title (see below)
)

HEBREW_SEEDS = [
    "nimrod",
    "garden",
    "farm",
    "organic",
    "veggies",
    "vegetables",
    "משק",
    "הגינה",
    "גינה",
    "חווה",
    "אורגני",
    "ירקות",
    "חקלאי",
    "שדה",
    "מושב",
    "משלוח",
    "ירוק",
    "טבע",
    "תוצרת",
    "שוק",
    "סל",
]

ENGLISH_SEEDS = [
    "farm",
    "organic",
    "garden",
    "veggie",
    "vegetable",
    "greens",
    "market",
    "shop",
    "fresh",
    "field",
    "produce",
    "basket",
    "box",
]


def slugify(text: str) -> str:
    text = text.strip()
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("_", "-").replace(" ", "-")
    text = re.sub(r"-{2,}", "-", text)
    text = re.sub(r"[^0-9A-Za-z\u0590-\u05FF\-]", "", text)
    return text.strip("-").lower()


def load_lines(path: Path) -> List[str]:
    if not path.exists():
        raise FileNotFoundError(path)
    lines: List[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        lines.append(s)
    return lines


def build_candidates(
    custom_seeds: Iterable[str],
    use_hebrew: bool,
    use_english: bool,
    numeric_suffixes: int,
    years: bool,
) -> List[str]:
    seeds: Set[str] = set()

    for s in custom_seeds:
        ss = slugify(s)
        if ss:
            seeds.add(ss)

    if use_hebrew:
        for s in HEBREW_SEEDS:
            ss = slugify(s)
            if ss:
                seeds.add(ss)

    if use_english:
        for s in ENGLISH_SEEDS:
            ss = slugify(s)
            if ss:
                seeds.add(ss)

    variants: Set[str] = set(seeds)
    for s in list(seeds):
        variants.add(s.replace("-", ""))
        if "-" not in s and len(s) > 4:
            variants.add(f"{s}-farm")
            variants.add(f"{s}-garden")
            variants.add(f"{s}-organic")
            variants.add(f"{s}-shop")

    if numeric_suffixes > 0:
        for s in list(variants):
            for i in range(1, numeric_suffixes + 1):
                variants.add(f"{s}{i}")
                variants.add(f"{s}-{i}")

    if years:
        for s in list(variants):
            for y in ("2023", "2024", "2025", "2026", "2027"):
                variants.add(f"{s}{y}")
                variants.add(f"{s}-{y}")

    candidates = sorted({v for v in variants if 2 <= len(v) <= 60})
    random.shuffle(candidates)
    return candidates


def extract_title(html: str) -> str:
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    if not m:
        return ""
    return re.sub(r"\s+", " ", m.group(1)).strip()


def is_likely_active(status: int, text: str) -> bool:
    if status != 200:
        return False
    body = text or ""
    if len(body.strip()) < 400:
        return False
    lower = body.lower()
    raw_title = extract_title(body)
    tl = raw_title.lower()

    # MyPIPS: generic shell vs real store (see module docstring).
    if raw_title and MYPIPS_GENERIC_STORE_TITLE_MARKER in raw_title:
        return False

    # Short error-style titles
    if tl:
        title_red_flags = ("404", "not found", "notfound", "error", "לא נמצא")
        if any(x in tl for x in title_red_flags) and len(tl) < 100:
            return False

    snippet = lower[:8000]
    for phrase in NOT_FOUND_PHRASES:
        if phrase in snippet:
            # "לא נמצא" in body can be generic; title already screened.
            if phrase == "לא נמצא" and phrase not in tl:
                continue
            return False

    return True


async def fetch_one(
    client: httpx.AsyncClient,
    slug: str,
) -> Tuple[str, int, int, bool, str]:
    url = f"{BASE_URL}/{quote(slug)}"
    try:
        resp = await client.get(url)
        text = resp.text
        active = is_likely_active(resp.status_code, text)
        title = extract_title(text) if text else ""
        return url, resp.status_code, len(text), active, title
    except httpx.HTTPError:
        return url, 0, 0, False, ""
    except Exception:
        return url, 0, 0, False, ""


async def run_scan(
    candidates: List[str],
    workers: int,
    delay: float,
    timeout_s: float,
    max_count: int | None,
) -> List[Tuple[str, int, int, bool, str]]:
    sem = asyncio.Semaphore(workers)
    results: List[Tuple[str, int, int, bool, str]] = []

    limits = httpx.Limits(max_connections=workers, max_keepalive_connections=workers)
    timeout = httpx.Timeout(timeout_s)

    async with httpx.AsyncClient(
        headers=DEFAULT_HEADERS,
        limits=limits,
        timeout=timeout,
        follow_redirects=True,
    ) as client:

        async def bounded(slug: str) -> Tuple[str, int, int, bool, str]:
            async with sem:
                res = await fetch_one(client, slug)
                if delay > 0:
                    await asyncio.sleep(delay)
                return res

        subset = candidates[:max_count] if max_count else candidates
        tasks = [asyncio.create_task(bounded(slug)) for slug in subset]
        for coro in asyncio.as_completed(tasks):
            res = await coro
            results.append(res)
            url, status, size, active, title = res
            flag = "ACTIVE" if active else "----"
            print(f"{flag} {status:3} {size:6} {url} {title}", flush=True)

    results.sort(key=lambda r: r[0])
    return results


def save_results(
    results: List[Tuple[str, int, int, bool, str]],
    out_csv: Path,
    out_txt: Path,
) -> int:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_txt.parent.mkdir(parents=True, exist_ok=True)

    active_rows = [r for r in results if r[3]]

    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["url", "status", "body_len", "active", "title"])
        writer.writerows(results)

    with out_txt.open("w", encoding="utf-8") as f:
        for url, status, size, active, title in active_rows:
            line = url
            if title:
                line += f" | {title}"
            f.write(line + "\n")

    print(file=sys.stdout)
    print(f"Saved full scan to:  {out_csv}", file=sys.stdout)
    print(f"Saved active only to: {out_txt}", file=sys.stdout)
    print(f"Active pages found:   {len(active_rows)}", file=sys.stdout)
    return len(active_rows)


def print_ethics_reminder() -> None:
    print(
        "Reminder: review https://mypips.app/robots.txt and site Terms of Use "
        "before large scans; keep --workers modest and --delay >= 0.8.",
        file=sys.stderr,
    )
