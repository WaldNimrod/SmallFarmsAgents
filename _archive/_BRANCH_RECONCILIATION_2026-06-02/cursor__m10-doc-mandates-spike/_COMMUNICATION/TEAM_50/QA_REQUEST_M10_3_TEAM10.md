# QA Review Request — M10.3 Static Parsers

**From:** Team 10  
**To:** Team 50  
**Date:** 2026-04-04  
**Mandate:** MANDATE-20260404-M10-3-STATIC-PARSERS  

## Deliverables

1. Completion report: `_COMMUNICATION/TEAM_10/reports/2026-04-04_M10_3_STATIC_PARSERS_COMPLETE_TEAM10.md`
2. HTML notes: `_COMMUNICATION/TEAM_10/reports/2026-04-04_M10_3_STATIC_HTML_ANALYSIS_SRC027_SRC028_TEAM10.md`
3. Code: `nizat.py`, `rexail.py`, `eranorgani.py`, `tamari.py`, `selector_catalog.py`, `parsers/engine.py`, `models/normalizer.py`
4. Migrations: `036`–`039` (`036_m10_3_static_parser_sources.py` through `039_m10_3_src025_residual.py`)

## Canonical execution (Team 50 agent)

Execute **`_COMMUNICATION/TEAM_50/QA_MANDATE_M10_G10_TEAM50.md`** (includes M10.3 metrics: **≥80** products, live page, upload).

## Requested QA actions

1. Verify **ingestion outcomes** for **SRC025–SRC028** in DB (raw row counts and normalization) per Team 10 completion report; mandate T03–T05 cover acceptance.
2. Confirm **≥85%** resolution **per** new source and **≥90%** community aggregate after dictionary pass.
3. Confirm **≥80** published products and successful **upload** when FTPS enabled.
4. File PASS/FAIL under `_COMMUNICATION/TEAM_50/reports/`.

## Note

Sources are set **active** in migration **036**; pause ingestion in non-prod if required by environment policy.
