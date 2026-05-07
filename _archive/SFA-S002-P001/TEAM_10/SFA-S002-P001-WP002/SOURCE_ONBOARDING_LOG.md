# MyPIPS Source Onboarding Log — SFA-S002-P001-WP002

**Date:** 2026-05-07
**Team:** Team 10 (sfa_build)
**WP:** WP002 — MyPIPS Source Integration

## Smoke Ingestion Results (AC-06)

All 4 priority sources probed live on 2026-05-07 using `MypipsCollector` (Playwright headless Chromium).

| Source | Handle | Timestamp (UTC) | Items | Status | Notes |
|--------|--------|-----------------|-------|--------|-------|
| משתלת הראה | mashtelatharoe | 2026-05-07T11:38:12Z | 32 | OPEN | First product: פומלית לבנה; display_bucket=grower |
| הננתיות | anatiyot | 2026-05-07T11:38:33Z | 32 | OPEN | AC-07 includeOrganic=true applied; first: אבטיח מתוק!; display_bucket=store |
| השחקן שהפך לירקן | fruit4soul | 2026-05-07T11:38:55Z | 32 | OPEN | First product: אבטיח גולי! מחיר לקג; display_bucket=store |
| משק רתם פיין | finerotem | 2026-05-07T11:39:16Z | 6 | OPEN | First product: navigation category label (non-product); display_bucket=grower |

## Technical Notes

- **URL correction:** Initial implementation used `https://www.mypips.co.il/shop/{handle}` — returns Wix 404.
  Live probe confirmed correct URL is `https://mypips.app/{handle}/products`.
  Collector updated accordingly.

- **Extraction strategy:** Primary DOM extraction uses `.bordered-card` / `.pips-card-content` CSS classes
  (React + MUI components rendered by Firestore). Verified 16–32 cards rendered per store.

- **networkidle timeout:** Firestore hydration consistently triggers `networkidle` timeout (~20s) but
  product DOM is already populated by `load` event. Timeout is handled gracefully; products extracted
  successfully post-timeout.

- **finerotem note:** 6 items extracted; first item appears to be a navigation/category label
  (emoji-rich text). Actual product rows start at index 1+. Store is small; content is valid.

- **anatiyot AC-07:** `includeOrganic=true` query param is appended when `handle in ANATIYOT_HANDLES`.
  Confirmed in URL at ingestion time and in unit tests.

## Fixture Status

HTML fixtures captured from stash and stored at `tests/fixtures/mypips/`:
- `mashtelatharoe.html` — synthetic fixture (JSON-LD, 2 products)
- `anatiyot.html` — synthetic fixture (JSON-LD, 1 product)
- `closed_store.html` — synthetic fixture for closed-store detection test

Live fixture capture available via `MypipsCollector.save_fixture()` method.

## Seeder Status

`scripts/seed_mypips_sources.py` ready. DB is online; seeder to be run by Team 00 or scheduled
after migration 034 is applied via `alembic upgrade head`.
