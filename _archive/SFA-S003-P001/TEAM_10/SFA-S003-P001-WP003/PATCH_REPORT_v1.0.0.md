---
artifact_type: PATCH_REPORT
work_package: SFA-S003-P001-WP003
patch: PATCH01
team: team_10 (sfa_build)
date: 2026-05-08
patch_commit: d972b15
branch: claude/strange-mcnulty-651551
gate_finding_source: L-GATE_V PASS_WITH_FINDINGS (team_190, 2026-05-08)
---

# PATCH REPORT — SFA-S003-P001-WP003 PATCH01

Remediates two MINOR findings from team_190 L-GATE_V verdict (PASS_WITH_FINDINGS).

---

## F-190-WP003-01 — Multi-season OR filter

**Finding:** `GET /crop-book/api/crops?season=X` used `request.args.get('season')` (scalar). When a caller passes `?season=summer&season=winter`, only the first value was captured and the second was silently ignored.

**Spec ref:** LOD400 §3.3 AC-03 — season checkboxes filter by `planting_season` substring match (OR logic when multiple seasons selected).

**Fix — `organic_market_agent/crop_book/views.py`:**

| | Before | After |
|---|---|---|
| Capture | `season = request.args.get("season", "").strip()` | `seasons = request.args.getlist("season")` |
| Guard | `if season:` | `if seasons:` |
| Logic | Single-token substring match | OR across all selected seasons via `_matches_any_season()` local helper |

The local helper `_matches_any_season(sel_seasons)` iterates over all selected season keys, looks up their Hebrew/English token lists from `season_map`, and returns `True` if any token matches `planting_season`. Empty `seasons` list → no filter (show all crops).

**Test added:** `TestSearch::test_api_multi_season_or_logic`
- Creates 3 crops: קיץ (summer), חורף (winter), אביב (spring)
- Requests `?season=summer&season=winter`
- Asserts both summer and winter crops in results, spring crop excluded

---

## F-190-WP003-02 — Timeline ruler weeks calculation

**Finding:** `total_weeks` in `crop_detail()` was calculated as `ceil((dtm + hw_max) / 7)`. Per spec, the ruler shows N weeks where N = `ceil(harvest_window_max_days / 7)`. For ארוגולה (DTM=21, harvest_window=80): old formula gave 15 weeks, correct is 12 weeks.

**Spec ref:** LOD400 §3.9 line 257: "Ruler: 1 to N weeks (N = harvest_window_max_days / 7, rounded up)". Line 320: ארוגולה harvest_window=80 → 12 weeks.

**Note on mandate file reference:** The mandate listed `_macros.html (timeline_bar macro)` but the actual calculation is in `views.py`. The `timeline_bar` macro only renders pre-computed phase widths. Fix is entirely in `views.py`.

**Fix — `organic_market_agent/crop_book/views.py`, line 197:**

```python
# Before
total_weeks = max(1, -(-total_days // 7))  # ceiling division

# After
total_weeks = max(1, -(-hw_max // 7))  # ruler: harvest_window only (LOD400 §3.9)
```

`total_days` and the `pct()` helper are **unchanged** — phase proportions (greenhouse / grow / harvest) remain proportional to `dtm + hw_max`.

**Test added:** `TestTimeline::test_timeline_weeks_based_on_harvest_window_only`
- Creates arugula variety: DTM=21, harvest_window=80
- Patches `render_template` to capture `timeline_data` dict
- Asserts `total_weeks == ceil(80/7) == 12` (not 15)

---

## Test Results

```
pytest tests/crop_book/test_views.py -v
51 passed in 1.27s   (was 49 — +2 new tests)

pytest tests/crop_book/ -q
80 passed in 1.31s   (all 80 green)
```

---

## AOS Validation

```
validate_aos.sh → 29 PASS / 17 SKIP / 0 FAIL
L-GATE_BUILD EXIT CRITERION: SATISFIED
```

---

## Patch Commit

`d972b15` — `fix(S003-WP003): PATCH01 — F-190-WP003-01 multi-season OR + F-190-WP003-02 ruler weeks`

Files changed:
- `organic_market_agent/crop_book/views.py` (+17, -8)
- `tests/crop_book/test_views.py` (+54, 0)

---

## Routing

- **To:** team_00, team_100
- **Cc:** team_190 (for L-GATE_V re-check / LOD500_LOCKED confirmation)
