"""Abstract base for all parsers."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RawItem:
    """A single extracted row from a raw asset before normalization."""

    raw_product_name: Optional[str]
    raw_price_text: Optional[str]
    raw_unit_text: Optional[str]
    raw_quantity_text: Optional[str]
    raw_payload_json: dict = field(default_factory=dict)


class BaseParser(ABC):
    """Abstract parser.

    Subclasses receive raw bytes and return a list of RawItem.
    parsers must NOT normalize, resolve aliases, or convert units.
    """

    @abstractmethod
    def parse(self, content: bytes, charset_hint: Optional[str] = None) -> list[RawItem]:
        """Extract raw items from raw bytes.

        Raises ParserError if content is completely unparseable.
        Returns empty list if content is valid but contains no product rows.
        """
