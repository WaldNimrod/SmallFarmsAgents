---
artifact: INQUIRY
topic: ANTHROPIC_API_KEY_MISSING
wp: SFA-S003-P002-WP-C2
from: team_10 (sfa_build)
to: team_00 (Nimrod)
date: 2026-05-27
priority: BLOCKER
---

# INQUIRY — Anthropic API Key Missing (WP-C2 Extraction Blocked)

## Status

WP-C2 code construction is **COMPLETE** (migration 053, 7 importers, extraction harness, seed.py wiring,
17 tests passing, validate_aos.sh 29/19/0). However, the **LLM extraction phase is BLOCKED** because
`ANTHROPIC_API_KEY` is not set in the current shell environment.

## What is blocked

The one-time extraction step that populates the JSON cache:

```bash
python3 scripts/extract_jmf_he.py --source aosnot --all      # L02 AOSNOT (HIGHEST PRIORITY)
python3 scripts/extract_jmf_he.py --source sham_variety_trials  # L11
python3 scripts/extract_jmf_he.py --source sham_hydro_guide    # L09
python3 scripts/extract_jmf_he.py --source zacks_leafy_survey  # L10
python3 scripts/extract_jmf_he.py --source jmf_ft_nurseryseeding_ext  # L14
python3 scripts/extract_jmf_he.py --source jmf_ft_seedingincellflats  # L16
python3 scripts/extract_jmf_he.py --source jmf_cover_crops_narrative  # L13
```

Without extraction, these ACs cannot be verified:
- AC-C2-02: L02 ≥20 crop JSONs
- AC-C2-03: frost_tolerance / israeli_regions / flowering_date ≥80% coverage
- AC-C2-04: L11 ≥5 lettuce variety_trial_score rows
- AC-C2-05: L09 ≥10 hydro_suitability rows
- AC-C2-07: L14/L16/L13 nursery_specific + growing_tip populated
- crop_knowledge_notes 200+ rows target

## What IS complete (no API key needed)

- Migration 053 applied (PostgreSQL + SQLite-safe)
- `NOTE_TYPE_VALUES` extended 13 → 19
- 7 NI importer classes built and importable
- `scripts/extract_jmf_he.py` written (awaits API key to run)
- `seed.py`: `--c2-only`, `--no-c2`, `_run_c2_ingestion()` wired
- 17 tests passing (all use fixture JSON, no API call)
- validate_aos.sh: 29/19/0
- Stub `--dry-run` extraction generates 6 stub cache files (4 rows in DB)

## Request

Please provide `ANTHROPIC_API_KEY` so extraction can be run:

```bash
export ANTHROPIC_API_KEY=<key>
python3 scripts/extract_jmf_he.py --source aosnot --all
# (then remaining sources)
python3 -m organic_market_agent.crop_book.importer.seed --c2-only
```

Budget cap is $20 (logged to `data/external_sources/extracted/_extraction_log.json`).
The harness will STOP automatically if this limit is reached.

team_10 / sfa_build
2026-05-27
