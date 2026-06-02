# Migration 072 request — v1.1.0 (Team 10 → Team 20)

**Date:** 2026-03-30  
**From:** Team 10  
**Handoff:** H1 per `HANDOFF_V1_1_ORCHESTRATION_TEAM10.md` §5.1  
**Prerequisite:** Team 10 has **not** run `alembic upgrade head` for this change set.

## Summary

1. **A1 (cherry / PRD028–PRD029 guards):** Prior migrations `067`, `068` addressed catalog drift. Re-run HANDOFF §A1 SQL locally after this migration if needed; **no additional fix-forward SQL** bundled here unless audits fail post-072.
2. **A2 (92-name triage):** Full triage table to be completed in the completion report; **no batch alias INSERTs** in this request. If triage produces SQL before gate, Team 10 will file **073** follow-up.
3. **A4 (SRC_WA):** LOD400 Phase A requires a placeholder source for WhatsApp intake. Below is proposed upgrade SQL for Team 20 to wrap as revision `072` (or next free revision if 072 is reserved).

## Proposed upgrade SQL (SRC_WA)

```sql
-- Community WhatsApp manual intake (SPEC-20260408-PHASE-A-LOD400 §A4)
INSERT INTO sources (
    code, name, base_url, source_group, market_scope, sales_channel,
    status, priority, legal_review_required, is_active
)
SELECT
    'SRC_WA',
    'Community WhatsApp intake',
    NULL,
    'direct_price',
    'community',
    'community_direct',
    'active',
    8,
    false,
    true
WHERE NOT EXISTS (SELECT 1 FROM sources WHERE code = 'SRC_WA');

INSERT INTO source_fetch_profiles (
    source_id, platform_family, fetch_mode, entry_url, http_method, schedule_kind, is_active
)
SELECT
    s.id,
    NULL,
    'html_page',
    'https://nimrod.bio/',
    'GET',
    'manual_check',
    false
FROM sources s
WHERE s.code = 'SRC_WA'
  AND NOT EXISTS (
      SELECT 1 FROM source_fetch_profiles sfp WHERE sfp.source_id = s.id
  );

INSERT INTO normalizer_profiles (source_id, normalizer_type, version, is_active)
SELECT s.id, 'simple_product_grid', '1.0', true
FROM sources s
WHERE s.code = 'SRC_WA'
  AND NOT EXISTS (
      SELECT 1 FROM normalizer_profiles np WHERE np.source_id = s.id
  );
```

## Request to Team 20

1. Create Alembic migration `072` (or next revision) with the SQL above, adjusted for idempotency patterns you prefer.
2. Apply on the shared/dev database and confirm.
3. File a short confirmation report in `_COMMUNICATION/TEAM_20/reports/` with `alembic current` output showing **head**.

## Wait condition (Team 10)

Team 10 proceeds to Phase B operator requests only after written Team 20 confirmation.
