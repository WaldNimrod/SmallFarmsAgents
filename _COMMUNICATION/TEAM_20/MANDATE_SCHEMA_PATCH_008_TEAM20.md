# Mandate — Team 20: Schema Patch 008 — Fix unresolvable_reason column
**From:** Team 100 (Architecture)
**Date:** 2026-03-30
**Priority:** BLOCKING — Gate G3 is FAIL until this is applied
**Context:** G3 QA T02 FAIL — `StringDataRightTruncation` on `raw_extracted_items.unresolvable_reason`

---

## Root Cause

`raw_extracted_items.unresolvable_reason` was defined as `VARCHAR(200)` in migration 001.

The normalizer writes:
```
"no alias match for 'some scraped product name...'"
```

Real scraped product names (Hebrew + metadata) routinely exceed 150 characters, making the
full error string exceed 200 characters. PostgreSQL raises `StringDataRightTruncation` and
rolls back the transaction, leaving `normalized_observations` empty.

---

## Step 1: Migration `008_fix_unresolvable_reason_text.py`

**File:** `organic_market_agent/db/versions/008_fix_unresolvable_reason_text.py`

```python
"""008: Widen unresolvable_reason from VARCHAR(200) to TEXT."""

from alembic import op
import sqlalchemy as sa

revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "raw_extracted_items",
        "unresolvable_reason",
        type_=sa.Text(),
        existing_type=sa.VARCHAR(200),
        existing_nullable=True,
    )


def downgrade() -> None:
    # Truncate existing values before downgrade to avoid data loss errors.
    op.execute(
        "UPDATE raw_extracted_items "
        "SET unresolvable_reason = LEFT(unresolvable_reason, 200) "
        "WHERE LENGTH(unresolvable_reason) > 200"
    )
    op.alter_column(
        "raw_extracted_items",
        "unresolvable_reason",
        type_=sa.VARCHAR(200),
        existing_type=sa.Text(),
        existing_nullable=True,
    )
```

---

## Step 2: Apply and Verify

```bash
cd /Users/nimrod/Documents/SmallFarmsAgents
source .env
alembic upgrade head
```

Expected output:
```
INFO  [alembic.runtime.migration] Running upgrade 007 -> 008, 008: Widen unresolvable_reason...
```

Verify the column type:
```bash
docker exec oma-g2-ev psql -U oma -d organic -c "\d raw_extracted_items" | grep unresolvable
```

Expected:
```
 unresolvable_reason   | text    |    | |
```

---

## Step 3: Re-run normalizer to confirm no crash

```bash
python3.11 -m organic_market_agent run_normalizer
```

Expected: no `StringDataRightTruncation` error. Output shows `resolved=N unresolvable=M skipped=K`.

---

## Submission

File your completion report at:
`_COMMUNICATION/TEAM_20/reports/2026-03-30_SCHEMA_PATCH_008_COMPLETE_TEAM20.md`

Include:
- `alembic upgrade head` output (revision 008 applied)
- Column type confirmation (`\d raw_extracted_items` → `unresolvable_reason | text`)
- `run_normalizer` output (no crash, shows counts)
- `python -m organic_market_agent.db.check` → RESULT: PASS
