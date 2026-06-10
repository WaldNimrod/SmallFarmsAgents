# DECISION — SFA-S003-P004-WP-CB-SRC-SWEEP — team_100 — v1.0.0

**Date:** 2026-06-11
**Author:** team_100
**WP:** SFA-S003-P004-WP-CB-SRC-SWEEP
**Type:** DECISION (source deprioritization)
**Approved by:** team_00 (Nimrod), in-session 2026-06-10

## Decision

The following 5 source artifacts under `data/` are **deprioritized — marked NOT RELEVANT to the SFA crop
book** and will NOT be integrated into the DB. Per the WP done-criterion, each is hereby explicitly
recorded via this DECISION (the alternative to DB integration). They are retained on disk for audit only.

| # | Source | Why not relevant | team_00 call |
|---|--------|------------------|--------------|
| 1 | `data/external_sources/israeli/L43_customer_leafy_greens.xlsx` | **Business economics**, not agronomy: cost-per-head, P&L, "Income 2026", vertical-farm space/sales models. Belongs (if ever) to a unit-economics domain, not the crop knowledge book. | "לזנוח — לסמן לא רלוונטי למערכת שלנו" |
| 2 | `data/external_sources/israeli/L44_israel_organic_greens.pdf` | **Mislabeled junk**: extraction is an OCR-mangled LED grow-light spec sheet ("700Wmax", "Made in Israel" reversed); 0 Hebrew characters; no agronomic content. | "לזנוח — לסמן לא רלוונטי" |
| 3 | `data/external_sources/jmf_extension/L26_BEIN_HATLAMIM_hebrew.pdf` | **Mislabeled junk**: the PDF is a bank transfer receipt (₪2,964 to "חוות בין התלמים" for produce). Filename = farm name only; no growing guide inside. | "לזנוח — לסמן לא רלוונטי" |
| 4 | `data/external_sources/misc_investigate/L38_libretto_orto_italian.pdf` | Italian vegetable guide, but the PDF is image-based and OCR produced ~2 non-empty lines — no extractable text. Low priority (already flagged in the handoff). Would need OCR + translation for marginal, likely-duplicate generic content. | "לזנוח — לסמן לא רלוונטי" |
| 5 | `jmf_book_alt` (importer `ni/jmf_book_alt.py`; dir `data/jmf/extracted/jmf_book_alt/`) | The alternate "Market Gardener" edition **source PDF does not exist** (empty dir). Nothing to extract; the main `jmf_book` edition is fully integrated (45 notes / 20 crops). | implicit (no source) |

## Consequences

- No DB rows, no extractor, no importer wiring are added for these 5.
- The `jmf_book_alt` importer remains registered (it no-ops on the empty dir — harmless) for the case a
  future DECISION supplies the source PDF.
- WP done-criterion satisfied: **every `data/` source is now either integrated (DB-confirmed rows) or
  explicitly deprioritized via this DECISION.**

## Reversal

Reviving any of these requires a new DECISION. L43 specifically may warrant a separate unit-economics WP if
business/cost modelling is later wanted in the product (it is genuine data, just out of crop-book scope).
