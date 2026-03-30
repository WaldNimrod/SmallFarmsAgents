# Mandate — Team 20: Seed Patch M1.1
**From:** Team 100 (Architecture)  
**Date:** 2026-03-30  
**Priority:** High — must complete before Gate G3 opens  
**Gate dependency:** Does not block M3 implementation. Blocks G3 QA sign-off.

---

## Background

Two seed-level defects were identified during G1/G2 validation:
1. 13 active products have zero aliases — the normalizer cannot resolve them
2. SRC018–SRC020 `normalizer_type` is `retail_benchmark` (JSON parser) but their pages are HTML

Both are seed data issues, not application code issues. The fix is two new Alembic migrations.

---

## Step 1: Migration `006_seed_aliases_complete.py`

Add aliases for the 13 products currently without any alias in `product_aliases`.

File: `organic_market_agent/db/versions/006_seed_aliases_complete.py`

```python
"""006: Complete product alias coverage — 13 products missing from revision 005."""

from alembic import op
from sqlalchemy import text

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def _norm(s: str) -> str:
    return s.strip().lower()


# Products without aliases after revision 005:
# PRD012 פטרוזיליה, PRD014 סלק, PRD015 לפת, PRD016 צנון,
# PRD018 בצל ירוק, PRD019 שום, PRD020 כרישה,
# PRD021 כרוב לבן, PRD022 כרובית, PRD023 ברוקולי,
# PRD024 שעועית ירוקה, PRD027 סל גדול, PRD028 סל משפחתי
ALIASES = [
    ("PRD012", "פטרוזיליה", "1.0"),
    ("PRD012", "פטרוזיליה צרור", "1.0"),
    ("PRD012", "parsley", "0.9"),
    ("PRD014", "סלק", "1.0"),
    ("PRD014", "סלק ק\"ג", "0.95"),
    ("PRD014", "beet", "0.9"),
    ("PRD014", "beetroot", "0.9"),
    ("PRD015", "לפת", "1.0"),
    ("PRD015", "לפת ק\"ג", "0.95"),
    ("PRD015", "turnip", "0.9"),
    ("PRD016", "צנון", "1.0"),
    ("PRD016", "צנון צרור", "1.0"),
    ("PRD016", "radish", "0.9"),
    ("PRD018", "בצל ירוק", "1.0"),
    ("PRD018", "בצל ירוק צרור", "1.0"),
    ("PRD018", "spring onion", "0.9"),
    ("PRD018", "scallion", "0.9"),
    ("PRD019", "שום", "1.0"),
    ("PRD019", "שום ק\"ג", "0.95"),
    ("PRD019", "שום שן", "0.85"),
    ("PRD019", "garlic", "0.9"),
    ("PRD020", "כרישה", "1.0"),
    ("PRD020", "כרישה ליחידה", "0.95"),
    ("PRD020", "leek", "0.9"),
    ("PRD021", "כרוב לבן", "1.0"),
    ("PRD021", "כרוב", "0.85"),
    ("PRD021", "white cabbage", "0.9"),
    ("PRD021", "cabbage", "0.85"),
    ("PRD022", "כרובית", "1.0"),
    ("PRD022", "כרובית ליחידה", "0.95"),
    ("PRD022", "cauliflower", "0.9"),
    ("PRD023", "ברוקולי", "1.0"),
    ("PRD023", "ברוקולי ליחידה", "0.95"),
    ("PRD023", "broccoli", "0.9"),
    ("PRD024", "שעועית ירוקה", "1.0"),
    ("PRD024", "שעועית", "0.85"),
    ("PRD024", "green beans", "0.9"),
    ("PRD024", "שעועית ק\"ג", "0.95"),
    ("PRD027", "סל גדול", "1.0"),
    ("PRD027", "סל ירקות גדול", "1.0"),
    ("PRD027", "ארגז גדול", "0.85"),
    ("PRD028", "סל משפחתי", "1.0"),
    ("PRD028", "סל ירקות משפחתי", "1.0"),
    ("PRD028", "ארגז משפחתי", "0.85"),
]


def upgrade() -> None:
    conn = op.get_bind()
    for pcode, alias_text, conf in ALIASES:
        n = _norm(alias_text)
        conn.execute(
            text(
                """
                INSERT INTO product_aliases (
                    product_id, alias_text, alias_text_normalized,
                    source_id, confidence, is_active
                )
                SELECT id, :alias_text, :alias_norm, NULL,
                       CAST(:conf AS NUMERIC(3,2)), true
                FROM products WHERE code = :pcode
                ON CONFLICT (alias_text_normalized, source_id)
                DO NOTHING
                """
            ),
            {"alias_text": alias_text, "alias_norm": n, "conf": conf, "pcode": pcode},
        )


def downgrade() -> None:
    conn = op.get_bind()
    codes = [row[0] for row in ALIASES]
    for pcode in set(codes):
        conn.execute(
            text(
                "DELETE FROM product_aliases WHERE product_id = "
                "(SELECT id FROM products WHERE code = :pcode) "
                "AND source_id IS NULL"
            ),
            {"pcode": pcode},
        )
```

---

## Step 2: Migration `007_fix_source_profiles.py`

Fix two issues in `source_fetch_profiles` and `normalizer_profiles`:

1. **SRC018–SRC020**: `normalizer_type` is currently `retail_benchmark` (maps to JSON parser) but pages are HTML. Change to `simple_product_grid`.
2. **SRC015, SRC016**: Government sources return HTTP 403. Mark as `status='candidate'` (not active) until correct API endpoints are confirmed. They will be re-activated when a verified JSON endpoint is found.
3. **EasyFarm selector profiles**: Populate `selector_profile` JSONB for the three main EasyFarm `easyfarm_catalog` sources (SRC002, SRC004, SRC005, SRC006) that returned 0 items due to selector mismatch. Use the revised selectors discovered during M2.

File: `organic_market_agent/db/versions/007_fix_source_profiles.py`

```python
"""007: Fix source profiles — normalizer_type alignment + selector overrides."""

from alembic import op
from sqlalchemy import text
import json

revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


# Updated selector profiles for EasyFarm sources based on live DOM inspection.
# These are broader selectors that catch more product rows.
EASYFARM_SELECTOR = {
    "product_row": (
        "div.product-item, li.product, tr.product-row, "
        "div[class*='product'], li[class*='product'], "
        "div.shop-item, div.item"
    ),
    "name": (
        ".product-name, .item-title, h3, h4, "
        ".product-title, [class*='name'], [class*='title']"
    ),
    "price": (
        ".product-price, .price, .item-price, "
        "[class*='price'], span[class*='cost']"
    ),
    "unit": (
        ".product-unit, .unit, .item-unit, "
        "[class*='unit'], [class*='weight']"
    ),
    "quantity": None,
}


def upgrade() -> None:
    conn = op.get_bind()

    # 1. Fix SRC018–SRC020: normalizer_type html→simple_product_grid
    for src_code in ("SRC018", "SRC019", "SRC020"):
        conn.execute(
            text(
                "UPDATE normalizer_profiles SET normalizer_type = 'simple_product_grid' "
                "WHERE source_id = (SELECT id FROM sources WHERE code = :code)"
            ),
            {"code": src_code},
        )

    # 2. Deactivate SRC015, SRC016 (HTTP 403 — no working endpoint confirmed)
    for src_code in ("SRC015", "SRC016"):
        conn.execute(
            text(
                "UPDATE sources SET status = 'candidate', is_active = false "
                "WHERE code = :code"
            ),
            {"code": src_code},
        )
        conn.execute(
            text(
                "UPDATE source_fetch_profiles SET is_active = false "
                "WHERE source_id = (SELECT id FROM sources WHERE code = :code)"
            ),
            {"code": src_code},
        )

    # 3. Update EasyFarm selector profiles (SRC002, SRC004, SRC005, SRC006)
    selector_json = json.dumps(EASYFARM_SELECTOR)
    for src_code in ("SRC002", "SRC004", "SRC005", "SRC006"):
        conn.execute(
            text(
                "UPDATE source_fetch_profiles "
                "SET selector_profile = CAST(:sel AS jsonb) "
                "WHERE source_id = (SELECT id FROM sources WHERE code = :code)"
            ),
            {"sel": selector_json, "code": src_code},
        )


def downgrade() -> None:
    conn = op.get_bind()
    for src_code in ("SRC018", "SRC019", "SRC020"):
        conn.execute(
            text(
                "UPDATE normalizer_profiles SET normalizer_type = 'retail_benchmark' "
                "WHERE source_id = (SELECT id FROM sources WHERE code = :code)"
            ),
            {"code": src_code},
        )
    for src_code in ("SRC015", "SRC016"):
        conn.execute(
            text(
                "UPDATE sources SET status = 'active', is_active = true "
                "WHERE code = :code"
            ),
            {"code": src_code},
        )
        conn.execute(
            text(
                "UPDATE source_fetch_profiles SET is_active = true "
                "WHERE source_id = (SELECT id FROM sources WHERE code = :code)"
            ),
            {"code": src_code},
        )
    for src_code in ("SRC002", "SRC004", "SRC005", "SRC006"):
        conn.execute(
            text(
                "UPDATE source_fetch_profiles SET selector_profile = NULL "
                "WHERE source_id = (SELECT id FROM sources WHERE code = :code)"
            ),
            {"code": src_code},
        )
```

---

## Step 3: Verification

After applying both migrations:

```bash
alembic upgrade head
python -m organic_market_agent.db.check
```

Then run the alias completeness check:
```sql
SELECT p.code, p.canonical_name_he
FROM products p
LEFT JOIN product_aliases pa ON pa.product_id = p.id AND pa.is_active = true
WHERE pa.id IS NULL AND p.is_active = true;
```
**Expected:** 0 rows.

And verify source profile fixes:
```sql
SELECT s.code, np.normalizer_type, sfp.is_active AS profile_active, s.is_active AS src_active
FROM sources s
JOIN normalizer_profiles np ON np.source_id = s.id
JOIN source_fetch_profiles sfp ON sfp.source_id = s.id
WHERE s.code IN ('SRC015','SRC016','SRC017','SRC018','SRC019','SRC020')
ORDER BY s.code;
```
**Expected:**
- SRC015, SRC016: `src_active = false`, `profile_active = false`
- SRC018–SRC020: `normalizer_type = 'simple_product_grid'`

---

## Submission

File your completion report at:
`_COMMUNICATION/TEAM_20/reports/{date}_SEED_PATCH_M1.1_COMPLETE_TEAM20.md`

Include:
- `alembic upgrade head` output (revisions 006, 007 applied)
- Output of alias completeness SQL query (0 rows)
- Output of source profiles verification SQL
- `python -m organic_market_agent.db.check` → RESULT: PASS
