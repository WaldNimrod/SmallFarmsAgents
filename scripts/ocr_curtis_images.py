"""One-time OCR pipeline for Curtis Stone scanned book pages (L41).

Usage:
    python3 scripts/ocr_curtis_images.py

Reads: data/external_sources/urban_farmer/L41_curtis_chart_NN.jpg
Writes: data/external_sources/extracted/curtis_ocr/L41_curtis_chart_NN.json
        data/external_sources/extracted/curtis_ocr/_ocr_log.json

Strategy: Anthropic Vision API (claude-haiku) preferred; tesseract fallback.
Idempotency: existing cache files are skipped.
Budget guard: aborts if cumulative cost exceeds $4.50.
"""

from __future__ import annotations

import base64
import json
import logging
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass, field
from decimal import Decimal
from pathlib import Path

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[1]
_IMAGE_DIR = _REPO_ROOT / "data" / "external_sources" / "urban_farmer"
_CACHE_DIR = _REPO_ROOT / "data" / "external_sources" / "extracted" / "curtis_ocr"
_OCR_LOG = _CACHE_DIR / "_ocr_log.json"

_BUDGET_CAP = Decimal("4.50")
_HAIKU_INPUT_COST_PER_1M = Decimal("0.80")   # claude-haiku-4-5 input $/1M tokens
_HAIKU_OUTPUT_COST_PER_1M = Decimal("4.00")  # claude-haiku-4-5 output $/1M tokens


@dataclass
class OcrEntry:
    image_id: str
    status: str       # "ok" | "error" | "skipped"
    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    error: str = ""


def _encode_image(path: Path) -> str:
    return base64.standard_b64encode(path.read_bytes()).decode("utf-8")


_VISION_PROMPT = (
    "You are processing a scanned page from 'The Urban Farmer' by Curtis Stone. "
    "Extract structured growing information and return JSON with these keys:\n"
    "  crop (string), planting_specs (string), varieties (list of strings), "
    "  dtm (integer or null, days to maturity), "
    "  avg_yield_per_bed (string), avg_gross_profit_per_bed (string), "
    "  narrative_text (string — key growing notes, max 1800 chars).\n"
    "Return ONLY valid JSON, no markdown fences."
)


def _call_anthropic_vision(image_path: Path) -> tuple[dict, int, int]:
    """Call Anthropic Vision API. Returns (parsed_json, input_tokens, output_tokens)."""
    import anthropic  # lazy import — only needed when API available

    client = anthropic.Anthropic()
    b64 = _encode_image(image_path)
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": b64,
                    },
                },
                {"type": "text", "text": _VISION_PROMPT},
            ],
        }],
    )
    raw = message.content[0].text.strip()
    # Strip markdown fences if model added them anyway
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    parsed = json.loads(raw)
    return parsed, message.usage.input_tokens, message.usage.output_tokens


def _call_tesseract(image_path: Path) -> str:
    """Run tesseract OCR and return raw text."""
    with tempfile.NamedTemporaryFile(suffix="", delete=False) as tf:
        out_base = tf.name
    try:
        result = subprocess.run(
            ["tesseract", str(image_path), out_base, "--oem", "1", "--psm", "6"],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode != 0:
            raise RuntimeError(f"tesseract failed: {result.stderr}")
        out_txt = Path(out_base + ".txt")
        return out_txt.read_text(encoding="utf-8", errors="replace").strip() if out_txt.exists() else ""
    finally:
        for ext in ("", ".txt"):
            Path(out_base + ext).unlink(missing_ok=True)


def _tesseract_to_json(image_id: str, text: str) -> dict:
    """Convert raw tesseract text to structured JSON heuristically."""
    # Try to extract crop name from first non-empty line
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    crop = lines[0] if lines else image_id

    # Heuristic: look for DTM-like pattern "NN days"
    dtm = None
    m = re.search(r"\b(\d{2,3})\s*days?\b", text, re.IGNORECASE)
    if m:
        dtm = int(m.group(1))

    return {
        "crop": crop,
        "planting_specs": "",
        "varieties": [],
        "dtm": dtm,
        "avg_yield_per_bed": "",
        "avg_gross_profit_per_bed": "",
        "narrative_text": text[:1800],
    }


def _load_log() -> list[dict]:
    if _OCR_LOG.exists():
        return json.loads(_OCR_LOG.read_text())
    return []


def _save_log(entries: list[OcrEntry]) -> None:
    _OCR_LOG.write_text(json.dumps([asdict(e) for e in entries], indent=2))


def run_ocr(image_dir: Path = _IMAGE_DIR, cache_dir: Path = _CACHE_DIR) -> list[OcrEntry]:
    """Process all L41 images; return OcrEntry list."""
    cache_dir.mkdir(parents=True, exist_ok=True)

    images = sorted(image_dir.glob("L41_curtis_chart_*.jpg"))
    if not images:
        logger.warning("No L41 images found in %s", image_dir)
        return []

    use_api = bool(os.environ.get("ANTHROPIC_API_KEY"))
    if not use_api:
        logger.warning("ANTHROPIC_API_KEY not set — using tesseract fallback")

    entries: list[OcrEntry] = []
    cumulative_cost = Decimal("0")

    for img_path in images:
        image_id = img_path.stem
        cache_path = cache_dir / f"{image_id}.json"

        if cache_path.exists():
            logger.info("Cache hit: %s — skipping", image_id)
            entries.append(OcrEntry(image_id=image_id, status="skipped"))
            continue

        entry = OcrEntry(image_id=image_id, status="error")
        try:
            if use_api:
                # Budget guard
                if cumulative_cost >= _BUDGET_CAP:
                    logger.error("Budget cap $%.2f reached — aborting", _BUDGET_CAP)
                    entry.status = "error"
                    entry.error = "budget_cap_reached"
                    entries.append(entry)
                    break

                parsed, in_tok, out_tok = _call_anthropic_vision(img_path)
                cost = (
                    Decimal(in_tok) / 1_000_000 * _HAIKU_INPUT_COST_PER_1M
                    + Decimal(out_tok) / 1_000_000 * _HAIKU_OUTPUT_COST_PER_1M
                )
                cumulative_cost += cost
                entry.model = "claude-haiku-4-5-20251001"
                entry.input_tokens = in_tok
                entry.output_tokens = out_tok
                entry.cost_usd = float(cost)
            else:
                text = _call_tesseract(img_path)
                parsed = _tesseract_to_json(image_id, text)
                entry.model = "tesseract-5"

            # Enforce narrative_text bound
            if "narrative_text" in parsed:
                parsed["narrative_text"] = parsed["narrative_text"][:1800]

            parsed["image_id"] = image_id
            cache_path.write_text(json.dumps(parsed, ensure_ascii=False, indent=2))
            entry.status = "ok"
            logger.info("OCR ok: %s (model=%s)", image_id, entry.model)

        except Exception as exc:
            entry.error = str(exc)
            logger.error("OCR error %s: %s", image_id, exc)

        entries.append(entry)

    _save_log(entries)
    ok = sum(1 for e in entries if e.status == "ok")
    skipped = sum(1 for e in entries if e.status == "skipped")
    total = len(images)
    logger.info("OCR complete: %d ok, %d skipped, %d total. Cost: $%.4f",
                ok, skipped, total, float(cumulative_cost))
    return entries


if __name__ == "__main__":
    logging.basicConfig(
        format="%(levelname)s %(name)s: %(message)s",
        level=logging.INFO,
        stream=sys.stdout,
    )
    entries = run_ocr()
    ok = sum(1 for e in entries if e.status == "ok")
    skipped = sum(1 for e in entries if e.status == "skipped")
    total_images = len(sorted(_IMAGE_DIR.glob("L41_curtis_chart_*.jpg")))
    print(f"\nSummary: {ok} newly processed, {skipped} from cache, {total_images} total images.")
    errors = [e for e in entries if e.status == "error"]
    if errors:
        print(f"Errors ({len(errors)}): {[e.image_id for e in errors]}")
        sys.exit(1)
