# MyFarmAgents — Canonical Glossary
**Version:** 1.0  
**Date:** 2026-03-29  
**Maintainer:** Team 100 (Architecture)

> This glossary is the single source of truth for all terminology used across
> the MyFarmAgents platform. All documents, code, and team communication MUST
> use the English terms listed here. Hebrew equivalents are provided for
> conversations with the project lead (Nimrod) only.

---

## Language Policy

**Rule:** All documents, code, comments, variable names, and inter-team
communication are written in English. This applies to all agents and all teams.

**Exception:** Direct conversation with project lead (Nimrod) may be in Hebrew.

**Enforcement:** Team 100 will reject any document or code review that contains
Hebrew in documentation, code comments, or file names.

---

## Platform & Project Names

| English Term | Hebrew | Notes |
|---|---|---|
| **MyFarmAgents** | מייפארם-איגנטס | The umbrella platform. All agents belong here. |
| **OrganicMarketAgent** | איגנט-מחירון-אורגני | First agent: community organic vegetable price index. |
| **Agent** | איגנט | An autonomous AI-driven service module within MyFarmAgents. |

---

## Core Architecture Terms

| English Term | Hebrew | Code Symbol | Notes |
|---|---|---|---|
| Ingestion Run | ריצת איסוף | `IngestionRun` | Full daily pipeline execution |
| Source Fetch Run | ריצת-מקור | `SourceFetchRun` | Single-source fetch within an ingestion run |
| Raw Asset | נכס-גולמי | `RawAsset` | Saved raw HTTP response (HTML/JSON/PDF) |
| Raw Extracted Item | פריט-גולמי | `RawExtractedItem` | Parsed item before normalization |
| Normalized Observation | תצפית-מנורמלת | `NormalizedObservation` | Core data unit after normalization |
| Daily Aggregate | אגרגט-יומי | `DailyAggregate` | Statistical summary per product per day |
| Weekly Snapshot | תמונת-שבועית | `WeeklySnapshot` | Weekly statistical freeze |
| Publish Run | ריצת-פרסום | `PublishRun` | Artifact build + upload cycle |
| Publish Artifact | קובץ-פרסום | `PublishArtifact` | JSON/HTML file produced by publisher |

---

## Pipeline Components

| English Term | Hebrew | Class | Notes |
|---|---|---|---|
| Collector | אוסף | `CollectorEngine` | Fetches raw data from sources |
| Parser | מפענח | `ParserEngine` | Extracts structured items from raw assets |
| Normalizer | מנרמל | `NormalizerEngine` | Maps raw items to canonical products + prices |
| Aggregator | מאגד | `AggregatorEngine` | Computes statistical aggregates |
| QA Engine | מנוע-בקרה | `QAEngine` | Detects anomalies, duplicates, outliers |
| Publisher | מפרסם | `PublishEngine` | Builds and uploads public artifacts |
| Ingestion Runner | מתזמן-ראשי | `IngestionRunner` | Orchestrates the full daily pipeline |

---

## Data Model Terms

| English Term | Hebrew | Notes |
|---|---|---|
| Product | מוצר | Canonical product entry (e.g. "Tomato") |
| Product Alias | שם-חלופי | Raw name that maps to a canonical product |
| Product Merge | מיזוג-מוצרים | Two product entries treated as one |
| Source | מקור | A data source (farm website, govt site, etc.) |
| Fetch Profile | פרופיל-איסוף | Technical config for how to fetch a source |
| Normalizer Profile | פרופיל-נרמול | Which normalizer type applies to a source |
| Normalizer Rule | כלל-נרמול | A single data-driven rule in the normalizer |
| Approved Scope Skip | דילוג-סקופ-מאושר | `catalog_scope_skip_rules` match → `raw_extracted_items` set to `ignored` with `approved_scope_skip:{category}#{rule_id}` — intentional V1 out-of-scope, not a normalizer failure |
| Observation Flag | דגל-תצפית | Admin/system mark on an observation (hide, review, etc.) |
| Measurement Unit | יחידת-מידה | kg, unit, bunch, basket_small, etc. |
| Unit Conversion | המרת-יחידות | Factor to convert from one unit to another |
| Confidence Score | ציון-אמינות | 0–1 score on a normalized observation |

---

## Publishing Terms

| English Term | Hebrew | Notes |
|---|---|---|
| Manifest | מניפסט | `manifest.json` — pointer to current published artifact |
| Last-Good Manifest | מניפסט-מגובה | `manifest_last_good.json` — fallback when publish fails |
| Artifact Version | גרסת-קובץ | Timestamp-based: `20260329-060000` |
| Staleness Level | רמת-ישנות | `ok` / `warning` (3d) / `stale` (8d) |
| Community Products | מוצרים-קהילתיים | Products from community (non-benchmark) sources |
| Benchmark Products | מוצרי-השוואה | Products from retail/govt benchmark sources |
| Basket Products | מוצרי-סל | CSA baskets — not decomposed to per-kg in V1 |

---

## Team Terms

| English Term | Hebrew | Notes |
|---|---|---|
| Team 100 | צוות-100 | Architecture — owns spec and decisions |
| Team 50 | צוות-50 | QA — validates implementation against spec |
| Team 20 | צוות-20 | Infrastructure — DB, env, skeleton |
| Team 10 | צוות-10 | Feature Dev — collectors, parsers, normalizer, admin UI |
| Gate | שער | Go/no-go decision point between milestones |
| Milestone | אבן-דרך | M1–M7 development phases |

---

## Source Classification Terms

| English Term | Hebrew | Notes |
|---|---|---|
| Community Source | מקור-קהילתי | Small farm, CSA, farm shop — `market_scope=community` |
| Benchmark Source | מקור-השוואה | Retail chain, govt — `market_scope=benchmark` |
| Verification Source | מקור-אימות | Organic certification body |
| Platform Family | משפחת-פלטפורמה | `easyfarm`, `standalone`, `govt`, `aggregator` |
| Discovery Source | מקור-גילוי | Used only for finding new sources, not price data |

---

## Status & Flag Values (code-level, no translation needed)

```
Source status:       active | candidate | deprecated | discovery_only
Ingestion run:       running | completed | partial | failed
Fetch run:           running | success | failed | skipped | timeout
Extraction status:   extracted | normalized | unresolvable | ignored
Observation flag:    ok | review | ignored | hidden
Staleness level:     ok | warning | stale
Publish status:      building | build_failed | uploading | upload_failed | published | aborted
Upload status:       pending | uploaded | failed | skipped
```

---

## File Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Team report | `YYYY-MM-DD_{TOPIC}_{TEAM_ID}.md` | `2026-03-29_M1_COMPLETE_TEAM20.md` |
| Artifact version | `YYYYMMDD-HHmmss` | `20260329-060000` |
| Report JSON | `public_report-{version}.json` | `public_report-20260329-060000.json` |
| Report HTML | `public_report-{version}.html` | `public_report-20260329-060000.html` |
| Raw asset | `{YYYY}/{MM}/{DD}/{SRC_CODE}_{HHmmss}.{ext}` | `2026/03/29/SRC002_143022.html` |
