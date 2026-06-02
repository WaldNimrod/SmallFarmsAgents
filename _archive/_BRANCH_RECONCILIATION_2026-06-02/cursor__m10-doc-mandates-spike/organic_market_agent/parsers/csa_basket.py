"""CSA basket sites (SRC033–SRC035) — prices plus policy context in ``raw_payload_json``."""

from __future__ import annotations

import html
import re
from typing import Any, Optional

from bs4 import BeautifulSoup

from organic_market_agent.parsers.base import BaseParser, RawItem
from organic_market_agent.utils.exceptions import ParserError
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)

_SHEKEL_LINE = re.compile(r"₪\s*([\d.]+)|([\d.]+)\s*₪")


def _visible_lines(content: bytes, charset_hint: Optional[str]) -> list[str]:
    enc = charset_hint or "utf-8"
    try:
        soup = BeautifulSoup(content, "html.parser", from_encoding=enc)
    except Exception as exc:
        raise ParserError(f"CsaBasketParser: HTML parse error: {exc}") from exc
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    raw = soup.get_text("\n")
    out: list[str] = []
    for ln in raw.split("\n"):
        s = " ".join(ln.split())
        if s:
            out.append(s)
    dedup: list[str] = []
    for ln in out:
        if not dedup or dedup[-1] != ln:
            dedup.append(ln)
    return dedup


def _next_price(lines: list[str], start: int) -> Optional[tuple[str, int]]:
    """Return (price_text, line_index) for first ₪ price after start."""
    for i in range(start, min(start + 12, len(lines))):
        ln = lines[i]
        m = _SHEKEL_LINE.search(ln)
        if m:
            return (m.group(1) or m.group(2) or "").strip(), i
    return None


def _shorashim_context(lines: list[str]) -> dict[str, Any]:
    """Excerpts for transparency (contents + cadence) when present."""
    contents_parts: list[str] = []
    cadence_parts: list[str] = []
    for i, ln in enumerate(lines):
        if "אז מה יש בסל" in ln or "מה היה השבוע בסל" in ln:
            chunk = " ".join(lines[i : min(i + 6, len(lines))])
            if len(chunk) > 40:
                contents_parts.append(chunk[:800])
        if "יום חמישי" in ln or "משלוחים מגיעים" in ln or "איסוף מהחווה" in ln:
            cadence_parts.append(ln[:400])
    return {
        "contents_summary": " | ".join(contents_parts)[:1200] or None,
        "cadence_or_delivery_note": " | ".join(cadence_parts)[:1200] or None,
        "context_incomplete": not contents_parts and not cadence_parts,
    }


def _parse_havat_shorashim(content: bytes, charset_hint: Optional[str]) -> list[RawItem]:
    lines = _visible_lines(content, charset_hint)
    ctx = _shorashim_context(lines)
    items: list[RawItem] = []

    def add(name: str, price: str) -> None:
        payload = {
            "parser": "csa_basket",
            "csa_site": "havat_shorashim",
            "csa_context": {k: v for k, v in ctx.items() if v is not None},
        }
        items.append(
            RawItem(
                raw_product_name=name[:300],
                raw_price_text=price,
                raw_unit_text="basket",
                raw_quantity_text=None,
                raw_payload_json=payload,
            )
        )

    # Use the pricing section near the "סל קטן" / "סל גדול" labels (not the nav duplicate).
    try:
        anchor = next(i for i, ln in enumerate(lines) if ln.strip() == "סל קטן")
    except StopIteration:
        anchor = 0
    money: list[str] = []
    for ln in lines[anchor : anchor + 25]:
        m = _SHEKEL_LINE.search(ln)
        if m:
            money.append((m.group(1) or m.group(2) or "").strip())
    if len(money) >= 2:
        add("סל קטן", money[0])
        add("סל גדול", money[1])

    for i, ln in enumerate(lines):
        if ("סל סטודנטים" in ln and "חדש" in ln) or ln.strip().startswith(
            "חדש! סל סטודנטים"
        ):
            for pr in money:
                if pr == "90":
                    add("סל סטודנטים", pr)
                    break
            else:
                hit = _next_price(lines, i + 1)
                if hit:
                    add("סל סטודנטים", hit[0])
            break

    return items


def _parse_meshek_organi(content: bytes, charset_hint: Optional[str]) -> list[RawItem]:
    raw = (content.decode(charset_hint or "utf-8", errors="replace")).replace("\xa0", " ")
    text = html.unescape(raw)
    items: list[RawItem] = []

    fam_m = re.search(
        r"סל\s+ירקות\s+אורגני\s+משפחתי[^.]{0,120}?(\d+)\s*ש[\"״]ח",
        text,
        re.DOTALL,
    )
    base_m = re.search(
        r"סל\s+ירקות\s+אורגני\s+בסיסי[^.]{0,120}?(\d+)\s*ש[\"״]ח",
        text,
        re.DOTALL,
    )
    contents_fam = re.search(
        r"סל\s+ירקות\s+אורגני\s+משפחתי\s+יכיל\s+([^\n]+)",
        text,
    )
    contents_base = re.search(
        r"סל\s+ירקות\s+אורגני\s+בסיסי\s+יכיל\s+([^\n]+)",
        text,
    )
    cadence = re.search(r"משלוח[^.\n]{0,200}", text)

    def ctx() -> dict[str, Any]:
        parts: dict[str, Any] = {}
        cf = contents_fam.group(1).strip()[:600] if contents_fam else None
        cb = contents_base.group(1).strip()[:600] if contents_base else None
        if cf or cb:
            parts["contents_summary"] = " | ".join(x for x in (cf, cb) if x)
        if cadence:
            parts["cadence_or_delivery_note"] = cadence.group(0).strip()[:600]
        parts["context_incomplete"] = not parts.get("contents_summary") and not parts.get(
            "cadence_or_delivery_note"
        )
        return parts

    c = ctx()
    if fam_m:
        items.append(
            RawItem(
                raw_product_name="סל ירקות אורגני משפחתי",
                raw_price_text=fam_m.group(1),
                raw_unit_text="basket",
                raw_quantity_text=None,
                raw_payload_json={
                    "parser": "csa_basket",
                    "csa_site": "meshek_organi",
                    "csa_context": c,
                },
            )
        )
    if base_m:
        items.append(
            RawItem(
                raw_product_name="סל ירקות אורגני בסיסי",
                raw_price_text=base_m.group(1),
                raw_unit_text="basket",
                raw_quantity_text=None,
                raw_payload_json={
                    "parser": "csa_basket",
                    "csa_site": "meshek_organi",
                    "csa_context": c,
                },
            )
        )
    return items


# Generic Wix/marketing paragraphs: "(סל|ארגז) … <digits> ש"ח" (possibly multiple per page).
_RE_SHEKEL_LINE_BASKETS = re.compile(
    r"((?:סל|ארגז)[^0-9\"״]{3,160}?)\s+(\d+)\s*ש[\"״]ח",
    re.DOTALL,
)


def _parse_shekel_line_baskets(
    content: bytes,
    charset_hint: Optional[str],
    selector: dict[str, Any],
) -> list[RawItem]:
    """Extract one row per ``סל``/``ארגז`` line with ILS shekel text price.

    ``selector_profile`` options:
    - ``shekel_require_organic`` (bool): keep only matches whose span contains
      אורגני / אורגנית / אורגניים (recommended for public organic index).
    """
    raw = (content.decode(charset_hint or "utf-8", errors="replace")).replace("\xa0", " ")
    text = html.unescape(raw)
    require_org = bool(selector.get("shekel_require_organic"))
    seen: set[tuple[str, str]] = set()
    items: list[RawItem] = []
    for m in _RE_SHEKEL_LINE_BASKETS.finditer(text):
        full = m.group(0)
        if require_org and not any(
            x in full for x in ("אורגני", "אורגנית", "אורגניים", "organic", "Organic")
        ):
            continue
        name = " ".join(m.group(1).split())[:300]
        price = m.group(2)
        key = (name.lower(), price)
        if key in seen:
            continue
        seen.add(key)
        start = max(0, m.start() - 120)
        end = min(len(text), m.end() + 120)
        window = " ".join(text[start:end].split())[:500]
        cadence = None
        if "משלוח" in window or "איסוף" in window or "מינימום" in window:
            cadence = window[:600]
        ctx: dict[str, Any] = {
            "context_incomplete": True,
        }
        if window:
            ctx["contents_summary"] = window
            ctx["context_incomplete"] = False
        if cadence:
            ctx["cadence_or_delivery_note"] = cadence
        items.append(
            RawItem(
                raw_product_name=name,
                raw_price_text=price,
                raw_unit_text="basket",
                raw_quantity_text=None,
                raw_payload_json={
                    "parser": "csa_basket",
                    "csa_site": "shekel_line_baskets",
                    "csa_context": ctx,
                },
            )
        )
    return items


def _parse_meshek_yosef(content: bytes, charset_hint: Optional[str]) -> list[RawItem]:
    """V1: no stable basket SKUs on the FAQ entry URL — do not invent rows."""
    lines = _visible_lines(content, charset_hint)
    ctx = {
        "contents_summary": None,
        "cadence_or_delivery_note": None,
        "context_incomplete": True,
    }
    note_parts: list[str] = []
    for ln in lines:
        if "ש\"ח" in ln or "שח" in ln:
            if any(k in ln for k in ("משלוח", "מינימום", "דמי")):
                note_parts.append(ln[:300])
    if note_parts:
        ctx["cadence_or_delivery_note"] = " | ".join(note_parts)[:1200]
        ctx["context_incomplete"] = False
    logger.info(
        "CsaBasketParser meshek_yosef: 0 SKUs (policy §4.5); context_note=%s",
        bool(note_parts),
    )
    return []


class CsaBasketParser(BaseParser):
    """Dispatches by ``selector_profile.csa_site``."""

    def __init__(self, selector_overrides: Optional[dict[str, Any]] = None) -> None:
        self._sel = selector_overrides or {}

    def parse(self, content: bytes, charset_hint: Optional[str] = None) -> list[RawItem]:
        site = (self._sel.get("csa_site") or "").strip()
        if site == "havat_shorashim":
            return _parse_havat_shorashim(content, charset_hint)
        if site == "meshek_organi":
            return _parse_meshek_organi(content, charset_hint)
        if site == "meshek_yosef":
            return _parse_meshek_yosef(content, charset_hint)
        if site == "shekel_line_baskets":
            return _parse_shekel_line_baskets(content, charset_hint, self._sel)
        logger.warning("CsaBasketParser: unknown csa_site=%r", site)
        return []
