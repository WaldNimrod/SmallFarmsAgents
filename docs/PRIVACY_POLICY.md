# Privacy Policy — OrganicMarketAgent

**Version:** 1.0
**Date:** 2026-04-02
**Author:** Team 100 (Architecture), based on Team 80 recommendation
**Status:** ACTIVE

---

## Core Principle

**The system MUST NEVER expose identifiable farm-level data in any public output.**

This is a non-negotiable design constraint that applies to all current and future
public-facing features of OrganicMarketAgent.

---

## Definitions

| Term | Meaning |
|------|---------|
| **Farm-level data** | Any data point that can be attributed to a specific farm, grower, or seller |
| **Aggregated data** | Statistical summaries computed from multiple independent sources |
| **Public output** | Any artifact accessible outside the local admin interface (HTML, JSON, WordPress page) |
| **Source** | A website, catalog, or data feed from which prices are scraped |

---

## Rules — What Is Forbidden

1. **No single-source pricing** — Never display a price observation that comes from
   only one source. Minimum 2 observations from 2 distinct sources required for publication.
2. **No source attribution** — Never reveal which specific farm or grower contributed
   a data point in public output. Source names appear only in the local admin interface.
3. **No raw submissions** — Never expose raw extracted items, raw payload JSON, or
   unprocessed scraping results in public output.
4. **No reverse identification** — Never publish data in a granularity or combination
   that would allow a reader to deduce a specific farm's pricing.
5. **No individual observation display** — Only aggregated values (average, median,
   min, max, stddev) appear in public output.

---

## Rules — What Is Allowed

1. **Aggregated statistics** — Average, median, min, max, standard deviation across
   all qualifying observations.
2. **Statistical ranges** — Price ranges showing the spread across multiple sources.
3. **Sample sizes** — Number of observations and distinct sources (as counts only,
   not identified).
4. **Confidence indicators** — Data quality signals based on sample size and dispersion.
5. **Temporal indicators** — Report date, last update timestamp, staleness warnings.

---

## Implementation — Current Enforcement

These privacy rules are enforced at multiple layers:

### Pipeline Level (automatic)
- `PublishEngine` enforces `min_observations >= 2` and `min_distinct_sources >= 2`
  before including a product in public output
- Price dispersion rules suppress outliers: 2-source spread >100% or 3+-source >2σ
- Scope-skip rules filter non-food items before they enter the pipeline

### Template Level (public_report_body.html)
- Template renders only aggregated fields: `avg_price`, `median_price`, `min_price`,
  `max_price`, `stddev_price`, `sample_size`, `distinct_sources`
- No source names, URLs, or identifiers appear in the public template
- Transparency block shows pipeline statistics (counts only)

### Admin Level (local only)
- Source names, raw data, and individual observations are visible only in the
  local admin interface at `127.0.0.1:5001`
- Admin interface is not exposed to the internet

---

## Public-Facing Privacy Statement

The following text appears in the transparency block on the public page:

> פרטיות: המערכת מציגה נתונים מצרפיים בלבד. אין חשיפה של מחירים ברמת חווה
> בודדת, ולא ניתן לזהות מגדל ספציפי מהנתונים המוצגים.

---

## Future Considerations

If farmer-submitted data is added (M9+):
- Submitted data must be anonymized before storage
- Submitted prices enter the same aggregation pipeline as scraped data
- No "submitted by" attribution in public output
- Farmers see only their own submissions (if authenticated)

---

## Review Schedule

This policy is reviewed at every milestone that touches public output or data collection.
Changes require Team 100 approval and Nimrod sign-off.
