# Catalog scope-skip rules — draft for Nimrod approval (English)

**Status:** DRAFT — not seeded in the database. After you approve the full numbered list, Team 10 applies a follow-up Alembic migration with `INSERT` into `catalog_scope_skip_rules`.

**Purpose:** Rows matching these rules become `extraction_status = 'ignored'` with `ignore_reason_code = 'approved_scope_skip'` and `unresolvable_reason` like `approved_scope_skip:{category}#{rule_id}`. This is an **intentional V1 out-of-scope skip**, not a normalizer failure.

## How to refresh the candidate list from your DB

Run against PostgreSQL (adjust source filter if needed):

```sql
SELECT rei.raw_product_name, COUNT(*) AS cnt
FROM raw_extracted_items rei
JOIN source_fetch_runs sfr ON sfr.id = rei.source_fetch_run_id
JOIN sources s ON s.id = sfr.source_id
WHERE rei.extraction_status = 'unresolvable'
  AND rei.is_quarantined IS NOT TRUE
GROUP BY rei.raw_product_name
ORDER BY cnt DESC
LIMIT 80;
```

## Proposed rules (numbered) — **requires your sign-off**

| display_order | category_code | match_type | pattern (Hebrew / text as stored) | notes |
|---------------|---------------|------------|-----------------------------------|-------|
| 1 | donation | prefix | תרומת ירקות | Donation line items; not V1 vegetable price index |
| 2 | donation | prefix | תרומה | Covers תרומה למנזר…, תרומה למשפחות… |
| 3 | cleaning | contains | מרכך כביסה | Laundry softener; not in V1 catalog |
| 4 | dry_grocery | contains | אורז | Packaged rice SKUs on mixed retail grids |
| 5 | dry_grocery | contains | ספגטי | Pasta |
| 6 | dry_grocery | contains | פיסטוק | Nuts |
| 7 | dry_grocery | contains | קשיו | Nuts |
| 8 | dry_grocery | contains | צימוק | Dried fruit |
| 9 | dry_grocery | prefix | מי קוקוס | Beverage / non-produce |
| 10 | dry_grocery | contains | חמאת שיאה | Packaged spread |
| 11 | dry_grocery | contains | לחם | Bread |
| 12 | other | contains | סבון | Soap / non-food retail |
| 13 | other | contains | חליטת | Tea blend product line |

**Edit this table** (add/remove/reorder) and confirm in writing before any seed migration ships.

## Admin UI

After migration `024`, the numbered catalog is visible at **`/catalog/scope-skip`** (read-only list + JSON export when logged in).
