---
id: BUILD_REPORT_WP-CB-UI-FIDELITY_team10_v1.1.0
from: team_10 (Builder, Claude Sonnet)
to: team_100 (Chief Architect)
date: 2026-06-04
wp: SFA-S003-P004-WP-CB-UI-FIDELITY
branch: claude/ui-polish-hub-cropbook-2026-06-03
supersedes: BUILD_REPORT_v1.0.0.md (incremental delta only)
decision_ref: DECISION_team00_season-and-questions_2026-06-04_v1.0.0.md
---

# BUILD REPORT v1.1.0 — Incremental delta (Decision A + B + correctness fix)

**No commits made.** Working tree dirty. team_100 commits with explicit sfa_delivery/ paths.

This report covers the incremental change on top of v1.0.0 (commit c82818c), implementing
DECISION_team00_season-and-questions_2026-06-04_v1.0.0.md Decisions A and B, plus a
subsequent correctness fix (Decision A bug: months read from wrong data source).

---

## CORRECTNESS FIX: Decision A data-source bug (applied after initial v1.1.0 submission)

**Root cause:** The original Decision A implementation read `sowing_months` /
`transplant_months` from `crops.payload_json['agronomy']` (the crop-level payload). The
ingest (`organic_market_agent/publisher/sfa_ingest_push.py` L470-487) puts these arrays into
`crop_varieties.payload_json['agronomy']`, NOT the crop payload (the crop's agronomy block
holds only numeric medians). Result: the season filter always received empty month arrays and
excluded every crop → 0 results for any season selection.

**Fix in `entry()` only** (`CropBookViewController.php`):

1. **`id` added to SELECT** (line 62):
   ```php
   $sql = 'SELECT id, slug, hebrew_name, ... FROM crops';
   ```

2. **Batched `crop_varieties` query** (after `$rows` fetch, before per-row loop):
   - Collect crop ids from `$rows`.
   - One `SELECT crop_id, payload_json FROM crop_varieties WHERE crop_id IN (?,…)`.
   - For each variety row: json_decode → read `agronomy.sowing_months` and
     `agronomy.transplant_months`, normalize each (tolerates JSON-string / array / absent),
     union-accumulate into `$monthsByCrop[crop_id]` across all varieties of that crop.
   - Guard: skip query if no crop ids; wrap in `try/catch` so missing `crop_varieties` table
     degrades to empty map (season filter then excludes all — acceptable, no fatal).

3. **Post-filter updated** (replaces the old crop-payload read):
   ```php
   $cropMonths = $monthsByCrop[(int)($row['id'] ?? 0)] ?? [];
   if (empty($cropMonths) || empty(array_intersect($cropMonths, $targetMonths))) {
       continue;
   }
   ```

The `$normalizeMonths` closure was moved to before the batched query (now shared by both
the variety accumulation loop and future callers within `entry()`).

**New regression test** (`tests/CropBookV1RouteTest.php`):
`testSeasonFilterReadsVarietyMonths()` — end-to-end route test using the existing
SQLite in-memory harness:
- Seeds 3 crops (pepper id=10, tomato id=11, basil id=12) with empty crop payloads.
- Seeds 3 `crop_varieties` rows: pepper→`agronomy.sowing_months=[3,4,5]` (spring),
  tomato→`[6,7,8]` (summer), basil→empty agronomy (no data).
- Asserts `?season=summer`: tomato present, pepper absent, basil absent.
- Asserts `?season=spring`: pepper present, tomato absent, basil absent.
- Test type: **end-to-end** (full Slim route → controller → SQLite → template → HTML).

**Achieved: end-to-end test** (not fallback logic-only) — the existing SQLite harness
supports seeding `crop_varieties`, so the full path is covered.

---

## Files Changed

### sfa_delivery/ (delivery tier — render layer only)

1. `sfa_delivery/app/Controllers/CropBookViewController.php`
2. `sfa_delivery/templates/pages/book_entry.php`
3. `sfa_delivery/tests/CropBookV1RouteTest.php` (regression test added)

No other files touched. No DB/data/migration changes.

---

## Decision A: months-based season post-filter

### Controller changes (`CropBookViewController.php`)

**`entry()` method:**

- **Removed** the SQL `season LIKE ?` clause (was line 54). The `crops.season` column
  (growth-cycle tokens) is no longer used as a season-filter backing.
- **Added** a PHP post-filter in the per-row loop (after the existing `frost` post-filter)
  using a season→months map and `array_intersect()`:

```php
// Season→months map (meteorological, Israel)
$seasonMonthsMap = [
    'summer' => [6, 7, 8],
    'autumn' => [9, 10, 11],
    'winter' => [12, 1, 2],
    'spring' => [3, 4, 5],
];

// In per-row loop:
if ($season !== '' && isset($seasonMonthsMap[$season])) {
    $targetMonths = $seasonMonthsMap[$season];

    $normalizeMonths = static function (mixed $raw): array {
        if (is_array($raw)) { return array_map('intval', $raw); }
        if (is_string($raw) && $raw !== '') {
            $decoded = json_decode($raw, true);
            if (is_array($decoded)) { return array_map('intval', $decoded); }
        }
        return [];
    };

    $agro = is_array($payload['agronomy'] ?? null) ? $payload['agronomy'] : [];
    $sowMonths        = $normalizeMonths($agro['sowing_months']     ?? ($payload['sowing_months']     ?? null));
    $transplantMonths = $normalizeMonths($agro['transplant_months'] ?? ($payload['transplant_months'] ?? null));
    $cropMonths = array_unique(array_merge($sowMonths, $transplantMonths));

    if (empty($cropMonths) || empty(array_intersect($cropMonths, $targetMonths))) {
        continue; // no month data, or months don't intersect the requested season
    }
}
```

**Intersection logic sanity trace (spring vs summer for `sowing_months=[3,4,5]`):**
- `spring` → targetMonths=`[3,4,5]` → `[3,4,5] ∩ [3,4,5]` = `[3,4,5]` → non-empty → KEEP (correct)
- `summer` → targetMonths=`[6,7,8]` → `[3,4,5] ∩ [6,7,8]` = `∅` → empty → SKIP (correct)

### Template changes (`book_entry.php`)

Replaced the "מחזור גידול" `<select>` (growth-cycle tokens `annual`/`biennial`/`year-round`)
with a real "עונה" season `<select>`:

```php
$season_opts = [
    ''       => 'הכל',
    'summer' => 'קיץ',
    'winter' => 'חורף',
    'spring' => 'אביב',
    'autumn' => 'סתיו',
];
```

Label changed from "מחזור גידול" to "עונה". Comment updated to reference Decision A.

---

## Decision B: restore leading questions + fix count

### Controller changes (`CropBookViewController.php`)

**`questions()` method:** restored from 1 question to 3:

```php
$questions = [
    ['slug' => 'summer', 'q_he' => 'מה מתאים לקיץ?',    'sub_he' => 'זריעה בחודשי הקיץ',   'href' => '/crop-book/?season=summer'],
    ['slug' => 'winter', 'q_he' => 'מה זורעים לחורף?',  'sub_he' => 'זריעה בחודשי החורף',   'href' => '/crop-book/?season=winter'],
    ['slug' => 'fast',   'q_he' => 'מה גדל מהר?',        'sub_he' => 'עד 60 ימ׳ להבשלה',     'href' => '/crop-book/?dtm_max=60'],
];
```

Comment updated: summer/winter now route to Decision A season filter (backed by months data);
team_35 Q4 note preserved for final/expanded set.

### Template changes (`book_entry.php`)

**Count fix:** default `$question_total` changed from `12` to `3` so the "שאלות מובילות"
entry card (`stat_he`) no longer advertises a lying "12 שאלות". Now shows "3 שאלות" which
matches the actual count of shipped questions.

```php
// Before:
$question_total = (int)($question_total ?? 12);
// After:
$question_total = (int)($question_total ?? 3);
```

---

## composer test Results

```
Tests: 168, Assertions: 415, PHPUnit Deprecations: 1
OK (168 green — 167 prior + 1 new testSeasonFilterReadsVarietyMonths; no regressions)
```

---

## php -l Results

```
No syntax errors detected in app/Controllers/CropBookViewController.php
No syntax errors detected in tests/CropBookV1RouteTest.php
No syntax errors detected in templates/pages/book_entry.php
```

---

## Coverage note (honest)

The months-based season filter has ~39/70 crops matching via `sowing_months` and ~44/70
with `transplant_months` unioned — mirroring the canonical Postgres `int[]` arrays via
`payload_json['agronomy']`. Crops lacking month data simply won't match any season filter
(honest partial coverage — documented in the template comment).

---

## Unchanged: no regressions to prior build

- WI-9 responsive table fix intact (not touched)
- All other v1.0.0 changes intact
- `crops.season` column still in SELECT (used by `tableView()` and `detail()`) — only the
  season-filter SQL clause in `entry()` was removed

---

*BUILD_REPORT v1.1.0 filed by team_10 · 2026-06-04 · Leave dirty for team_100 review*
