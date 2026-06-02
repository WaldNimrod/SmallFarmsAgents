"""Product row icons for public publish — IconPark Outline (Apache-2.0), vendored SVG.

Single visual system: all icons from the same IconPark *outline* set for stroke weight
and corner radius consistency. See documentation/02-architecture/PRODUCT_ICONS_STANDARD.md.
"""
from __future__ import annotations

from pathlib import Path

# Relative to publish output root and to HTML artifact location (same folder as public_report.html).
ICON_SUBDIR = "icons/iconpark"

# Hex baked into vendored SVGs at fetch time (matches --sfa-green-dark in WP / local report).
ICON_BRAND_COLOR = "#1b4332"

# Iconify collection id (for scripts / docs only; runtime uses local paths).
ICONIFY_COLLECTION = "icon-park-outline"

DEFAULT_SLUG = "leaf"

# product_id in publish JSON is Product.code (e.g. PRD001).
PRODUCT_CODE_TO_SLUG: dict[str, str] = {
    "PRD001": "tomato",
    "PRD002": "cherry",
    "PRD003": "radish",
    "PRD004": "peas",
    "PRD005": "vegetables",
    "PRD006": "eggplant",
    "PRD007": "pumpkin",
    "PRD031": "cherry",
    "PRD032": "chili",
    "PRD008": "leaf",
    "PRD030": "leaf",
    "PRD009": "leaf",
    "PRD010": "leaf",
    "PRD011": "leaf",
    "PRD012": "leaf",
    "PRD013": "carrot",
    "PRD014": "radish-one",
    "PRD015": "pumpkin",
    "PRD016": "radish",
    "PRD017": "garlic",
    "PRD018": "scallion",
    "PRD019": "garlic",
    "PRD020": "scallion",
    "PRD021": "pumpkin",
    "PRD022": "pear",
    "PRD023": "peas",
    "PRD024": "vicia-faba",
    "PRD025": "bowl-one",
    "PRD026": "vegetable-basket",
    "PRD027": "tray",
    "PRD028": "vegetable-basket",
    "PRD029": "vegetable-basket",
}

# Filter bar (channel) — same IconPark outline family.
FILTER_ICONS: dict[str, str] = {
    "all": "view-grid-list",
    "grower": "seedling",
    "baskets": "vegetable-basket",
    "store": "shop",
    "chain": "shopping-mall",
}


def icon_slug_for_product_code(product_code: str) -> str:
    return PRODUCT_CODE_TO_SLUG.get((product_code or "").strip(), DEFAULT_SLUG)


def icon_href(slug: str) -> str:
    """Relative URL fragment for <img src> next to public_report.html."""
    return f"{ICON_SUBDIR}/{slug}.svg"


def augment_publish_product(row: dict) -> None:
    """Mutate rolling publish product dict: add icon_slug + icon_path (in-place)."""
    code = str(row.get("product_id") or "")
    slug = icon_slug_for_product_code(code)
    row["icon_slug"] = slug
    row["icon_path"] = icon_href(slug)


def static_iconpark_dir() -> Path:
    """Package directory containing vendored *.svg files."""
    return Path(__file__).resolve().parent / "static" / "icons" / "iconpark"


def all_vendored_icon_slugs() -> list[str]:
    """Slugs for which a file exists under static_iconpark_dir()."""
    d = static_iconpark_dir()
    if not d.is_dir():
        return []
    return sorted(p.stem for p in d.glob("*.svg"))


def list_output_icon_paths(output_dir: Path) -> list[str]:
    """Relative posix paths under output_dir for FTPS / manifest bookkeeping."""
    d = output_dir / "icons" / "iconpark"
    if not d.is_dir():
        return []
    return sorted(f"{ICON_SUBDIR}/{p.name}" for p in d.glob("*.svg"))


def filter_icon_hrefs() -> dict[str, str]:
    """Relative img src paths for channel filter buttons (same directory convention)."""
    return {channel: icon_href(slug) for channel, slug in FILTER_ICONS.items()}
