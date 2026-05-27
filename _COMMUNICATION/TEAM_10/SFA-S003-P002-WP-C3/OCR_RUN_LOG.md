# OCR Run Log — WP-C3 Curtis Stone Images

**Date:** 2026-05-27
**Source images:** `data/external_sources/urban_farmer/L41_curtis_chart_01–27.jpg`
**Output cache:** `data/external_sources/extracted/curtis_ocr/`

## Summary

| Metric | Value |
|--------|-------|
| Images found | 27 |
| Images processed | 27 |
| Images skipped (cache hit) | 0 |
| Errors | 0 |
| OCR engine | tesseract-5 (fallback — ANTHROPIC_API_KEY not set) |
| Cumulative cost | $0.00 |
| Budget limit | $4.50 |

**AC-C3-02: 27/27 JSONs cached — PASS**

## Spec discrepancy

Spec (BUILDER_MANDATE §4.3) states 34 images; actual repo has **27** JPG files
(L41_curtis_chart_01 through L41_curtis_chart_27). Achieved 100% (27/27) of
available images. Discrepancy noted for team_190 at L-GATE_V.

## OCR quality note

All 27 images were processed via tesseract-5 (the Anthropic Vision API fallback
path, since `ANTHROPIC_API_KEY` is not set in this environment). Tesseract on
complex book-layout scanned pages extracts raw text without structured crop
identification — the `crop` field in each JSON typically contains the page
header ("Crops for the Urban Farmer NNN") rather than the crop name.

The `curtis_ocr_importer.py` compensates via keyword scanning of `narrative_text`
with an ambiguity threshold of 4 distinct crops per page, yielding **10 distinct
crop notes** in `crop_knowledge_notes` (AC-C3-03: ≥10 — PASS).

If the Anthropic Vision API becomes available, re-running `scripts/ocr_curtis_images.py`
with `ANTHROPIC_API_KEY` set will overwrite the cached JSONs with structured
`crop` fields and richer `varieties` lists, improving note attribution.

## Per-image log

| Image | Status | Model |
|-------|--------|-------|
| L41_curtis_chart_01 | ok | tesseract-5 |
| L41_curtis_chart_02 | ok | tesseract-5 |
| L41_curtis_chart_03 | ok | tesseract-5 |
| L41_curtis_chart_04 | ok | tesseract-5 |
| L41_curtis_chart_05 | ok | tesseract-5 |
| L41_curtis_chart_06 | ok | tesseract-5 |
| L41_curtis_chart_07 | ok | tesseract-5 |
| L41_curtis_chart_08 | ok | tesseract-5 |
| L41_curtis_chart_09 | ok | tesseract-5 |
| L41_curtis_chart_10 | ok | tesseract-5 |
| L41_curtis_chart_11 | ok | tesseract-5 |
| L41_curtis_chart_12 | ok | tesseract-5 |
| L41_curtis_chart_13 | ok | tesseract-5 |
| L41_curtis_chart_14 | ok | tesseract-5 |
| L41_curtis_chart_15 | ok | tesseract-5 |
| L41_curtis_chart_16 | ok | tesseract-5 |
| L41_curtis_chart_17 | ok | tesseract-5 |
| L41_curtis_chart_18 | ok | tesseract-5 |
| L41_curtis_chart_19 | ok | tesseract-5 |
| L41_curtis_chart_20 | ok | tesseract-5 |
| L41_curtis_chart_21 | ok | tesseract-5 |
| L41_curtis_chart_22 | ok | tesseract-5 |
| L41_curtis_chart_23 | ok | tesseract-5 |
| L41_curtis_chart_24 | ok | tesseract-5 |
| L41_curtis_chart_25 | ok | tesseract-5 |
| L41_curtis_chart_26 | ok | tesseract-5 |
| L41_curtis_chart_27 | ok | tesseract-5 |
