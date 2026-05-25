---
id: DECISION_SFA-S003-P002-WP-B3-WHITELIST_2026-05-25_v1.0.0
from: team_00 (Principal)
to: [team_110, team_190]
date: 2026-05-25
type: DECISION
wp: SFA-S003-P002-WP-B3
project: smallfarmsagents
authority: team_00 Principal (CLAUDE.md Directory Authority)
authorizes:
  - SFA-S003-P002-WP-B3 LOD400 Tend task whitelist scope (advisory #3 per PRE_HANDOFF_VERDICT)
  - SFA-S003-P002-WP-B3 GCR-B3-1 (TASK_TYPE_VALUES tuple extension by 6 entries)
---

# DECISION — SFA-S003-P002-WP-B3 Tend Task Whitelist + GCR-B3-1

## 1. Decision summary

team_00 (Nimrod, Principal) on 2026-05-25 authorized **Option B** for the WP-B3 Tend task whitelist, after team_110 presented a full distribution analysis of all 21 Task Type values across the live `Tend_2022/TASKS.CSV` (798 rows).

### Confirmed whitelist (11 categories, 758 rows = 95.0% coverage)

| # | Tend Task Type | Rows | Source-of-truth |
|---|----------------|------|------------------|
| 1 | `Transplant` | 234 | PROGRAM_BRIEF §4 original 9 |
| 2 | `Greenhouse Sow` | 143 | PROGRAM_BRIEF §4 original 9 |
| 3 | `Direct Sow` | 124 | PROGRAM_BRIEF §4 original 9 |
| 4 | `Weed` | 78 | PROGRAM_BRIEF §4 original 9 |
| 5 | `Row Cover & Mulch` | 55 | PROGRAM_BRIEF §4 original 9 |
| 6 | `Stale Bed` | 42 | PROGRAM_BRIEF §4 original 9 |
| 7 | `Pest & Disease` | 27 | PROGRAM_BRIEF §4 original 9 |
| 8 | `Potting up` | 16 | PROGRAM_BRIEF §4 original 9 |
| 9 | `Thin` | 7 | PROGRAM_BRIEF §4 original 9 |
| 10 | `Trellis` | 13 | **Option-B addition** — recurring template on tomatoes/peppers |
| 11 | `Fertilize & Amend` | 13 | **Option-B addition** — recurring template (Methods: Spread, Foliar feed, Incorporate) |

### Confirmed blacklist (10 categories, 40 rows = 5.0%)

| Tend Task Type | Rows | Rationale |
|----------------|------|-----------|
| `Greenhouse Activity` | 16 | Mixed content (mostly `GH Saw - השלמות` gap-fills, not template) |
| `Cultivation & Tillage` | 6 | Single-crop (Carrots only); 0.75% coverage value — not worth enum scope |
| `Maintenance` | 6 | Non-template |
| `Prune` | 6 | Low volume; overlaps `hand_weed` semantically |
| `השלמות שתילה` | 4 | Replanting gap-fills (not template) |
| `Irrigate` | 3 | Per-event, not recurring template |
| `Seed Cleaning` | 2 | Back-office |
| `Drill Sow` | 1 | Single occurrence |
| `ריכוז שעות` | 1 | Labor-tracking artifact |
| `הידרופוניקה` | 1 | Single occurrence |

## 2. GCR-B3-1 authorization

team_00 also authorizes **GCR-B3-1**: a scoped exception allowing WP-B3 to modify the LOD500_LOCKED `organic_market_agent/crop_book/crop_task_templates.py` file to append exactly 6 string entries to the `TASK_TYPE_VALUES` tuple. Authorized values:

```python
"nursery_seed", "pest_spray", "potting_up", "thinning", "trellis", "fertilize"
```

Total tuple size after extension: 20 entries (14 B1 baseline + 6 B3 additions).

Rationale: the migration 046 CHECK constraint extension must be mirrored at the ORM level to keep validation symmetric (DB ↔ Python tuple consistency); otherwise B1's existing tests and B3's new tests diverge.

No other modification of `crop_task_templates.py` is authorized — no new column, no method change, no class restructure. Verifiable by `git diff <patch01-lock>..HEAD -- organic_market_agent/crop_book/crop_task_templates.py` showing only the tuple extension + a section comment.

## 3. Authorization chain

This DECISION is itself an Iron Rule #4 exception (team_00 Principal directly authorizing under CLAUDE.md Directory Authority, bypassing the normal team_100 ↔ team_110 routing). Pattern matches the prior `DECISION_SFA-S003-P002-WP-A-LOD200_2026-05-23_v1.0.0.md` precedent (the WP-A GCR_1 authorization for the 3 trust columns).

The DECISION will be referenced by:
- B3 LOD400 §6 (whitelist constant definition)
- B3 LOD400 §10 + §12 (advisory #3 disposition)
- L-GATE_S R1 mandate to team_190 (mandate §1 cites this file as the team_00 sign-off evidence)

## 4. Evidence

Distribution analysis run by team_110 on 2026-05-25 against the live workbook:
```
$ python3 - <<'PY'
import csv
from collections import Counter
with open("/Users/nimrod/Documents/israel Microgreens/crop data/Tend_2022/TASKS (from macBook Air - nimrod).CSV") as f:
    rows = list(csv.DictReader(f))
c = Counter(r["Task Type"].strip() for r in rows)
for tt, n in c.most_common():
    print(f"  {n:>4}  {tt!r}")
PY
```

Output (21 distinct values, 798 rows) reviewed by team_00 alongside the 3-option proposal (A=conservative 91% / B=recommended 95% / C=maximum 96.5%). team_00 selected B with explicit consideration of:
- Trellis IS recurring template on tomatoes (Plantings field populated)
- Fertilize & Amend IS recurring template (Methods: Spread / Foliar feed / Incorporate)
- Cultivation & Tillage / Prune / Greenhouse Activity excluded for low volume + ambiguity

## 5. Disposition

- **Whitelist scope:** FROZEN per this DECISION. B3 LOD400 §6 implements verbatim.
- **GCR-B3-1:** AUTHORIZED. B3 LOD400 §5 + §10 implements the scoped tuple extension.
- **Future changes:** if a future Tend year (e.g., Tend_2023) introduces new Task Type values, file a new DECISION (this one is year-scoped to the Tend_2022 distribution).

---

*DECISION authored 2026-05-25 by team_110 (Claude Opus 4.7) on behalf of team_00's in-session approval. Filed alongside L-GATE_S R1 mandate per the established AOS Iron Rule #4 exception protocol.*
*team_00 Principal authority — CLAUDE.md Directory Authority table.*
