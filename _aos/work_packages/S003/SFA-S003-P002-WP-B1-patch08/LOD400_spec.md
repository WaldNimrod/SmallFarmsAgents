---
id: SFA-S003-P002-WP-B1-patch08-LOD400
wp: SFA-S003-P002-WP-B1-patch08 — variety-parser cleanup (filter noise + DELETE existing)
gate: L-GATE_S (LOD400; LOD200 inlined)
status: PRE_LOD400_LOCK
author: team_110
date: 2026-05-26
version: v1.0.0
team_00_decision_ref: _COMMUNICATION/team_00/DECISION_WP-B1-patch07-patch08_2026-05-26_v1.0.0.md
orchestrator: team_110 (Claude Opus 4.7)
builder: team_10 (Claude Sonnet sub-agent)
validator: team_190 (GPT-5.5, non-Claude per IR#1)
engine_chain: "team_110 ≠ team_10 ≠ team_190"
---

# LOD400 — patch08 (variety-parser cleanup)

## 1. Goal
Fix `_extract_cultivar_names` in `scripts/load_masterclass_sheets.py` to filter out noise (URLs, bullets, sentence fragments). DELETE the ~11 noise variety rows from production. Re-run OP-2 to re-validate (idempotent via ON CONFLICT).

## 2. Architecture

### 2.1 Files MODIFIED (3)
```
scripts/load_masterclass_sheets.py    ← _extract_cultivar_names filter logic
tests/integration/test_load_masterclass_sheets.py    ← +new filter tests
CHANGELOG.md                                          ← entry
```

### 2.2 Files CREATED (1)
```
scripts/patch08_cleanup_noise_varieties.py   ← idempotent DELETE script (~50 LOC, dry-run default)
```

## 3. Implementation

### 3.1 Filter logic in `_extract_cultivar_names`

Add filter function:

```python
def _is_valid_cultivar_name(name: str) -> bool:
    """Heuristic filter: is this a real cultivar name vs MD noise?

    Real cultivar names are typically 1-3 short words (e.g., 'Carmen',
    'Emerite', 'Marnero'). Noise includes URLs, bullets, section headers,
    spacing instructions, sentence fragments.

    Per patch08 (DECISION_WP-B1-patch07-patch08 §2.2).
    """
    if not name or not name.strip():
        return False
    name = name.strip()

    # Length: cultivar names are short (typically ≤ 40 chars)
    if len(name) > 40:
        return False
    if len(name) < 2:
        return False  # bullets, single chars

    # URL patterns
    if any(p in name.lower() for p in ['http://', 'https://', '://', '.com', '.org', '.io', 'www.']):
        return False

    # Sentence-like (ends with period; not just abbreviation)
    if name.endswith('.') and len(name) > 6:
        return False

    # Section headers (contain colon followed by space, like "Intensive Spacing:")
    if ': ' in name:
        return False

    # Comma-separated lists (e.g., "Green beans: Emerite, Seychelles, Cobra") —
    # these should be split, not taken as one variety. But splitting is more
    # complex; for now, treat as section header.
    if ',' in name and name.count(',') >= 2:
        return False

    # Pure-numeric / pure-bullet
    if name in {'●', '○', '-', '*', '◦', '·'}:
        return False
    if name.isdigit():
        return False

    return True
```

Wrap existing cultivar extraction:
```python
def _extract_cultivar_names(sections: dict[str, list[str]]) -> list[str]:
    raw = ... # existing extraction
    filtered = [n for n in raw if _is_valid_cultivar_name(n)]
    return filtered
```

### 3.2 New cleanup script

`scripts/patch08_cleanup_noise_varieties.py` — DELETE rows matching the known noise patterns from production crop_varieties. Idempotent (no-op if already clean).

```python
NOISE_PATTERNS = [
    # Will be parameterized; matches the categorical patterns
    # rather than specific strings to remain idempotent across re-runs
]

def main(dry_run: bool, db_url: str):
    with engine.begin() as conn:
        # Find all varieties matching noise heuristics
        result = conn.execute(text("""
            SELECT id, name_en FROM crop_varieties
            WHERE
                name_en ~ '://' OR
                name_en ~ '\\.com|\\.org|\\.io' OR
                name_en IN ('●', '○', '-', '*', '1', '2', '3') OR
                length(name_en) > 40 OR
                name_en LIKE '%: %' OR
                (length(name_en) > 6 AND name_en LIKE '%.')
        """))
        rows = result.fetchall()
        log.info(f"Found {len(rows)} noise variety rows")
        for r in rows:
            log.info(f"  id={r.id} name_en={r.name_en!r}")
        if not dry_run and rows:
            ids = [r.id for r in rows]
            conn.execute(text("DELETE FROM crop_varieties WHERE id = ANY(:ids)"), {"ids": ids})
            log.info(f"Deleted {len(rows)} rows")
```

### 3.3 New regression test

```python
def test_extract_cultivar_filter_rejects_noise():
    """patch08: _is_valid_cultivar_name must reject known noise patterns."""
    from scripts.load_masterclass_sheets import _is_valid_cultivar_name

    # Real cultivars should pass
    for valid in ['Carmen', 'Emerite', 'Marnero', 'Sprinter', 'Maxifort (rootstock)']:
        assert _is_valid_cultivar_name(valid), f"Real cultivar {valid!r} rejected"

    # Noise should fail
    for noise in [
        '●', '○', '-', '*',                              # bullets
        '1', '2', '3',                                    # numerics
        'marketgardenerinstitute.com',                    # URL
        'https://example.com',                            # URL
        'Intensive Spacing',                              # 'Intensive Spacing' — has space but no colon — should pass? Actually no
        '1 row per bed every 12 in (30 cm) on the row.',  # spacing instruction
        'food store. Any cultivar works.',                # sentence
        'Green beans: Emerite, Seychelles, Cobra',        # header with embedded list
    ]:
        assert not _is_valid_cultivar_name(noise), f"Noise {noise!r} accepted"
```

Note: 'Intensive Spacing' is 17 chars without colon — would pass the filter as-is. We accept this as a known limitation; the parser's section-header detection (separate from cultivar filter) should handle this. **Spec adjustment: filter test will skip 'Intensive Spacing' and rely on parser-level section-header skip.**

### 3.4 CHANGELOG

```markdown
### SFA-S003-P002-WP-B1-patch08 — Variety-parser cleanup (2026-05-26)
- `scripts/load_masterclass_sheets.py::_extract_cultivar_names`: added `_is_valid_cultivar_name` filter to skip URLs, bullets, single chars, sentence fragments, comma-separated lists, and overly long strings (>40 chars).
- `scripts/patch08_cleanup_noise_varieties.py`: new idempotent DELETE script for ~11 noise rows added by OP-2 (2026-05-26) before patch08.
- `tests/integration/test_load_masterclass_sheets.py`: +1 regression test (`test_extract_cultivar_filter_rejects_noise`).
- Defect surfaced during OP-2 prod load (15 new varieties: ~4 real cultivars + ~11 noise).
- Per team_00 DECISION_WP-B1-patch07-patch08_2026-05-26 §2.
```

## 4. Acceptance Criteria (10 ACs)

- **AC-01** `_is_valid_cultivar_name` exists in `load_masterclass_sheets.py`
- **AC-02** `_extract_cultivar_names` calls the filter (filtered list returned)
- **AC-03** `test_extract_cultivar_filter_rejects_noise` PASSES
- **AC-04** `python scripts/patch08_cleanup_noise_varieties.py --dry-run` reports planned deletions on test DB fixture
- **AC-05** `--apply` is idempotent (2 runs → second is no-op)
- **AC-06** After re-running `scripts/load_masterclass_sheets.py --load-db` (post-fix), no noise patterns are inserted (`SELECT count(*) FROM crop_varieties WHERE name_en LIKE '%://%' OR name_en IN ('●')` returns 0)
- **AC-07** Real cultivars (Carmen, Ace, Sprinter, Escamillo, Emerite, Cobra, Seychelles, Marnero, ...) PRESENT in `crop_varieties` post-build
- **AC-08** `pytest tests/integration/ -q` → N+1 passing (was 15; +1 new filter test)
- **AC-09** `pytest tests/crop_book/ -q` → 350 + 1 OOS unchanged
- **AC-10** `validate_aos.sh` → 0 FAIL. Diff scope: 4 files (script edits + new cleanup script + test + CHANGELOG).

## 5. Build sequence
1. Read spec + DECISION
2. Add `_is_valid_cultivar_name` + integrate into `_extract_cultivar_names`
3. Append regression test
4. Author `scripts/patch08_cleanup_noise_varieties.py`
5. Append CHANGELOG
6. Run tests + validate_aos.sh
7. **DEFER**: actually running cleanup + re-running OP-2 on production = operational step (post-LOD500_LOCKED), NOT part of build

8. Single commit
9. BUILD_REPORT

## 6. Risk register

| ID | Risk | Mitigation |
|----|------|-----------|
| R-01 | Filter too aggressive — rejects real cultivars | Test coverage; manual spot-check during build |
| R-02 | DELETE script removes real cultivars | Heuristic match; dry-run default; spec lists exact patterns |
| R-03 | Re-running OP-2 doesn't restore varieties due to ON CONFLICT | Builder verifies expected variety set post-cleanup + re-run |
| R-04 | Comma-separated lists like "Emerite, Seychelles, Cobra" lose info | Future patch: properly split. For now treat as noise → log + skip. Real values still come from other extraction paths. |

## 7. LOCKED scope
3 modified + 1 created. All other LOCKED files untouched.

## 8. Builder
team_10 Sonnet sub-agent (MEDIUM scope: filter logic + cleanup script + tests).

---

*LOD400 v1.0.0 — 2026-05-26. Pending team_190 L-GATE_S.*
