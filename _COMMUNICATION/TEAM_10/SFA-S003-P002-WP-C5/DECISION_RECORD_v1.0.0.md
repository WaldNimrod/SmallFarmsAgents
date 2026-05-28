---
id: DECISION_RECORD_SFA-S003-P002-WP-C5_v1.0.0
from: team_10
to: team_00 + team_100
date: 2026-05-28
type: decision_record
wp: SFA-S003-P002-WP-C5
authority: team_00 in-session 2026-05-28
status: APPROVED
---

# Decision Record — WP-C5 Cleanup Phase

team_00 approved 5 decisions on 2026-05-28 after data-state review showed
crop name duplicates, anonymous variety orphans, and a new WR trust tier
without governance integration. This record canonicalizes the decisions
before cleanup execution.

---

## Decision 1 — Basil consolidation

**Approved: MERGE**

`crop_id=58 'בזיליקום'` → merge into `crop_id=4 'בזיל'`
- crop 58 has 1 variety (vid=461) with 9 source_values, 0 enrichment
- crop 4 has 6 varieties, 32 sv, 71 enrichment

**Action:**
1. `UPDATE crop_varieties SET crop_id=4 WHERE crop_id=58`
2. variety 461 becomes a non-default variant of crop 4
3. `DELETE FROM crops WHERE id=58`

---

## Decision 2 — Tomato consolidation (Option A — separate but clean)

**Approved: Option A — keep both crops, merge anonymous orphans within each**

Final state:
- `crop_id=49 'עגבנייה'` (Tomatoes) — 15 named varieties + 1 default
- `crop_id=73 'עגבניית שרי'` (Cherry Tomato) — 1 default (with all consolidated sv)

**Anonymous orphan merges**:

For crop 49 (עגבנייה) — merge into vid 233 (default):
- vid 222 "Generic Variety" (17 sv) → 233 (likely duplicate of default)
- vid 403 (None, 57 sv) → 233
- vid 404 (None, 36 sv) → 233
- vid 405 (None, 57 sv) → 233
- vid 406 (None, 18 sv) → 233
- vid 227 "montecarlo F.1" (18 sv) → 225 "hyd. montecarlo F1" (named duplicate)
- vid 229 "Lobelo - חישתיל מורכב" → 226 "Lobelo hyd. מורכב" (named duplicate)

For crop 73 (עגבניית שרי) — merge into vid 460 (default):
- vid 443 (None, 8 sv) → 460
- vid 444 (None, 3 sv) → 460
- vid 445 (None, 1 sv) → 460
- vid 477 (None, 9 sv) → 460  (current "default" with low data — verify before merge)

**Idempotency**: source_value rows have UNIQUE(variety_id, field_name, source).
When merging, use ON CONFLICT DO NOTHING; conflicting rows are kept on the
target (default) variety.

---

## Decision 3 — Bean consolidation

**Approved: MERGE under crop_id=6, "default = מטפסת (Pole/climbing)"**

Current state:
- `crop_id=6 'שעועית'` — 8 varieties, 40 sv  ← KEEP as primary
- `crop_id=59 'שעועית שיחית'` — 1 variety (vid 476), 0 sv  ← MERGE
- `crop_id=60 'שעועית מטפסת'` — 9 varieties (8 with nonsense names from bad import, 1 default vid 479), 1 sv  ← MERGE + CLEANUP

**Action:**
1. Rename crop 6 name_en from `'Beans: Bush & Pole'` to `'Beans (default: Pole/Climbing)'`
2. Move all valid varieties from crop 60 → crop 6 (filter out nonsense names like `'●'`, `'1'`, `'marketgardenerinstitute.com'`, `'Intensive Spacing'`)
   - The 9 vid varieties in crop 60: mostly nonsense from a bad import; only vid 479 (default, 1 sv) is real → merge to crop 6 default
3. Move vid 476 (crop 59 default) → crop 6 as `is_default=False`, `name_en='Bush variant'`
4. `DELETE FROM crops WHERE id IN (59, 60)`
5. DELETE nonsense varieties (those with 0 sv and obviously bad names)

---

## Decision 4 — WP-C6 (Sparse Crops Future Expansion)

**Approved: register as PROPOSED + write LOD200 spec**

Scope: ~20 sparse crops (≤2 enriched fields), mostly:
- 12 herbs (מרווה, טימין, טרגון, נענע, לימון בלם, etc.)
- 5 specialty (ג'ינג'ר, כורכום, ארטישוק ירושלמי, פאק צ'וי, תפוז)
- 3 new vegetables (בזיליקום post-merge sub-variety, etc.)

Future sources to investigate:
- ICARDA / CIHEAM (Mediterranean herbs)
- Wikipedia Hebrew (עשבי תיבול)
- JMF book chapters not yet extracted
- team_00 EX overrides for confident-knowledge fields

LOD200 placeholder at `_aos/work_packages/S003/SFA-S003-P002-WP-C6/LOD200_spec.md`.
Not for execution now — register in roadmap as PROPOSED.

---

## Decision 5 — WR tier weight + ★ DB-driven weights architecture

**Approved: Option B (WR = 0.60) — WITH CRITICAL REQUIREMENT**

**team_00 requirement (verbatim):**
> "זה חייב להיות שמור בבסיס הנתונים בצורה נפרדת כך שיתאפשר שינוי משקלים
> באופן קל ופשוט לכלל המערכת בהמשך בהתאם לנסיון בשטח והתוצר הסופי שיתקבל
> והמשוב שנקבל מהחקלאים."

**Translation**: weights must be stored in the DB in a separate way that
allows easy system-wide weight changes later based on field experience,
final output, and farmer feedback.

### Architectural change required

Replace Python-constant `SOURCE_REGISTRY` with a DB-backed table:

**New table `crop_source_weights`** (migration 054):
- `source_label` (exact label OR prefix pattern like `'WR:*'`)
- `trust_tier` (EX/NI/PR/OP/MK/WB/UC/WR)
- `weight` (NUMERIC(5,4), NULL = hard override)
- `is_hard_override` BOOLEAN
- `requires_moderation` BOOLEAN
- `notes` TEXT (rationale, last-tuned-by, etc.)
- `updated_at` TIMESTAMP (for audit)

**Helper module** `source_weights_db.py`:
- `get_source_spec(source_label) -> SourceSpec` reads from DB with in-process cache
- Fallback chain: exact match → prefix pattern → unknown-source default

**Reconciler integration**:
- `source_registry.py` becomes a thin facade calling `source_weights_db`
- Existing `SOURCE_REGISTRY` Python constant kept as default seed only

### Seed values (migration 055)

| source_label | trust_tier | weight | notes |
|--------------|-----------|--------|-------|
| `team_00` | EX | NULL (hard) | Principal authority |
| `JMF`, `PR:*` | PR | 0.70 | Published research (university extension) |
| `Tend_*`, `OP:*` | OP | 0.55 | Operational farm data |
| `NI:*` | NI | NULL (hard) | Nimrod-curated narrative |
| **`WR:*`** | **WR** | **0.60 ★** | **AI-synthesized research (LLM-derived)** |
| `MK:*` | MK | 0.40 | Market data (placeholder) |
| `WB:*` | WB | 0.30 | Web blog (placeholder) |
| `UC:*` | UC | NULL (moderation) | User-contributed |

WR weight = **0.60 (Option B — Moderate)** rationale:
- Higher than OP (0.55): synthesized research draws on multiple published sources
- Lower than PR (0.70): not first-party / peer-reviewed
- Sufficient for solo coverage on new crops (single-source confidence = 0.60)
- Loses to PR when both present (as expected)
- Tunable later via DB UPDATE — single SQL statement system-wide

### Future tuning workflow

When team_00 receives farmer feedback:
```sql
UPDATE crop_source_weights
SET weight = 0.65,
    notes = 'increased after farmer feedback Q3-2026 — IL research proved reliable',
    updated_at = NOW()
WHERE source_label = 'WR:*';
```
Then re-run blending with new weights via the enrichment runner
(`organic_market_agent.crop_book.importer.enrichment_runner.run_enrichment(session, dry_run=False)`).
**No code deployment needed.**

---

## Execution sequence (WP-C5 Phase A)

1. Migration 054: create `crop_source_weights` table
2. Migration 055: data cleanup (basil + tomato + beans) — non-reversible data migration
3. Migration 056: seed `crop_source_weights` with current weights + WR=0.60
4. Update `source_registry.py` to read from DB (cached, with constants fallback)
5. Re-run enrichment (engine v1.1 inheritance + DB-driven weights)
6. validate_aos.sh + focused tests
7. Commit + tag

---

## Addendum — variety-ID corrections post pre-snapshot

Pre-cleanup DB snapshot 2026-05-28 (run before migration 055) revealed two
variety-ID typos in the decisions above; the **intent is preserved** but
migration 055 uses the correct IDs:

1. **Decision #1 (Basil)**: the single variety in crop 58 is actually
   `vid 477` (default, 9 sv), not `vid 461`. (vid 461 lives in crop 75
   with 50 sv — unrelated.) Migration repoints `crop_id=58` varieties to
   crop 4 by `WHERE crop_id=58` (defensive), not by `WHERE id=461`.

2. **Decision #2 (Tomato 73 merge list)**: `vid 477` listed there is the
   basil default (handled by Decision #1), not a Cherry Tomato orphan.
   Crop 73 actually has 4 varieties: 443, 444, 445, 460. Migration merges
   `(443, 444, 445) → 460` only.

All other decisions and the WR=0.60 + DB-driven-weights architecture are
applied as written above.

---

*Decision record by team_10 (Claude Sonnet 4.7) 2026-05-28 per team_00 approval.
Addendum added 2026-05-28 post pre-snapshot for ID accuracy.*
