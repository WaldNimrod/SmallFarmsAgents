# Phase B + Phase E — operator runbook (canonical CLI)

**Date:** 2026-04-08  
**From:** Team 10  
**To:** Nimrod (operator)  
**Status:** `[USER ACTION REQUIRED]`

## Preconditions

- `alembic upgrade head` → **073** confirmed (`2026-04-08_V1_1_ENV_VERIFICATION_TEAM10.md` on green workstation).
- A2 batch applied when infra files follow-up migration (see `2026-04-08_V1_1_MIGRATION_072_DATA_REQUEST_TEAM10.md`).

## Phase B

```bash
alembic current
python -m organic_market_agent run_ingestion --run-type manual --normalize
python -m organic_market_agent run_aggregator
python -m organic_market_agent run_publisher
```

**Verify:** published products ≥ 77; PRD027 count ≤ 1 in `output/public/public_report.json`; `pytest tests/test_publisher_local.py::test_publish_one_row_per_product_code`.

## Phase E (FTPS)

```bash
python -m organic_market_agent run_ingestion --run-type manual --normalize
python -m organic_market_agent run_aggregator
python -m organic_market_agent run_publisher --upload
```

**Privacy:**

```bash
python3 -c "
import json, re
from pathlib import Path
text = Path('output/public/public_report.json').read_text(encoding='utf-8')
m = re.findall(r'SRC\d+', text)
print('FAIL' if m else 'Privacy check (SRC codes): PASS')
"
grep -R -n -E 'SRC[0-9]{3}' output/public/
```

Reply with logs in the dated completion report addendum.
