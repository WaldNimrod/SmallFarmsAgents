"""WP004 — Filter parity tests (AC-04, AC-09).

Verifies that the JS SPA filter logic (implemented in Python-mimicked form here)
produces identical crop-id sets as the Flask /api/crops endpoint for the 12-case
matrix specified in spec §11.1.

The JS logic is transcribed to Python for unit-testing without a JS runtime.
The Flask endpoint is tested via the test client.

DB-dependent tests (AC-04 cases 1-12) skip if PostgreSQL is unavailable.
"""
from __future__ import annotations

from typing import Any

import pytest


# ---------------------------------------------------------------------------
# Python mirror of JS filterCrops() — must match views.py:234-304 exactly
# ---------------------------------------------------------------------------

SEASON_MAP = {
    "summer": ["קיץ", "summer"],
    "spring": ["אביב", "spring"],
    "winter": ["חורף", "winter"],
    "fall":   ["סתיו", "fall", "autumn"],
}


def _default_var(crop: dict) -> dict | None:
    varieties = crop.get("varieties") or []
    if not varieties:
        return None
    for v in varieties:
        if v.get("is_default"):
            return v
    return varieties[0]


def js_filter_crops(crops: list[dict], opts: dict) -> list[int]:
    """Python mirror of sfagent-crop-book.js filterCrops(). Returns sorted crop IDs."""
    q        = (opts.get("q") or "").strip().lower()
    category = opts.get("category") or ""
    seasons  = opts.get("seasons") or []
    dtm_max_raw = opts.get("dtmMax")
    dtm_max  = int(dtm_max_raw) if dtm_max_raw is not None else None

    results = []
    for crop in crops:
        # Category filter
        if category and category != "all" and crop.get("category") != category:
            continue

        # Text search
        if q:
            he  = (crop.get("name_he")  or "").lower()
            en  = (crop.get("name_en")  or "").lower()
            sci = (crop.get("scientific_name") or "").lower()
            if q not in he and q not in en and q not in sci:
                continue

        dv = _default_var(crop)

        # DTM filter
        if dtm_max is not None:
            dtm = dv.get("days_to_maturity") if dv else None
            if dtm is None or dtm > dtm_max:
                continue

        # Season filter — OR logic
        if seasons:
            planting = (dv.get("planting_season") or "").lower() if dv else ""
            matches_any = any(
                any(t.lower() in planting for t in SEASON_MAP.get(s, [s]))
                for s in seasons
            )
            if not matches_any:
                continue

        results.append(crop["id"])

    return sorted(results)


# ---------------------------------------------------------------------------
# Flask client helper
# ---------------------------------------------------------------------------

def flask_filter_crops(client, opts: dict) -> list[int]:
    """Call Flask /api/crops with opts. Returns sorted crop IDs."""
    params: list[tuple[str, str]] = []
    if opts.get("q"):
        params.append(("q", opts["q"]))
    if opts.get("category") and opts["category"] != "all":
        params.append(("category", opts["category"]))
    for s in (opts.get("seasons") or []):
        params.append(("season", s))
    dtm_max = opts.get("dtmMax")
    if dtm_max is not None and dtm_max < 365:
        params.append(("dtm_max", str(dtm_max)))

    resp = client.get("/crop-book/api/crops", query_string=params)
    assert resp.status_code == 200, f"Flask /api/crops returned {resp.status_code}"
    import json
    crops = json.loads(resp.data)
    return sorted(c["id"] for c in crops)


# ---------------------------------------------------------------------------
# Spec §11.1 — 12-case parity matrix
# ---------------------------------------------------------------------------

PARITY_CASES = [
    # (label, q, category, seasons, dtm_max)
    ("all-crops",               "",       "all",        [],               365),
    ("vegetables",              "",       "vegetables",  [],               365),
    ("herbs",                   "",       "herbs",       [],               365),
    ("search-tomato-en",        "tomato", "all",        [],               365),
    ("search-egv-he",           "עגב",    "all",        [],               365),
    ("summer-only",             "",       "all",        ["summer"],        365),
    ("winter-only",             "",       "all",        ["winter"],        365),
    ("summer-fall-or",          "",       "all",        ["summer", "fall"],365),
    ("all-seasons",             "",       "all",        ["summer","spring","winter","fall"], 365),
    ("dtm-max-60",              "",       "all",        [],               60),
    ("dtm-max-30",              "",       "all",        [],               30),
    ("combined",                "tomato", "vegetables", ["summer"],        90),
]


@pytest.mark.integration
class TestFilterParity:
    """DB-dependent parity tests — skip if PostgreSQL unavailable."""

    @pytest.fixture(autouse=True)
    def _require_db(self, db_session):
        self.db_session = db_session

    @pytest.fixture
    def data_json(self, tmp_path, db_session):
        from organic_market_agent.crop_book.publisher.engine import CropBookPublisher
        CropBookPublisher().run(db_session, tmp_path)
        import json
        return json.loads((tmp_path / "sfagent-crop-book-data.json").read_text(encoding="utf-8"))

    @pytest.fixture
    def crop_book_client(self, admin_app):
        return admin_app.test_client()

    @pytest.mark.parametrize("label,q,category,seasons,dtm_max", PARITY_CASES)
    def test_parity(self, label, q, category, seasons, dtm_max, data_json, crop_book_client):
        opts = {"q": q, "category": category, "seasons": seasons,
                "dtmMax": dtm_max if dtm_max < 365 else None}

        js_ids    = js_filter_crops(data_json["crops"], opts)
        flask_ids = flask_filter_crops(crop_book_client, opts)

        assert js_ids == flask_ids, (
            f"Filter parity FAIL — case '{label}'\n"
            f"  opts: {opts}\n"
            f"  JS   ids ({len(js_ids)}): {js_ids[:20]}\n"
            f"  Flask ids ({len(flask_ids)}): {flask_ids[:20]}"
        )


# ---------------------------------------------------------------------------
# AC-09: multi-season OR semantics (unit test, no DB)
# ---------------------------------------------------------------------------

def test_multi_season_or():
    """Season filter with [summer, fall] returns crops matching EITHER, not AND."""
    crops = [
        {"id": 1, "name_he": "a", "name_en": None, "scientific_name": None,
         "category": "vegetables",
         "varieties": [{"id": 1, "is_default": True, "planting_season": "קיץ",
                        "days_to_maturity": 45}]},
        {"id": 2, "name_he": "b", "name_en": None, "scientific_name": None,
         "category": "vegetables",
         "varieties": [{"id": 2, "is_default": True, "planting_season": "סתיו",
                        "days_to_maturity": 60}]},
        {"id": 3, "name_he": "c", "name_en": None, "scientific_name": None,
         "category": "vegetables",
         "varieties": [{"id": 3, "is_default": True, "planting_season": "חורף",
                        "days_to_maturity": 80}]},
    ]

    # Both summer + fall: expect crops 1 and 2
    result = js_filter_crops(crops, {"seasons": ["summer", "fall"]})
    assert sorted(result) == [1, 2], f"Expected [1,2] got {result}"

    # Only summer: expect crop 1
    result_summer = js_filter_crops(crops, {"seasons": ["summer"]})
    assert result_summer == [1]

    # Only winter: expect crop 3
    result_winter = js_filter_crops(crops, {"seasons": ["winter"]})
    assert result_winter == [3]

    # All seasons: expect all 3
    result_all = js_filter_crops(crops, {"seasons": ["summer", "spring", "winter", "fall"]})
    assert sorted(result_all) == [1, 2, 3]
