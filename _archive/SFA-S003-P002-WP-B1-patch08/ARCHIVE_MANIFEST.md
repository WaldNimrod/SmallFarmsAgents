---
id: ARCHIVE_MANIFEST_SFA-S003-P002-WP-B1-patch08
wp: SFA-S003-P002-WP-B1-patch08 — variety-parser cleanup
status: LOD500_LOCKED
closed_at: "2026-05-26"
orchestrator: team_110 (Claude Opus 4.7)
builder: team_10 (Claude Sonnet sub-agent)
validator: team_190 (GPT-5.5 — non-Claude per IR#1)
---

# Archive Manifest — patch08

## 1. Gate chain
| Gate | Result | Commit |
|------|--------|--------|
| L-GATE_E | PASS (team_00 via DECISION) | — |
| L-GATE_S R1 | FAIL (1 BLOCKER F-S-PATCH08-01: 'Intensive Spacing' not caught) | `aada1e0` |
| L-GATE_S R2 | PASS clean | `f455b38` |
| L-GATE_BUILD | BUILD_COMPLETE (Sonnet) | `7645860` (build+report bundled — see §4 MINOR) |
| L-GATE_V R1 | PASS_WITH_FINDINGS (1 MINOR process) | `dd41e1f` |

## 2. Deliverables
- `scripts/load_masterclass_sheets.py` — `KNOWN_SECTION_HEADERS` frozenset + `_is_valid_cultivar_name` integrated into `_extract_cultivar_names`
- `scripts/patch08_cleanup_noise_varieties.py` (NEW) — idempotent DELETE
- `tests/integration/test_load_masterclass_sheets.py` — +1 regression test
- `CHANGELOG.md` entry

## 3. ADR042 closure
| Step | Outcome |
|------|---------|
| 1 | This archive manifest |
| 2 | Roadmap: DONE / LOD500_LOCKED / L-GATE_V / closed_at / archive_ref |
| 3 | validate_aos.sh: 29 / 19 / 0 FAIL ✓ |

## 4. Findings disposition
| Round | Severity | Finding | Resolution |
|-------|----------|---------|------------|
| L-GATE_S R1 | BLOCKER | F-S-PATCH08-01: 'Intensive Spacing' bypassed generic heuristics | RESOLVED v1.0.1 (KNOWN_SECTION_HEADERS allowlist) |
| L-GATE_V R1 | MINOR | VC-V8: build commit `7645860` bundled BUILD_REPORT artifact with the 4 product files; report commit `083aadc` was empty marker | Acknowledged — Sonnet builders to keep build/report commits separate going forward. Non-blocking; product scope clean; roadmap untouched. |

## 5. Iron Rules
- IR#1 cross-engine ✅
- IR#4 single-writer roadmap ✅
- IR#11 governance untouched ✅

## 6. Operational follow-up
- `python scripts/patch08_cleanup_noise_varieties.py --apply` against production Postgres to remove the ~11 noise variety rows from OP-2 (idempotent — safe).

---

*Archive manifest 2026-05-26 by team_110.*
